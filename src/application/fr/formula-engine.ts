import { Injectable } from "@nestjs/common";
import type { FormulaRepository } from "../../domain/fr/fr-repositories.js";
import { DomainError } from "../../shared/domain-error.js";

export interface FormulaContext {
  variables: Record<string, number>;
  accountBalances: Record<string, number>;
  periodValues: Record<string, number[]>;
  reportValues: Record<string, Record<string, Record<string, number>>>;
}

@Injectable()
export class FormulaEngine {
  private formulaCache = new Map<string, (ctx: FormulaContext) => number>();

  constructor(private readonly formulaRepo: FormulaRepository) {}

  async evaluate(formulaText: string, context: FormulaContext): Promise<number> {
    if (this.formulaCache.has(formulaText)) {
      const fn = this.formulaCache.get(formulaText)!;
      return fn(context);
    }
    const fn = this.compile(formulaText);
    this.formulaCache.set(formulaText, fn);
    return fn(context);
  }

  async evaluateNested(
    formulaId: string,
    context: FormulaContext,
    visited = new Set<string>(),
  ): Promise<number> {
    if (visited.has(formulaId)) {
      throw new DomainError("BusinessRule", `Circular formula reference: ${formulaId}`);
    }
    visited.add(formulaId);

    const formula = await this.formulaRepo.findById(formulaId as any);
    if (!formula) throw new DomainError("NotFound", `Formula ${formulaId} not found`);

    const resolved = formula.expression.replace(/\{FORMULA\(([^)]+)\)\}/g, (_match: string, ref: string) => {
      return String(this.evaluateNested(ref.trim(), context, visited));
    });

    return this.evaluate(resolved, context);
  }

  private compile(expression: string): (ctx: FormulaContext) => number {
    const tokens = this.tokenize(expression);
    const rpn = this.shunt(tokens);
    return (ctx: FormulaContext) => this.execute(rpn, ctx);
  }

  private tokenize(expr: string): string[] {
    const cleaned = expr.replace(/\s+/g, "");
    const tokens: string[] = [];
    let i = 0;
    while (i < cleaned.length) {
      if ("+-*/()".includes(cleaned[i])) {
        tokens.push(cleaned[i]);
        i++;
      } else if (cleaned[i] === ",") {
        tokens.push(",");
        i++;
      } else if (cleaned[i] >= "0" && cleaned[i] <= "9" || cleaned[i] === ".") {
        let num = "";
        while (i < cleaned.length && (cleaned[i] >= "0" && cleaned[i] <= "9" || cleaned[i] === ".")) {
          num += cleaned[i];
          i++;
        }
        tokens.push(num);
      } else {
        let ident = "";
        while (i < cleaned.length && /[A-Za-z0-9_.]/.test(cleaned[i])) {
          ident += cleaned[i];
          i++;
        }
        tokens.push(ident.toUpperCase());
      }
    }
    return tokens;
  }

  private precedence(op: string): number {
    switch (op) {
      case "+": case "-": return 1;
      case "*": case "/": return 2;
      default: return 0;
    }
  }

  private shunt(tokens: string[]): string[] {
    const output: string[] = [];
    const ops: string[] = [];
    for (const t of tokens) {
      if (!isNaN(Number(t))) { output.push(t); }
      else if (t === "(") { ops.push(t); }
      else if (t === ")") {
        while (ops.length && ops[ops.length - 1] !== "(") output.push(ops.pop()!);
        ops.pop();
        if (ops.length && /^[A-Z_]/.test(ops[ops.length - 1])) output.push(ops.pop()!);
      }
      else if (t === ",") {
        while (ops.length && ops[ops.length - 1] !== "(") output.push(ops.pop()!);
      }
      else if ("+-*/".includes(t)) {
        while (ops.length && this.precedence(ops[ops.length - 1]) >= this.precedence(t)) {
          output.push(ops.pop()!);
        }
        ops.push(t);
      }
      else { ops.push(t); }
    }
    while (ops.length) output.push(ops.pop()!);
    return output;
  }

  private execute(rpn: string[], ctx: FormulaContext): number {
    const stack: number[] = [];
    for (const t of rpn) {
      if (!isNaN(Number(t))) { stack.push(Number(t)); }
      else if ("+-*/".includes(t)) {
        const b = stack.pop()!;
        const a = stack.pop()!;
        switch (t) {
          case "+": stack.push(a + b); break;
          case "-": stack.push(a - b); break;
          case "*": stack.push(a * b); break;
          case "/": stack.push(b === 0 ? 0 : a / b); break;
        }
      } else if (t === "SUM") {
        const count = stack.pop()!;
        let total = 0;
        for (let i = 0; i < count; i++) total += stack.pop()!;
        stack.push(total);
      } else if (t === "AVG") {
        const count = stack.pop()!;
        let total = 0;
        for (let i = 0; i < count; i++) total += stack.pop()!;
        stack.push(count > 0 ? total / count : 0);
      } else if (t === "MIN") {
        const count = stack.pop()!;
        let min = Infinity;
        for (let i = 0; i < count; i++) { const v = stack.pop()!; if (v < min) min = v; }
        stack.push(min === Infinity ? 0 : min);
      } else if (t === "MAX") {
        const count = stack.pop()!;
        let max = -Infinity;
        for (let i = 0; i < count; i++) { const v = stack.pop()!; if (v > max) max = v; }
        stack.push(max === -Infinity ? 0 : max);
      } else if (t === "COUNT") {
        const count = stack.pop()!;
        let nonZero = 0;
        for (let i = 0; i < count; i++) { if (stack.pop()! !== 0) nonZero++; }
        stack.push(nonZero);
      } else if (t.startsWith("ACCOUNT(")) {
        const code = t.slice(8, -1);
        stack.push(ctx.accountBalances[code] ?? 0);
      } else if (t.startsWith("VAR(")) {
        const name = t.slice(4, -1);
        stack.push(ctx.variables[name] ?? 0);
      } else if (t.startsWith("PERIOD(")) {
        const offset = parseInt(t.slice(7, -1), 10);
        const values = ctx.periodValues["default"] ?? [];
        const idx = values.length - 1 + offset;
        stack.push(idx >= 0 && idx < values.length ? values[idx] : 0);
      } else if (t.startsWith("REPORT(")) {
        const parts = t.slice(7, -1).split(",");
        const reportCode = parts[0]?.trim();
        const rowCode = parts[1]?.trim();
        const colCode = parts[2]?.trim();
        const reportData = ctx.reportValues[reportCode ?? ""];
        const rowData = reportData?.[rowCode ?? ""];
        stack.push(rowData?.[colCode ?? ""] ?? 0);
      } else {
        stack.push(ctx.variables[t] ?? 0);
      }
    }
    return stack[0] ?? 0;
  }

  async evaluateFormula(formulaCode: string, periodBalances: Record<string, number>): Promise<number> {
    const context: FormulaContext = {
      variables: {},
      accountBalances: periodBalances,
      periodValues: {},
      reportValues: {},
    };
    const formula = await this.formulaRepo.findByCode(formulaCode);
    if (!formula) throw new DomainError("NotFound", `Formula ${formulaCode} not found`);
    return this.evaluateNested(formula.id.value, context);
  }

  clearCache(): void {
    this.formulaCache.clear();
  }
}
