from app.agents.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_experimental.utilities import PythonREPL
import os

# Initialize LLM (Ensure OPENAI_API_KEY is set in .env)
# For now, we will assume the key is present or mock it if needed.
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), temperature=0)

def mathematician_node(state: GraphState):
    """
    Node A: Solves the math problem using SymPy.
    """
    print("---NODE A: MATHEMATICIAN---")
    user_input = state['user_input']
    
    # Prompt to generate SymPy code
    system_prompt = """You are a rigorous mathematician. 
    Your goal is to solve the user's math problem using Python and SymPy.
    Do NOT just answer in text. You MUST write a Python script that uses SymPy to calculate the solution.
    Output ONLY the valid Python code. No markdown formatting like ```python.
    Verify your constraints. If the problem is "Graph y=x^2", you should calculate the range or significant points if useful, 
    but primarily you are verifying the math.
    """
    
    # Simple generation (in production, use a structured output chain)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Problem: {user_input}")
    ])
    
    code = response.content.strip().replace("```python", "").replace("```", "")
    
    print(f"Generated SymPy code:\n{code}")
    
    # Execute code
    repl = PythonREPL()
    result = repl.run(code)
    
    print(f"Execution Result:\n{result}")
    
    # If empty or error, we might need to handle it. 
    # For this prototype, we assume success or stick the error in the solution.
    if not result:
        result = "No output from SymPy code. Code might be correct but didn't print anything."
    
    full_solution = f"## Math Analysis\n\nCode used:\n```python\n{code}\n```\n\nResult:\n{result}"
    
    return {"math_solution": full_solution}
