"""Load the Halcyon knowledge base and evaluation questions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# JSON section name -> node kind
ENTITY_SECTIONS = {
    "people": "person",
    "skills": "skill",
    "tools": "tool",
    "projects": "project",
    "decisions": "decision",
}


@dataclass
class Entity:
    id: str
    kind: str
    name: str
    attrs: dict


@dataclass
class Document:
    id: str
    title: str
    type: str
    text: str
    attrs: dict


@dataclass
class Relationship:
    source: str
    type: str
    target: str
    properties: dict = field(default_factory=dict)


@dataclass
class Question:
    id: str
    question: str
    type: str
    expected_answer: str
    supporting_documents: list[str]
    supporting_entities: list[str]


@dataclass
class KnowledgeBase:
    entities: dict[str, Entity]
    documents: dict[str, Document]
    relationships: list[Relationship]
    metadata: dict

    def name(self, node_id: str) -> str:
        if node_id in self.entities:
            return self.entities[node_id].name
        return self.documents[node_id].title

    def name_index(self) -> dict[str, str]:
        """Lower-cased name/title -> id, for entity linking."""
        index = {e.name.lower(): e.id for e in self.entities.values()}
        index.update({d.title.lower(): d.id for d in self.documents.values()})
        return index


def load_kb(path: Path = DATA_DIR / "moc-data.json") -> KnowledgeBase:
    raw = json.loads(path.read_text(encoding="utf-8"))
    entities: dict[str, Entity] = {}
    for section, kind in ENTITY_SECTIONS.items():
        for item in raw[section]:
            attrs = {k: v for k, v in item.items() if k not in ("id", "name", "title")}
            name = item.get("name") or item["title"]
            entities[item["id"]] = Entity(item["id"], kind, name, attrs)

    documents = {
        d["id"]: Document(
            d["id"], d["title"], d["type"], d["text"],
            {k: v for k, v in d.items() if k not in ("id", "title", "type", "text")},
        )
        for d in raw["documents"]
    }
    relationships = [
        Relationship(r["source"], r["type"], r["target"], r.get("properties", {}))
        for r in raw["relationships"]
    ]
    known = entities.keys() | documents.keys()
    for r in relationships:
        if r.source not in known or r.target not in known:
            raise ValueError(f"Relationship references unknown node: {r}")
    return KnowledgeBase(entities, documents, relationships, raw["metadata"])


def load_questions(path: Path = DATA_DIR / "moc-questions.json") -> list[Question]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Question(**q) for q in raw["evaluation_questions"]]
