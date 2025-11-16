"""
Classificador Binário de Câncer de Pele (BENIGNO vs MALIGNO)
Usa modelo treinado customizado
"""

import os
import numpy as np
import cv2
import base64
import logging
from io import BytesIO
from PIL import Image

import tensorflow as tf
from tensorflow import keras

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = '/home/ubuntu/skin_cancer_classifier_k230_page/models/skin_cancer_model.h5'
IMG_SIZE = (224, 224)

# Mapeamento de classes
CLASS_NAMES = {
    0: 'BENIGNO',
    1: 'MALIGNO'
}

CLASS_NAMES_PT = {
    0: 'Lesão Benigna',
    1: 'Lesão Maligna'
}

CLASS_DESCRIPTIONS = {
    'BENIGNO': 'Lesão benigna de pele sem características de malignidade',
    'MALIGNO': 'Lesão com características suspeitas de malignidade que requer avaliação médica urgente'
}


class BinarySkinClassifier:
    """
    Classificador binário de lesões de pele
    """
    
    def __init__(self, model_path=MODEL_PATH):
        """
        Inicializa o classificador
        
        Args:
            model_path: Caminho para o modelo treinado (.h5)
        """
        self.model_path = model_path
        self.model = None
        self.img_size = IMG_SIZE
        self._load_model()
    
    def _load_model(self):
        """
        Carrega o modelo treinado
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo não encontrado: {self.model_path}")
        
        logger.info(f"Carregando modelo de: {self.model_path}")
        self.model = keras.models.load_model(self.model_path)
        
        # Forçar construção do modelo com build() para definir inputs
        if not self.model.built:
            self.model.build(input_shape=(None, 224, 224, 3))
        
        # Inicializar modelo com predição dummy para garantir que todas as camadas sejam inicializadas
        import numpy as np
        dummy_input = np.zeros((1, 224, 224, 3), dtype=np.float32)
        _ = self.model.predict(dummy_input, verbose=0)
        
        logger.info("Modelo carregado, construído e inicializado com sucesso")
    
    def preprocess_image(self, image_path):
        """
        Pré-processa imagem para predição
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Array numpy preprocessado
        """
        # Carregar imagem
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Converter BGR para RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Redimensionar
        img = cv2.resize(img, self.img_size)
        
        # Normalizar (0-1)
        img = img.astype(np.float32) / 255.0
        
        # Adicionar dimensão do batch
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def predict(self, image_path):
        """
        Realiza predição em uma imagem
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dict com resultados da classificação
        """
        # Preprocessar imagem
        img = self.preprocess_image(image_path)
        
        # Predição
        prediction = self.model.predict(img, verbose=0)[0][0]
        
        # Converter para classe
        predicted_class = int(prediction > 0.5)
        confidence = float(prediction if predicted_class == 1 else 1 - prediction)
        
        # Preparar resultado
        result = {
            'class': CLASS_NAMES[predicted_class],
            'class_name': CLASS_NAMES_PT[predicted_class],
            'description': CLASS_DESCRIPTIONS[CLASS_NAMES[predicted_class]],
            'confidence': confidence,
            'probabilities': {
                'BENIGNO': float(1 - prediction),
                'MALIGNO': float(prediction)
            },
            'risk_level': self._get_risk_level(predicted_class, confidence)
        }
        
        logger.info(f"Predição: {result['class']} ({confidence:.2%})")
        
        return result
    
    def _get_risk_level(self, predicted_class, confidence):
        """
        Determina nível de risco baseado na predição
        """
        if predicted_class == 0:  # BENIGNO
            if confidence > 0.8:
                return 'BAIXO'
            elif confidence > 0.6:
                return 'MODERADO-BAIXO'
            else:
                return 'MODERADO'
        else:  # MALIGNO
            if confidence > 0.8:
                return 'ALTO'
            elif confidence > 0.6:
                return 'MODERADO-ALTO'
            else:
                return 'MODERADO'
    
    def generate_gradcam(self, image_path):
        """
        Gera visualização Grad-CAM usando GradCAMGenerator
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            String base64 da imagem Grad-CAM
        """
        try:
            from gradcam_generator import GradCAMGenerator
            
            logger.info("Gerando Grad-CAM com GradCAMGenerator...")
            generator = GradCAMGenerator(self.model)
            gradcam_base64 = generator.generate(image_path)
            
            return gradcam_base64
            
        except Exception as e:
            logger.error(f"Erro ao gerar Grad-CAM: {e}")
            # Retornar imagem original em caso de erro
            img_original = cv2.imread(image_path)
            img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_original)
            buffer = BytesIO()
            pil_img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
    
    def save_to_dataset(self, image_path: str, predicted_class: str, confidence: float) -> dict:
        """
        Salva imagem no dataset incremental para retreinamento contínuo
        
        Args:
            image_path: Caminho da imagem original
            predicted_class: Classe predita (BENIGNO/MALIGNO)
            confidence: Confiança da predição (0-1)
        
        Returns:
            dict: Informações sobre o salvamento
        """
        import hashlib
        import shutil
        from datetime import datetime
        
        try:
            # Diretório base do dataset incremental
            dataset_base = '/home/ubuntu/skin_cancer_classifier_k230_page/dataset_incremental'
            class_dir = os.path.join(dataset_base, predicted_class)
            
            # Criar diretório se não existir
            os.makedirs(class_dir, exist_ok=True)
            
            # Calcular hash MD5 da imagem
            with open(image_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Verificar se imagem já existe (por hash)
            existing_files = os.listdir(class_dir)
            for existing_file in existing_files:
                if file_hash in existing_file:
                    logger.info(f"Imagem duplicada detectada (hash: {file_hash[:8]})")
                    return {
                        "success": False,
                        "reason": "duplicate",
                        "hash": file_hash,
                        "existing_file": existing_file
                    }
            
            # Gerar nome do arquivo com timestamp e hash
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = os.path.splitext(image_path)[1]
            new_filename = f"{predicted_class}_{timestamp}_{file_hash[:8]}{extension}"
            destination_path = os.path.join(class_dir, new_filename)
            
            # Copiar imagem
            shutil.copy2(image_path, destination_path)
            
            logger.info(f"Imagem salva no dataset: {destination_path}")
            
            return {
                "success": True,
                "path": destination_path,
                "hash": file_hash,
                "filename": new_filename,
                "class": predicted_class,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar no dataset: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_last_conv_layer(self):
        """
        Obtém nome da última camada convolucional
        """
        logger.info("Buscando última camada convolucional...")
        logger.info(f"Camadas do modelo: {[layer.name for layer in self.model.layers]}")
        
        # Procurar MobileNetV2 base model
        base_model = None
        for layer in self.model.layers:
            if 'mobilenetv2' in layer.name.lower():
                base_model = layer
                logger.info(f"Base model encontrado: {layer.name}")
                break
        
        if base_model and hasattr(base_model, 'layers'):
            # Listar camadas do MobileNetV2
            logger.info(f"Camadas do MobileNetV2: {[l.name for l in base_model.layers[-10:]]}")
            
            # Procurar última camada convolucional
            for layer in reversed(base_model.layers):
                layer_class = layer.__class__.__name__
                if 'Conv' in layer_class:
                    layer_name = layer.name
                    logger.info(f"Última camada conv encontrada: {layer_name} (tipo: {layer_class})")
                    return layer_name
        
        # Fallback: usar camada antes do pooling
        logger.warning("Usando fallback: camada mobilenetv2_1.00_224")
        return 'mobilenetv2_1.00_224'


# Singleton
_classifier_instance = None

def get_binary_classifier():
    """
    Retorna instância singleton do classificador binário
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = BinarySkinClassifier()
    return _classifier_instance
