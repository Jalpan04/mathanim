from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        # Parameters:
        # {{ FUNC }}    - Python expression, e.g. "x**2"
        # {{ A }}       - lower bound, e.g. 0
        # {{ B }}       - upper bound, e.g. 2
        # {{ N_RECTS }} - number of Riemann rects, e.g. 6
        # {{ LABEL }}   - LaTeX label, e.g. r"\int_0^2 x^2 dx"

        func_str = """{{ FUNC }}"""
        a = {{ A }}
        b = {{ B }}
        n_rects = {{ N_RECTS }}
        label_str = """{{ LABEL }}"""

        axes = Axes(
            x_range=[a - 0.5, b + 0.5, 0.5],
            y_range=[0, None, 1],
            axis_config={"include_tip": True},
        )
        axes.add_coordinates()

        def f(x):
            return eval(func_str, {"x": x, "np": np, "sin": np.sin, "cos": np.cos})

        # Riemann rectangles (coarse)
        rects_coarse = axes.get_riemann_rectangles(
            lambda x: f(x),
            x_range=[a, b],
            dx=(b - a) / n_rects,
            color=BLUE,
            fill_opacity=0.6,
        )

        curve = axes.plot(lambda x: f(x), color=YELLOW)
        formula = MathTex(label_str, font_size=40).to_edge(UP)

        self.play(Create(axes), Write(formula))
        self.wait(0.5)

        # Show Riemann rects
        self.play(Create(rects_coarse), run_time=1.5)
        self.wait(1)

        # Refine to smooth shaded area
        filled_area = axes.get_area(curve, x_range=[a, b], color=BLUE, opacity=0.4)
        self.play(Create(curve), Transform(rects_coarse, filled_area), run_time=2)
        self.wait(2)
