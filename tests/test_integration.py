import unittest
import shutil
import subprocess
import ast
import sympy
from app.services.validator import RenderValidator
from app.services.hybrid_router import route_and_generate
from app.agents.graph import define_graph


class TestMathAnimIntegration(unittest.TestCase):

    def test_01_manim_environment(self):
        """Test if the Manim executable is available in the environment."""
        manim_bin = shutil.which("manim")
        self.assertIsNotNone(manim_bin, "Manim executable not found in PATH")
        res = subprocess.run([manim_bin, "--version"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Manim Community", res.stdout)

    def test_02_sympy_computations(self):
        """Test in-process SymPy computation support."""
        x = sympy.Symbol('x')
        expr = 2 * x + 5
        solution = sympy.solve(sympy.Eq(expr, 15), x)
        self.assertEqual(solution, [5])

    def test_03_critic_autofix_and_validation(self):
        """Test RenderValidator AST validation and autofix routines."""
        broken_code = r"""
from manim import *
class QuadraticScene(Scene):
    def construct(self):
        t = MathTex(r"Title \( x^2 \)")
        self.play(Write(t))
"""
        fixed_code = RenderValidator.autofix(broken_code)
        self.assertIn("class MathScene", fixed_code)
        self.assertNotIn(r"\(", fixed_code)

        errors = RenderValidator.validate(fixed_code)
        self.assertEqual(len(errors), 0, f"Unexpected validation errors: {errors}")

    def test_04_hybrid_router_classification(self):
        """Test archetype classification on curriculum topics."""
        _, archetype_graph = route_and_generate("Graph y = x^2 - 4")
        self.assertEqual(archetype_graph, "graphing")

        _, archetype_geom = route_and_generate("Find the area of a circle with radius 5")
        self.assertEqual(archetype_geom, "geometry")

        _, archetype_eq = route_and_generate("Solve 3x + 10 = 25 step by step")
        self.assertEqual(archetype_eq, "equation")

    def test_05_agent_graph_compilation(self):
        """Test that the LangGraph workflow compiles cleanly."""
        graph_app = define_graph()
        self.assertIsNotNone(graph_app)


if __name__ == '__main__':
    unittest.main()
