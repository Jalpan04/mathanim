# MathAnim — Agent & Architecture Context

> **Purpose of this file**: Authoritative reference for any LLM agent, developer, or tool operating inside the MathAnim codebase. Read this before writing or modifying any code.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Core Architecture — Agent Swarm](#2-core-architecture--agent-swarm)
3. [Pipeline Node Contracts](#3-pipeline-node-contracts)
4. [Hybrid Router & Archetype Classification](#4-hybrid-router--archetype-classification)
5. [Reference Templates](#5-reference-templates)
6. [Data Layer — topics.yaml](#6-data-layer--topicsyaml)
7. [Execution Environment](#7-execution-environment)
8. [Manim Code Generation Rules](#8-manim-code-generation-rules)
9. [GraphState Schema](#9-graphstate-schema)
10. [Error Handling & Self-Healing](#10-error-handling--self-healing)
11. [Key Decisions & Anti-Patterns](#11-key-decisions--anti-patterns)
12. [Extending the System — Checklists](#12-extending-the-system--checklists)

---

## 1. Project Overview

MathAnim is a **hybrid rendering engine** that converts natural-language math problems into Manim animations.

| Dimension | Detail |
|---|---|
| **Input** | Natural-language math problem (string) |
| **Output** | MP4 animation file URL |
| **Architecture** | LLM-first generative pipeline (Agent Swarm via LangGraph) |
| **Fallback** | Static pre-rendered videos for known low-confidence inputs |

### Design Philosophy

- **LLM-first**: Agents write full, fresh Manim scripts. No string interpolation into rigid templates.
- **Reference, don't inject**: Templates show structural patterns; the Developer LLM adapts all values.
- **Self-healing by default**: Every render failure loops back through the Developer with the error log.

---

## 2. Core Architecture — Agent Swarm

All non-fallback requests pass through a LangGraph graph. The state object (`GraphState`) flows through four sequential nodes.

```
User Request
     │
     ▼
[Hybrid Router] ── classifies archetype, loads Reference Template
     │
     ▼
[Mathematician] ── solves problem, emits step-by-step solution
     │
     ▼
[Architect] ── builds RAG query, retrieves Manim doc snippets
     │
     ▼
[Developer] ── writes Manim Python script (uses template as pattern only)
     │
     ▼
[Critic] ── dry-run render
     │
  PASS? ──Yes──► return video URL
     │
    No
     │
     ▼
[Developer] ◄── retry with error log  (max 3 attempts, then static fallback)
```

---

## 3. Pipeline Node Contracts

Each node reads specific fields from `GraphState` and writes specific fields. Do not read/write outside these contracts.

### 3.1 Mathematician

| | Fields |
|---|---|
| **Reads** | `user_input` |
| **Writes** | `math_solution` (step-by-step string), `topic_hint` (optional, e.g. "integral") |

**Responsibilities**
- Solve the problem completely before passing state forward.
- Express solutions in plain mathematical notation, not LaTeX.
- Set `topic_hint` if the problem domain is unambiguous; leave `None` otherwise.

---

### 3.2 Architect

| | Fields |
|---|---|
| **Reads** | `user_input`, `math_solution`, `archetype` |
| **Writes** | `rag_snippets` (list of Manim doc strings) |

**Responsibilities**
- Construct a focused RAG query from the archetype + math domain.
- Return 3–5 relevant Manim snippets. Prefer concise API examples over long prose.
- Do **not** generate code here — only retrieve context.

---

### 3.3 Developer

| | Fields |
|---|---|
| **Reads** | `user_input`, `math_solution`, `archetype`, `reference_template`, `rag_snippets`, `last_error` (if retry) |
| **Writes** | `generated_code` (complete Python string), `attempt_count` (increment) |

**Responsibilities**
- Write a **complete, runnable** Manim Python script.
- Use `reference_template` as a structural pattern only — do not copy values verbatim.
- On retry: read `last_error` carefully and fix the root cause. Do not just re-generate.
- See [§8 Manim Code Generation Rules](#8-manim-code-generation-rules) for all hard rules.

---

### 3.4 Critic

| | Fields |
|---|---|
| **Reads** | `generated_code`, `attempt_count` |
| **Writes** | `render_status` (`"pass"` / `"fail"`), `last_error` (stderr string on fail), `video_url` (on pass) |

**Responsibilities**
- Execute a dry-run render via the Docker renderer.
- On failure: populate `last_error` with the full stderr; do **not** truncate.
- If `attempt_count >= 3` and status is still `"fail"`, set `render_status = "fallback"` to trigger static video.

---

## 4. Hybrid Router & Archetype Classification

**File**: `app/services/hybrid_router.py`

### Classification Pipeline (in order)

1. **Keyword match** against `topics.yaml` — fast path, O(n) string search.
2. **Fast keyword pre-check** — secondary heuristic before LLM call.
3. **LLM classification** (Gemma 3) — only if steps 1–2 yield no confident match.

### Output Contract

```python
{
    "archetype": str,          # e.g. "graphing", "calculus", "geometry"
    "reference_template": str, # raw source of the matching template file
    "confidence": float        # 0.0–1.0; below 0.4 triggers static fallback
}
```

### Rules

- Never modify `reference_template` content in the router. Pass it verbatim.
- If no archetype matches with confidence ≥ 0.4, return `archetype = "unknown"` and route to static fallback.
- The router must not call the Agent Swarm — it only classifies.

---

## 5. Reference Templates

**Directory**: `app/templates/`

These are **clean, working Manim scripts** used as structural patterns by the Developer LLM. They contain no placeholders.

| File | Use Case |
|---|---|
| `graphing_template.py` | 2D/3D functions using `Axes` |
| `calculus_template.py` | Integrals and Riemann sums |
| `geometry_template.py` | Shapes, areas, perimeter |
| `number_line_template.py` | Addition / subtraction on a number line |
| `equation_template.py` | Step-by-step algebraic solving |
| `sequence_template.py` | Arithmetic / geometric series |
| `unit_circle_template.py` | Trigonometric animations |

### Template Rules

- Templates must remain **self-contained and runnable** at all times. Run `manim -ql <template>` before committing.
- Templates define **structure** (scene class layout, animation rhythm, mobject hierarchy) — not domain values.
- Never add `{{ PLACEHOLDER }}` syntax. This pattern is permanently retired.
- When adding a new template, add a corresponding entry in `topics.yaml` and register it in the router's archetype map.

---

## 6. Data Layer — topics.yaml

**File**: `curriculum/topics.yaml`

### Schema

```yaml
- id: string          # snake_case unique identifier
  name: string        # Human-readable topic name
  archetype: string   # Must match a file in app/templates/
  keywords: [string]  # Used for keyword-match classification
```

### Rules

- **No hardcoded constants** (values, coefficients, formulae). Topics are classifiers only.
- `archetype` must exactly match the stem of a template filename (e.g. `calculus` → `calculus_template.py`).
- Keywords should be domain terms a user would naturally type, not internal code identifiers.
- Entries are append-only in production. Deprecate by setting `active: false`, never delete.

### Example Entry

```yaml
- id: riemann_sum
  name: Riemann Sum
  archetype: calculus
  keywords: ["riemann", "riemann sum", "left sum", "right sum", "midpoint rule", "numerical integration"]
```

---

## 7. Execution Environment

### API Layer

**File**: `app/api/main.py` | Framework: **FastAPI**

| Endpoint | Method | Purpose |
|---|---|---|
| `/solve` | `POST` | Submit a problem; returns `task_id` |
| `/status/{task_id}` | `GET` | Poll for result; returns status + video URL |

### Worker

**File**: `workers/tasks.py` | Runtime: **Celery + Redis**

- Tasks are async. `/solve` enqueues immediately; `/status` polls.
- Workers must not block the event loop — all render subprocesses must be spawned, not awaited inline.

### Renderer

- **Image**: `mathanim-renderer` (Docker)
- Render command: `manim -ql <script_path> <SceneClassName>`
- Stdout/stderr captured fully and passed to Critic node.

### File Paths

| Path | Purpose |
|---|---|
| `generated_scenes/` | Temporary generated Python scripts (cleaned up after render) |
| `media/videos/` | Final MP4 output files |

---

## 8. Manim Code Generation Rules

These rules are **mandatory** for the Developer node. Violations cause render failures.

### Imports

```python
# Always use wildcard import — never import individual names
from manim import *
```

Rationale: Manim color constants (`BLUE`, `RED`, `WHITE`, etc.) and mobject classes are only guaranteed available via `*`. Selective imports cause `NameError` at render time.

### LaTeX / MathTex

| Rule | Correct | Wrong |
|---|---|---|
| Use `MathTex` for all equations | `MathTex(r"\int_0^1 x^2 dx")` | `Tex(r"\int_0^1 x^2 dx")` |
| Use raw strings for all LaTeX | `r"\frac{1}{2}"` | `"\frac{1}{2}"` |
| Never use bare `Tex` with math symbols | — | `Tex("$x^2$")` |

### Scene Class

- Every script must define exactly **one** `Scene` subclass.
- Class name must be `PascalCase` and descriptive (e.g. `QuadraticGraphScene`, not `MyScene`).
- The Critic extracts the class name automatically — do not hardcode it elsewhere.

### Animation Hygiene

- Call `self.wait()` between significant animation steps for visual breathing room.
- Group related mobjects with `VGroup` to simplify transforms and positioning.
- Use `self.play(Write(...))` for text; `self.play(Create(...))` for geometric shapes.
- Avoid deprecated methods: `ShowCreation` → `Create`, `FadeInFrom` → `FadeIn(shift=...)`.

### Code Quality Checklist (Developer must verify before writing `generated_code`)

- [ ] `from manim import *` is the first import
- [ ] All LaTeX strings are raw strings (`r"..."`)
- [ ] Only `MathTex` is used for mathematical expressions
- [ ] Exactly one `Scene` subclass is defined
- [ ] No undefined variable names (especially color constants)
- [ ] No placeholder strings or `TODO` comments in generated code

---

## 9. GraphState Schema

**File**: `app/agents/state.py`

All agents read and write only via `GraphState`. Never pass data outside this object.

```python
class GraphState(TypedDict):
    # Inputs
    user_input: str                        # Raw problem from user

    # Router outputs
    archetype: str                         # Classified archetype
    reference_template: str               # Raw source of matching template
    confidence: float                      # Classification confidence (0.0–1.0)

    # Agent outputs
    topic_hint: Optional[str]             # Set by Mathematician
    math_solution: str                    # Step-by-step solution
    rag_snippets: List[str]               # Manim doc snippets from Architect
    generated_code: str                   # Manim Python script from Developer

    # Critic / execution
    render_status: Literal["pending", "pass", "fail", "fallback"]
    last_error: Optional[str]             # Stderr from last failed render
    video_url: Optional[str]              # Set on successful render
    attempt_count: int                    # Developer retry counter (max 3)
```

**Rules**
- Never add fields to `GraphState` without updating this file and this document.
- `attempt_count` must be incremented by the Developer, not the Critic.
- `last_error` must be set to `None` on a successful render pass.

---

## 10. Error Handling & Self-Healing

### Retry Logic

```
attempt_count = 0
while attempt_count < 3:
    Developer generates/fixes code
    Critic runs dry-run
    if PASS → return video_url
    else → increment attempt_count, pass last_error back to Developer

if still FAIL after 3 attempts → set render_status = "fallback"
```

### Developer Retry Instructions

When retrying with `last_error` present:
1. Read the full error — don't skim.
2. Identify the **root cause** (import error, undefined name, LaTeX syntax, etc.).
3. Fix specifically. Do not regenerate the whole script unless the error is structural.
4. Re-verify the [§8 Code Quality Checklist](#8-manim-code-generation-rules) before writing.

### Common Error Causes & Fixes

| Error Pattern | Root Cause | Fix |
|---|---|---|
| `NameError: name 'BLUE' is not defined` | Missing `from manim import *` | Add wildcard import |
| `NameError: name 'MathTex' is not defined` | Same as above | Same fix |
| `ValueError: ...LaTeX` | Non-raw string with backslash sequences | Wrap in `r"..."` |
| `AttributeError: 'Scene' has no attribute '...'` | Deprecated Manim API | Check Manim v0.17+ docs |
| `TypeError` on `self.play(...)` | Wrong argument type or deprecated method | Check animation API |

---

## 11. Key Decisions & Anti-Patterns

### ✅ Do This

- Let the Developer LLM write the **full script** from scratch using the template as a pattern.
- Always pass the **complete** stderr to the Developer on retry.
- Keep templates runnable and committed to version control.
- Use `MathTex` + raw strings everywhere without exception.

### ❌ Never Do This

| Anti-Pattern | Why |
|---|---|
| `{{ PLACEHOLDER }}` injection into templates | Brittle, breaks on unexpected input, retired permanently |
| Selective Manim imports (`from manim import Scene, Axes`) | Color constants and many mobjects are missing; causes `NameError` |
| Truncating `last_error` before passing to Developer | Developer needs full context to fix the root cause |
| Hardcoding math values in `topics.yaml` | Topics are classifiers only; values belong in generated code |
| Using `Tex` for equations with math symbols | Use `MathTex` exclusively for anything with LaTeX math |
| Adding logic to the Hybrid Router beyond classification | Router classifies only; no agent calls, no code generation |

---

## 12. Extending the System — Checklists

### Adding a New Topic

- [ ] Add entry to `curriculum/topics.yaml` (id, name, archetype, keywords only)
- [ ] Verify `archetype` maps to an existing template file
- [ ] Test classification: does the new topic route correctly via the hybrid router?
- [ ] No constants or values in the YAML entry

### Adding a New Archetype (Template)

- [ ] Create `app/templates/<archetype>_template.py` — clean, runnable Manim script
- [ ] Run `manim -ql app/templates/<archetype>_template.py <ClassName>` — must succeed
- [ ] Register archetype in `app/services/hybrid_router.py` archetype map
- [ ] Add at least one topic entry in `topics.yaml` pointing to the new archetype
- [ ] Document the template in [§5 Reference Templates](#5-reference-templates) above
- [ ] Add example keywords that users would naturally type

### Adding a New Agent Node

- If rendering fails due to a `NameError` (e.g., `BLUE` not found), ensure `from manim import *` is at the top of the generated code.
- **NEVER** use `.get_label()` on basic shapes like `Circle` or `Square`. Use `MathTex` + `.next_to()` instead.
- Always adhere to the `GraphState` in `app/agents/state.py`.
- [ ] Define input/output fields clearly in [§3 Pipeline Node Contracts](#3-pipeline-node-contracts)
- [ ] Add any new fields to `GraphState` in `app/agents/state.py`
- [ ] Update this document's schema table in [§9](#9-graphstate-schema)
- [ ] Register the node in the LangGraph graph definition
- [ ] Write a unit test that validates the node's contract in isolation

---

*Last updated: 2026-06 · Maintain this file alongside any architectural change.*