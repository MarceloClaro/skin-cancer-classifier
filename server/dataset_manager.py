"""
Gerenciador de Dataset Incremental para Retreinamento
Salva imagens classificadas organizadas por classe para melhorar modelo
"""

import os
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Diretório base para dataset incremental
DATASET_BASE_DIR = "/home/ubuntu/skin_cancer_classifier_k230_page/dataset_incremental"
METADATA_FILE = "metadata.json"


class DatasetManager:
    """
    Gerenciador de dataset incremental para retreinamento
    """
    
    def __init__(self, base_dir: str = DATASET_BASE_DIR):
        """
        Inicializa o gerenciador
        
        Args:
            base_dir: Diretório base para o dataset
        """
        self.base_dir = Path(base_dir)
        self.classes = ["BENIGNO", "MALIGNO"]
        self._initialize_structure()
    
    def _initialize_structure(self):
        """
        Inicializa estrutura de diretórios
        """
        # Criar diretório base
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar diretórios por classe
        for class_name in self.classes:
            class_dir = self.base_dir / class_name
            class_dir.mkdir(exist_ok=True)
        
        # Criar diretório de metadados
        metadata_dir = self.base_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        logger.info(f"Estrutura de dataset inicializada em: {self.base_dir}")
    
    def save_classified_image(
        self,
        image_path: str,
        classification_result: Dict[str, Any],
        user_id: Optional[str] = None,
        save_original: bool = True
    ) -> Dict[str, Any]:
        """
        Salva imagem classificada no dataset incremental
        
        Args:
            image_path: Caminho da imagem original
            classification_result: Resultado da classificação
            user_id: ID do usuário (opcional)
            save_original: Se deve salvar imagem original (não Grad-CAM)
            
        Returns:
            Dict com informações do salvamento
        """
        try:
            if not save_original:
                logger.info("Salvamento desabilitado (save_original=False)")
                return {"success": False, "reason": "Salvamento desabilitado"}
            
            # Extrair informações
            predicted_class = classification_result.get('class', 'UNKNOWN')
            confidence = classification_result.get('confidence', 0.0)
            
            # Validar classe
            if predicted_class not in self.classes:
                logger.warning(f"Classe inválida: {predicted_class}")
                return {"success": False, "reason": f"Classe inválida: {predicted_class}"}
            
            # Gerar hash da imagem para evitar duplicatas
            image_hash = self._calculate_image_hash(image_path)
            
            # Verificar se já existe
            if self._image_exists(image_hash):
                logger.info(f"Imagem já existe no dataset: {image_hash}")
                return {"success": False, "reason": "Imagem duplicada", "hash": image_hash}
            
            # Gerar nome único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{predicted_class}_{timestamp}_{image_hash[:8]}.png"
            
            # Caminho de destino
            dest_dir = self.base_dir / predicted_class
            dest_path = dest_dir / filename
            
            # Copiar imagem
            shutil.copy2(image_path, dest_path)
            logger.info(f"Imagem salva: {dest_path}")
            
            # Salvar metadados
            metadata = {
                "filename": filename,
                "class": predicted_class,
                "confidence": confidence,
                "probabilities": classification_result.get('probabilities', {}),
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "image_hash": image_hash,
                "original_path": str(image_path)
            }
            
            metadata_path = self.base_dir / "metadata" / f"{filename}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Metadados salvos: {metadata_path}")
            
            # Atualizar estatísticas
            self._update_statistics()
            
            return {
                "success": True,
                "filename": filename,
                "class": predicted_class,
                "path": str(dest_path),
                "hash": image_hash
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagem: {e}")
            logger.exception(e)
            return {"success": False, "error": str(e)}
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """
        Calcula hash MD5 da imagem
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Hash MD5
        """
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _image_exists(self, image_hash: str) -> bool:
        """
        Verifica se imagem já existe no dataset
        
        Args:
            image_hash: Hash da imagem
            
        Returns:
            True se existe
        """
        metadata_dir = self.base_dir / "metadata"
        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    if metadata.get('image_hash') == image_hash:
                        return True
            except Exception:
                continue
        return False
    
    def _update_statistics(self):
        """
        Atualiza estatísticas do dataset
        """
        try:
            stats = {
                "last_updated": datetime.now().isoformat(),
                "classes": {}
            }
            
            for class_name in self.classes:
                class_dir = self.base_dir / class_name
                count = len(list(class_dir.glob("*.png")))
                stats["classes"][class_name] = count
            
            stats["total"] = sum(stats["classes"].values())
            
            stats_path = self.base_dir / "statistics.json"
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"Estatísticas atualizadas: {stats}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do dataset
        
        Returns:
            Dict com estatísticas
        """
        try:
            stats_path = self.base_dir / "statistics.json"
            if stats_path.exists():
                with open(stats_path, 'r') as f:
                    return json.load(f)
            else:
                # Calcular estatísticas se não existir
                self._update_statistics()
                with open(stats_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"error": str(e)}
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Retorna informações completas do dataset
        
        Returns:
            Dict com informações
        """
        stats = self.get_statistics()
        
        return {
            "base_dir": str(self.base_dir),
            "classes": self.classes,
            "statistics": stats,
            "ready_for_training": stats.get("total", 0) >= 10  # Mínimo 10 imagens
        }


# Singleton
_manager_instance = None

def get_dataset_manager():
    """
    Retorna instância singleton do gerenciador
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DatasetManager()
    return _manager_instance
