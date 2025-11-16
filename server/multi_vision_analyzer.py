#!/usr/bin/env python3
"""
Sistema Multi-API de Análise de Visão com Fallback em Cascata
Tenta Gemini → Groq → Fallback CNN
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MultiVisionAnalyzer:
    """
    Analisador que tenta múltiplas APIs em cascata
    """
    
    def __init__(self):
        """
        Inicializa analisadores
        """
        self.gemini_analyzer = None
        self.groq_analyzer = None
        
        # Importar analisadores
        try:
            from gemini_vision_analyzer import GeminiVisionAnalyzer
            self.gemini_analyzer = GeminiVisionAnalyzer()
            logger.info("Gemini Vision Analyzer carregado")
        except Exception as e:
            logger.warning(f"Erro ao carregar Gemini Analyzer: {e}")
        
        try:
            from groq_vision_analyzer import GroqVisionAnalyzer
            self.groq_analyzer = GroqVisionAnalyzer()
            logger.info("Groq Vision Analyzer carregado")
        except Exception as e:
            logger.warning(f"Erro ao carregar Groq Analyzer: {e}")
    
    def analyze_lesion(
        self,
        image_path: str,
        classification_result: Dict[str, Any],
        gradcam_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Análise multimodal com fallback em cascata
        
        Ordem de tentativa:
        1. Gemini Vision API
        2. Groq Vision API
        3. Fallback CNN (gerado internamente)
        
        Args:
            image_path: Caminho da imagem
            classification_result: Resultado da classificação CNN
            gradcam_base64: Mapa Grad-CAM em base64
            
        Returns:
            Dict com análise completa
        """
        logger.info("Iniciando análise multimodal com fallback em cascata...")
        
        # Tentativa 1: Gemini Vision
        if self.gemini_analyzer:
            logger.info("Tentando Gemini Vision API...")
            result = self.gemini_analyzer.analyze_lesion(
                image_path=image_path,
                classification_result=classification_result,
                gradcam_base64=gradcam_base64
            )
            
            if result.get('success'):
                logger.info("✓ Gemini Vision API: Sucesso")
                result['provider'] = 'gemini'
                return result
            else:
                logger.warning(f"✗ Gemini Vision API falhou: {result.get('error', 'Unknown')}")
        
        # Tentativa 2: Groq Vision
        if self.groq_analyzer:
            logger.info("Tentando Groq Vision API...")
            result = self.groq_analyzer.analyze_lesion(
                image_path=image_path,
                classification_result=classification_result,
                gradcam_base64=gradcam_base64
            )
            
            if result.get('success'):
                logger.info("✓ Groq Vision API: Sucesso")
                result['provider'] = 'groq'
                return result
            else:
                logger.warning(f"✗ Groq Vision API falhou: {result.get('error', 'Unknown')}")
        
        # Tentativa 3: Fallback CNN
        logger.info("Usando fallback CNN (todas as APIs falharam)")
        return self._generate_cnn_fallback(classification_result)
    
    def _generate_cnn_fallback(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera análise baseada apenas em CNN quando todas as APIs falham
        
        Args:
            classification_result: Resultado da classificação
            
        Returns:
            Análise fallback
        """
        predicted_class = classification_result.get('class_name', 'Desconhecido')
        confidence = classification_result.get('confidence', 0.0)
        risk_level = classification_result.get('risk_level', 'INDETERMINADO')
        
        analysis = f"""## Relatório Diagnóstico Automatizado

**⚠️ NOTA:** Análise multimodal indisponível (Gemini e Groq falharam). Relatório baseado apenas em classificação CNN.

### 1. Resultado da Classificação

- **Diagnóstico Principal:** {predicted_class}
- **Confiança:** {confidence:.1f}%
- **Nível de Risco:** {risk_level}

### 2. Interpretação

"""
        
        if predicted_class == "Lesão Maligna" or predicted_class == "MALIGNO":
            analysis += """Esta lesão foi classificada como **potencialmente maligna** pelo modelo de deep learning.

**Achados Sugestivos:**
- Padrões dermatoscópicos compatíveis com malignidade
- Alta probabilidade de lesão suspeita

**Recomendações:**
- ⚠️ **URGENTE:** Encaminhar para dermatologista imediatamente
- Considerar biópsia excisional para confirmação histopatológica
- Não postergar avaliação especializada
- Documentação fotográfica seriada
- Avaliação de linfonodos regionais

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
- Autoexame mensal
- Proteção solar adequada (FPS 50+)

"""
        
        analysis += """### 3. Diagnóstico Diferencial

Consulte dermatologista para avaliação completa e diagnóstico diferencial apropriado.

### 4. Limitações

- Análise baseada apenas em classificação automática
- Sem avaliação visual detalhada por IA multimodal
- Requer correlação com história clínica e exame físico
- Sensibilidade/especificidade do modelo CNN: ~82%

### 5. Nota Importante

Este sistema é uma ferramenta auxiliar de estudo para residentes em dermatologia. **NÃO substitui avaliação clínica presencial** por dermatologista qualificado. Sempre correlacione com achados clínicos e história do paciente.

---
*Gerado por: Sistema de Classificação de Câncer de Pele K230*
*Modelo: MobileNetV2 treinado customizado (CNN apenas)*
"""
        
        return {
            "success": False,
            "analysis": analysis,
            "model": "cnn_only",
            "multimodal": False,
            "error": "Todas as APIs de visão falharam (Gemini, Groq)",
            "provider": "fallback"
        }


# Singleton
_multi_analyzer_instance = None

def get_multi_vision_analyzer():
    """
    Retorna instância singleton do analisador multi-API
    """
    global _multi_analyzer_instance
    if _multi_analyzer_instance is None:
        _multi_analyzer_instance = MultiVisionAnalyzer()
    return _multi_analyzer_instance
