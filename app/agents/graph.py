from langgraph.graph import StateGraph, END
from app.agents.state import GraphState
from app.agents.mathematician import mathematician_node
from app.agents.architect import architect_node
from app.agents.developer import developer_node
from app.agents.critic import critic_node

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
    
    # Speed Mode: Critic Disabled
    workflow.add_edge("developer", END)
    
    # workflow.add_edge("developer", "critic")
    # workflow.add_conditional_edges(...)
    
    app = workflow.compile()
    return app

if __name__ == "__main__":
    # Test run
    app = define_graph()
    print("Graph compiled successfully.")
