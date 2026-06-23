import { PipelineStep, PipelineStepStage, executePipelineSteps, PipelineExecutionError } from "./pipeline-step.js";
import { PostingContext, toRuleContext } from "./posting-context.js";
import { RuleEngine } from "../rules/rule-engine.js";
import { RuleCategory, RuleEffect, RuleSeverity } from "../rules/posting-rule.js";

export interface PipelineConfig {
  maxRetries?: number;
  failOnWarning?: boolean;
  enabledSteps?: string[];
  disabledSteps?: string[];
}

export class PostingPipeline {
  private steps: PipelineStep[] = [];

  constructor(
    private ruleEngine: RuleEngine,
    private config: PipelineConfig = {},
  ) {}

  addStep(step: PipelineStep): void {
    if (this.config.disabledSteps?.includes(step.name)) return;
    if (this.config.enabledSteps && !this.config.enabledSteps.includes(step.name)) return;
    this.steps.push(step);
  }

  addSteps(steps: PipelineStep[]): void {
    for (const step of steps) {
      this.addStep(step);
    }
  }

  getSteps(stage?: PipelineStepStage): PipelineStep[] {
    if (!stage) return [...this.steps].sort((a, b) => a.order - b.order);
    return this.steps
      .filter(s => s.stage === stage)
      .sort((a, b) => a.order - b.order);
  }

  async execute(ctx: PostingContext): Promise<PostingContext> {
    const preSteps = this.getSteps(PipelineStepStage.PreValidation);
    const postSteps = this.getSteps(PipelineStepStage.PostValidation);
    const preCommitSteps = this.getSteps(PipelineStepStage.PreCommit);
    const postCommitSteps = this.getSteps(PipelineStepStage.PostCommit);

    ctx = await executePipelineSteps(preSteps, ctx);
    ctx = await executePipelineSteps(postSteps, ctx);

    const ruleCtx = toRuleContext(ctx);
    const allRuleCategories = Object.values(RuleCategory);
    const ruleResult = await this.ruleEngine.evaluate(ruleCtx, allRuleCategories);
    ctx.ruleResults = ruleResult.results;

    if (!ruleResult.passed) {
      throw new PipelineExecutionError(
        "RuleEngine",
        `Rule validation failed: ${ruleResult.errors.join("; ")}`,
        new Error(ruleResult.errors.join("; ")),
      );
    }

    ctx = await executePipelineSteps(preCommitSteps, ctx);
    ctx = await executePipelineSteps(postCommitSteps, ctx);
    ctx.state = "committed";

    return ctx;
  }
}
