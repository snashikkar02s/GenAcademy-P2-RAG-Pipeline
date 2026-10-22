"""Run both pipelines on the evaluation questions and compare them."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from . import llm
from .data import KnowledgeBase, Question, load_kb, load_questions
from .graph_rag import GraphRAG
from .vector_rag import VectorRAG

RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def entity_recall(kb: KnowledgeBase, q: Question, context: str) -> float:
    """Share of the question's supporting entities whose name appears in the context."""
    if not q.supporting_entities:
        return float("nan")
    text = context.lower()
    hits = sum(kb.name(e).lower() in text for e in q.supporting_entities)
    return hits / len(q.supporting_entities)


def doc_recall(q: Question, context: str) -> float:
    """Share of the question's supporting documents that appear in the context."""
    if not q.supporting_documents:
        return float("nan")
    cited = set(re.findall(r"\[(doc\d+):", context))
    return len(cited & set(q.supporting_documents)) / len(q.supporting_documents)


def evaluate_question(kb, vector: VectorRAG, graph: GraphRAG, q: Question) -> list[dict]:
    rows = []
    for name, pipeline in (("vector", vector), ("graph", graph)):
        result = pipeline.answer(q.question)
        grade = llm.judge(q.question, q.expected_answer, result["answer"])
        rows.append({
            "id": q.id,
            "type": q.type,
            "question": q.question,
            "pipeline": name,
            "answer": result["answer"],
            "score": grade.score,
            "rationale": grade.rationale,
            "entity_recall": entity_recall(kb, q, result["context"]),
            "doc_recall": doc_recall(q, result["context"]),
            "context_chars": len(result["context"]),
        })
    print(f"  {q.id}: vector={rows[0]['score']} graph={rows[1]['score']}  {q.question}")
    return rows


def run(workers: int = 4) -> pd.DataFrame:
    kb = load_kb()
    questions = load_questions()
    vector, graph = VectorRAG(kb), GraphRAG(kb)
    print(f"Evaluating {len(questions)} questions with {llm.MODEL}...")
    with ThreadPoolExecutor(workers) as pool:
        batches = pool.map(lambda q: evaluate_question(kb, vector, graph, q), questions)
    df = pd.DataFrame([row for batch in batches for row in batch])

    RESULTS_DIR.mkdir(exist_ok=True)
    df.to_csv(RESULTS_DIR / "eval_results.csv", index=False)
    (RESULTS_DIR / "comparison.md").write_text(report(df), encoding="utf-8")
    print(f"Wrote {RESULTS_DIR / 'eval_results.csv'} and comparison.md")
    return df


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """Mean score and recall by question type and pipeline."""
    by_type = df.pivot_table(
        index="type", columns="pipeline", values=["score", "entity_recall"], aggfunc="mean"
    )
    overall = df.groupby("pipeline")[["score", "entity_recall"]].mean()
    by_type.loc["ALL"] = [overall.loc[p, m] for m, p in by_type.columns]
    return by_type.round(2)


def _md_table(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(map(str, df.columns)) + " |"
    rule = "|" + "---|" * len(df.columns)
    body = ["| " + " | ".join(map(str, row)) + " |" for row in df.itertuples(index=False)]
    return "\n".join([header, rule, *body])


def report(df: pd.DataFrame) -> str:
    s = summary(df)
    flat = s.copy()
    flat.columns = [f"{p} {m}" for m, p in s.columns]
    flat = flat.reset_index()

    wide = df.pivot(index=["id", "type", "question"], columns="pipeline", values="score").reset_index()
    wide = wide[["id", "type", "question", "vector", "graph"]]

    answers = []
    for qid, grp in df.groupby("id", sort=True):
        r = {row.pipeline: row for row in grp.itertuples()}
        answers.append(
            f"### {qid} ({r['graph'].type}): {r['graph'].question}\n\n"
            f"- **Vector** ({r['vector'].score}/2): {r['vector'].answer}\n"
            f"  - _Judge:_ {r['vector'].rationale}\n"
            f"- **Graph** ({r['graph'].score}/2): {r['graph'].answer}\n"
            f"  - _Judge:_ {r['graph'].rationale}\n"
        )

    return "\n\n".join([
        "# GraphRAG vs Vector RAG: evaluation results",
        f"Model: `{llm.MODEL}`. Scores are 0-2, graded by an LLM judge against the reference "
        "answer. Entity recall is the share of a question's supporting entities named "
        "anywhere in the retrieved context.",
        "## By question type\n\n" + _md_table(flat),
        "## Per question\n\n" + _md_table(wide),
        "## Answers\n\n" + "\n".join(answers),
    ])
