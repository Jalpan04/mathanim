from app.agents.state import GraphState
from app.rag.store import ManimStore
from app.rag.memory import SolutionMemory
from app.core.llm import get_llm

ARCHETYPE_QUERIES = {
    "graphing": "Axes plot add_coordinates MathTex curve",
    "geometry": "Circle Polygon Line Square MathTex next_to",
    "calculus": "Axes get_area get_riemann_rectangles MathTex",
    "unit_circle": "Circle ValueTracker always_redraw DashedLine MathTex",
    "equation": "MathTex VGroup arrange TransformMatchingTex",
    "number_line": "NumberLine Dot Arrow MathTex",
    "sequence": "MathTex VGroup arrange FadeIn",
}


def architect_node(state: GraphState) -> dict:
    """
    Node B: Architect.
    Recalls proven solutions from memory or retrieves relevant Manim doc snippets via ChromaDB RAG.
    """
    print("---NODE B: ARCHITECT---")
    user_input = state["user_input"]
    archetype = state.get("archetype", "general")

    # 1. Check if template_code is already available
    if state.get("template_code"):
        print("Architect: Template code already provided by TemplateEngine. Skipping RAG.")
        return {"retrieved_docs": []}

    # 2. Check Solution Memory first
    try:
        memory = SolutionMemory()
        proven_code = memory.recall_experience(user_input)
        if proven_code:
            print("Architect: Found proven solution in memory! Skipping RAG.")
            return {"proven_code": proven_code, "retrieved_docs": []}
    except Exception as e:
        print(f"Architect: Memory recall error (non-fatal): {e}")

    # 3. Build RAG query
    base_query = ARCHETYPE_QUERIES.get(archetype, "")
    query = f"{archetype} {user_input} {base_query}".strip()

    # 3. Retrieve docs from ChromaDB store
    retrieved_docs = []
    try:
        store = ManimStore()
        results = store.query(query, n_results=3)
        if results.get("documents") and results["documents"]:
            retrieved_docs = results["documents"][0]
        print(f"Architect: Retrieved {len(retrieved_docs)} doc snippets from ChromaDB.")
    except Exception as e:
        print(f"Architect: RAG query error (non-fatal): {e}")

    return {
        "retrieved_docs": retrieved_docs,
    }
