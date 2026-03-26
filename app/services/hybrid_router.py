import os
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from pathlib import Path

# Initialize LLM
llm = ChatOllama(model="gemma3:12b", temperature=0.1)

def get_template_content(template_name: str) -> str:
    template_path = Path("app/templates") / f"{template_name}_template.py"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def route_and_generate(user_input: str) -> str:
    """
    Parses user input and returns generated code using a template if possible.
    Returns None if no template matches.
    """
    print(f"Hybrid Router: Analyzing '{user_input}'")
    
    prompt = f"""
    You are a Math Intent Parser. 
    Analyze the user input and determine if it matches one of the following templates:
    1. 'graphing': For plotting 2D functions (e.g., "Graph x^2", "Plot sin(x)").
    2. 'geometry': For basic shape properties like area or perimeter (e.g., "Area of a circle with radius 3").
    3. 'none': For anything else.
    
    If you pick a template, extract the required parameters in JSON format.
    
    For 'graphing':
    - formula: The math formula in Python syntax (e.g., "x**2").
    - label: The LaTeX label (e.g., "f(x) = x^2").
    - x_range: list [min, max, step] (default [-5, 5, 1]).
    - y_range: list [min, max, step] (default [-5, 5, 1]).
    
    For 'geometry':
    - shape: "Circle", "Square", etc.
    - radius: float value (if applicable).
    - formula: LaTeX formula for area/perimeter.
    - calculation: LaTeX step-by-step substitution.
    
    User Input: "{user_input}"
    
    Output ONLY JSON.
    Example: {{"template": "graphing", "params": {{"formula": "x**2", "label": "f(x)=x^2", "x_range": [-5, 5, 1], "y_range": [-5, 5, 1]}}}}
    """
    
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        result = json.loads(response.content.strip())
        
        template_name = result.get("template")
        params = result.get("params")
        
        if template_name == "none" or not template_name:
            print("Hybrid Router: No template match. Falling back to Agents.")
            return None
            
        print(f"Hybrid Router: Matched template '{template_name}'")
        
        # Load template
        code = get_template_content(template_name)
        
        # Inject parameters
        for key, value in params.items():
            placeholder = "{{" + f" {key.upper()} " + "}}"
            if isinstance(value, list) or isinstance(value, (int, float)):
                code = code.replace(placeholder, str(value))
            else:
                code = code.replace(placeholder, str(value))
                
        return code
        
    except Exception as e:
        print(f"Hybrid Router Error: {e}")
        return None
