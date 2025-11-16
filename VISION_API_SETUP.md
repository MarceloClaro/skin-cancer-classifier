# Google Cloud Vision API - Guia de Configuração

## 📋 Visão Geral

Este sistema integra a **Google Cloud Vision API** para análise dermatoscópica avançada de lesões de pele, combinando classificação por CNN (MobileNetV2) com detecção visual de características (labels, cores dominantes, objetos).

## 🔑 Configuração da API Key

### Passo 1: Habilitar a Vision API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione seu projeto (ou crie um novo)
3. Vá em **APIs & Services** → **Library**
4. Procure por "**Cloud Vision API**"
5. Clique em **Enable** (Ativar)
6. Aguarde alguns minutos para propagação

### Passo 2: Criar API Key

1. No Google Cloud Console, vá em **APIs & Services** → **Credentials**
2. Clique em **+ CREATE CREDENTIALS** → **API key**
3. Copie a chave gerada (formato: `AIzaSy...`)
4. (Opcional) Clique em **Restrict Key** para limitar uso:
   - **Application restrictions:** None (ou HTTP referrers para produção)
   - **API restrictions:** Restrict key → Selecione "Cloud Vision API"

### Passo 3: Configurar no Projeto

#### Desenvolvimento (Local)

```bash
export VISION_API_KEY="AIzaSy..."
# ou
export GEMINI_API_KEY="AIzaSy..."  # Fallback automático
```

#### Produção (Manus)

1. Acesse o painel de gerenciamento do projeto
2. Vá em **Settings** → **Secrets**
3. Adicione nova secret:
   - **Key:** `VISION_API_KEY`
   - **Value:** `AIzaSy...`

## 🧪 Testar Integração

### Teste 1: Vision API Diretamente

```bash
cd /home/ubuntu/skin_cancer_classifier_k230_page

# Testar com imagem de lesão
VISION_API_KEY="AIzaSy..." python3 server/vision_analyzer.py /path/to/image.png
```

**Resultado Esperado:**
```json
{
  "success": true,
  "labels": [
    {"description": "Skin", "confidence": 95.2},
    {"description": "Mole", "confidence": 87.3}
  ],
  "dominant_colors": [
    {"red": 180, "green": 120, "blue": 90, "pixel_fraction": 0.45}
  ],
  "objects": [
    {"name": "Lesion", "confidence": 82.1}
  ]
}
```

### Teste 2: Classificação Completa (CNN + Vision API)

```bash
python3 server/classify_wrapper.py /path/to/image.png true true
```

**Resultado Esperado:**
```json
{
  "success": true,
  "class": "MALIGNO",
  "confidence": 0.82,
  "risk_level": "ALTO",
  "gradcam": "data:image/png;base64,...",
  "diagnosis": {
    "success": true,
    "analysis": "# Análise Dermatoscópica Multimodal\n\n...",
    "model": "vision_api",
    "vision_data": { ... }
  }
}
```

## 📊 Features da Vision API Utilizadas

### 1. LABEL_DETECTION
Detecta características visuais gerais da imagem:
- Tipo de pele (Skin)
- Estruturas (Mole, Lesion, Spot)
- Texturas (Rough, Smooth)
- Padrões (Irregular, Asymmetric)

**Máximo:** 20 labels por imagem

### 2. IMAGE_PROPERTIES
Extrai cores dominantes da lesão:
- RGB values
- Pixel fraction (% da imagem)
- Score (relevância da cor)

**Uso clínico:** Detecção de variação de cores (critério ABCDE)

### 3. SAFE_SEARCH_DETECTION
Verifica se a imagem é apropriada para análise médica:
- Adult content: VERY_UNLIKELY
- Medical content: LIKELY
- Violence: VERY_UNLIKELY

### 4. OBJECT_LOCALIZATION
Localiza e identifica objetos na imagem:
- Bounding boxes
- Confidence scores
- Object names

**Máximo:** 10 objetos por imagem

## 🔄 Sistema de Fallback

O sistema implementa fallback automático quando a Vision API está indisponível:

```python
# Fluxo de decisão
if vision_api.success:
    # Relatório multimodal (CNN + Vision API)
    diagnosis = generate_multimodal_report(cnn_result, vision_result)
else:
    # Relatório CNN apenas
    diagnosis = generate_cnn_report(cnn_result)
```

