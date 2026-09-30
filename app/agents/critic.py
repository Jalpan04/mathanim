from app.agents.state import GraphState
from app.services.validator import RenderValidator


def critic_node(state: GraphState) -> dict:
    """
    Node D: Critic.
    Validates and auto-repairs the generated Manim code before rendering.
    """
    print("---NODE D: CRITIC---")
    code = state.get("manim_code", "")
    attempt_count = state.get("attempt_count", 0)

    if not code or not code.strip():
        return {
            "error_log": "REJECTED: Developer produced empty code.",
            "attempt_count": attempt_count + 1
        }

    # Run auto-corrections first
    code = RenderValidator.autofix(code)

    # Run pre-flight validation
    errors = RenderValidator.validate(code)

    if errors:
        error_summary = " | ".join(errors)
        print(f"Critic: Found {len(errors)} error(s): {error_summary}")
        return {
            "manim_code": code,
            "error_log": f"REJECTED: {error_summary}",
            "attempt_count": attempt_count + 1,
            "render_errors": errors,
        }

    print("Critic: Code passed all validation checks.")
    return {
        "manim_code": code,
        "error_log": None,
        "render_errors": [],
        "attempt_count": attempt_count,
    }
