from app.agents.state import GraphState
from app.services.validator import RenderValidator


def critic_node(state: GraphState):
    """
    Node D: Critic.
    Validates the generated Manim code before rendering.
    Uses RenderValidator for Python AST, LaTeX, and size checks.
    On failure, returns error_log so the developer retries.
    """
    print("---NODE D: CRITIC---")
    code = state.get("manim_code", "")
    attempt_count = state.get("attempt_count", 0)

    if not code or not code.strip():
        return {
            "error_log": "REJECTED: Developer produced empty code.",
            "attempt_count": attempt_count + 1
        }

    # Run pre-flight validation
    errors = RenderValidator.validate(code)

    if errors:
        error_summary = " | ".join(errors)
        print(f"Critic: Found {len(errors)} error(s): {error_summary}")
        return {
            "error_log": f"REJECTED: {error_summary}",
            "attempt_count": attempt_count + 1,
            "render_errors": errors,
        }

    print("Critic: Code passed all validation checks.")
    return {
        "error_log": None,
        "render_errors": [],
        "attempt_count": attempt_count,
    }
