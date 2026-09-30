import re
from app.agents.state import GraphState
from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.services.latex_sanitizer import sanitize_latex

llm = get_llm(temperature=0.1)

ARCHETYPE_HINTS = {
    "graphing": (
        "Use Axes, axes.plot(), and ValueTracker for animations. "
        "Use MathTex for all mathematical expressions and labels, never bare Tex. "
        "Set sensible x_range/y_range to avoid overflow."
    ),
    "geometry": (
        "Use Circle, Polygon, Line, or Square for shapes. "
        "After creating any shape, call shape.scale_to_fit_height(4.5) if it is large. "
        "Use MathTex and .next_to() for labels. NEVER use .get_label() on shapes (it causes errors). "
        "Use shape.get_right(), shape.get_center() for geometric points, never raw offset arithmetic."
    ),
    "calculus": (
        "Use axes.get_area() for integral shading. "
        "For Riemann sums, use axes.get_riemann_rectangles(). "
        "Use ValueTracker for animated bounds or Riemann rect count. "
        "Use MathTex for all formula labels."
    ),
    "unit_circle": (
        "Use Circle(radius=2.5). Use ValueTracker for the angle (0 to 2*PI). "
        "Use always_redraw for sin/cos projections. "
        "Use MathTex for all labels. Position them using .next_to(point, direction)."
    ),
    "equation": (
        "Align equations with VGroup().arrange(DOWN, aligned_edge=LEFT). "
        "Use TransformMatchingTex or Write to transition between equation steps. "
        "Always use MathTex with raw strings (r'...') for formulas."
    ),
    "number_line": (
        "Use NumberLine() with sensible x_range and length=10. "
        "Use Dot() for points, Arrow() for step direction. "
        "Use MathTex labels for numeric values."
    ),
    "sequence": (
        "Use VGroup() and arrange(RIGHT, buff=0.6). "
        "Use FadeIn with lag_ratio=0.3 for sequential appearance. "
        "Use MathTex for each term."
    ),
}


def _clean_code(raw_content: str) -> str:
    """Extracts Python code from LLM response, stripping markdown fences."""
    text = raw_content.strip()
    match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        match_generic = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match_generic:
            code = match_generic.group(1).strip()
        else:
            code = text

    # Remove any stray markdown header lines before imports
    lines = code.splitlines()
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from manim") or line.strip().startswith("import "):
            start_idx = i
            break
    code = "\n".join(lines[start_idx:]).strip()

    # Ensure from manim import * is present
    if "from manim import *" not in code and "import manim" not in code:
        code = "from manim import *\n" + code

    # Apply LaTeX escape sanitization pass
    code = sanitize_latex(code)

    return code


def developer_node(state: GraphState) -> dict:
    """
    Node C: Developer.
    Generates COMPLETE Manim code using the reference template as a structural guide
    and the user's question for content.
    """
    print("---NODE C: DEVELOPER---")
    user_input = state["user_input"]
    math_solution = state.get("math_solution", "")
    archetype = state.get("archetype", "general")
    reference_template = state.get("reference_template", "")

    # Use proven code from memory if available
    if state.get("proven_code"):
        print("Developer: Using proven code from memory.")
        return {"manim_code": state["proven_code"]}

    # Use deterministic template code if generated
    if state.get("template_code") and not state.get("error_log"):
        print("Developer: Using deterministic template code from TemplateEngine.")
        return {"manim_code": state["template_code"]}

    retrieved_docs = "\n\n".join(state.get("retrieved_docs", []))
    hint = ARCHETYPE_HINTS.get(archetype, "Create a clear, educational Manim animation.")

    # Check for errors to fix (retry loop)
    previous_error = state.get("error_log")
    if not previous_error and state.get("render_errors"):
        previous_error = "\n".join(state["render_errors"])

    attempt_count = state.get("attempt_count", 0)

    if previous_error:
        print(f"Developer: Fixing error (attempt {attempt_count})")
        prompt = f"""You are an Expert Manim Code Fixer.

User Task: {user_input}
Math Solution: {math_solution}

PREVIOUS RENDER / VALIDATION ERROR TO FIX:
{previous_error}

Archetype: {archetype.upper()}
Hint: {hint}

Reference Structural Pattern:
```python
{reference_template}
```

MANDATORY RULES:
1. Fix the error completely while keeping the animation visually appealing and correct.
2. Use `MathTex(r"...")` for ALL mathematical expressions. Never use `Tex()` for math.
3. Every LaTeX string MUST be a raw string: `r"..."`.
4. The Scene class MUST be named `MathScene(Scene):`.
5. NEVER use `.get_label()` on geometric shapes like Circle or Square. Use `MathTex(r"...").next_to(shape)`.
6. Import `from manim import *` at the top.
7. No `input()` or interactive prompts.
8. NO STATIC SCENES: NEVER use `self.add()` to dump shapes or labels all at once. Animate EVERY element step-by-step using `self.play(Create(...))`, `self.play(Write(...))`, with `self.wait(0.5)` pacing between steps.

Output ONLY valid, executable Python code inside ```python ``` blocks. No conversational text.
"""
    else:
        prompt = f"""You are an Elite Manim (Community Edition) Animation Engineer.

Goal: Create a visually stunning, pedagogically clear mathematical animation for:
"{user_input}"

Mathematical Solution & Storyboard:
{math_solution}

Manim Documentation Snippets:
{retrieved_docs}

Archetype: {archetype.upper()}
Hint: {hint}

Reference Structural Template (adapt the structure and style, but use the EXACT problem values):
```python
{reference_template}
```

CRITICAL RULES:
1. Write a COMPLETE, RUNNABLE Python script with `from manim import *`.
2. Class MUST be named `class MathScene(Scene):`.
3. Use `MathTex(r"...")` for all equations and mathematical variables.
4. Keep all objects bounded within standard camera limits (width 14, height 8). Scale shapes if needed.
5. Include `self.wait(1)` after significant visual milestones.
6. Use clear contrasting colors (YELLOW, BLUE, TEAL, GREEN, WHITE).
7. Never use `.get_label()` on basic shapes; use `.next_to()`.
8. NO STATIC SCENES: NEVER use `self.add()` to dump objects onto the screen. Every line, dot, label, and shape MUST be introduced dynamically with `self.play(Create(...))`, `self.play(Write(...))`, or `self.play(FadeIn(...))`. Use step banners (`Text('Step 1: ...', font_size=20).to_edge(DOWN)`) to narrate the construction step-by-step.

Output ONLY executable Python code inside ```python ``` blocks. No conversational text.
"""

    print("Developer: Prompting LLM for Manim code...")
    response = llm.invoke([SystemMessage(content=prompt)])
    raw_content = response.content if hasattr(response, "content") else str(response)
    code = _clean_code(raw_content)

    return {"manim_code": code}
