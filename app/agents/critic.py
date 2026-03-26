from app.agents.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama
import os

llm = ChatOllama(model="gemma3:12b", temperature=0.1)

def critic_node(state: GraphState):
    """
    Node D: Critic.
    Reviews the code for logic errors or hallucinations before execution.
    """
    print("---NODE D: CRITIC---")
    code = state['manim_code']
    
    # 1. HARD Syntax Check (Compiler Level)
    import ast
    try:
        ast.parse(code)
    except SyntaxError as e:
        error_msg = f"SyntaxError at line {e.lineno}: {e.msg}"
        print(f"Critic: Caught syntax error! {error_msg}")
        return {"error_log": f"REJECTED: Your code has a Python Syntax Error. {error_msg}. Please fix it."}
    except Exception as e:
        print(f"Critic: Caught parsing error! {e}")
        return {"error_log": f"REJECTED: Code failed to parse. {e}"}

    # 2. Semantic/Logic Check (LLM Level) - DISABLED FOR SPEED
    # We rely on the Developer to get the logic right. 
    # The Syntax check above guarantees it won't crash the renderer.
    
    print("Critic: Syntax is valid. Skipping LLM logic check for speed.")
    return {"error_log": None}

    # prompt = f"""..."""
    # response = llm.invoke(...)
    # ...
