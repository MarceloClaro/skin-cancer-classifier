import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Play, Square, Download, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface TrainingConfig {
  learningRate: number;
  epochs: number;
  batchSize: number;
  augmentation: {
    rotation: boolean;
    zoom: boolean;
    flip: boolean;
    shift: boolean;
  };
}

interface TrainingStatus {
  isRunning: boolean;
  currentEpoch: number;
  totalEpochs: number;
  currentAccuracy: number;
  currentLoss: number;
  logs: string[];
}

export default function RetrainingInterface() {
  const [config, setConfig] = useState<TrainingConfig>({
    learningRate: 0.0001,
    epochs: 20,
    batchSize: 8,
    augmentation: {
      rotation: true,
      zoom: true,
      flip: true,
      shift: true,
    },
  });

  const [status, setStatus] = useState<TrainingStatus>({
    isRunning: false,
    currentEpoch: 0,
    totalEpochs: 0,
    currentAccuracy: 0,
    currentLoss: 0,
    logs: [],
  });

  const handleStartTraining = async () => {
    toast.info("Iniciando treinamento...");
    
    setStatus({
      isRunning: true,
      currentEpoch: 0,
      totalEpochs: config.epochs,
      currentAccuracy: 0,
      currentLoss: 0,
      logs: ["[INFO] Iniciando treinamento com configurações personalizadas..."],
    });

    // Simulação de treinamento (em produção, isso seria uma chamada tRPC)
    for (let epoch = 1; epoch <= config.epochs; epoch++) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      const accuracy = 50 + (epoch / config.epochs) * 40 + Math.random() * 5;
      const loss = 2 - (epoch / config.epochs) * 1.5 + Math.random() * 0.2;

      setStatus((prev) => ({
        ...prev,
        currentEpoch: epoch,
        currentAccuracy: accuracy,
        currentLoss: loss,
        logs: [
          ...prev.logs,
          `[EPOCH ${epoch}/${config.epochs}] Acurácia: ${accuracy.toFixed(2)}% | Loss: ${loss.toFixed(4)}`,
        ],
      }));
    }

    setStatus((prev) => ({
      ...prev,
      isRunning: false,
      logs: [...prev.logs, "[SUCCESS] Treinamento concluído com sucesso!"],
    }));

    toast.success("Treinamento concluído!");
  };

  const handleStopTraining = () => {
    setStatus((prev) => ({
      ...prev,
      isRunning: false,
      logs: [...prev.logs, "[WARNING] Treinamento cancelado pelo usuário"],
    }));
    toast.warning("Treinamento cancelado");
  };

  const progress = status.totalEpochs > 0 ? (status.currentEpoch / status.totalEpochs) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container py-12 max-w-7xl">
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              Interface de Retreinamento
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Configure e execute o retreinamento do modelo de classificação de câncer de pele
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Configuração */}
            <Card>
              <CardHeader>
                <CardTitle>Configuração de Hiperparâmetros</CardTitle>
                <CardDescription>
                  Ajuste os parâmetros de treinamento conforme necessário
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Learning Rate */}
                <div className="space-y-2">
                  <Label htmlFor="learning-rate">
                    Learning Rate: {config.learningRate.toExponential(1)}
                  </Label>
                  <Slider
                    id="learning-rate"
                    min={0.00001}
                    max={0.01}
                    step={0.00001}
                    value={[config.learningRate]}
                    onValueChange={([value]) =>
                      setConfig({ ...config, learningRate: value })
                    }
                    disabled={status.isRunning}
                  />
                </div>

                {/* Epochs */}
                <div className="space-y-2">
                  <Label htmlFor="epochs">Épocas: {config.epochs}</Label>
                  <Slider
                    id="epochs"
                    min={5}
                    max={100}
                    step={5}
                    value={[config.epochs]}
                    onValueChange={([value]) => setConfig({ ...config, epochs: value })}
                    disabled={status.isRunning}
                  />
                </div>

                {/* Batch Size */}
                <div className="space-y-2">
                  <Label htmlFor="batch-size">Batch Size: {config.batchSize}</Label>
                  <Slider
                    id="batch-size"
                    min={4}
                    max={32}
                    step={4}
                    value={[config.batchSize]}
                    onValueChange={([value]) => setConfig({ ...config, batchSize: value })}
                    disabled={status.isRunning}
                  />
                </div>

                {/* Data Augmentation */}
                <div className="space-y-4">
                  <Label>Data Augmentation</Label>
                  <div className="space-y-3">
                    {Object.entries(config.augmentation).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <Label htmlFor={key} className="capitalize">
                          {key}
                        </Label>
                        <Switch
                          id={key}
                          checked={value}
                          onCheckedChange={(checked) =>
                            setConfig({
                              ...config,
                              augmentation: { ...config.augmentation, [key]: checked },
                            })
                          }
                          disabled={status.isRunning}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Botões de Controle */}
                <div className="flex gap-4 pt-4">
                  {!status.isRunning ? (
                    <Button onClick={handleStartTraining} className="flex-1">
                      <Play className="h-4 w-4 mr-2" />
                      Iniciar Treinamento
                    </Button>
                  ) : (
                    <Button
                      onClick={handleStopTraining}
                      variant="destructive"
                      className="flex-1"
                    >
                      <Square className="h-4 w-4 mr-2" />
                      Cancelar Treinamento
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Status e Logs */}
            <div className="space-y-6">
              {/* Status Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Status do Treinamento</CardTitle>
                  <CardDescription>
                    Acompanhe o progresso em tempo real
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {status.isRunning ? (
                    <>
                      <Alert>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <AlertTitle>Treinamento em andamento</AlertTitle>
                        <AlertDescription>
                          Época {status.currentEpoch} de {status.totalEpochs}
                        </AlertDescription>
                      </Alert>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Progresso</span>
                          <span>{progress.toFixed(0)}%</span>
                        </div>
                        <Progress value={progress} />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">Acurácia Atual</p>
                          <p className="text-2xl font-bold">
                            {status.currentAccuracy.toFixed(2)}%
                          </p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-sm text-muted-foreground">Loss Atual</p>
                          <p className="text-2xl font-bold">
                            {status.currentLoss.toFixed(4)}
                          </p>
                        </div>
                      </div>
                    </>
                  ) : status.currentEpoch > 0 ? (
                    <Alert>
                      <CheckCircle2 className="h-4 w-4" />
                      <AlertTitle>Treinamento concluído</AlertTitle>
                      <AlertDescription>
                        Acurácia final: {status.currentAccuracy.toFixed(2)}%
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Aguardando início</AlertTitle>
                      <AlertDescription>
                        Configure os hiperparâmetros e clique em "Iniciar Treinamento"
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>

              {/* Logs Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Logs de Treinamento</CardTitle>
                  <CardDescription>Saída em tempo real do processo</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                    {status.logs.length > 0 ? (
                      status.logs.map((log, index) => (
                        <div key={index} className="py-1">
                          {log}
                        </div>
                      ))
                    ) : (
                      <p className="text-muted-foreground">Nenhum log disponível</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
