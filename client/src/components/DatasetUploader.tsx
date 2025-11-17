import { useState, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Upload, FileArchive, Image as ImageIcon, Loader2, 
  CheckCircle2, AlertCircle, Info 
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";

interface DatasetUploaderProps {
  onSuccess?: () => void;
}

export default function DatasetUploader({ onSuccess }: DatasetUploaderProps) {
  const [uploadMode, setUploadMode] = useState<"zip" | "images">("images");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedClass, setSelectedClass] = useState<"BENIGNO" | "MALIGNO">("MALIGNO");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadMutation = trpc.dataset.uploadImages.useMutation({
    onSuccess: (data) => {
      if (data.success) {
        toast.success(`✅ ${data.uploaded} imagens enviadas com sucesso!`, {
          description: data.errors.length > 0 
            ? `${data.errors.length} imagens com erro` 
            : "Todas as imagens foram processadas",
        });
        onSuccess?.();
        setSelectedFiles([]);
        setUploadProgress(0);
      } else {
        toast.error("Erro no upload", {
          description: data.error || "Erro desconhecido",
        });
      }
      setIsUploading(false);
    },
    onError: (error) => {
      toast.error("Erro no upload", {
        description: error.message,
      });
      setIsUploading(false);
      setUploadProgress(0);
    },
  });

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    // Filtrar apenas imagens
    const imageFiles = files.filter(file => 
      file.type.startsWith('image/') && 
      (file.type.includes('png') || file.type.includes('jpeg') || file.type.includes('jpg'))
    );
    
    if (imageFiles.length < files.length) {
      toast.warning("Alguns arquivos foram ignorados", {
        description: "Apenas imagens PNG e JPG são aceitas",
      });
    }
    
    setSelectedFiles(imageFiles);
  }, []);

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error("Nenhuma imagem selecionada");
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Converter imagens para base64
      const images = await Promise.all(
        selectedFiles.map(async (file, index) => {
          const reader = new FileReader();
          
          return new Promise<{ data: string; class: "BENIGNO" | "MALIGNO"; filename: string }>((resolve, reject) => {
            reader.onload = () => {
              setUploadProgress(((index + 1) / selectedFiles.length) * 50); // 0-50%
              resolve({
                data: reader.result as string,
                class: selectedClass,
                filename: file.name,
              });
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
          });
        })
      );

      setUploadProgress(60); // 60%

      // Enviar para o servidor
      uploadMutation.mutate({ images });
      
      setUploadProgress(100); // 100%

    } catch (error: any) {
      toast.error("Erro ao processar imagens", {
        description: error.message,
      });
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Upload de Dataset
        </CardTitle>
        <CardDescription>
          Envie imagens individuais ou um arquivo ZIP organizado por classes
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={uploadMode} onValueChange={(v) => setUploadMode(v as "zip" | "images")}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="images">
              <ImageIcon className="w-4 h-4 mr-2" />
              Múltiplas Imagens
            </TabsTrigger>
            <TabsTrigger value="zip" disabled>
              <FileArchive className="w-4 h-4 mr-2" />
              Arquivo ZIP (em breve)
            </TabsTrigger>
          </TabsList>

          <TabsContent value="images" className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Selecione múltiplas imagens e escolha a classe (BENIGNO ou MALIGNO).
                Formatos aceitos: PNG, JPG, JPEG
              </AlertDescription>
            </Alert>

            {/* Seleção de Classe */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Classe das Imagens:</label>
              <div className="flex gap-2">
                <Button
                  variant={selectedClass === "BENIGNO" ? "default" : "outline"}
                  onClick={() => setSelectedClass("BENIGNO")}
                  disabled={isUploading}
                  className="flex-1"
                >
                  BENIGNO
                </Button>
                <Button
                  variant={selectedClass === "MALIGNO" ? "default" : "outline"}
                  onClick={() => setSelectedClass("MALIGNO")}
                  disabled={isUploading}
                  className="flex-1"
                >
                  MALIGNO
                </Button>
              </div>
            </div>

            {/* Seleção de Arquivos */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Selecionar Imagens:</label>
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                multiple
                onChange={handleFileSelect}
                disabled={isUploading}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-primary file:text-primary-foreground
                  hover:file:bg-primary/90
                  disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Lista de Arquivos Selecionados */}
            {selectedFiles.length > 0 && (
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Arquivos Selecionados ({selectedFiles.length}):
                </label>
                <div className="max-h-48 overflow-y-auto border rounded-md p-2 space-y-1">
                  {selectedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-muted rounded-md text-sm"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <ImageIcon className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{file.name}</span>
                        <span className="text-muted-foreground text-xs flex-shrink-0">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      {!isUploading && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveFile(index)}
                          className="flex-shrink-0"
                        >
                          ✕
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Progresso */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Enviando...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} />
              </div>
            )}

            {/* Botão de Upload */}
            <Button
              onClick={handleUpload}
              disabled={selectedFiles.length === 0 || isUploading}
              className="w-full"
              size="lg"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Enviando {selectedFiles.length} imagens...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Enviar {selectedFiles.length} imagens como {selectedClass}
                </>
              )}
            </Button>
          </TabsContent>

          <TabsContent value="zip">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Upload de arquivo ZIP estará disponível em breve.
                O ZIP deve conter pastas BENIGNO e MALIGNO com as respectivas imagens.
              </AlertDescription>
            </Alert>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
