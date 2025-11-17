import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import path from "path";
import fs from "fs";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  // OAuth callback under /api/oauth/callback
  registerOAuthRoutes(app);
  
  // Model download endpoint
  app.get('/api/download/model/:type', (req, res) => {
    const { type } = req.params;
    
    let filePath: string;
    let filename: string;
    
    try {
      const baseDir = '/home/ubuntu/skin_cancer_classifier_k230_page';
      
      if (type === 'quantized') {
        filePath = path.join(baseDir, 'models', 'tflite', 'skin_cancer_k230_quantized.tflite');
        filename = 'skin_cancer_k230_quantized.tflite';
      } else if (type === 'full') {
        filePath = path.join(baseDir, 'models', 'tflite', 'skin_cancer_k230.tflite');
        filename = 'skin_cancer_k230.tflite';
      } else if (type === 'documentation') {
        filePath = path.join(baseDir, 'models', 'tflite', 'README.md');
        filename = 'K230_Model_Documentation.md';
      } else {
        return res.status(400).json({ error: 'Invalid model type' });
      }
      
      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'File not found' });
      }
      
      res.download(filePath, filename, (err) => {
        if (err) {
          console.error('[DOWNLOAD] Error:', err);
          if (!res.headersSent) {
            res.status(500).json({ error: 'Download failed' });
          }
        }
      });
    } catch (error) {
      console.error('[DOWNLOAD] Error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });
  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
