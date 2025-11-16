"""
Módulo de Classificação de Câncer de Pele
Baseado no projeto: https://github.com/marceloclaro/pele
Adaptado para TensorFlow/Keras com MobileNetV2 e Grad-CAM
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import cv2
from PIL import Image
import io
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Classes do HAM10000 dataset
CLASSES = [
    'akiec',  # Actinic keratoses and intraepithelial carcinoma
    'bcc',    # Basal cell carcinoma
    'bkl',    # Benign keratosis-like lesions
    'df',     # Dermatofibroma
    'mel',    # Melanoma
    'nv',     # Melanocytic nevi
    'vasc'    # Vascular lesions
]

CLASS_NAMES_PT = {
    'akiec': 'Queratose Actínica / Carcinoma Intraepitelial',
    'bcc': 'Carcinoma Basocelular',
    'bkl': 'Lesões Benignas Queratose-like',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Nevos Melanocíticos',
    'vasc': 'Lesões Vasculares'
}

class SkinCancerClassifier:
    """
    Classificador de câncer de pele usando MobileNetV2 pré-treinado
    """
    
    def __init__(self, model_path=None):
        """
        Inicializa o classificador
        
        Args:
            model_path: Caminho para modelo treinado (opcional)
        """
        self.model = None
        self.img_size = (224, 224)
        
        if model_path:
            try:
                self.model = keras.models.load_model(model_path)
                logger.info(f"Modelo carregado de: {model_path}")
            except Exception as e:
                logger.warning(f"Não foi possível carregar modelo: {e}")
                self._create_base_model()
        else:
            self._create_base_model()
    
    def _create_base_model(self):
        """
        Cria modelo base MobileNetV2 pré-treinado
        """
        base_model = MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Congelar camadas base
        base_model.trainable = False
        
        # Adicionar camadas de classificação
        inputs = keras.Input(shape=(224, 224, 3))
        x = base_model(inputs, training=False)
        x = keras.layers.GlobalAveragePooling2D()(x)
        x = keras.layers.Dropout(0.5)(x)
        outputs = keras.layers.Dense(len(CLASSES), activation='softmax')(x)
        
        self.model = keras.Model(inputs, outputs)
        logger.info("Modelo base MobileNetV2 criado")
    
    def preprocess_image(self, img_data):
        """
        Pré-processa imagem para classificação
        
        Args:
            img_data: Dados da imagem (bytes, PIL Image, ou caminho)
            
        Returns:
            Tensor preprocessado e imagem PIL original
        """
        # Converter para PIL Image se necessário
        if isinstance(img_data, bytes):
            img = Image.open(io.BytesIO(img_data))
        elif isinstance(img_data, str):
            img = Image.open(img_data)
        else:
            img = img_data
        
        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar
        img_resized = img.resize(self.img_size)
        
        # Converter para array e preprocessar
        img_array = image.img_to_array(img_resized)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        return img_array, img_resized
    
    def predict(self, img_data):
        """
        Realiza predição em uma imagem
        
        Args:
            img_data: Dados da imagem
            
        Returns:
            dict com classe, confiança e probabilidades
        """
        img_array, img_pil = self.preprocess_image(img_data)
        
        # Predição
        predictions = self.model.predict(img_array, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        # Preparar resultado
        result = {
            'class': CLASSES[class_idx],
            'class_name': CLASS_NAMES_PT[CLASSES[class_idx]],
            'confidence': confidence,
            'probabilities': {
                CLASSES[i]: float(predictions[0][i])
                for i in range(len(CLASSES))
            }
        }
        
        logger.info(f"Predição: {result['class']} ({confidence:.2%})")
        return result
    
    def generate_gradcam(self, img_data, class_idx=None):
        """
        Gera mapa de calor Grad-CAM para interpretabilidade
        
        Args:
            img_data: Dados da imagem
            class_idx: Índice da classe (None = classe predita)
            
        Returns:
            Imagem com overlay do Grad-CAM (base64)
        """
        img_array, img_pil = self.preprocess_image(img_data)
        
        # Se class_idx não fornecido, usar classe predita
        if class_idx is None:
            preds = self.model.predict(img_array, verbose=0)
            class_idx = np.argmax(preds[0])
        
        # Criar modelo Grad-CAM
        last_conv_layer_name = self._get_last_conv_layer()
        grad_model = keras.Model(
            inputs=self.model.inputs,
            outputs=[
                self.model.get_layer(last_conv_layer_name).output,
                self.model.output
            ]
        )
        
        # Computar gradientes
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, class_idx]
        
        # Gradientes da classe em relação à última camada convolucional
        grads = tape.gradient(loss, conv_outputs)
        
        # Pooling dos gradientes
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiplicar cada canal pelo peso do gradiente
        conv_outputs = conv_outputs[0]
        pooled_grads = pooled_grads.numpy()
        conv_outputs = conv_outputs.numpy()
        
        for i in range(pooled_grads.shape[-1]):
            conv_outputs[:, :, i] *= pooled_grads[i]
        
        # Média dos canais para obter heatmap
        heatmap = np.mean(conv_outputs, axis=-1)
        
        # Normalizar heatmap
        heatmap = np.maximum(heatmap, 0)
        heatmap /= (np.max(heatmap) + 1e-10)
        
        # Redimensionar heatmap para tamanho da imagem
        heatmap = cv2.resize(heatmap, self.img_size)
        
        # Aplicar colormap
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        # Converter imagem PIL para array
        img_array_original = np.array(img_pil)
        
        # Sobrepor heatmap na imagem original
        superimposed = cv2.addWeighted(img_array_original, 0.6, heatmap, 0.4, 0)
        
        # Converter para base64
        _, buffer = cv2.imencode('.png', cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
        gradcam_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info("Grad-CAM gerado com sucesso")
        return f"data:image/png;base64,{gradcam_base64}"
    
    def _get_last_conv_layer(self):
        """
        Obtém nome da última camada convolucional do modelo
        """
        # Para MobileNetV2 dentro de um Sequential, precisamos acessar a camada base
        base_model = None
        for layer in self.model.layers:
            if 'mobilenetv2' in layer.name.lower():
                base_model = layer
                break
        
        if base_model:
            # Procurar última camada convolucional dentro do MobileNetV2
            for layer in reversed(base_model.layers):
                if 'Conv' in layer.__class__.__name__ or 'conv' in layer.name:
                    return f"{base_model.name}/{layer.name}"
        
        # Fallback: procurar em todas as camadas
        for layer in reversed(self.model.layers):
            if 'Conv' in layer.__class__.__name__:
                return layer.name
        
        return 'mobilenetv2_1.00_224'  # Fallback para a camada base


def get_classifier():
    """
    Retorna instância singleton do classificador
    """
    if not hasattr(get_classifier, '_instance'):
        get_classifier._instance = SkinCancerClassifier()
    return get_classifier._instance
