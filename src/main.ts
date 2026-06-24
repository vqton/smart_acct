import { resolve } from "node:path";
import "reflect-metadata";
import "dotenv/config";
import express from "express";
import type { Request, Response, NextFunction } from "express";
import { NestFactory } from "@nestjs/core";
import type { NestExpressApplication } from "@nestjs/platform-express";
import { AppModule } from "./app.module.js";
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";
import { ValidationPipe } from "@nestjs/common";

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  app.enableCors();
  app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true }));

  const frontendDir = process.env.FRONTEND_DIR;
  if (frontendDir) {
    app.use(express.static(resolve(frontendDir)));
    app.use((req: Request, res: Response, next: NextFunction) => {
      if (req.method === "GET" && !req.path.startsWith("/api")) {
        res.sendFile(resolve(frontendDir, "index.html"));
      } else {
        next();
      }
    });
  }

  const config = new DocumentBuilder()
    .setTitle("smart_acct API")
    .setDescription("Vietnamese accounting system — TT 99/2025/TT-BTC compliant")
    .setVersion("0.2.0")
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup("api/docs", app, document);

  const port = parseInt(process.env.PORT ?? "8080", 10);
  await app.listen(port);
  console.log(`smart_acct running on http://127.0.0.1:${port}`);
  console.log(`Swagger docs at http://127.0.0.1:${port}/api/docs`);
}

bootstrap().catch(console.error);
