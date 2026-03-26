from manim import *


class MathScene(Scene):
    def construct(self):
        # Parameters injected by hybrid_router:
        # {{ START }} - e.g. -5
        # {{ END }}   - e.g. 5
        # {{ A }}     - first value e.g. 3
        # {{ B }}     - second value e.g. 2
        # {{ OPERATION }} - e.g. "addition" or "subtraction"
        # {{ LABEL }} - e.g. "3 + 2 = 5"

        start_val = {{ START }}
        end_val = {{ END }}
        a = {{ A }}
        b = {{ B }}
        operation = "{{ OPERATION }}"
        label_str = """{{ LABEL }}"""

        number_line = NumberLine(
            x_range=[start_val, end_val, 1],
            length=10,
            include_numbers=True,
            include_tip=True,
        )

        title = Text(label_str, font_size=36).to_edge(UP)
        self.play(Create(number_line), Write(title))
        self.wait(1)

        # Mark starting point
        dot_a = Dot(number_line.n2p(a), color=YELLOW)
        label_a = MathTex(str(a), color=YELLOW).next_to(dot_a, UP)
        self.play(Create(dot_a), Write(label_a))
        self.wait(0.5)

        # Animate the operation with an arrow
        result = a + b if operation != "subtraction" else a - b
        arrow = Arrow(
            start=number_line.n2p(a),
            end=number_line.n2p(result),
            color=GREEN,
            buff=0,
        ).shift(UP * 0.5)
        arrow_label = MathTex(f"{'+'  if operation != 'subtraction' else '-'}{abs(b)}", color=GREEN)
        arrow_label.next_to(arrow, UP, buff=0.1)

        self.play(Create(arrow), Write(arrow_label))
        self.wait(0.5)

        # Mark result
        dot_result = Dot(number_line.n2p(result), color=RED)
        label_result = MathTex(str(result), color=RED).next_to(dot_result, DOWN, buff=0.4)
        self.play(Create(dot_result), Write(label_result))
        self.wait(2)
