from manim import *


class MathScene(Scene):
    def construct(self):
        # Parameters:
        # {{ TERMS }}      - Python list of LaTeX strings, e.g. ["1", "3", "5", "7", "9"]
        # {{ TITLE }}      - e.g. "Arithmetic Sequence: 1, 3, 5, 7..."
        # {{ PATTERN }}    - LaTeX description, e.g. "a_n = 2n - 1"

        terms = {{ TERMS }}
        title_str = """{{ TITLE }}"""
        pattern_str = """{{ PATTERN }}"""

        title = Text(title_str, font_size=34).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Create term boxes
        boxes = VGroup()
        for term in terms:
            box = VGroup(
                Square(side_length=1.0, color=BLUE),
                MathTex(term, font_size=36)
            )
            boxes.add(box)

        boxes.arrange(RIGHT, buff=0.4).move_to(ORIGIN)

        # Animate each box appearing
        for box in boxes:
            self.play(Create(box[0]), Write(box[1]), run_time=0.4)
        self.wait(1)

        # Show the pattern
        pattern = MathTex(pattern_str, font_size=40, color=YELLOW).next_to(boxes, DOWN, buff=0.8)
        self.play(Write(pattern))
        self.wait(2)
