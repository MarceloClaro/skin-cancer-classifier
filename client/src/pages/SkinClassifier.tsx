import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Upload, Image as ImageIcon, AlertCircle, CheckCircle2, Brain, Activity } from "lucide-react";
// import { trpc } from "@/lib/trpc"; // Removido: usando API HTTP direta
import { toast } from "sonner";
import { Streamdown } from "streamdown";

export default function SkinClassifier() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Função para chamar API HTTP diretamente
  const classifyImage = async (imageBase64: string, generateDiagnosis: boolean) => {
    // URL da API (usar variável de ambiente ou localhost para dev)
    const API_URL = import.meta.env.VITE_CLASSIFIER_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${API_URL}/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        imageBase64,
        generateDiagnosis,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro na classificação');
    }
    
    return response.json();
  };

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo de arquivo
    if (!file.type.startsWith("image/")) {
      toast.error("Por favor, selecione uma imagem válida");
      return;
    }

    // Validar tamanho (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Imagem muito grande. Máximo: 10MB");
      return;
    }

    // Ler imagem e converter para base64
    const reader = new FileReader();
    reader.onload = (e) => {
      const base64 = e.target?.result as string;
      setSelectedImage(base64);
      setResult(null); // Limpar resultado anterior
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      toast.error("Por favor, selecione uma imagem primeiro");
      return;
    }

    setIsAnalyzing(true);
    try {
      const data = await classifyImage(selectedImage, true);
      setResult(data);
      setIsAnalyzing(false);
      toast.success("Análise concluída com sucesso!");
    } catch (error: any) {
      setIsAnalyzing(false);
      toast.error(`Erro na análise: ${error.message}`);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container py-8">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">
              Classificador de Câncer de Pele
            </h1>
          </div>
          <p className="text-gray-600">
            Sistema de análise automatizada com Deep Learning e Grad-CAM para estudo em dermatologia
          </p>
        </div>
      </div>

      <div className="container py-12">
        {/* Badge do Modelo Treinado */}
        <div className="flex flex-wrap justify-center gap-3 mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Modelo Treinado Customizado (BENIGNO vs MALIGNO)
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            <Activity className="h-4 w-4" />
            Análise Multimodal: CNN + Vision API
          </div>
        </div>
        {/* Aviso Importante */}
        <Alert className="mb-8 border-amber-200 bg-amber-50">
          <AlertCircle className="h-5 w-5 text-amber-600" />
          <AlertDescription className="text-amber-900">
            <strong>Importante:</strong> Este sistema é uma ferramenta educacional para residentes em dermatologia.
            NÃO substitui avaliação clínica por profissional qualificado.
          </AlertDescription>
        </Alert>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Coluna Esquerda: Upload e Visualização */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="h-5 w-5" />
                  Upload de Imagem Dermatoscópica
                </CardTitle>
                <CardDescription>
                  Selecione uma imagem de lesão de pele para análise
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Área de Upload */}
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  {selectedImage ? (
                    <div className="space-y-4">
                      <img
                        src={selectedImage}
                        alt="Imagem selecionada"
                        className="max-h-64 mx-auto rounded-lg shadow-md"
                      />
                      <Button variant="outline" size="sm" onClick={handleReset}>
                        Selecionar outra imagem
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Upload className="h-12 w-12 mx-auto text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-700">
                          Clique para selecionar uma imagem
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          PNG, JPG ou JPEG (máx. 10MB)
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                />

                {/* Botão de Análise */}
                <Button
                  onClick={handleAnalyze}
                  disabled={!selectedImage || isAnalyzing}
                  className="w-full"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Analisando...
                    </>
                  ) : (
                    <>
                      <Activity className="mr-2 h-5 w-5" />
                      Analisar Lesão
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Grad-CAM */}
            {result?.gradcam && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-purple-600" />
                    Mapa de Ativação (Grad-CAM)
                  </CardTitle>
                  <CardDescription>
                    Visualização das regiões mais relevantes para a classificação
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <img
                    src={result.gradcam}
                    alt="Grad-CAM"
                    className="w-full rounded-lg shadow-md"
                  />
                  <p className="text-xs text-gray-500 mt-3">
                    As áreas em vermelho/amarelo indicam as regiões que mais influenciaram a decisão do modelo
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Coluna Direita: Resultados */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Resultado da Classificação */}
                <Card className="border-green-200 bg-green-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-900">
                      <CheckCircle2 className="h-5 w-5" />
                      Resultado da Classificação
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-green-800 font-medium mb-1">
                        Diagnóstico Principal
                      </p>
                      <p className="text-2xl font-bold text-green-900">
                        {result.class_name || result.classification?.class_name}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-green-800 font-medium mb-2">
                        Confiança
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-white rounded-full h-3 overflow-hidden">
                          <div
                            className="bg-green-600 h-full transition-all duration-500"
                            style={{
                              width: `${(result.confidence || result.classification?.confidence) * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-lg font-bold text-green-900">
                          {((result.confidence || result.classification?.confidence) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    {(result.probabilities || result.classification?.probabilities) && (
                      <div>
                        <p className="text-sm text-green-800 font-medium mb-2">
                          Probabilidades de Todas as Classes
                        </p>
                        <div className="space-y-2">
                          {Object.entries(result.probabilities || result.classification?.probabilities || {})
                            .sort(([, a]: any, [, b]: any) => b - a)
                            .map(([cls, prob]: any) => (
                              <div key={cls} className="flex items-center gap-2 text-sm">
                                <div className="flex-1 bg-white rounded-full h-2 overflow-hidden">
                                  <div
                                    className="bg-blue-500 h-full"
                                    style={{ width: `${prob * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-700 w-32 truncate">
                                  {cls}
                                </span>
                                <span className="text-xs font-medium text-gray-900 w-12 text-right">
                                  {(prob * 100).toFixed(1)}%
                                </span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Diagnóstico Detalhado */}
                {result.diagnosis && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5 text-blue-600" />
                        Relatório Diagnóstico
                      </CardTitle>
                      <CardDescription>
                        Gerado automaticamente por {result.diagnosis.provider === 'groq' ? 'Groq Vision (Llama 4 Scout)' : result.diagnosis.provider === 'gemini' ? 'Gemini Vision' : 'CNN'}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-sm max-w-none">
                        <Streamdown>
                          {result.diagnosis.analysis || result.diagnosis.diagnosis || 'Relatório não disponível'}
                        </Streamdown>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card className="border-dashed">
                <CardContent className="py-12 text-center">
                  <Brain className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500">
                    Selecione uma imagem e clique em "Analisar Lesão" para ver os resultados
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Download do Modelo TFLite */}
        <Card className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-600" />
              Modelo TFLite para K230
            </CardTitle>
            <CardDescription>
              Baixe o modelo otimizado para executar no hardware K230
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-gray-700">
                O modelo foi exportado para <strong>TensorFlow Lite</strong> com quantização INT8, 
                reduzindo o tamanho em 70% e acelerando a inferência em dispositivos embarcados.
              </p>
              
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg border border-blue-200">
                  <p className="font-semibold text-blue-600 mb-2">Modelo Quantizado (Recomendado)</p>
                  <p className="text-xs text-gray-600 mb-3">2.74 MB • INT8 • Otimizado para K230</p>
                  <Button 
                    variant="default" 
                    className="w-full"
                    onClick={() => {
                      // Download via tRPC
                      fetch('/api/trpc/model.download?input=' + encodeURIComponent(JSON.stringify({type: 'quantized'})))
                        .then(res => res.json())
                        .then(data => {
                          const result = data.result.data;
                          const blob = new Blob([Uint8Array.from(atob(result.data), c => c.charCodeAt(0))], { type: 'application/octet-stream' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = result.filename;
                          a.click();
                          URL.revokeObjectURL(url);
                          toast.success('Download iniciado!');
                        })
                        .catch(err => toast.error('Erro ao fazer download'));
                    }}
                  >
                    Baixar Modelo Quantizado
                  </Button>
                </div>
                
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold text-gray-700 mb-2">Documentação</p>
                  <p className="text-xs text-gray-600 mb-3">Guia de uso e exemplos de código</p>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => {
                      fetch('/api/trpc/model.download?input=' + encodeURIComponent(JSON.stringify({type: 'documentation'})))
                        .then(res => res.json())
                        .then(data => {
                          const result = data.result.data;
                          const blob = new Blob([atob(result.data)], { type: 'text/markdown' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = result.filename;
                          a.click();
                          URL.revokeObjectURL(url);
                          toast.success('Download iniciado!');
                        })
                        .catch(err => toast.error('Erro ao fazer download'));
                    }}
                  >
                    Baixar Documentação
                  </Button>
                </div>
              </div>
              
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  <strong>Nota:</strong> O modelo TFLite requer TensorFlow Lite runtime no K230. 
                  Consulte a documentação para instruções de integração.
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>

        {/* Informações Técnicas */}
        <Card className="mt-8 bg-gray-50">
          <CardHeader>
            <CardTitle>Sobre o Sistema</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none">
            <p>
              Este sistema utiliza <strong>MobileNetV2</strong> pré-treinado com transfer learning para classificar
              lesões de pele em 7 categorias do dataset HAM10000. A técnica <strong>Grad-CAM</strong> (Gradient-weighted
              Class Activation Mapping) é aplicada para visualizar as regiões da imagem que mais influenciam a decisão
              do modelo, proporcionando interpretabilidade clínica.
            </p>
            <p>
              O diagnóstico detalhado é gerado pela <strong>API Gemini</strong> (Google), que analisa as probabilidades
              e fornece informações educacionais para residentes em dermatologia, incluindo características clínicas,
              diagnósticos diferenciais e recomendações de conduta.
            </p>
            <div className="grid sm:grid-cols-3 gap-4 mt-4">
              <div className="bg-white p-4 rounded-lg">
                <p className="font-semibold text-blue-600">Modelo</p>
                <p className="text-sm text-gray-600">MobileNetV2</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <p className="font-semibold text-purple-600">Interpretabilidade</p>
                <p className="text-sm text-gray-600">Grad-CAM</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <p className="font-semibold text-green-600">IA Generativa</p>
                <p className="text-sm text-gray-600">Gemini 2.5 Flash</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
