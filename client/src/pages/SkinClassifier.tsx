import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Upload, Image as ImageIcon, AlertCircle, CheckCircle2, Brain, Activity } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";
import { Streamdown } from "streamdown";

export default function SkinClassifier() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const classifyMutation = trpc.skinClassifier.classify.useMutation({
    onSuccess: (data) => {
      setResult(data);
      setIsAnalyzing(false);
      toast.success("Análise concluída com sucesso!");
    },
    onError: (error) => {
      setIsAnalyzing(false);
      toast.error(`Erro na análise: ${error.message}`);
    },
  });

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
      await classifyMutation.mutateAsync({
        imageBase64: selectedImage,
        generateDiagnosis: true,
      });
    } catch (error) {
      // Erro já tratado no onError
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
                        {result.classification.class_name}
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
                              width: `${result.classification.confidence * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-lg font-bold text-green-900">
                          {(result.classification.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm text-green-800 font-medium mb-2">
                        Probabilidades de Todas as Classes
                      </p>
                      <div className="space-y-2">
                        {Object.entries(result.classification.probabilities)
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
                        Gerado automaticamente pela API Gemini
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-sm max-w-none">
                        <Streamdown>
                          {result.diagnosis.diagnosis}
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
