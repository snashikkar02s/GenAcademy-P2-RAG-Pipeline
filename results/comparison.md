# GraphRAG vs Vector RAG: evaluation results

Model: `claude-sonnet-5-5`. Scores are 0-2, graded by an LLM judge against the reference answer. Entity recall is the share of a question's supporting entities named anywhere in the retrieved context.

## By question type

| type | graph entity_recall | vector entity_recall | graph score | vector score |
|---|---|---|---|---|
| aggregation | 1.0 | 0.32 | 2.0 | 0.0 |
| multi_hop | 1.0 | 0.81 | 2.0 | 1.0 |
| passage_detail | 1.0 | 0.5 | 2.0 | 2.0 |
| single_hop | 1.0 | 0.0 | 2.0 | 0.0 |
| temporal | 1.0 | 0.5 | 2.0 | 2.0 |
| ALL | 1.0 | 0.53 | 2.0 | 1.17 |

## Per question

| id | type | question | vector | graph |
|---|---|---|---|---|
| q01 | multi_hop | Why was the Atlas launch moved to August? | 1 | 2 |
| q02 | passage_detail | Why didn't the team use pgvector for Atlas? | 2 | 2 |
| q03 | multi_hop | Who should I contact about Kafka consumer lag in the pipeline that Atlas depends on? | 2 | 2 |
| q04 | aggregation | Which projects are affected by decisions Fatima Al-Sayed proposed? | 0 | 2 |
| q05 | passage_detail | How much did hybrid search improve relevance over vector-only search? | 2 | 2 |
| q06 | temporal | What is the current status of Drift? | 2 | 2 |
| q07 | aggregation | Which people have both Python and LLM evaluation skills? | 0 | 2 |
| q08 | passage_detail | What incident happened during the Citadel rollout? | 2 | 2 |
| q09 | multi_hop | Which tools does Echo rely on, directly or through its project dependencies? | 1 | 2 |
| q10 | passage_detail | Can Echo answer questions about parental leave? | 2 | 2 |
| q11 | single_hop | Who approved the move from RabbitMQ to Kafka? | 0 | 2 |
| q12 | multi_hop | Which of Maya Chen's direct reports work on Atlas? | 0 | 2 |

## Answers

### q01 (multi_hop): Why was the Atlas launch moved to August?

- **Vector** (1/2): Atlas ranking v1 depends on Beacon click events, and Beacon couldn't go live on schedule: the schema registry rejected several Avro schemas as backward-incompatible, so order events need to be re-versioned. Lena noted that Atlas therefore can't launch in June without those events. Sam proposed mid-August to leave four weeks of ranking tuning after Beacon goes live, and was to confirm the new date by Wednesday (per the 2026-05-18 sync).
  - _Judge:_ The candidate gets the dependency on Beacon click events and the schema registry rejecting backward-incompatible Avro schemas, but omits the key fact that Beacon's cutover slipped from April 30 to July 15, and adds details like order events and re-versioning that the reference does not support.
- **Graph** (2/2): The Atlas launch was moved to August 17, 2026 (decision accepted 2026-05-20) because the Beacon cutover slipped from April 30 to July 15. The cause was the schema registry rejecting several Avro schemas as backward-incompatible, so order events had to be re-versioned. Atlas ranking v1 depends on Beacon click events, so it couldn't launch in June. Sam Whitfield proposed mid-August to leave four weeks of ranking tuning after Beacon goes live, and Maya Chen approved.
  - _Judge:_ The candidate includes all key facts: Atlas ranking depends on Beacon click events, Beacon cutover slipped from April 30 to July 15, and the schema registry rejected backward-incompatible Avro schemas; extra details do not contradict the reference.

### q02 (passage_detail): Why didn't the team use pgvector for Atlas?

- **Vector** (2/2): The team rejected pgvector because load tests at 40 million vectors showed p95 latency above 300 ms, far over Atlas's 80 ms budget (ADR-007). They chose self-hosted Weaviate on EKS instead.
  - _Judge:_ The candidate states the same key facts as the reference (load tests at 40M vectors, p95 latency above 300 ms, versus the 80 ms budget) and the added details about ADR-007 and Weaviate do not contradict it.
