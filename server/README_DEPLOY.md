# 🚀 Deploy Automático no Railway

Guia completo para fazer deploy da API Python no Railway usando o script semi-automático.

## 📋 Pré-requisitos

1. **Conta no Railway** (gratuita)
   - Acesse: https://railway.app/
   - Faça login com GitHub ou email
   - Crédito gratuito: $5/mês

2. **Git** instalado
   - Verificar: `git --version`

3. **Bash** (Linux/Mac) ou **Git Bash** (Windows)

## 🎯 Método 1: Script Automático (Recomendado)

### Passo 1: Baixar Código

```bash
# Clonar repositório (se ainda não tiver)
git clone <seu-repositorio>
cd skin_cancer_classifier_k230_page/server
```

### Passo 2: Executar Script

```bash
./deploy.sh
```

### O que o script faz:

1. ✅ Instala Railway CLI automaticamente (se necessário)
2. ✅ Abre navegador para login (você faz login uma vez)
3. ✅ Cria projeto Railway
4. ✅ Configura variáveis de ambiente
5. ✅ Faz deploy do Docker
6. ✅ Gera URL pública
7. ✅ Salva URL em `.railway_url`

### Tempo estimado:
- **Primeira vez:** 10-15 minutos (build Docker)
- **Deploys seguintes:** 5-8 minutos (cache)

---

## 🔧 Método 2: Manual (Passo a Passo)

### 1. Instalar Railway CLI

**Linux/Mac:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Windows:**
```powershell
iwr https://railway.app/install.ps1 | iex
```

### 2. Fazer Login

```bash
railway login
```

Isso abre o navegador automaticamente. Faça login com GitHub ou email.

### 3. Criar Projeto

```bash
cd server/
railway init
```

Escolha:
- **Nome:** `skin-cancer-classifier-api`
- **Template:** Empty Project

### 4. Configurar Variáveis

```bash
railway variables set GROQ_API_KEY="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"
railway variables set GEMINI_API_KEY="<sua_chave_gemini>"
railway variables set PORT=8000
```

### 5. Fazer Deploy

```bash
railway up
```

Aguarde 5-10 minutos. Você verá:
```
✓ Build successful
✓ Deployment live
```

### 6. Gerar URL Pública

```bash
railway domain
```

Copia a URL gerada (ex: `https://skin-cancer-api.up.railway.app`)

---

## 🧪 Testar API

### Health Check

```bash
curl https://skin-cancer-api.up.railway.app/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "models/skin_cancer_model.h5"
}
```

### Classificação (Teste)

```bash
curl -X POST https://skin-cancer-api.up.railway.app/classify \
  -H "Content-Type: application/json" \
  -d '{
    "imageBase64": "data:image/png;base64,iVBORw0KG...",
    "generateDiagnosis": true
  }'
```

---

## ⚙️ Configurar Frontend

### Opção 1: Via Painel de Gerenciamento

1. Acesse o painel do projeto
2. Vá em **Settings** → **Secrets**
3. Adicione:
   ```
   VITE_CLASSIFIER_API_URL=https://skin-cancer-api.up.railway.app
   ```
4. Clique em **Publish** para republicar

### Opção 2: Via Arquivo .env

Crie `.env` na raiz do projeto:

```env
VITE_CLASSIFIER_API_URL=https://skin-cancer-api.up.railway.app
```

---

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
railway logs
```

### Ver Logs das Últimas 100 Linhas

```bash
railway logs --tail 100
```

### Ver Métricas

```bash
railway status
```

### Acessar Dashboard Web

```bash
railway open
```

Abre o dashboard do Railway no navegador.

---

## 🔄 Atualizar Deploy

Após fazer alterações no código:

```bash
git add .
git commit -m "Atualização"
railway up
```

Ou simplesmente:

```bash
./deploy.sh
```

---

## 💰 Custos

### Plano Gratuito (Hobby)
- **Crédito:** $5/mês
- **Memória:** 512 MB RAM
- **CPU:** Compartilhada
- **Largura de banda:** 100 GB/mês
- **Build time:** Ilimitado

### Estimativa de Uso
- **API idle:** ~$0.50/mês
- **100 classificações/dia:** ~$2-3/mês
- **1000 classificações/dia:** ~$8-12/mês

**Nota:** Com $5 gratuitos, você consegue rodar ~2-3 meses sem custo.

---

## 🐛 Troubleshooting

### Erro: "Build failed"

**Causa:** Dependências muito grandes ou timeout

**Solução:**
```bash
# Aumentar timeout
railway up --timeout 600
```

### Erro: "Out of memory"

**Causa:** Modelo TensorFlow muito grande (512 MB RAM)

**Solução:**
1. Upgrade para plano pago ($5/mês = 1 GB RAM)
2. Ou otimizar modelo (quantização INT8)

### Erro: "Port already in use"

**Causa:** Variável PORT não configurada

**Solução:**
```bash
railway variables set PORT=8000
railway restart
```

### Deploy lento (>15 min)

**Causa:** Instalação de TensorFlow demora

**Solução:**
- Normal na primeira vez
- Deploys seguintes usam cache (~5 min)

---

## 🔐 Segurança

### Proteger API Keys

**Nunca** commite API keys no Git. Use:

```bash
railway variables set GROQ_API_KEY="<sua_chave>"
```

### Limitar CORS (Produção)

Edite `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pele.manus.space"],  # Seu domínio
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

---

## 📚 Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `railway login` | Fazer login |
| `railway init` | Criar projeto |
| `railway up` | Deploy |
| `railway logs` | Ver logs |
| `railway status` | Ver status |
| `railway domain` | Gerar URL pública |
| `railway variables` | Ver variáveis |
| `railway open` | Abrir dashboard |
| `railway restart` | Reiniciar serviço |
| `railway delete` | Deletar projeto |

---

## 🆘 Suporte

- **Documentação Railway:** https://docs.railway.app/
- **Discord Railway:** https://discord.gg/railway
- **Issues GitHub:** <seu-repositorio>/issues

---

## ✅ Checklist Final

Após deploy bem-sucedido:

- [ ] API respondendo em `/health`
- [ ] URL pública gerada
- [ ] `VITE_CLASSIFIER_API_URL` configurado no frontend
- [ ] Frontend republicado
- [ ] Teste de classificação funcionando
- [ ] Logs sem erros críticos

**Pronto! Sua API está no ar! 🎉**
