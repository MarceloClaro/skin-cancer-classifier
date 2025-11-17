import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Image as ImageIcon, Trash2, Loader2, Filter, 
  ChevronLeft, ChevronRight 
} from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";

interface DatasetGalleryProps {
  onRefresh?: () => void;
}

export default function DatasetGallery({ onRefresh }: DatasetGalleryProps) {
  const [classFilter, setClassFilter] = useState<"all" | "BENIGNO" | "MALIGNO">("all");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  // Query para listar imagens
  const { data, isLoading, refetch } = trpc.dataset.listImages.useQuery({
    classFilter,
    page: currentPage,
    pageSize,
  }, {
    refetchInterval: 10000, // Atualizar a cada 10 segundos
  });

  // Mutation para deletar imagem
  const deleteMutation = trpc.dataset.deleteImage.useMutation({
    onSuccess: (result) => {
      if (result.success) {
        toast.success("Imagem removida com sucesso");
        refetch();
        onRefresh?.();
      } else {
        toast.error("Erro ao remover imagem", {
          description: result.error,
        });
      }
    },
    onError: (error) => {
      toast.error("Erro ao remover imagem", {
        description: error.message,
      });
    },
  });

  const handleDelete = (filename: string, className: "BENIGNO" | "MALIGNO") => {
    if (confirm(`Tem certeza que deseja remover a imagem ${filename}?`)) {
      deleteMutation.mutate({
        filename,
        class: className,
      });
    }
  };

  const handleFilterChange = (value: string) => {
    setClassFilter(value as "all" | "BENIGNO" | "MALIGNO");
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  const images = data?.images || [];
  const totalPages = data?.totalPages || 1;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="w-5 h-5" />
              Galeria do Dataset
            </CardTitle>
            <CardDescription>
              {data?.total || 0} imagens no total
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <Select value={classFilter} onValueChange={handleFilterChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtrar por classe" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas as Classes</SelectItem>
                <SelectItem value="BENIGNO">BENIGNO</SelectItem>
                <SelectItem value="MALIGNO">MALIGNO</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {images.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <ImageIcon className="w-16 h-16 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              Nenhuma imagem encontrada
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Faça upload de imagens para começar
            </p>
          </div>
        ) : (
          <>
            {/* Grid de Imagens */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
              {images.map((image: any, index: number) => (
                <div
                  key={index}
                  className="relative group border rounded-lg overflow-hidden bg-muted"
                >
                  {/* Badge de Classe */}
                  <Badge
                    variant={image.class === "BENIGNO" ? "default" : "destructive"}
                    className="absolute top-2 left-2 z-10"
                  >
                    {image.class}
                  </Badge>

                  {/* Botão de Deletar */}
                  <Button
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleDelete(image.filename, image.class)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>

                  {/* Placeholder de Imagem */}
                  <div className="aspect-square bg-gradient-to-br from-muted to-muted-foreground/10 flex items-center justify-center">
                    <ImageIcon className="w-12 h-12 text-muted-foreground/50" />
                  </div>

                  {/* Info */}
                  <div className="p-2 bg-background">
                    <p className="text-xs truncate font-mono" title={image.filename}>
                      {image.filename}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(image.created).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Paginação */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Página {currentPage} de {totalPages}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Anterior
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                  >
                    Próxima
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
