# REFERENCE TEMPLATE: Equation Archetype
# The LLM should adapt this pattern for step-by-step equation solving.
# This example solves 2x + 3 = 7 step by step.

from manim import *


class MathScene(Scene):
    def construct(self):
        title = Text("Solving 2x + 3 = 7", font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        steps = [
            r"2x + 3 = 7",
            r"2x = 7 - 3",
            r"2x = 4",
            r"x = 2",
        ]

        step_mobs = VGroup()
        for i, step in enumerate(steps):
            tex = MathTex(step, font_size=40)
            if i == 0:
                tex.next_to(title, DOWN, buff=0.8).to_edge(LEFT, buff=1.5)
            else:
                tex.next_to(step_mobs[-1], DOWN, aligned_edge=LEFT, buff=0.5)
            step_mobs.add(tex)
            self.play(Write(tex))
            self.play(tex.animate.set_color(YELLOW), run_time=0.3)
            self.play(tex.animate.set_color(WHITE), run_time=0.3)
            self.wait(0.5)

        self.wait(2)
