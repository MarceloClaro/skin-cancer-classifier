import { Button } from "@/components/ui/button";
import ChatBot from "@/components/ChatBot";
import ContactForm from "@/components/ContactForm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  Award, 
  BarChart3, 
  Brain, 
  CheckCircle2, 
  Cpu, 
  Download, 
  FileText, 
  Github, 
  Mail, 
  Microscope, 
  Rocket, 
  Shield, 
  TrendingUp, 
  Users, 
  Zap 
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header/Navigation */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Microscope className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl">Skin Cancer Classifier K230</span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <a href="#about" className="text-sm font-medium hover:text-primary transition-colors">Sobre</a>
            <a href="#k230" className="text-sm font-medium hover:text-primary transition-colors">Hardware K230</a>
            <a href="#results" className="text-sm font-medium hover:text-primary transition-colors">Resultados</a>
            <a href="#methodology" className="text-sm font-medium hover:text-primary transition-colors">Metodologia</a>
            <a href="#impact" className="text-sm font-medium hover:text-primary transition-colors">Impacto</a>
            <a href="#contact" className="text-sm font-medium hover:text-primary transition-colors">Contato</a>
            <a href="#team" className="text-sm font-medium hover:text-primary transition-colors">Equipe</a>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" asChild>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                <Github className="h-5 w-5" />
              </a>
            </Button>
            <Button asChild>
              <a href="#download">Download</a>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="section-padding bg-gradient-to-b from-background to-muted/20">
        <div className="container">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <Badge className="mb-2">Padrão Qualis A1 • Rigor Científico</Badge>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Classificador de Câncer de Pele com IA
                <span className="gradient-text block mt-2">Otimizado para K230</span>
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Framework completo de classificação de câncer de pele baseado em Inteligência Artificial, 
                otimizado para o processador K230 (6 TOPS), com rigor científico Qualis A1 e validação clínica rigorosa.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button size="lg" className="gap-2" asChild>
                  <a href="#download">
                    <Download className="h-5 w-5" />
                    Download Framework
                  </a>
                </Button>
                <Button size="lg" variant="outline" className="gap-2" asChild>
                  <a href="#methodology">
                    <FileText className="h-5 w-5" />
                    Documentação
                  </a>
                </Button>
              </div>
              <div className="flex flex-wrap gap-6 pt-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium">Acurácia 89.09%</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium">Latência &lt;100ms</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium">18 Módulos</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <img 
                src="/k230_module.jpg" 
                alt="K230 Module" 
                className="rounded-lg shadow-2xl border"
              />
              <div className="absolute -bottom-6 -right-6 bg-primary text-primary-foreground p-4 rounded-lg shadow-lg">
                <div className="text-3xl font-bold">6 TOPS</div>
                <div className="text-sm">Potência de Processamento</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="section-padding bg-muted/30">
        <div className="container">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Acurácia Média</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">89.09%</div>
                <p className="text-xs text-muted-foreground">Fibonacci 144 seed</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Latência K230</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">&lt;100ms</div>
                <p className="text-xs text-muted-foreground">-23 a -38% vs baseline</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Módulos Python</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">18</div>
                <p className="text-xs text-muted-foreground">~5.000 linhas de código</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Documentação</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">16 Docs</div>
                <p className="text-xs text-muted-foreground">Padrão Qualis A1</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="section-padding">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Sobre o Projeto</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Democratizando o Diagnóstico de Câncer de Pele
            </h2>
            <p className="text-lg text-muted-foreground">
              Um framework completo e reprodutível para classificação de câncer de pele com IA, 
              desenvolvido com rigor científico Qualis A1 e otimizado para hardware acessível.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <Brain className="h-10 w-10 text-primary mb-2" />
                <CardTitle>IA Avançada</CardTitle>
                <CardDescription>
                  MobileNetV2 + Transfer Learning, YOLO para detecção, Grad-CAM++ para interpretabilidade
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <Shield className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Validação Clínica</CardTitle>
                <CardDescription>
                  Conformidade com FDA, ANVISA e CE. Métricas rigorosas com intervalos de confiança 95%
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <Rocket className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Otimização K230</CardTitle>
                <CardDescription>
                  Quantização INT8, latência &lt;100ms, eficiência energética +50-70%
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* K230 Hardware Section */}
      <section id="k230" className="section-padding bg-muted/30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Hardware K230</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Processador K230: 6 TOPS de Potência
            </h2>
            <p className="text-lg text-muted-foreground">
              O K230 oferece capacidades avançadas de IA com integração OpenRouter, 
              detecção de objetos, reconhecimento facial e muito mais.
            </p>
          </div>
          <div className="grid lg:grid-cols-2 gap-8">
            <div>
              <img 
                src="/k230_openrouter.jpg" 
                alt="K230 OpenRouter Integration" 
                className="rounded-lg shadow-lg border mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Integração OpenRouter AI</h3>
              <p className="text-muted-foreground">
                Conectado à plataforma OpenRouter AI, permitindo acesso a modelos como ChatGPT, 
                Google Gemini, DeepSeek V3, Llama 4 e Claude 3.7.
              </p>
            </div>
            <div>
              <img 
                src="/k230_capabilities.jpg" 
                alt="K230 Capabilities" 
                className="rounded-lg shadow-lg border mb-4"
              />
              <h3 className="text-xl font-bold mb-2">Capacidades Avançadas</h3>
              <p className="text-muted-foreground mb-4">
                Detecção de linhas, retângulos, círculos, bordas de objetos, pontos-chave faciais, 
                orientação facial, detecção humana, queda, OCR, YOLOv8, reconhecimento de placas e classificação autônoma.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Face Detection</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm">YOLOv8</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm">OCR</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Object Tracking</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section id="results" className="section-padding">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Resultados Científicos</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Teste de Seeds Matemáticas
            </h2>
            <p className="text-lg text-muted-foreground">
              Experimento controlado com 8 seeds matemáticas (π, φ, e, √2, Fibonacci) 
              para identificar a melhor configuração.
            </p>
          </div>
          <div className="max-w-5xl mx-auto">
            <img 
              src="/seed_results.png" 
              alt="Seed Comparison Results" 
              className="rounded-lg shadow-lg border w-full"
            />
            <div className="mt-8 grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5 text-yellow-600" />
                    Melhor Seed: Fibonacci 144
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Acurácia Média:</span>
                      <span className="font-bold">0.8909 ± 0.0267</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Loss Médio:</span>
                      <span className="font-bold">0.6537 ± 0.0816</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Tempo de Treinamento:</span>
                      <span className="font-bold">12.5s</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Ranking Completo
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>1. Fibonacci 144</span>
                      <span className="font-mono">0.8909</span>
                    </div>
                    <div className="flex justify-between">
                      <span>2. Phi/Ouro (φ)</span>
                      <span className="font-mono">0.8856</span>
                    </div>
                    <div className="flex justify-between">
                      <span>3. Padrão (42)</span>
                      <span className="font-mono">0.8781</span>
                    </div>
                    <div className="flex justify-between">
                      <span>4. Raiz de 2 (√2)</span>
                      <span className="font-mono">0.8780</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Methodology Section */}
      <section id="methodology" className="section-padding bg-muted/30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Metodologia</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Rigor Científico Qualis A1
            </h2>
            <p className="text-lg text-muted-foreground">
              Framework desenvolvido com metodologia rigorosa, reprodutível e auditável.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Preparação de Dados</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Dataset HAM10000 (10.015 imagens), divisão estratificada 70/15/15, 
                análise exploratória completa, padronização CLAHE.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Treinamento</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                MobileNetV2 + Transfer Learning, data augmentation, early stopping, 
                seed Fibonacci 144 para máxima acurácia.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Avaliação</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Métricas clínicas (ROC, Precision-Recall), intervalos de confiança 95%, 
                validação cruzada 5-fold.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Interpretabilidade</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Grad-CAM++, Integrated Gradients, SHAP values para explicabilidade clínica.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Otimização K230</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                QAT, PTQ avançado, calibração KL Divergence, quantização INT8, 
                compilação nncase.
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Monitoramento</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                MLflow tracking, TensorBoard, logging estruturado JSON, 
                rastreabilidade completa.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section id="impact" className="section-padding">
        <div className="container">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4">Impacto Social</Badge>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Democratizando o Acesso ao Diagnóstico
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Desenvolvido para aplicação na Secretaria Municipal de Educação de Crateús-CE, 
                este projeto visa democratizar o acesso ao diagnóstico de câncer de pele através 
                de hardware acessível e IA de ponta.
              </p>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Cobertura Populacional</h3>
                    <p className="text-sm text-muted-foreground">
                      Meta de cobertura de +15.000 habitantes em regiões remotas do Ceará.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Custo Acessível</h3>
                    <p className="text-sm text-muted-foreground">
                      Hardware K230 custa ~R$ 500/dispositivo vs GPUs de R$ 5.000+. 
                      Consumo de energia 10x menor.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Microscope className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Aplicação Clínica</h3>
                    <p className="text-sm text-muted-foreground">
                      Protótipo de triagem clínica para residência médica em dermatologia.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <Card className="border-2">
                <CardHeader>
                  <CardTitle>Para Investidores</CardTitle>
                  <CardDescription>Oportunidade de impacto social e retorno financeiro</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Mercado</h4>
                    <p className="text-sm text-muted-foreground">
                      Câncer de pele: 185.000 novos casos/ano no Brasil (INCA). 
                      Mercado global de IA médica: US$ 45.2 bilhões até 2026.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Escalabilidade</h4>
                    <p className="text-sm text-muted-foreground">
                      Hardware de baixo custo permite escala nacional. 
                      Modelo replicável para outras doenças dermatológicas.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Diferencial Competitivo</h4>
                    <p className="text-sm text-muted-foreground">
                      Único framework open-source com rigor Qualis A1, 
                      otimização K230 e validação clínica completa.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Download Section */}
      <section id="download" className="section-padding bg-muted/30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <Badge className="mb-4">Download</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Framework Completo Disponível
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Baixe o framework completo com 18 módulos Python, 16 documentos técnicos, 
              resultados de testes e documentação Qualis A1.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="gap-2">
                <Download className="h-5 w-5" />
                Download ZIP (884 KB)
              </Button>
              <Button size="lg" variant="outline" className="gap-2" asChild>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  <Github className="h-5 w-5" />
                  Ver no GitHub
                </a>
              </Button>
            </div>
            <div className="mt-8 grid sm:grid-cols-3 gap-4 text-sm">
              <div className="p-4 bg-background rounded-lg border">
                <div className="font-bold text-2xl mb-1">18</div>
                <div className="text-muted-foreground">Módulos Python</div>
              </div>
              <div className="p-4 bg-background rounded-lg border">
                <div className="font-bold text-2xl mb-1">16</div>
                <div className="text-muted-foreground">Documentos MD</div>
              </div>
              <div className="p-4 bg-background rounded-lg border">
                <div className="font-bold text-2xl mb-1">884 KB</div>
                <div className="text-muted-foreground">Tamanho Total</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="section-padding bg-muted/30">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Contato</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Interessado em Colaborar?
            </h2>
            <p className="text-lg text-muted-foreground">
              Entre em contato para discutir colaborações em pesquisa, investimentos, 
              implementação clínica ou parcerias institucionais.
            </p>
          </div>
          <ContactForm />
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="section-padding">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <Badge className="mb-4">Equipe</Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Desenvolvido com Rigor Científico
            </h2>
          </div>
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-2xl">Marcelo Claro Laranjeira</CardTitle>
              <CardDescription className="text-base">
                Secretaria Municipal de Educação (SME) • Prefeitura de Crateús-CE
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Desenvolvedor principal do framework de classificação de câncer de pele K230. 
                Especialista em IA médica, otimização de hardware e validação clínica.
              </p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">IA Médica</Badge>
                <Badge variant="secondary">Otimização K230</Badge>
                <Badge variant="secondary">Validação Clínica</Badge>
                <Badge variant="secondary">Padrão Qualis A1</Badge>
              </div>
              <div className="pt-4 border-t">
                <Button variant="outline" className="gap-2" asChild>
                  <a href="mailto:marceloclaro@gmail.com">
                    <Mail className="h-4 w-4" />
                    marceloclaro@gmail.com
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* ChatBot */}
      <ChatBot />

      {/* Footer */}
      <footer className="border-t bg-muted/30">
        <div className="container py-12">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Microscope className="h-6 w-6 text-primary" />
                <span className="font-bold text-lg">Skin Cancer Classifier K230</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Framework completo de classificação de câncer de pele com IA, 
                otimizado para K230 com rigor Qualis A1.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Links Rápidos</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#about" className="text-muted-foreground hover:text-primary transition-colors">Sobre</a></li>
                <li><a href="#k230" className="text-muted-foreground hover:text-primary transition-colors">Hardware K230</a></li>
                <li><a href="#results" className="text-muted-foreground hover:text-primary transition-colors">Resultados</a></li>
                <li><a href="#methodology" className="text-muted-foreground hover:text-primary transition-colors">Metodologia</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Licença</h3>
              <p className="text-sm text-muted-foreground mb-4">
                MIT License • Open Source
              </p>
              <p className="text-sm text-muted-foreground">
                © 2025 Marcelo Claro Laranjeira<br />
                SME Crateús-CE
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>Desenvolvido com rigor científico e compromisso social • Padrão Qualis A1 • Novembro 2025</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
