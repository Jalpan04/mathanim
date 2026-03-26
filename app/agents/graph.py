from langgraph.graph import StateGraph, END
from app.agents.state import GraphState
from app.agents.mathematician import mathematician_node
from app.agents.architect import architect_node
from app.agents.developer import developer_node
from app.agents.critic import critic_node


def should_retry(state: GraphState) -> str:
    """
    Conditional edge: if critic found errors and we haven't retried too many times,
    send back to the developer to fix.
    """
    has_error = bool(state.get("error_log"))
    attempt_count = state.get("attempt_count", 0)
    
    if has_error and attempt_count < 2:
        print(f"Graph: Retrying developer (attempt {attempt_count + 1}/2)...")
        return "retry"
    
    if has_error:
        print("Graph: Max retries reached. Proceeding with best available code.")
    
    return "done"


def define_graph():
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("mathematician", mathematician_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("critic", critic_node)

    # Define Edges
    workflow.set_entry_point("mathematician")

    workflow.add_edge("mathematician", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "critic")

    # Conditional: retry developer on failure (max 2 retries), else finish
    workflow.add_conditional_edges(
        "critic",
        should_retry,
        {
            "retry": "developer",
            "done": END,
        }
    )

    app = workflow.compile()
    return app


if __name__ == "__main__":
    app = define_graph()
    print("Graph compiled successfully.")
