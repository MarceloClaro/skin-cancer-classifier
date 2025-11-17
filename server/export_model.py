#!/usr/bin/env python3
"""
Script para Exportação de Modelos em Múltiplos Formatos
Suporta H5, TFLite (float32 e quantizado), e ONNX
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

import numpy as np
import tensorflow as tf
from tensorflow import keras

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
TFLITE_DIR = MODELS_DIR / "tflite"
EXPORT_DIR = MODELS_DIR / "exports"


def export_h5(model_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exporta modelo em formato H5 (completo)
    
    Args:
        model_path: Caminho do modelo original
        output_dir: Diretório de saída
        
    Returns:
        Dict com resultado
    """
    try:
        logger.info("Exportando modelo H5...")
        
        # Carregar modelo
        model = keras.models.load_model(model_path)
        
        # Salvar cópia
        output_path = output_dir / "skin_cancer_model_export.h5"
        model.save(output_path)
        
        # Obter informações
        file_size = output_path.stat().st_size
        
        logger.info(f"Modelo H5 exportado: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return {
            "success": True,
            "format": "h5",
            "path": str(output_path),
            "size_bytes": file_size,
            "size_mb": file_size / 1024 / 1024
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar H5: {e}")
        return {
            "success": False,
            "format": "h5",
            "error": str(e)
        }


def export_tflite_float32(model_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exporta modelo em formato TFLite (float32)
    
    Args:
        model_path: Caminho do modelo original
        output_dir: Diretório de saída
        
    Returns:
        Dict com resultado
    """
    try:
        logger.info("Exportando modelo TFLite (float32)...")
        
        # Carregar modelo
        model = keras.models.load_model(model_path)
        
        # Converter para TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = []  # Sem otimizações (float32 puro)
        
        tflite_model = converter.convert()
        
        # Salvar
        output_path = output_dir / "skin_cancer_k230.tflite"
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        file_size = len(tflite_model)
        
        logger.info(f"Modelo TFLite (float32) exportado: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return {
            "success": True,
            "format": "tflite_float32",
            "path": str(output_path),
            "size_bytes": file_size,
            "size_mb": file_size / 1024 / 1024
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar TFLite (float32): {e}")
        return {
            "success": False,
            "format": "tflite_float32",
            "error": str(e)
        }


def export_tflite_quantized(model_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exporta modelo em formato TFLite (quantizado INT8)
    
    Args:
        model_path: Caminho do modelo original
        output_dir: Diretório de saída
        
    Returns:
        Dict com resultado
    """
    try:
        logger.info("Exportando modelo TFLite (quantizado INT8)...")
        
        # Carregar modelo
        model = keras.models.load_model(model_path)
        
        # Converter para TFLite com quantização
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Quantização INT8 completa
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8
        
        # Dataset representativo para calibração
        def representative_dataset():
            for _ in range(100):
                # Gerar imagens aleatórias para calibração
                data = np.random.rand(1, 224, 224, 3).astype(np.float32)
                yield [data]
        
        converter.representative_dataset = representative_dataset
        
        tflite_model = converter.convert()
        
        # Salvar
        output_path = output_dir / "skin_cancer_k230_quantized.tflite"
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        file_size = len(tflite_model)
        
        logger.info(f"Modelo TFLite (quantizado) exportado: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return {
            "success": True,
            "format": "tflite_quantized",
            "path": str(output_path),
            "size_bytes": file_size,
            "size_mb": file_size / 1024 / 1024,
            "compression_ratio": None  # Será calculado depois
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar TFLite (quantizado): {e}")
        return {
            "success": False,
            "format": "tflite_quantized",
            "error": str(e)
        }


def export_onnx(model_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Exporta modelo em formato ONNX
    
    Args:
        model_path: Caminho do modelo original
        output_dir: Diretório de saída
        
    Returns:
        Dict com resultado
    """
    try:
        logger.info("Exportando modelo ONNX...")
        
        # Tentar importar tf2onnx
        try:
            import tf2onnx
        except ImportError:
            logger.warning("tf2onnx não instalado. Pulando exportação ONNX.")
            return {
                "success": False,
                "format": "onnx",
                "error": "tf2onnx não instalado (pip install tf2onnx)"
            }
        
        # Carregar modelo
        model = keras.models.load_model(model_path)
        
        # Converter para ONNX
        output_path = output_dir / "skin_cancer_model.onnx"
        
        spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
        model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec)
        
        with open(output_path, 'wb') as f:
            f.write(model_proto.SerializeToString())
        
        file_size = output_path.stat().st_size
        
        logger.info(f"Modelo ONNX exportado: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
        
        return {
            "success": True,
            "format": "onnx",
            "path": str(output_path),
            "size_bytes": file_size,
            "size_mb": file_size / 1024 / 1024
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar ONNX: {e}")
        return {
            "success": False,
            "format": "onnx",
            "error": str(e)
        }


def create_documentation(results: list, output_dir: Path):
    """
    Cria documentação dos modelos exportados
    
    Args:
        results: Lista de resultados de exportação
        output_dir: Diretório de saída
    """
    try:
        doc = []
        doc.append("# Modelos Exportados - Classificador de Câncer de Pele K230\n")
        doc.append(f"Data de exportação: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        doc.append("## Formatos Disponíveis\n\n")
        
        for result in results:
            if result["success"]:
                doc.append(f"### {result['format'].upper()}\n")
                doc.append(f"- **Arquivo**: `{Path(result['path']).name}`\n")
                doc.append(f"- **Tamanho**: {result['size_mb']:.2f} MB\n")
                
                if result['format'] == 'h5':
                    doc.append("- **Uso**: Modelo completo TensorFlow/Keras\n")
                    doc.append("- **Plataforma**: Python, TensorFlow\n")
                elif result['format'] == 'tflite_float32':
                    doc.append("- **Uso**: Inferência em dispositivos móveis (float32)\n")
                    doc.append("- **Plataforma**: Android, iOS, Edge Devices\n")
                elif result['format'] == 'tflite_quantized':
                    doc.append("- **Uso**: Inferência otimizada para K230 (INT8)\n")
                    doc.append("- **Plataforma**: K230, Microcontroladores\n")
                    doc.append("- **Otimização**: Quantização INT8 completa\n")
                elif result['format'] == 'onnx':
                    doc.append("- **Uso**: Interoperabilidade entre frameworks\n")
                    doc.append("- **Plataforma**: ONNX Runtime, PyTorch, etc.\n")
                
                doc.append("\n")
        
        doc.append("## Como Usar\n\n")
        doc.append("### TensorFlow/Keras (H5)\n")
        doc.append("```python\n")
        doc.append("import tensorflow as tf\n")
        doc.append("model = tf.keras.models.load_model('skin_cancer_model_export.h5')\n")
        doc.append("```\n\n")
        
        doc.append("### TFLite\n")
        doc.append("```python\n")
        doc.append("import tensorflow as tf\n")
        doc.append("interpreter = tf.lite.Interpreter(model_path='skin_cancer_k230_quantized.tflite')\n")
        doc.append("interpreter.allocate_tensors()\n")
        doc.append("```\n\n")
        
        doc.append("### ONNX\n")
        doc.append("```python\n")
        doc.append("import onnxruntime as ort\n")
        doc.append("session = ort.InferenceSession('skin_cancer_model.onnx')\n")
        doc.append("```\n\n")
        
        # Salvar documentação
        doc_path = output_dir / "README.md"
        with open(doc_path, 'w') as f:
            f.writelines(doc)
        
        logger.info(f"Documentação criada: {doc_path}")
        
    except Exception as e:
        logger.error(f"Erro ao criar documentação: {e}")


def export_all_formats(model_path: str) -> Dict[str, Any]:
    """
    Exporta modelo em todos os formatos disponíveis
    
    Args:
        model_path: Caminho do modelo H5 original
        
    Returns:
        Dict com resultados de todas as exportações
    """
    logger.info("=" * 60)
    logger.info("EXPORTAÇÃO DE MODELOS EM MÚLTIPLOS FORMATOS")
    logger.info("=" * 60)
    
    model_path = Path(model_path)
    
    if not model_path.exists():
        logger.error(f"Modelo não encontrado: {model_path}")
        return {
            "success": False,
            "error": f"Modelo não encontrado: {model_path}"
        }
    
    # Criar diretório de exportação
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Exportar em todos os formatos
    results = []
    
    results.append(export_h5(model_path, EXPORT_DIR))
    results.append(export_tflite_float32(model_path, EXPORT_DIR))
    results.append(export_tflite_quantized(model_path, EXPORT_DIR))
    results.append(export_onnx(model_path, EXPORT_DIR))
    
    # Criar documentação
    create_documentation(results, EXPORT_DIR)
    
    # Resumo
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    logger.info("=" * 60)
    logger.info(f"EXPORTAÇÃO CONCLUÍDA")
    logger.info(f"Sucesso: {len(successful)}/{len(results)}")
    if failed:
        logger.warning(f"Falhas: {[r['format'] for r in failed]}")
    logger.info(f"Diretório de exportação: {EXPORT_DIR}")
    logger.info("=" * 60)
    
    return {
        "success": len(successful) > 0,
        "total": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "results": results,
        "export_dir": str(EXPORT_DIR)
    }


def main():
    """Função principal"""
    
    parser = argparse.ArgumentParser(description="Exportação de modelos em múltiplos formatos")
    parser.add_argument("--model", type=str, 
                       default=str(MODELS_DIR / "skin_cancer_model.h5"),
                       help="Caminho do modelo H5 para exportar")
    
    args = parser.parse_args()
    
    result = export_all_formats(args.model)
    
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    # Importar pandas apenas se necessário
    try:
        import pandas as pd
    except ImportError:
        import datetime
        class pd:
            class Timestamp:
                @staticmethod
                def now():
                    class FakeTimestamp:
                        @staticmethod
                        def strftime(fmt):
                            return datetime.datetime.now().strftime(fmt)
                    return FakeTimestamp()
    
    main()
