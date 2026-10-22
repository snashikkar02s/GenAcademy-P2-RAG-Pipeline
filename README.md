# GenAcademy: GraphRAG for Organizational Knowledge

This project models the knowledge of **Halcyon Systems**, a fictional software company, as a graph and answers questions over it two ways:

- **Vector RAG** splits the 11 documents into overlapping sentence chunks, embeds them locally with `fastembed` (`BAAI/bge-small-en-v1.5`), and retrieves the top 4 by cosine similarity.
- **GraphRAG** works in four steps:
  1. Claude maps the question onto the graph and picks entry entities and relation types to follow.
  2. The pipeline links those names to nodes.
  3. It expands 2 hops through typed edges. It always follows `DEPENDS_ON` and `SUPERSEDES` chains to the end.
  4. It answers from the entity attributes, the relationship facts and the text of linked documents.

Both pipelines answer the same 12 evaluation questions, and an LLM judge grades the answers. The point is to show **when structured relationships matter more than semantic similarity**.

## The knowledge graph

`data/moc-data.json` has **57 nodes** and **148 typed edges**.

Nodes:

| Kind | Count |
|---|---|
| Skills | 12 |
| Documents | 11 |
| People | 10 |
| Tools | 10 |
| Decisions | 9 |
| Projects | 5 |

Edges include `REPORTS_TO`, `HAS_SKILL`, `WORKS_ON`, `LEADS`, `USES_TOOL`, `DEPENDS_ON`, `PROPOSED`, `APPROVED`, `AFFECTS`, `SUPERSEDES`, `RECORDS` and `AUTHORED_BY`. Some carry properties such as `role`, `level` and `reason`.

`data/moc-questions.json` has 12 questions, each tagged `single_hop`, `multi_hop`, `aggregation`, `temporal` or `passage_detail`, with reference answers and supporting entities.

## Layout

```
src/genacademy_p2_rag_pipeline/
  data.py        load + validate the JSON into dataclasses
  graph.py       NetworkX MultiDiGraph, k-hop traversal, triple rendering
  vector_rag.py  chunking, local embeddings, cosine retrieval
  graph_rag.py   query planning, entity linking, subgraph retrieval
  llm.py         Claude calls: answer, plan_query (structured), judge (structured)
  evaluate.py    run both pipelines, score, write results/
notebooks/graphrag_vs_vector.ipynb   walkthrough with graph plots and the comparison
tests/test_graph.py                  offline tests (no API calls)
```

## Setup

```bash
uv sync
export ANTHROPIC_API_KEY=sk-ant-...      # PowerShell: $env:ANTHROPIC_API_KEY = "sk-ant-..."
```

The model defaults to `claude-sonnet-5-5`; override it with `CLAUDE_MODEL`. The embedding model (about 130 MB) downloads on first use. The package loads the OS certificate store through `truststore`, so downloads and API calls work behind corporate TLS inspection.

## Usage

```bash
uv run pytest                                      # offline tests
uv run genacademy-p2-rag-pipeline graph-stats      # node / edge counts
uv run genacademy-p2-rag-pipeline ask "Which people have both Python and LLM evaluation skills?" --mode both
uv run genacademy-p2-rag-pipeline eval             # writes results/eval_results.csv + results/comparison.md
```

To walk through the comparison, open `notebooks/graphrag_vs_vector.ipynb` with the `.venv` kernel.

## What to expect

| Question type | Example | Winner | Why |
|---|---|---|---|
| aggregation | Who has both Python and LLM-evaluation skills? | Graph | No document states it; the answer is a set intersection over `HAS_SKILL` edges |
| multi_hop | Which tools does Echo rely on, including through dependencies? | Graph | Echo → `DEPENDS_ON` → Atlas/Citadel → `USES_TOOL` is spread across three documents |
| single_hop (no doc) | Who approved the move from RabbitMQ to Kafka? | Graph | The approval exists only as an `APPROVED` edge |
| temporal | What is the current status of Drift? | Graph | `SUPERSEDES` resolves which decision is current |
| passage_detail | How much did hybrid search improve relevance? | Vector, or a tie | The answer is a number inside prose; GraphRAG only has it through linked document text |

`results/comparison.md` holds the measured scores after you run `eval`.
