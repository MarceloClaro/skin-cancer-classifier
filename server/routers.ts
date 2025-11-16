import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";
import { createContact, saveChatConversation, getChatHistory } from "./db";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Contact form router
  contact: router({
    submit: publicProcedure
      .input(z.object({
        name: z.string().min(1),
        email: z.string().email(),
        institution: z.string().optional(),
        interestType: z.enum(["pesquisador", "investidor", "instituicao", "outro"]),
        message: z.string().min(10),
      }))
      .mutation(async ({ input }) => {
        await createContact(input);
        return { success: true };
      }),
  }),

  // Chat bot router
  chat: router({
    sendMessage: publicProcedure
      .input(z.object({
        message: z.string(),
        sessionId: z.string(),
      }))
      .mutation(async ({ input }) => {
        const GEMINI_API_KEY_PRIMARY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs"; // Chave funcional
        const GEMINI_API_KEY_FALLBACK = "AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0";
        const GEMINI_MODEL = "models/gemini-2.5-flash"; // Modelo estável e rápido (prefixo obrigatório)
        const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/${GEMINI_MODEL}:generateContent`;

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

Responda de forma técnica, didática e motivadora para pesquisadores e investidores.`;

        try {
          console.log("[CHAT] Recebida mensagem:", input.message);
          console.log("[CHAT] Session ID:", input.sessionId);
          console.log("[CHAT] Tentando API Gemini com chave primária...");
          
          // Tentar com chave primária
          let response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY_PRIMARY}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              contents: [
                {
                  parts: [
                    {
                      text: `${PROJECT_CONTEXT}\n\nPergunta do usuário: ${input.message}`
                    }
                  ]
                }
              ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 2048, // Aumentado para evitar MAX_TOKENS
            topP: 0.95,
            topK: 40,
          }
            })
          });

          console.log("[CHAT] Resposta primária - Status:", response.status, response.statusText);
          
          // Se falhar, tentar com chave fallback
          if (!response.ok) {
            console.log("[CHAT] Chave primária falhou, tentando fallback...");
            response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY_FALLBACK}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                contents: [
                  {
                    parts: [
                      {
                        text: `${PROJECT_CONTEXT}\n\nPergunta do usuário: ${input.message}`
                      }
                    ]
                  }
                ],
                generationConfig: {
                  temperature: 0.7,
                  maxOutputTokens: 2048,
                  topP: 0.95,
                  topK: 40,
                }
              })
            });
          }

          if (!response.ok) {
            const errorText = await response.text();
            console.error("[CHAT] Erro na API Gemini:", response.status, errorText);
            throw new Error(`Erro ao comunicar com a API Gemini: ${response.status}`);
          }

          const data = await response.json();
          console.log("[CHAT] Resposta da API:", JSON.stringify(data, null, 2));
          
          // Verificar estrutura da resposta
          if (!data.candidates || !data.candidates[0]) {
            console.error("[CHAT] Formato de resposta inválido (sem candidates):", data);
            throw new Error("Formato de resposta inválido da API Gemini");
          }

          const candidate = data.candidates[0];
          
          // Verificar se há conteúdo na resposta
          if (!candidate.content || !candidate.content.parts || !candidate.content.parts[0]) {
            console.error("[CHAT] Resposta sem conteúdo (finishReason:", candidate.finishReason, ")");
            
            // Se atingiu MAX_TOKENS, retornar mensagem informativa
            if (candidate.finishReason === "MAX_TOKENS") {
              throw new Error("A resposta foi muito longa. Por favor, faça uma pergunta mais específica.");
            }
            
            throw new Error("A API não retornou conteúdo. Tente novamente.");
          }
          
          const botResponse = candidate.content.parts[0].text;
          console.log("[CHAT] Resposta do bot:", botResponse);

          // Salvar conversa no banco de dados
          await saveChatConversation({
            sessionId: input.sessionId,
            userMessage: input.message,
            botResponse,
          });

          return { response: botResponse };
        } catch (error: any) {
          console.error("[CHAT] ERRO COMPLETO:", error);
          console.error("[CHAT] Stack trace:", error.stack);
          throw new Error(`Erro ao processar sua mensagem: ${error.message}`);
        }
      }),
    saveConversation: publicProcedure
      .input(z.object({
        sessionId: z.string(),
        userMessage: z.string(),
        botResponse: z.string(),
      }))
      .mutation(async ({ input }) => {
        await saveChatConversation(input);
        return { success: true };
      }),
    getHistory: publicProcedure
      .input(z.object({
        sessionId: z.string(),
      }))
      .query(async ({ input }) => {
        return await getChatHistory(input.sessionId);
      }),
  }),
});

export type AppRouter = typeof appRouter;
