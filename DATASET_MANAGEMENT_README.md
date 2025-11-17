# Sistema de Gerenciamento de Dataset e Treinamento - K230

## Visão Geral

Este documento descreve o sistema completo de gerenciamento de dataset e treinamento para o Classificador de Câncer de Pele K230, implementado com as seguintes funcionalidades:

### ✅ Funcionalidades Implementadas

#### 1. **Botão de Reset Completo**
- Interface com modal de confirmação
- Remove todo o dataset incremental (BENIGNO e MALIGNO)
- Limpa modelos treinados e visualizações
- Apaga histórico e status de retreinamento
- Confirmação obrigatória digitando "LIMPAR TUDO"

#### 2. **Upload de Dataset Personalizado**
- Interface para upload de múltiplas imagens
- Seleção de classe (BENIGNO ou MALIGNO)
- Validação automática de formato (PNG, JPG, JPEG)
- Detecção de duplicatas por hash MD5
- Progresso visual durante upload
- Suporte futuro para arquivos ZIP

#### 3. **Correção de Erros de API**
- Tratamento robusto de erros em todos os endpoints
- Retorno consistente de JSON em caso de erro
- Logs detalhados para debugging
- Mensagens de erro estruturadas

#### 4. **Página de Gerenciamento de Dataset**
- Dashboard com estatísticas em tempo real
- Galeria de imagens com miniaturas
- Filtro por classe (BENIGNO/MALIGNO)
- Paginação de resultados
- Opção de excluir imagens individuais
- Gráficos de distribuição temporal e por classe

#### 5. **Sistema de Treinamento Personalizado**
- Configuração de hiperparâmetros:
  - Learning rate
  - Número de épocas
  - Batch size
  - Data augmentation (rotação, flip, zoom, shift)
  - Divisão treino/validação
- Callbacks automáticos:
  - Early stopping
  - Redução de learning rate
  - Checkpoint do melhor modelo
  - Log CSV de métricas

#### 6. **Monitoramento de Treinamento**
- Status em tempo real salvo em JSON
- Progresso por época
- Métricas de treino e validação
- Atualização automática no frontend

#### 7. **Validação de Modelo**
- Matriz de confusão
- Curva ROC com AUC
- Relatório de classificação (precision, recall, F1)
- Visualizações salvas automaticamente

#### 8. **Exportação de Modelo**
- Formato H5 (completo)
- TFLite float32
- TFLite quantizado INT8 (otimizado para K230)
- ONNX (interoperabilidade)
- Documentação automática

## Estrutura de Arquivos

```
skin-cancer-classifier/
├── server/
│   ├── routers.ts                    # Endpoints tRPC
│   ├── reset_dataset.py              # Script de reset
│   ├── process_zip.py                # Processamento de ZIP
│   ├── train_model_custom.py         # Treinamento personalizado
│   ├── export_model.py               # Exportação de modelos
│   └── dataset_manager.py            # Gerenciador de dataset
├── client/src/
│   ├── components/
│   │   ├── ResetDatasetModal.tsx    # Modal de confirmação
│   │   ├── DatasetUploader.tsx      # Interface de upload
│   │   └── DatasetGallery.tsx       # Galeria de imagens
│   └── pages/
│       └── AdminDataset.tsx          # Dashboard principal
├── dataset_incremental/
│   ├── BENIGNO/                      # Imagens benignas
│   ├── MALIGNO/                      # Imagens malignas
│   ├── metadata/                     # Metadados JSON
│   ├── retrain_status.json           # Status do treinamento
│   ├── retrain_history.json          # Histórico de treinos
│   └── statistics.json               # Estatísticas do dataset
└── models/
    ├── skin_cancer_model.h5          # Modelo treinado
    ├── tflite/                       # Modelos TFLite
    ├── exports/                      # Exportações
    └── training_report_*/            # Relatórios de treinamento
```

## Endpoints tRPC Implementados

### Dataset Management

#### `dataset.getStatistics`
Retorna estatísticas do dataset em tempo real.

**Resposta:**
```json
{
  "total_images": 21,
  "total_by_class": {
    "BENIGNO": 3,
    "MALIGNO": 18
  },
  "temporal_distribution": [...],
  "duplicates_detected": 0,
  "retraining_status": "idle",
  "last_retrain": null
}
```

#### `dataset.resetAll`
Remove todo o dataset e modelos.

**Resposta:**
```json
{
  "success": true,
  "message": "Dataset e modelos limpos com sucesso"
}
```

#### `dataset.listImages`
Lista imagens com paginação e filtro.

**Entrada:**
```json
{
  "classFilter": "all" | "BENIGNO" | "MALIGNO",
  "page": 1,
  "pageSize": 20
}
```

