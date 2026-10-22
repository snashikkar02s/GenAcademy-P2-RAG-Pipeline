import argparse
import sys
import textwrap

from pathlib import Path

import truststore
from dotenv import load_dotenv

# Use the OS certificate store so HTTPS works behind corporate TLS inspection.
truststore.inject_into_ssl()
# Load ANTHROPIC_API_KEY etc. from the repo's .env; real environment variables take precedence.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _ask(question: str, mode: str) -> None:
    from .data import load_kb

    kb = load_kb()
    if mode in ("vector", "both"):
        from .vector_rag import VectorRAG

        result = VectorRAG(kb).answer(question)
        print("=== Vector RAG ===")
        print(textwrap.indent(result["context"], "  | "))
        print(f"\nAnswer: {result['answer']}\n")
    if mode in ("graph", "both"):
        from .graph_rag import GraphRAG

        result = GraphRAG(kb).answer(question)
        print("=== GraphRAG ===")
        print(f"Plan: {result['plan'].model_dump()}")
        print(f"Seeds: {result['seeds']}  Triples: {len(result['triples'])}  Docs: {result['documents']}")
        print(f"\nAnswer: {result['answer']}\n")


def _graph_stats() -> None:
    from .data import load_kb
    from .graph import build_graph, stats

    g = build_graph(load_kb())
    nodes, edges = stats(g)
    print(f"Nodes: {g.number_of_nodes()}")
    for kind, n in nodes.most_common():
        print(f"  {kind:<10} {n}")
    print(f"Edges: {g.number_of_edges()}")
    for t, n in edges.most_common():
        print(f"  {t:<16} {n}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="GraphRAG vs vector RAG over the Halcyon knowledge base")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="Answer one question")
    ask.add_argument("question")
    ask.add_argument("--mode", choices=["vector", "graph", "both"], default="both")
    sub.add_parser("eval", help="Run both pipelines on all evaluation questions")
    sub.add_parser("graph-stats", help="Print node and edge counts")
    args = parser.parse_args()

    if args.command == "ask":
        _ask(args.question, args.mode)
    elif args.command == "eval":
        from .evaluate import run

        run()
    else:
        _graph_stats()
