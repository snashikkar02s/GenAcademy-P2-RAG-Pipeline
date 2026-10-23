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

## Results

These come from one run on 12 questions, with `claude-sonnet-5-5` answering and judging. Scores are 0–2 per question. Every answer and the judge's rationale are in [results/comparison.md](results/comparison.md).

| Question type | # | Vector RAG | GraphRAG |
|---|---|---|---|
| aggregation | 2 | 0.0 | **2.0** |
| multi_hop | 4 | 1.0 | **2.0** |
| single_hop | 1 | 0.0 | **2.0** |
| temporal | 1 | 2.0 | 2.0 |
| passage_detail | 4 | 2.0 | 2.0 |
| **Total** | 12 | **14 / 24** | **24 / 24** |

| Retrieval metric (mean) | Vector RAG | GraphRAG |
|---|---|---|
| Supporting entities present in context | 53% | 100% |
| Supporting documents present in context | 88% | 87% |
| Context size sent to the LLM | ~1,100 chars | ~10,700 chars |

## Analysis: when each approach wins

**GraphRAG wins when the answer lives in the relationships.** Vector RAG scored 0 on four questions and 1 on two:

- **Facts never written in prose** (q11, *who approved RabbitMQ → Kafka*; q07, *who has Python and LLM-evaluation skills*). These exist only as `APPROVED` and `HAS_SKILL` edges. Vector RAG retrieved related-sounding chunks and correctly said it couldn't find the answer.
- **Joins across entities** (q04, *projects affected by Fatima's decisions*; q12, *Maya's direct reports on Atlas*). Vector RAG found the right *topic*: it listed the Atlas staff for q12. It could not apply the second condition, `REPORTS_TO` or `PROPOSED → AFFECTS`.
- **Facts scattered across documents** (q09, *Echo's tools through dependencies*). All four retrieved chunks came from the Echo PRD, the single most similar document. Atlas's and Citadel's tools were never retrieved. The graph walked `DEPENDS_ON → USES_TOOL` straight to them.
- **Partial causal chains** (q01, *why Atlas moved to August*). Vector RAG found the meeting notes but missed the Beacon slip dates that the graph's `CAUSED_BY` edge pointed to.

**Vector RAG holds its own when the answer is a passage.** It scored 2/2 on every passage_detail question (metrics, rationales, incidents, policy). It also got q06 (Drift status) right, because the newer meeting note explicitly says it "replaces the March decision". When the text spells out the relationship, similarity search is enough.

**Caveats, and what GraphRAG's perfect score does not mean:**
- **GraphRAG here is really a hybrid.** It ties on passage questions only because it also pulls the text of linked documents. A pure triple store would have lost those: the graph records *that* pgvector was rejected, not *why* (300 ms vs 80 ms).
- **It costs more context.** GraphRAG sends about 10× more context (2-hop neighbourhoods plus documents), which means more tokens and more room for distraction. In q09 it volunteered loosely related tools (Kafka, dbt), hedged, which a stricter judge might penalise.
- **The graph only knows what was modelled.** Someone has to build and maintain the edges. Entity linking also has to work: if the question's names don't map to a node, GraphRAG retrieves nothing useful.
- **The evaluation is small and favourable.** It's 12 questions, a single run, and the same model family answers and judges. The dataset was also written so that both pipelines draw on the same facts. Treat the numbers as an illustration of the pattern, not a benchmark.

**Rule of thumb:** use the graph for *who / what / which / how is X connected to Y*, and text retrieval for *why / how much / what exactly happened*. In production, combine them: walk the graph to find the right entities, then fetch their documents for detail.
