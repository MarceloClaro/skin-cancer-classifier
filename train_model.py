"""
Script de Treinamento do Modelo de Classificação de Câncer de Pele
Dataset: BENIGNO vs MALIGNO (classificação binária)
Arquitetura: MobileNetV2 com Transfer Learning
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split

# Configurações
DATASET_PATH = '/home/ubuntu/skin_dataset'
MODEL_SAVE_PATH = '/home/ubuntu/skin_cancer_classifier_k230_page/models'
IMG_SIZE = (224, 224)
BATCH_SIZE = 8  # Pequeno devido ao dataset reduzido
EPOCHS = 50
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2

# Criar diretório para modelos
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)

print("=" * 60)
print("🚀 TREINAMENTO DO MODELO DE CLASSIFICAÇÃO DE CÂNCER DE PELE")
print("=" * 60)
print(f"Dataset: {DATASET_PATH}")
print(f"Classes: BENIGNO vs MALIGNO")
print(f"Tamanho da imagem: {IMG_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Épocas: {EPOCHS}")
print("=" * 60)

# Data Augmentation agressivo para dataset pequeno
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest',
    validation_split=VALIDATION_SPLIT
)

# Validação sem augmentation
val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=VALIDATION_SPLIT
)

print("\n📊 Carregando dados de treinamento...")
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training',
    shuffle=True,
    seed=42
)

print("\n📊 Carregando dados de validação...")
val_generator = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation',
    shuffle=False,
    seed=42
)

print(f"\n✅ Treinamento: {train_generator.samples} imagens")
print(f"✅ Validação: {val_generator.samples} imagens")
print(f"✅ Classes: {train_generator.class_indices}")

# Criar modelo com Transfer Learning
print("\n🧠 Criando modelo MobileNetV2 com Transfer Learning...")

base_model = MobileNetV2(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

# Congelar camadas base inicialmente
base_model.trainable = False

# Construir modelo
inputs = keras.Input(shape=(*IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(1, activation='sigmoid')(x)

model = keras.Model(inputs, outputs)

# Compilar modelo
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss='binary_crossentropy',
    metrics=['accuracy', keras.metrics.AUC(name='auc')]
)

print("\n📋 Arquitetura do modelo:")
model.summary()

# Callbacks
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        os.path.join(MODEL_SAVE_PATH, 'best_model.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

# Fase 1: Treinar apenas camadas superiores
print("\n" + "=" * 60)
print("🎯 FASE 1: Treinamento das camadas superiores (base congelada)")
print("=" * 60)

history_phase1 = model.fit(
    train_generator,
    epochs=20,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# Fase 2: Fine-tuning (descongelar últimas camadas)
print("\n" + "=" * 60)
print("🎯 FASE 2: Fine-tuning (descongelando últimas camadas)")
print("=" * 60)

base_model.trainable = True

# Congelar apenas as primeiras camadas
for layer in base_model.layers[:100]:
    layer.trainable = False

# Recompilar com learning rate menor
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
    loss='binary_crossentropy',
    metrics=['accuracy', keras.metrics.AUC(name='auc')]
)

history_phase2 = model.fit(
    train_generator,
    epochs=EPOCHS,
    initial_epoch=history_phase1.epoch[-1],
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# Combinar históricos
history = {
    'accuracy': history_phase1.history['accuracy'] + history_phase2.history['accuracy'],
    'val_accuracy': history_phase1.history['val_accuracy'] + history_phase2.history['val_accuracy'],
    'loss': history_phase1.history['loss'] + history_phase2.history['loss'],
    'val_loss': history_phase1.history['val_loss'] + history_phase2.history['val_loss'],
    'auc': history_phase1.history['auc'] + history_phase2.history['auc'],
    'val_auc': history_phase1.history['val_auc'] + history_phase2.history['val_auc'],
}

# Salvar modelo final
final_model_path = os.path.join(MODEL_SAVE_PATH, 'skin_cancer_model.h5')
model.save(final_model_path)
print(f"\n✅ Modelo salvo em: {final_model_path}")

# Avaliar no conjunto de validação
print("\n" + "=" * 60)
print("📊 AVALIAÇÃO DO MODELO")
print("=" * 60)

val_generator.reset()
predictions = model.predict(val_generator, verbose=1)
predicted_classes = (predictions > 0.5).astype(int).flatten()
true_classes = val_generator.classes

# Métricas
print("\n📈 Relatório de Classificação:")
print(classification_report(
    true_classes,
    predicted_classes,
    target_names=['BENIGNO', 'MALIGNO']
))

# Matriz de confusão
cm = confusion_matrix(true_classes, predicted_classes)
print("\n📊 Matriz de Confusão:")
print(cm)

# Acurácia final
final_accuracy = np.mean(predicted_classes == true_classes)
print(f"\n✅ Acurácia Final: {final_accuracy:.2%}")

# Plotar curvas de treinamento
plt.figure(figsize=(15, 5))

# Acurácia
plt.subplot(1, 3, 1)
plt.plot(history['accuracy'], label='Treino')
plt.plot(history['val_accuracy'], label='Validação')
plt.axvline(x=len(history_phase1.history['accuracy']), color='r', linestyle='--', label='Início Fine-tuning')
plt.title('Acurácia')
plt.xlabel('Época')
plt.ylabel('Acurácia')
plt.legend()
plt.grid(True)

# Loss
plt.subplot(1, 3, 2)
plt.plot(history['loss'], label='Treino')
plt.plot(history['val_loss'], label='Validação')
plt.axvline(x=len(history_phase1.history['loss']), color='r', linestyle='--', label='Início Fine-tuning')
plt.title('Loss')
plt.xlabel('Época')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

# AUC
plt.subplot(1, 3, 3)
plt.plot(history['auc'], label='Treino')
plt.plot(history['val_auc'], label='Validação')
plt.axvline(x=len(history_phase1.history['auc']), color='r', linestyle='--', label='Início Fine-tuning')
plt.title('AUC')
plt.xlabel('Época')
plt.ylabel('AUC')
plt.legend()
plt.grid(True)

plt.tight_layout()
training_curves_path = os.path.join(MODEL_SAVE_PATH, 'training_curves.png')
plt.savefig(training_curves_path, dpi=150)
print(f"\n✅ Curvas de treinamento salvas em: {training_curves_path}")

# Matriz de confusão visual
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['BENIGNO', 'MALIGNO'],
            yticklabels=['BENIGNO', 'MALIGNO'])
plt.title('Matriz de Confusão')
plt.ylabel('Verdadeiro')
plt.xlabel('Predito')
plt.tight_layout()
cm_path = os.path.join(MODEL_SAVE_PATH, 'confusion_matrix.png')
plt.savefig(cm_path, dpi=150)
print(f"✅ Matriz de confusão salva em: {cm_path}")

# Curva ROC
fpr, tpr, thresholds = roc_curve(true_classes, predictions)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos')
plt.ylabel('Taxa de Verdadeiros Positivos')
plt.title('Curva ROC')
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
roc_path = os.path.join(MODEL_SAVE_PATH, 'roc_curve.png')
plt.savefig(roc_path, dpi=150)
print(f"✅ Curva ROC salva em: {roc_path}")

# Salvar metadados do treinamento
metadata = {
    'timestamp': datetime.now().isoformat(),
    'dataset_path': DATASET_PATH,
    'total_images': train_generator.samples + val_generator.samples,
    'train_images': train_generator.samples,
    'val_images': val_generator.samples,
    'classes': train_generator.class_indices,
    'img_size': IMG_SIZE,
    'batch_size': BATCH_SIZE,
    'epochs': len(history['accuracy']),
    'final_accuracy': float(final_accuracy),
    'final_val_accuracy': float(history['val_accuracy'][-1]),
    'final_auc': float(history['val_auc'][-1]),
    'model_path': final_model_path,
}

metadata_path = os.path.join(MODEL_SAVE_PATH, 'training_metadata.json')
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Metadados salvos em: {metadata_path}")

print("\n" + "=" * 60)
print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print(f"📁 Modelo: {final_model_path}")
print(f"📊 Acurácia Final: {final_accuracy:.2%}")
print(f"📈 AUC: {roc_auc:.2f}")
print("=" * 60)
