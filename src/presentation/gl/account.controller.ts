import { Controller, Get, Post, Put, Delete, Param, Body, Query, NotFoundException, ConflictException, BadRequestException } from "@nestjs/common";
import { ApiTags, ApiOperation, ApiQuery } from "@nestjs/swagger";
import { PrismaAccountRepository } from "../../infrastructure/gl/gl-prisma-repos.js";
import { AccountId } from "../../domain/gl/account-id.js";
import { Account } from "../../domain/gl/account.js";
import { CreateAccountDto, UpdateAccountDto } from "./dto/account.dto.js";

@ApiTags("GL Accounts")
@Controller("api/gl/accounts")
export class AccountController {
  constructor(private readonly accountRepo: PrismaAccountRepository) {}

  @Post()
  @ApiOperation({ summary: "Create a new account" })
  async create(@Body() dto: CreateAccountDto) {
    const existing = await this.accountRepo.findByCode(dto.code);
    if (existing) throw new ConflictException(`Account code ${dto.code} already exists`);

    if (dto.parentId) {
      const parent = await this.accountRepo.findById(new AccountId(dto.parentId));
      if (!parent) throw new NotFoundException(`Parent account ${dto.parentId} not found`);
    }

    const account = Account.create({
      code: dto.code,
      name: dto.name,
      category: dto.category,
      nature: dto.nature,
      parentId: dto.parentId,
      currencyCode: dto.currencyCode,
      description: dto.description,
      isControl: dto.isControl,
      isPosting: dto.isPosting,
    });

    await this.accountRepo.save(account);
    return account.toState();
  }

  @Get()
  @ApiOperation({ summary: "List all accounts" })
  @ApiQuery({ name: "keyword", required: false })
  @ApiQuery({ name: "category", required: false })
  @ApiQuery({ name: "isActive", required: false })
  async findAll(
    @Query("keyword") keyword?: string,
    @Query("category") category?: string,
    @Query("isActive") isActive?: string,
  ) {
    if (keyword || category || isActive !== undefined) {
      return this.accountRepo.search({
        keyword,
        category,
        isActive: isActive !== undefined ? isActive === "true" : undefined,
      });
    }
    return this.accountRepo.findAll();
  }

  @Get("tree")
  @ApiOperation({ summary: "Get chart of accounts as tree" })
  async getTree() {
    const accounts = await this.accountRepo.findAll();
    const map = new Map<string, any>();
    const roots: any[] = [];

    for (const a of accounts) {
      map.set(a.id.value, { ...a.toState(), children: [] });
    }

    for (const a of accounts) {
      const node = map.get(a.id.value)!;
      if (a.parentId && map.has(a.parentId)) {
        map.get(a.parentId)!.children.push(node);
      } else {
        roots.push(node);
      }
    }

    return roots;
  }

  @Get(":id")
  @ApiOperation({ summary: "Get account by ID" })
  async findById(@Param("id") id: string) {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new NotFoundException("Account not found");
    return account.toState();
  }

  @Put(":id")
  @ApiOperation({ summary: "Update account" })
  async update(@Param("id") id: string, @Body() dto: UpdateAccountDto) {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new NotFoundException("Account not found");

    account.modify({
      name: dto.name,
      nameEn: dto.nameEn,
      description: dto.description,
      isActive: dto.isActive,
    });

    await this.accountRepo.save(account);
    return account.toState();
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete account (soft)" })
  async delete(@Param("id") id: string) {
    const account = await this.accountRepo.findById(new AccountId(id));
    if (!account) throw new NotFoundException("Account not found");
    account.markDeleted();
    await this.accountRepo.save(account);
    return { success: true };
  }

  @Post("seed")
  @ApiOperation({ summary: "Seed chart of accounts" })
  async seed() {
    const existing = await this.accountRepo.findAll();
    if (existing.length > 0) throw new BadRequestException("Accounts already seeded");

    const accounts: Array<{
      code: string; name: string; category: any; nature: any; isControl?: boolean; isPosting?: boolean;
    }> = [
      { code: "1", name: "Tài sản", category: "short_term_asset" as any, nature: "debit" as any, isControl: true, isPosting: false },
      { code: "11", name: "Tiền và tương đương tiền", category: "short_term_asset" as any, nature: "debit" as any, isControl: true, isPosting: false },
      { code: "111", name: "Tiền mặt", category: "short_term_asset" as any, nature: "debit" as any, isControl: true, isPosting: false },
      { code: "1111", name: "Tiền mặt VNĐ", category: "short_term_asset" as any, nature: "debit" as any },
      { code: "1112", name: "Tiền mặt USD", category: "short_term_asset" as any, nature: "debit" as any },
      { code: "112", name: "Tiền gửi ngân hàng", category: "short_term_asset" as any, nature: "debit" as any, isControl: true, isPosting: false },
      { code: "1121", name: "Tiền gửi ngân hàng VNĐ", category: "short_term_asset" as any, nature: "debit" as any },
      { code: "2", name: "Nợ phải trả", category: "short_term_liability" as any, nature: "credit" as any, isControl: true, isPosting: false },
      { code: "3", name: "Vốn chủ sở hữu", category: "equity" as any, nature: "credit" as any, isControl: true, isPosting: false },
      { code: "4", name: "Doanh thu", category: "revenue" as any, nature: "credit" as any, isControl: true, isPosting: false },
      { code: "5", name: "Chi phí", category: "operating_expense" as any, nature: "debit" as any, isControl: true, isPosting: false },
      { code: "6", name: "Giá vốn hàng bán", category: "cost_of_goods_sold" as any, nature: "debit" as any, isControl: true, isPosting: false },
    ];

    // first pass: create all accounts
    const idMap = new Map<string, string>();
    for (const a of accounts) {
      const account = Account.create(a);
      await this.accountRepo.save(account);
      idMap.set(a.code, account.id.value);
    }

    // second pass: set parentId based on code prefix
    for (const a of accounts) {
      if (a.code.length > 1) {
        const parentCode = a.code.slice(0, -1);
        const parentId = idMap.get(parentCode);
        if (parentId) {
          const account = await this.accountRepo.findById(new AccountId(idMap.get(a.code)!));
          if (account) {
            (account as any)._parentId = parentId;
            await this.accountRepo.save(account);
          }
        }
      }
    }

    return { count: accounts.length };
  }
}
