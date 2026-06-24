## Session init

Before any other work, always perform these initialization steps in order:

1. Load the `caveman` skill.
   - Use terse mode.
   - No filler.
   - No unnecessary explanations.

2. Load the `karpathy-guidelines` skill.
   - Prefer surgical changes.
   - Avoid overcomplication.
   - Preserve existing architecture whenever possible.

3. Look for an `AGENTS.md` file, starting from the current working directory and then walking upward toward the repository root.
   - If found, read and follow all applicable instructions.
   - Automatically select and apply any relevant skills, workflows, conventions, or constraints defined in `AGENTS.md` before performing the task.
   - If multiple skills are applicable, combine them consistently.
   - If no `AGENTS.md` exists, continue normally.

Only after completing these initialization steps should you begin the requested task.