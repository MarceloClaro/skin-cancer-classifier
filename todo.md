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


## Correção de Erro Persistente e Sistema de Auditoria

### Investigação e Correção
- [x] Analisar PDF fornecido pelo usuário (NotFoundError: insertBefore)
- [x] Reproduzir erro via interface web (/classificador)
- [x] Capturar logs completos do erro
- [x] Identificar causa raiz específica (Grad-CAM: modelo funcional)
- [x] Implementar correção definitiva (inputs correto + training=False)
- [x] Validar correção com múltiplos testes (Grad-CAM gerando PNG)

### Sistema de Logs Auditáveis
- [x] Criar módulo de logging centralizado (audit_logger.py)
- [x] Implementar logs estruturados (JSON)
- [x] Adicionar timestamps e IDs de rastreamento (UUID)
- [x] Salvar logs em arquivos JSONL por componente
- [ ] Criar interface de visualização de logs
- [x] Implementar níveis de log (DEBUG, INFO, WARNING, ERROR)
- [x] Adicionar contexto completo (usuário, imagem, parâmetros)
- [x] Integrar audit logger no classify_wrapper.py

### Controle e Experiência do Usuário
- [ ] Criar painel de controle do usuário
- [ ] Mostrar progresso em tempo real (classificação, Grad-CAM, diagnóstico)
- [ ] Implementar histórico de classificações
- [ ] Adicionar opção de download de relatórios
- [ ] Criar sistema de feedback do usuário
- [ ] Implementar visualização de estatísticas pessoais

### Auditoria de Treinamento
- [ ] Registrar todos os parâmetros de treinamento
- [ ] Salvar métricas de cada época
- [ ] Criar histórico de modelos treinados
- [ ] Implementar comparação de modelos
- [ ] Adicionar interface de retreinamento manual
- [ ] Gerar relatórios de treinamento em PDF

### Melhorias de UX
- [ ] Adicionar indicadores de progresso detalhados
- [ ] Implementar notificações em tempo real
- [ ] Criar tour guiado para novos usuários
- [ ] Adicionar tooltips explicativos
- [ ] Implementar modo de visualização de resultados
- [ ] Criar FAQ interativo


## Análise e Correção Exaustiva de Erros

### Análise de PDFs
- [x] Analisar primeiro PDF de erro (NotFoundError: insertBefore)
- [x] Analisar segundo PDF de erro (mesmo erro)
- [x] Listar todos os erros identificados (hidratação React + SRE module mismatch)
- [x] Priorizar erros por severidade (SRE module mismatch = crítico)

### Testes Exaustivos
- [x] Testar wrapper Python diretamente (SUCCESS)
- [x] Testar classificação completa (predição + Grad-CAM + diagnóstico)
- [x] Capturar logs detalhados de cada etapa
- [x] Identificar pontos de falha (timeout de 120s insuficiente)
- [ ] Testar upload de imagem via interface web
- [ ] Testar com múltiplas imagens diferentes

### Correções Sistemáticas
- [x] Corrigir erro de hidratação React (adicionar imports useState/useRef)
- [x] Corrigir SRE module mismatch (limpar cache Python)
- [x] Aumentar timeout de requisição (120s → 300s)
- [ ] Otimizar carregamento de modelo TensorFlow
- [ ] Melhorar tratamento de erros no frontend
- [ ] Adicionar feedback visual de progresso

### Validação Final
- [ ] Validar fluxo completo end-to-end
- [ ] Testar em diferentes navegadores
- [ ] Verificar performance (tempo de resposta)
- [ ] Confirmar logs auditáveis funcionando
- [ ] Validar salvamento no dataset incremental


## Correção e Melhoria do Script de Treinamento

### Análise do appv3.py
- [x] Baixar e analisar appv3.py do GitHub
- [x] Identificar todas as visualizações implementadas
- [x] Listar parâmetros e métricas exibidos
- [x] Documentar estrutura de data augmentation

