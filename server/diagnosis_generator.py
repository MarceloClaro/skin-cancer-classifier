"""
Gerador de Diagnósticos Automáticos usando API Gemini
Integra resultados de classificação e Grad-CAM para gerar relatórios médicos
"""

import os
import logging
import requests
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0")
GEMINI_MODEL = "models/gemini-2.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent"


class DiagnosisGenerator:
    """
    Gerador de diagnósticos automáticos para lesões de pele
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa o gerador de diagnósticos
        
        Args:
            api_key: Chave da API Gemini (opcional)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.api_url = GEMINI_API_URL
    
    def generate_diagnosis(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera diagnóstico automático baseado nos resultados da classificação
        
        Args:
            classification_result: Resultado da classificação contendo:
                - class: Classe predita
                - class_name: Nome da classe em português
                - confidence: Confiança da predição
                - probabilities: Probabilidades de todas as classes
                
        Returns:
            Dict com diagnóstico gerado
        """
        try:
            # Preparar contexto para o Gemini
            prompt = self._build_prompt(classification_result)
            
            # Chamar API Gemini
            response = self._call_gemini_api(prompt)
            
            if response:
                return {
                    'success': True,
                    'diagnosis': response,
                    'confidence': classification_result['confidence'],
                    'class': classification_result['class'],
                    'class_name': classification_result['class_name']
                }
            else:
                return {
                    'success': False,
                    'error': 'Falha ao gerar diagnóstico',
                    'diagnosis': self._get_fallback_diagnosis(classification_result)
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar diagnóstico: {e}")
            return {
                'success': False,
                'error': str(e),
                'diagnosis': self._get_fallback_diagnosis(classification_result)
            }
    
    def _build_prompt(self, result: Dict[str, Any]) -> str:
        """
        Constrói prompt para o Gemini baseado nos resultados
        """
        class_name = result['class_name']
        confidence = result['confidence']
        probabilities = result['probabilities']
        
        # Ordenar probabilidades
        sorted_probs = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]  # Top 3
        
        prob_text = "\n".join([
            f"  - {self._get_class_name_pt(cls)}: {prob:.1%}"
            for cls, prob in sorted_probs
        ])
        
        prompt = f"""Você é um assistente médico especializado em dermatologia, auxiliando residentes em dermatologia no estudo de lesões de pele.

**CONTEXTO DO EXAME:**
Um sistema de inteligência artificial baseado em deep learning (MobileNetV2) analisou uma imagem dermatoscópica e forneceu os seguintes resultados:

**RESULTADO DA CLASSIFICAÇÃO:**
- Diagnóstico Principal: {class_name}
- Confiança: {confidence:.1%}

**PROBABILIDADES DAS CLASSES:**
{prob_text}

**INSTRUÇÕES:**
Com base nos resultados acima, gere um relatório diagnóstico estruturado para fins educacionais de residência em dermatologia. O relatório deve incluir:

1. **Interpretação do Resultado**: Explique o que significa o diagnóstico principal e o nível de confiança
2. **Características Clínicas**: Descreva as características típicas desta lesão
3. **Diagnósticos Diferenciais**: Liste os principais diagnósticos diferenciais baseados nas outras probabilidades
4. **Recomendações**: Sugira próximos passos (biópsia, acompanhamento, etc.)
5. **Nota Educacional**: Adicione informações relevantes para residentes em dermatologia

**IMPORTANTE:**
- Use linguagem técnica apropriada para residentes médicos
- Seja objetivo e baseado em evidências
- Mencione que este é um sistema auxiliar e não substitui avaliação clínica
- Formate o texto em markdown para melhor legibilidade

Gere o relatório agora:"""

        return prompt
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Chama a API Gemini para gerar o diagnóstico
        """
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                    "topP": 0.95,
                    "topK": 40,
                }
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            return parts[0]['text']
                
                logger.warning(f"Resposta Gemini sem conteúdo: {data}")
                return None
            else:
                logger.error(f"Erro API Gemini: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao chamar API Gemini: {e}")
            return None
    
    def _get_fallback_diagnosis(self, result: Dict[str, Any]) -> str:
        """
        Retorna diagnóstico fallback quando API falha
        """
        class_name = result['class_name']
        confidence = result['confidence']
        
        diagnoses = {
            'akiec': {
                'desc': 'Queratose actínica ou carcinoma intraepitelial',
                'info': 'Lesão pré-maligna causada por exposição solar crônica. Requer acompanhamento e possível tratamento.',
                'action': 'Recomenda-se biópsia para confirmação histopatológica e avaliação de tratamento (crioterapia, tópicos, etc.).'
            },
            'bcc': {
                'desc': 'Carcinoma basocelular',
                'info': 'Tipo mais comum de câncer de pele, geralmente de crescimento lento e raramente metastático.',
                'action': 'Biópsia obrigatória para confirmação. Tratamento cirúrgico é geralmente indicado.'
            },
            'bkl': {
                'desc': 'Lesões benignas queratose-like',
                'info': 'Lesões benignas que incluem queratose seborreica e líquen plano-like. Geralmente não requerem tratamento.',
                'action': 'Acompanhamento clínico. Remoção apenas por razões estéticas ou se houver mudanças suspeitas.'
            },
            'df': {
                'desc': 'Dermatofibroma',
                'info': 'Nódulo fibroso benigno comum, geralmente assintomático.',
                'action': 'Não requer tratamento. Remoção cirúrgica apenas se sintomático ou por preferência do paciente.'
            },
            'mel': {
                'desc': 'Melanoma',
                'info': 'Tipo mais agressivo de câncer de pele com potencial metastático. Requer atenção imediata.',
                'action': 'URGENTE: Biópsia excisional e encaminhamento para oncologia. Estadiamento completo necessário.'
            },
            'nv': {
                'desc': 'Nevos melanocíticos (pintas)',
                'info': 'Lesões benignas comuns. A maioria não requer intervenção.',
                'action': 'Acompanhamento fotográfico. Remoção se houver mudanças suspeitas (regra ABCDE).'
            },
            'vasc': {
                'desc': 'Lesões vasculares',
                'info': 'Inclui hemangiomas, angiomas e outras lesões vasculares benignas.',
                'action': 'Geralmente benignas. Tratamento apenas se sintomáticas ou por razões estéticas.'
            }
        }
        
        class_key = result['class']
        info = diagnoses.get(class_key, {
            'desc': class_name,
            'info': 'Informação não disponível',
            'action': 'Consulte um dermatologista para avaliação completa'
        })
        
        return f"""## Relatório Diagnóstico Automatizado

