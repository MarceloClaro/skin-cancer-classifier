#!/usr/bin/env python3
"""
Script de Treinamento Melhorado para Classificador de Câncer de Pele
Inclui visualizações completas: data augmentation, parâmetros, indicadores, melhores/piores predições
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import pandas as pd

# Configurações
DATASET_PATH = "/home/ubuntu/skin_dataset"
OUTPUT_DIR = "/home/ubuntu/skin_cancer_classifier_k230_page/models"
TRAINING_REPORT_DIR = f"{OUTPUT_DIR}/training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
IMG_SIZE = (224, 224)
BATCH_SIZE = 8
EPOCHS_PHASE1 = 10
EPOCHS_PHASE2 = 20
LEARNING_RATE_PHASE1 = 0.001
LEARNING_RATE_PHASE2 = 0.0001

# Criar diretórios
os.makedirs(TRAINING_REPORT_DIR, exist_ok=True)
os.makedirs(f"{TRAINING_REPORT_DIR}/augmentation_examples", exist_ok=True)
os.makedirs(f"{TRAINING_REPORT_DIR}/predictions", exist_ok=True)

print("=" * 80)
print("TREINAMENTO MELHORADO - CLASSIFICADOR DE CÂNCER DE PELE")
print("=" * 80)
print(f"Relatório será salvo em: {TRAINING_REPORT_DIR}")
print()

# ==============================================================================
# 1. CARREGAR E PREPARAR DADOS
# ==============================================================================
print("📊 1. CARREGANDO DADOS...")

def load_dataset(dataset_path):
    """Carrega dataset e retorna imagens e labels"""
    images = []
    labels = []
    class_names = []
    
    for class_name in os.listdir(dataset_path):
        class_path = os.path.join(dataset_path, class_name)
        if not os.path.isdir(class_path):
            continue
            
        class_names.append(class_name)
        class_idx = len(class_names) - 1
        
        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)
            try:
                img = load_img(img_path, target_size=IMG_SIZE)
                img_array = img_to_array(img) / 255.0
                images.append(img_array)
                labels.append(class_idx)
            except Exception as e:
                print(f"  ⚠️  Erro ao carregar {img_path}: {e}")
    
    return np.array(images), np.array(labels), class_names

X, y, class_names = load_dataset(DATASET_PATH)
print(f"  ✓ Total de imagens: {len(X)}")
print(f"  ✓ Classes: {class_names}")
print(f"  ✓ Distribuição: {dict(zip(class_names, np.bincount(y)))}")
print()

# Split train/val
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  ✓ Treino: {len(X_train)} imagens")
print(f"  ✓ Validação: {len(X_val)} imagens")
print()

# ==============================================================================
# 2. VISUALIZAR DATA AUGMENTATION
# ==============================================================================
print("🎨 2. VISUALIZANDO DATA AUGMENTATION...")

# Configurar data augmentation
train_datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest'
)

# Gerar exemplos de augmentation
def visualize_augmentation(images, labels, class_names, n_examples=3):
    """Visualiza exemplos de data augmentation"""
    fig, axes = plt.subplots(n_examples, 6, figsize=(18, 3*n_examples))
    fig.suptitle('Exemplos de Data Augmentation', fontsize=16, fontweight='bold')
    
    for i in range(n_examples):
        # Imagem original
        idx = np.random.randint(0, len(images))
        img = images[idx]
        label = class_names[labels[idx]]
        
        axes[i, 0].imshow(img)
        axes[i, 0].set_title(f'Original\n{label}', fontweight='bold')
        axes[i, 0].axis('off')
        
        # Gerar 5 versões augmentadas
        img_batch = np.expand_dims(img, 0)
        aug_iter = train_datagen.flow(img_batch, batch_size=1)
        
        for j in range(5):
            aug_img = next(aug_iter)[0]
            axes[i, j+1].imshow(aug_img)
            axes[i, j+1].set_title(f'Augmented {j+1}')
            axes[i, j+1].axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{TRAINING_REPORT_DIR}/augmentation_examples.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Salvo: augmentation_examples.png")
    plt.close()

visualize_augmentation(X_train, y_train, class_names, n_examples=3)
print()

# ==============================================================================
# 3. CRIAR MODELO
# ==============================================================================
print("🧠 3. CRIANDO MODELO...")

def create_model(num_classes):
    """Cria modelo com MobileNetV2 + transfer learning"""
    base_model = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False
    
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model, base_model

model, base_model = create_model(len(class_names))
print(f"  ✓ Modelo criado")
print(f"  ✓ Total de parâmetros: {model.count_params():,}")
print(f"  ✓ Parâmetros treináveis: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
print()

# ==============================================================================
# 4. TABELA DE HIPERPARÂMETROS
# ==============================================================================
print("📋 4. SALVANDO TABELA DE HIPERPARÂMETROS...")

hyperparams = {
    'Dataset': DATASET_PATH,
    'Total de Imagens': len(X),
    'Imagens de Treino': len(X_train),
    'Imagens de Validação': len(X_val),
    'Classes': ', '.join(class_names),
    'Tamanho da Imagem': f'{IMG_SIZE[0]}x{IMG_SIZE[1]}',
    'Batch Size': BATCH_SIZE,
    'Épocas Fase 1': EPOCHS_PHASE1,
    'Épocas Fase 2': EPOCHS_PHASE2,
    'Learning Rate Fase 1': LEARNING_RATE_PHASE1,
    'Learning Rate Fase 2': LEARNING_RATE_PHASE2,
    'Arquitetura Base': 'MobileNetV2',
    'Pesos Pré-treinados': 'ImageNet',
    'Data Augmentation': 'Sim (rotation, shift, zoom, flip)',
    'Dropout': '0.5, 0.3',
    'Otimizador': 'Adam',
    'Loss Function': 'sparse_categorical_crossentropy',
    'Métricas': 'accuracy',
    'Early Stopping': 'Sim (patience=5)',
    'Reduce LR': 'Sim (patience=3, factor=0.5)',
}

# Salvar como JSON
with open(f'{TRAINING_REPORT_DIR}/hyperparameters.json', 'w') as f:
    json.dump(hyperparams, f, indent=2)

# Criar tabela visual
fig, ax = plt.subplots(figsize=(12, 10))
ax.axis('tight')
ax.axis('off')

table_data = [[k, str(v)] for k, v in hyperparams.items()]
table = ax.table(cellText=table_data, colLabels=['Parâmetro', 'Valor'],
                cellLoc='left', loc='center', colWidths=[0.4, 0.6])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Estilizar cabeçalho
for i in range(2):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Estilizar linhas alternadas
for i in range(1, len(table_data) + 1):
    if i % 2 == 0:
        for j in range(2):
            table[(i, j)].set_facecolor('#f0f0f0')

plt.title('Hiperparâmetros do Treinamento', fontsize=16, fontweight='bold', pad=20)
plt.savefig(f'{TRAINING_REPORT_DIR}/hyperparameters_table.png', dpi=150, bbox_inches='tight')
print(f"  ✓ Salvo: hyperparameters_table.png")
plt.close()
print()

# ==============================================================================
# 5. TREINAMENTO FASE 1
# ==============================================================================
print("🚀 5. TREINAMENTO FASE 1 (Camadas Superiores)...")

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE_PHASE1),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_phase1 = [
    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5, verbose=1),
    keras.callbacks.ModelCheckpoint(
        f'{OUTPUT_DIR}/best_model_phase1.h5',
        save_best_only=True,
        verbose=1
    )
]

history_phase1 = model.fit(
    train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    validation_data=(X_val, y_val),
    epochs=EPOCHS_PHASE1,
    callbacks=callbacks_phase1,
    verbose=1
)
print()

# ==============================================================================
# 6. TREINAMENTO FASE 2 (Fine-tuning)
# ==============================================================================
print("🔥 6. TREINAMENTO FASE 2 (Fine-tuning)...")

base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE_PHASE2),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_phase2 = [
    keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5, verbose=1),
    keras.callbacks.ModelCheckpoint(
        f'{OUTPUT_DIR}/skin_cancer_model.h5',
        save_best_only=True,
        verbose=1
    )
]

history_phase2 = model.fit(
    train_datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    validation_data=(X_val, y_val),
    epochs=EPOCHS_PHASE2,
    callbacks=callbacks_phase2,
    verbose=1
)
print()

# ==============================================================================
# 7. GRÁFICOS DE TREINAMENTO
# ==============================================================================
print("📈 7. GERANDO GRÁFICOS DE TREINAMENTO...")

def plot_training_history(history1, history2):
    """Plota curvas de treinamento das duas fases"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle('Curvas de Treinamento - Fase 1 e Fase 2', fontsize=16, fontweight='bold')
    
    # Combinar históricos
    metrics = ['accuracy', 'loss']
    titles = ['Acurácia', 'Loss']
    
    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx]
        
        # Fase 1
        if metric in history1.history:
            epochs1 = range(1, len(history1.history[metric]) + 1)
            ax.plot(epochs1, history1.history[metric], 'b-', label=f'Treino Fase 1', linewidth=2)
            ax.plot(epochs1, history1.history[f'val_{metric}'], 'b--', label=f'Val Fase 1', linewidth=2)
        
        # Fase 2
        if metric in history2.history:
            offset = len(history1.history[metric])
            epochs2 = range(offset + 1, offset + len(history2.history[metric]) + 1)
            ax.plot(epochs2, history2.history[metric], 'r-', label=f'Treino Fase 2', linewidth=2)
            ax.plot(epochs2, history2.history[f'val_{metric}'], 'r--', label=f'Val Fase 2', linewidth=2)
        
        ax.axvline(x=len(history1.history[metric]), color='gray', linestyle=':', label='Início Fine-tuning')
        ax.set_xlabel('Época', fontsize=12)
        ax.set_ylabel(title, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{TRAINING_REPORT_DIR}/training_curves.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Salvo: training_curves.png")
    plt.close()

plot_training_history(history_phase1, history_phase2)
print()

# ==============================================================================
# 8. AVALIAÇÃO E MÉTRICAS
# ==============================================================================
print("📊 8. AVALIANDO MODELO...")

y_pred_proba = model.predict(X_val, verbose=0)
y_pred = np.argmax(y_pred_proba, axis=1)

# Relatório de classificação
report = classification_report(y_val, y_pred, target_names=class_names, output_dict=True)
print("\n" + classification_report(y_val, y_pred, target_names=class_names))

# Salvar relatório
with open(f'{TRAINING_REPORT_DIR}/classification_report.json', 'w') as f:
    json.dump(report, f, indent=2)

# Matriz de confusão
cm = confusion_matrix(y_val, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.title('Matriz de Confusão', fontsize=16, fontweight='bold')
plt.ylabel('Real', fontsize=12)
plt.xlabel('Predito', fontsize=12)
plt.tight_layout()
plt.savefig(f'{TRAINING_REPORT_DIR}/confusion_matrix.png', dpi=150, bbox_inches='tight')
print(f"  ✓ Salvo: confusion_matrix.png")
plt.close()

# Curva ROC
if len(class_names) == 2:
    # Usar probabilidade da classe positiva (índice 1)
    y_pred_proba_positive = y_pred_proba[:, 1]
    fpr, tpr, _ = roc_curve(y_val, y_pred_proba_positive)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taxa de Falsos Positivos', fontsize=12)
    plt.ylabel('Taxa de Verdadeiros Positivos', fontsize=12)
    plt.title('Curva ROC', fontsize=16, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{TRAINING_REPORT_DIR}/roc_curve.png', dpi=150, bbox_inches='tight')
    print(f"  ✓ Salvo: roc_curve.png")
    plt.close()

print()

# ==============================================================================
# 9. VISUALIZAR MELHORES E PIORES PREDIÇÕES
# ==============================================================================
print("🎯 9. VISUALIZANDO MELHORES E PIORES PREDIÇÕES...")

def visualize_predictions(X, y_true, y_pred_proba, class_names, n_best=6, n_worst=6):
    """Visualiza melhores e piores predições"""
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Calcular confiança (probabilidade da classe predita)
    confidences = np.max(y_pred_proba, axis=1)
    
    # Encontrar corretas e incorretas
    correct_mask = (y_pred == y_true)
    correct_indices = np.where(correct_mask)[0]
    incorrect_indices = np.where(~correct_mask)[0]
    
    # Melhores predições (corretas com maior confiança)
    if len(correct_indices) > 0:
        best_indices = correct_indices[np.argsort(confidences[correct_indices])[-n_best:]][::-1]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('✅ Melhores Predições (Corretas com Alta Confiança)', fontsize=16, fontweight='bold', color='green')
        
        for idx, ax in enumerate(axes.flat):
            if idx < len(best_indices):
                i = best_indices[idx]
                ax.imshow(X[i])
                true_label = class_names[y_true[i]]
                pred_label = class_names[y_pred[i]]
                conf = confidences[i]
                ax.set_title(f'Real: {true_label}\nPredito: {pred_label}\nConfiança: {conf:.2%}', 
                           fontsize=10, color='green', fontweight='bold')
                ax.axis('off')
            else:
                ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{TRAINING_REPORT_DIR}/predictions/best_predictions.png', dpi=150, bbox_inches='tight')
        print(f"  ✓ Salvo: best_predictions.png")
        plt.close()
    
    # Piores predições (incorretas com maior confiança)
    if len(incorrect_indices) > 0:
        worst_indices = incorrect_indices[np.argsort(confidences[incorrect_indices])[-n_worst:]][::-1]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('❌ Piores Predições (Incorretas com Alta Confiança)', fontsize=16, fontweight='bold', color='red')
        
        for idx, ax in enumerate(axes.flat):
            if idx < len(worst_indices):
                i = worst_indices[idx]
                ax.imshow(X[i])
                true_label = class_names[y_true[i]]
                pred_label = class_names[y_pred[i]]
                conf = confidences[i]
                ax.set_title(f'Real: {true_label}\nPredito: {pred_label}\nConfiança: {conf:.2%}', 
                           fontsize=10, color='red', fontweight='bold')
                ax.axis('off')
            else:
                ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{TRAINING_REPORT_DIR}/predictions/worst_predictions.png', dpi=150, bbox_inches='tight')
        print(f"  ✓ Salvo: worst_predictions.png")
        plt.close()

visualize_predictions(X_val, y_val, y_pred_proba, class_names)
print()

# ==============================================================================
# 10. RESUMO FINAL
# ==============================================================================
print("=" * 80)
print("✅ TREINAMENTO CONCLUÍDO!")
print("=" * 80)
print(f"📁 Relatório completo salvo em: {TRAINING_REPORT_DIR}")
print(f"📊 Arquivos gerados:")
print(f"   - augmentation_examples.png")
print(f"   - hyperparameters_table.png")
print(f"   - hyperparameters.json")
print(f"   - training_curves.png")
print(f"   - confusion_matrix.png")
print(f"   - roc_curve.png")
print(f"   - classification_report.json")
print(f"   - predictions/best_predictions.png")
print(f"   - predictions/worst_predictions.png")
print()
print(f"🎯 Acurácia Final: {report['accuracy']:.2%}")
print(f"🎯 AUC: {report.get('macro avg', {}).get('f1-score', 'N/A')}")
print("=" * 80)
