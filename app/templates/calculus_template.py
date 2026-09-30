# REFERENCE TEMPLATE: Calculus Archetype
# The LLM should adapt this pattern for integrals, Riemann sums, derivatives.
# This example shows a Riemann sum for integral of x^2 from 0 to 2.

from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-0.5, 2.5, 0.5],
            y_range=[-0.5, 5, 1],
            axis_config={"include_tip": True},
        )
        axes.add_coordinates()

        def f(x):
            return x**2

        curve = axes.plot(f, color=YELLOW)
        formula = MathTex(r"\int_0^2 x^2 \, dx = \frac{8}{3}", font_size=40).to_edge(UP)

        self.play(Create(axes), Write(formula))
        self.wait(0.5)

        rects = axes.get_riemann_rectangles(
            curve, x_range=[0, 2], dx=0.33, color=BLUE, fill_opacity=0.6
        )
        self.play(Create(rects), run_time=1.5)
        self.wait(1)

        filled_area = axes.get_area(curve, x_range=[0, 2], color=BLUE, opacity=0.4)
        self.play(Create(curve), Transform(rects, filled_area), run_time=2)
        self.wait(2)
