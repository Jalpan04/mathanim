from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def generate_fallback_code(prompt: str) -> str:
    """
    Generates Manim code using local Ollama (gemma3:12b) when main agents fail.
    """
    print(f"Fallback Generator: Using Ollama (gemma3:12b) for '{prompt}'")
    
    try:
        # Initialize Ollama
        # Ensure 'ollama serve' is running
        llm = ChatOllama(model="gemma3:12b", temperature=0.1)
        
        # Dynamic Prompt Improvements
        base_system_prompt = """You are an expert Manim (Community Version) developer.
        Write a COMPLETE, RUNNABLE Python script using Manim to visualize the user's request.
        
        Rules:
        1. Class name MUST be `MathScene`.
        2. Inherit from `Scene` (unless told otherwise).
        3. Use `from manim import *`.
        4. Do NOT use markdown backticks. Output raw code only.
        5. Keep it simple and robust.
        """

        # Specialized Knowledge Injection
        specific_rules = ""
        prompt_lower = prompt.lower()

        if any(w in prompt_lower for w in ["graph", "plot", "function", "axis", "axes"]):
            specific_rules += """
            GRAPHING RULES:
            - You MUST define axes first: `axes = Axes(x_range=[-3, 3], y_range=[-3, 3], ...)`
            - Use `axes.add_coordinates()` (NOT add_coordinate_labels).
            - Plot functions using: `func = axes.plot(lambda x: x**2, color=BLUE)`
            - Use `Create(axes)` then `Create(func)`.
            """
        
        if any(w in prompt_lower for w in ["3d", "sphere", "cube", "surface", "z-axis"]):
            specific_rules += """
            3D RULES:
            - Class definition: `class MathScene(ThreeDScene):`
            - In `construct`: `self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES)`
            - Use `ThreeDAxes()` instead of `Axes()`.
            """
            
        if any(w in prompt_lower for w in ["area", "integral", "under user curve"]):
            specific_rules += """
            CALCULUS RULES:
            - To shade area: `area = axes.get_area(graph, x_range=[0, 2], color=YELLOW, opacity=0.5)`
            """

        full_system_prompt = f"{base_system_prompt}\n{specific_rules}"
        
        response = llm.invoke([
            SystemMessage(content=full_system_prompt),
            HumanMessage(content=f"Visualize this: {prompt}")
        ])
        
        # Clean Output
        code = response.content.strip()
        code = code.replace("```python", "").replace("```", "").strip()
        
        # Validation (Basic)
        if "class MathScene" not in code:
            raise ValueError("Ollama failed to generate valid Scene class.")
            
        return code

    except Exception as e:
        print(f"Ollama Fallback Failed: {e}")
        # Last Resort: Minimal Dummy
        return """
from manim import *
class MathScene(Scene):
    def construct(self):
        t = Text("Ollama & OpenAI Failed", color=RED)
        self.add(t)
"""
