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
        const GEMINI_API_KEY_PRIMARY = "AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0";
        const GEMINI_API_KEY_FALLBACK = "AIzaSyDVc5QnyhxvwoY1gqniVZ2jNCzeOEf4Nnc";
        const GEMINI_MODEL = "gemini-pro";
        const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

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
                maxOutputTokens: 1024,
              }
            })
          });

          // Se falhar, tentar com chave fallback
          if (!response.ok) {
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
                  maxOutputTokens: 1024,
                }
              })
            });
          }

          if (!response.ok) {
            throw new Error("Erro ao comunicar com a API Gemini");
          }

          const data = await response.json();
          const botResponse = data.candidates[0].content.parts[0].text;

          // Salvar conversa no banco de dados
          await saveChatConversation({
            sessionId: input.sessionId,
            userMessage: input.message,
            botResponse,
          });

          return { response: botResponse };
        } catch (error) {
          console.error("Erro ao processar mensagem:", error);
          throw new Error("Erro ao processar sua mensagem. Por favor, tente novamente.");
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
