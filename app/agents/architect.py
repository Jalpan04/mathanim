from app.agents.state import GraphState
from app.rag.store import ManimStore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

# Initialize LLM
llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), temperature=0)

def architect_node(state: GraphState):
    """
    Node B: Architect. 
    Analyzes the math solution and retrieves relevant Manim docs.
    """
    print("---NODE B: ARCHITECT---")
    user_input = state['user_input']
    math_solution = state['math_solution']
    
    # 1. Determine what to search for
    search_query_prompt = f"""
    Based on the following math problem and solution, generate a search query to find the best Manim (Community Version) objects to visualize it.
    
    Problem: {user_input}
    Solution Context: {math_solution}
    
    Output ONLY the search query string (e.g., "how to draw a tangent line to a curve").
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
    
    return {"retrieved_docs": retrieved_docs}
