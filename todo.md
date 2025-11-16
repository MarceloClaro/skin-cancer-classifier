# Project TODO

## Features to Implement

- [x] Hero section com título e descrição do projeto
- [x] Seção sobre o hardware K230 (capacidades, especificações)
- [x] Seção de resultados científicos (teste de seeds, métricas)
- [x] Seção de metodologia (rigor Qualis A1)
- [x] Seção de impacto social e aplicação clínica
- [x] Seção para investidores (ROI, escalabilidade, mercado)
- [x] Seção de documentação técnica (links para docs)
- [x] Seção de equipe e autoria
- [x] Footer com contatos e licença
- [x] Design responsivo (mobile-first)
- [x] Animações e micro-interações
- [x] Integração de imagens do K230
- [x] Seção de download do framework

## Novas Features Solicitadas

- [x] Formulário de contato para pesquisadores e investidores
- [x] Chat flutuante com bot técnico
- [x] Integração com API Gemini para respostas automáticas
- [x] Sistema de conhecimento sobre o projeto para o bot

## Correções Necessárias

- [x] Corrigir integração hardcoded da API Gemini no ChatBot
- [x] Testar funcionamento do chat bot com API real

## Feature de Banco de Dados

- [x] Adicionar feature web-db-user ao projeto
- [x] Criar schema para tabela de contatos
- [x] Criar schema para tabela de conversas do chat
- [x] Implementar persistência no formulário de contato
- [x] Implementar persistência no histórico do chat bot
- [ ] Criar painel administrativo para visualizar dados

## Sistema de Notificações Personalizadas

- [x] Implementar sistema de toast notifications
- [x] Adicionar notificações de sucesso no formulário
- [x] Adicionar notificações de erro
- [x] Integrar notificações com o chat bot
- [x] Criar notificações personalizadas por tipo de ação

## Bug Crítico

- [x] Corrigir chat bot que está retornando erro para todas as mensagens
- [x] Verificar integração da API Gemini
- [x] Testar comunicação com a API

## Correção da Chave API Gemini

- [x] Atualizar chave API do Gemini para AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0
- [x] Testar chat bot com nova chave

## Teste e Correção da API Gemini

- [x] Criar script de teste da API Gemini
- [x] Executar teste e identificar erros
- [x] Corrigir problemas de conexão/formato (modelo gemini-pro-latest + chave funcional)
- [x] Verificar funcionamento do chat bot

## Bug Crítico - Chat Bot Sem Resposta

- [x] Verificar logs do servidor em tempo real
- [x] Testar endpoint tRPC manualmente
- [x] Identificar problema na comunicação frontend-backend (imports faltantes)
- [x] Corrigir e validar funcionamento completo

## Bug Urgente - Chat Bot Falhando no Processamento

- [ ] Adicionar logs detalhados no backend (server/routers.ts)
- [ ] Testar chat bot e capturar logs de erro completos
- [ ] Identificar causa raiz do erro na API Gemini
- [ ] Corrigir problema e validar funcionamento

## Integração do Sistema de Classificação de Câncer de Pele

