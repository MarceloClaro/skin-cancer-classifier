import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Mail, Send, User, Building } from "lucide-react";
import { trpc } from "@/lib/trpc";

export default function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    institution: "",
    role: "",
    interest: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitContactMutation = trpc.contact.submit.useMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await submitContactMutation.mutateAsync({
        name: formData.name,
        email: formData.email,
        institution: formData.institution || undefined,
        interestType: formData.interest as "pesquisador" | "investidor" | "instituicao" | "outro",
        message: formData.message,
      });

      toast.success("🎉 Mensagem enviada com sucesso!", {
        description: "Entraremos em contato em breve. Você também pode nos contatar diretamente em marceloclaro@gmail.com",
        duration: 5000,
      });

      setFormData({
        name: "",
        email: "",
        institution: "",
        role: "",
        interest: "",
        message: ""
      });
    } catch (error) {
      toast.error("❌ Erro ao enviar mensagem", {
        description: "Por favor, tente novamente ou entre em contato diretamente por email.",
        duration: 5000,
      });
      console.error("Erro ao enviar contato:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-2 mb-2">
          <Mail className="h-6 w-6 text-primary" />
          <CardTitle className="text-2xl">Entre em Contato</CardTitle>
        </div>
        <CardDescription>
          Interessado em colaborar, investir ou saber mais sobre o projeto? 
          Preencha o formulário abaixo e entraremos em contato.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Nome Completo *
                </div>
              </Label>
              <Input
                id="name"
                placeholder="Seu nome"
                value={formData.name}
                onChange={(e) => handleChange("name", e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email *
                </div>
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={formData.email}
                onChange={(e) => handleChange("email", e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="institution">
                <div className="flex items-center gap-2">
                  <Building className="h-4 w-4" />
                  Instituição/Empresa
                </div>
              </Label>
              <Input
                id="institution"
                placeholder="Nome da instituição"
                value={formData.institution}
                onChange={(e) => handleChange("institution", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Você é: *</Label>
              <Select value={formData.role} onValueChange={(value) => handleChange("role", value)} required>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma opção" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="researcher">Pesquisador/Acadêmico</SelectItem>
                  <SelectItem value="investor">Investidor</SelectItem>
                  <SelectItem value="healthcare">Profissional de Saúde</SelectItem>
                  <SelectItem value="student">Estudante</SelectItem>
                  <SelectItem value="industry">Indústria/Empresa</SelectItem>
                  <SelectItem value="other">Outro</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="interest">Interesse Principal *</Label>
            <Select value={formData.interest} onValueChange={(value) => handleChange("interest", value)} required>
              <SelectTrigger>
                <SelectValue placeholder="Selecione seu interesse" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="collaboration">Colaboração em Pesquisa</SelectItem>
                <SelectItem value="investment">Investimento/Financiamento</SelectItem>
                <SelectItem value="implementation">Implementação Clínica</SelectItem>
                <SelectItem value="technical">Detalhes Técnicos</SelectItem>
                <SelectItem value="partnership">Parceria Institucional</SelectItem>
                <SelectItem value="licensing">Licenciamento</SelectItem>
                <SelectItem value="other">Outro</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="message">Mensagem *</Label>
            <Textarea
              id="message"
              placeholder="Conte-nos mais sobre seu interesse no projeto..."
              value={formData.message}
              onChange={(e) => handleChange("message", e.target.value)}
              required
              rows={6}
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <Button type="submit" disabled={isSubmitting} className="flex-1 gap-2">
              {isSubmitting ? (
                <>Enviando...</>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Enviar Mensagem
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="flex-1 gap-2"
              asChild
            >
              <a href="mailto:marceloclaro@gmail.com">
                <Mail className="h-4 w-4" />
                Email Direto
              </a>
            </Button>
          </div>

          <p className="text-xs text-muted-foreground text-center">
            * Campos obrigatórios. Seus dados serão tratados com confidencialidade conforme a LGPD.
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