**Causas de Fallback:**
- API key inválida ou expirada
- Vision API não habilitada no projeto
- Timeout de requisição (> 60s)
- Quota excedida
- Erro de rede

## 📈 Relatório Multimodal

Quando a Vision API está ativa, o diagnóstico inclui:

### Seção 1: Classificação CNN
- Resultado (BENIGNO/MALIGNO)
- Confiança (%)
- Nível de risco

### Seção 2: Características Visuais (Vision API)
- **Labels detectados:** Top 5 características
- **Cores dominantes:** Top 3 cores RGB
- **Estruturas detectadas:** Objetos localizados

### Seção 3: Interpretação Clínica
- Achados sugestivos
- Recomendações (encaminhamento, biópsia, monitoramento)

### Seção 4: Diagnóstico Diferencial
- Lista de possíveis diagnósticos (5 opções)

### Seção 5: Notas Importantes
- Limitações do sistema
- Necessidade de correlação clínica

## 🚨 Troubleshooting

### Erro 403: PERMISSION_DENIED

```json
{
  "error": {
    "code": 403,
    "message": "Requests to this API ... are blocked.",
    "reason": "API_KEY_SERVICE_BLOCKED"
  }
}
```

**Solução:**
1. Verificar se Vision API está habilitada no projeto
2. Aguardar 5-10 minutos após habilitar
3. Verificar se API key tem permissões corretas

### Erro 400: INVALID_ARGUMENT

```json
{
  "error": {
    "code": 400,
    "message": "Invalid image content"
  }
}
```

**Solução:**
- Verificar se imagem está em formato válido (PNG, JPG, WEBP)
- Verificar se imagem não está corrompida
- Verificar tamanho máximo (20 MB para Vision API)

### Erro 429: RESOURCE_EXHAUSTED

```json
{
  "error": {
    "code": 429,
    "message": "Quota exceeded"
  }
}
```

**Solução:**
- Verificar quota no Google Cloud Console
- Aguardar reset da quota (geralmente diário)
- Considerar upgrade do plano

## 💰 Custos

### Vision API Pricing (Novembro 2025)

| Feature | Primeiras 1.000 unidades/mês | Acima de 1.000 unidades/mês |
|---------|------------------------------|------------------------------|
| LABEL_DETECTION | Grátis | $1.50 / 1.000 imagens |
| IMAGE_PROPERTIES | Grátis | $1.50 / 1.000 imagens |
| SAFE_SEARCH_DETECTION | Grátis | $1.50 / 1.000 imagens |
| OBJECT_LOCALIZATION | Grátis | $1.50 / 1.000 imagens |

**Exemplo de Uso:**
- 100 classificações/dia = 3.000 imagens/mês
- Custo mensal: (3.000 - 1.000) × $1.50 / 1.000 = **$3.00**

**Referência:** [Vision API Pricing](https://cloud.google.com/vision/pricing)

## 📚 Referências

- [Cloud Vision API Documentation](https://cloud.google.com/vision/docs)
- [Vision API REST Reference](https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate)
- [Vision API Python Client](https://cloud.google.com/python/docs/reference/vision/latest)
- [Vision API Supported Image Formats](https://cloud.google.com/vision/docs/supported-files)

## 🔐 Segurança

### Boas Práticas

1. **Nunca commitar API keys** no código-fonte
2. **Usar variáveis de ambiente** para armazenar chaves
3. **Restringir API keys** por IP ou domínio em produção
4. **Rotacionar chaves** periodicamente (a cada 90 dias)
5. **Monitorar uso** no Google Cloud Console
6. **Habilitar alertas** de quota e custos

### Restrições Recomendadas

```
Application restrictions:
  - HTTP referrers: https://pele.manus.space/*

API restrictions:
  - Cloud Vision API only
```

## 📞 Suporte

Para problemas com a Vision API:
1. Verificar [Status Dashboard](https://status.cloud.google.com/)
2. Consultar [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-vision)
3. Abrir ticket no [Google Cloud Support](https://cloud.google.com/support)

---

**Última atualização:** Novembro 2025  
**Versão do sistema:** 1.0.0  
**Autor:** Marcelo Claro Laranjeira
