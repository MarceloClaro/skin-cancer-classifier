#!/usr/bin/env python3
"""
Script de Treinamento Personalizado para Classificador de Câncer de Pele K230
Permite configuração de hiperparâmetros e monitoramento em tempo real
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, 
    CSVLogger, Callback
)
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "dataset_incremental"
MODELS_DIR = BASE_DIR / "models"
STATUS_FILE = DATASET_DIR / "retrain_status.json"
HISTORY_FILE = DATASET_DIR / "retrain_history.json"

# Configurações padrão
DEFAULT_CONFIG = {
    "learning_rate": 0.0001,
    "epochs": 50,
    "batch_size": 16,
    "image_size": (224, 224),
    "validation_split": 0.2,
    "test_split": 0.1,
    "early_stopping_patience": 10,
    "reduce_lr_patience": 5,
    "augmentation": {
        "enabled": True,
        "rotation_range": 20,
        "width_shift_range": 0.2,
        "height_shift_range": 0.2,
        "horizontal_flip": True,
        "vertical_flip": True,
        "zoom_range": 0.2,
        "fill_mode": "nearest"
    }
}


class ProgressCallback(Callback):
    """Callback para salvar progresso em tempo real"""
    
    def __init__(self, status_file: Path):
        super().__init__()
        self.status_file = status_file
    
    def on_epoch_end(self, epoch, logs=None):
        """Atualiza status ao final de cada época"""
        logs = logs or {}
        
        status = {
            "status": "running",
            "current_epoch": epoch + 1,
            "total_epochs": self.params['epochs'],
            "metrics": {
                "loss": float(logs.get('loss', 0)),
                "accuracy": float(logs.get('accuracy', 0)),
                "val_loss": float(logs.get('val_loss', 0)),
                "val_accuracy": float(logs.get('val_accuracy', 0))
            },
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"Época {epoch+1}/{self.params['epochs']} - "
                   f"Loss: {logs.get('loss', 0):.4f} - "
                   f"Acc: {logs.get('accuracy', 0):.4f} - "
                   f"Val Loss: {logs.get('val_loss', 0):.4f} - "
                   f"Val Acc: {logs.get('val_accuracy', 0):.4f}")


def update_status(status: str, **kwargs):
    """Atualiza arquivo de status"""
    data = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Status atualizado: {status}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Carrega configuração de treinamento"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            custom_config = json.load(f)
        # Merge com configuração padrão
        config = {**DEFAULT_CONFIG, **custom_config}
        logger.info(f"Configuração carregada de: {config_path}")
    else:
        config = DEFAULT_CONFIG
        logger.info("Usando configuração padrão")
    
    return config


def check_dataset() -> Dict[str, int]:
    """Verifica dataset disponível"""
    stats = {}
    
    for class_name in ["BENIGNO", "MALIGNO"]:
        class_dir = DATASET_DIR / class_name
        if class_dir.exists():
            images = list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpg"))
            stats[class_name] = len(images)
        else:
            stats[class_name] = 0
    
    stats["total"] = sum(stats.values())
    
    logger.info(f"Dataset: {stats['total']} imagens "
               f"(BENIGNO: {stats['BENIGNO']}, MALIGNO: {stats['MALIGNO']})")
    
    return stats


def create_data_generators(config: Dict[str, Any]):
    """Cria geradores de dados com augmentation"""
    
    # Data augmentation para treino
    if config["augmentation"]["enabled"]:
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=config["augmentation"]["rotation_range"],
            width_shift_range=config["augmentation"]["width_shift_range"],
            height_shift_range=config["augmentation"]["height_shift_range"],
            horizontal_flip=config["augmentation"]["horizontal_flip"],
            vertical_flip=config["augmentation"]["vertical_flip"],
            zoom_range=config["augmentation"]["zoom_range"],
            fill_mode=config["augmentation"]["fill_mode"],
            validation_split=config["validation_split"]
        )
    else:
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=config["validation_split"]
        )
    
    # Sem augmentation para validação
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=config["validation_split"]
    )
    
    # Geradores
    train_generator = train_datagen.flow_from_directory(
        str(DATASET_DIR),
        target_size=config["image_size"],
        batch_size=config["batch_size"],
        class_mode='binary',
        subset='training',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        str(DATASET_DIR),
        target_size=config["image_size"],
        batch_size=config["batch_size"],
        class_mode='binary',
        subset='validation',
        shuffle=False
    )
    
    logger.info(f"Geradores criados: {train_generator.samples} treino, "
               f"{val_generator.samples} validação")
    
    return train_generator, val_generator


def create_model(config: Dict[str, Any]) -> keras.Model:
    """Cria modelo CNN otimizado para K230"""
    
    base_model = keras.applications.MobileNetV2(
        input_shape=(*config["image_size"], 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Congelar camadas base inicialmente
    base_model.trainable = False
    
    # Adicionar camadas customizadas
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    
    # Compilar
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config["learning_rate"]),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    logger.info("Modelo criado (MobileNetV2 + Custom Layers)")
    logger.info(f"Total de parâmetros: {model.count_params():,}")
    
    return model


def create_callbacks(config: Dict[str, Any]) -> list:
    """Cria callbacks para treinamento"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = MODELS_DIR / f"training_report_{timestamp}"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    callbacks = [
        # Checkpoint do melhor modelo
        ModelCheckpoint(
            str(MODELS_DIR / "skin_cancer_model.h5"),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        
        # Early stopping
        EarlyStopping(
            monitor='val_loss',
            patience=config["early_stopping_patience"],
            restore_best_weights=True,
            verbose=1
        ),
        
        # Redução de learning rate
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=config["reduce_lr_patience"],
            min_lr=1e-7,
            verbose=1
        ),
        
        # Log CSV
        CSVLogger(
            str(report_dir / "training_log.csv"),
            append=False
        ),
        
        # Progresso em tempo real
        ProgressCallback(STATUS_FILE)
    ]
    
    return callbacks


