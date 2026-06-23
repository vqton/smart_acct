import { PostingContext } from "./posting-context.js";

export enum PipelineStepStage {
  PreValidation = "pre_validation",
  PostValidation = "post_validation",
  PreCommit = "pre_commit",
  PostCommit = "post_commit",
  Rollback = "rollback",
}

export interface PipelineStep {
  readonly name: string;
  readonly stage: PipelineStepStage;
  readonly order: number;
  execute(ctx: PostingContext): Promise<PostingContext>;
  rollback?(ctx: PostingContext): Promise<PostingContext>;
}

export class PipelineExecutionError extends Error {
  constructor(
    public readonly stepName: string,
    message: string,
    public readonly originalError: Error,
  ) {
    super(`[${stepName}] ${message}`);
    this.name = "PipelineExecutionError";
  }
}

export async function executePipelineSteps(steps: PipelineStep[], ctx: PostingContext): Promise<PostingContext> {
  ctx.state = "validating";
  const executedSteps: PipelineStep[] = [];

  try {
    for (const step of steps) {
      ctx = await step.execute(ctx);
      executedSteps.push(step);
    }
    ctx.state = "posting";
    return ctx;
  } catch (error) {
    ctx.state = "failed";
    ctx.error = error instanceof Error ? error : new Error(String(error));

    const rollbackSteps = executedSteps.reverse().filter(s => s.rollback);
    for (const step of rollbackSteps) {
      try {
        ctx = await step.rollback!(ctx);
      } catch (rbError) {
        console.error(`Rollback failed for step ${step.name}:`, rbError);
      }
    }
    ctx.state = "rolled_back";
    throw new PipelineExecutionError(
      executedSteps.length > 0 ? executedSteps[executedSteps.length - 1].name : "unknown",
      `Pipeline failed: ${(error as Error).message}`,
      error instanceof Error ? error : new Error(String(error)),
    );
  }
}
