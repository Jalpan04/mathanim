from app.agents.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), temperature=0)

def critic_node(state: GraphState):
    """
    Node D: Critic.
    Reviews the code for logic errors or hallucinations before execution.
    """
    print("---NODE D: CRITIC---")
    code = state['manim_code']
    
    prompt = f"""You are a senior Code Reviewer for Manim scripts.
    Review the following Python code for errors.
    
    Check for:
    1. Import `from manim import *`
    2. Class inheriting from Scene.
    3. Correct use of methods (no hallucinations).
    4. Syntax errors.
    
    Code:
    {code}
    
    If the code looks correct, output "APPROVED".
    If there are issues, output a brief critique explaining what to fix.
    """
    
    response = llm.invoke([SystemMessage(content=prompt)])
    review = response.content.strip()
    
    if review == "APPROVED":
        return {"error_log": None}
    else:
        # If rejected, we might want to send it back to Developer.
        # Ideally we would update the state with the critique so Developer can see it.
        # For this directed graph, we'll store it as an error log or feedback.
        return {"error_log": review}
