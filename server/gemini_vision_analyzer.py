"""
Análise Multimodal de Lesões de Pele com Gemini Vision API
Combina análise de imagem + dados de classificação para diagnóstico avançado
"""

import os
import logging
import base64
import requests
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "models/gemini-2.0-flash-exp"  # Suporta visão
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent"


class GeminiVisionAnalyzer:
    """
    Analisador multimodal de lesões de pele usando Gemini Vision
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o analisador
        
        Args:
            api_key: Chave da API Gemini (opcional)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.api_url = GEMINI_API_URL
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não encontrada - análise multimodal desabilitada")
    
    def analyze_lesion(
        self,
        image_path: str,
        classification_result: Dict[str, Any],
        gradcam_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Análise multimodal completa de lesão de pele
        
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
            
            logger.info("Iniciando análise multimodal com Gemini Vision...")
            
            # Carregar e codificar imagem
            image_base64 = self._encode_image(image_path)
            
            # Criar prompt especializado
            prompt = self._create_dermatology_prompt(classification_result, bool(gradcam_base64))
            
            # Preparar payload para Gemini Vision
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.4,  # Mais determinístico para medicina
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            # Adicionar Grad-CAM se disponível
            if gradcam_base64:
                # Remover prefixo data:image/png;base64,
                gradcam_clean = gradcam_base64.split(',')[1] if ',' in gradcam_base64 else gradcam_base64
                payload["contents"][0]["parts"].append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": gradcam_clean
                    }
                })
                payload["contents"][0]["parts"].insert(1, {
                    "text": "**Mapa de Atenção (Grad-CAM):**"
                })
            
            # Fazer requisição à API
            headers = {"Content-Type": "application/json"}
            url = f"{self.api_url}?key={self.api_key}"
            
            logger.info(f"Enviando requisição para Gemini Vision: {self.model}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                logger.error(f"Erro API Gemini: {response.status_code} - {error_data}")
                return self._generate_fallback_analysis(classification_result)
            
            # Parsear resposta
            result = response.json()
            
            if "candidates" not in result or not result["candidates"]:
                logger.error("Resposta sem candidates")
                return self._generate_fallback_analysis(classification_result)
            
            candidate = result["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                logger.error("Resposta sem content/parts")
                return self._generate_fallback_analysis(classification_result)
            
            # Extrair texto da análise
            analysis_text = candidate["content"]["parts"][0].get("text", "")
            
            if not analysis_text:
                logger.error("Análise vazia")
                return self._generate_fallback_analysis(classification_result)
            
            logger.info(f"Análise multimodal gerada com sucesso ({len(analysis_text)} chars)")
            
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "multimodal": True,
                "includes_gradcam": bool(gradcam_base64)
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout na API Gemini")
            return self._generate_fallback_analysis(classification_result)
        except Exception as e:
            logger.error(f"Erro ao gerar análise multimodal: {e}")
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
        Gera análise básica quando Gemini não está disponível
        
        Args:
            classification_result: Resultado da classificação
            
        Returns:
            Análise fallback
        """
        predicted_class = classification_result.get('class_name', 'Desconhecido')
        confidence = classification_result.get('confidence', 0.0)
        risk_level = classification_result.get('risk_level', 'INDETERMINADO')
        
        analysis = f"""## Relatório Diagnóstico Automatizado

**⚠️ NOTA:** Análise multimodal com Gemini Vision indisponível. Relatório baseado apenas em classificação CNN.

### 1. Resultado da Classificação

- **Diagnóstico Principal:** {predicted_class}
- **Confiança:** {confidence:.1f}%
- **Nível de Risco:** {risk_level}

### 2. Interpretação

"""
        
        if predicted_class == "Lesão Maligna":
            analysis += """Esta lesão foi classificada como **potencialmente maligna** pelo modelo de deep learning.

**Achados Sugestivos:**
- Padrões dermatoscópicos compatíveis com malignidade
- Alta probabilidade de lesão suspeita

**Recomendações:**
- ⚠️ **URGENTE:** Encaminhar para dermatologista imediatamente
- Considerar biópsia excisional para confirmação histopatológica
- Não postergar avaliação especializada

"""
        else:
            analysis += """Esta lesão foi classificada como **provavelmente benigna** pelo modelo de deep learning.

**Achados Sugestivos:**
- Padrões dermatoscópicos compatíveis com lesão benigna
- Baixo risco de malignidade

**Recomendações:**
- Acompanhamento dermatológico de rotina
- Monitorar mudanças (tamanho, cor, forma)
- Fotodocumentação para comparação futura

"""
        
        analysis += """### 3. Diagnóstico Diferencial

Consulte dermatologista para avaliação completa e diagnóstico diferencial apropriado.

### 4. Limitações

- Análise baseada apenas em classificação automática
- Sem avaliação visual detalhada por especialista
- Requer correlação com história clínica e exame físico

### 5. Nota Importante

Este sistema é uma ferramenta auxiliar de estudo para residentes em dermatologia. **NÃO substitui avaliação clínica presencial** por dermatologista qualificado. Sempre correlacione com achados clínicos e história do paciente.

---
*Gerado por: Sistema de Classificação de Câncer de Pele K230*
*Modelo: MobileNetV2 treinado customizado*
"""
        
        return {
            "success": False,
            "analysis": analysis,
            "model": "fallback",
            "multimodal": False,
            "error": "Gemini Vision API indisponível"
        }


# Singleton
_analyzer_instance = None

def get_gemini_vision_analyzer():
    """
    Retorna instância singleton do analisador
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GeminiVisionAnalyzer()
    return _analyzer_instance
