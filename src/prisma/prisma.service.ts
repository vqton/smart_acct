import { Injectable, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { PrismaClient } from "../generated/prisma/client.js";
import { PrismaMariaDb } from "@prisma/adapter-mariadb";

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor() {
    const adapter = new PrismaMariaDb({
      host: process.env.DB_HOST ?? "127.0.0.1",
      port: parseInt(process.env.DB_PORT ?? "3306", 10),
      user: process.env.DB_USER ?? "dev",
      password: process.env.DB_PASSWORD ?? "123456",
      database: process.env.DB_NAME ?? "smart_acct_dev",
    });
    super({ adapter });
  }

  async onModuleInit(): Promise<void> {
    await this.$connect();
  }

  async onModuleDestroy(): Promise<void> {
    await this.$disconnect();
  }
}
