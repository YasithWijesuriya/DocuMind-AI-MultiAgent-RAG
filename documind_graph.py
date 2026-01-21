from langgraph.graph import StateGraph
from pipelines.graph_state import DocuMindState
from pipelines.graph_nodes import *

graph = StateGraph(DocuMindState)

graph.add_node("memory_read", memory_read_node)
graph.add_node("rewrite", rewrite_node)
graph.add_node("router", router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("summary", summary_node)
graph.add_node("compare", compare_node)
graph.add_node("expert", expert_node)
graph.add_node("synthesis", synthesis_node)
graph.add_node("validator", validator_node)
graph.add_node("memory_write", memory_write_node)


graph.set_entry_point("memory_read")

graph.add_edge("memory_read", "rewrite")
graph.add_edge("rewrite", "router")

def route_decision(state):
    return state["route"]

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "retrieval": "retrieval",
        "summary": "summary",
        "compare": "compare",
        "expert": "expert"  
    }
)

graph.add_edge("retrieval", "synthesis")
graph.add_edge("summary", "synthesis")
graph.add_edge("compare", "synthesis")
graph.add_edge("expert", "synthesis")
graph.add_edge("synthesis", "validator")
graph.add_edge("validator", "memory_write")

app = graph.compile()
