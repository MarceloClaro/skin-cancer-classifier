import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const GEMINI_API_KEY = "AIzaSyDVc5QnyhxvwoY1gqniVZ2jNCzeOEf4Nnc";
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent";

const PROJECT_CONTEXT = `Você é um assistente técnico especializado no projeto "Classificador de Câncer de Pele K230". 
Suas respostas devem ser técnicas, precisas e baseadas nas seguintes informações do projeto:

**Sobre o Projeto:**
- Framework completo de classificação de câncer de pele com IA
- Otimizado para o processador K230 (6 TOPS)
- Padrão Qualis A1 de rigor científico
- 18 módulos Python (~5.000 linhas de código)
- 16 documentos técnicos completos

**Resultados Científicos:**
- Acurácia média: 89.09% (seed Fibonacci 144)
- Latência K230: <100ms (-23 a -38% vs baseline)
- Melhor seed: Fibonacci 144 (0.8909 ± 0.0267)
- Dataset: HAM10000 (10.015 imagens)

**Tecnologias:**
- Modelo: MobileNetV2 + Transfer Learning
- Detecção: YOLOv8-nano (320x320)
- Interpretabilidade: Grad-CAM++, Integrated Gradients, SHAP
- Otimização: QAT, PTQ avançado, calibração KL Divergence
- Quantização: INT8 completa
- Monitoramento: MLflow + TensorBoard

**Hardware K230:**
- Processador: 6 TOPS de potência
- Custo: ~R$ 500/dispositivo
- Consumo: 10x menor que GPUs
- Integração: OpenRouter AI (ChatGPT, Gemini, Llama, Claude)

**Validação Clínica:**
- Conformidade: FDA, ANVISA, CE
- Métricas: ROC, Precision-Recall, IC 95%
- Calibração de confiança: Temperature Scaling, ECE
- Salvamento automático em SD para auditoria

**Aplicação:**
- Instituição: SME Crateús-CE
- Uso: Triagem clínica para residência médica em dermatologia
- Impacto: Cobertura de +15.000 habitantes
- Autor: Marcelo Claro Laranjeira (marceloclaro@gmail.com)

**Módulos Principais:**
1. Preparação de dados (EDA, divisão estratificada)
2. Treinamento (MobileNetV2, data augmentation)
3. Avaliação (métricas clínicas completas)
4. Grad-CAM++ (mapas de calor)
5. Exportação TFLite
6. Compilação K230 (nncase)
7. Padronização de imagens (CLAHE)
8. Calibração de confiança
9. YOLO detecção
10. Validação cruzada 5-fold
11. Relatório científico Qualis A1
12. Knowledge Distillation + Pruning
13. Análise de atenção avançada
14. Sistema de monitoramento
15. Ensemble com seeds matemáticas
16. Salvamento padrão médico
17. Teste de seeds
18. Sistema de inferência K230

Responda de forma técnica, didática e motivadora para pesquisadores e investidores. 
Se a pergunta for sobre colaboração, direcione para o formulário de contato ou email: marceloclaro@gmail.com`;

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Olá! Sou o assistente técnico do projeto Classificador de Câncer de Pele K230. Como posso ajudá-lo a entender melhor nosso framework?"
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `${PROJECT_CONTEXT}\n\nPergunta do usuário: ${input}`
                }
              ]
            }
          ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 1024,
          }
        })
      });

      if (!response.ok) {
        throw new Error("Erro ao comunicar com a API");
      }

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.candidates[0].content.parts[0].text
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente ou entre em contato diretamente pelo email: marceloclaro@gmail.com"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <Card className="fixed bottom-6 right-6 w-96 h-[600px] shadow-2xl z-50 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
              <CardTitle className="text-lg">Assistente Técnico K230</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </CardContent>
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                placeholder="Digite sua pergunta..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Powered by Google Gemini AI
            </p>
          </div>
        </Card>
      )}
    </>
  );
}
