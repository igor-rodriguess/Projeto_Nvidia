from langgraph.graph import StateGraph, END

from app.core.startup_analysis_state import StartupAnalysisState
from app.agents.search_planner_agent import SearchPlannerAgent
from app.agents.source_collector_agent import SourceCollectorAgent
from app.agents.data_extractor_agent import DataExtractorAgent


def build_graph() -> StateGraph:
    graph = StateGraph(StartupAnalysisState)

    graph.add_node("search_planner", SearchPlannerAgent().run)
    graph.add_node("source_collector", SourceCollectorAgent().run)
    graph.add_node("data_extractor", DataExtractorAgent().run)

    graph.set_entry_point("search_planner")
    graph.add_edge("search_planner", "source_collector")
    graph.add_edge("source_collector", "data_extractor")
    graph.add_edge("data_extractor", END)

    return graph.compile()


startup_discovery_graph = build_graph()
