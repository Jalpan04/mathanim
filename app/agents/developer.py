from app.agents.state import GraphState
from langchain_core.messages import SystemMessage
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="gemma3:12b", temperature=0.1)

ARCHETYPE_HINTS = {
    "graphing": (
        "Use Axes, axes.plot(), and ValueTracker for animations. "
        "Use MathTex for all labels, never Tex. "
        "Set sensible x_range/y_range to avoid overflow."
    ),
    "geometry": (
        "Use Circle, Polygon, or Line for shapes. "
        "After creating any shape, call shape.scale_to_fit_height(5) if its height > 5. "
        "Use shape.get_right(), shape.get_center() for geometric points, never raw offset arithmetic."
    ),
    "calculus": (
        "Use axes.get_area() for integral shading. "
        "For Riemann sums, use axes.get_riemann_rectangles(). "
        "Use ValueTracker for animated bounds or Riemann rect count."
    ),
    "unit_circle": (
        "Use Circle(radius=2.5). Use ValueTracker for the angle (0 to 2*PI). "
        "Use always_redraw for sin/cos projections. "
        "Split-screen if showing both circle and wave."
    ),
    "equation": (
        "Align equations with VGroup().arrange(DOWN, aligned_edge=LEFT). "
        "Use TransformMatchingTex to morph between equation steps. "
        "Always use MathTex, never Tex, for formulas."
    ),
    "number_line": (
        "Use NumberLine() with sensible x_range. "
        "Use Dot() for points, Arrow() for direction. "
        "Use MathTex labels, not Text, for numeric values."
    ),
    "sequence": (
        "Use VGroup() and arrange(RIGHT, buff=0.5). "
        "Use FadeIn with lag_ratio=0.3 for sequential appearance. "
        "Use MathTex for each term."
    ),
}


def developer_node(state: GraphState):
    """
    Node C: Developer.
    Writes the Manim scene code, using archetype-specific hints from the Architect.
    """
    print("---NODE C: DEVELOPER---")
    user_input = state["user_input"]
    math_solution = state.get("math_solution", "")
    archetype = state.get("archetype", "general")

    # 0. Use proven code from memory if available
    if state.get("proven_code"):
        print("Developer: Using proven code from memory.")
        return {"manim_code": state["proven_code"]}

    retrieved_docs = "\n\n".join(state.get("retrieved_docs", []))
    hint = ARCHETYPE_HINTS.get(archetype, "Create a clear, educational Manim animation.")

    previous_error = state.get("error_log")
    if previous_error:
        print(f"Developer: Fixing previous error (attempt {state.get('attempt_count', 0)}): {previous_error}")
        prompt = f"""You are a CODE FIXER AGENT for Manim animations.

        Original Task: {user_input}
        Error to Fix:
        {previous_error}

        Archetype Hint ({archetype.upper()}):
        {hint}

        Rules:
        - Use MathTex() for all math. Never use Tex() with ^, _, or backslash commands.
        - Class must be named MathScene.
        - Shapes should NOT exceed screen height 6. Use scale_to_fit_height(5) if needed.
        - No input(), no interactivity.

        Output ONLY the fixed Python code.
        """
    else:
        prompt = f"""You are an Elite Manim (Community) Developer.

        Goal: Create an EDUCATIONAL animation for: "{user_input}"

        Math Context:
        {math_solution}

        Manim Docs Reference:
        {retrieved_docs}

        Archetype ({archetype.upper()}) - follow these hints precisely:
        {hint}

        --- LAYOUT RULES ---
        1. Use MathTex for all equations. NEVER use Tex() with math symbols.
        2. Use Text() only for titles/plain labels (no math symbols).
        3. Keep all objects within the screen. Use VGroup with buff=0.5.
        4. Add self.wait(1) after each important animation.

        --- TECHNICAL RULES ---
        1. Class name: MathScene. Import: from manim import *
        2. Never add scalars to Manim vectors. Use .get_center(), .get_right() etc.
        3. No input() or interactive calls.

        Output ONLY the raw Python code. No markdown, no explanation.
        """

    print("Developer: Prompting LLM for Manim code...")
    response = llm.invoke([SystemMessage(content=prompt)])
    print("Developer: LLM generation complete.")
    code = response.content.strip().replace("```python", "").replace("```", "")

    return {"manim_code": code}