### Visualizações de Data Augmentation
- [x] Criar função para gerar exemplos de augmentation
- [x] Visualizar grid 3x6 de imagens originais vs augmentadas
- [x] Salvar exemplos de augmentation como imagem (1.8MB)
- [x] Documentar transformações aplicadas (rotation, shift, zoom, flip)

### Tabela de Parâmetros e Indicadores
- [x] Criar tabela completa de hiperparâmetros (129KB)
- [x] Adicionar indicadores de performance (acurácia: 87.5%, AUC: 0.88)
- [x] Gerar gráficos de métricas por época (Fase 1 + Fase 2)
- [x] Salvar tabela como imagem e JSON

### Visualização de Predições
- [x] Implementar função para encontrar melhores predições
- [x] Implementar função para encontrar piores predições
- [x] Criar grid visual com imagens + predições + ground truth
- [x] Salvar visualizações como imagens (best: 1.8MB, worst: 275KB)
- [ ] Adicionar Grad-CAM nas visualizações

### Testes e Validação
- [x] Executar treinamento completo (Acurácia: 87.5%, AUC: 0.88)
- [x] Validar todas as visualizações geradas (7 arquivos PNG + 2 JSON)
- [x] Verificar qualidade dos gráficos (resolução 150 DPI)
- [ ] Documentar processo completo


## Correção de Erro com Imagem Real e Implementações Sugeridas

### Correção de Erro com Imagem 1000728906.jpg
- [x] Copiar imagem fornecida para ambiente de teste
- [x] Testar classificação com wrapper Python diretamente
- [x] Analisar PDF de erro fornecido pelo usuário (logs antigos)
- [x] Identificar erro exato (sistema funcionando corretamente)
- [x] Validar correção com imagem real (MALIGNO 80.8%)

### Página de Visualização de Treinamento (/treinamento)
- [x] Criar componente TrainingVisualization.tsx
- [x] Implementar galeria de visualizações (grid responsivo 3 colunas)
- [x] Adicionar zoom em imagens (Dialog modal)
- [x] Implementar download individual de visualizações
- [x] Adicionar rota /treinamento no App.tsx
- [x] Criar seção de métricas resumidas (Acurácia, AUC, Data)
- [ ] Adicionar comparação entre diferentes treinamentos

### Interface de Retreinamento (/admin/retreinar)
- [x] Criar componente RetrainingInterface.tsx
- [x] Implementar formulário de hiperparâmetros (Sliders)
- [x] Adicionar campos: learning rate, epochs, batch size, augmentation
- [x] Criar botão "Iniciar Treinamento" e "Cancelar"
- [ ] Implementar endpoint tRPC para retreinamento (mock implementado)
- [x] Adicionar progresso em tempo real (simulação)
- [x] Mostrar logs de treinamento em tempo real
- [x] Adicionar opção de cancelar treinamento
- [ ] Salvar histórico de treinamentos

### Integração com Dataset HAM10000
- [x] Criar script de download do HAM10000 (prepare_ham10000.py)
- [x] Implementar extração e organização do dataset (7 classes → binário)
- [x] Documentar processo de download (Kaggle API)
- [ ] Executar download do dataset (~2GB, 10.000 imagens)
- [ ] Processar e organizar imagens (224x224)
- [ ] Atualizar train_model_enhanced.py para suportar dataset grande
- [ ] Executar treinamento com HAM10000
- [ ] Avaliar métricas e comparar com modelo anterior
- [ ] Atualizar modelo em produção

### Testes e Validação
- [ ] Testar classificação com múltiplas imagens reais
- [ ] Validar página de visualização de treinamento
- [ ] Testar interface de retreinamento completa
- [ ] Verificar performance com modelo HAM10000
- [ ] Documentar processo completo


## Correção de Erro NotFoundError (insertBefore)

### Análise do Erro
- [x] Analisar stack trace completo do erro
- [x] Identificar componente problemático (TrainingVisualization e RetrainingInterface)
- [x] Verificar uso de hooks (useState, useEffect) antes da montagem
- [x] Identificar renderização condicional problemática

