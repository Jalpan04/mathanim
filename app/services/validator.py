import re
import ast


class RenderValidator:
    """
    Pre-flight validation layer. Runs BEFORE any generated code is sent to Docker.
    Catches common failure patterns that would cause Manim rendering errors.
    """

    # Matches Tex() calls with math symbols inside (should be MathTex)
    LATEX_VIOLATIONS = re.compile(
        r'Tex\s*\(\s*["\'].*?(\\[a-zA-Z]+|[_^{}\$]).*?["\']'
    )

    # Matches raw radius values that would overflow the screen (Manim frame h=8)
    OVERSIZE_RADIUS = re.compile(r'radius\s*=\s*(\d+(?:\.\d+)?)')

    # Matches scale() calls with very large values
    OVERSIZE_SCALE = re.compile(r'\.scale\s*\(\s*(\d+(?:\.\d+)?)\s*\)')

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
            # Stop here - further checks are unreliable on broken code
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
                    "Add 'shape.scale_to_fit_height(5)' after creation."
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
                "The renderer expects exactly this class name."
            )

        # 6. Must import manim
        if "from manim import" not in code and "import manim" not in code:
            errors.append(
                "IMPORT_ERROR: Missing 'from manim import *'."
            )

        return errors
