from manim import *

class MathScene(Scene):
    def construct(self):
        # Parameters to be replaced by the router
        # {{ FORMULA }} - e.g. "x**2"
        # {{ X_RANGE }} - e.g. "[-3, 3, 1]"
        # {{ Y_RANGE }} - e.g. "[-3, 3, 1]"
        # {{ LABEL }} - e.g. "f(x) = x^2"
        
        formula_str = """{{ FORMULA }}"""
        label_str = """{{ LABEL }}"""
        
        axes = Axes(
            x_range={{ X_RANGE }},
            y_range={{ Y_RANGE }},
            axis_config={"include_tip": True}
        )
        axes.add_coordinates()
        
        # Define the function
        import numpy as np
        # Need to handle potential issues with certain functions
        func = axes.plot(lambda x: eval(formula_str, {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi}), color=BLUE)
        
        # Label for the function
        label = MathTex(label_str, color=BLUE).next_to(axes, UP, buff=0.5).to_edge(RIGHT)
        
        # Animation
        self.play(Create(axes))
        self.wait(1)
        self.play(Create(func), Write(label), run_time=2)
        self.wait(2)
