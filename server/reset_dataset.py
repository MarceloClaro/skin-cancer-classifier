#!/usr/bin/env python3
"""
Script para Reset Completo do Dataset e Modelos
Remove todo o dataset incremental e modelos treinados
"""

import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "dataset_incremental"
MODELS_DIR = BASE_DIR / "models"


def reset_dataset() -> Dict[str, Any]:
    """
    Remove todas as imagens do dataset incremental
    
    Returns:
        Dict com resultado da operação
    """
    try:
        removed_count = 0
        
        # Limpar diretórios de classes
        for class_name in ["BENIGNO", "MALIGNO"]:
            class_dir = DATASET_DIR / class_name
            if class_dir.exists():
                files = list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpg"))
                for file in files:
                    file.unlink()
                    removed_count += 1
                    logger.info(f"Removida: {file.name}")
        
        # Limpar metadados
        metadata_dir = DATASET_DIR / "metadata"
        if metadata_dir.exists():
            files = list(metadata_dir.glob("*.json"))
            for file in files:
                file.unlink()
                logger.info(f"Removido metadado: {file.name}")
        
        logger.info(f"Dataset limpo: {removed_count} imagens removidas")
        
        return {
            "success": True,
            "images_removed": removed_count
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar dataset: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def reset_status_files() -> Dict[str, Any]:
    """
    Remove arquivos de status e histórico
    
    Returns:
        Dict com resultado da operação
    """
    try:
        removed_files = []
        
        status_files = [
            DATASET_DIR / "retrain_history.json",
            DATASET_DIR / "retrain_status.json",
            DATASET_DIR / "statistics.json"
        ]
        
        for file in status_files:
            if file.exists():
                file.unlink()
                removed_files.append(file.name)
                logger.info(f"Removido: {file.name}")
        
        logger.info(f"Arquivos de status limpos: {len(removed_files)}")
        
        return {
            "success": True,
            "files_removed": removed_files
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar arquivos de status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def reset_trained_models() -> Dict[str, Any]:
    """
    Remove modelos treinados (mantém pré-treinados)
    
    Returns:
        Dict com resultado da operação
    """
    try:
        removed_files = []
        
        # Arquivos de modelo para remover
        model_files = [
            MODELS_DIR / "skin_cancer_model.h5",
            MODELS_DIR / "training_curves.png",
            MODELS_DIR / "confusion_matrix.png",
            MODELS_DIR / "roc_curve.png"
        ]
        
        for file in model_files:
            if file.exists():
                file.unlink()
                removed_files.append(file.name)
                logger.info(f"Removido: {file.name}")
        
        # Remover diretórios de relatórios de treinamento
        for report_dir in MODELS_DIR.glob("training_report_*"):
            if report_dir.is_dir():
                shutil.rmtree(report_dir)
                removed_files.append(report_dir.name)
                logger.info(f"Removido diretório: {report_dir.name}")
        
        logger.info(f"Modelos limpos: {len(removed_files)} arquivos/diretórios")
        
        return {
            "success": True,
            "files_removed": removed_files
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar modelos: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def reset_all() -> Dict[str, Any]:
    """
    Executa reset completo: dataset, status e modelos
    
    Returns:
        Dict com resultado completo
    """
    logger.info("=" * 60)
    logger.info("INICIANDO RESET COMPLETO")
    logger.info("=" * 60)
    
    results = {
        "dataset": reset_dataset(),
        "status": reset_status_files(),
        "models": reset_trained_models()
    }
    
    all_success = all(r["success"] for r in results.values())
    
    logger.info("=" * 60)
    if all_success:
        logger.info("RESET COMPLETO CONCLUÍDO COM SUCESSO")
    else:
        logger.error("RESET COMPLETO CONCLUÍDO COM ERROS")
    logger.info("=" * 60)
    
    return {
        "success": all_success,
        "details": results
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        result = reset_all()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    else:
        print("AVISO: Este script irá remover:")
        print("  - Todo o dataset incremental (BENIGNO e MALIGNO)")
        print("  - Todos os modelos treinados")
        print("  - Histórico e status de retreinamento")
        print("  - Visualizações de treinamento")
        print()
        print("Para confirmar, execute:")
        print(f"  python3 {sys.argv[0]} --confirm")
        sys.exit(0)
