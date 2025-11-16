#!/usr/bin/python3.11
"""
Wrapper robusto para classificação de lesões de pele
Implementa logs detalhados e tratamento de erros rigoroso
"""

import sys
import json
import logging
import traceback
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/skin_classifier.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

# Importar módulos do projeto
sys.path.insert(0, str(Path(__file__).parent))

try:
    from binary_skin_classifier import BinarySkinClassifier
    from diagnosis_generator import generate_diagnosis
    from audit_logger import AuditLogger
    from vision_analyzer import VisionAnalyzer
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    print(json.dumps({
        "success": False,
        "error": {
            "type": "ImportError",
            "message": f"Falha ao importar módulos necessários: {str(e)}",
            "traceback": traceback.format_exc()
        }
    }))
    sys.exit(1)

# Inicializar audit logger
audit_logger = AuditLogger(component='classifier')

def classify_image(image_path: str, generate_gradcam: bool = True, generate_diagnosis_flag: bool = True):
    """
    Classifica uma imagem de lesão de pele
    
    Args:
        image_path: Caminho para a imagem
        generate_gradcam: Se deve gerar Grad-CAM
        generate_diagnosis_flag: Se deve gerar diagnóstico automático
    
    Returns:
        dict: Resultado da classificação
    """
    start_time = time.time()
    event_id = audit_logger.log_classification_start(image_path)
    
    try:
        logger.info("=== INICIANDO CLASSIFICAÇÃO ===")
        logger.info(f"Imagem: {image_path}")
        logger.info(f"Grad-CAM: {generate_gradcam}")
        logger.info(f"Diagnóstico: {generate_diagnosis_flag}")
        
        # Verificar se imagem existe
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
        
        # Inicializar classificador
        logger.info("Inicializando classificador...")
        classifier = BinarySkinClassifier()
        
        # Classificar
        logger.info("Executando classificação...")
        result = classifier.predict(image_path=image_path)
        
        # Gerar Grad-CAM se solicitado
        if generate_gradcam:
            logger.info("Gerando Grad-CAM...")
            try:
                result['gradcam'] = classifier.generate_gradcam(image_path)
            except Exception as e:
                logger.warning(f"Erro ao gerar Grad-CAM: {e}")
                result['gradcam'] = None
        
        logger.info(f"Classificação concluída: {result['class']} ({result['confidence']:.2%})")
        
        # Analisar com Vision API
        vision_analysis = None
        logger.info("Analisando com Vision API...")
        try:
            vision_analyzer = VisionAnalyzer()
            vision_analysis = vision_analyzer.analyze_skin_lesion(image_path)
            logger.info(f"Vision API: {vision_analysis.get('success', False)}")
        except Exception as e:
            logger.warning(f"Erro na Vision API: {e}")
            vision_analysis = {'success': False, 'error': str(e)}
        
        # Gerar diagnóstico se solicitado
        diagnosis = None
        if generate_diagnosis_flag:
            logger.info("Gerando diagnóstico multimodal...")
            try:
                # Se Vision API funcionou, usar relatório combinado
                if vision_analysis and vision_analysis.get('success'):
                    vision_analyzer = VisionAnalyzer()
                    cnn_prediction = {
                        'class': result['class'],
                        'confidence': result['confidence'],
                        'risk_level': result['risk_level']
                    }
                    diagnosis_text = vision_analyzer.generate_dermatological_report(
                        vision_analysis=vision_analysis,
                        cnn_prediction=cnn_prediction
                    )
                    diagnosis = {
                        "success": True,
                        "analysis": diagnosis_text,
                        "model": "vision_api",
                        "vision_data": vision_analysis
                    }
                else:
                    # Fallback: usar diagnóstico CNN apenas
                    diagnosis = generate_diagnosis(
                        image_path=image_path,
                        classification_result=result['class'],
                        confidence=result['confidence'],
                        gradcam_base64=result.get('gradcam')
                    )
                    diagnosis['model'] = 'cnn_only'
                
                logger.info(f"Diagnóstico gerado: {diagnosis.get('model', 'unknown')}")
            except Exception as e:
                logger.warning(f"Erro ao gerar diagnóstico: {e}")
                diagnosis = {
                    "success": False,
                    "error": str(e)
                }
        
        # Salvar no dataset incremental
        logger.info("Salvando imagem no dataset incremental...")
        try:
            saved_info = classifier.save_to_dataset(image_path, result['class'], result['confidence'])
            logger.info(f"Salvamento: {saved_info}")
        except Exception as e:
            logger.warning(f"Erro ao salvar no dataset: {e}")
            saved_info = {"success": False, "error": str(e)}
        
        duration = time.time() - start_time
        logger.info(f"=== CLASSIFICAÇÃO CONCLUÍDA ({duration:.2f}s) ===")
        logger.info(f"Resultado: {result['class']} ({result['confidence']:.2%})")
        
        return {
            "success": True,
            "class": result['class'],
            "confidence": result['confidence'],
            "risk_level": result['risk_level'],
            "gradcam": result.get('gradcam'),
            "diagnosis": diagnosis,
            "saved_to_dataset": saved_info
        }
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        logger.error(f"Event ID: {event_id}")
        
        logger.error("=== ERRO NA CLASSIFICAÇÃO ===")
        logger.error(f"Tipo: {type(e).__name__}")
        logger.error(f"Mensagem: {error_msg}")
        logger.error("Stack trace completo:")
        logger.error(error_traceback)
        
        return {
            "success": False,
            "error": {
                "type": type(e).__name__,
                "message": error_msg,
                "traceback": error_traceback
            }
        }

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": {
                "type": "ArgumentError",
                "message": "Uso: classify_wrapper.py <image_path> [generate_gradcam] [generate_diagnosis]"
            }
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    generate_gradcam = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True
    generate_diagnosis_flag = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
    
    result = classify_image(image_path, generate_gradcam, generate_diagnosis_flag)
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
