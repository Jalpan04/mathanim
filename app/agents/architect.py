from app.agents.state import GraphState
from app.rag.store import ManimStore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.chat_models import ChatOllama
import os

# Initialize LLM
llm = ChatOllama(model="gemma3:12b", temperature=0.1)

def architect_node(state: GraphState):
    """
    Node B: Architect. 
    Analyzes the math solution and retrieves relevant Manim docs.
    """
    print("---NODE B: ARCHITECT---")
    user_input = state['user_input']
    math_solution = state['math_solution']
    
    # 0. Check Memory (Self-Improving System)
    from app.rag.memory import SolutionMemory
    memory = SolutionMemory()
    proven_code = memory.recall_experience(user_input)
    
    if proven_code:
        print("Architect: Found proven solution in memory! Skipping RAG.")
        return {"proven_code": proven_code, "retrieved_docs": []}

    # 1. Determine what to search for
    search_query_prompt = f"""
    You are a Senior Animation Director.
    
    Goal: Identify the BEST Manim objects/animations for this math problem.
    
    Problem: {user_input}
    Math Context: {math_solution}
    
    Task:
    Generate a specific Keyword Search Query for the Manim documentation.
    -   Example: "Axes Graph Plot" (for graphing)
    -   Example: "Circle Arc Rotate" (for geometry)
    -   Example: "ThreeDScene Sphere" (for 3D)
    
    Output ONLY the query string.
    """
    
    response = llm.invoke([SystemMessage(content=search_query_prompt)])
    query = response.content.strip()
    print(f"Generated Search Query: {query}")
    
    # 2. Retrieve docs
    # Note: efficient instantiation/singleton usage suggested for production
    store = ManimStore() 
    results = store.query(query, n_results=3)
    
    retrieved_docs = []
    if results['documents']:
        # Flatten the list of lists
        retrieved_docs = results['documents'][0]
        
    print(f"Retrieved {len(retrieved_docs)} docs.")
    
    return {"retrieved_docs": retrieved_docs, "proven_code": None}
