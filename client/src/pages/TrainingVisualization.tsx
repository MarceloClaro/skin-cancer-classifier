import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, ZoomIn, TrendingUp, BarChart3, Activity } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface TrainingReport {
  id: string;
  timestamp: string;
  accuracy: number;
  auc: number;
  visualizations: {
    augmentation: string;
    hyperparameters: string;
    trainingCurves: string;
    confusionMatrix: string;
    rocCurve: string;
    bestPredictions: string;
    worstPredictions: string;
  };
}

// Mock data - em produção, isso viria de uma API
const mockReport: TrainingReport = {
  id: "training_report_20251116_140724",
  timestamp: "2025-11-16 14:07:24",
  accuracy: 87.5,
  auc: 0.88,
  visualizations: {
    augmentation: "/api/training-viz/augmentation_examples.png",
    hyperparameters: "/api/training-viz/hyperparameters_table.png",
    trainingCurves: "/api/training-viz/training_curves.png",
    confusionMatrix: "/api/training-viz/confusion_matrix.png",
    rocCurve: "/api/training-viz/roc_curve.png",
    bestPredictions: "/api/training-viz/predictions/best_predictions.png",
    worstPredictions: "/api/training-viz/predictions/worst_predictions.png",
  },
};

export default function TrainingVisualization() {
  const [selectedImage, setSelectedImage] = useState<{ url: string; title: string } | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  const visualizationCards = [
    {
      title: "Data Augmentation",
      description: "Exemplos de transformações aplicadas às imagens",
      icon: <Activity className="h-5 w-5" />,
      image: mockReport.visualizations.augmentation,
      size: "1.8 MB",
    },
    {
      title: "Hiperparâmetros",
      description: "Configuração completa do treinamento",
      icon: <BarChart3 className="h-5 w-5" />,
      image: mockReport.visualizations.hyperparameters,
      size: "129 KB",
    },
    {
      title: "Curvas de Treinamento",
      description: "Evolução de acurácia e loss por época",
      icon: <TrendingUp className="h-5 w-5" />,
      image: mockReport.visualizations.trainingCurves,
      size: "121 KB",
    },
    {
      title: "Matriz de Confusão",
      description: "Análise de predições corretas e incorretas",
      icon: <BarChart3 className="h-5 w-5" />,
      image: mockReport.visualizations.confusionMatrix,
      size: "36 KB",
    },
    {
      title: "Curva ROC",
      description: `AUC = ${mockReport.auc.toFixed(2)}`,
      icon: <TrendingUp className="h-5 w-5" />,
      image: mockReport.visualizations.rocCurve,
      size: "63 KB",
    },
    {
      title: "Melhores Predições",
      description: "Imagens classificadas corretamente com alta confiança",
      icon: <Activity className="h-5 w-5" />,
      image: mockReport.visualizations.bestPredictions,
      size: "1.8 MB",
    },
    {
      title: "Piores Predições",
      description: "Imagens classificadas incorretamente",
      icon: <Activity className="h-5 w-5" />,
      image: mockReport.visualizations.worstPredictions,
      size: "275 KB",
    },
  ];

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <div className="container py-12">
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">
            Visualização de Treinamento
          </h1>
          <p className="text-xl text-muted-foreground">
            Análise completa do processo de treinamento do modelo de classificação de câncer de pele
          </p>
        </div>

        {/* Métricas Resumidas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Acurácia
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{mockReport.accuracy}%</div>
              <p className="text-xs text-muted-foreground mt-1">
                Dataset de validação
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                AUC-ROC
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{mockReport.auc.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Área sob a curva ROC
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Data do Treinamento
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold">{mockReport.timestamp}</div>
              <p className="text-xs text-muted-foreground mt-1">
                ID: {mockReport.id}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Grid de Visualizações */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          {visualizationCards.map((viz, index) => (
            <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {viz.icon}
                    <CardTitle className="text-lg">{viz.title}</CardTitle>
                  </div>
                  <span className="text-xs text-muted-foreground">{viz.size}</span>
                </div>
                <CardDescription>{viz.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Preview da Imagem */}
                <div
                  className="relative aspect-video bg-muted rounded-lg overflow-hidden cursor-pointer group"
                  onClick={() => setSelectedImage({ url: viz.image, title: viz.title })}
                >
                  <img
                    src={viz.image}
                    alt={viz.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <ZoomIn className="h-8 w-8 text-white" />
                  </div>
                </div>

                {/* Botão de Download */}
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => handleDownload(viz.image, `${viz.title.replace(/\s+/g, "_")}.png`)}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Modal de Zoom */}
      <Dialog open={selectedImage !== null} onOpenChange={() => setSelectedImage(null)}>
        <DialogContent className="max-w-7xl max-h-[90vh] overflow-auto">
          <DialogHeader>
            <DialogTitle>{selectedImage?.title}</DialogTitle>
            <DialogDescription>
              Clique fora da imagem para fechar
            </DialogDescription>
          </DialogHeader>
          {selectedImage && (
            <div className="relative">
              <img
                src={selectedImage.url}
                alt={selectedImage.title}
                className="w-full h-auto rounded-lg"
              />
              <Button
                variant="secondary"
                size="sm"
                className="absolute top-4 right-4"
                onClick={() =>
                  handleDownload(
                    selectedImage.url,
                    `${selectedImage.title.replace(/\s+/g, "_")}.png`
                  )
                }
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
