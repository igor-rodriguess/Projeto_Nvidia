from langgraph.graph import END, StateGraph

from app.agents.data_extractor_agent import data_extractor_agent
from app.agents.search_planner_agent import search_planner_agent
from app.agents.source_collector_agent import source_collector_agent
from app.core.startup_analysis_state import StartupAnalysisState


def _route_after_collection(state: StartupAnalysisState) -> str:
    if state.get("sources"):
        return "data_extractor"

    if state.get("attempt_count", 0) < 3:
        return "search_planner"

    return "controlled_error"


def _controlled_error(state: StartupAnalysisState) -> StartupAnalysisState:
    state.setdefault("errors", []).append(
        "startup_discovery_graph: no sources found after 3 attempts"
    )
    state["sources"] = state.get("sources", [])
    state["startups"] = state.get("startups", [])
    return state


def build_graph():
    graph = StateGraph(StartupAnalysisState)

    graph.add_node("search_planner", search_planner_agent)
    graph.add_node("source_collector", source_collector_agent)
    graph.add_node("data_extractor", data_extractor_agent)
    graph.add_node("controlled_error", _controlled_error)

    graph.set_entry_point("search_planner")
    graph.add_edge("search_planner", "source_collector")
    graph.add_conditional_edges("source_collector", _route_after_collection)
    graph.add_edge("data_extractor", END)
    graph.add_edge("controlled_error", END)

    return graph.compile()


startup_discovery_graph = build_graph()
