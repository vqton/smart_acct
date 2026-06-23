import { Module } from "@nestjs/common";
import { CoaService } from "../../application/coa/coa-service.js";
import {
  PrismaAccountClassRepository,
  PrismaAccountTypeRepository,
  PrismaAccountMappingRepository,
  PrismaAccountExtensionRepository,
} from "../../infrastructure/coa/coa-prisma-repos.js";
import { CoaAccountClassController } from "./coa-class.controller.js";
import { CoaAccountTypeController } from "./coa-type.controller.js";
import { CoaAccountMappingController } from "./coa-mapping.controller.js";
import { CoaAccountExtensionController } from "./coa-extension.controller.js";

@Module({
  controllers: [
    CoaAccountClassController,
    CoaAccountTypeController,
    CoaAccountMappingController,
    CoaAccountExtensionController,
  ],
  providers: [
    CoaService,
    PrismaAccountClassRepository,
    PrismaAccountTypeRepository,
    PrismaAccountMappingRepository,
    PrismaAccountExtensionRepository,
  ],
  exports: [
    CoaService,
    PrismaAccountClassRepository,
    PrismaAccountTypeRepository,
    PrismaAccountMappingRepository,
    PrismaAccountExtensionRepository,
  ],
})
export class CoaModule {}