- [x] Analisar código appv4.py do GitHub (https://github.com/marceloclaro/pele)
- [x] Criar backend Python para classificação com TensorFlow/Keras e MobileNetV2
- [x] Implementar geração de Grad-CAM (mapa de calor) para interpretabilidade
- [x] Integrar API Gemini para gerar diagnósticos baseados em estatísticas e Grad-CAM
- [x] Criar endpoint tRPC para upload de imagens e classificação
- [x] Implementar interface web de upload de imagens dermatoscópicas
- [x] Adicionar visualização de resultados (classe, confiança, Grad-CAM, diagnóstico)
- [x] Criar seção "Classificação ao Vivo" no site (/classificador)
- [x] Testar sistema completo end-to-end
- [x] Corrigir Grad-CAM para MobileNetV2
- [x] Atualizar chave API Gemini no gerador de diagnósticos
- [ ] Documentar API e uso do sistema


## Treinamento de Modelo Personalizado

- [x] Extrair dataset TREINO.zip (40 imagens: 20 BENIGNO + 20 MALIGNO)
- [x] Analisar estrutura e classes do dataset
- [x] Criar script de treinamento com data augmentation agressivo
- [x] Implementar transfer learning com MobileNetV2 em 2 fases
- [x] Treinar modelo com validação (80/20 split)
- [x] Avaliar métricas (Acurácia: 75%, AUC: 0.62)
- [x] Gerar matriz de confusão e curvas ROC
- [x] Salvar modelo treinado (skin_cancer_model.h5)
- [x] Criar binary_skin_classifier.py para modelo binário
- [x] Integrar endpoint tRPC classifyBinary
- [x] Atualizar frontend com badge de modelo treinado
- [x] Testar classificador com modelo personalizado (MALIGNO 64.68%)
- [ ] Documentar processo de treinamento e resultados


## Correção de Erro na Análise de Lesões

- [x] Implementar sistema de logs detalhado no backend (routers.ts)
- [x] Adicionar logs no binary_skin_classifier.py
- [x] Criar wrapper Python robusto (classify_wrapper.py)
- [x] Verificar logs do servidor em tempo real
- [x] Reproduzir erro com upload de imagem
- [x] Analisar stack trace completo (SRE module mismatch)
- [x] Identificar causa raiz: scripts temporários com módulos Python inconsistentes
- [x] Implementar correção robusta: wrapper isolado com subprocess
- [x] Corrigir busca de camada Grad-CAM (Conv_1 dentro de MobileNetV2)
- [x] Adicionar tratamento de exceções apropriado
- [x] Validar correção com múltiplos testes (Grad-CAM: 153.770 chars)
- [x] Documentar solução e prevenção (TROUBLESHOOTING.md)


## Melhorias Avançadas do Sistema de Classificação

### Correção de Erro Persistente
- [x] Verificar logs do servidor em tempo real
- [x] Reproduzir erro com upload de imagem via interface web
- [x] Analisar resposta completa do endpoint tRPC
- [x] Identificar causa raiz específica do erro atual (SRE module mismatch + Grad-CAM)
- [x] Implementar correção definitiva (wrapper Python isolado)

### Análise Multimodal com Gemini Vision
- [x] Integrar Gemini Vision API para análise de imagens
- [x] Criar prompt especializado para dermatologia (critérios ABCD, diagnóstico diferencial)
- [x] Combinar classificação CNN + análise LLM
- [x] Gerar diagnóstico rico com contexto visual (inclui Grad-CAM)
- [x] Implementar fallback robusto

### Sistema de Salvamento de Imagens
- [x] Criar estrutura de diretórios para dataset incremental
- [x] Salvar imagens classificadas com metadados (classe, confiança, timestamp)
- [x] Organizar por classe predita (BENIGNO/MALIGNO)
- [x] Implementar versionamento de dataset (hash MD5 para evitar duplicatas)
- [ ] Criar interface de revisão manual (admin)

### Retreinamento Automático
- [ ] Criar script de retreinamento incremental
- [ ] Implementar data augmentation adaptativo
- [ ] Monitorar métricas de performance
- [ ] Salvar checkpoints de modelos
- [ ] Implementar A/B testing de modelos

### Exportação TFLite
- [x] Converter modelo Keras para TFLite
- [x] Otimizar modelo (quantização INT8 - 69.8% compressão)
- [x] Validar acurácia pós-conversão
- [x] Criar endpoint de download do modelo (model.download)
- [x] Gerar documentação de uso (K230) com exemplos Python/C++
- [x] Adicionar botão de download na interface

### Testes e Validação
- [x] Testar fluxo completo via wrapper Python (classificação + Grad-CAM + análise)
- [x] Validar salvamento de imagens (dataset_incremental com hash MD5)
- [x] Verificar download de modelo TFLite (endpoint model.download)
- [x] Corrigir Grad-CAM (acesso correto à camada Conv_1)
- [x] Corrigir Gemini Vision (remover safetySettings inválido)
- [ ] Testar fluxo completo via interface web
- [ ] Documentar processo completo