def plot_training_history(history, output_dir: Path):
    """Plota curvas de treinamento"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Acurácia
    ax1.plot(history.history['accuracy'], label='Treino')
    ax1.plot(history.history['val_accuracy'], label='Validação')
    ax1.set_title('Acurácia do Modelo')
    ax1.set_xlabel('Época')
    ax1.set_ylabel('Acurácia')
    ax1.legend()
    ax1.grid(True)
    
    # Loss
    ax2.plot(history.history['loss'], label='Treino')
    ax2.plot(history.history['val_loss'], label='Validação')
    ax2.set_title('Loss do Modelo')
    ax2.set_xlabel('Época')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / "training_curves.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Curvas de treinamento salvas em: {output_dir}")


def evaluate_model(model, val_generator, output_dir: Path):
    """Avalia modelo e gera métricas"""
    
    # Predições
    val_generator.reset()
    y_true = val_generator.classes
    y_pred_proba = model.predict(val_generator, verbose=1)
    y_pred = (y_pred_proba > 0.5).astype(int).flatten()
    
    # Matriz de confusão
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['BENIGNO', 'MALIGNO'],
                yticklabels=['BENIGNO', 'MALIGNO'])
    plt.title('Matriz de Confusão')
    plt.ylabel('Real')
    plt.xlabel('Predito')
    plt.tight_layout()
    plt.savefig(output_dir / "confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Curva ROC
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2,
             label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taxa de Falsos Positivos')
    plt.ylabel('Taxa de Verdadeiros Positivos')
    plt.title('Curva ROC')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_dir / "roc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Relatório de classificação
    report = classification_report(y_true, y_pred,
                                   target_names=['BENIGNO', 'MALIGNO'],
                                   output_dict=True)
    
    with open(output_dir / "classification_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Métricas salvas em: {output_dir}")
    logger.info(f"Acurácia: {report['accuracy']:.4f}")
    logger.info(f"AUC-ROC: {roc_auc:.4f}")
    
    return {
        "accuracy": report['accuracy'],
        "auc_roc": float(roc_auc),
        "confusion_matrix": cm.tolist(),
        "classification_report": report
    }


def save_training_history(config: Dict[str, Any], metrics: Dict[str, Any], 
                         dataset_stats: Dict[str, int]):
    """Salva histórico de treinamento"""
    
    # Carregar histórico existente
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    # Adicionar novo registro
    record = {
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "dataset": dataset_stats,
        "metrics": metrics
    }
    
    history.append(record)
    
    # Salvar
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    logger.info(f"Histórico atualizado: {HISTORY_FILE}")


def train_model(config: Dict[str, Any]) -> Dict[str, Any]:
    """Executa treinamento completo"""
    
    logger.info("=" * 60)
    logger.info("INICIANDO TREINAMENTO")
    logger.info("=" * 60)
    
    try:
        # Atualizar status
        update_status("starting")
        
        # Verificar dataset
        dataset_stats = check_dataset()
        if dataset_stats["total"] < 10:
            raise ValueError(f"Dataset insuficiente: {dataset_stats['total']} imagens (mínimo 10)")
        
        # Criar geradores
        train_gen, val_gen = create_data_generators(config)
        
        # Criar modelo
        model = create_model(config)
        
        # Criar callbacks
        callbacks = create_callbacks(config)
        
        # Treinar
        update_status("training")
        
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=config["epochs"],
            callbacks=callbacks,
            verbose=1
        )
        
        # Criar diretório de relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = MODELS_DIR / f"training_report_{timestamp}"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Plotar curvas
        plot_training_history(history, report_dir)
        
        # Avaliar modelo
        metrics = evaluate_model(model, val_gen, report_dir)
        
        # Salvar histórico
        save_training_history(config, metrics, dataset_stats)
        
        # Atualizar status final
        update_status("completed", 
                     accuracy=metrics["accuracy"],
                     auc_roc=metrics["auc_roc"],
                     images_used=dataset_stats["total"])
        
        logger.info("=" * 60)
        logger.info("TREINAMENTO CONCLUÍDO COM SUCESSO")
        logger.info(f"Acurácia: {metrics['accuracy']:.4f}")
        logger.info(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "metrics": metrics,
            "report_dir": str(report_dir)
        }
        
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}", exc_info=True)
        update_status("failed", error=str(e))
        
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description="Treinamento personalizado do modelo")
    parser.add_argument("--config", type=str, help="Caminho para arquivo de configuração JSON")
    parser.add_argument("--auto", action="store_true", help="Modo automático (usa config padrão)")
    
    args = parser.parse_args()
    
    # Carregar configuração
    config = load_config(args.config)
    
    # Treinar
    result = train_model(config)
    
    # Imprimir resultado
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
