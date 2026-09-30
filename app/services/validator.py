import re
import ast


class RenderValidator:
    """
    Pre-flight validation and autofix layer. Runs BEFORE code is rendered.
    Catches and corrects common failure patterns that would cause Manim rendering errors.
    """

    # Matches Tex() calls (not MathTex) with math symbols inside
    LATEX_VIOLATIONS = re.compile(
        r'\bTex\s*\(\s*["\'].*?(\\[a-zA-Z]+|[_^{}\$]).*?["\']'
    )

    # Matches raw radius values that would overflow the screen (Manim frame h=8)
    OVERSIZE_RADIUS = re.compile(r'radius\s*=\s*(\d+(?:\.\d+)?)')

    # Matches scale() calls with very large values
    OVERSIZE_SCALE = re.compile(r'\.scale\s*\(\s*(\d+(?:\.\d+)?)\s*\)')

    # Matches y_range with None as second element
    NONE_YRANGE = re.compile(r'y_range\s*=\s*\[.*?None.*?\]')

    @classmethod
    def autofix(cls, code: str) -> str:
        """Attempts safe, deterministic auto-corrections on the code."""
        # 1. Ensure from manim import * is present
        if "from manim import *" not in code and "import manim" not in code:
            code = "from manim import *\n" + code

        # 2. Fix class name if user created a different Scene class
        if "class MathScene(" not in code:
            # Look for any class inheriting from Scene or ThreeDScene
            code = re.sub(r'class\s+([A-Za-z0-9_]+)\s*\(\s*(ThreeDScene|Scene)\s*\):', r'class MathScene(\2):', code, count=1)

        # 3. Replace Tex(r"...") with MathTex(r"...") if math symbols are found
        code = re.sub(r'\bTex\s*\((\s*r?["\'].*?(\\[a-zA-Z]+|[_^{}\$]).*?["\']\s*)\)', r'MathTex(\1)', code)

        # 4. Strip \( and \) inside MathTex expressions (since MathTex is already in math mode)
        def _clean_mathtex_delims(m):
            inner = m.group(1)
            cleaned = inner.replace(r"\(", "").replace(r"\)", "").replace("$", "")
            return f"MathTex({cleaned})"
        code = re.sub(r'\bMathTex\s*\((.*?)\)', _clean_mathtex_delims, code)

        # 5. Convert bare static self.add(...) into animated self.play(...)
        def _convert_self_add(m):
            args = m.group(1).strip()
            if "," in args:
                return f"self.play(FadeIn(VGroup({args})))"
            return f"self.play(Create({args}))"
        code = re.sub(r'\bself\.add\s*\((.*?)\)', _convert_self_add, code)

        return code

    @classmethod
    def validate(cls, code: str) -> list[str]:
        """
        Returns a list of error strings. Empty list = valid code.
        """
        errors = []

        # 1. Python AST syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
            return errors

        # 2. LaTeX guard: Tex() should not contain raw math symbols
        if cls.LATEX_VIOLATIONS.search(code):
            errors.append(
                "LATEX_ERROR: Found Tex() with math symbols. "
                "Use MathTex() for expressions containing \\, ^, _, or {}."
            )

        # 3. Oversize shape guard
        for match in cls.OVERSIZE_RADIUS.finditer(code):
            val = float(match.group(1))
            if val > 3.5:
                errors.append(
                    f"OVERSIZE_ERROR: radius={val} may exceed screen bounds (max ~3.5). "
                    "Scale the shape or reduce radius."
                )

        # 4. Oversize scale guard
        for match in cls.OVERSIZE_SCALE.finditer(code):
            val = float(match.group(1))
            if val > 4.0:
                errors.append(
                    f"OVERSIZE_ERROR: .scale({val}) may push objects off-screen."
                )

        # 5. Must define MathScene class
        if "class MathScene" not in code:
            errors.append(
                "STRUCTURE_ERROR: Missing 'class MathScene(Scene):'. "
                "The renderer expects this class name."
            )

        # 6. Must import manim
        if "from manim import" not in code and "import manim" not in code:
            errors.append(
                "IMPORT_ERROR: Missing 'from manim import *'."
            )

        # 7. y_range=None guard
        if cls.NONE_YRANGE.search(code):
            errors.append(
                "AXES_ERROR: y_range contains None. Provide explicit numeric bounds."
            )

        # 8. Hallucinated .get_label() on shapes
        if ".get_label(" in code:
            if not re.search(r'(axes|axis|line|number_line)\.get_label', code, re.I):
                errors.append(
                    "HALLUCINATION_ERROR: Found '.get_label()' on a non-axis shape. "
                    "Use MathTex(r'...').next_to(object) instead."
                )

        # 9. Static video guard: flag if scene uses bare self.add with no self.play animations
        if re.search(r'\bself\.add\s*\(', code) and not re.search(r'\bself\.play\s*\(', code):
            errors.append(
                "ANIMATION_ERROR: Scene uses bare self.add() with no animations. "
                "Animate elements step-by-step using self.play(Create(...)), self.play(Write(...)), etc."
            )

        return errors