**⚠️ NOTA:** Este diagnóstico foi gerado automaticamente. A API Gemini está temporariamente indisponível.

### Resultado da Classificação
- **Diagnóstico Principal:** {class_name}
- **Confiança:** {confidence:.1%}

### Descrição
{info['desc']}

### Informações Clínicas
{info['info']}

### Recomendações
{info['action']}

### Nota Importante
Este sistema é uma ferramenta auxiliar de estudo para residentes em dermatologia. **NÃO substitui avaliação clínica presencial** por dermatologista qualificado. Sempre correlacione com achados clínicos e história do paciente.

---
*Gerado por: Sistema de Classificação de Câncer de Pele K230*
"""
    
    def _get_class_name_pt(self, class_key: str) -> str:
        """
        Retorna nome da classe em português
        """
        names = {
            'akiec': 'Queratose Actínica / Carcinoma Intraepitelial',
            'bcc': 'Carcinoma Basocelular',
            'bkl': 'Lesões Benignas Queratose-like',
            'df': 'Dermatofibroma',
            'mel': 'Melanoma',
            'nv': 'Nevos Melanocíticos',
            'vasc': 'Lesões Vasculares'
        }
        return names.get(class_key, class_key)


def get_diagnosis_generator():
    """
    Retorna instância singleton do gerador de diagnósticos
    """
    if not hasattr(get_diagnosis_generator, '_instance'):
        get_diagnosis_generator._instance = DiagnosisGenerator()
    return get_diagnosis_generator._instance
