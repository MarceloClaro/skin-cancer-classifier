# Documentação do Sistema de Classificação de Câncer de Pele K230

## Visão Geral

Sistema de classificação binária de lesões cutâneas (BENIGNO vs MALIGNO) usando deep learning otimizado para o processador K230. Inclui análise dermatoscópica multimodal com Gemini Vision API, retreinamento automático e salvamento incremental de dados.

---

## Arquitetura do Sistema

### 1. Frontend (React + TypeScript)

**Páginas Principais:**
- `/` - Landing page com informações do projeto
- `/classificador` - Interface de classificação de imagens
- `/treinamento` - Visualização de métricas de treinamento
- `/admin/dataset` - Dashboard de métricas do dataset incremental
- `/admin/retreinar` - Interface de retreinamento manual

**Componentes Chave:**
- `SkinClassifier.tsx` - Upload e classificação de imagens
- `AdminDataset.tsx` - Visualização de estatísticas e controle de retreinamento
- Gráficos: Recharts (Pizza, Linha, Barras)

### 2. Backend (Node.js + tRPC)

**Endpoints Principais:**

```typescript
// Classificação binária
skinClassifier.classifyBinary({
  imageData: string,      // Base64
  generateDiagnosis: boolean
})

// Estatísticas do dataset
dataset.getStatistics()

// Retreinamento manual
dataset.triggerRetrain()
```

### 3. Modelo de Deep Learning

**Arquitetura:**
- Base: MobileNetV2 (pré-treinado ImageNet)
- Camadas adicionais:
  - GlobalAveragePooling2D
  - Dense(128, activation='relu')
  - Dense(1, activation='sigmoid')

**Entrada:**
- Tamanho: 224x224x3
- Normalização: 0-1 (rescale 1./255)

**Saída:**
- Probabilidade binária (0-1)
- 0 = BENIGNO, 1 = MALIGNO

**Otimização:**
- Optimizer: Adam (lr=0.0001)
- Loss: Binary Crossentropy
- Métricas: Accuracy

---

## Fluxo de Classificação

### Passo 1: Upload da Imagem

```
Usuário → Frontend → tRPC → Backend
```

1. Imagem convertida para Base64
2. Enviada via endpoint `skinClassifier.classifyBinary`
3. Salva temporariamente em `/tmp/skin_binary_*.png`

### Passo 2: Classificação

```python
# classify_wrapper.py
classifier = BinarySkinClassifier()
result = classifier.predict(image_path)
# → { class: "MALIGNO", confidence: 0.8231, risk_level: "ALTO" }
```

### Passo 3: Geração de Grad-CAM

```python
gradcam_base64 = classifier.generate_gradcam(image_path, predicted_class)
# → Mapa de ativação sobreposto na imagem original
```

### Passo 4: Análise Gemini Vision (Opcional)

```python
diagnosis = generator.generate_diagnosis_binary(
    classification_result="MALIGNO",
    confidence=0.82,
    image_path="/tmp/skin_binary_*.png",
    gradcam_base64="data:image/png;base64,..."
)
```

**Prompt Dermatológico:**
- Achados dermatoscópicos (ABCDE)
- Interpretação clínica
- Diagnóstico diferencial (3-5 opções)
- Recomendações (conduta, urgência, exames)
- Limitações e avisos

### Passo 5: Salvamento no Dataset Incremental

```python
saved_info = classifier.save_to_dataset(
    image_path="/tmp/skin_binary_*.png",
    predicted_class="MALIGNO",
    confidence=0.82
)
```

**Estrutura de Salvamento:**
```
/dataset_incremental/
├── BENIGNO/
│   └── BENIGNO_20251116_160530_a1b2c3d4.png
├── MALIGNO/
│   └── MALIGNO_20251116_160545_e5f6g7h8.png
├── metadata/
└── statistics.json
```

**Detecção de Duplicatas:**
- Hash MD5 calculado para cada imagem
- Comparação com hashes existentes
- Salvamento bloqueado se duplicata detectada

---

## Retreinamento Automático

### Condições de Ativação

1. **Threshold Mínimo:** ≥ 2 imagens no dataset incremental
2. **Desbalanceamento:** Diferença > 5 imagens entre classes

### Processo de Retreinamento

```python
# retrain_model.py

# 1. Verificar condições
can_retrain, counts = check_retrain_conditions()

# 2. Balancear dataset (se necessário)
if abs(counts['BENIGNO'] - counts['MALIGNO']) > 5:
    balanced_counts = balance_dataset(counts)

# 3. Retreinar modelo
retrain_metrics = retrain_model(balanced_counts)

# 4. Atualizar estatísticas
update_statistics(retrain_metrics, balanced_counts)
```

### Geração de Imagens Sintéticas