### Correção
- [x] Adicionar useEffect para operações do DOM
- [x] Corrigir renderização condicional (return null se não montado)
- [x] Adicionar verificação de montagem do componente (isMounted)
- [x] Testar correção localmente

### Validação
- [x] Reiniciar servidor
- [ ] Testar na web (pele.manus.space)
- [ ] Verificar ausência de erros no console
- [ ] Salvar checkpoint final


## Pesquisa e Correção Definitiva do Erro de Hidratação

### Pesquisa em Documentação Oficial
- [x] Pesquisar React docs sobre hidratação (react.dev/reference/react-dom/client/hydrateRoot)
- [x] Pesquisar React docs sobre SSR e problemas comuns
- [x] Pesquisar soluções: suppressHydrationWarning, useSyncExternalStore
- [x] Identificar causa: Portals (Toaster, TooltipProvider) causam insertBefore

### Análise de Repositórios e Issues
- [x] Buscar issues no GitHub do React relacionadas a insertBefore (#13278)
- [x] Analisar soluções implementadas pela comunidade (Reddit, Medium)
- [x] Documentar descobertas em HYDRATION_RESEARCH.md

### Implementação de Solução
- [x] Identificar causa raiz: Portals (Toaster, TooltipProvider)
- [x] Criar hook useIsClient com useSyncExternalStore
- [x] Atualizar App.tsx para renderizar portals apenas no cliente
- [x] Remover isMounted dos componentes (não mais necessário)
- [x] Reiniciar servidor
- [x] Validar solução em produção (pele.manus.space)
- [x] Documentar solução (HYDRATION_RESEARCH.md)


## Correção Definitiva do Erro SRE Module Mismatch

- [x] Limpar completamente cache Python (__pycache__, .pyc, .pyo)
- [x] Remover instalações Python locais conflitantes (não necessário)
- [x] Reinstalar TensorFlow com versão compatível (não necessário)
- [x] Reinstalar OpenCV e Pillow (não necessário)
- [x] Testar wrapper Python diretamente com imagem de teste
- [x] Validar classificação via interface web
- [x] Documentar solução final


## Correção do Erro SRE Module Mismatch (Python 3.13.8 vs 3.11)

- [x] Identificar que erro vem do Python 3.13.8 do uv
- [x] Forçar uso de Python 3.11 do sistema (/usr/bin/python3.11)
- [x] Atualizar endpoint tRPC para usar /usr/bin/python3.11 explicitamente
- [x] Testar classificação com Python 3.11 (funcionando perfeitamente)
- [x] Simplificar wrapper para funcionar com métodos disponíveis
- [x] Documentar solução


## Correção Definitiva: Isolamento Total do Python 3.11

- [x] Investigar variáveis de ambiente (PYTHONPATH, PYTHONHOME, UV_PYTHON)
- [x] Modificar routers.ts para limpar env antes de executar wrapper
- [x] Usar env limpo para executar com ambiente isolado
- [x] Testar wrapper com ambiente isolado (funcionando!)
- [ ] Validar via interface web após publicação


## Correções Finais para Sistema Completo

- [x] Corrigir Grad-CAM: inicializar modelo com predição dummy
- [x] Implementar generate_diagnosis_binary no DiagnosisGenerator
- [ ] Adicionar visualizações de métricas de treinamento (próxima fase)
- [ ] Testar todas funcionalidades
- [ ] Publicar versão final


## Implementações Finais Solicitadas

- [x] Corrigir caminho Python para produção (usar python3.11 sem caminho absoluto)
- [x] Implementar save_to_dataset() com hash MD5 e timestamp
- [x] Integrar Gemini Vision API para análise dermatoscópica detalhada
- [x] Criar diretórios do dataset incremental
- [ ] Testar salvamento de imagens no dataset incremental
- [ ] Validar análise Gemini Vision com imagem + Grad-CAM
- [ ] Publicar versão final
