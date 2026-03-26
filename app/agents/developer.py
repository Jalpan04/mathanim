from app.agents.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama
import os

llm = ChatOllama(model="gemma3:12b", temperature=0.1)

def developer_node(state: GraphState):
    """
    Node C: Developer.
    Writes the Manim scene code.
    """
    print("---NODE C: DEVELOPER---")
    user_input = state['user_input']
    math_solution = state['math_solution']
    
    # 0. Check for Proven Code (Memory)
    if state.get("proven_code"):
        print("Developer: Using proven code from memory.")
        return {"manim_code": state["proven_code"]}

    retrieved_docs = "\n\n".join(state['retrieved_docs'])
    
    previous_error = state.get("error_log")
    if previous_error:
        print(f"Developer: Fixing previous error: {previous_error}")
        prompt = f"""You are now the CODE FIXER AGENT.
        
        Your Goal: Fix the broken Manim script below.
        
        CONTEXT:
        - Original Task: {user_input}
        - Error Log:
        {previous_error}
        
        INSTRUCTIONS:
        1. Identify the line causing the error.
        2. Fix the syntax or logic.
        3. Do NOT change anything else unless necessary.
        4. Output ONLY the fixed Python code.
        """
    else:
        # Standard Generation Prompt
        # Enhanced Prompt: Layout & Clarity Focus
        prompt = f"""You are an Elite Manim (Community) Developer.
        
        Goal: Create an EDUCATIONAL video for: "{user_input}"
        
        Math Context (Animation Plan):
        {math_solution}
        
        Docs:
        {retrieved_docs}
        
        --- LAYOUT & CLARITY RULES ---
        1.  **Typography**: Use `MathTex` for equations. ALWAYS wrap math symbols in `MathTex` (e.g. `MathTex("\\pi r^2")`).
        2.  **Tex vs MathTex**: Use `Text` for titles/labels. Use `MathTex` for formulas. NEVER put raw symbols like `\pi` or `π` inside `Tex()` or `Text()` without math environment.
        3.  **Spacing**: Do not crowd the screen. Use `VGroup` and `arrange(DOWN, buff=1)`.
        4.  **Timing**: Give the viewer time to read. `self.wait(1)` after text appears.
        
        --- TECHNICAL RULES ---
        1.  **Class Name**: `MathScene`.
        2.  **Imports**: `from manim import *`.
        3.  **Vector Math**: NEVER add a scalar to a vector (e.g. `np.array + 1` is OK but `manim.Line + scalar` is bad). For points near a circle, use `circle.point_at_angle(PI/4)` or `circle.get_center() + radius * UP`.
        4.  **No Interactivity**: Do NOT use `input()`.
        
        Output ONLY the raw Python code.
        Code:
        """
    
    print("Developer: Prompting LLM for Manim code...")
    response = llm.invoke([SystemMessage(content=prompt)])
    print("Developer: LLM generation complete.")
    code = response.content.strip().replace("```python", "").replace("```", "")
    
    return {"manim_code": code}
