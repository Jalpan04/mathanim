from app.agents.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), temperature=0)

def developer_node(state: GraphState):
    """
    Node C: Developer.
    Writes the Manim scene code.
    """
    print("---NODE C: DEVELOPER---")
    user_input = state['user_input']
    math_solution = state['math_solution']
    retrieved_docs = "\n\n".join(state['retrieved_docs'])
    
    prompt = f"""You are an expert Manim (Community Version) developer.
    
    Goal: Create a Manim scene to visualize the following math problem and solution.
    
    Problem: {user_input}
    
    Math Solution Breakdown:
    {math_solution}
    
    Relevant Documentation / Examples:
    {retrieved_docs}
    
    Instructions:
    1. Write a complete Python script.
    2. The script must define a class that inherits from `Scene` (or `MovingCameraScene`, `ThreeDScene` as appropriate).
    3. The class name should be `MathScene`.
    4. Use standard Manim syntax. Do NOT use `ManimGL` syntax. Use `from manim import *`.
    5. Ensure the animations are smooth and paced correctly (use `wait()`).
    6. Include explanations as `Text` or `Tex` objects on screen if helpful.
    7. Output ONLY the Python code.
    
    Code:
    """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    code = response.content.strip().replace("```python", "").replace("```", "")
    
    return {"manim_code": code}
