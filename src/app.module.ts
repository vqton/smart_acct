import { Module } from "@nestjs/common";
import { PrismaModule } from "./prisma/prisma.module.js";
import { GlModule } from "./presentation/gl/gl.module.js";
import { TaxModule } from "./presentation/tax/tax.module.js";
import { CoaModule } from "./presentation/coa/coa.module.js";
import { CmModule } from "./presentation/cm/cm.module.js";
import { BankModule } from "./presentation/bank/bank.module.js";

@Module({
  imports: [PrismaModule, GlModule, TaxModule, CoaModule, CmModule, BankModule],
})
export class AppModule {}
