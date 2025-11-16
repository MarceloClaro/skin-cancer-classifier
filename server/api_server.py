#!/usr/bin/env python3
"""
API HTTP para Classificação de Câncer de Pele
Servidor FastAPI para deploy separado (Render, Railway, Fly.io)
"""

import os
import sys
import base64
import logging
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Adicionar diretório server ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar módulos do projeto
try:
    from binary_skin_classifier import BinarySkinClassifier
    from multi_vision_analyzer import get_multi_vision_analyzer
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    raise

# Criar app FastAPI
app = FastAPI(
    title="Skin Cancer Classifier API",
    description="API para classificação de lesões de pele usando Deep Learning",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar classificador (singleton)
classifier = None

def get_classifier():
    """Retorna instância singleton do classificador"""
    global classifier
    if classifier is None:
        logger.info("Inicializando classificador...")
        classifier = BinarySkinClassifier()
        logger.info("Classificador inicializado com sucesso")
    return classifier


class ClassifyRequest(BaseModel):
    """Request para classificação"""
    imageBase64: str
    generateDiagnosis: bool = True


class ClassifyResponse(BaseModel):
    """Response da classificação"""
    success: bool
    class_name: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    probabilities: Optional[dict] = None
    gradcam: Optional[str] = None
    diagnosis: Optional[dict] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Skin Cancer Classifier API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check detalhado"""
    try:
        clf = get_classifier()
        return {
            "status": "healthy",
            "model_loaded": clf.model is not None,
            "model_path": clf.model_path
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/classify", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest):
    """
    Classifica uma lesão de pele
    
    Args:
        request: ClassifyRequest com imageBase64 e generateDiagnosis
        
    Returns:
        ClassifyResponse com resultado da classificação
    """
    try:
        logger.info("Recebendo requisição de classificação...")
        
        # Decodificar imagem base64
        try:
            # Remover prefixo data:image/...;base64, se existir
            image_data = request.imageBase64
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Decodificar
            image_bytes = base64.b64decode(image_data)
            logger.info(f"Imagem decodificada: {len(image_bytes)} bytes")
        except Exception as e:
            logger.error(f"Erro ao decodificar imagem: {e}")
            raise HTTPException(status_code=400, detail=f"Imagem base64 inválida: {str(e)}")
        
        # Salvar imagem temporária
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name
        
        logger.info(f"Imagem salva em: {tmp_path}")
        
        try:
            # Obter classificador
            clf = get_classifier()
            
            # Classificar
            logger.info("Executando classificação...")
            result = clf.predict(image_path=tmp_path)
            
            # Gerar Grad-CAM
            logger.info("Gerando Grad-CAM...")
            try:
                gradcam = clf.generate_gradcam(tmp_path)
            except Exception as e:
                logger.warning(f"Erro ao gerar Grad-CAM: {e}")
                gradcam = None
            
            # Gerar diagnóstico se solicitado
            diagnosis = None
            if request.generateDiagnosis:
                logger.info("Gerando diagnóstico multimodal...")
                try:
                    multi_analyzer = get_multi_vision_analyzer()
                    cnn_prediction = {
                        'class_name': result['class'],
                        'confidence': result['confidence'] * 100,
                        'risk_level': result['risk_level'],
                        'probabilities': result.get('probabilities', {})
                    }
                    vision_analysis = multi_analyzer.analyze_lesion(
                        image_path=tmp_path,
                        classification_result=cnn_prediction,
                        gradcam_base64=gradcam
                    )
                    
                    diagnosis = {
                        "success": vision_analysis.get('success', False),
                        "analysis": vision_analysis.get('analysis', ''),
                        "model": vision_analysis.get('model', 'unknown'),
                        "provider": vision_analysis.get('provider', 'unknown'),
                        "multimodal": vision_analysis.get('multimodal', False)
                    }
                    logger.info(f"Diagnóstico gerado: provider={diagnosis['provider']}")
                except Exception as e:
                    logger.warning(f"Erro ao gerar diagnóstico: {e}")
                    diagnosis = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Salvar no dataset incremental
            logger.info("Salvando no dataset incremental...")
            try:
                saved_info = clf.save_to_dataset(tmp_path, result['class'], result['confidence'])
                logger.info(f"Salvamento: {saved_info}")
            except Exception as e:
                logger.warning(f"Erro ao salvar no dataset: {e}")
            
            # Montar resposta
            response = ClassifyResponse(
                success=True,
                class_name=result['class'],
                confidence=result['confidence'],
                risk_level=result['risk_level'],
                probabilities=result.get('probabilities', {}),
                gradcam=gradcam,
                diagnosis=diagnosis
            )
            
            logger.info(f"Classificação concluída: {result['class']} ({result['confidence']:.2%})")
            return response
            
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na classificação: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro na classificação: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Porta padrão: 8000 (Render usa PORT env var)
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Iniciando servidor na porta {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
