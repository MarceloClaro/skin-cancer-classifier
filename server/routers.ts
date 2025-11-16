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