- **Graph** (2/2): The team rejected pgvector because load tests at 40 million vectors showed p95 latency above 300 ms, far over Atlas's 80 ms budget. This is recorded in ADR-007: Vector Store Selection, authored by Lena Okafor, which led to the decision (2026-02-10) to adopt self-hosted Weaviate instead.
  - _Judge:_ The candidate states the same key facts as the reference (40M vectors, p95 above 300 ms, 80 ms budget) and its extra details do not contradict the reference.

### q03 (multi_hop): Who should I contact about Kafka consumer lag in the pipeline that Atlas depends on?

- **Vector** (2/2): Atlas depends on the Beacon Kafka topics, so the Beacon Migration Runbook applies. For consumer lag, page Hana Kobayashi first and Arjun Patel second, since both have run the Kafka consumer groups in staging.
  - _Judge:_ The candidate names Hana Kobayashi first and Arjun Patel second, matches the Beacon dependency, and gives a consistent reason; the extra runbook and staging details do not contradict the reference.
- **Graph** (2/2): Atlas depends on Beacon (the RabbitMQ-to-Kafka pipeline migration), and the Beacon Migration Runbook says to page Hana Kobayashi first and Arjun Patel second for consumer lag or partition rebalancing issues. Both have run the Kafka consumer groups in staging. Hana leads Beacon, and Arjun works on its Kafka consumers.
  - _Judge:_ The candidate names Hana Kobayashi first and Arjun Patel second, and identifies Beacon as the dependency pipeline, matching all key facts in the reference; the extra details do not contradict it.

### q04 (aggregation): Which projects are affected by decisions Fatima Al-Sayed proposed?

- **Vector** (0/2): The context doesn't show any specific decisions that Fatima Al-Sayed proposed. It does say she authored the Secrets Management security policy, which is rolled out through Project Citadel, so Citadel is the project tied to her policy work. She attended the planning meetings in which Citadel and Drift were discussed, but the notes don't credit her with proposing the decision to resume Drift on October 5, 2026.
  - _Judge:_ The candidate says no decisions by Fatima are shown and names only Citadel (plus a mention of Drift as not hers), missing Beacon and Echo and the Vault mandate d03, so it misses the point.
- **Graph** (2/2): Fatima Al-Sayed proposed one decision in the context, "Mandate Vault for all service secrets" (2025-11-03). It affects three projects: Citadel, Beacon, and Echo. She only consulted on the Echo HR-exclusion decision and did not propose it.
  - _Judge:_ The candidate names Citadel, Beacon, and Echo as affected by the Vault mandate decision Fatima proposed, matching the reference; the extra detail does not contradict it.

### q05 (passage_detail): How much did hybrid search improve relevance over vector-only search?

- **Vector** (2/2): Hybrid search (BM25 plus vectors merged with reciprocal rank fusion) scored nDCG@10 of 0.68 versus 0.61 for vector-only search. That is an improvement of 0.07 points, or about 11% relative. The experiment used 2,400 labeled queries, and the report by Arjun Patel and Lena Okafor recommended shipping hybrid search.
  - _Judge:_ The candidate gives nDCG@10 of 0.68 for hybrid with RRF versus 0.61 for vector-only, matching the reference; the extra computed improvement (0.07, ~11% relative) is correct and nothing contradicts the reference.
- **Graph** (2/2): Hybrid search (BM25 plus vectors merged with reciprocal rank fusion) scored nDCG@10 of 0.68 versus 0.61 for vector-only search, an improvement of 0.07 points (about 11% relative). This comes from the Atlas Search Relevance Experiment Report, which tested 2,400 labeled queries. Vector-only search also failed badly on exact-match queries such as SKU numbers and part codes, which BM25 handled well.
  - _Judge:_ The candidate gives the same nDCG@10 figures as the reference (0.61 vector-only vs 0.68 hybrid with reciprocal rank fusion) and adds a correct derived difference (0.07, ~11% relative) without contradicting it.

