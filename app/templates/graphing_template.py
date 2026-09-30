# REFERENCE TEMPLATE: Graphing Archetype
# The LLM should adapt this pattern to plot any user-specified function(s).
# This example plots y = x^2. Adapt formula, ranges, labels to the user's question.

from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            axis_config={"include_tip": True},
        )
        axes.add_coordinates()

        title = Text("y = x^2", font_size=32).to_edge(UP)
        self.play(Write(title), Create(axes))
        self.wait(0.5)

        curve = axes.plot(lambda x: x**2, color=BLUE, use_smoothing=True)
        curve_label = MathTex(r"y = x^2", color=BLUE, font_size=28).next_to(
            curve.get_end(), RIGHT, buff=0.2
        )

        self.play(Create(curve), Write(curve_label), run_time=2)
        self.wait(3)
