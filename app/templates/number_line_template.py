# REFERENCE TEMPLATE: Number Line Archetype
# The LLM should adapt this pattern for number line operations, inequalities.
# This example shows 3 + 2 = 5 on a number line.

from manim import *


class MathScene(Scene):
    def construct(self):
        title = Text("Addition on a Number Line", font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        number_line = NumberLine(
            x_range=[-2, 8, 1],
            length=10,
            include_numbers=True,
            include_tip=True,
        )
        self.play(Create(number_line))
        self.wait(0.5)

        start_dot = Dot(number_line.n2p(3), color=YELLOW, radius=0.12)
        start_label = MathTex(r"3", font_size=28).next_to(start_dot, UP, buff=0.3)
        self.play(Create(start_dot), Write(start_label))
        self.wait(0.5)

        arrow = Arrow(
            number_line.n2p(3), number_line.n2p(5), color=GREEN, buff=0
        ).shift(UP * 0.5)
        arrow_label = MathTex(r"+2", font_size=28, color=GREEN).next_to(arrow, UP, buff=0.1)
        self.play(Create(arrow), Write(arrow_label))
        self.wait(0.5)

        end_dot = Dot(number_line.n2p(5), color=RED, radius=0.12)
        end_label = MathTex(r"5", font_size=28).next_to(end_dot, DOWN, buff=0.3)
        self.play(Create(end_dot), Write(end_label))
        self.wait(0.5)

        result = MathTex(r"3 + 2 = 5", font_size=40).to_edge(DOWN)
        self.play(Write(result))
        self.wait(2)