**Resposta:**
```json
{
  "images": [...],
  "total": 21,
  "page": 1,
  "pageSize": 20,
  "totalPages": 2
}
```

#### `dataset.deleteImage`
Remove uma imagem específica.

**Entrada:**
```json
{
  "filename": "MALIGNO_20251116_130939_1e6f9384.png",
  "class": "MALIGNO"
}
```

#### `dataset.uploadImages`
Faz upload de múltiplas imagens.

**Entrada:**
```json
{
  "images": [
    {
      "data": "base64...",
      "class": "MALIGNO",
      "filename": "lesao1.png"
    }
  ]
}
```

**Resposta:**
```json
{
  "success": true,
  "uploaded": 5,
  "total": 5,
  "errors": []
}
```

#### `dataset.triggerRetrain`
Inicia retreinamento do modelo.

**Resposta:**
```json
{
  "success": true,
  "message": "Retreinamento iniciado com sucesso"
}
```

## Scripts Python

### 1. reset_dataset.py

Remove todo o dataset e modelos.

**Uso:**
```bash
# Modo interativo (confirmação)
python3 server/reset_dataset.py

# Modo automático
python3 server/reset_dataset.py --confirm
```

**Saída:**
```json
{
  "success": true,
  "details": {
    "dataset": {"success": true, "images_removed": 21},
    "status": {"success": true, "files_removed": [...]},
    "models": {"success": true, "files_removed": [...]}
  }
}
```

### 2. process_zip.py

Processa upload de dataset em ZIP.

**Estrutura do ZIP:**
```
dataset.zip
├── BENIGNO/
│   ├── imagem1.png
│   ├── imagem2.jpg
│   └── ...
└── MALIGNO/
    ├── imagem1.png
    ├── imagem2.jpg
    └── ...
```

**Uso:**
```bash
python3 server/process_zip.py /caminho/para/dataset.zip
```

**Saída:**
```json
{
  "success": true,
  "stats": {
    "total": 100,
    "valid": 95,
    "invalid": 3,
    "duplicates": 2,
    "by_class": {
      "BENIGNO": {"total": 50, "valid": 48, ...},
      "MALIGNO": {"total": 50, "valid": 47, ...}
    }
  }
}
```

### 3. train_model_custom.py

Treinamento personalizado com configuração de hiperparâmetros.

**Uso:**
```bash
# Modo automático (configuração padrão)
python3 server/train_model_custom.py --auto

# Com arquivo de configuração
python3 server/train_model_custom.py --config config.json
```

**Configuração (config.json):**
```json
{
  "learning_rate": 0.0001,
  "epochs": 50,
  "batch_size": 16,
  "image_size": [224, 224],
  "validation_split": 0.2,
  "test_split": 0.1,
  "early_stopping_patience": 10,
  "reduce_lr_patience": 5,
  "augmentation": {
    "enabled": true,
    "rotation_range": 20,
    "width_shift_range": 0.2,
    "height_shift_range": 0.2,
    "horizontal_flip": true,
    "vertical_flip": true,
    "zoom_range": 0.2,
    "fill_mode": "nearest"
  }
}
```

**Saída:**
```json
{
  "success": true,
  "metrics": {
    "accuracy": 0.8909,
    "auc_roc": 0.9234,
    "confusion_matrix": [[...], [...]],
    "classification_report": {...}
  },
  "report_dir": "models/training_report_20251117_120000"
}
```

**Arquivos Gerados:**
- `models/skin_cancer_model.h5` - Modelo treinado
- `models/training_report_*/training_curves.png` - Curvas de treinamento
- `models/training_report_*/confusion_matrix.png` - Matriz de confusão
- `models/training_report_*/roc_curve.png` - Curva ROC
- `models/training_report_*/classification_report.json` - Relatório detalhado
- `models/training_report_*/training_log.csv` - Log de épocas

### 4. export_model.py

Exporta modelo em múltiplos formatos.

**Uso:**
```bash
# Exportar modelo padrão
python3 server/export_model.py

# Exportar modelo específico
python3 server/export_model.py --model models/best_model.h5
```

**Saída:**
```json
{
  "success": true,
  "total": 4,
  "successful": 3,
  "failed": 1,
  "results": [
    {"success": true, "format": "h5", "size_mb": 8.5, ...},
    {"success": true, "format": "tflite_float32", "size_mb": 8.2, ...},
    {"success": true, "format": "tflite_quantized", "size_mb": 2.1, ...},
    {"success": false, "format": "onnx", "error": "tf2onnx não instalado"}
  ],
  "export_dir": "models/exports"
}
```

**Formatos Exportados:**
- `skin_cancer_model_export.h5` - Modelo completo TensorFlow/Keras
- `skin_cancer_k230.tflite` - TFLite float32
- `skin_cancer_k230_quantized.tflite` - TFLite INT8 (otimizado para K230)
- `skin_cancer_model.onnx` - ONNX (se tf2onnx estiver instalado)
- `README.md` - Documentação dos modelos

