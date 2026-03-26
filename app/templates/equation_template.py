from manim import *


class MathScene(Scene):
    def construct(self):
        # Parameters injected by hybrid_router:
        # {{ TITLE }}  - e.g. "Solving 2x + 3 = 7"
        # {{ STEPS }}  - Python list of LaTeX strings, e.g. ["2x + 3 = 7", "2x = 4", "x = 2"]

        title_str = """{{ TITLE }}"""
        steps = {{ STEPS }}

        title = Text(title_str, font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Render each step sequentially, aligned left
        step_mobs = VGroup()
        for i, step in enumerate(steps):
            tex = MathTex(step, font_size=40)
            if i == 0:
                tex.next_to(title, DOWN, buff=0.8).to_edge(LEFT, buff=1.5)
            else:
                tex.next_to(step_mobs[-1], DOWN, aligned_edge=LEFT, buff=0.5)
            step_mobs.add(tex)
            self.play(Write(tex))

            # Highlight the new equation in accent color on first appear
            self.play(tex.animate.set_color(YELLOW), run_time=0.3)
            self.play(tex.animate.set_color(WHITE), run_time=0.3)
            self.wait(0.8)

        self.wait(2)
