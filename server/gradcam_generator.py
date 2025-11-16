#!/usr/bin/env python3
"""
Gerador de Grad-CAM usando pytorch-grad-cam
Converte modelo Keras/TensorFlow para PyTorch e gera visualizações
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

logger = logging.getLogger(__name__)


class GradCAMGenerator:
    """
    Gerador de Grad-CAM robusto usando implementação alternativa
    """
    
    def __init__(self, model):
        """
        Inicializa o gerador
        
        Args:
            model: Modelo Keras/TensorFlow
        """
        self.model = model
        self.img_size = (224, 224)
    
    def generate(self, image_path: str) -> str:
        """
        Gera visualização Grad-CAM
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            String base64 da imagem Grad-CAM
        """
        try:
            logger.info("Gerando Grad-CAM...")
            
            # Carregar e preprocessar imagem
            img_array = self._load_and_preprocess(image_path)
            
            # Obter última camada convolucional
            last_conv_layer_name = self._get_last_conv_layer()
            logger.info(f"Usando camada: {last_conv_layer_name}")
            
            # Criar modelo Grad-CAM
            grad_model = self._create_grad_model(last_conv_layer_name)
            
            # Computar heatmap
            heatmap = self._compute_heatmap(grad_model, img_array)
            
            # Sobrepor heatmap na imagem original
            superimposed = self._superimpose_heatmap(image_path, heatmap)
            
            # Converter para base64
            gradcam_base64 = self._to_base64(superimposed)
            
            logger.info("Grad-CAM gerado com sucesso")
            return f"data:image/png;base64,{gradcam_base64}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar Grad-CAM: {e}")
            logger.exception(e)
            # Retornar imagem original em caso de erro
            return self._fallback_image(image_path)
    
    def _load_and_preprocess(self, image_path: str) -> np.ndarray:
        """
        Carrega e preprocessa imagem
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Array numpy preprocessado
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Não foi possível carregar imagem: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.img_size)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def _get_last_conv_layer(self) -> str:
        """
        Obtém nome da última camada convolucional
        
        Returns:
            Nome da camada
        """
        # Procurar por MobileNetV2 base model
        for layer in self.model.layers:
            if 'mobilenetv2' in layer.name.lower():
                base_model = layer
                # Procurar última camada Conv2D no base model
                for sublayer in reversed(base_model.layers):
                    if isinstance(sublayer, keras.layers.Conv2D):
                        return sublayer.name
        
        # Fallback: procurar última Conv2D no modelo principal
        for layer in reversed(self.model.layers):
            if isinstance(layer, keras.layers.Conv2D):
                return layer.name
        
        raise ValueError("Nenhuma camada convolucional encontrada")
    
    def _create_grad_model(self, last_conv_layer_name: str):
        """
        Cria modelo para computar gradientes
        
        Args:
            last_conv_layer_name: Nome da última camada conv
            
        Returns:
            Modelo Keras
        """
        # Obter base model (MobileNetV2)
        base_model = None
        for layer in self.model.layers:
            if 'mobilenetv2' in layer.name.lower():
                base_model = layer
                break
        
        if base_model is None:
            raise ValueError("MobileNetV2 base model não encontrado")
        
        # Obter camada convolucional
        conv_layer = base_model.get_layer(last_conv_layer_name)
        
        # Criar modelo que retorna output da conv layer e predição final
        grad_model = keras.Model(
            inputs=self.model.input,
            outputs=[conv_layer.output, self.model.output]
        )
        
        return grad_model
    
    def _compute_heatmap(self, grad_model, img_array: np.ndarray) -> np.ndarray:
        """
        Computa heatmap Grad-CAM
        
        Args:
            grad_model: Modelo para gradientes
            img_array: Imagem preprocessada
            
        Returns:
            Heatmap normalizado
        """
        # Converter para tensor
        img_tensor = tf.convert_to_tensor(img_array)
        
        # Computar gradientes
        with tf.GradientTape() as tape:
            tape.watch(img_tensor)
            conv_outputs, predictions = grad_model(img_tensor, training=False)
            
            # Para classificação binária com sigmoid
            if predictions.shape[-1] == 1:
                class_channel = predictions[:, 0]
            else:
                # Para classificação multiclasse
                class_channel = predictions[:, tf.argmax(predictions[0])]
        
        # Gradientes da classe predita em relação aos outputs da conv layer
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Pooling global dos gradientes
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiplicar cada canal pelo seu peso (gradiente)
        conv_outputs = conv_outputs[0]
        pooled_grads = pooled_grads.numpy()
        conv_outputs = conv_outputs.numpy()
        
        for i in range(pooled_grads.shape[-1]):
            conv_outputs[:, :, i] *= pooled_grads[i]
        
        # Média dos canais ponderados
        heatmap = np.mean(conv_outputs, axis=-1)
        
        # ReLU e normalização
        heatmap = np.maximum(heatmap, 0)
        if heatmap.max() > 0:
            heatmap /= heatmap.max()
        
        return heatmap
    
    def _superimpose_heatmap(self, image_path: str, heatmap: np.ndarray) -> np.ndarray:
        """
        Sobrepõe heatmap na imagem original
        
        Args:
            image_path: Caminho da imagem original
            heatmap: Heatmap Grad-CAM
            
        Returns:
            Imagem com heatmap sobreposto
        """
        # Carregar imagem original
        img_original = cv2.imread(image_path)
        img_original = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)
        
        # Redimensionar heatmap para tamanho original
        heatmap_resized = cv2.resize(heatmap, (img_original.shape[1], img_original.shape[0]))
        
        # Converter heatmap para RGB usando colormap
        heatmap_colored = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Sobrepor com transparência
        superimposed = cv2.addWeighted(img_original, 0.6, heatmap_colored, 0.4, 0)
        
        return superimposed
    
    def _to_base64(self, image: np.ndarray) -> str:
        """
        Converte imagem para base64
        
        Args:
            image: Array numpy da imagem
            
        Returns:
            String base64
        """
        pil_img = Image.fromarray(image)
        buffer = BytesIO()
        pil_img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _fallback_image(self, image_path: str) -> str:
        """
        Retorna imagem original em caso de erro
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            String base64 da imagem original
        """
        try:
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return f"data:image/png;base64,{self._to_base64(img)}"
        except Exception as e:
            logger.error(f"Erro ao gerar fallback: {e}")
            return None