## Fluxo de Trabalho Completo

### 1. Preparação do Dataset

```bash
# Opção 1: Upload via interface web
# Acesse /admin/dataset e clique em "Upload Dataset"

# Opção 2: Upload via ZIP
python3 server/process_zip.py dataset.zip
```

### 2. Verificação do Dataset

```bash
# Acessar dashboard em /admin/dataset
# Verificar estatísticas e distribuição
```

### 3. Configuração do Treinamento

Criar arquivo `training_config.json`:
```json
{
  "learning_rate": 0.0001,
  "epochs": 100,
  "batch_size": 32,
  "augmentation": {
    "enabled": true,
    "rotation_range": 30
  }
}
```

### 4. Treinamento

```bash
# Via interface web
# Clicar em "Iniciar Retreinamento Manual"

# Ou via linha de comando
python3 server/train_model_custom.py --config training_config.json
```

### 5. Monitoramento

```bash
# Acompanhar status em tempo real
cat dataset_incremental/retrain_status.json

# Ou via dashboard web
```

### 6. Validação

```bash
# Verificar métricas no relatório
cat models/training_report_*/classification_report.json

# Visualizar curvas e matrizes
ls models/training_report_*/*.png
```

### 7. Exportação

```bash
# Exportar modelo em todos os formatos
python3 server/export_model.py

# Verificar exportações
ls models/exports/
```

### 8. Reset (se necessário)

```bash
# Via interface web
# Clicar em "Limpar Tudo" e confirmar

# Ou via linha de comando
python3 server/reset_dataset.py --confirm
```

## Componentes React

### ResetDatasetModal

Modal de confirmação para reset completo.

**Props:**
```typescript
interface ResetDatasetModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}
```

**Uso:**
```tsx
<ResetDatasetModal
  open={showResetModal}
  onOpenChange={setShowResetModal}
  onSuccess={() => refetch()}
/>
```

### DatasetUploader

Interface para upload de múltiplas imagens.

**Props:**
```typescript
interface DatasetUploaderProps {
  onSuccess?: () => void;
}
```

**Uso:**
```tsx
<DatasetUploader onSuccess={() => refetch()} />
```

### DatasetGallery

Galeria de imagens com filtros e paginação.

**Props:**
```typescript
interface DatasetGalleryProps {
  onRefresh?: () => void;
}
```

**Uso:**
```tsx
<DatasetGallery onRefresh={() => refetch()} />
```

## Tratamento de Erros

Todos os endpoints e scripts implementam tratamento robusto de erros:

### Backend (tRPC)
```typescript
try {
  // Operação
  return { success: true, data: ... };
} catch (error: any) {
  console.error("[ENDPOINT] Erro:", error);
  return {
    success: false,
    error: error.message
  };
}
```

### Python
```python
try:
    # Operação
    return {"success": True, "data": ...}
except Exception as e:
    logger.error(f"Erro: {e}")
    return {"success": False, "error": str(e)}
```

### Frontend
```tsx
const mutation = trpc.endpoint.useMutation({
  onSuccess: (data) => {
    if (data.success) {
      toast.success("Operação concluída!");
    } else {
      toast.error("Erro", { description: data.error });
    }
  },
  onError: (error) => {
    toast.error("Erro", { description: error.message });
  },
});
```

## Logs e Debugging

### Logs do Backend
```bash
# Logs do servidor Node.js
# Verificar console do servidor

# Logs de treinamento Python
cat dataset_incremental/retrain_status.json
```

### Logs do Frontend
```bash
# Console do navegador (F12)
# Verificar network tab para requisições tRPC
```

## Dependências Python

```bash
pip install tensorflow pillow numpy scikit-learn matplotlib seaborn
```

Opcional para ONNX:
```bash
pip install tf2onnx
```

## Próximas Melhorias

- [ ] Upload de arquivo ZIP via interface web
- [ ] Configuração de treinamento via interface
- [ ] Monitoramento em tempo real com WebSocket
- [ ] Comparação entre versões de modelos
- [ ] Detecção automática de duplicatas
- [ ] Balanceamento automático de classes
- [ ] Geração de imagens sintéticas (SMOTE, GAN)
- [ ] Exportação para outros formatos (CoreML, TensorRT)

## Suporte

Para problemas ou dúvidas, consulte:
- `TROUBLESHOOTING.md` - Solução de problemas comuns
- `DOCUMENTATION.md` - Documentação completa do projeto
- GitHub Issues - Reportar bugs ou sugerir melhorias

## Licença

Este projeto está sob a mesma licença do projeto principal.