### q06 (temporal): What is the current status of Drift?

- **Vector** (2/2): Drift is set to resume in Q4 2026, starting October 5, with Daniel Brooks as lead. This is a Q3 2026 planning decision that replaces the earlier Q2 decision to pause it. That pause had been made because Platform had only one SRE and couldn't run Citadel and Drift in parallel. The first milestone is distributed tracing for the Atlas search API and Beacon consumers.
  - _Judge:_ The candidate gives the October 5, 2026 resumption with Daniel Brooks as lead and says it supersedes the earlier pause, which matches the reference; the extra details do not contradict it, though it omits the March 1 pause date and June 15 decision date.
- **Graph** (2/2): Drift is currently **on hold**. It was paused on 2026-03-01 so SRE capacity could go to Citadel. That pause decision has since been superseded by the 2026-06-15 decision to resume Drift in Q4 2026, starting October 5, with Daniel Brooks leading. The project's recorded status is still "on_hold" until that restart.
  - _Judge:_ The candidate includes all key facts: on hold since March 1, 2026, the June 15 decision superseding the pause, resumption on October 5, 2026 (Q4), and Daniel Brooks as lead, with no contradictions.

### q07 (aggregation): Which people have both Python and LLM evaluation skills?

- **Vector** (0/2): The context doesn't say anything about anyone's Python or LLM evaluation skills. It only mentions Arjun Patel and Lena Okafor as authors of the Atlas search relevance report, Sam Whitfield as product owner, and Fatima Al-Sayed as the security policy author, and none of these passages lists skills.
  - _Judge:_ The candidate says the context lacks skill information and names no one with both skills, so it misses the reference answer of Lena Okafor and Priya Nair.
- **Graph** (2/2): Lena Okafor (Python: expert, LLM evaluation: advanced) and Priya Nair (Python: advanced, LLM evaluation: advanced) have both skills. Arjun Patel and Hana Kobayashi have Python but no LLM evaluation skill listed.
  - _Judge:_ The candidate names Lena Okafor and Priya Nair as having both skills, matching the reference, and the extra details about others lacking LLM evaluation do not contradict it.

### q08 (passage_detail): What incident happened during the Citadel rollout?

- **Vector** (2/2): During the Citadel rollout, on May 6, 2026, a rotation of the Airflow metadata credentials broke Beacon's Airflow connections for about three hours. The old secret was revoked before workers had picked up the new one.
  - _Judge:_ The candidate matches all key facts: May 6, 2026, Airflow metadata credential rotation, Beacon's Airflow connections broken for about three hours, and old secret revoked too early (before workers picked up the new one).
