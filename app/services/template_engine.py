import re
import math
from typing import Optional, Tuple, Dict, Any, List
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import numpy as np

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _parse_math_expr(s: str):
    clean = s.strip().replace("^", "**")
    return parse_expr(clean, transformations=_TRANSFORMATIONS)


class TemplateEngine:
    """
    Deterministic Manim Template Engine.
    Matches mathematical problem archetypes, extracts parameters,
    solves geometric coordinates and algebraic steps with SymPy,
    and slots values into verified, bug-free Manim Community templates.
    """

    @classmethod
    def match_and_generate(cls, user_input: str) -> Optional[Tuple[str, str, str]]:
        """
        Attempts to match the user input against all registered templates.
        Returns (manim_code, math_solution, archetype) if matched, else None.
        """
        lower = user_input.lower().strip()

        # 1. Rhombus Construction (Diagonals)
        rhombus_match = cls._match_rhombus_construction(user_input, lower)
        if rhombus_match:
            return rhombus_match

        # 2. Parallelogram / Rectangle / Square Construction
        para_match = cls._match_parallelogram_construction(user_input, lower)
        if para_match:
            return para_match

        # 3. Circle Tangent Construction
        circle_tan_match = cls._match_circle_tangent_construction(user_input, lower)
        if circle_tan_match:
            return circle_tan_match

        # 4. Arithmetic Progression
        ap_match = cls._match_arithmetic_progression(user_input, lower)
        if ap_match:
            return ap_match

        # 5. Matrix Determinant
        matrix_match = cls._match_matrix_determinant(user_input, lower)
        if matrix_match:
            return matrix_match

        # 2. Angle Construction / Bisector
        angle_match = cls._match_angle_construction(user_input, lower)
        if angle_match:
            return angle_match

        # 3. Pythagorean Theorem
        pythagoras_match = cls._match_pythagoras(user_input, lower)
        if pythagoras_match:
            return pythagoras_match

        # 4. Vector Addition
        vector_match = cls._match_vector_addition(user_input, lower)
        if vector_match:
            return vector_match

        # 5. System of 2 Linear Equations
        system_match = cls._match_system_of_equations(user_input, lower)
        if system_match:
            return system_match

        # 6. Derivative and Tangent Line
        tangent_match = cls._match_derivative_tangent(user_input, lower)
        if tangent_match:
            return tangent_match

        # 7. Quadrilateral Construction (Sides + Diagonal)
        quad_match = cls._match_quadrilateral_construction(user_input, lower)
        if quad_match:
            return quad_match

        # 8. Triangle Construction
        tri_match = cls._match_triangle_construction(user_input, lower)
        if tri_match:
            return tri_match

        # 9. Quadratic Equation Solver
        quad_eq_match = cls._match_quadratic_equation(user_input, lower)
        if quad_eq_match:
            return quad_eq_match

        # 10. Linear Equation Solver
        lin_eq_match = cls._match_linear_equation(user_input, lower)
        if lin_eq_match:
            return lin_eq_match

        # 11. Definite Integral / Area under curve
        calc_match = cls._match_calculus_integral(user_input, lower)
        if calc_match:
            return calc_match

        # 12. Function Graphing
        graph_match = cls._match_function_graph(user_input, lower)
        if graph_match:
            return graph_match

        # 7. Area & Perimeter of 2D Shapes
        geom_match = cls._match_geometry_area_perimeter(user_input, lower)
        if geom_match:
            return geom_match

        # 8. Number Line Operations
        num_line_match = cls._match_number_line(user_input, lower)
        if num_line_match:
            return num_line_match

        return None

    # ----------------------------------------------------------------------
    # 0. RHOMBUS CONSTRUCTION TEMPLATE (Two Diagonals)
    # ----------------------------------------------------------------------
    @classmethod
    def _match_rhombus_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("rhombus" in lower or ("diagonal" in lower and ("construct" in lower or "draw" in lower))):
            return None

        pairs = re.findall(r"([A-Za-z]{1,2})\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if len(pairs) < 2:
            return None

        if len(pairs) >= 4:
            return None

        d1_name, d1_val_s = pairs[0]
        d2_name, d2_val_s = pairs[1]
        d1_val = float(d1_val_s)
        d2_val = float(d2_val_s)
        if d1_val <= 0 or d2_val <= 0:
            return None

        name_match = re.search(r"rhombus\s+([A-Za-z]{4})", text, re.IGNORECASE)
        if name_match:
            v_names = name_match.group(1).upper()
            vB, vE, vN, vD = v_names[0], v_names[1], v_names[2], v_names[3]
        else:
            vB, vE, vN, vD = "B", "E", "N", "D"

        scale = min(5.5 / max(d1_val, 0.1), 4.2 / max(d2_val, 0.1), 3.0 / max(d1_val, d2_val))
        O = np.array([0.0, -0.3, 0.0])
        pB = np.round(O + np.array([-d1_val / 2.0 * scale, 0.0, 0.0]), 3)
        pN = np.round(O + np.array([d1_val / 2.0 * scale, 0.0, 0.0]), 3)
        pD = np.round(O + np.array([0.0, d2_val / 2.0 * scale, 0.0]), 3)
        pE = np.round(O + np.array([0.0, -d2_val / 2.0 * scale, 0.0]), 3)

        half_d2 = d2_val / 2.0
        r_bisect = round((d1_val / 2.0 + 0.6) * scale, 3)
        r_half = round(half_d2 * scale, 3)
        bisector_h = round(half_d2 * scale + 0.6, 3)
        bisector_top = np.round(O + np.array([0.0, bisector_h, 0.0]), 3)
        bisector_bot = np.round(O + np.array([0.0, -bisector_h, 0.0]), 3)

        side_len = math.sqrt((d1_val / 2.0)**2 + (half_d2)**2)

        math_solution = f"""Rhombus {vB}{vE}{vN}{vD} Construction Plan:
Given diagonals: {d1_name.upper()} = {d1_val} cm, {d2_name.upper()} = {d2_val} cm.
Property: The diagonals of a rhombus bisect each other at right angles (90 degrees).
1. Draw diagonal {d1_name.upper()} = {d1_val} cm horizontally.
2. Draw the perpendicular bisector of {d1_name.upper()} intersecting at midpoint O.
3. From O, cut arcs of length {d2_val}/2 = {half_d2:.2f} cm on both sides of the bisector to locate vertices {vD} and {vE}.
4. Join {vB}{vE}, {vE}{vN}, {vN}{vD}, and {vD}{vB} to form rhombus {vB}{vE}{vN}{vD}.
Side length = sqrt(({d1_val}/2)^2 + ({half_d2:.2f})^2) = {side_len:.2f} cm.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing Rhombus {vB}{vE}{vN}{vD}", font_size=32).to_edge(UP)
        given_text = MathTex(
            r"\\text{{Given diagonals: }} {d1_name.upper()} = {d1_val}\\text{{ cm}},\\ {d2_name.upper()} = {d2_val}\\text{{ cm}}",
            font_size=24, color=GRAY_A
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        O = np.array({list(O)})
        pB = np.array({list(pB)})
        pN = np.array({list(pN)})
        pD = np.array({list(pD)})
        pE = np.array({list(pE)})

        # Step 1: Draw base diagonal
        step_banner = Text("Step 1: Draw diagonal {d1_name.upper()} = {d1_val} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        dotB = Dot(pB, color=BLUE)
        dotN = Dot(pN, color=BLUE)
        lblB = MathTex(r"{vB}", font_size=26).next_to(dotB, LEFT, buff=0.12)
        lblN = MathTex(r"{vN}", font_size=26).next_to(dotN, RIGHT, buff=0.12)
        lineBN = DashedLine(pB, pN, color=BLUE_B, dash_length=0.15)
        lblBN = MathTex(r"{d1_name.upper()} = {d1_val}\\text{{ cm}}", font_size=20, color=BLUE_A).next_to(lineBN, UP, buff=0.1)

        self.play(Write(step_banner), Create(dotB), Write(lblB), Create(dotN), Write(lblN))
        self.play(Create(lineBN), Write(lblBN))
        self.wait(0.8)

        # Step 2: Perpendicular bisector
        self.play(Transform(step_banner, Text("Step 2: Draw arcs from {vB} and {vN} to construct perpendicular bisector", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_top_B = Arc(radius={r_bisect}, start_angle=0.6, angle=0.6, arc_center=pB, color=TEAL)
        arc_top_N = Arc(radius={r_bisect}, start_angle=1.9, angle=0.6, arc_center=pN, color=TEAL)
        arc_bot_B = Arc(radius={r_bisect}, start_angle=-1.2, angle=0.6, arc_center=pB, color=TEAL)
        arc_bot_N = Arc(radius={r_bisect}, start_angle=-2.5, angle=0.6, arc_center=pN, color=TEAL)

        self.play(Create(arc_top_B), Create(arc_top_N))
        self.play(Create(arc_bot_B), Create(arc_bot_N))

        bisector_line = DashedLine(np.array({list(bisector_bot)}), np.array({list(bisector_top)}), color=PURPLE, dash_length=0.12)
        dotO = Dot(O, color=WHITE, radius=0.07)
        lblO = MathTex(r"O", font_size=22).next_to(dotO, DL, buff=0.08)

        self.play(Create(bisector_line), Create(dotO), Write(lblO))
        self.wait(0.8)

        # Step 3: Locate remaining vertices along perpendicular bisector
        self.play(Transform(step_banner, Text("Step 3: From O, cut arcs of {half_d2:.2f} cm (half of {d2_name.upper()}) to mark {vD} and {vE}", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_D = Arc(radius={r_half}, start_angle=1.2, angle=0.7, arc_center=O, color=ORANGE)
        arc_E = Arc(radius={r_half}, start_angle=-1.9, angle=0.7, arc_center=O, color=ORANGE)
        self.play(Create(arc_D), Create(arc_E))

        dotD = Dot(pD, color=RED)
        dotE = Dot(pE, color=RED)
        lblD = MathTex(r"{vD}", font_size=26).next_to(dotD, UP, buff=0.12)
        lblE = MathTex(r"{vE}", font_size=26).next_to(dotE, DOWN, buff=0.12)
        lblDE = MathTex(r"{d2_name.upper()} = {d2_val}\\text{{ cm}}", font_size=20, color=PURPLE_A).next_to(pD, RIGHT, buff=0.2)

        self.play(Create(dotD), Write(lblD), Create(dotE), Write(lblE), Write(lblDE))
        self.wait(0.8)

        # Step 4: Join sides
        self.play(Transform(step_banner, Text("Step 4: Connect vertices {vB}-{vE}-{vN}-{vD} to complete the rhombus", font_size=20, color=YELLOW).to_edge(DOWN)))
        side_BE = Line(pB, pE, color=YELLOW, stroke_width=3)
        side_EN = Line(pE, pN, color=YELLOW, stroke_width=3)
        side_ND = Line(pN, pD, color=YELLOW, stroke_width=3)
        side_DB = Line(pD, pB, color=YELLOW, stroke_width=3)

        self.play(Create(side_BE), Create(side_EN))
        self.play(Create(side_ND), Create(side_DB))
        self.wait(0.5)

        # Highlight final shape
        rhombus_poly = Polygon(pB, pE, pN, pD, color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, stroke_width=4)
        self.play(
            FadeOut(arc_top_B), FadeOut(arc_top_N),
            FadeOut(arc_bot_B), FadeOut(arc_bot_N),
            FadeOut(arc_D), FadeOut(arc_E),
            Create(rhombus_poly)
        )
        self.play(Transform(step_banner, Text("Rhombus {vB}{vE}{vN}{vD} Constructed Successfully", font_size=22, color=GREEN_B).to_edge(DOWN)))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # ANGLE CONSTRUCTION AND BISECTOR TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_angle_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("angle" in lower and ("construct" in lower or "bisect" in lower or "draw" in lower)):
            return None

        deg_match = re.search(r"([0-9]+)\s*(?:deg|degree|°)", lower)
        deg = float(deg_match.group(1)) if deg_match else 60.0
        rad = math.radians(deg)

        O = np.array([-2.5, -1.0, 0.0])
        r_base = 4.5
        pA = O + np.array([r_base, 0.0, 0.0])
        pB = O + np.array([r_base * math.cos(rad), r_base * math.sin(rad), 0.0])

        math_solution = f"""Angle Construction and Bisection Plan:
Target Angle: {deg:g} degrees.
1. Draw base ray OA.
2. With center O and convenient radius, draw circular arc cutting OA at P.
3. Draw arc from P intersecting main arc at Q to establish angle of {deg:g} degrees.
4. Draw ray OB through Q.
5. Draw arcs from P and Q intersecting at R. Ray OR bisects angle AOB into two equal {deg/2:g}-degree angles.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing and Bisecting Angle ({deg:g} deg)", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        O = np.array({list(np.round(O, 3))})
        pA = np.array({list(np.round(pA, 3))})
        pB = np.array({list(np.round(pB, 3))})

        # Step 1: Base ray OA
        step_banner = Text("Step 1: Draw base ray OA", font_size=20, color=YELLOW).to_edge(DOWN)
        dotO = Dot(O, color=BLUE)
        lblO = MathTex(r"O", font_size=26).next_to(dotO, DL, buff=0.1)
        rayOA = Line(O, pA, color=BLUE, stroke_width=4)
        lblA = MathTex(r"A", font_size=26).next_to(pA, RIGHT, buff=0.1)

        self.play(Write(step_banner), Create(dotO), Write(lblO), Create(rayOA), Write(lblA))
        self.wait(0.8)

        # Step 2: Main arc from O
        self.play(Transform(step_banner, Text("Step 2: Draw circular arc from center O", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_main = Arc(radius=2.2, start_angle=0, angle={round(rad + 0.35, 3)}, arc_center=O, color=TEAL)
        self.play(Create(arc_main))
        self.wait(0.5)

        # Step 3: Draw Ray OB forming angle
        self.play(Transform(step_banner, Text("Step 3: Draw ray OB forming {deg:g}-degree angle", font_size=20, color=YELLOW).to_edge(DOWN)))
        rayOB = Line(O, pB, color=YELLOW, stroke_width=4)
        lblB = MathTex(r"B", font_size=26).next_to(pB, UR, buff=0.1)
        self.play(Create(rayOB), Write(lblB))
        self.wait(0.8)

        # Step 4: Bisector ray
        self.play(Transform(step_banner, Text("Step 4: Draw bisector ray cutting angle into two equal halves", font_size=20, color=YELLOW).to_edge(DOWN)))
        half_rad = {round(rad / 2.0, 3)}
        p_bisect = O + np.array([4.2 * np.cos(half_rad), 4.2 * np.sin(half_rad), 0.0])
        ray_bisect = DashedLine(O, p_bisect, color=GREEN, dash_length=0.15)
        lbl_half = MathTex(r"{deg/2:g}^\\circ", font_size=22, color=GREEN).next_to(O + np.array([1.5 * np.cos(half_rad), 1.5 * np.sin(half_rad), 0.0]), UR, buff=0.08)

        self.play(Create(ray_bisect), Write(lbl_half))
        self.play(Transform(step_banner, Text("Angle Constructed and Bisected Successfully", font_size=22, color=GREEN_B).to_edge(DOWN)))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # PYTHAGOREAN THEOREM TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_pythagoras(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("pythagor" in lower or "hypotenuse" in lower or ("right" in lower and "triangle" in lower)):
            return None

        nums = [float(n) for n in re.findall(r"([0-9]+(?:\.[0-9]+)?)", text)]
        if len(nums) < 2:
            return None

        a = nums[0]
        b = nums[1]
        c = math.sqrt(a**2 + b**2)
        c_str = f"{c:g}" if c == int(c) else f"{c:.2f}"

        max_dim = max(a, b)
        scale = min(3.8 / max(max_dim, 0.1), 3.0 / max(b, 0.1))
        pC = np.array([-3.5, -1.8, 0.0])
        pB = pC + np.array([a * scale, 0.0, 0.0])
        pA = pC + np.array([0.0, b * scale, 0.0])

        math_solution = f"""Pythagorean Theorem Solution:
Right Triangle with legs a = {a:g} and b = {b:g}.
Formula: a^2 + b^2 = c^2
Substitution: ({a:g})^2 + ({b:g})^2 = {a**2:g} + {b**2:g} = {a**2 + b**2:g}
Hypotenuse c = sqrt({a**2 + b**2:g}) = {c_str}.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Pythagorean Theorem: a^2 + b^2 = c^2", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        pC = np.array({list(np.round(pC, 3))})
        pB = np.array({list(np.round(pB, 3))})
        pA = np.array({list(np.round(pA, 3))})

        leg_a = Line(pC, pB, color=BLUE, stroke_width=4)
        leg_b = Line(pC, pA, color=BLUE, stroke_width=4)
        lbl_a = MathTex(r"a = {a:g}", font_size=26, color=BLUE_A).next_to(leg_a, DOWN, buff=0.15)
        lbl_b = MathTex(r"b = {b:g}", font_size=26, color=BLUE_A).next_to(leg_b, LEFT, buff=0.15)

        self.play(Create(leg_a), Write(lbl_a))
        self.play(Create(leg_b), Write(lbl_b))
        self.wait(0.5)

        corner_size = 0.35
        ra_h = Line(pC + UP * corner_size, pC + UP * corner_size + RIGHT * corner_size, color=WHITE)
        ra_v = Line(pC + RIGHT * corner_size, pC + UP * corner_size + RIGHT * corner_size, color=WHITE)
        self.play(Create(ra_h), Create(ra_v))

        hyp = Line(pA, pB, color=YELLOW, stroke_width=5)
        lbl_c = MathTex(r"c = {c_str}", font_size=28, color=YELLOW).next_to(hyp.get_center(), UR, buff=0.1)
        self.play(Create(hyp), Write(lbl_c))
        self.wait(0.8)

        f1 = MathTex(r"a^2 + b^2 = c^2", font_size=32, color=YELLOW)
        f2 = MathTex(r"({a:g})^2 + ({b:g})^2 = c^2", font_size=30, color=BLUE_B)
        f3 = MathTex(r"{a**2:g} + {b**2:g} = {a**2 + b**2:g} = c^2", font_size=30, color=TEAL)
        f4 = MathTex(r"c = \\sqrt{{{a**2 + b**2:g}}} = {c_str}", font_size=34, color=GREEN)
        box = SurroundingRectangle(f4, color=GREEN, buff=0.15)

        formula_group = VGroup(f1, f2, f3, f4).arrange(DOWN, buff=0.4, aligned_edge=LEFT).shift(RIGHT * 2.5 + DOWN * 0.2)

        self.play(Write(f1))
        self.wait(0.5)
        self.play(Write(f2))
        self.wait(0.5)
        self.play(Write(f3))
        self.wait(0.5)
        self.play(Write(f4), Create(box))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # VECTOR ADDITION TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_vector_addition(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("vector" in lower and ("add" in lower or "sum" in lower or "+" in lower or "resultant" in lower)):
            return None

        vec_matches = re.findall(r"[\[\(]\s*([+-]?[0-9.]+)\s*[,;\s]\s*([+-]?[0-9.]+)\s*[\]\)]", text)
        if len(vec_matches) < 2:
            return None

        u_x, u_y = float(vec_matches[0][0]), float(vec_matches[0][1])
        v_x, v_y = float(vec_matches[1][0]), float(vec_matches[1][1])
        w_x, w_y = u_x + v_x, u_y + v_y

        math_solution = f"""Vector Addition (Head-to-Tail & Parallelogram):
Vector u = [{u_x:g}, {u_y:g}]
Vector v = [{v_x:g}, {v_y:g}]
Resultant w = u + v = [{u_x:g} + {v_x:g}, {u_y:g} + {v_y:g}] = [{w_x:g}, {w_y:g}].
Magnitude |w| = sqrt(({w_x:g})^2 + ({w_y:g})^2) = {math.sqrt(w_x**2 + w_y**2):.2f}.
"""

        all_x = [0, u_x, v_x, w_x]
        all_y = [0, u_y, v_y, w_y]
        x_min, x_max = min(all_x) - 1, max(all_x) + 2
        y_min, y_max = min(all_y) - 1, max(all_y) + 2

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Vector Addition: \\vec{{u}} + \\vec{{v}} = \\vec{{w}}", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        axes = Axes(
            x_range=[{int(x_min)}, {int(x_max)}, 1],
            y_range=[{int(y_min)}, {int(y_max)}, 1],
            x_length=7,
            y_length=4.5,
            axis_config={{"include_tip": True, "font_size": 18}}
        ).shift(LEFT * 1.5 + DOWN * 0.3)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))
        self.wait(0.5)

        p_origin = axes.c2p(0, 0)
        p_u = axes.c2p({u_x}, {u_y})
        p_w = axes.c2p({w_x}, {w_y})

        vec_u = Arrow(p_origin, p_u, buff=0, color=BLUE, stroke_width=4)
        lbl_u = MathTex(r"\\vec{{u}} = \\begin{{bmatrix}} {u_x:g} \\\\ {u_y:g} \\end{{bmatrix}}", font_size=24, color=BLUE_A).next_to(p_u, UL, buff=0.1)
        self.play(GrowArrow(vec_u), Write(lbl_u))
        self.wait(0.5)

        vec_v = Arrow(p_u, p_w, buff=0, color=TEAL, stroke_width=4)
        lbl_v = MathTex(r"\\vec{{v}} = \\begin{{bmatrix}} {v_x:g} \\\\ {v_y:g} \\end{{bmatrix}}", font_size=24, color=TEAL_A).next_to(p_w, UR, buff=0.1)
        self.play(GrowArrow(vec_v), Write(lbl_v))
        self.wait(0.5)

        vec_w = Arrow(p_origin, p_w, buff=0, color=YELLOW, stroke_width=5)
        lbl_w = MathTex(r"\\vec{{w}} = \\begin{{bmatrix}} {w_x:g} \\\\ {w_y:g} \\end{{bmatrix}}", font_size=26, color=YELLOW).next_to(vec_w.get_center(), DR, buff=0.15)
        self.play(GrowArrow(vec_w), Write(lbl_w))
        self.wait(0.8)

        f_sum = MathTex(
            r"\\vec{{w}} = \\begin{{bmatrix}} {u_x:g} + {v_x:g} \\\\ {u_y:g} + {v_y:g} \\end{{bmatrix}} = \\begin{{bmatrix}} {w_x:g} \\\\ {w_y:g} \\end{{bmatrix}}",
            font_size=28, color=GREEN
        ).shift(RIGHT * 4.0 + DOWN * 0.3)
        box = SurroundingRectangle(f_sum, color=GREEN, buff=0.15)
        self.play(Write(f_sum), Create(box))
        self.wait(2)
'''
        return manim_code, math_solution, "equation"

    # ----------------------------------------------------------------------
    # SYSTEM OF 2 LINEAR EQUATIONS TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_system_of_equations(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("system" in lower or ("and" in lower and "=" in text and "x" in lower and "y" in lower)):
            return None

        eq_matches = re.findall(r"([0-9xy\^\*\+\-\/\s\(\)]+=[0-9xy\^\*\+\-\/\s\(\)]+)", text)
        if len(eq_matches) < 2:
            return None

        x, y = sp.symbols("x y")
        try:
            lhs1, rhs1 = eq_matches[0].split("=")
            lhs2, rhs2 = eq_matches[1].split("=")
            e1 = sp.Eq(_parse_math_expr(lhs1), _parse_math_expr(rhs1))
            e2 = sp.Eq(_parse_math_expr(lhs2), _parse_math_expr(rhs2))
            sol = sp.solve((e1, e2), (x, y))
            if not sol:
                return None
            sol_x = sol[x]
            sol_y = sol[y]
            num_x = float(sol_x)
            num_y = float(sol_y)
        except Exception:
            return None

        e1_latex = sp.latex(e1)
        e2_latex = sp.latex(e2)
        sol_x_latex = sp.latex(sol_x)
        sol_y_latex = sp.latex(sol_y)

        math_solution = f"""System of 2 Linear Equations Solution:
Equation (1): {e1_latex}
Equation (2): {e2_latex}
1. Solve algebraically by substitution / elimination:
   x = {sol_x_latex}, y = {sol_y_latex}
2. Graphical interpretation:
   The two lines intersect at unique point ({sol_x_latex}, {sol_y_latex}).
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Solving System of Linear Equations", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        eq1_tex = MathTex(r"(1)\\quad {e1_latex}", font_size=30, color=BLUE_B)
        eq2_tex = MathTex(r"(2)\\quad {e2_latex}", font_size=30, color=TEAL_B)
        eq_group = VGroup(eq1_tex, eq2_tex).arrange(DOWN, buff=0.3, aligned_edge=LEFT).shift(LEFT * 3.5 + UP * 1.5)

        self.play(Write(eq1_tex), Write(eq2_tex))
        self.wait(0.5)

        step_text = Text("Elimination / Substitution Step:", font_size=20, color=YELLOW).next_to(eq_group, DOWN, buff=0.4, aligned_edge=LEFT)
        sol_tex = MathTex(r"x = {sol_x_latex},\\quad y = {sol_y_latex}", font_size=32, color=GREEN).next_to(step_text, DOWN, buff=0.3, aligned_edge=LEFT)
        box = SurroundingRectangle(sol_tex, color=GREEN, buff=0.15)

        self.play(FadeIn(step_text), Write(sol_tex), Create(box))
        self.wait(0.8)

        axes = Axes(
            x_range=[{int(num_x) - 4}, {int(num_x) + 4}, 1],
            y_range=[{int(num_y) - 4}, {int(num_y) + 4}, 1],
            x_length=5.5,
            y_length=4.0,
            axis_config={{"include_tip": True, "font_size": 16}}
        ).shift(RIGHT * 3.0 + DOWN * 0.5)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        pt_intersect = axes.c2p({num_x}, {num_y})
        dot = Dot(pt_intersect, color=YELLOW, radius=0.1)
        lbl_pt = MathTex(r"({sol_x_latex}, {sol_y_latex})", font_size=22, color=YELLOW).next_to(dot, UR, buff=0.1)

        self.play(Create(axes), Write(axes_labels))
        self.play(Create(dot), Write(lbl_pt))
        self.wait(2)
'''
        return manim_code, math_solution, "equation"

    # ----------------------------------------------------------------------
    # DERIVATIVE AND TANGENT LINE TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_derivative_tangent(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("tangent" in lower or ("derivative" in lower and "at" in lower) or "slope of" in lower):
            return None

        pt_match = re.search(r"(?:at\s+x\s*=|at\s+x\s+is\s+|=)\s*([+-]?[0-9.]+)", lower)
        x0_val = float(pt_match.group(1)) if pt_match else 1.0

        x = sp.Symbol("x")
        func_expr = None
        m_func = re.search(r"(?:y|f\(x\))\s*=\s*([a-zA-Z0-9\s\^\*\+\-\/\(\)]+)", text)
        if not m_func:
            m_func = re.search(r"(?:curve|function)\s+([a-zA-Z0-9\s\^\*\+\-\/\(\)]+)", text, re.IGNORECASE)

        if m_func:
            raw = m_func.group(1).split("at")[0].strip()
            try:
                candidate = _parse_math_expr(raw)
                if candidate.has(x):
                    func_expr = candidate
            except Exception:
                pass

        if func_expr is None:
            func_expr = x**2

        try:
            f_prime = sp.diff(func_expr, x)
            y0 = float(func_expr.subs(x, x0_val))
            slope = float(f_prime.subs(x, x0_val))
        except Exception:
            return None

        f_latex = sp.latex(func_expr)
        f_prime_latex = sp.latex(f_prime)
        slope_str = f"{slope:g}"

        math_solution = f"""Derivative and Tangent Line Solution:
Function: f(x) = {f_latex}
Point of tangency: x0 = {x0_val:g}, y0 = f({x0_val:g}) = {y0:g}
1. Derivative function: f'(x) = {f_prime_latex}
2. Slope of tangent at x = {x0_val:g}: m = f'({x0_val:g}) = {slope_str}
3. Equation of tangent line: y - {y0:g} = {slope_str}(x - {x0_val:g})
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Derivative as Slope of Tangent Line", font_size=30).to_edge(UP)
        f_tex = MathTex(r"f(x) = {f_latex},\\quad f'(x) = {f_prime_latex}", font_size=26, color=YELLOW).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Write(f_tex))
        self.wait(0.5)

        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 8, 2],
            x_length=7,
            y_length=4.2,
            axis_config={{"include_tip": True, "font_size": 18}}
        ).shift(DOWN * 0.6)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))

        curve = axes.plot(lambda x: {sp.pycode(func_expr)}, x_range=[-3, 3], color=BLUE)
        self.play(Create(curve))
        self.wait(0.5)

        pt_tangent = axes.c2p({x0_val}, {y0})
        dot = Dot(pt_tangent, color=RED, radius=0.09)
        lbl_pt = MathTex(r"P({x0_val:g}, {y0:g})", font_size=20, color=RED_A).next_to(dot, UR, buff=0.1)
        self.play(Create(dot), Write(lbl_pt))
        self.wait(0.5)

        dx = 1.8
        t_start = axes.c2p({x0_val} - dx, {y0} - {slope} * dx)
        t_end = axes.c2p({x0_val} + dx, {y0} + {slope} * dx)
        t_line = Line(t_start, t_end, color=ORANGE, stroke_width=4)
        lbl_slope = MathTex(r"m = {slope_str}", font_size=24, color=ORANGE).next_to(t_line.get_center(), UL, buff=0.15)

        self.play(Create(t_line), Write(lbl_slope))
        self.wait(2)
'''
        return manim_code, math_solution, "calculus"

    # ----------------------------------------------------------------------
    # 1. QUADRILATERAL CONSTRUCTION TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_quadrilateral_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("quadrilateral" in lower or "construct" in lower):
            return None

        # Extract sides: AB, BC, CD, AD/DA, and diagonal AC or BD
        pairs = re.findall(r"([A-Za-z]{2})\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if len(pairs) < 4:
            return None

        lengths = {}
        for edge, val in pairs:
            edge_norm = edge.upper()
            lengths[edge_norm] = float(val)

        AB = lengths.get("AB") or lengths.get("BA")
        BC = lengths.get("BC") or lengths.get("CB")
        CD = lengths.get("CD") or lengths.get("DC")
        AD = lengths.get("AD") or lengths.get("DA")
        AC = lengths.get("AC") or lengths.get("CA")
        BD = lengths.get("BD") or lengths.get("DB")

        if not (AB and BC and CD and AD and (AC or BD)):
            return None

        use_ac = AC is not None
        diag_name = "AC" if use_ac else "BD"
        diag_len = AC if use_ac else BD

        s_AB, s_BC, s_CD, s_AD = AB, BC, CD, AD

        # Law of cosines for B (in triangle ABC)
        try:
            cos_a = (s_AB**2 + diag_len**2 - s_BC**2) / (2 * s_AB * diag_len)
            if not (-1.0 <= cos_a <= 1.0):
                return None
            sin_a = math.sqrt(max(0.0, 1.0 - cos_a**2))

            cos_d = (s_AD**2 + diag_len**2 - s_CD**2) / (2 * s_AD * diag_len)
            if not (-1.0 <= cos_d <= 1.0):
                return None
            sin_d = math.sqrt(max(0.0, 1.0 - cos_d**2))
        except ZeroDivisionError:
            return None

        # Coordinates with respect to base center
        L = diag_len
        pA = np.array([-L / 2.0, 0.0, 0.0])
        pC = np.array([L / 2.0, 0.0, 0.0])
        pB = pA + s_AB * np.array([cos_a, sin_a, 0.0])
        pD = pA + s_AD * np.array([cos_d, -sin_d, 0.0])

        # Centering and scaling for Manim camera (ensure radius <= 3.2 to fit screen)
        pts = [pA, pB, pC, pD]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        max_edge = max(s_AB, s_BC, s_CD, s_AD, diag_len)
        center = np.array([(min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, 0.0])
        scale = min(5.2 / max(w, 0.1), 3.2 / max(h, 0.1), 3.0 / max(max_edge, 0.1))

        A_s = np.round((pA - center) * scale + np.array([0, -0.3, 0]), 3)
        B_s = np.round((pB - center) * scale + np.array([0, -0.3, 0]), 3)
        C_s = np.round((pC - center) * scale + np.array([0, -0.3, 0]), 3)
        D_s = np.round((pD - center) * scale + np.array([0, -0.3, 0]), 3)

        angle_A_to_B = math.atan2(B_s[1] - A_s[1], B_s[0] - A_s[0])
        angle_C_to_B = math.atan2(B_s[1] - C_s[1], B_s[0] - C_s[0])
        angle_A_to_D = math.atan2(D_s[1] - A_s[1], D_s[0] - A_s[0])
        angle_C_to_D = math.atan2(D_s[1] - C_s[1], D_s[0] - C_s[0])

        r_AB_s = round(s_AB * scale, 3)
        r_BC_s = round(s_BC * scale, 3)
        r_AD_s = round(s_AD * scale, 3)
        r_CD_s = round(s_CD * scale, 3)

        math_solution = f"""Quadrilateral ABCD Construction Plan:
Given sides: AB = {AB}, BC = {BC}, CD = {CD}, AD = {AD}, and diagonal {diag_name} = {diag_len}.
1. Draw diagonal {diag_name} as the base line.
2. From A, draw a compass arc of radius {AB}. From C, draw a compass arc of radius {BC}. Their intersection is vertex B.
3. Draw sides AB and BC to complete triangle ABC.
4. From A, draw a compass arc of radius {AD}. From C, draw a compass arc of radius {CD}. Their intersection is vertex D.
5. Draw sides AD and CD to complete triangle ACD.
6. The resulting polygon ABCD is the required quadrilateral.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing Quadrilateral ABCD", font_size=32).to_edge(UP)
        given_text = MathTex(
            r"AB={AB},\\ BC={BC},\\ CD={CD},\\ AD={AD},\\ {diag_name}={diag_len}",
            font_size=24, color=GRAY_A
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        step1 = Text("Step 1: Draw diagonal {diag_name} = {diag_len} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        pA = np.array({list(A_s)})
        pC = np.array({list(C_s)})
        dotA = Dot(pA, color=BLUE)
        dotC = Dot(pC, color=BLUE)
        lblA = MathTex(r"A", font_size=26).next_to(dotA, LEFT, buff=0.15)
        lblC = MathTex(r"C", font_size=26).next_to(dotC, RIGHT, buff=0.15)
        lineAC = DashedLine(pA, pC, color=PURPLE, dash_length=0.15)
        lblAC = MathTex(r"{diag_name} = {diag_len}", font_size=22, color=PURPLE).next_to(lineAC, UP, buff=0.1)

        self.play(Write(step1), Create(dotA), Write(lblA), Create(dotC), Write(lblC))
        self.play(Create(lineAC), Write(lblAC))
        self.wait(0.5)

        self.play(Transform(step1, Text("Step 2: Draw arcs from A ({AB} cm) and C ({BC} cm) to locate B", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_AB = Arc(radius={r_AB_s}, start_angle={round(angle_A_to_B - 0.35, 3)}, angle=0.7, arc_center=pA, color=TEAL)
        arc_BC = Arc(radius={r_BC_s}, start_angle={round(angle_C_to_B - 0.35, 3)}, angle=0.7, arc_center=pC, color=TEAL)
        self.play(Create(arc_AB), Create(arc_BC))

        pB = np.array({list(B_s)})
        dotB = Dot(pB, color=RED)
        lblB = MathTex(r"B", font_size=26).next_to(dotB, UP, buff=0.15)
        lineAB = Line(pA, pB, color=RED)
        lineBC = Line(pC, pB, color=RED)
        lblAB = MathTex(r"{AB}", font_size=20, color=RED_A).next_to(lineAB.get_center(), UL, buff=0.08)
        lblBC = MathTex(r"{BC}", font_size=20, color=RED_A).next_to(lineBC.get_center(), UR, buff=0.08)

        self.play(Create(dotB), Write(lblB))
        self.play(Create(lineAB), Write(lblAB), Create(lineBC), Write(lblBC))
        self.wait(0.5)

        self.play(Transform(step1, Text("Step 3: Draw arcs from A ({AD} cm) and C ({CD} cm) to locate D", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_AD = Arc(radius={r_AD_s}, start_angle={round(angle_A_to_D - 0.35, 3)}, angle=0.7, arc_center=pA, color=GREEN)
        arc_CD = Arc(radius={r_CD_s}, start_angle={round(angle_C_to_D - 0.35, 3)}, angle=0.7, arc_center=pC, color=GREEN)
        self.play(Create(arc_AD), Create(arc_CD))

        pD = np.array({list(D_s)})
        dotD = Dot(pD, color=GREEN)
        lblD = MathTex(r"D", font_size=26).next_to(dotD, DOWN, buff=0.15)
        lineAD = Line(pA, pD, color=GREEN)
        lineCD = Line(pC, pD, color=GREEN)
        lblAD = MathTex(r"{AD}", font_size=20, color=GREEN_A).next_to(lineAD.get_center(), DL, buff=0.08)
        lblCD = MathTex(r"{CD}", font_size=20, color=GREEN_A).next_to(lineCD.get_center(), DR, buff=0.08)

        self.play(Create(dotD), Write(lblD))
        self.play(Create(lineAD), Write(lblAD), Create(lineCD), Write(lblCD))
        self.wait(0.5)

        self.play(Transform(step1, Text("Quadrilateral ABCD Constructed Successfully", font_size=22, color=GREEN_B).to_edge(DOWN)))
        quad = Polygon(pA, pB, pC, pD, color=YELLOW, fill_color=YELLOW, fill_opacity=0.2, stroke_width=4)
        self.play(FadeOut(arc_AB), FadeOut(arc_BC), FadeOut(arc_AD), FadeOut(arc_CD))
        self.play(Create(quad))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # 2. TRIANGLE CONSTRUCTION TEMPLATE (SSS)
    # ----------------------------------------------------------------------
    @classmethod
    def _match_triangle_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("triangle" in lower and ("construct" in lower or "draw" in lower or "sides" in lower)):
            return None

        pairs = re.findall(r"([A-Za-z]{1,2})\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if len(pairs) < 3:
            return None

        vals = [float(v) for _, v in pairs[:3]]
        vals.sort()
        a, b, c = vals[0], vals[1], vals[2]
        if a + b <= c:
            return None

        cos_A = (b**2 + c**2 - a**2) / (2 * b * c)
        sin_A = math.sqrt(max(0.0, 1.0 - cos_A**2))

        pA = np.array([-c / 2.0, 0.0, 0.0])
        pB = np.array([c / 2.0, 0.0, 0.0])
        pC = pA + b * np.array([cos_A, sin_A, 0.0])

        pts = [pA, pB, pC]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        max_edge = max(a, b, c)
        center = np.array([(min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, 0.0])
        scale = min(5.2 / max(w, 0.1), 3.2 / max(h, 0.1), 3.0 / max(max_edge, 0.1))

        A_s = np.round((pA - center) * scale + np.array([0, -0.4, 0]), 3)
        B_s = np.round((pB - center) * scale + np.array([0, -0.4, 0]), 3)
        C_s = np.round((pC - center) * scale + np.array([0, -0.4, 0]), 3)

        angle_A_to_C = math.atan2(C_s[1] - A_s[1], C_s[0] - A_s[0])
        angle_B_to_C = math.atan2(C_s[1] - B_s[1], C_s[0] - B_s[0])

        r_b_s = round(b * scale, 3)
        r_a_s = round(a * scale, 3)

        math_solution = f"""Triangle Construction Plan (SSS):
Given side lengths: a = {a}, b = {b}, c = {c}.
1. Draw base AB of length {c} cm.
2. From A, draw a compass arc of radius {b} cm.
3. From B, draw a compass arc of radius {a} cm.
4. Mark the intersection as vertex C.
5. Connect AC and BC to form triangle ABC.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing Triangle ABC (SSS)", font_size=32).to_edge(UP)
        given_text = MathTex(r"c={c},\\ b={b},\\ a={a}", font_size=24, color=GRAY_A).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        step1 = Text("Step 1: Draw base AB = {c} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        pA = np.array({list(A_s)})
        pB = np.array({list(B_s)})
        dotA = Dot(pA, color=BLUE)
        dotB = Dot(pB, color=BLUE)
        lblA = MathTex(r"A", font_size=26).next_to(dotA, DL, buff=0.1)
        lblB = MathTex(r"B", font_size=26).next_to(dotB, DR, buff=0.1)
        lineAB = Line(pA, pB, color=BLUE)
        lblAB = MathTex(r"{c}", font_size=22, color=BLUE_A).next_to(lineAB, DOWN, buff=0.1)

        self.play(Write(step1), Create(dotA), Write(lblA), Create(dotB), Write(lblB), Create(lineAB), Write(lblAB))
        self.wait(0.5)

        self.play(Transform(step1, Text("Step 2: Draw arcs from A ({b} cm) and B ({a} cm)", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_b = Arc(radius={r_b_s}, start_angle={round(angle_A_to_C - 0.35, 3)}, angle=0.7, arc_center=pA, color=TEAL)
        arc_a = Arc(radius={r_a_s}, start_angle={round(angle_B_to_C - 0.35, 3)}, angle=0.7, arc_center=pB, color=TEAL)
        self.play(Create(arc_b), Create(arc_a))

        pC = np.array({list(C_s)})
        dotC = Dot(pC, color=RED)
        lblC = MathTex(r"C", font_size=26).next_to(dotC, UP, buff=0.15)
        lineAC = Line(pA, pC, color=RED)
        lineBC = Line(pB, pC, color=RED)
        lblAC = MathTex(r"{b}", font_size=20, color=RED_A).next_to(lineAC.get_center(), UL, buff=0.08)
        lblBC = MathTex(r"{a}", font_size=20, color=RED_A).next_to(lineBC.get_center(), UR, buff=0.08)

        self.play(Create(dotC), Write(lblC))
        self.play(Create(lineAC), Write(lblAC), Create(lineBC), Write(lblBC))
        self.wait(0.5)

        self.play(Transform(step1, Text("Triangle ABC Completed", font_size=22, color=GREEN_B).to_edge(DOWN)))
        tri = Polygon(pA, pB, pC, color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, stroke_width=4)
        self.play(FadeOut(arc_a), FadeOut(arc_b), Create(tri))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # 3. QUADRATIC EQUATION SOLVER TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_quadratic_equation(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("x^2" in lower or "x**2" in lower or "quadratic" in lower):
            return None

        eq_match = re.search(r"([0-9x\^\*\+\-\/\s\(\)]+=[0-9x\^\*\+\-\/\s\(\)]+)", text)
        if not eq_match:
            return None

        raw_eq = eq_match.group(1).strip()
        parts = raw_eq.split("=")
        if len(parts) != 2:
            return None

        x = sp.Symbol("x")
        try:
            lhs = _parse_math_expr(parts[0])
            rhs = _parse_math_expr(parts[1])
            diff = sp.simplify(lhs - rhs)
            poly = sp.Poly(diff, x)
            if poly.degree() != 2:
                return None
            coeffs = poly.all_coeffs()
            a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
        except Exception:
            return None

        D = b**2 - 4 * a * c
        roots = sp.solve(diff, x)
        roots_latex = ",\\ ".join([f"x = {sp.latex(r)}" for r in roots])

        a_str = f"{a:g}"
        b_str = f"{b:g}"
        c_str = f"{c:g}"
        D_str = f"{D:g}"

        math_solution = f"""Quadratic Equation Solution:
Equation: {sp.latex(lhs)} = {sp.latex(rhs)}
1. Simplified standard form: {sp.latex(diff)} = 0
2. Coefficients: a = {a_str}, b = {b_str}, c = {c_str}
3. Discriminant: D = b^2 - 4ac = ({b_str})^2 - 4({a_str})({c_str}) = {D_str}
4. Roots by Quadratic Formula: x = (-b +- sqrt(D)) / (2a)
5. Solutions: {roots_latex}
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Solving Quadratic Equation", font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        eq_given = MathTex(r"{sp.latex(lhs)} = {sp.latex(rhs)}", font_size=40, color=YELLOW)
        eq_given.shift(UP * 2.0)
        self.play(Write(eq_given))
        self.wait(0.5)

        coeff_tex = MathTex(r"a = {a_str},\\quad b = {b_str},\\quad c = {c_str}", font_size=30, color=BLUE_B)
        coeff_tex.next_to(eq_given, DOWN, buff=0.4)
        self.play(FadeIn(coeff_tex))
        self.wait(0.5)

        disc_tex = MathTex(r"D = b^2 - 4ac = ({b_str})^2 - 4({a_str})({c_str}) = {D_str}", font_size=30, color=TEAL)
        disc_tex.next_to(coeff_tex, DOWN, buff=0.4)
        self.play(Write(disc_tex))
        self.wait(0.5)

        formula_tex = MathTex(r"x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}", font_size=32, color=ORANGE)
        formula_tex.next_to(disc_tex, DOWN, buff=0.4)
        self.play(Write(formula_tex))
        self.wait(0.5)

        sol_tex = MathTex(r"{roots_latex}", font_size=36, color=GREEN)
        sol_tex.next_to(formula_tex, DOWN, buff=0.5)
        box = SurroundingRectangle(sol_tex, color=GREEN, buff=0.15)
        self.play(Write(sol_tex), Create(box))
        self.wait(2)
'''
        return manim_code, math_solution, "equation"

    # ----------------------------------------------------------------------
    # 4. LINEAR EQUATION SOLVER TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_linear_equation(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("=" in text and ("solve" in lower or "linear" in lower or "equation" in lower or "find x" in lower)):
            return None

        if "x^2" in lower or "x**2" in lower:
            return None

        eq_match = re.search(r"([0-9x\^\*\+\-\/\s\(\)]+=[0-9x\^\*\+\-\/\s\(\)]+)", text)
        if not eq_match:
            return None

        raw_eq = eq_match.group(1).strip()
        parts = raw_eq.split("=")
        if len(parts) != 2:
            return None

        x = sp.Symbol("x")
        try:
            lhs = _parse_math_expr(parts[0])
            rhs = _parse_math_expr(parts[1])
            diff = sp.simplify(lhs - rhs)
            poly = sp.Poly(diff, x)
            if poly.degree() != 1:
                return None
            sol = sp.solve(diff, x)[0]
        except Exception:
            return None

        step1 = f"{sp.latex(lhs)} = {sp.latex(rhs)}"
        coeffs = poly.all_coeffs()
        A, B = coeffs[0], coeffs[1]
        step2 = f"{sp.latex(A * x)} = {sp.latex(-B)}"
        step3 = f"x = {sp.latex(sol)}"

        math_solution = f"""Linear Equation Step-by-Step Solution:
Given: {step1}
Step 1: Simplify and isolate variable terms: {step2}
Step 2: Divide by coefficient to solve for x: {step3}
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Solving Linear Equation Step-by-Step", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        eq1 = MathTex(r"{step1}", font_size=38, color=YELLOW)
        eq1.shift(UP * 1.5)
        self.play(Write(eq1))
        self.wait(0.8)

        step_lbl1 = Text("Isolate terms with x:", font_size=22, color=BLUE_B).next_to(eq1, DOWN, buff=0.35, aligned_edge=LEFT)
        eq2 = MathTex(r"{step2}", font_size=38, color=TEAL).next_to(step_lbl1, DOWN, buff=0.25)
        self.play(FadeIn(step_lbl1), Write(eq2))
        self.wait(0.8)

        step_lbl2 = Text("Divide both sides to find x:", font_size=22, color=BLUE_B).next_to(eq2, DOWN, buff=0.35, aligned_edge=LEFT)
        eq3 = MathTex(r"{step3}", font_size=42, color=GREEN).next_to(step_lbl2, DOWN, buff=0.25)
        box = SurroundingRectangle(eq3, color=GREEN, buff=0.15)
        self.play(FadeIn(step_lbl2), Write(eq3), Create(box))
        self.wait(2)
'''
        return manim_code, math_solution, "equation"

    # ----------------------------------------------------------------------
    # 5. CALCULUS DEFINITE INTEGRAL / AREA UNDER CURVE TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_calculus_integral(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("integral" in lower or "area under" in lower or "riemann" in lower or "integrate" in lower):
            return None

        bounds_match = re.search(r"from\s*([+-]?[0-9.]+)\s*to\s*([+-]?[0-9.]+)", lower)
        a_val, b_val = (0.0, 2.0)
        if bounds_match:
            a_val = float(bounds_match.group(1))
            b_val = float(bounds_match.group(2))

        x = sp.Symbol("x")
        func_expr = None
        expr_patterns = [
            r"(?:integral\s+of|area\s+under\s+(?:curve)?\s*(?:y\s*=)?)\s*([a-zA-Z0-9\s\^\*\+\-\/]+?)(?:\s+from|\s+between|$)",
            r"integrate\s+([a-zA-Z0-9\s\^\*\+\-\/]+?)(?:\s+from|\s+between|$)",
        ]
        for pat in expr_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw_func = m.group(1).strip().replace("^", "**")
                try:
                    candidate = sp.sympify(raw_func)
                    if candidate.has(x) or candidate.is_number:
                        func_expr = candidate
                        break
                except Exception:
                    pass

        if func_expr is None:
            func_expr = x**2

        try:
            antideriv = sp.integrate(func_expr, x)
            val = sp.integrate(func_expr, (x, a_val, b_val))
            val_num = float(val)
        except Exception:
            return None

        f_latex = sp.latex(func_expr)
        F_latex = sp.latex(antideriv)
        val_latex = sp.latex(val)

        x_min = min(a_val - 1.0, -1.0)
        x_max = max(b_val + 1.0, 4.0)

        math_solution = f"""Calculus Definite Integral / Area Solution:
Function: f(x) = {f_latex}
Bounds: [{a_val:g}, {b_val:g}]
1. Antiderivative: F(x) = \\int ({f_latex})\\,dx = {F_latex} + C
2. Fundamental Theorem of Calculus:
   \\int_{{{a_val:g}}}^{{{b_val:g}}} ({f_latex})\\,dx = F({b_val:g}) - F({a_val:g}) = {val_latex} \\approx {val_num:.3f}
3. Shaded region represents exact area under curve between x = {a_val:g} and x = {b_val:g}.
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Definite Integral as Area Under Curve", font_size=30).to_edge(UP)
        formula = MathTex(
            r"\\int_{{{a_val:g}}}^{{{b_val:g}}} \\left({f_latex}\\right) dx = \\left[ {F_latex} \\right]_{{{a_val:g}}}^{{{b_val:g}}} = {val_latex}",
            font_size=26, color=YELLOW
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Write(formula))
        self.wait(0.5)

        axes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[-1, 8, 2],
            x_length=8,
            y_length=4.2,
            axis_config={{"include_tip": True, "font_size": 20}},
        ).shift(DOWN * 0.8)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        curve = axes.plot(lambda x: {sp.pycode(func_expr)}, x_range=[{x_min}, {x_max}], color=BLUE)
        curve_label = MathTex(r"f(x) = {f_latex}", font_size=24, color=BLUE).next_to(axes.c2p({b_val}, 4), UR)

        self.play(Create(axes), Write(axes_labels))
        self.play(Create(curve), Write(curve_label))
        self.wait(0.5)

        area = axes.get_area(curve, x_range=[{a_val}, {b_val}], color=TEAL, opacity=0.4)
        area_label = MathTex(r"\\text{{Area}} = {val_latex}", font_size=24, color=TEAL_A).next_to(area, UP, buff=0.2)

        self.play(FadeIn(area), Write(area_label))
        self.wait(2)
'''
        return manim_code, math_solution, "calculus"

    # ----------------------------------------------------------------------
    # 6. FUNCTION GRAPHING TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_function_graph(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("graph" in lower or "plot" in lower or "curve" in lower or "parabola" in lower):
            return None

        if "integral" in lower or "area under" in lower or "riemann" in lower:
            return None

        m = re.search(r"(?:y|f\(x\))\s*=\s*([a-zA-Z0-9\s\^\*\+\-\/\(\)]+)", text)
        if not m:
            m = re.search(r"(?:graph|plot)\s+([a-zA-Z0-9\s\^\*\+\-\/\(\)]+)", text, re.IGNORECASE)

        if not m:
            return None

        raw = m.group(1).strip().replace("^", "**")
        x = sp.Symbol("x")
        try:
            expr = sp.sympify(raw)
            if not expr.has(x):
                return None
        except Exception:
            return None

        roots = []
        try:
            sol = sp.solve(expr, x)
            for r in sol:
                if r.is_real and r.is_number:
                    roots.append(float(r))
        except Exception:
            pass

        y_intercept = float(expr.subs(x, 0)) if expr.subs(x, 0).is_real else 0.0

        f_latex = sp.latex(expr)
        math_solution = f"""Function Plot Plan:
Function: f(x) = {f_latex}
y-intercept: (0, {y_intercept:.2f})
Roots: {roots}
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Graph of Function", font_size=32).to_edge(UP)
        f_lbl = MathTex(r"f(x) = {f_latex}", font_size=30, color=YELLOW).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Write(f_lbl))
        self.wait(0.5)

        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            x_length=7,
            y_length=4.5,
            axis_config={{"include_tip": True, "font_size": 18}},
        ).shift(DOWN * 0.5)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        self.play(Create(axes), Write(axes_labels))

        curve = axes.plot(lambda x: {sp.pycode(expr)}, x_range=[-4.5, 4.5], color=BLUE)
        self.play(Create(curve))
        self.wait(0.5)

        pt_y = axes.c2p(0, {y_intercept})
        dot_y = Dot(pt_y, color=RED)
        lbl_y = MathTex(r"(0, {round(y_intercept, 2)})", font_size=20, color=RED_A).next_to(dot_y, RIGHT, buff=0.1)
        self.play(Create(dot_y), Write(lbl_y))
        self.wait(2)
'''
        return manim_code, math_solution, "graphing"

    # ----------------------------------------------------------------------
    # 7. GEOMETRY AREA & PERIMETER TEMPLATE (Circle, Rectangle)
    # ----------------------------------------------------------------------
    @classmethod
    def _match_geometry_area_perimeter(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("area" in lower or "perimeter" in lower or "circumference" in lower):
            return None

        if "construct" in lower or "quadrilateral" in lower:
            return None

        if "circle" in lower or "radius" in lower:
            r_match = re.search(r"radius\s*(?:of|is|=)?\s*([0-9.]+)", lower)
            r = float(r_match.group(1)) if r_match else 3.0
            area = math.pi * (r**2)
            perim = 2 * math.pi * r

            math_solution = f"""Area and Circumference of a Circle:
Radius r = {r}
Area: A = pi * r^2 = pi * ({r})^2 = {r**2} * pi approx {area:.2f}
Circumference: C = 2 * pi * r = 2 * pi * ({r}) = {2*r} * pi approx {perim:.2f}
"""
            manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Area and Circumference of a Circle", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        circle = Circle(radius=1.8, color=BLUE, fill_color=BLUE_E, fill_opacity=0.3).shift(LEFT * 2.5 + DOWN * 0.3)
        rad_line = Line(circle.get_center(), circle.get_right(), color=YELLOW)
        rad_lbl = MathTex(r"r = {r}", font_size=26, color=YELLOW).next_to(rad_line, UP, buff=0.08)

        self.play(Create(circle), Create(rad_line), Write(rad_lbl))
        self.wait(0.5)

        formula_A = MathTex(r"A = \\pi r^2 = \\pi ({r})^2 = {r**2}\\pi \\approx {area:.2f}", font_size=28, color=TEAL)
        formula_C = MathTex(r"C = 2\\pi r = 2\\pi ({r}) = {2*r}\\pi \\approx {perim:.2f}", font_size=28, color=GREEN)
        vbox = VGroup(formula_A, formula_C).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(RIGHT * 2.0 + DOWN * 0.3)

        self.play(Write(formula_A))
        self.wait(0.5)
        self.play(Write(formula_C))
        self.wait(2)
'''
            return manim_code, math_solution, "geometry"

        if "rectangle" in lower:
            nums = [float(n) for n in re.findall(r"([0-9.]+)", text)]
            length = nums[0] if len(nums) > 0 else 5.0
            width = nums[1] if len(nums) > 1 else 3.0
            area = length * width
            perim = 2 * (length + width)

            math_solution = f"""Area and Perimeter of a Rectangle:
Length = {length}, Width = {width}
Area: A = l * w = {length} * {width} = {area}
Perimeter: P = 2(l + w) = 2({length} + {width}) = {perim}
"""
            manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Area and Perimeter of a Rectangle", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        rect = Rectangle(width=4.0, height=2.4, color=BLUE, fill_color=BLUE_E, fill_opacity=0.3).shift(LEFT * 2.2 + DOWN * 0.3)
        lbl_w = MathTex(r"{length}", font_size=26, color=YELLOW).next_to(rect, UP, buff=0.1)
        lbl_h = MathTex(r"{width}", font_size=26, color=YELLOW).next_to(rect, RIGHT, buff=0.1)

        self.play(Create(rect), Write(lbl_w), Write(lbl_h))
        self.wait(0.5)

        formula_A = MathTex(r"A = l \\times w = {length} \\times {width} = {area}", font_size=30, color=TEAL)
        formula_P = MathTex(r"P = 2(l + w) = 2({length} + {width}) = {perim}", font_size=30, color=GREEN)
        vbox = VGroup(formula_A, formula_P).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(RIGHT * 2.5 + DOWN * 0.3)

        self.play(Write(formula_A))
        self.wait(0.5)
        self.play(Write(formula_P))
        self.wait(2)
'''
            return manim_code, math_solution, "geometry"

        return None

    # ----------------------------------------------------------------------
    # 8. NUMBER LINE OPERATIONS TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_number_line(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("number line" in lower):
            return None

        op_match = re.search(r"([+-]?[0-9.]+)\s*([+-])\s*([0-9.]+)", text)
        if not op_match:
            return None

        start = float(op_match.group(1))
        op = op_match.group(2)
        step = float(op_match.group(3))
        end = start + step if op == "+" else start - step

        min_val = min(start, end, 0) - 2
        max_val = max(start, end, 0) + 2

        math_solution = f"""Number Line Operation:
Expression: {start:g} {op} {step:g} = {end:g}
1. Begin at {start:g} on the number line.
2. Move {'right' if op == '+' else 'left'} by {step:g} units.
3. Land on final result: {end:g}.
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Number Line Operation", font_size=32).to_edge(UP)
        expr_tex = MathTex(r"{start:g} {op} {step:g} = {end:g}", font_size=36, color=YELLOW).next_to(title, DOWN, buff=0.2)
        self.play(Write(title), Write(expr_tex))
        self.wait(0.5)

        nl = NumberLine(
            x_range=[{int(min_val)}, {int(max_val)}, 1],
            length=10,
            include_numbers=True,
            font_size=22
        ).shift(DOWN * 0.8)
        self.play(Create(nl))
        self.wait(0.5)

        pt_start = nl.number_to_point({start})
        dot_start = Dot(pt_start, color=BLUE, radius=0.1)
        lbl_start = MathTex(r"\\text{{Start: }}{start:g}", font_size=22, color=BLUE_A).next_to(dot_start, UP, buff=0.15)
        self.play(Create(dot_start), Write(lbl_start))
        self.wait(0.5)

        pt_end = nl.number_to_point({end})
        arrow = CurvedArrow(pt_start + UP*0.15, pt_end + UP*0.15, angle=-0.5, color=TEAL)
        step_lbl = MathTex(r"{op}{step:g}", font_size=24, color=TEAL_A).next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), Write(step_lbl))
        self.wait(0.5)

        dot_end = Dot(pt_end, color=GREEN, radius=0.12)
        lbl_end = MathTex(r"\\text{{Result: }}{end:g}", font_size=24, color=GREEN).next_to(dot_end, DOWN, buff=0.25)
        self.play(Create(dot_end), Write(lbl_end))
        self.wait(2)
'''
        return manim_code, math_solution, "number_line"

    # ----------------------------------------------------------------------
    # 15. PARALLELOGRAM / RECTANGLE / SQUARE CONSTRUCTION TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_parallelogram_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        is_square = "square" in lower and ("construct" in lower or "draw" in lower or "side" in lower)
        is_rect = "rectangle" in lower and ("construct" in lower or "draw" in lower or "side" in lower or "length" in lower)
        is_para = "parallelogram" in lower

        if not (is_square or is_rect or is_para):
            return None

        # Case 1: Square
        if is_square:
            s_m = re.search(r"side\s*(?:of|=|length)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
            if not s_m:
                s_m = re.search(r"([A-Za-z]{2})\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text)
            if not s_m:
                return None
            s_val = float(s_m.group(1 if len(s_m.groups()) == 1 else 2))
            if s_val <= 0:
                return None

            name_m = re.search(r"square\s+([A-Za-z]{4})", text, re.IGNORECASE)
            v = name_m.group(1).upper() if name_m else "READ"
            v1, v2, v3, v4 = v[0], v[1], v[2], v[3]

            scale = min(2.8 / s_val, 0.8)
            half = round(s_val * scale / 2.0, 3)
            p1 = np.round(np.array([-half, -half, 0.0]), 3)
            p2 = np.round(np.array([half, -half, 0.0]), 3)
            p3 = np.round(np.array([half, half, 0.0]), 3)
            p4 = np.round(np.array([-half, half, 0.0]), 3)

            math_solution = f"""Square {v1}{v2}{v3}{v4} Construction Plan:
Given: Side length s = {s_val} cm. All interior angles = 90 degrees.
1. Draw base segment {v1}{v2} = {s_val} cm horizontally.
2. At vertices {v1} and {v2}, erect perpendicular rays (90 degrees).
3. With compass set to {s_val} cm, cut arcs from {v1} and {v2} along the perpendiculars to locate {v4} and {v3}.
4. Join {v4}{v3} to complete square {v1}{v2}{v3}{v4}.
Perimeter = 4 * {s_val} = {4 * s_val:.2f} cm.
Area = {s_val}^2 = {s_val**2:.2f} sq cm.
"""
            manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing Square {v1}{v2}{v3}{v4}", font_size=32).to_edge(UP)
        given_text = MathTex(r"\\text{{Side }} s = {s_val}\\text{{ cm}},\\quad \\text{{All angles }} = 90^\\circ", font_size=24, color=GRAY_A).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        p1 = np.array({list(p1)})
        p2 = np.array({list(p2)})
        p3 = np.array({list(p3)})
        p4 = np.array({list(p4)})

        # Step 1: Base side
        step_banner = Text("Step 1: Draw base side {v1}{v2} = {s_val} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        dot1 = Dot(p1, color=BLUE)
        dot2 = Dot(p2, color=BLUE)
        lbl1 = MathTex(r"{v1}", font_size=26).next_to(dot1, DL, buff=0.1)
        lbl2 = MathTex(r"{v2}", font_size=26).next_to(dot2, DR, buff=0.1)
        line12 = Line(p1, p2, color=BLUE_B, stroke_width=4)
        lbl12 = MathTex(r"{s_val}\\text{{ cm}}", font_size=22, color=BLUE_A).next_to(line12, DOWN, buff=0.1)

        self.play(Write(step_banner), Create(dot1), Write(lbl1), Create(dot2), Write(lbl2), Create(line12), Write(lbl12))
        self.wait(0.8)

        # Step 2: Perpendiculars at endpoints
        self.play(Transform(step_banner, Text("Step 2: Erect perpendiculars at {v1} and {v2}", font_size=20, color=YELLOW).to_edge(DOWN)))
        ray1 = DashedLine(p1, p1 + np.array([0, {round(half*2 + 0.6, 3)}, 0]), color=TEAL, dash_length=0.12)
        ray2 = DashedLine(p2, p2 + np.array([0, {round(half*2 + 0.6, 3)}, 0]), color=TEAL, dash_length=0.12)
        self.play(Create(ray1), Create(ray2))
        self.wait(0.6)

        # Step 3: Cut arcs of length s to locate remaining vertices
        self.play(Transform(step_banner, Text("Step 3: Cut arcs of radius {s_val} cm to locate {v4} and {v3}", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc1 = Arc(radius={round(half*2, 3)}, start_angle=1.2, angle=0.6, arc_center=p1, color=ORANGE)
        arc2 = Arc(radius={round(half*2, 3)}, start_angle=1.2, angle=0.6, arc_center=p2, color=ORANGE)
        self.play(Create(arc1), Create(arc2))

        dot3 = Dot(p3, color=RED)
        dot4 = Dot(p4, color=RED)
        lbl3 = MathTex(r"{v3}", font_size=26).next_to(dot3, UR, buff=0.1)
        lbl4 = MathTex(r"{v4}", font_size=26).next_to(dot4, UL, buff=0.1)
        self.play(Create(dot3), Write(lbl3), Create(dot4), Write(lbl4))
        self.wait(0.8)

        # Step 4: Connect sides
        self.play(Transform(step_banner, Text("Step 4: Connect sides to complete square {v1}{v2}{v3}{v4}", font_size=20, color=YELLOW).to_edge(DOWN)))
        side23 = Line(p2, p3, color=YELLOW, stroke_width=3)
        side34 = Line(p3, p4, color=YELLOW, stroke_width=3)
        side41 = Line(p4, p1, color=YELLOW, stroke_width=3)
        self.play(Create(side23), Create(side34), Create(side41))
        self.wait(0.5)

        square_poly = Polygon(p1, p2, p3, p4, color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, stroke_width=4)
        self.play(FadeOut(arc1), FadeOut(arc2), FadeOut(ray1), FadeOut(ray2), Create(square_poly))
        self.play(Transform(step_banner, Text("Square {v1}{v2}{v3}{v4} Constructed Successfully", font_size=22, color=GREEN_B).to_edge(DOWN)))
        self.wait(2)
'''
            return manim_code, math_solution, "geometry"

        # Case 2: Rectangle / Parallelogram
        pairs = re.findall(r"([A-Za-z]{1,2})\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        ang_m = re.search(r"angle\s*(?:[A-Za-z]\s*)?[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:degrees|deg|°)?", text, re.IGNORECASE)

        if is_rect:
            if len(pairs) < 2:
                nums = [float(x) for x in re.findall(r"([0-9]+(?:\.[0-9]+)?)", text)]
                if len(nums) >= 2:
                    a_val, b_val = nums[0], nums[1]
                else:
                    return None
            else:
                a_val, b_val = float(pairs[0][1]), float(pairs[1][1])
            ang_deg = 90.0
            shape_type = "Rectangle"
            name_m = re.search(r"rectangle\s+([A-Za-z]{4})", text, re.IGNORECASE)
            v = name_m.group(1).upper() if name_m else "ABCD"
        else:
            if len(pairs) < 2:
                return None
            a_val, b_val = float(pairs[0][1]), float(pairs[1][1])
            name_m = re.search(r"parallelogram\s+([A-Za-z]{4})", text, re.IGNORECASE)
            v = name_m.group(1).upper() if name_m else "ABCD"
            shape_type = "Parallelogram"

            if ang_m:
                ang_deg = float(ang_m.group(1))
            elif len(pairs) >= 3:
                d_val = float(pairs[2][1])
                cos_B = (a_val**2 + b_val**2 - d_val**2) / (2.0 * a_val * b_val)
                if not (-1.0 < cos_B < 1.0):
                    return None
                ang_deg = round(math.degrees(math.acos(-cos_B)), 1)
            else:
                ang_deg = 60.0

        if a_val <= 0 or b_val <= 0:
            return None

        v1, v2, v3, v4 = v[0], v[1], v[2], v[3]
        rad = math.radians(ang_deg)
        dx_raw = b_val * math.cos(rad)
        dy_raw = b_val * math.sin(rad)
        if dy_raw <= 0:
            return None

        scale = min(4.8 / (a_val + abs(dx_raw)), 3.0 / dy_raw, 2.8 / max(a_val, b_val, 0.1))
        dx = round(dx_raw * scale, 3)
        dy = round(dy_raw * scale, 3)
        a_scaled = round(a_val * scale, 3)
        b_scaled = round(b_val * scale, 3)

        p1 = np.round(np.array([-a_scaled / 2.0 - dx / 2.0, -dy / 2.0, 0.0]), 3)
        p2 = np.round(p1 + np.array([a_scaled, 0.0, 0.0]), 3)
        p4 = np.round(p1 + np.array([dx, dy, 0.0]), 3)
        p3 = np.round(p2 + np.array([dx, dy, 0.0]), 3)

        math_solution = f"""{shape_type} {v1}{v2}{v3}{v4} Construction Plan:
Given: Side {v1}{v2} = {a_val} cm, Side {v2}{v3} = {v1}{v4} = {b_val} cm, Angle = {ang_deg} degrees.
Opposite sides are equal and parallel: {v1}{v2} = {v4}{v3} = {a_val} cm, {v1}{v4} = {v2}{v3} = {b_val} cm.
1. Draw base line segment {v1}{v2} = {a_val} cm.
2. At vertex {v1}, construct angle of {ang_deg} degrees.
3. On this ray, cut an arc of radius {b_val} cm to locate vertex {v4}.
4. From vertex {v4}, cut an arc of radius {a_val} cm.
5. From vertex {v2}, cut an arc of radius {b_val} cm, intersecting the arc from {v4} at vertex {v3}.
6. Join {v2}{v3} and {v4}{v3} to complete the {shape_type.lower()} {v1}{v2}{v3}{v4}.
Perimeter = 2 * ({a_val} + {b_val}) = {2 * (a_val + b_val):.2f} cm.
Area = base * height = {a_val * dy_raw:.2f} sq cm.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing {shape_type} {v1}{v2}{v3}{v4}", font_size=32).to_edge(UP)
        given_text = MathTex(
            r"\\text{{Sides: }} {v1}{v2} = {a_val}\\text{{ cm}},\\ {v1}{v4} = {b_val}\\text{{ cm}},\\quad \\angle = {ang_deg}^\\circ",
            font_size=24, color=GRAY_A
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        p1 = np.array({list(p1)})
        p2 = np.array({list(p2)})
        p3 = np.array({list(p3)})
        p4 = np.array({list(p4)})

        # Step 1: Base side
        step_banner = Text("Step 1: Draw base side {v1}{v2} = {a_val} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        dot1 = Dot(p1, color=BLUE)
        dot2 = Dot(p2, color=BLUE)
        lbl1 = MathTex(r"{v1}", font_size=26).next_to(dot1, DL, buff=0.1)
        lbl2 = MathTex(r"{v2}", font_size=26).next_to(dot2, DR, buff=0.1)
        line12 = Line(p1, p2, color=BLUE_B, stroke_width=4)
        lbl12 = MathTex(r"{a_val}\\text{{ cm}}", font_size=22, color=BLUE_A).next_to(line12, DOWN, buff=0.1)

        self.play(Write(step_banner), Create(dot1), Write(lbl1), Create(dot2), Write(lbl2), Create(line12), Write(lbl12))
        self.wait(0.8)

        # Step 2: Angle and vertex 4
        self.play(Transform(step_banner, Text("Step 2: Construct angle of {ang_deg} degrees at {v1} and mark {v4}", font_size=20, color=YELLOW).to_edge(DOWN)))
        ray_dir = (p4 - p1) / np.linalg.norm(p4 - p1)
        ray_end = p1 + ray_dir * ({b_scaled} + 0.6)
        ray1 = DashedLine(p1, ray_end, color=TEAL, dash_length=0.12)
        arc_ang = Arc(radius=0.5, start_angle=0, angle={round(rad, 3)}, arc_center=p1, color=YELLOW)
        arc_cut4 = Arc(radius={b_scaled}, start_angle={round(rad - 0.2, 3)}, angle=0.4, arc_center=p1, color=ORANGE)

        self.play(Create(arc_ang), Create(ray1))
        self.play(Create(arc_cut4))

        dot4 = Dot(p4, color=RED)
        lbl4 = MathTex(r"{v4}", font_size=26).next_to(dot4, UL, buff=0.1)
        side14 = Line(p1, p4, color=YELLOW, stroke_width=3)
        lbl14 = MathTex(r"{b_val}\\text{{ cm}}", font_size=20, color=ORANGE).next_to(side14, LEFT, buff=0.1)

        self.play(Create(dot4), Write(lbl4), Create(side14), Write(lbl14))
        self.wait(0.8)

        # Step 3: Arcs for vertex 3
        self.play(Transform(step_banner, Text("Step 3: Cut arcs from {v4} ({a_val} cm) and {v2} ({b_val} cm) to locate {v3}", font_size=20, color=YELLOW).to_edge(DOWN)))
        arc_from4 = Arc(radius={a_scaled}, start_angle=-0.2, angle=0.4, arc_center=p4, color=PURPLE)
        arc_from2 = Arc(radius={b_scaled}, start_angle={round(rad - 0.2, 3)}, angle=0.4, arc_center=p2, color=PURPLE)

        self.play(Create(arc_from4), Create(arc_from2))
        dot3 = Dot(p3, color=RED)
        lbl3 = MathTex(r"{v3}", font_size=26).next_to(dot3, UR, buff=0.1)
        self.play(Create(dot3), Write(lbl3))
        self.wait(0.6)

        # Step 4: Connect remaining sides
        self.play(Transform(step_banner, Text("Step 4: Connect sides {v2}{v3} and {v4}{v3} to complete the {shape_type.lower()}", font_size=20, color=YELLOW).to_edge(DOWN)))
        side23 = Line(p2, p3, color=YELLOW, stroke_width=3)
        side43 = Line(p4, p3, color=YELLOW, stroke_width=3)
        self.play(Create(side23), Create(side43))
        self.wait(0.5)

        poly = Polygon(p1, p2, p3, p4, color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, stroke_width=4)
        self.play(FadeOut(arc_ang), FadeOut(ray1), FadeOut(arc_cut4), FadeOut(arc_from4), FadeOut(arc_from2), Create(poly))
        self.play(Transform(step_banner, Text("{shape_type} {v1}{v2}{v3}{v4} Constructed Successfully", font_size=22, color=GREEN_B).to_edge(DOWN)))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # 16. CIRCLE TANGENTS FROM EXTERNAL POINT TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_circle_tangent_construction(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not (("circle" in lower or "tangent" in lower) and ("tangent" in lower or "tangents" in lower)):
            return None

        r_m = re.search(r"radius\s*(?:of|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if not r_m:
            return None
        r_val = float(r_m.group(1))

        d_m = re.search(r"distance\s*(?:of|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if not d_m:
            d_m = re.search(r"point\s*(?:[A-Za-z]\s*)?(?:is\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?", text, re.IGNORECASE)
        if not d_m:
            d_m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:cm|m|units)?\s*away\s*from\s*(?:its|the)?\s*cent", text, re.IGNORECASE)

        if d_m:
            d_val = float(d_m.group(1))
        else:
            nums = [float(x) for x in re.findall(r"([0-9]+(?:\.[0-9]+)?)", text) if float(x) != r_val]
            if nums:
                d_val = max(nums)
            else:
                return None

        if d_val <= r_val or r_val <= 0:
            return None

        pt_m = re.search(r"point\s+([A-Za-z])\b", text, re.IGNORECASE)
        name = pt_m.group(1).upper() if pt_m else "P"

        s = round(4.8 / (d_val + r_val), 4)
        pO = np.round(np.array([-d_val * s / 2.0, 0.0, 0.0]), 3)
        pP = np.round(np.array([d_val * s / 2.0, 0.0, 0.0]), 3)
        pM = np.array([0.0, 0.0, 0.0])
        R_aux = round(d_val * s / 2.0, 3)
        x_int = ((r_val**2 - (d_val**2) / 2.0) / d_val) * s
        y_int = math.sqrt(max(R_aux**2 - x_int**2, 0.0))
        pT1 = np.round(np.array([x_int, y_int, 0.0]), 3)
        pT2 = np.round(np.array([x_int, -y_int, 0.0]), 3)
        L = math.sqrt(d_val**2 - r_val**2)
        r_disp = round(r_val * s, 3)

        math_solution = f"""Construction of Tangents to Circle from External Point {name}:
Given: Circle with center O and radius r = {r_val} cm. External point {name} at distance OP = {d_val} cm.
1. Draw the circle with center O and radius {r_val} cm.
2. Join OP = {d_val} cm.
3. Draw the perpendicular bisector of OP to find its midpoint M.
4. Taking M as center and MO as radius, draw an auxiliary circle intersecting the given circle at T1 and T2.
5. Join {name}T1 and {name}T2. These are the required pair of tangents.
By Pythagoras Theorem in right triangle OT1{name} (angle OT1{name} = 90 deg):
Tangent length {name}T1 = {name}T2 = sqrt(OP^2 - OT1^2) = sqrt({d_val}^2 - {r_val}^2) = {L:.2f} cm.
"""

        manim_code = f'''from manim import *
import numpy as np

class MathScene(Scene):
    def construct(self):
        title = Text("Constructing Tangents to a Circle from External Point", font_size=28).to_edge(UP)
        given_text = MathTex(
            r"\\text{{Radius }} r = {r_val}\\text{{ cm}},\\quad \\text{{Distance }} OP = {d_val}\\text{{ cm}}",
            font_size=24, color=GRAY_A
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_text))
        self.wait(0.5)

        pO = np.array({list(pO)})
        pP = np.array({list(pP)})
        pM = np.array({list(pM)})
        pT1 = np.array({list(pT1)})
        pT2 = np.array({list(pT2)})

        # Step 1: Draw circle with center O
        step_banner = Text("Step 1: Draw circle with center O and radius {r_val} cm", font_size=20, color=YELLOW).to_edge(DOWN)
        dotO = Dot(pO, color=BLUE)
        lblO = MathTex(r"O", font_size=26).next_to(dotO, DL, buff=0.1)
        circle_main = Circle(radius={r_disp}, color=BLUE, stroke_width=3).move_to(pO)
        self.play(Write(step_banner), Create(dotO), Write(lblO), Create(circle_main))
        self.wait(0.6)

        # Step 2: Mark external point P and line OP
        self.play(Transform(step_banner, Text("Step 2: Mark external point {name} at distance {d_val} cm and join O{name}", font_size=20, color=YELLOW).to_edge(DOWN)))
        dotP = Dot(pP, color=RED)
        lblP = MathTex(r"{name}", font_size=26).next_to(dotP, RIGHT, buff=0.12)
        lineOP = DashedLine(pO, pP, color=GRAY_B, dash_length=0.12)
        lblOP = MathTex(r"{d_val}\\text{{ cm}}", font_size=20, color=GRAY_A).next_to(lineOP, DOWN, buff=0.1)
        self.play(Create(dotP), Write(lblP), Create(lineOP), Write(lblOP))
        self.wait(0.6)

        # Step 3: Perpendicular bisector of OP to find midpoint M
        self.play(Transform(step_banner, Text("Step 3: Draw perpendicular bisector of O{name} to locate midpoint M", font_size=20, color=YELLOW).to_edge(DOWN)))
        dotM = Dot(pM, color=WHITE, radius=0.07)
        lblM = MathTex(r"M", font_size=22).next_to(dotM, DOWN, buff=0.1)
        bisector_line = DashedLine(pM + UP*1.8, pM + DOWN*1.8, color=TEAL, dash_length=0.1)
        self.play(Create(bisector_line), Create(dotM), Write(lblM))
        self.wait(0.6)

        # Step 4: Auxiliary circle with center M and radius MO
        self.play(Transform(step_banner, Text("Step 4: Draw auxiliary circle with center M passing through O and {name}", font_size=20, color=YELLOW).to_edge(DOWN)))
        circle_aux = DashedVMobject(Circle(radius={R_aux}, color=PURPLE, stroke_width=2).move_to(pM), num_dashes=30)
        dotT1 = Dot(pT1, color=YELLOW)
        dotT2 = Dot(pT2, color=YELLOW)
        lblT1 = MathTex(r"T_1", font_size=24).next_to(dotT1, UP, buff=0.1)
        lblT2 = MathTex(r"T_2", font_size=24).next_to(dotT2, DOWN, buff=0.1)
        self.play(Create(circle_aux))
        self.play(Create(dotT1), Write(lblT1), Create(dotT2), Write(lblT2))
        self.wait(0.8)

        # Step 5: Draw tangents PT1 and PT2
        self.play(Transform(step_banner, Text("Step 5: Draw tangents {name}T_1 and {name}T_2", font_size=20, color=YELLOW).to_edge(DOWN)))
        tan1 = Line(pP, pT1, color=GREEN, stroke_width=4)
        tan2 = Line(pP, pT2, color=GREEN, stroke_width=4)
        rad1 = DashedLine(pO, pT1, color=BLUE_A, stroke_width=2)
        rad2 = DashedLine(pO, pT2, color=BLUE_A, stroke_width=2)
        self.play(Create(rad1), Create(rad2), Create(tan1), Create(tan2))
        self.wait(0.6)

        # Step 6: Measurement validation
        self.play(FadeOut(bisector_line), FadeOut(circle_aux))
        summary_box = MathTex(
            r"\\text{{Length of Tangent: }} {name}T = \\sqrt{{{d_val}^2 - {r_val}^2}} = {L:.2f}\\text{{ cm}}",
            font_size=24, color=GREEN_B
        ).to_edge(DOWN)
        self.play(Transform(step_banner, summary_box))
        self.wait(2)
'''
        return manim_code, math_solution, "geometry"

    # ----------------------------------------------------------------------
    # 17. ARITHMETIC PROGRESSION (AP) SEQUENCE & SERIES TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_arithmetic_progression(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("arithmetic progression" in lower or "arithmetic sequence" in lower or ("ap" in lower and ("term" in lower or "sum" in lower or "first term" in lower or "difference" in lower))):
            return None

        seq_m = re.search(r"(?:ap:?|progression:?|sequence:?)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*,\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*,\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*,\s*([+-]?[0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
        a_val, d_val = None, None
        if seq_m:
            t0, t1, t2, t3 = [float(x) for x in seq_m.groups()]
            a_val = t0
            d_val = round(t1 - t0, 3)
        else:
            am = re.search(r"a\s*=\s*([+-]?[0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
            dm = re.search(r"d\s*=\s*([+-]?[0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
            if am and dm:
                a_val = float(am.group(1))
                d_val = float(dm.group(1))

        if a_val is None or d_val is None:
            return None

        n_m = re.search(r"([0-9]+)(?:st|nd|rd|th)?\s*term", text, re.IGNORECASE)
        if not n_m:
            n_m = re.search(r"first\s*([0-9]+)\s*terms", text, re.IGNORECASE)
        n_val = int(n_m.group(1)) if n_m else 10

        terms = [round(a_val + i * d_val, 3) for i in range(5)]
        an = round(a_val + (n_val - 1) * d_val, 3)
        sn = round((n_val / 2.0) * (2 * a_val + (n_val - 1) * d_val), 3)

        math_solution = f"""Arithmetic Progression (AP) Solution:
Given: First term a = {a_val:g}, Common difference d = {d_val:g}, Target n = {n_val}.
1. First 5 terms: {', '.join(f'{t:g}' for t in terms)}...
2. n-th term formula: a_n = a + (n - 1)d
   a_{n_val} = {a_val:g} + ({n_val} - 1)({d_val:g}) = {an:g}
3. Sum of first n terms formula: S_n = (n / 2)[2a + (n - 1)d]
   S_{n_val} = ({n_val} / 2)[2({a_val:g}) + ({n_val} - 1)({d_val:g})] = {sn:g}
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Arithmetic Progression (AP)", font_size=32).to_edge(UP)
        given_tex = MathTex(
            r"\\text{{First term }} a = {a_val:g},\\quad \\text{{Common difference }} d = {d_val:g}",
            font_size=26, color=GRAY_A
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(given_tex))
        self.wait(0.5)

        # Step 1: Sequence terms visualization
        step_banner = Text("Step 1: First 5 terms with common difference d = {d_val:g}", font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(Write(step_banner))

        boxes = VGroup()
        for val in {terms}:
            box = RoundedRectangle(corner_radius=0.15, height=0.9, width=1.2, color=BLUE, fill_color=BLUE_E, fill_opacity=0.4)
            num = MathTex(f"{{val:g}}", font_size=28, color=WHITE).move_to(box.get_center())
            boxes.add(VGroup(box, num))
        boxes.arrange(RIGHT, buff=0.6).shift(UP * 0.7)
        self.play(FadeIn(boxes, lag_ratio=0.2))

        # Difference arrows
        arrows = VGroup()
        for i in range(len(boxes) - 1):
            p_start = boxes[i].get_top()
            p_end = boxes[i+1].get_top()
            arrow = CurvedArrow(p_start + UP*0.05, p_end + UP*0.05, angle=-0.5, color=TEAL, stroke_width=2)
            d_lbl = MathTex(r"+{d_val:g}", font_size=18, color=TEAL_A).next_to(arrow, UP, buff=0.05)
            arrows.add(arrow, d_lbl)
        self.play(Create(arrows))
        self.wait(0.8)

        # Step 2: N-th Term Calculation
        self.play(Transform(step_banner, Text("Step 2: Find the {n_val}th term using a_n = a + (n - 1)d", font_size=20, color=YELLOW).to_edge(DOWN)))
        an_formula = MathTex(r"a_n = a + (n - 1)d", font_size=26, color=YELLOW).shift(DOWN * 0.5)
        an_calc = MathTex(
            r"a_{{{n_val}}} = {a_val:g} + ({n_val} - 1)({d_val:g}) = {an:g}",
            font_size=26, color=GREEN_B
        ).next_to(an_formula, DOWN, buff=0.2)
        self.play(Write(an_formula))
        self.play(Write(an_calc))
        self.wait(1.0)

        # Step 3: Sum of N terms Calculation
        self.play(Transform(step_banner, Text("Step 3: Find sum of first {n_val} terms using S_n = n/2 [2a + (n-1)d]", font_size=20, color=YELLOW).to_edge(DOWN)))
        sn_formula = MathTex(r"S_n = \\frac{{n}}{{2}}\\left[2a + (n - 1)d\\right]", font_size=26, color=YELLOW).next_to(an_calc, DOWN, buff=0.3)
        sn_calc = MathTex(
            r"S_{{{n_val}}} = \\frac{{{n_val}}}{{2}}\\left[2({a_val:g}) + ({n_val}-1)({d_val:g})\\right] = {sn:g}",
            font_size=26, color=GREEN_B
        ).next_to(sn_formula, DOWN, buff=0.2)
        self.play(Write(sn_formula))
        self.play(Write(sn_calc))
        self.wait(2)
'''
        return manim_code, math_solution, "sequence"

    # ----------------------------------------------------------------------
    # 18. 2X2 MATRIX DETERMINANT STEP-BY-STEP TEMPLATE
    # ----------------------------------------------------------------------
    @classmethod
    def _match_matrix_determinant(cls, text: str, lower: str) -> Optional[Tuple[str, str, str]]:
        if not ("determinant" in lower and ("matrix" in lower or "[[" in text or "2x2" in lower)):
            return None

        m = re.search(r"\[\s*\[\s*([+-]?[0-9.]+)\s*,\s*([+-]?[0-9.]+)\s*\]\s*,\s*\[\s*([+-]?[0-9.]+)\s*,\s*([+-]?[0-9.]+)\s*\]\s*\]", text)
        if not m:
            nums = [float(x) for x in re.findall(r"([+-]?[0-9]+(?:\.[0-9]+)?)", text)]
            if len(nums) >= 4:
                a, b, c, d = nums[0], nums[1], nums[2], nums[3]
            else:
                return None
        else:
            a, b, c, d = [float(x) for x in m.groups()]

        p1 = round(a * d, 3)
        p2 = round(b * c, 3)
        det = round(p1 - p2, 3)

        math_solution = f"""Determinant of 2x2 Matrix:
Matrix A = [[{a:g}, {b:g}], [{c:g}, {d:g}]]
Formula: det(A) = ad - bc
1. Main diagonal product: ({a:g}) * ({d:g}) = {p1:g}
2. Anti-diagonal product: ({b:g}) * ({c:g}) = {p2:g}
3. Evaluation: det(A) = {p1:g} - ({p2:g}) = {det:g}
"""

        manim_code = f'''from manim import *

class MathScene(Scene):
    def construct(self):
        title = Text("Determinant of 2x2 Matrix", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Matrix display
        matrix_m = Matrix([["{a:g}", "{b:g}"], ["{c:g}", "{d:g}"]], bracket_h_buff=0.15).scale(1.2).shift(LEFT * 2.5)
        mat_lbl = MathTex(r"A = ", font_size=34).next_to(matrix_m, LEFT, buff=0.2)
        self.play(Write(mat_lbl), Create(matrix_m))
        self.wait(0.6)

        step_banner = Text("Step 1: Main diagonal product (a * d)", font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(Write(step_banner))

        # Main diagonal highlight
        elem_a = matrix_m.get_entries()[0]
        elem_d = matrix_m.get_entries()[3]
        diag1_arrow = Arrow(elem_a.get_center(), elem_d.get_center(), color=GREEN, buff=0.15, stroke_width=3)
        self.play(Create(diag1_arrow))

        calc_steps = VGroup(
            MathTex(r"\\det(A) = \\begin{{vmatrix}} a & b \\\\ c & d \\end{{vmatrix}} = ad - bc", font_size=26, color=YELLOW),
            MathTex(r"\\text{{Main diagonal: }} ({a:g}) \\times ({d:g}) = {p1:g}", font_size=26, color=GREEN_A),
            MathTex(r"\\text{{Anti-diagonal: }} ({b:g}) \\times ({c:g}) = {p2:g}", font_size=26, color=RED_A),
            MathTex(r"\\det(A) = ({p1:g}) - ({p2:g}) = {det:g}", font_size=32, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(RIGHT * 2.5)

        self.play(Write(calc_steps[0]))
        self.play(Write(calc_steps[1]))
        self.wait(0.6)

        # Anti diagonal highlight
        self.play(Transform(step_banner, Text("Step 2: Anti-diagonal product (b * c)", font_size=20, color=YELLOW).to_edge(DOWN)))
        elem_b = matrix_m.get_entries()[1]
        elem_c = matrix_m.get_entries()[2]
        diag2_arrow = Arrow(elem_c.get_center(), elem_b.get_center(), color=RED, buff=0.15, stroke_width=3)
        self.play(Create(diag2_arrow), Write(calc_steps[2]))
        self.wait(0.6)

        # Final evaluation
        self.play(Transform(step_banner, Text("Step 3: Subtract anti-diagonal from main diagonal", font_size=20, color=YELLOW).to_edge(DOWN)))
        self.play(Write(calc_steps[3]))
        box = SurroundingRectangle(calc_steps[3], color=YELLOW, buff=0.15)
        self.play(Create(box))
        self.wait(2)
'''
        return manim_code, math_solution, "equation"

