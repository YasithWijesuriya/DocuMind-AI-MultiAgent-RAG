# 1. Imports
from langgraph.graph import StateGraph
from graph_state import DocuMindState
from graph_nodes import *

# 2. Create Graph
graph = StateGraph(DocuMindState)

# 3. Add Nodes
graph.add_node("router", router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("summary", summary_node)
graph.add_node("compare", compare_node)
graph.add_node("synthesis", synthesis_node)
graph.add_node("validator", validator_node)

# 4. Set Entry Point
graph.set_entry_point("router")


def route_decision(state):
    return state["route"]

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "retrieval": "retrieval",
        "summary": "summary",
        "compare": "compare",
        "expert": "summary"  # temporary
    }
)

# 6. Normal Edges
graph.add_edge("retrieval", "synthesis")
graph.add_edge("summary", "synthesis")
graph.add_edge("compare", "synthesis")
graph.add_edge("synthesis", "validator")

# 7. Compile Graph (LAST STEP)
app = graph.compile()