**Data Augmentation:**
```python
ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
```

**Estratégia:**
- Identificar classe minoritária
- Gerar imagens sintéticas até balancear
- Salvar com sufixo `_synthetic_`

### Configurações de Treinamento

```python
BATCH_SIZE = 16
EPOCHS = 20
VALIDATION_SPLIT = 0.2

callbacks = [
    EarlyStopping(patience=5),
    ModelCheckpoint(save_best_only=True)
]
```

### Métricas Salvas

```json
{
  "timestamp": "2025-11-16T16:05:30.000Z",
  "accuracy": 0.9234,
  "loss": 0.1876,
  "epochs": 15,
  "images_used": 45,
  "class_distribution": {
    "BENIGNO": 23,
    "MALIGNO": 22
  }
}
```

---

## Dashboard de Métricas

### Visualizações Disponíveis

1. **Cards de Resumo:**
   - Total de imagens
   - Imagens benignas
   - Imagens malignas
   - Status do dataset (balanceado/desbalanceado)

2. **Gráfico de Pizza:**
   - Distribuição por classe (BENIGNO vs MALIGNO)

3. **Gráfico de Linha:**
   - Distribuição temporal (imagens adicionadas ao longo do tempo)

4. **Informações de Retreinamento:**
   - Data do último retreinamento
   - Acurácia alcançada
   - Imagens usadas
   - Épocas treinadas

### Atualização Automática

- Polling a cada 10 segundos
- Atualização em tempo real durante retreinamento

---

## Integração Gemini Vision API

### Configuração

```bash
# Variável de ambiente (já configurada)
GEMINI_API_KEY=<sua_chave>
```

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}
```

### Payload

```json
{
  "contents": [{
    "parts": [
      { "text": "<prompt_dermatologico>" },
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "<base64_image>"
        }
      }
    ]
  }],
  "generationConfig": {
    "temperature": 0.4,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 2048
  }
}
```

### Resposta

```json
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "## 1. Achados Dermatoscópicos\n\n..."
      }]
    }
  }]
}
```

### Fallback

Se Gemini Vision falhar ou estiver indisponível:
- Diagnóstico baseado apenas em classificação CNN
- Relatório estruturado com informações básicas
- Aviso sobre limitações

---

## Resolução de Problemas

### Erro: `python3.11: not found`

**Causa:** Produção usa `python3` em vez de `python3.11`

**Solução:**
```typescript
// routers.ts
const command = `python3 ${wrapperPath} ...`;
```

```python
#!/usr/bin/env python3
# classify_wrapper.py
```

### Erro: `SRE module mismatch`

**Causa:** Conflito entre Python 3.11 e 3.13.8 (uv)

**Solução:**
```typescript
// Limpar variáveis de ambiente
const cleanEnv = {
  ...process.env,
  PYTHONPATH: undefined,
  PYTHONHOME: undefined,
  NUITKA_PYTHONPATH: undefined
};

execAsync(command, { env: cleanEnv });
```

### Erro: `The layer sequential has never been called`

**Causa:** Modelo não inicializado antes de gerar Grad-CAM

**Solução:**
```python
# binary_skin_classifier.py
def _load_model(self):
    self.model = keras.models.load_model(self.model_path)
    
    # Inicializar modelo com predição dummy
    dummy_input = np.zeros((1, 224, 224, 3))
    _ = self.model.predict(dummy_input, verbose=0)
```

---

## Manutenção e Monitoramento

### Logs

**Classificação:**
```bash
tail -f /tmp/skin_classifier.log
```

**Retreinamento:**
```bash
tail -f /tmp/retrain_model.log
```

### Limpeza de Arquivos Temporários

```bash
# Remover imagens temporárias antigas (> 24h)
find /tmp -name "skin_binary_*.png" -mtime +1 -delete
```

### Backup do Dataset

```bash
# Backup manual
tar -czf dataset_backup_$(date +%Y%m%d).tar.gz /home/ubuntu/skin_cancer_classifier_k230_page/dataset_incremental/
```

### Versionamento de Modelos

```bash
# Criar backup antes de retreinamento
cp models/skin_cancer_model.h5 models/skin_cancer_model_v1_backup.h5
```

---

## Referências

- **Gemini API:** https://ai.google.dev/gemini-api/docs
- **MobileNetV2:** https://keras.io/api/applications/mobilenet/
- **Grad-CAM:** https://arxiv.org/abs/1610.02391
- **TensorFlow:** https://www.tensorflow.org/
- **tRPC:** https://trpc.io/

---

## Contato e Suporte

Para dúvidas ou suporte, entre em contato através do formulário em [pele.manus.space](https://pele.manus.space).

---

*Última atualização: 16 de novembro de 2025*
