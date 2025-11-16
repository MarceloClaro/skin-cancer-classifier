"""
Sistema de Logs Auditáveis para Rastreamento Completo
Registra todas as operações do sistema com contexto detalhado
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid
import traceback

# Diretório de logs
LOGS_DIR = "/home/ubuntu/skin_cancer_classifier_k230_page/logs"
Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AuditLogger:
    """
    Logger auditável com rastreamento completo
    """
    
    def __init__(self, component: str):
        """
        Inicializa logger para um componente específico
        
        Args:
            component: Nome do componente (ex: 'classifier', 'training', 'api')
        """
        self.component = component
        self.logger = logging.getLogger(f"audit.{component}")
        
        # Arquivo de log específico do componente
        self.log_file = Path(LOGS_DIR) / f"{component}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
    
    def log_event(
        self,
        event_type: str,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> str:
        """
        Registra um evento auditável
        
        Args:
            event_type: Tipo do evento (ex: 'classification_start', 'training_complete')
            level: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Mensagem descritiva
            context: Contexto adicional (parâmetros, dados, etc.)
            error: Exceção (se houver)
            
        Returns:
            ID único do evento
        """
        event_id = str(uuid.uuid4())
        
        event_data = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "component": self.component,
            "event_type": event_type,
            "level": level,
            "message": message,
            "context": context or {},
        }
        
        # Adicionar informações de erro se houver
        if error:
            event_data["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc()
            }
        
        # Escrever no arquivo JSONL
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
        
        # Também logar no console
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{event_type}] {message} | event_id={event_id}")
        
        return event_id
    
    def log_classification_start(
        self,
        image_path: str,
        user_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra início de classificação
        """
        return self.log_event(
            event_type="classification_start",
            level="INFO",
            message=f"Iniciando classificação de imagem: {image_path}",
            context={
                "image_path": image_path,
                "user_id": user_id,
                "parameters": parameters or {}
            }
        )
    
    def log_classification_complete(
        self,
        event_id: str,
        result: Dict[str, Any],
        duration_seconds: float
    ) -> str:
        """
        Registra conclusão de classificação
        """
        return self.log_event(
            event_type="classification_complete",
            level="INFO",
            message=f"Classificação concluída em {duration_seconds:.2f}s",
            context={
                "parent_event_id": event_id,
                "result": result,
                "duration_seconds": duration_seconds
            }
        )
    
    def log_classification_error(
        self,
        event_id: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra erro na classificação
        """
        return self.log_event(
            event_type="classification_error",
            level="ERROR",
            message=f"Erro na classificação: {str(error)}",
            context={
                "parent_event_id": event_id,
                **(context or {})
            },
            error=error
        )
    
    def log_training_start(
        self,
        dataset_info: Dict[str, Any],
        hyperparameters: Dict[str, Any]
    ) -> str:
        """
        Registra início de treinamento
        """
        return self.log_event(
            event_type="training_start",
            level="INFO",
            message="Iniciando treinamento de modelo",
            context={
                "dataset_info": dataset_info,
                "hyperparameters": hyperparameters
            }
        )
    
    def log_training_epoch(
        self,
        event_id: str,
        epoch: int,
        metrics: Dict[str, float]
    ) -> str:
        """
        Registra métricas de uma época de treinamento
        """
        return self.log_event(
            event_type="training_epoch",
            level="DEBUG",
            message=f"Época {epoch} concluída",
            context={
                "parent_event_id": event_id,
                "epoch": epoch,
                "metrics": metrics
            }
        )
    
    def log_training_complete(
        self,
        event_id: str,
        final_metrics: Dict[str, float],
        model_path: str,
        duration_seconds: float
    ) -> str:
        """
        Registra conclusão de treinamento
        """
        return self.log_event(
            event_type="training_complete",
            level="INFO",
            message=f"Treinamento concluído em {duration_seconds:.2f}s",
            context={
                "parent_event_id": event_id,
                "final_metrics": final_metrics,
                "model_path": model_path,
                "duration_seconds": duration_seconds
            }
        )
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registra requisição à API
        """
        return self.log_event(
            event_type="api_request",
            level="INFO",
            message=f"{method} {endpoint}",
            context={
                "endpoint": endpoint,
                "method": method,
                "user_id": user_id,
                "params": params or {}
            }
        )
    
    def log_api_response(
        self,
        event_id: str,
        status_code: int,
        duration_ms: float
    ) -> str:
        """
        Registra resposta da API
        """
        return self.log_event(
            event_type="api_response",
            level="INFO",
            message=f"Resposta {status_code} em {duration_ms:.2f}ms",
            context={
                "parent_event_id": event_id,
                "status_code": status_code,
                "duration_ms": duration_ms
            }
        )
    
    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Retorna eventos recentes
        
        Args:
            event_type: Filtrar por tipo de evento (opcional)
            limit: Número máximo de eventos
            
        Returns:
            Lista de eventos
        """
        events = []
        
        if not self.log_file.exists():
            return events
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event_type is None or event.get('event_type') == event_type:
                        events.append(event)
                except json.JSONDecodeError:
                    continue
        
        # Retornar os mais recentes
        return events[-limit:]
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca evento por ID
        
        Args:
            event_id: ID do evento
            
        Returns:
            Dados do evento ou None
        """
        if not self.log_file.exists():
            return None
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get('event_id') == event_id:
                        return event
                except json.JSONDecodeError:
                    continue
        
        return None


# Singletons para cada componente
_loggers = {}

def get_audit_logger(component: str) -> AuditLogger:
    """
    Retorna logger auditável para um componente
    
    Args:
        component: Nome do componente
        
    Returns:
        AuditLogger
    """
    if component not in _loggers:
        _loggers[component] = AuditLogger(component)
    return _loggers[component]


# Funções de conveniência
def log_classification(image_path: str, **kwargs) -> str:
    """Atalho para log de classificação"""
    logger = get_audit_logger('classifier')
    return logger.log_classification_start(image_path, **kwargs)

def log_training(**kwargs) -> str:
    """Atalho para log de treinamento"""
    logger = get_audit_logger('training')
    return logger.log_training_start(**kwargs)

def log_api(endpoint: str, method: str, **kwargs) -> str:
    """Atalho para log de API"""
    logger = get_audit_logger('api')
    return logger.log_api_request(endpoint, method, **kwargs)
