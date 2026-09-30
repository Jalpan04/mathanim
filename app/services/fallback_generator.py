from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.services.latex_sanitizer import sanitize_latex

llm = get_llm(temperature=0.1)


def generate_fallback_code(prompt: str) -> str:
    """
    Generates a minimal, robust Manim code script when main agents fail.
    """
    print(f"Fallback Generator: Generating fallback animation for '{prompt}'")

    try:
        base_system_prompt = """You are an expert Manim (Community Version) developer.
Write a COMPLETE, MINIMAL, RUNNABLE Python script using Manim to visualize the user's math request.

Rules:
1. Class name MUST be `MathScene(Scene):`.
2. Use `from manim import *`.
3. Do NOT use markdown backticks. Output raw Python code only.
4. Keep the animation simple, robust, and clean.
5. Use MathTex(r"...") for formulas.
"""
        response = llm.invoke([
            SystemMessage(content=base_system_prompt),
            HumanMessage(content=f"Create a Manim visualization for: {prompt}")
        ])

        raw = response.content.strip().replace("```python", "").replace("```", "").strip()
        code = sanitize_latex(raw)

        if "class MathScene" not in code:
            raise ValueError("Generated fallback missing MathScene class.")

        if "from manim import *" not in code:
            code = "from manim import *\n" + code

        return code

    except Exception as e:
        print(f"Fallback Generator Error: {e}")
        escaped_prompt = prompt.replace('"', '\\"')[:50]
        return f"""from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("MathAnim", font_size=40, color=BLUE).to_edge(UP)
        problem = Text("{escaped_prompt}", font_size=24, color=WHITE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(FadeIn(problem))
        self.wait(2)
"""
