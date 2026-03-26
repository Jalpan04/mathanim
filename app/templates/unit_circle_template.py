from manim import *
import numpy as np


class MathScene(Scene):
    def construct(self):
        # Parameters:
        # {{ START_ANGLE }} - start in degrees, e.g. 0
        # {{ END_ANGLE }}   - end in degrees, e.g. 90

        start_deg = {{ START_ANGLE }}
        end_deg = {{ END_ANGLE }}

        # Build axes
        axes = Axes(
            x_range=[-1.5, 1.5, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": True},
        ).to_edge(LEFT)
        axes.add_coordinates()

        # Draw unit circle
        circle = Circle(radius=axes.x_length / (1.5 - (-1.5)), color=BLUE)
        circle.move_to(axes.c2p(0, 0))

        title = Text("The Unit Circle", font_size=34).to_edge(UP)
        self.play(Write(title), Create(axes), Create(circle))
        self.wait(1)

        # Angle tracker
        angle_tracker = ValueTracker(start_deg * DEGREES)

        # Dynamic dot on circle
        radius_num = axes.x_length / (1.5 - (-1.5))
        origin = axes.c2p(0, 0)

        def get_dot():
            ang = angle_tracker.get_value()
            x = np.cos(ang) * radius_num
            y = np.sin(ang) * radius_num
            return Dot(np.array([origin[0] + x, origin[1] + y, 0]), color=YELLOW)

        dot = always_redraw(get_dot)

        def get_radius_line():
            ang = angle_tracker.get_value()
            x = np.cos(ang) * radius_num
            y = np.sin(ang) * radius_num
            return Line(origin, np.array([origin[0] + x, origin[1] + y, 0]), color=GREEN)

        radius_line = always_redraw(get_radius_line)

        # cos/sin label
        cos_sin_label = always_redraw(lambda: MathTex(
            r"(\cos\theta, \sin\theta)",
            font_size=30,
            color=YELLOW
        ).next_to(get_dot(), UR, buff=0.15))

        self.play(Create(dot), Create(radius_line))
        self.play(FadeIn(cos_sin_label))
        self.wait(1)

        # Animate angle sweep
        self.play(
            angle_tracker.animate.set_value(end_deg * DEGREES),
            run_time=3,
            rate_func=linear
        )
        self.wait(2)
