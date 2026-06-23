import { Module } from "@nestjs/common";
import { PrismaModule } from "./prisma/prisma.module.js";
import { GlModule } from "./presentation/gl/gl.module.js";
import { TaxModule } from "./presentation/tax/tax.module.js";

@Module({
  imports: [PrismaModule, GlModule, TaxModule],
})
export class AppModule {}
