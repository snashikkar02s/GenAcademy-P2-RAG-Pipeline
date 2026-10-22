"""Thin wrapper around the Anthropic SDK for answering, query planning and judging."""

from __future__ import annotations

import os
from functools import cache
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

ANSWER_SYSTEM = (
    "You answer questions about Halcyon Systems, a software company, using only the "
    "context provided. The context may be document excerpts, knowledge-graph facts "
    "written as `Source [kind] -[RELATION]-> Target [kind]`, or both. Answer in 1-3 "
    "sentences and name specific people, projects, tools and dates. If the context "
    "does not contain the answer, say so plainly rather than guessing."
)


@cache
def client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _text(response) -> str:
    if response.stop_reason == "refusal":
        return "[refused]"
    return "".join(b.text for b in response.content if b.type == "text").strip()


def answer(question: str, context: str) -> str:
    response = client().beta.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=ANSWER_SYSTEM,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{
            "role": "user",
            "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}",
        }],
    )
    return _text(response)


class QueryPlan(BaseModel):
    entities: list[str] = Field(
        description="Names from the catalog that the question mentions or clearly refers to, spelled exactly as in the catalog."
    )
    relation_types: list[str] = Field(
        description="Relation types from the catalog needed to answer. Empty if unsure."
    )
    target_kinds: list[str] = Field(
        description="Kinds of node the answer consists of, e.g. person, tool, project."
    )


def plan_query(question: str, catalog: str) -> QueryPlan:
    """Map a question onto graph entry points. `catalog` must be stable across calls so it caches."""
    response = client().messages.parse(
        model=MODEL,
        max_tokens=1024,
        output_config={"effort": "low"},
        system=[{
            "type": "text",
            "text": (
                "Map the user's question onto a knowledge graph so it can be traversed. "
                "Pick entry-point entities from the catalog below, the relation types "
                "to follow, and the kinds of node that form the answer.\n\n" + catalog
            ),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": question}],
        output_format=QueryPlan,
    )
    return response.parsed_output


class Grade(BaseModel):
    score: Literal[0, 1, 2] = Field(description="2 = fully correct, 1 = partially correct, 0 = wrong or missing")
    rationale: str = Field(description="One sentence explaining the score.")


def judge(question: str, expected: str, actual: str) -> Grade:
    response = client().messages.parse(
        model=MODEL,
        max_tokens=1024,
        output_config={"effort": "low"},
        system=(
            "Grade a candidate answer against a reference answer. Judge factual "
            "content only, not style. Give 2 if it contains every key fact in the "
            "reference without contradicting it, 1 if it has some key facts or is "
            "incomplete, 0 if it is wrong, says it doesn't know, or misses the point."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Question: {question}\n\nReference answer: {expected}\n\n"
                f"Candidate answer: {actual}"
            ),
        }],
        output_format=Grade,
    )
    return response.parsed_output
