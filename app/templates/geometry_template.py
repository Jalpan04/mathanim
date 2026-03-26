from manim import *

class MathScene(Scene):
    def construct(self):
        # Parameters to be replaced
        # {{ SHAPE }} - e.g. "Circle"
        # {{ RADIUS }} - e.g. "2"
        # {{ FORMULA }} - e.g. "Area = \\pi r^2"
        # {{ CALCULATION }} - e.g. "Area = \\pi (2)^2 = 4\\pi"
        
        radius_val = {{ RADIUS }}
        
        shape = Circle(radius=radius_val)
        shape.set_fill(BLUE, opacity=0.5)
        # Ensure it fits the screen (Max height is 8, so 6 is safe)
        if shape.height > 6:
            shape.scale_to_fit_height(6)
        
        radius_line = Line(shape.get_center(), shape.get_right(), color=RED)
        radius_label = MathTex("r = " + str(radius_val)).next_to(radius_line, UP, buff=0.1)
        
        formula = MathTex("""{{ FORMULA }}""").to_edge(UP, buff=0.5)
        calculation = MathTex("""{{ CALCULATION }}""").next_to(formula, DOWN, buff=0.5)
        
        # Animation
        self.play(Create(shape))
        self.play(Create(radius_line), Write(radius_label))
        self.wait(1)
        self.play(Write(formula))
        self.wait(1)
        self.play(Write(calculation))
        self.wait(2)
