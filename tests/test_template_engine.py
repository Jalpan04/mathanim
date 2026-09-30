import ast
import pytest
from app.services.template_engine import TemplateEngine
from app.services.validator import RenderValidator


def test_quadrilateral_construction():
    prompt = "Construct a quadrilateral ABCD where AB = 4.5 cm BC = 5.5 cm CD = 4 cm AD = 6 cm AC = 7 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    assert "class MathScene(Scene):" in code
    assert "Polygon" in code
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_rhombus_construction():
    prompt = "Construct a rhombus BEND where BN = 5.6 cm and DE = 6.5 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    assert "class MathScene(Scene):" in code
    assert "Polygon" in code
    assert code.count("self.play") >= 10
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_triangle_construction():
    prompt = "Construct a triangle ABC with AB = 5 cm, BC = 6 cm, CA = 7 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_quadratic_equation_explicit_mult():
    prompt = "Solve quadratic equation 2*x^2 + 5*x - 3 = 0"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_quadratic_equation_implicit_mult():
    prompt = "Solve quadratic equation 2x^2 + 5x - 3 = 0"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_linear_equation():
    prompt = "Solve linear equation 3x + 7 = 22"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_calculus_integral():
    prompt = "Find the integral of x^2 from 0 to 3"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "calculus"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_function_graphing():
    prompt = "Plot the graph of y = x^2 - 4"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "graphing"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_geometry_circle_area():
    prompt = "Find the area of a circle with radius 5"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_number_line():
    prompt = "Show 3 + 4 on number line"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "number_line"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_angle_construction():
    prompt = "Construct an angle of 60 degrees and bisect it"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_pythagoras():
    prompt = "Find hypotenuse using pythagorean theorem for legs 3 and 4"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_vector_addition():
    prompt = "Add vectors u = [3, 1] and v = [1, 3]"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_system_of_equations():
    prompt = "Solve system of equations 2*x + y = 7 and x - y = 1"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_derivative_tangent():
    prompt = "Find derivative and tangent line of y = x^2 at x = 2"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "calculus"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_square_construction():
    prompt = "Construct a square READ with side 5.1 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_rectangle_construction():
    prompt = "Construct a rectangle ABCD with AB = 5 cm and BC = 3 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_parallelogram_construction_with_angle():
    prompt = "Construct a parallelogram ABCD where AB = 6 cm, BC = 4 cm and angle B = 60 degrees"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_parallelogram_construction_with_diagonal():
    prompt = "Construct a parallelogram MORE where OR = 6 cm, RE = 4.5 cm, EO = 7.5 cm"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_circle_tangent_construction():
    prompt = "Draw a circle of radius 4 cm. From a point 10 cm away from its centre, construct the pair of tangents to the circle"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "geometry"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_arithmetic_progression():
    prompt = "Find the 10th term and sum of first 10 terms of AP: 2, 5, 8, 11..."
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "sequence"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_matrix_determinant():
    prompt = "Calculate the determinant of matrix [[3, 2], [1, 4]]"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is not None
    code, solution, archetype = result
    assert archetype == "equation"
    ast.parse(code)
    errors = RenderValidator.validate(code)
    assert errors == []


def test_unmatched_query_falls_back():
    prompt = "Explain quantum entanglement using animated particles"
    result = TemplateEngine.match_and_generate(prompt)
    assert result is None

