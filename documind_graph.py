from langgraph.graph import StateGraph, END
from pipelines.graph_state import DocuMindState
from pipelines.graph_nodes import (
    memory_read_node,
    rewrite_node,
    router_node,
    retrieval_node,
    compare_node,
    synthesis_node,
    validator_node,
    memory_write_node
)

graph = StateGraph(DocuMindState)

# Add all nodes
graph.add_node("memory_read", memory_read_node)
graph.add_node("rewrite", rewrite_node)
graph.add_node("router", router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("compare", compare_node)
graph.add_node("synthesis", synthesis_node)
graph.add_node("validator", validator_node)
graph.add_node("memory_write", memory_write_node)

graph.set_entry_point("memory_read")

# Add edges for main flow (SEQUENTIAL)
graph.add_edge("memory_read", "rewrite")
graph.add_edge("rewrite", "router")

def route_decision(state):
    """
    Conditional routing based on router decision
    """
    route = state.get("route", "retrieval")
    print(f">>> Router decided: {route}")
    return route

# ALWAYS start with retrieval regardless of route
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "retrieval": "retrieval",
        "summary": "retrieval",
        "expert": "retrieval",
        "compare": "compare"
    }
)

graph.add_edge("retrieval", "synthesis")
graph.add_edge("compare", "synthesis")

graph.add_edge("synthesis", "validator")
graph.add_edge("validator", "memory_write")
graph.add_edge("memory_write", END)

app = graph.compile()