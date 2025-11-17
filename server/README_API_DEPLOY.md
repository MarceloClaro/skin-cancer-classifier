# Deploy da API Python no Render

## Pré-requisitos

1. Conta no [Render](https://render.com/) (gratuita)
2. Repositório Git com o código (GitHub, GitLab, etc.)

## Passos para Deploy

### 1. Preparar Repositório

Certifique-se de que os seguintes arquivos estão no diretório `server/`:

- `api_server.py` - Servidor FastAPI
- `requirements.txt` - Dependências Python
- `render.yaml` - Configuração do Render
- `binary_skin_classifier.py` - Classificador
- `multi_vision_analyzer.py` - Analisador multimodal
- `gradcam_generator.py` - Gerador de Grad-CAM
- `models/skin_cancer_model.h5` - Modelo treinado

### 2. Criar Web Service no Render

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **New** → **Web Service**
3. Conecte seu repositório Git
4. Configure:
   - **Name:** `skin-cancer-classifier-api`
   - **Region:** Oregon (ou mais próximo)
   - **Branch:** `main` (ou sua branch principal)
   - **Root Directory:** `server`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python api_server.py`

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá em **Environment** e adicione:

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=<sua_nova_chave_gemini>
PORT=10000
```

### 4. Deploy

1. Clique em **Create Web Service**
2. Aguarde o build (pode levar 5-10 minutos)
3. Quando o status ficar **Live**, copie a URL (ex: `https://skin-cancer-classifier-api.onrender.com`)

### 5. Configurar Frontend

No projeto frontend, adicione a variável de ambiente:

**Arquivo:** `.env` (ou configurar no painel de gerenciamento)

```
VITE_CLASSIFIER_API_URL=https://skin-cancer-classifier-api.onrender.com
```

## Testar API

### Health Check

```bash
curl https://skin-cancer-classifier-api.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "models/skin_cancer_model.h5"
}
```

### Classificação

```bash
curl -X POST https://skin-cancer-classifier-api.onrender.com/classify \
  -H "Content-Type: application/json" \
  -d '{
    "imageBase64": "data:image/png;base64,iVBORw0KG...",
    "generateDiagnosis": true
  }'
```

## Limitações do Plano Gratuito

- **Spin Down:** Após 15 minutos de inatividade, o serviço entra em sleep (primeira requisição leva ~30s)
- **Memória:** 512 MB RAM (suficiente para o modelo)
- **Largura de banda:** 100 GB/mês
- **Build time:** 500 horas/mês

## Alternativas

Se o Render não funcionar:

1. **Railway:** https://railway.app/ (similar ao Render)
2. **Fly.io:** https://fly.io/ (mais controle, requer Dockerfile)
3. **Google Cloud Run:** Serverless, paga por uso
4. **AWS Lambda:** Requer containerização

## Troubleshooting

### Erro: "Model file not found"

Certifique-se de que `models/skin_cancer_model.h5` está no repositório Git.

### Erro: "Out of memory"

O modelo é muito grande para o plano gratuito. Considere:
- Usar plano pago ($7/mês)
- Otimizar modelo (quantização)
- Usar serviço com mais memória

### Erro: "Build timeout"

Instalação de TensorFlow demora. Soluções:
- Usar imagem Docker pré-configurada
- Cachear dependências
- Upgrade para plano pago

## Monitoramento

No painel do Render:
- **Logs:** Ver logs em tempo real
- **Metrics:** CPU, memória, requisições
- **Events:** Histórico de deploys

## Custos

- **Plano Gratuito:** $0/mês (com limitações)
- **Starter:** $7/mês (sem spin down, 512 MB RAM)
- **Standard:** $25/mês (2 GB RAM)
