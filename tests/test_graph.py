"""Offline checks of graph construction and retrieval (no LLM calls)."""

import pytest

from genacademy_p2_rag_pipeline.data import load_kb, load_questions
from genacademy_p2_rag_pipeline.graph import build_graph, k_hop_triples, neighbors
from genacademy_p2_rag_pipeline.graph_rag import GraphRAG
from genacademy_p2_rag_pipeline.llm import QueryPlan


@pytest.fixture(scope="module")
def kb():
    return load_kb()


@pytest.fixture(scope="module")
def g(kb):
    return build_graph(kb)


def test_graph_size(kb, g):
    assert g.number_of_nodes() == 57
    assert g.number_of_edges() == len(kb.relationships) == 148


def test_questions_load():
    assert len(load_questions()) == 12


def test_echo_tools_through_dependencies(g):
    """q09: Echo's tools, directly or via the projects it depends on."""
    tools = set()
    for u, t, v, _ in k_hop_triples(g, ["pr05"], k=2, types={"USES_TOOL", "DEPENDS_ON"}):
        if t == "USES_TOOL":
            tools.add(v)
    assert {"t08", "t03", "t01", "t06", "t05", "t10"} <= tools


def test_skill_intersection(g):
    """q07: people with both Python and LLM evaluation skills."""
    python = neighbors(g, "s01", {"HAS_SKILL"})
    llm_eval = neighbors(g, "s12", {"HAS_SKILL"})
    assert python & llm_eval == {"p03", "p05"}


def test_supersedes(g):
    assert "d04" in neighbors(g, "d09", {"SUPERSEDES"})


def test_graph_rag_retrieval_offline(kb):
    rag = GraphRAG(kb)
    plan = QueryPlan(entities=["Fatima Al-Sayed"], relation_types=["PROPOSED", "AFFECTS"], target_kinds=["project"])
    result = rag.retrieve("Which projects are affected by decisions Fatima Al-Sayed proposed?", plan)
    assert result["seeds"] == ["p09"]
    context = rag.context(result)
    for name in ("Citadel", "Beacon", "Echo"):
        assert name in context


def test_vector_baseline_finds_adr(kb):
    from genacademy_p2_rag_pipeline.vector_rag import VectorRAG

    hits = VectorRAG(kb).retrieve("Why didn't the team use pgvector for Atlas?", k=3)
    assert "doc03" in {c.doc_id for c, _ in hits}
