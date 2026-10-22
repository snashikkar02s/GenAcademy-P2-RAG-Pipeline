"""Build the knowledge graph and traverse it."""

from __future__ import annotations

from collections import Counter

import networkx as nx

from .data import KnowledgeBase

# Edge types worth following past the hop limit (chains like A depends on B depends on C).
TRANSITIVE_TYPES = {"DEPENDS_ON", "SUPERSEDES"}
# Edges that tie a document to what it is about.
DOC_LINK_TYPES = {"DESCRIBES", "RECORDS", "AUTHORED_BY"}

Triple = tuple[str, str, str, dict]  # (source, type, target, properties)


def build_graph(kb: KnowledgeBase) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for e in kb.entities.values():
        g.add_node(e.id, kind=e.kind, name=e.name, **e.attrs)
    for d in kb.documents.values():
        g.add_node(d.id, kind="document", name=d.title, doc_type=d.type, **d.attrs)
    for r in kb.relationships:
        g.add_edge(r.source, r.target, key=r.type, type=r.type, **r.properties)
    return g


def stats(g: nx.MultiDiGraph) -> tuple[Counter, Counter]:
    nodes = Counter(kind for _, kind in g.nodes(data="kind"))
    edges = Counter(t for _, _, t in g.edges(data="type"))
    return nodes, edges


def incident_edges(g: nx.MultiDiGraph, node: str, types: set[str] | None = None) -> list[Triple]:
    """All edges touching `node` in either direction, optionally filtered by type."""
    out = []
    for u, v, data in [*g.out_edges(node, data=True), *g.in_edges(node, data=True)]:
        if types is None or data["type"] in types:
            props = {k: val for k, val in data.items() if k != "type"}
            out.append((u, data["type"], v, props))
    return out


def neighbors(g: nx.MultiDiGraph, node: str, types: set[str] | None = None) -> set[str]:
    return {v if u == node else u for u, _, v, _ in incident_edges(g, node, types)}


def k_hop_triples(
    g: nx.MultiDiGraph,
    seeds: list[str],
    k: int = 2,
    types: set[str] | None = None,
    limit: int = 80,
) -> list[Triple]:
    """Breadth-first expansion from `seeds`, collecting edges in hop order.

    Edges in TRANSITIVE_TYPES are always followed, even past `k`, so dependency
    and supersession chains are never cut off midway.
    """
    allowed = None if types is None else types | TRANSITIVE_TYPES
    seen_edges: set[tuple[str, str, str]] = set()
    triples: list[Triple] = []
    visited = set(seeds)
    frontier = [(s, 0) for s in seeds if s in g]
    while frontier and len(triples) < limit:
        node, depth = frontier.pop(0)
        for u, t, v, props in incident_edges(g, node, allowed):
            if (u, t, v) in seen_edges:
                continue
            if depth >= k and t not in TRANSITIVE_TYPES:
                continue
            seen_edges.add((u, t, v))
            triples.append((u, t, v, props))
            other = v if u == node else u
            if other not in visited:
                visited.add(other)
                frontier.append((other, depth + 1))
    return triples[:limit]


def triples_to_text(g: nx.MultiDiGraph, triples: list[Triple]) -> str:
    def label(n: str) -> str:
        data = g.nodes[n]
        extra = data.get("date") or data.get("status") if data["kind"] == "decision" else None
        return f'{data["name"]} [{data["kind"]}{", " + extra if extra else ""}]'

    lines = []
    for u, t, v, props in triples:
        line = f"{label(u)} -[{t}]-> {label(v)}"
        if props:
            line += " (" + ", ".join(f"{k}: {val}" for k, val in props.items()) + ")"
        lines.append(line)
    return "\n".join(lines)


def node_card(g: nx.MultiDiGraph, node: str) -> str:
    """One-line attribute summary of a node (skipping document text)."""
    data = g.nodes[node]
    attrs = ", ".join(f"{k}: {v}" for k, v in data.items() if k not in ("name", "kind"))
    return f'{data["name"]} ({data["kind"]}) — {attrs}'
