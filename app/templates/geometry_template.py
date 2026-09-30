# REFERENCE TEMPLATE: Geometry Archetype
# The LLM should adapt this pattern for any shape, area, perimeter question.
# This example draws a circle and shows its area formula.

from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        title = Text("Area of a Circle", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        circle = Circle(radius=2.0, color=BLUE, fill_color=BLUE_D, fill_opacity=0.3)
        self.play(Create(circle))
        self.wait(0.5)

        radius_line = Line(circle.get_center(), circle.get_right(), color=YELLOW)
        r_label = MathTex(r"r", font_size=30).next_to(radius_line, DOWN, buff=0.1)
        self.play(Create(radius_line), Write(r_label))
        self.wait(0.5)

        formula = MathTex(r"A = \pi r^2", font_size=44).next_to(circle, DOWN, buff=0.8)
        self.play(Write(formula))
        self.wait(0.5)

        result = MathTex(
            r"A = \pi (2)^2 = 4\pi", font_size=40
        ).next_to(formula, DOWN, buff=0.4)
        self.play(Write(result))
        self.wait(2)
