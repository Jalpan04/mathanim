import re
import sys
from app.agents.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_llm
from app.services.template_engine import TemplateEngine

llm = get_llm(temperature=0.1)


def _safe_sympy_eval(expr_str: str) -> str:
    """Safely evaluate simple math expressions using local SymPy in-process."""
    try:
        import sympy
        # Basic sanitization
        clean = expr_str.strip().replace("^", "**")
        result = sympy.sympify(clean, evaluate=True)
        return str(result)
    except Exception:
        return ""


def mathematician_node(state: GraphState) -> dict:
    """
    Node A: Mathematician.
    Checks for deterministic pre-built templates first. If matched, generates
    exact coordinates, steps, and Manim code instantly. Otherwise falls back to LLM.
    """
    print("---NODE A: MATHEMATICIAN---")
    user_input = state["user_input"]

    # 1. Fast Template Engine Match
    try:
        template_res = TemplateEngine.match_and_generate(user_input)
        if template_res:
            code, solution, archetype = template_res
            print(f"Mathematician: Matched deterministic template for archetype '{archetype}'! Skipping LLM.")
            return {
                "math_solution": solution,
                "template_code": code,
                "archetype": archetype,
            }
    except Exception as e:
        print(f"Mathematician: Template check warning (proceeding to LLM): {e}")

    system_prompt = """You are an expert Mathematical Problem Solver and Animation Director.

Your Goal: Break down the math problem into an accurate, rigorous mathematical solution and a visual animation storyboard.

Instructions:
1. **Solve**: State the exact mathematical problem, formulas, and step-by-step solution.
2. **Key Values**: List exact domain, range, points, roots, or geometry coordinates needed for animation.
3. **Animation Storyboard**:
   - Scene Title / Equation intro
   - Visual element creation (axes, curves, shapes, number line, or equations)
   - Transformations / Highlights / Transitions
   - Final result highlight

Constraints:
- Be mathematically exact and clear.
- Use plain mathematical and LaTeX notation where appropriate.
- Keep the breakdown structured and concise for the developer.
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Math Problem: {user_input}")
    ])

    solution = response.content.strip()
    print("Mathematician: Solution and visual storyboard generated.")

    return {"math_solution": solution}
