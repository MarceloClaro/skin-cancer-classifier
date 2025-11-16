#!/usr/bin/env python3
"""
Script para download e preparação do dataset HAM10000
Dataset: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
"""

import os
import sys
import json
import shutil
from pathlib import Path
import pandas as pd
from PIL import Image
import requests
from tqdm import tqdm

# Configurações
DATASET_DIR = Path("/home/ubuntu/skin_cancer_classifier_k230_page/datasets/ham10000")
RAW_DIR = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"
METADATA_FILE = DATASET_DIR / "metadata.json"

# Mapeamento de classes HAM10000 para binário
CLASS_MAPPING = {
    "mel": "MALIGNO",  # Melanoma
    "bcc": "MALIGNO",  # Basal cell carcinoma
    "akiec": "MALIGNO",  # Actinic keratoses
    "bkl": "BENIGNO",  # Benign keratosis-like lesions
    "df": "BENIGNO",  # Dermatofibroma
    "nv": "BENIGNO",  # Melanocytic nevi
    "vasc": "BENIGNO",  # Vascular lesions
}


def create_directories():
    """Criar estrutura de diretórios"""
    print("📁 Criando estrutura de diretórios...")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    (PROCESSED_DIR / "BENIGNO").mkdir(exist_ok=True)
    (PROCESSED_DIR / "MALIGNO").mkdir(exist_ok=True)
    print("✅ Diretórios criados")


def download_ham10000():
    """
    Download do dataset HAM10000
    
    NOTA: Este script assume que você tem o Kaggle API configurado.
    Para configurar:
    1. Instale: pip install kaggle
    2. Configure credenciais: https://github.com/Kaggle/kaggle-api#api-credentials
    3. Execute: kaggle datasets download -d kmader/skin-cancer-mnist-ham10000
    """
    print("\n📥 Baixando dataset HAM10000...")
    print("⚠️  NOTA: Você precisa ter o Kaggle API configurado")
    print("⚠️  Execute manualmente: kaggle datasets download -d kmader/skin-cancer-mnist-ham10000")
    print("⚠️  E extraia os arquivos em:", RAW_DIR)
    
    # Verificar se já existe
    if (RAW_DIR / "HAM10000_metadata.csv").exists():
        print("✅ Dataset já baixado")
        return True
    
    print("\n❌ Dataset não encontrado. Por favor, baixe manualmente.")
    print("\nPasso a passo:")
    print("1. Acesse: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
    print("2. Baixe o dataset")
    print(f"3. Extraia em: {RAW_DIR}")
    return False


def process_dataset():
    """Processar e organizar o dataset"""
    print("\n🔄 Processando dataset...")
    
    # Verificar se metadata existe
    metadata_path = RAW_DIR / "HAM10000_metadata.csv"
    if not metadata_path.exists():
        print(f"❌ Arquivo de metadata não encontrado: {metadata_path}")
        return False
    
    # Carregar metadata
    print("📊 Carregando metadata...")
    df = pd.read_csv(metadata_path)
    print(f"✅ {len(df)} imagens encontradas")
    
    # Estatísticas
    print("\n📈 Estatísticas do dataset:")
    print(df['dx'].value_counts())
    
    # Processar imagens
    print("\n🖼️  Processando imagens...")
    processed_count = {"BENIGNO": 0, "MALIGNO": 0}
    errors = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processando"):
        image_id = row['image_id']
        dx = row['dx']
        binary_class = CLASS_MAPPING.get(dx, "BENIGNO")
        
        # Procurar imagem (pode estar em diferentes pastas)
        image_paths = [
            RAW_DIR / f"{image_id}.jpg",
            RAW_DIR / "HAM10000_images_part_1" / f"{image_id}.jpg",
            RAW_DIR / "HAM10000_images_part_2" / f"{image_id}.jpg",
        ]
        
        source_path = None
        for path in image_paths:
            if path.exists():
                source_path = path
                break
        
        if source_path is None:
            errors.append(f"Imagem não encontrada: {image_id}")
            continue
        
        # Copiar para diretório processado
        dest_path = PROCESSED_DIR / binary_class / f"{image_id}_{dx}.jpg"
        
        try:
            # Verificar e redimensionar se necessário
            img = Image.open(source_path)
            if img.size != (224, 224):
                img = img.resize((224, 224), Image.LANCZOS)
            img.save(dest_path, quality=95)
            processed_count[binary_class] += 1
        except Exception as e:
            errors.append(f"Erro ao processar {image_id}: {str(e)}")
    
    # Salvar metadata
    metadata = {
        "dataset": "HAM10000",
        "total_images": len(df),
        "processed": {
            "BENIGNO": processed_count["BENIGNO"],
            "MALIGNO": processed_count["MALIGNO"],
        },
        "class_mapping": CLASS_MAPPING,
        "errors": errors,
    }
    
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Processamento concluído!")
    print(f"   BENIGNO: {processed_count['BENIGNO']} imagens")
    print(f"   MALIGNO: {processed_count['MALIGNO']} imagens")
    print(f"   Erros: {len(errors)}")
    
    if errors:
        print("\n⚠️  Erros encontrados:")
        for error in errors[:10]:
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... e mais {len(errors) - 10} erros")
    
    return True


def create_splits():
    """Criar splits de treino/validação/teste"""
    print("\n📊 Criando splits de treino/validação/teste...")
    
    # TODO: Implementar splits estratificados
    print("⚠️  Splits serão criados durante o treinamento")
    

def main():
    """Função principal"""
    print("=" * 60)
    print("🔬 Preparação do Dataset HAM10000")
    print("=" * 60)
    
    # Criar diretórios
    create_directories()
    
    # Download (manual)
    if not download_ham10000():
        print("\n❌ Por favor, baixe o dataset manualmente e execute novamente")
        return 1
    
    # Processar dataset
    if not process_dataset():
        print("\n❌ Erro ao processar dataset")
        return 1
    
    # Criar splits
    create_splits()
    
    print("\n" + "=" * 60)
    print("✅ Preparação concluída com sucesso!")
    print("=" * 60)
    print(f"\n📁 Dataset processado em: {PROCESSED_DIR}")
    print(f"📄 Metadata salvo em: {METADATA_FILE}")
    print("\n🚀 Próximo passo: Execute o treinamento com train_model_enhanced.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
