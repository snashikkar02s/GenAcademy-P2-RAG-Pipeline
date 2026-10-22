"""GraphRAG: link the question to graph nodes, expand a subgraph, answer from it."""

from __future__ import annotations

import difflib
from collections import Counter, defaultdict

from . import llm
from .data import KnowledgeBase
from .graph import (
    DOC_LINK_TYPES,
    Triple,
    build_graph,
    k_hop_triples,
    node_card,
    triples_to_text,
)

MAX_TRIPLES = 80
MAX_DOCS = 3


class GraphRAG:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.g = build_graph(kb)
        self.names = kb.name_index()
        self.relation_types = sorted({r.type for r in kb.relationships})
        self.catalog = self._catalog()

    def _catalog(self) -> str:
        by_kind = defaultdict(list)
        for node, data in self.g.nodes(data=True):
            by_kind[data["kind"]].append(data["name"])
        signatures = defaultdict(set)
        for u, v, t in self.g.edges(data="type"):
            signatures[t].add((self.g.nodes[u]["kind"], self.g.nodes[v]["kind"]))
        lines = ["## Entities by kind"]
        lines += [f"- {kind}: " + "; ".join(sorted(names)) for kind, names in sorted(by_kind.items())]
        lines.append("\n## Relation types (source kind -> target kind)")
        lines += [
            f"- {t}: " + ", ".join(f"{a} -> {b}" for a, b in sorted(signatures[t]))
            for t in self.relation_types
        ]
        return "\n".join(lines)

    def link(self, mentions: list[str], question: str) -> list[str]:
        """Resolve mentioned names to node ids; also catch names written verbatim in the question."""
        seeds: list[str] = []
        for m in mentions:
            key = m.lower().strip()
            match = self.names.get(key)
            if match is None:
                close = difflib.get_close_matches(key, self.names, n=1, cutoff=0.75)
                match = self.names[close[0]] if close else None
            if match and match not in seeds:
                seeds.append(match)
        q = question.lower()
        for name, node in self.names.items():
            if len(name) > 3 and name in q and node not in seeds:
                seeds.append(node)
        return seeds

    def retrieve(self, question: str, plan: llm.QueryPlan | None = None) -> dict:
        plan = plan or llm.plan_query(question, self.catalog)
        seeds = self.link(plan.entities, question)
        types = {t for t in plan.relation_types if t in self.relation_types} or None

        # Edges on the planned relation types come first; unfiltered neighbourhood fills the rest.
        triples = k_hop_triples(self.g, seeds, k=2, types=types, limit=MAX_TRIPLES)
        if types is not None and len(triples) < MAX_TRIPLES:
            seen = {(u, t, v) for u, t, v, _ in triples}
            for tr in k_hop_triples(self.g, seeds, k=2, limit=MAX_TRIPLES):
                if (tr[0], tr[1], tr[2]) not in seen and len(triples) < MAX_TRIPLES:
                    triples.append(tr)

        return {
            "plan": plan,
            "seeds": seeds,
            "triples": triples,
            "documents": self._linked_documents(seeds, triples),
        }

    def _linked_documents(self, seeds: list[str], triples: list[Triple]) -> list[str]:
        """Documents in the subgraph, ranked by how many seeds they directly touch."""
        seed_set = set(seeds)
        score: Counter[str] = Counter()
        for u, t, v, _ in triples:
            if t not in DOC_LINK_TYPES:
                continue
            doc, other = (u, v) if u in self.kb.documents else (v, u)
            score[doc] += 2 if other in seed_set else 1
        for s in seeds:
            if s in self.kb.documents:
                score[s] += 10
        return [d for d, _ in score.most_common(MAX_DOCS)]

    def context(self, retrieval: dict) -> str:
        nodes = []
        for u, _, v, _ in retrieval["triples"]:
            for n in (u, v):
                if n not in nodes and n not in self.kb.documents:
                    nodes.append(n)
        parts = [
            "## Entities\n" + "\n".join(node_card(self.g, n) for n in nodes),
            "## Relationships\n" + triples_to_text(self.g, retrieval["triples"]),
        ]
        if retrieval["documents"]:
            parts.append("## Linked documents\n" + "\n\n".join(
                f"[{d}: {self.kb.documents[d].title}]\n{self.kb.documents[d].text}"
                for d in retrieval["documents"]
            ))
        return "\n\n".join(parts)

    def answer(self, question: str) -> dict:
        retrieval = self.retrieve(question)
        context = self.context(retrieval)
        return {"answer": llm.answer(question, context), "context": context, **retrieval}
