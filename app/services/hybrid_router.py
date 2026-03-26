import os
import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage
from pathlib import Path
from app.services import curriculum_loader

# Initialize LLM
llm = ChatOllama(model="gemma3:12b", temperature=0.1)

# Supported archetypes and their keyword hints
ARCHETYPE_KEYWORDS = {
    "graphing":    ["graph", "plot", "draw y=", "draw f(x)", "function", "curve", "parabola", "sine", "cosine"],
    "geometry":    ["area of", "perimeter", "circle", "triangle", "rectangle", "radius", "diameter", "circumference"],
    "number_line": ["number line", "addition on", "subtraction on", "inequality", "on number line"],
    "equation":    ["solve", "simplify", "factor", "expand", "evaluate expression", "foil", "quadratic formula"],
    "unit_circle": ["unit circle", "trig circle", "sin cos tan on circle"],
    "calculus":    ["integral", "riemann sum", "derivative", "limit", "area under curve", "antiderivative"],
    "sequence":    ["sequence", "series", "arithmetic sequence", "geometric sequence"],
}


def _keyword_precheck(user_input: str) -> str | None:
    """
    Fast O(1) keyword scan before calling Ollama.
    Returns archetype name or None.
    """
    lower = user_input.lower()
    for archetype, keywords in ARCHETYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return archetype
    return None


def _get_template_code(template_name: str) -> str:
    template_path = Path("app/templates") / f"{template_name}_template.py"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def _inject_params(code: str, params: dict) -> str:
    """Inject parameters into template placeholders like {{ KEY }}."""
    for key, value in params.items():
        placeholder = "{{" + f" {key.upper()} " + "}}"
        if isinstance(value, list):
            code = code.replace(placeholder, str(value))
        elif isinstance(value, (int, float)):
            code = code.replace(placeholder, str(value))
        else:
            code = code.replace(placeholder, str(value))
    return code


def route_and_generate(user_input: str) -> tuple[str | None, str | None]:
    """
    3-stage hybrid routing:
    1. Curriculum registry exact keyword match
    2. Fast keyword pre-check
    3. Ollama LLM classification (fallback)

    Returns (manim_code, archetype) or (None, None) if no template match.
    """
    print(f"Hybrid Router: Analyzing '{user_input}'")

    # --- Stage 1: Curriculum Registry ---
    topic = curriculum_loader.find_by_keyword(user_input)
    if topic:
        archetype = topic["archetype"]
        params = topic["params"]
        print(f"Hybrid Router: Curriculum match -> topic {topic['id']} ({archetype})")
        try:
            code = _get_template_code(archetype)
            code = _inject_params(code, params)
            return code, archetype
        except Exception as e:
            print(f"Hybrid Router: Template injection failed for curriculum match: {e}")
            # Fall through to LLM

    # --- Stage 2: Fast keyword pre-check ---
    archetype = _keyword_precheck(user_input)
    if archetype:
        print(f"Hybrid Router: Keyword pre-check matched '{archetype}'. Asking LLM for params only.")
        params = _llm_extract_params(user_input, archetype)
        if params:
            try:
                code = _get_template_code(archetype)
                code = _inject_params(code, params)
                return code, archetype
            except Exception as e:
                print(f"Hybrid Router: Template injection failed for '{archetype}': {e}")
                return None, None

    # --- Stage 3: Full LLM classification ---
    print("Hybrid Router: No keyword match, running full LLM classification.")
    result = _llm_classify_and_extract(user_input)
    if not result:
        return None, None

    template_name = result.get("template")
    params = result.get("params")

    if not template_name or template_name == "none":
        print("Hybrid Router: LLM returned no template. Falling back to Agent Swarm.")
        return None, None

    print(f"Hybrid Router: LLM matched template '{template_name}'")
    try:
        code = _get_template_code(template_name)
        code = _inject_params(code, params)
        return code, template_name
    except Exception as e:
        print(f"Hybrid Router: Template injection error: {e}")
        return None, None


def _llm_extract_params(user_input: str, archetype: str) -> dict | None:
    """Ask the LLM only to extract params for a known archetype (faster)."""
    param_schemas = {
        "graphing": '{"formula": "python_expr", "label": "latex_str", "x_range": [min,max,step], "y_range": [min,max,step]}',
        "geometry": '{"shape": "Circle|Triangle|Rectangle", "radius": 2.0, "formula": "latex", "calculation": "latex"}',
        "number_line": '{"start": -5, "end": 10, "a": 3, "b": 2, "operation": "addition|subtraction", "label": "description"}',
        "equation": '{"title": "plain text", "steps": ["latex_step1", "latex_step2"]}',
        "unit_circle": '{"start_angle": 0, "end_angle": 360}',
        "calculus": '{"func": "x**2", "a": 0, "b": 2, "n_rects": 6, "label": "latex_integral"}',
        "sequence": '{"terms": ["1","3","5"], "title": "plain text", "pattern": "a_n = ..."}',
    }
    schema = param_schemas.get(archetype, "{}")

    prompt = f"""Extract parameters for a '{archetype}' math animation from this request: "{user_input}"
Output ONLY JSON matching this schema: {schema}
Use sensible defaults for missing values. Output ONLY valid JSON, no explanation."""

    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        raw = response.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Hybrid Router: Param extraction failed: {e}")
        return None


def _llm_classify_and_extract(user_input: str) -> dict | None:
    """Full LLM classification + param extraction for unknown inputs."""
    prompt = f"""You are a Math Intent Parser.
Analyze the user input and determine if it matches one of these templates:
1. 'graphing': Plotting 2D functions, lines, curves (e.g., "Graph x^2", "draw y=4", "plot sin(x)")
2. 'geometry': Shapes, area, perimeter, radius (e.g., "Area of a circle with radius 3")
3. 'number_line': Number line addition/subtraction/inequalities
4. 'equation': Solving, factoring, simplifying equations step-by-step
5. 'unit_circle': Unit circle, trig angles
6. 'calculus': Integrals, derivatives, Riemann sums, limits
7. 'sequence': Arithmetic or geometric sequences
8. 'none': Anything else

User Input: "{user_input}"

If you pick a template, extract its parameters:
- graphing: {{"template": "graphing", "params": {{"formula": "x**2", "label": "f(x)=x^2", "x_range": [-5,5,1], "y_range": [-5,5,1]}}}}
- geometry: {{"template": "geometry", "params": {{"shape": "Circle", "radius": 2.0, "formula": "\\\\pi r^2", "calculation": "\\\\pi(2)^2=4\\\\pi"}}}}
- equation: {{"template": "equation", "params": {{"title": "Solving", "steps": ["step1", "step2"]}}}}
- sequence: {{"template": "sequence", "params": {{"terms": ["1","3","5"], "title": "Sequence", "pattern": "a_n"}}}}
- calculus: {{"template": "calculus", "params": {{"func": "x**2", "a": 0, "b": 2, "n_rects": 6, "label": "\\\\int_0^2 x^2 dx"}}}}
- unit_circle: {{"template": "unit_circle", "params": {{"start_angle": 0, "end_angle": 360}}}}
- number_line: {{"template": "number_line", "params": {{"start": -5, "end": 10, "a": 3, "b": 2, "operation": "addition", "label": "3+2=5"}}}}
- none: {{"template": "none", "params": {{}}}}

Output ONLY valid JSON. No markdown, no explanation."""

    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        raw = response.content.strip()
        print(f"Hybrid Router: Raw LLM Response: {raw[:200]}")
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Hybrid Router: LLM classification failed: {e}")
        return None
