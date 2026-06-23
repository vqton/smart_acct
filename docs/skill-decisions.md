# Skill Selection — 4W-H Decision Guide

Pick the right skill for any task. Each entry:

| Axis | Question |
|------|----------|
| **What** | What kind of task triggers this? |
| **Why** | What outcome does it produce? |
| **When** | Where in the TDD/workflow cycle? |
| **Where** | Where does output land? |
| **How** | How to invoke / activate? |

---

## 1. Bug — something is broken

```
What:    Unexpected crash, wrong output, performance regression
Why:     Find root cause. Get regression test. Ship fix.
When:    After bug report. Before any code change.
Where:   Unit/integration test, then src/, then commit.
How:     /diagnose → build feedback loop → reproduce → hypothesise
         → instrument → fix → regression test → post-mortem
```

**Primary:** `diagnose`
**Supporting:** `debugging-and-error-recovery` (systematic root-cause alt flow), `zoom-out` (unfamiliar area), `improve-codebase-architecture` (seam missing), `doubt-driven-development` (adversarial review of high-stakes fix)

---

## 2. Feature — new capability

```
What:    User story or PRD describes new behaviour
Why:     Deliver working code satisfying acceptance criteria
When:    After plan/PRD approved. Before release.
Where:   src/ + tests/. Committed in vertical slices.
How:     /to-issues → tracer-bullet issues
         → each issue: /tdd → RED (test) → GREEN (impl) → REFACTOR
```

**Primary:** `tdd` or `test-driven-development`
**Pre-requisite:** `/to-issues` (break plan), `/to-prd` (synthesise plan)
**Supporting:** `incremental-implementation` (slice discipline), `karpathy-guidelines` (avoid overcomplication), `spec-driven-development` (spec-first), `planning-and-task-breakdown` (ordered tasks), `source-driven-development` (ground in official docs), `api-and-interface-design` (design public boundaries)

---

## 3. Architecture — codebase friction

```
What:    Untestable code, slow CI, hard to navigate modules
Why:     Surface shallow modules. Deepen them. Improve locality + leverage.
When:    After noticing friction. Before it compounds.
Where:   src/ restructuring. ADRs + CONTEXT.md updated.
How:     /improve-codebase-architecture → explore → present candidates
         → /grill-with-docs → sharpen language → implement
```

**Primary:** `improve-codebase-architecture`
**Supporting:** `grill-with-docs` (sharpen language, write ADRs), `zoom-out` (map modules), `code-simplification` (reduce complexity), `api-and-interface-design` (redesign module boundaries)

---

## 4. Plan — unclear direction

```
What:    Vague feature request, lots of unknowns, trade-offs to resolve
Why:     Shared understanding. Written decisions. Actionable breakdown.
When:    Before any implementation. After initial request.
Where:   Issue tracker (PRD), docs/adr/, CONTEXT.md.
How:     /grill-me → walk design tree one Q at a time
         → /to-prd → write PRD → publish
         → /to-issues → slice into actionable chunks
```

**Primary:** `grill-me` (no docs) or `grill-with-docs` (has CONTEXT.md)
**Supporting:** `to-prd` (capture decisions), `to-issues` (slice), `spec-driven-development` (spec before code), `interview-me` (extract real intent when ask is underspecified), `idea-refine` (divergent→convergent for vague concepts)

---

## 5. Learning — unfamiliar code area

```
What:    First time touching this module. Need the big picture.
Why:     Understand callers, dependencies, entrypoints before changing.
When:    Before any edit in an area you haven't explored.
Where:   Mental model. Optional: update CONTEXT.md.
How:     /zoom-out → "map all relevant modules and callers"
```

**Primary:** `zoom-out`

---

## 6. Review — pre-merge quality gate

```
What:    Code written by agent or human needs review before merge
Why:     Catch bugs, style issues, security holes, architecture drift
When:    Before merging. After implementation complete.
Where:   PR comments. Issue tracker. AGENTS.md notes.
How:     /code-review-and-quality → multi-axis review
         → surface findings → fix
```

**Primary:** `code-review-and-quality`
**Supporting:** `code-simplification` (reduce complexity found during review), `security-and-hardening` (audit for vulns), `doubt-driven-development` (adversarial review of critical paths)

---

## 7. Security audit

```
What:    Handling user input, auth, data storage, external integrations
Why:     Prevent vulnerabilities, data leaks, auth bypass
When:    Before shipping any feature that touches untrusted data.
Where:   src/ + config + infra.
How:     /security-and-hardening → review threat model → fix
```

**Primary:** `security-and-hardening`

---

## 8. Performance

```
What:    Slow response times, high CPU/memory, poor Core Web Vitals
Why:     Meet performance budgets. Improve UX.
When:    After profiling reveals bottlenecks.
Where:   src/, queries, bundle, caching.
How:     /performance-optimization → profile → identify → fix → measure
```

**Primary:** `performance-optimization`
**Supporting:** `observability-and-instrumentation` (add metrics/tracing to measure)

---

## 9. CI/CD pipeline

```
What:    Build, test, lint, deploy automation
Why:     Consistent quality gates. Fast feedback.
When:    During project setup. When adding new stages.
Where:   .github/, CI config, deploy scripts.
How:     /ci-cd-and-automation → design pipeline → implement
```

