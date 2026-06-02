from langgraph.graph import StateGraph, END

from agents import (
    content_agent,
    quality_agent,
    structure_critic,
    repo_analyzer,
    reviewer
)
from  state import A3State
from agents import llm_enrichment_agent

def route_reviewer(state):
    if state.get("attempts", 0) >= 2:
        return "pass"
    return state.get("status", "pass")

def build_graph():

    graph = StateGraph(A3State)

    graph.add_node("analyzer", repo_analyzer)
    graph.add_node("content", content_agent)

    graph.add_node("structure", structure_critic)
    graph.add_node("quality", quality_agent)

    graph.add_node("reviewer", reviewer)
    graph.add_node("llm_enricher", llm_enrichment_agent)
    graph.set_entry_point("analyzer")

    graph.add_edge("analyzer", "content")

    graph.add_edge("analyzer", "structure")
    graph.add_edge("analyzer", "quality")


    graph.add_edge("content", "reviewer")


    graph.add_edge("quality", "reviewer")
    graph.add_edge("structure", "reviewer")
    graph.add_edge("reviewer", "llm_enricher")



    graph.add_conditional_edges(
        "llm_enricher",
        lambda s: s["status"],
        {
            "retry": "content",
            "pass": END
        }
    )

    return graph.compile()