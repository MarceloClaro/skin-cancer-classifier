import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertTriangle, Trash2 } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { toast } from "sonner";

interface ResetDatasetModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export default function ResetDatasetModal({
  open,
  onOpenChange,
  onSuccess,
}: ResetDatasetModalProps) {
  const [confirmText, setConfirmText] = useState("");
  const [isResetting, setIsResetting] = useState(false);

  const resetMutation = trpc.dataset.resetAll.useMutation({
    onSuccess: (data) => {
      if (data.success) {
        toast.success("✅ Dataset limpo com sucesso!", {
          description: "Todo o dataset e modelos foram removidos.",
        });
        onSuccess?.();
        onOpenChange(false);
      } else {
        toast.error("Erro ao limpar dataset", {
          description: data.error || "Erro desconhecido",
        });
      }
      setIsResetting(false);
      setConfirmText("");
    },
    onError: (error) => {
      toast.error("Erro ao limpar dataset", {
        description: error.message,
      });
      setIsResetting(false);
      setConfirmText("");
    },
  });

  const handleReset = () => {
    if (confirmText !== "LIMPAR TUDO") {
      toast.error("Confirmação incorreta", {
        description: 'Digite "LIMPAR TUDO" para confirmar',
      });
      return;
    }

    setIsResetting(true);
    resetMutation.mutate();
  };

  const handleCancel = () => {
    setConfirmText("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="w-5 h-5" />
            Limpar Todo o Dataset
          </DialogTitle>
          <DialogDescription>
            Esta ação é irreversível e irá remover permanentemente:
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <ul className="list-disc list-inside space-y-1 text-sm mt-2">
                <li>Todas as imagens do dataset incremental (BENIGNO e MALIGNO)</li>
                <li>Todos os modelos treinados (skin_cancer_model.h5)</li>
                <li>Histórico de retreinamento</li>
                <li>Visualizações de treinamento (curvas, matrizes, etc.)</li>
                <li>Arquivos de status e estatísticas</li>
              </ul>
            </AlertDescription>
          </Alert>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              Digite <span className="font-bold text-destructive">LIMPAR TUDO</span> para confirmar:
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              placeholder="LIMPAR TUDO"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-destructive"
              disabled={isResetting}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isResetting}
          >
            Cancelar
          </Button>
          <Button
            variant="destructive"
            onClick={handleReset}
            disabled={isResetting || confirmText !== "LIMPAR TUDO"}
          >
            {isResetting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Limpando...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Limpar Tudo
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