**Primary:** `ci-cd-and-automation`

---

## 10. Shipping / launch

```
What:    Preparing to ship to production
Why:     Avoid launch-day surprises. Rollback plan.
When:    Before deploying. After feature complete.
Where:   Monitoring config, runbook, release notes.
How:     /shipping-and-launch → pre-launch checklist
         → monitoring → staged rollout → rollback plan
```

**Primary:** `shipping-and-launch`

---

## 11. Deprecation / migration

```
What:    Removing old APIs, features, systems
Why:     Clean up tech debt. Migrate users to new path.
When:    When old system exists. Before it blocks progress.
Where:   src/ (old code), docs/ (migration guide), issue tracker.
How:     /deprecation-and-migration → plan deprecation → implement
```

**Primary:** `deprecation-and-migration`

---

## 12. Frontend UI

```
What:    Building or modifying user-facing interfaces
Why:     Production-quality look and feel. Good UX.
When:    After API contract is stable. Before visual polish.
Where:   Components, layouts, styles, state management.
How:     /frontend-ui-engineering → component → layout → state → polish
```

**Primary:** `frontend-ui-engineering`
**Supporting:** `browser-testing-with-devtools` (inspect DOM, capture console, verify output)

---

## 13. Triage — incoming issue

```
What:    New GitHub/GitLab issue or local bug report
Why:     Classify (bug/enhancement). Gather info. Route to agent or human.
When:    As issues arrive. Before they sit stale.
Where:   Issue tracker labels + comments.
How:     /triage → read → recommend category+state
         → reproduce (bugs) → grill (if needs info)
         → apply outcome (agent brief, wontfix, etc.)
```

**Primary:** `triage`

---

## 14. Documentation — project knowledge

```
What:    AGENTS.md, CONTEXT.md, ADRs, issue-tracker config, skills
Why:     Future sessions ramp faster. Consistent vocabulary.
When:    During setup. Whenever a decision crystallises.
Where:   AGENTS.md, docs/adr/, docs/agents/, CONTEXT.md, .opencode/.
How:     /setup-matt-pocock-skills (one-time per repo)
         /documentation-and-adrs (record decisions + docs)
         /grill-with-docs (updates CONTEXT.md + ADRs inline)
         /context-engineering (optimise agent context setup)
         /write-a-skill (create new skill files)
```

**Primary:** `setup-matt-pocock-skills`, `documentation-and-adrs`
**Supporting:** `grill-with-docs`, `write-a-skill`, `context-engineering`

---

## 15. Editing — improve existing writing

```
What:    Draft article, README, or design doc needs tightening
Why:     Clearer structure, shorter paragraphs, better flow.
When:    After first draft. Before publishing.
Where:   The file in place.
How:     /edit-article → propose sections → rewrite each
```

**Primary:** `edit-article`

---

## 16. Git workflow

```
What:    Committing, branching, resolving conflicts
Why:     Clean history. Safe rollbacks. Parallel work streams.
When:    Throughout development.
Where:   Git history, branch structure, PRs.
How:     /git-workflow-and-versioning → commit → branch → merge
```

**Primary:** `git-workflow-and-versioning`

---

## 17. Observability / instrumentation

```
What:    Adding logging, metrics, tracing, alerting
Why:     See what production does. Debug without access.
When:    When shipping production code. When you can't explain behaviour.
Where:   src/ + monitoring config.
How:     /observability-and-instrumentation → instrument → verify
```

**Primary:** `observability-and-instrumentation`

---

## 18. Meta — session/context management

```
What:    New session, degraded output quality, switching tasks
Why:     Reset context. Load right config. Get unstuck.
When:    At session start. When agent quality degrades.
Where:   AGENTS.md, opencode.json, .opencode/instructions/.
How:     /context-engineering → review context → adjust rules
         /using-agent-skills → discover which skill fits
```

**Primary:** `context-engineering`, `using-agent-skills`

---

## Decision Tree (quick reference)

```
Task type?
├── Bug → /diagnose | /debugging-and-error-recovery
├── Feature
│   ├── Need plan? → /interview-me → /grill-me → /spec-driven-development → /to-prd → /to-issues
│   ├── Have plan? → /to-issues → /tdd per slice
│   └── During impl → /source-driven-development | /api-and-interface-design | /incremental-implementation
├── Architecture friction → /improve-codebase-architecture | /code-simplification
├── Unclear direction → /interview-me | /idea-refine | /grill-me | /grill-with-docs
├── First time in module → /zoom-out
├── Pre-merge review → /code-review-and-quality | /security-and-hardening
├── Before shipping → /security-and-hardening | /performance-optimization | /shipping-and-launch
├── Already in prod, blind → /observability-and-instrumentation
├── CI/CD → /ci-cd-and-automation
├── Deprecation → /deprecation-and-migration
├── UI work → /frontend-ui-engineering | /browser-testing-with-devtools
├── Incoming issue → /triage
├── Project setup / docs → /setup-matt-pocock-skills | /documentation-and-adrs | /context-engineering
├── Edit prose → /edit-article
├── Git ops → /git-workflow-and-versioning
└── Meta (which skill?) → /using-agent-skills
```
