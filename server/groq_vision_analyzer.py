#!/usr/bin/env python3
"""
Groq Vision API Integration for Skin Lesion Analysis
Integra a Groq Vision API para análise dermatoscópica
"""

import os
import base64
import requests
import json
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Modelo com suporte a visão (Llama 4 Scout)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqVisionAnalyzer:
    """
    Integração com Groq Vision API para análise de lesões de pele
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o analisador
        
        Args:
            api_key: Chave da API Groq (opcional)
        """
        self.api_key = api_key or GROQ_API_KEY
        self.model = GROQ_MODEL
        self.api_url = GROQ_API_URL
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY não encontrada - análise multimodal desabilitada")
    
    def analyze_lesion(
        self,
        image_path: str,
        classification_result: Dict[str, Any],
        gradcam_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Análise multimodal completa de lesão de pele com Groq
        
        Args:
            image_path: Caminho da imagem original
            classification_result: Resultado da classificação CNN
            gradcam_base64: Imagem Grad-CAM em base64 (opcional)
            
        Returns:
            Dict com análise completa
        """
        try:
            if not self.api_key:
                return self._generate_fallback_analysis(classification_result)
            
            logger.info("Iniciando análise multimodal com Groq Vision...")
            
            # Carregar e codificar imagem
            image_base64 = self._encode_image(image_path)
            
            # Criar prompt especializado
            prompt = self._create_dermatology_prompt(classification_result, bool(gradcam_base64))
            
            # Preparar mensagens para Groq (formato OpenAI)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Adicionar Grad-CAM se disponível
            if gradcam_base64:
                # Remover prefixo data:image/png;base64, se existir
                gradcam_clean = gradcam_base64.split(',')[1] if ',' in gradcam_base64 else gradcam_base64
                messages[0]["content"].insert(1, {
                    "type": "text",
                    "text": "\n\n**Mapa de Atenção (Grad-CAM):**"
                })
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{gradcam_clean}"
                    }
                })
            
            # Preparar payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 2048,
                "top_p": 0.95
            }
            
            # Fazer requisição à API Groq
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"Enviando requisição para Groq Vision: {self.model}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                logger.error(f"Erro API Groq: {response.status_code} - {error_data}")
                return self._generate_fallback_analysis(classification_result)
            
            # Parsear resposta
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                logger.error("Resposta sem choices")
                return self._generate_fallback_analysis(classification_result)
            
            # Extrair texto da análise
            analysis_text = result["choices"][0]["message"]["content"]
            
            if not analysis_text:
                logger.error("Análise vazia")
                return self._generate_fallback_analysis(classification_result)
            
            logger.info(f"Análise multimodal gerada com sucesso ({len(analysis_text)} chars)")
            
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "multimodal": True,
                "includes_gradcam": bool(gradcam_base64),
                "provider": "groq"
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na API Groq")
            return self._generate_fallback_analysis(classification_result)
        except Exception as e:
            logger.error(f"Erro ao gerar análise multimodal com Groq: {e}")
            logger.exception(e)
            return self._generate_fallback_analysis(classification_result)
    
    def _encode_image(self, image_path: str) -> str:
        """
        Codifica imagem em base64
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            String base64
        """
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _create_dermatology_prompt(self, classification_result: Dict[str, Any], has_gradcam: bool) -> str:
        """
        Cria prompt especializado para análise dermatológica
        
        Args:
            classification_result: Resultado da classificação
            has_gradcam: Se há mapa Grad-CAM disponível
            
        Returns:
            Prompt formatado
        """
        predicted_class = classification_result.get('class_name', 'Desconhecido')
        confidence = classification_result.get('confidence', 0.0)
        probabilities = classification_result.get('probabilities', {})
        
        prompt = f"""Você é um dermatologista especialista em análise de lesões de pele para residência médica.

**DADOS DA CLASSIFICAÇÃO AUTOMÁTICA (CNN):**
- Diagnóstico Predito: {predicted_class}
- Confiança: {confidence:.1f}%
- Probabilidades:
"""
        
        for class_name, prob in probabilities.items():
            prompt += f"  * {class_name}: {prob:.1f}%\n"
        
        if has_gradcam:
            prompt += "\n**MAPA DE ATENÇÃO (Grad-CAM):** Fornecido abaixo (áreas em vermelho indicam regiões mais relevantes para a classificação).\n"
        
        prompt += """
**TAREFA:**
Analise a imagem dermatoscópica fornecida e gere um relatório diagnóstico completo para estudo de residência em dermatologia, incluindo:

1. **Análise Visual Detalhada:**
   - Descreva padrões dermatoscópicos observados (rede pigmentar, glóbulos, estrias, véu azul-esbranquiçado, etc.)
   - Identifique assimetria, bordas, cores e diâmetro (critérios ABCD)
   - Avalie estruturas específicas (pontos, linhas, áreas sem estrutura)

2. **Correlação com Classificação CNN:**
   - Compare sua análise visual com o diagnóstico predito pelo modelo
   - Avalie se a confiança do modelo está alinhada com os achados visuais
   - Identifique possíveis discrepâncias ou pontos de atenção

3. **Diagnóstico Diferencial:**
   - Liste 2-3 diagnósticos diferenciais principais
   - Justifique cada diagnóstico com base nos achados

4. **Recomendações Clínicas:**
   - Sugira próximos passos (acompanhamento, biópsia, excisão, etc.)
   - Indique urgência (rotina, prioritário, urgente)
   - Mencione fatores de risco relevantes

5. **Nota Educacional:**
   - Destaque pontos de aprendizado para residentes
   - Cite referências ou critérios diagnósticos relevantes

**FORMATO:** Use Markdown com seções claras. Seja objetivo, preciso e educacional.

**IMPORTANTE:** Este é um sistema auxiliar de estudo. Sempre correlacione com história clínica e exame físico completo.
"""
        
        return prompt
    
    def _generate_fallback_analysis(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera análise básica quando Groq não está disponível
        
        Args:
            classification_result: Resultado da classificação
            
        Returns:
            Análise fallback
        """
        return {
            "success": False,
            "analysis": "",
            "model": "fallback",
            "multimodal": False,
            "error": "Groq Vision API indisponível",
            "provider": "groq"
        }


def get_groq_vision_analyzer():
    """
    Retorna instância do analisador Groq
    """
    return GroqVisionAnalyzer()
