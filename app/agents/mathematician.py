from app.agents.state import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
from langchain_experimental.utilities import PythonREPL
import os

# Initialize LLM (Local Ollama)
llm = ChatOllama(model="gemma3:12b", temperature=0.1)

def mathematician_node(state: GraphState):
    """
    Node A: Solves the math problem using SymPy.
    """
    print("---NODE A: MATHEMATICIAN---")
    user_input = state['user_input']
    
    system_prompt = """You are a Math Simplifier for Animation.
    
    Goal: Break down the math problem into simple, visualizable steps for the Developer.
    
    Instructions:
    1.  **Solve**: Calculate the necessary values (domains, ranges, roots).
    2.  **Simplify**: Convert complex math into simple steps.
    3.  **Plan**: List the **Key Frames** needed for the animation.
        -   Frame 1: Show Equation.
        -   Frame 2: Graph Function (domain X to Y).
        -   Frame 3: Highlight Key Points.
    
    Output Constraints:
    -   Output valid Python code (using SymPy) that prints this "Visual Plan".
    -   The output should be the logical "script" for the video.
    """
    
    # Simple generation (in production, use a structured output chain)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Problem: {user_input}")
    ])
    
    code = response.content.strip().replace("```python", "").replace("```", "")
    
    print(f"Generated SymPy code:\n{code}")
    
    # Execute code SAFELY (Docker Sandbox - Production Ready)
    import subprocess
    import uuid
    from pathlib import Path
    
    # 1. Setup paths
    # We use 'generated_scenes' because we know it's mountable/accessible
    temp_dir = Path("generated_scenes")
    temp_dir.mkdir(exist_ok=True)
    
    script_name = f"calc_{uuid.uuid4().hex}.py"
    host_script_path = temp_dir / script_name
    
    # 2. Write code to file
    with open(host_script_path, "w", encoding="utf-8") as f:
        f.write(code)
        
    print(f"Sandbox: Script written to {host_script_path}")
    
    try:
        # 3. Docker Command
        # Mount the entire dir to /app/scenes for simplicity
        abs_temp_dir = temp_dir.resolve()
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{abs_temp_dir}:/app/scenes",
            "mathanim-renderer", 
            "python3", f"/app/scenes/{script_name}"
        ]
        
        # 4. Run with timeout
        print(f"Sandbox: Running {script_name} in Docker...")
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if res.returncode == 0:
            result = res.stdout
        else:
            result = f"Error (Exit Code {res.returncode}):\n{res.stderr}\nStdout: {res.stdout}"
            
    except subprocess.TimeoutExpired:
        result = "Error: Computation timed out (20s limit)."
    except Exception as e:
        result = f"Sandbox Infrastructure Error: {e}"
    finally:
        # 5. Cleanup
        if host_script_path.exists():
            try:
                os.remove(host_script_path)
                print("Sandbox: Concierge cleaned up temp file.")
            except:
                pass

    print(f"Execution Result:\n{result}")

    print(f"Execution Result:\n{result}")
    
    # If empty or error, we might need to handle it. 
    # For this prototype, we assume success or stick the error in the solution.
    if not result:
        result = "No output from SymPy code. Code might be correct but didn't print anything."
    
    full_solution = f"## Math Analysis\n\nCode used:\n```python\n{code}\n```\n\nResult:\n{result}"
    
    return {"math_solution": full_solution}