- **Graph** (2/2): During the Citadel rollout, on May 6, 2026, a rotation of the Airflow metadata credentials broke Beacon's Airflow connections for about three hours. The old secret was revoked before workers picked up the new one. As a result, rotations now happen in two stages with an overlap window (per the Citadel Retrospective by Fatima Al-Sayed and Daniel Brooks).
  - _Judge:_ The candidate matches all key facts in the reference (May 6, 2026, Airflow metadata credential rotation, Beacon's Airflow connections broken for about three hours, old secret revoked too early) and the extra details do not contradict it.

### q09 (multi_hop): Which tools does Echo rely on, directly or through its project dependencies?

- **Vector** (1/2): Based on the Echo Product Requirements, Echo relies on these tools and services:

- **Atlas embedding service**, which Echo reuses.
- **Weaviate**, where Echo stores its index.
- **Airflow**, which runs the ingestion jobs.
- **Vault**, which issues Echo's model API keys under the Citadel standard.

The context does not describe what tools Atlas itself depends on, so any further indirect dependencies through Atlas or Citadel aren't covered here.
  - _Judge:_ The candidate correctly lists Weaviate and Airflow as direct dependencies and mentions Vault via Citadel, but it omits PostgreSQL via Atlas, AWS EKS, and GitHub Actions via Citadel, and it says indirect dependencies are not covered.
- **Graph** (2/2): Echo uses two tools directly: Weaviate (its vector index) and Airflow (ingestion jobs).

Through its project dependencies it also relies on:
- **Atlas**, which Echo depends on for the embedding service. Atlas uses Weaviate (already counted) and PostgreSQL. Atlas in turn depends on Beacon, which uses Airflow and Kafka, though the context only lists Airflow as a Beacon tool.
- **Citadel**, which issues Echo's model API keys. Citadel uses HashiCorp Vault, AWS EKS and GitHub Actions.

So the full set is Weaviate, Airflow, PostgreSQL, HashiCorp Vault, AWS EKS and GitHub Actions. Kafka and dbt are tied to Beacon through decisions and people, not through a listed USES_TOOL relationship, so I haven't counted them.
  - _Judge:_ The candidate lists all reference tools: direct Weaviate and Airflow, via Atlas PostgreSQL (and Weaviate), via Citadel Vault, EKS, GitHub Actions; the extra Beacon/Kafka discussion is hedged and not counted, so it doesn't contradict the reference.

### q10 (passage_detail): Can Echo answer questions about parental leave?

- **Vector** (2/2): No. HR, compensation, and performance documents are excluded from Echo's index, a decision Priya Nair made on May 12, 2026 after consulting Fatima Al-Sayed on privacy risk. Questions about benefits or leave policy, including parental leave, should be redirected to the HR portal.
  - _Judge:_ The candidate says No, states that HR/compensation/performance documents are excluded from Echo's index, and says leave questions are redirected to the HR portal, matching all key facts; the extra details about who made the decision and when do not contradict the reference.
- **Graph** (2/2): No. Echo excludes HR, compensation, and performance documents from its index. This follows the May 12, 2026 decision by Priya Nair, made after consulting Fatima Al-Sayed on privacy risk. According to the Echo Product Requirements, questions about benefits or leave policy should be redirected to the HR portal.
  - _Judge:_ The candidate says no, states that HR, compensation, and performance documents are excluded from the index, and says leave questions are redirected to the HR portal, matching all key facts in the reference; the extra details about the decision do not contradict it.

### q11 (single_hop): Who approved the move from RabbitMQ to Kafka?

- **Vector** (0/2): The context doesn't say who approved the move from RabbitMQ to Kafka. The Beacon Migration Runbook describes the cutover (producers dual-write for two weeks before RabbitMQ consumers are drained) and names Hana Kobayashi as primary contact, but it doesn't mention an approver.
  - _Judge:_ The candidate says the approver is not stated and never names Priya Nair, so it misses the key fact in the reference answer.
- **Graph** (2/2): Priya Nair approved the decision to migrate the event pipeline from RabbitMQ to Kafka on 2026-01-15. Hana Kobayashi proposed it.
  - _Judge:_ The candidate names Priya Nair as the approver, matching the reference, and the added details (date, proposer) do not contradict it.

### q12 (multi_hop): Which of Maya Chen's direct reports work on Atlas?

- **Vector** (0/2): The context doesn't say which of Maya Chen's direct reports work on Atlas. It states only that Platform reports to Maya Chen, and it doesn't list who is on the Platform team beyond Fatima Al-Sayed being the contact for Vault access.

Atlas contributors named in the context are Arjun Patel (search API), Tomás Rivera (React search UI), Owen Gallagher (UX research on autocomplete), Sam Whitfield (product owner), and Lena Okafor (co-author of the relevance experiment report). None of them is explicitly identified as reporting to Maya Chen.
  - _Judge:_ The candidate says the answer can't be determined and doesn't identify Arjun Patel and Tomás Rivera as Maya Chen's direct reports on Atlas, even though it names them as contributors.
- **Graph** (2/2): Two of Maya Chen's direct reports work on Atlas: Arjun Patel, who owns the Search API, and Tomás Rivera, who works on the Search UI. Daniel Brooks and Fatima Al-Sayed also report to her, but they work on Beacon, Citadel and Echo rather than Atlas.
  - _Judge:_ The candidate names exactly Arjun Patel and Tomás Rivera as Maya Chen's direct reports on Atlas, matching the reference; the extra details about other reports and projects do not contradict it.
