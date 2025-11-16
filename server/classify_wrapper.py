#!/usr/bin/env python3
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

# Importar audit logger
try:
    sys.path.insert(0, '/home/ubuntu/skin_cancer_classifier_k230_page/server')
    from audit_logger import get_audit_logger
    audit_logger = get_audit_logger('classifier')
except ImportError as e:
    audit_logger = None
    logger.warning(f"Audit logger não disponível: {e}")

def classify_image(image_path: str, generate_gradcam: bool = True, generate_diagnosis: bool = True):
    """
    Classifica imagem de lesão de pele
    
    Args:
        image_path: Caminho para a imagem
        generate_gradcam: Se deve gerar Grad-CAM
        generate_diagnosis: Se deve gerar diagnóstico
        
    Returns:
        Dict com resultados
    """
    start_time = time.time()
    event_id = None
    
    try:
        logger.info(f"=== INICIANDO CLASSIFICAÇÃO ===")
        logger.info(f"Imagem: {image_path}")
        logger.info(f"Grad-CAM: {generate_gradcam}")
        logger.info(f"Diagnóstico: {generate_diagnosis}")
        
        # Log auditável
        if audit_logger:
            event_id = audit_logger.log_classification_start(
                image_path=image_path,
                parameters={
                    "generate_gradcam": generate_gradcam,
                    "generate_diagnosis": generate_diagnosis
                }
            )
        
        # Verificar se imagem existe
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
        
        logger.info("Importando módulos...")
        sys.path.insert(0, '/home/ubuntu/skin_cancer_classifier_k230_page/server')
        
        from binary_skin_classifier import get_binary_classifier
        logger.info("✓ binary_skin_classifier importado")
        
        # Classificação
        logger.info("Carregando classificador...")
        classifier = get_binary_classifier()
        logger.info("✓ Classificador carregado")
        
        logger.info("Realizando predição...")
        classification_result = classifier.predict(image_path)
        logger.info(f"✓ Predição: {classification_result['class']} ({classification_result['confidence']:.2%})")
        
        result = {
            'success': True,
            'classification': classification_result,
            'gradcam': None,
            'diagnosis': None
        }
        
        # Grad-CAM
        if generate_gradcam:
            try:
                logger.info("Gerando Grad-CAM...")
                gradcam_image = classifier.generate_gradcam(image_path)
                result['gradcam'] = gradcam_image
                logger.info("✓ Grad-CAM gerado")
            except Exception as e:
                logger.error(f"Erro ao gerar Grad-CAM: {e}")
                logger.error(traceback.format_exc())
                result['gradcam'] = None
        
        # Diagnóstico
        if generate_diagnosis:
            try:
                logger.info("Gerando análise multimodal com Gemini Vision...")
                from gemini_vision_analyzer import get_gemini_vision_analyzer
                
                analyzer = get_gemini_vision_analyzer()
                diagnosis = analyzer.analyze_lesion(
                    image_path=image_path,
                    classification_result=classification_result,
                    gradcam_base64=result.get('gradcam')
                )
                result['diagnosis'] = diagnosis
                logger.info(f"✓ Análise gerada (multimodal: {diagnosis.get('multimodal', False)})")
            except Exception as e:
                logger.error(f"Erro ao gerar análise: {e}")
                logger.error(traceback.format_exc())
                result['diagnosis'] = {
                    'success': False,
                    'error': str(e),
                    'analysis': f"Análise não disponível. Classificação: {classification_result.get('class_name', 'Desconhecido')} ({classification_result.get('confidence', 0):.1f}%)",
                    'multimodal': False
                }
        
        # Salvar imagem no dataset incremental
        try:
            logger.info("Salvando imagem no dataset incremental...")
            from dataset_manager import get_dataset_manager
            
            manager = get_dataset_manager()
            save_result = manager.save_classified_image(
                image_path=image_path,
                classification_result=classification_result,
                save_original=True
            )
            result['saved_to_dataset'] = save_result
            
            if save_result.get('success'):
                logger.info(f"✓ Imagem salva no dataset: {save_result.get('filename')}")
            else:
                logger.info(f"✓ Imagem não salva: {save_result.get('reason', 'Desconhecido')}")
        except Exception as e:
            logger.error(f"Erro ao salvar no dataset: {e}")
            result['saved_to_dataset'] = {'success': False, 'error': str(e)}
        
        logger.info("=== CLASSIFICAÇÃO CONCLUÍDA COM SUCESSO ===")
        
        # Log auditável de conclusão
        if audit_logger and event_id:
            duration = time.time() - start_time
            audit_logger.log_classification_complete(
                event_id=event_id,
                result=result,
                duration_seconds=duration
            )
        
        return result
        
    except Exception as e:
        logger.error(f"=== ERRO NA CLASSIFICAÇÃO ===")
        logger.error(f"Tipo: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Stack trace completo:")
        logger.error(traceback.format_exc())
        
        # Log auditável de erro
        if audit_logger and event_id:
            audit_logger.log_classification_error(
                event_id=event_id,
                error=e,
                context={
                    "image_path": image_path,
                    "stage": "classification"
                }
            )
        
        return {
            'success': False,
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
        }


def main():
    """
    Função principal para execução via linha de comando
    """
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': {
                'type': 'ArgumentError',
                'message': 'Uso: classify_wrapper.py <image_path> [generate_gradcam] [generate_diagnosis]'
            }
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    generate_gradcam = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True
    generate_diagnosis = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
    
    result = classify_image(image_path, generate_gradcam, generate_diagnosis)
    
    # Output JSON para stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
