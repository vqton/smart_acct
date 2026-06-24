import { Module } from "@nestjs/common";
import { PrismaModule } from "./prisma/prisma.module.js";
import { GlModule } from "./presentation/gl/gl.module.js";
import { TaxModule } from "./presentation/tax/tax.module.js";
import { CoaModule } from "./presentation/coa/coa.module.js";
import { CmModule } from "./presentation/cm/cm.module.js";
import { BankModule } from "./presentation/bank/bank.module.js";
import { PurchasingModule } from "./presentation/purchasing/purchasing.module.js";
import { SalesModule } from "./presentation/sales/sales.module.js";
import { InventoryModule } from "./presentation/inventory/inventory.module.js";
import { PrlModule } from "./presentation/prl/prl.module.js";
import { EinvModule } from "./presentation/einvoice/einv.module.js";
import { FrModule } from "./presentation/fr/fr.module.js";
import { CstModule } from "./presentation/costing/cst.module.js";
import { BudgetModule } from "./presentation/budget/budget.module.js";
import { FaModule } from "./presentation/fa/fa.module.js";
import { AuthModule } from "./auth/presentation/auth.module.js";

@Module({
  imports: [AuthModule, PrismaModule, GlModule, TaxModule, CoaModule, CmModule, BankModule, PurchasingModule, SalesModule, InventoryModule, PrlModule, EinvModule, FrModule, CstModule, BudgetModule, FaModule],
})
export class AppModule {}
