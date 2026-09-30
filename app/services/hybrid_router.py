from pathlib import Path
from typing import Tuple, Optional
from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.services import curriculum_loader

llm = get_llm(temperature=0.0)

ARCHETYPE_KEYWORDS = {
    "graphing":    ["graph", "plot", "draw y=", "draw f(x)", "function", "curve", "parabola", "sine", "cosine", "cubic", "linear function"],
    "geometry":    ["area of", "perimeter", "circle", "triangle", "rectangle", "radius", "diameter", "circumference", "polygon", "shape", "quadrilateral", "construct", "construction", "rhombus", "trapezoid", "parallelogram", "diagonal", "tangent", "tangents", "square"],
    "number_line": ["number line", "addition on", "subtraction on", "inequality", "on number line", "integers on"],
    "equation":    ["solve", "simplify", "factor", "expand", "evaluate expression", "quadratic formula", "linear equation", "system of equations", "matrix", "vector", "determinant", "cramer"],
    "unit_circle": ["unit circle", "trig circle", "sin cos tan on circle", "radian", "trigonometric circle"],
    "calculus":    ["integral", "riemann sum", "derivative", "limit", "area under curve", "antiderivative", "definite integral"],
    "sequence":    ["sequence", "series", "arithmetic sequence", "geometric sequence", "terms of", "arithmetic progression", "progression", "ap:"],
}


def _keyword_precheck(user_input: str) -> Optional[str]:
    """Fast keyword scan. Returns archetype name or None."""
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


def _llm_classify(user_input: str) -> Optional[str]:
    """Ask the LLM to classify the archetype only."""
    prompt = f"""You are a Math Animation Classifier.
Classify this user request into exactly ONE of these animation archetypes:
- graphing: Plotting 2D functions, lines, curves
- geometry: Shapes, area, perimeter, angles, triangles, circles
- number_line: Number line addition, subtraction, inequalities
- equation: Step-by-step solving, factoring, simplifying, matrices, vectors
- unit_circle: Unit circle, trigonometric angles
- calculus: Integrals, derivatives, Riemann sums, limits
- sequence: Arithmetic or geometric sequences
- none: Does not fit any archetype

User Input: "{user_input}"

Output ONLY the single archetype word. No punctuation, no explanation."""

    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        raw = response.content.strip().lower().replace('"', '').replace("'", "")
        if raw in ARCHETYPE_KEYWORDS:
            return raw
        return None
    except Exception as e:
        print(f"Hybrid Router: LLM classification fallback: {e}")
        return None


def route_and_generate(user_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Classifies the user input into an archetype and loads the reference template.
    Returns (reference_template_code, archetype) or (None, None).
    """
    print(f"Hybrid Router: Routing input '{user_input}'")

    # Stage 0: Deterministic Template Engine check
    archetype: Optional[str] = None
    try:
        from app.services.template_engine import TemplateEngine
        t_match = TemplateEngine.match_and_generate(user_input)
        if t_match:
            _, _, archetype = t_match
            print(f"Hybrid Router: Stage 0 (TemplateEngine Match) -> {archetype}")
    except Exception as e:
        print(f"Hybrid Router: TemplateEngine check warning: {e}")

    # Stage 1: Curriculum keyword match
    if not archetype:
        archetype = curriculum_loader.find_archetype(user_input)
        if archetype:
            print(f"Hybrid Router: Stage 1 (Curriculum) -> {archetype}")

    # Stage 2: Fast keyword pre-check
    if not archetype:
        archetype = _keyword_precheck(user_input)
        if archetype:
            print(f"Hybrid Router: Stage 2 (Keywords) -> {archetype}")

    # Stage 3: LLM classification
    if not archetype:
        print("Hybrid Router: Running Stage 3 (LLM Classify)")
        archetype = _llm_classify(user_input)
        if archetype:
            print(f"Hybrid Router: Stage 3 (LLM) -> {archetype}")

    # Fallback to general equation archetype if still undetermined
    if not archetype:
        archetype = "equation"
        print("Hybrid Router: Defaulting to 'equation' archetype.")

    # Load reference template
    try:
        ref_code = _get_template_code(archetype)
        return ref_code, archetype
    except FileNotFoundError as e:
        print(f"Hybrid Router: {e}")

    return None, archetype
