#!/bin/bash

# Script Semi-Automático de Deploy no Railway
# Classificador de Câncer de Pele - API Python

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cor
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║   Skin Cancer Classifier - Deploy Automático         ║
║   Railway Platform                                    ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Passo 1: Verificar Railway CLI
print_step "Verificando Railway CLI..."
if ! command -v railway &> /dev/null; then
    print_error "Railway CLI não encontrado!"
    echo ""
    echo "Instalando Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    
    # Adicionar ao PATH
    export PATH="$HOME/.railway/bin:$PATH"
    
    if ! command -v railway &> /dev/null; then
        print_error "Falha na instalação. Instale manualmente:"
        echo "  curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
fi
print_success "Railway CLI instalado"

# Passo 2: Verificar login
print_step "Verificando autenticação..."
if ! railway whoami &> /dev/null; then
    print_warning "Você não está logado no Railway"
    echo ""
    echo "Abrindo navegador para login..."
    echo "Por favor, faça login com sua conta GitHub ou email"
    echo ""
    read -p "Pressione ENTER para abrir o navegador..."
    
    railway login
    
    if ! railway whoami &> /dev/null; then
        print_error "Login falhou. Tente novamente com: railway login"
        exit 1
    fi
fi

RAILWAY_USER=$(railway whoami 2>/dev/null || echo "Usuário")
print_success "Logado como: $RAILWAY_USER"

# Passo 3: Criar ou selecionar projeto
print_step "Configurando projeto Railway..."

# Verificar se já existe projeto linkado
if railway status &> /dev/null; then
    print_warning "Projeto Railway já existe neste diretório"
    read -p "Deseja usar o projeto existente? (Y/n): " use_existing
    
    if [[ $use_existing =~ ^[Nn]$ ]]; then
        print_step "Criando novo projeto..."
        railway init
    fi
else
    print_step "Criando novo projeto Railway..."
    railway init --name "skin-cancer-classifier-api"
fi

print_success "Projeto configurado"

# Passo 4: Configurar variáveis de ambiente
print_step "Configurando variáveis de ambiente..."

echo ""
echo "Digite suas API keys (ou pressione ENTER para pular):"
echo ""

read -p "GROQ_API_KEY: " GROQ_KEY
GROQ_KEY=${GROQ_KEY:-YOUR_GROQ_API_KEY_HERE}

read -p "GEMINI_API_KEY (deixe vazio se não tiver): " GEMINI_KEY

# Configurar variáveis
railway variables set GROQ_API_KEY="$GROQ_KEY"
if [ -n "$GEMINI_KEY" ]; then
    railway variables set GEMINI_API_KEY="$GEMINI_KEY"
fi
railway variables set PORT=8000

print_success "Variáveis configuradas"

# Passo 5: Deploy
print_step "Iniciando deploy..."
echo ""
print_warning "Isso pode levar 5-10 minutos (build do Docker + instalação de dependências)"
echo ""

railway up --detach

print_success "Deploy iniciado!"

# Passo 6: Aguardar deploy
print_step "Aguardando deploy completar..."
echo ""
echo "Monitorando logs (Ctrl+C para sair)..."
echo ""

sleep 5
railway logs --tail 50

# Passo 7: Obter URL
print_step "Obtendo URL pública..."

# Gerar domínio público
railway domain

sleep 3

# Capturar URL
API_URL=$(railway domain 2>/dev/null | grep -oP 'https://[^\s]+' | head -1)

if [ -z "$API_URL" ]; then
    print_warning "Não foi possível obter URL automaticamente"
    echo ""
    echo "Execute manualmente:"
    echo "  railway domain"
    echo ""
else
    print_success "Deploy concluído!"
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  DEPLOY COMPLETO!                     ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "URL da API: ${BLUE}$API_URL${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. Testar API:"
    echo -e "     ${YELLOW}curl $API_URL/health${NC}"
    echo ""
    echo "  2. Configurar frontend:"
    echo -e "     ${YELLOW}VITE_CLASSIFIER_API_URL=$API_URL${NC}"
    echo ""
    echo "  3. Monitorar logs:"
    echo -e "     ${YELLOW}railway logs${NC}"
    echo ""
    
    # Salvar URL em arquivo
    echo "$API_URL" > .railway_url
    print_success "URL salva em .railway_url"
fi

echo ""
print_success "Script concluído!"
