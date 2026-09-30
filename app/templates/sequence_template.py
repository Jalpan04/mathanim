# REFERENCE TEMPLATE: Sequence Archetype
# The LLM should adapt this pattern for arithmetic/geometric sequences.
# This example shows the arithmetic sequence 1, 3, 5, 7, 9.

from manim import *


class MathScene(Scene):
    def construct(self):
        title = Text("Arithmetic Sequence", font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        terms = ["1", "3", "5", "7", "9"]
        term_mobs = VGroup()
        for t in terms:
            mob = MathTex(t, font_size=48)
            term_mobs.add(mob)
        term_mobs.arrange(RIGHT, buff=0.8)

        self.play(FadeIn(term_mobs, lag_ratio=0.3), run_time=2)
        self.wait(1)

        pattern = MathTex(r"a_n = 2n - 1", font_size=40).next_to(term_mobs, DOWN, buff=1.0)
        self.play(Write(pattern))
        self.wait(2)
