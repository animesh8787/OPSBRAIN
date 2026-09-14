import logging
import re

from langgraph.graph import StateGraph, END
from agents.graph_state import AgentState
from agents.copilot_agent import generate_answer
from app.llm.generate import generate
from rag.citation import extract_and_verify_citations
from rag.reranker import rerank
from app.db.postgres import AsyncSessionLocal
from app.services.search_service import hybrid_search
from app.services.graph_service import get_equipment_neighborhood

logger = logging.getLogger(__name__)

EQUIPMENT_TAG_PATTERN = re.compile(r"\b[A-Z]{1,3}-\d{2,4}[A-Z]?\b")


async def classify_intent_node(state: AgentState) -> AgentState:
    prompt = f"""Classify this query into exactly one category: copilot, maintenance, compliance.
Query: "{state['query']}"
Respond with only the category name."""

    try:
        raw = await generate(prompt, json_mode=False)
        raw = raw.strip().lower()
    except Exception as exc:
        logger.warning("Intent classification failed: %s", exc)
        raw = ""

    if raw in {"copilot", "maintenance", "compliance"}:
        intent = raw
    else:
        intent = "copilot"

    return {**state, "intent": intent}


async def retrieve_node(state: AgentState) -> AgentState:
    async with AsyncSessionLocal() as db:
        results = await hybrid_search(
            db=db,
            query=state["query"],
            top_k=5,
            doc_type_filter=None,
            equipment_filter=None,
        )
    results = rerank(state["query"], results)
    return {**state, "retrieved_chunks": results}


async def graph_lookup_node(state: AgentState) -> AgentState:
    match = EQUIPMENT_TAG_PATTERN.search(state["query"])
    if not match:
        return {**state, "graph_context": None}

    tag = match.group(0)
    async with AsyncSessionLocal() as db:
        equipment = await get_equipment_neighborhood(db, tag=tag, max_depth=2)
    return {**state, "graph_context": equipment}


async def copilot_agent_node(state: AgentState) -> AgentState:
    answer = await generate_answer(state["query"], state["retrieved_chunks"])
    return {**state, "answer": answer}


async def generate_citations_node(state: AgentState) -> AgentState:
    cleaned_answer, citations = extract_and_verify_citations(
        state["answer"], state["retrieved_chunks"]
    )
    return {**state, "answer": cleaned_answer, "citations": citations}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("graph_lookup", graph_lookup_node)
    graph.add_node("copilot_agent", copilot_agent_node)
    graph.add_node("generate_citations", generate_citations_node)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "retrieve")
    graph.add_edge("retrieve", "graph_lookup")
    graph.add_conditional_edges(
        "graph_lookup",
        lambda state: state["intent"],
        {
            "copilot": "copilot_agent",
            "maintenance": "copilot_agent",
            "compliance": "copilot_agent",
        },
    )
    graph.add_edge("copilot_agent", "generate_citations")
    graph.add_edge("generate_citations", END)

    return graph.compile()


_compiled_graph = None


async def run_copilot_query(query: str, auth_token: str = "") -> dict:
    """
    Single entry point for the whole pipeline. Builds (once, lazily) and
    invokes the compiled graph, returning the final state's answer and
    citations. This is the only function other code (a future FastAPI route)
    should call - never call the individual node functions directly.
    """
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()

    initial_state: AgentState = {
        "query": query,
        "auth_token": auth_token,
        "intent": "",
        "retrieved_chunks": [],
        "graph_context": None,
        "answer": "",
        "citations": [],
    }
    final_state = await _compiled_graph.ainvoke(initial_state)
    return {
        "answer": final_state["answer"],
        "citations": final_state["citations"],
        "graph_context": final_state["graph_context"],
    }
