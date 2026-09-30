# REFERENCE TEMPLATE: Unit Circle Archetype
# The LLM should adapt this pattern for unit circle, trig angle visualizations.
# This example draws the unit circle and traces sin/cos projections.

from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        title = Text("The Unit Circle", font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        circle = Circle(radius=2.5, color=WHITE)
        axes = Axes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1],
            axis_config={"include_tip": False, "stroke_width": 1},
        )
        self.play(Create(axes), Create(circle))
        self.wait(0.5)

        angle = ValueTracker(0)

        dot = always_redraw(
            lambda: Dot(
                point=circle.point_at_angle(angle.get_value()),
                color=YELLOW, radius=0.1,
            )
        )
        cos_line = always_redraw(
            lambda: DashedLine(
                circle.point_at_angle(angle.get_value()),
                [circle.point_at_angle(angle.get_value())[0], 0, 0],
                color=BLUE,
            )
        )
        sin_line = always_redraw(
            lambda: DashedLine(
                circle.point_at_angle(angle.get_value()),
                [0, circle.point_at_angle(angle.get_value())[1], 0],
                color=RED,
            )
        )

        cos_label = MathTex(r"\cos\theta", color=BLUE, font_size=28).to_edge(DOWN + LEFT)
        sin_label = MathTex(r"\sin\theta", color=RED, font_size=28).next_to(cos_label, RIGHT, buff=1)
        self.play(Create(dot), Write(cos_label), Write(sin_label))
        self.add(cos_line, sin_line)

        self.play(angle.animate.set_value(2 * PI), run_time=6, rate_func=linear)
        self.wait(2)
