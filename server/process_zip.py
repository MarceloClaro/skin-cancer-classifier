#!/usr/bin/env python3
"""
Script para Processar Upload de Dataset em ZIP
Extrai e valida imagens organizadas em pastas BENIGNO e MALIGNO
"""

import os
import sys
import json
import zipfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "dataset_incremental"
TEMP_DIR = BASE_DIR / "temp_upload"

# Formatos de imagem suportados
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}

# Classes válidas
VALID_CLASSES = {'BENIGNO', 'MALIGNO'}


def validate_image(image_path: Path) -> bool:
    """
    Valida se o arquivo é uma imagem válida
    
    Args:
        image_path: Caminho da imagem
        
    Returns:
        True se válida
    """
    try:
        # Verificar extensão
        if image_path.suffix not in SUPPORTED_FORMATS:
            logger.warning(f"Formato não suportado: {image_path.name}")
            return False
        
        # Tentar abrir com PIL
        with Image.open(image_path) as img:
            img.verify()
        
        # Verificar tamanho mínimo (32x32)
        with Image.open(image_path) as img:
            width, height = img.size
            if width < 32 or height < 32:
                logger.warning(f"Imagem muito pequena: {image_path.name} ({width}x{height})")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao validar imagem {image_path.name}: {e}")
        return False


def calculate_hash(file_path: Path) -> str:
    """
    Calcula hash MD5 do arquivo
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Hash MD5
    """
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def check_duplicate(image_hash: str) -> bool:
    """
    Verifica se imagem já existe no dataset
    
    Args:
        image_hash: Hash da imagem
        
    Returns:
        True se duplicada
    """
    metadata_dir = DATASET_DIR / "metadata"
    if not metadata_dir.exists():
        return False
    
    for metadata_file in metadata_dir.glob("*.json"):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                if metadata.get('image_hash') == image_hash:
                    return True
        except Exception:
            continue
    
    return False


def extract_zip(zip_path: str) -> Dict[str, Any]:
    """
    Extrai arquivo ZIP para diretório temporário
    
    Args:
        zip_path: Caminho do arquivo ZIP
        
    Returns:
        Dict com resultado da extração
    """
    try:
        # Criar diretório temporário
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
        TEMP_DIR.mkdir(parents=True)
        
        # Extrair ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)
        
        logger.info(f"ZIP extraído para: {TEMP_DIR}")
        
        return {
            "success": True,
            "temp_dir": str(TEMP_DIR)
        }
        
    except Exception as e:
        logger.error(f"Erro ao extrair ZIP: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def find_class_directories(root_dir: Path) -> Dict[str, Path]:
    """
    Encontra diretórios de classes no ZIP extraído
    
    Args:
        root_dir: Diretório raiz
        
    Returns:
        Dict mapeando classe -> caminho
    """
    class_dirs = {}
    
    # Procurar em até 2 níveis de profundidade
    for depth in range(3):
        for item in root_dir.rglob("*"):
            if item.is_dir() and item.name.upper() in VALID_CLASSES:
                class_name = item.name.upper()
                if class_name not in class_dirs:
                    class_dirs[class_name] = item
                    logger.info(f"Encontrado diretório: {class_name} em {item}")
    
    return class_dirs


def process_images(class_dirs: Dict[str, Path]) -> Dict[str, Any]:
    """
    Processa e copia imagens para o dataset
    
    Args:
        class_dirs: Dict mapeando classe -> caminho
        
    Returns:
        Dict com resultado do processamento
    """
    stats = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "duplicates": 0,
        "by_class": {}
    }
    
    for class_name, class_dir in class_dirs.items():
        class_stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "duplicates": 0
        }
        
        # Criar diretório de destino
        dest_dir = DATASET_DIR / class_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Processar imagens
        for image_file in class_dir.iterdir():
            if not image_file.is_file():
                continue
            
            class_stats["total"] += 1
            stats["total"] += 1
            
            # Validar imagem
            if not validate_image(image_file):
                class_stats["invalid"] += 1
                stats["invalid"] += 1
                continue
            
            # Verificar duplicata
            image_hash = calculate_hash(image_file)
            if check_duplicate(image_hash):
                logger.info(f"Imagem duplicada ignorada: {image_file.name}")
                class_stats["duplicates"] += 1
                stats["duplicates"] += 1
                continue
            
            # Copiar imagem
            timestamp = int(Path(image_file).stat().st_mtime * 1000)
            new_filename = f"{class_name}_{timestamp}_{image_hash[:8]}.png"
            dest_path = dest_dir / new_filename
            
            # Converter para PNG se necessário
            with Image.open(image_file) as img:
                # Converter para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(dest_path, 'PNG')
            
            # Salvar metadados
            metadata = {
                "filename": new_filename,
                "class": class_name,
                "image_hash": image_hash,
                "original_name": image_file.name,
                "source": "zip_upload",
                "timestamp": timestamp
            }
            
            metadata_path = DATASET_DIR / "metadata" / f"{new_filename}.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            class_stats["valid"] += 1
            stats["valid"] += 1
            
            logger.info(f"Imagem processada: {new_filename}")
        
        stats["by_class"][class_name] = class_stats
        logger.info(f"Classe {class_name}: {class_stats['valid']} válidas, {class_stats['invalid']} inválidas, {class_stats['duplicates']} duplicadas")
    
    return stats


def cleanup_temp():
    """Remove diretório temporário"""
    try:
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
            logger.info("Diretório temporário removido")
    except Exception as e:
        logger.error(f"Erro ao remover diretório temporário: {e}")


def process_zip_upload(zip_path: str) -> Dict[str, Any]:
    """
    Processa upload de ZIP completo
    
    Args:
        zip_path: Caminho do arquivo ZIP
        
    Returns:
        Dict com resultado completo
    """
    logger.info("=" * 60)
    logger.info(f"PROCESSANDO UPLOAD DE ZIP: {zip_path}")
    logger.info("=" * 60)
    
    try:
        # Extrair ZIP
        extract_result = extract_zip(zip_path)
        if not extract_result["success"]:
            return extract_result
        
        # Encontrar diretórios de classes
        class_dirs = find_class_directories(TEMP_DIR)
        
        if not class_dirs:
            return {
                "success": False,
                "error": "Nenhum diretório BENIGNO ou MALIGNO encontrado no ZIP"
            }
        
        logger.info(f"Encontradas {len(class_dirs)} classes: {list(class_dirs.keys())}")
        
        # Processar imagens
        stats = process_images(class_dirs)
        
        # Limpar temporário
        cleanup_temp()
        
        logger.info("=" * 60)
        logger.info(f"PROCESSAMENTO CONCLUÍDO")
        logger.info(f"Total: {stats['total']} | Válidas: {stats['valid']} | Inválidas: {stats['invalid']} | Duplicadas: {stats['duplicates']}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar ZIP: {e}")
        cleanup_temp()
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 process_zip.py <caminho_do_zip>")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    
    if not os.path.exists(zip_path):
        print(f"Erro: Arquivo não encontrado: {zip_path}")
        sys.exit(1)
    
    result = process_zip_upload(zip_path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
