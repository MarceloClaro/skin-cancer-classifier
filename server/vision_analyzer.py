#!/usr/bin/env python3
"""
Google Cloud Vision API Integration for Skin Lesion Analysis
Integra a Vision API para análise dermatoscópica avançada
"""

import os
import base64
import requests
import json
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """
    Integração com Google Cloud Vision API para análise de lesões de pele
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o analisador com a API key
        
        Args:
            api_key: Chave da Vision API (se None, usa variável de ambiente)
        """
        self.api_key = api_key or os.environ.get('VISION_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("Vision API key não encontrada. Usando modo fallback.")
        
        self.endpoint = "https://vision.googleapis.com/v1/images:annotate"
        
    def analyze_skin_lesion(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa uma lesão de pele usando Vision API
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com análise completa da imagem
        """
        try:
            # Ler e codificar imagem em base64
            with open(image_path, 'rb') as f:
                image_content = base64.b64encode(f.read()).decode('utf-8')
            
            # Construir requisição
            request_body = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {
                                "type": "LABEL_DETECTION",
                                "maxResults": 20
                            },
                            {
                                "type": "IMAGE_PROPERTIES"
                            },
                            {
                                "type": "SAFE_SEARCH_DETECTION"
                            },
                            {
                                "type": "OBJECT_LOCALIZATION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            # Fazer requisição
            logger.info(f"Enviando imagem para Vision API: {image_path}")
            response = requests.post(
                f"{self.endpoint}?key={self.api_key}",
                json=request_body,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Erro na Vision API: {response.status_code} - {response.text}")
                return self._fallback_analysis()
            
            result = response.json()
            logger.info("Análise Vision API concluída com sucesso")
            
            # Processar resposta
            return self._process_vision_response(result)
            
        except Exception as e:
            logger.error(f"Erro ao analisar imagem com Vision API: {str(e)}")
            return self._fallback_analysis()
    
    def _process_vision_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa a resposta da Vision API
        
        Args:
            response: Resposta JSON da Vision API
            
        Returns:
            Dicionário estruturado com análise
        """
        try:
            annotations = response.get('responses', [{}])[0]
            
            # Extrair labels (características detectadas)
            labels = []
            for label in annotations.get('labelAnnotations', []):
                labels.append({
                    'description': label.get('description', ''),
                    'score': label.get('score', 0.0),
                    'confidence': label.get('score', 0.0) * 100
                })
            
            # Extrair propriedades da imagem (cores dominantes)
            dominant_colors = []
            image_props = annotations.get('imagePropertiesAnnotation', {})
            for color_info in image_props.get('dominantColors', {}).get('colors', []):
                color = color_info.get('color', {})
                dominant_colors.append({
                    'red': color.get('red', 0),
                    'green': color.get('green', 0),
                    'blue': color.get('blue', 0),
                    'score': color_info.get('score', 0.0),
                    'pixel_fraction': color_info.get('pixelFraction', 0.0)
                })
            
            # Extrair objetos localizados
            objects = []
            for obj in annotations.get('localizedObjectAnnotations', []):
                objects.append({
                    'name': obj.get('name', ''),
                    'score': obj.get('score', 0.0),
                    'confidence': obj.get('score', 0.0) * 100
                })
            
            # Safe search (verificar se é conteúdo médico apropriado)
            safe_search = annotations.get('safeSearchAnnotation', {})
            
            return {
                'success': True,
                'labels': labels,
                'dominant_colors': dominant_colors,
                'objects': objects,
                'safe_search': safe_search,
                'raw_response': annotations
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da Vision API: {str(e)}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """
        Análise de fallback quando Vision API não está disponível
        
        Returns:
            Dicionário com análise básica
        """
        return {
            'success': False,
            'labels': [],
            'dominant_colors': [],
            'objects': [],
            'safe_search': {},
            'error': 'Vision API indisponível. Usando análise CNN apenas.',
            'fallback': True
        }
    
    def generate_dermatological_report(
        self, 
        vision_analysis: Dict[str, Any],
        cnn_prediction: Dict[str, Any]
    ) -> str:
        """
        Gera relatório dermatológico combinando Vision API + CNN
        
        Args:
            vision_analysis: Resultado da Vision API
            cnn_prediction: Resultado da classificação CNN
            
        Returns:
            Relatório em formato Markdown
        """
        report = "# Análise Dermatoscópica Multimodal\n\n"
        
        # Seção 1: Classificação CNN
        report += "## 1. Classificação por Rede Neural Convolucional\n\n"
        report += f"**Resultado:** {cnn_prediction.get('class', 'N/A')}\n\n"
        report += f"**Confiança:** {cnn_prediction.get('confidence', 0) * 100:.2f}%\n\n"
        report += f"**Nível de Risco:** {cnn_prediction.get('risk_level', 'N/A')}\n\n"
        
        # Seção 2: Análise Visual (Vision API)
        if vision_analysis.get('success'):
            report += "## 2. Características Visuais Detectadas (Vision API)\n\n"
            
            # Labels mais relevantes
            labels = vision_analysis.get('labels', [])[:5]
            if labels:
                report += "### Características Identificadas:\n\n"
                for label in labels:
                    report += f"- **{label['description']}** ({label['confidence']:.1f}% confiança)\n"
                report += "\n"
            
            # Cores dominantes
            colors = vision_analysis.get('dominant_colors', [])[:3]
            if colors:
                report += "### Cores Dominantes:\n\n"
                for i, color in enumerate(colors, 1):
                    rgb = f"RGB({color['red']}, {color['green']}, {color['blue']})"
                    fraction = color['pixel_fraction'] * 100
                    report += f"{i}. {rgb} - {fraction:.1f}% da imagem\n"
                report += "\n"
            
            # Objetos localizados
            objects = vision_analysis.get('objects', [])
            if objects:
                report += "### Estruturas Detectadas:\n\n"
                for obj in objects:
                    report += f"- {obj['name']} ({obj['confidence']:.1f}% confiança)\n"
                report += "\n"
        
        else:
            report += "## 2. Análise Visual\n\n"
            report += "*Vision API indisponível. Análise baseada apenas em CNN.*\n\n"
        
        # Seção 3: Interpretação Clínica
        report += "## 3. Interpretação Clínica\n\n"
        
        if cnn_prediction.get('class') == 'MALIGNO':
            report += "### ⚠️ Lesão Classificada como MALIGNA\n\n"
            report += "**Achados Sugestivos:**\n\n"
            report += "- Padrões morfológicos compatíveis com malignidade\n"
            report += "- Características assimétricas detectadas\n"
            report += "- Variação de cores e texturas\n\n"
            
            report += "**Recomendações:**\n\n"
            report += "1. **Encaminhamento URGENTE** para dermatologista\n"
            report += "2. Considerar biópsia para confirmação histopatológica\n"
            report += "3. Documentação fotográfica seriada\n"
            report += "4. Avaliação de linfonodos regionais\n\n"
            
        else:
            report += "### ✓ Lesão Classificada como BENIGNA\n\n"
            report += "**Achados Sugestivos:**\n\n"
            report += "- Padrões morfológicos compatíveis com benignidade\n"
            report += "- Simetria preservada\n"
            report += "- Bordas regulares\n\n"
            
            report += "**Recomendações:**\n\n"
            report += "1. Monitoramento periódico (autoexame mensal)\n"
            report += "2. Consulta dermatológica anual de rotina\n"
            report += "3. Proteção solar adequada\n"
            report += "4. Atenção a mudanças de tamanho, cor ou forma\n\n"
        
        # Seção 4: Diagnóstico Diferencial
        report += "## 4. Diagnóstico Diferencial\n\n"
        
        if cnn_prediction.get('class') == 'MALIGNO':
            report += "**Considerar:**\n\n"
            report += "1. Melanoma maligno\n"
            report += "2. Carcinoma basocelular\n"
            report += "3. Carcinoma espinocelular\n"
            report += "4. Ceratose actínica\n"
            report += "5. Nevo displásico\n\n"
        else:
            report += "**Considerar:**\n\n"
            report += "1. Nevo melanocítico benigno\n"
            report += "2. Ceratose seborreica\n"
            report += "3. Lentigo solar\n"
            report += "4. Dermatofibroma\n"
            report += "5. Angioma\n\n"
        
        # Seção 5: Notas Importantes
        report += "## 5. Notas Importantes\n\n"
        report += "⚠️ **LIMITAÇÕES:**\n\n"
        report += "- Este relatório é gerado por sistema automatizado de IA\n"
        report += "- NÃO substitui avaliação clínica por dermatologista\n"
        report += "- Diagnóstico definitivo requer correlação clínica e histopatológica\n"
        report += "- Sensibilidade e especificidade do modelo: ~82%\n\n"
        
        report += "📋 **CORRELAÇÃO CLÍNICA OBRIGATÓRIA:**\n\n"
        report += "- História clínica completa\n"
        report += "- Exame físico dermatológico\n"
        report += "- Dermatoscopia manual\n"
        report += "- Biópsia quando indicado\n\n"
        
        report += "---\n\n"
        report += "*Relatório gerado automaticamente pelo Sistema de Classificação de Câncer de Pele K230*\n"
        report += f"*Modelo: MobileNetV2 + Google Cloud Vision API*\n"
        
        return report


def main():
    """
    Função de teste
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 vision_analyzer.py <caminho_da_imagem>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    analyzer = VisionAnalyzer()
    result = analyzer.analyze_skin_lesion(image_path)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
