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

- **Vector** (1/2): Atlas ranking v1 depends on Beacon click events, so it can't launch in June without them. The schema registry rejected several Avro schemas as backward-incompatible, so order events need to be re-versioned. Sam proposed mid-August to leave four weeks of ranking tuning after Beacon goes live, and was to confirm the new date by Wednesday after the 2026-05-18 sync.
  - _Judge:_ The candidate captures the Atlas dependency on Beacon click events and the schema registry rejecting backward-incompatible Avro schemas, but omits the key fact that Beacon's cutover slipped from April 30 to July 15, and adds details like order events re-versioning that are not in the reference.
- **Graph** (2/2): The Atlas launch was moved to August 17, 2026 (decision accepted 2026-05-20) because the Beacon cutover slipped from April 30 to July 15. The slip happened because the schema registry rejected several Avro schemas as backward-incompatible, so order events had to be re-versioned. Atlas ranking v1 depends on Beacon click events, so it couldn't launch in June. Sam Whitfield proposed mid-August to leave four weeks of ranking tuning after Beacon goes live, and Maya Chen approved.
  - _Judge:_ The candidate includes all key facts: Atlas ranking depends on Beacon click events, Beacon cutover slipped from April 30 to July 15, and the schema registry rejected backward-incompatible Avro schemas; extra details do not contradict the reference.

### q02 (passage_detail): Why didn't the team use pgvector for Atlas?

- **Vector** (2/2): The team rejected pgvector because load tests at 40 million vectors showed p95 latency above 300 ms, far over Atlas's 80 ms budget (ADR-007). They adopted self-hosted Weaviate on EKS instead.
  - _Judge:_ The candidate states the same key facts as the reference (40 million vectors, p95 latency above 300 ms, 80 ms budget) and its extra details about ADR-007 and Weaviate do not contradict the reference.
- **Graph** (2/2): The team rejected pgvector because load tests at 40 million vectors showed p95 latency above 300 ms, well over Atlas's 80 ms budget. This is recorded in ADR-007 (Vector Store Selection), which led to the 2026-02-10 decision to use self-hosted Weaviate. The ADR was proposed by Lena Okafor and approved by Maya Chen.
  - _Judge:_ The candidate states the same key facts as the reference (40 million vectors, p95 latency above 300 ms, 80 ms budget) and the extra details about the ADR do not contradict it.

### q03 (multi_hop): Who should I contact about Kafka consumer lag in the pipeline that Atlas depends on?

- **Vector** (2/2): Atlas depends on Beacon's Kafka topics for clickstream data. According to the Beacon Migration Runbook, for consumer lag or partition rebalancing issues you should page Hana Kobayashi first and Arjun Patel second, since both have run the Kafka consumer groups in staging.
  - _Judge:_ The candidate names Hana Kobayashi first and Arjun Patel second, identifies Beacon as the dependency, and notes their Kafka experience, matching all key facts in the reference.
- **Graph** (2/2): Atlas depends on Beacon (the RabbitMQ-to-Kafka pipeline), and the Beacon Migration Runbook says to page Hana Kobayashi first, since she is the primary contact and leads Beacon. Page Arjun Patel second. Both have run the Kafka consumer groups in staging. Arjun also works on Beacon's Kafka consumers. If the problem is in the Kafka Connect workers on EKS, Daniel Brooks owns that deployment.
  - _Judge:_ The candidate names Hana Kobayashi first and Arjun Patel second, identifies Beacon as the dependency, and notes their Kafka experience, matching the reference; the extra Daniel Brooks detail does not contradict it.

### q04 (aggregation): Which projects are affected by decisions Fatima Al-Sayed proposed?

- **Vector** (0/2): The context doesn't say which decisions Fatima Al-Sayed proposed, so I can't say which projects were affected by them. What it does show is that she authored the Secrets Management security policy, which is rolled out through Project Citadel (doc04), and that she attended the Q2 and Q3 2026 planning meetings. The planning notes record decisions, including Drift resuming October 5, 2026 under Daniel Brooks, but they don't credit any of them to her.
  - _Judge:_ The candidate says it cannot determine which projects are affected and omits Beacon and Echo, so it misses the reference answer (Citadel, Beacon, Echo via the Vault mandate d03); its passing mention of Citadel comes via a different link and does not answer the question.
- **Graph** (2/2): Fatima Al-Sayed proposed one decision, "Mandate Vault for all service secrets" (2025-11-03). It affects three projects: Citadel, Beacon, and Echo. She was only consulted on the "Exclude HR documents from Echo" decision, not its proposer, so that one doesn't count.
  - _Judge:_ The candidate identifies Citadel, Beacon, and Echo as affected by the Vault mandate decision, matching the reference, and adds no contradicting facts.

### q05 (passage_detail): How much did hybrid search improve relevance over vector-only search?

- **Vector** (2/2): Hybrid search (BM25 plus vectors merged with reciprocal rank fusion) scored nDCG@10 of 0.68 versus 0.61 for vector-only search, an improvement of 0.07 points (about 11.5% relative). This came from the Atlas Search Relevance Experiment Report by Arjun Patel and Lena Okafor, which tested 2,400 labeled queries.
  - _Judge:_ The candidate gives the same nDCG@10 values (0.61 vector-only, 0.68 hybrid with reciprocal rank fusion) and correctly computes the 0.07 absolute and ~11.5% relative gain; the extra details do not contradict the reference.
- **Graph** (2/2): Hybrid search (BM25 plus vectors merged with reciprocal rank fusion) scored nDCG@10 of 0.68, versus 0.61 for vector-only search. That is an improvement of 0.07 points, or about 11% relative. The result comes from the Atlas Search Relevance Experiment Report, which tested 2,400 labeled queries. It also noted that vector-only search failed badly on exact-match queries such as SKU numbers and part codes.
  - _Judge:_ The candidate gives the same nDCG@10 figures (0.61 vector-only vs 0.68 hybrid with reciprocal rank fusion) and correctly computes the 0.07 absolute and ~11% relative gain; extra details do not contradict the reference.

### q06 (temporal): What is the current status of Drift?

- **Vector** (2/2): Drift is set to resume in Q4 2026, starting October 5, with Daniel Brooks as lead. This is from the Q3 2026 planning notes (doc11) and replaces the earlier pause decided in the Q2 notes (doc05), when Daniel moved to Citadel full-time. The first milestone is distributed tracing for the Atlas search API and Beacon consumers.
  - _Judge:_ The candidate states Drift resumes October 5, 2026 with Daniel Brooks as lead and that this supersedes the earlier pause, matching the reference; the extra details do not contradict it, though the March 1 pause date and June 15 decision date are not stated explicitly.
- **Graph** (2/2): Drift is currently **on hold**, but it's set to resume. The March 1, 2026 decision to pause it so SRE capacity could go to Citadel was superseded by the June 15, 2026 decision (approved by Maya Chen) to restart it in Q4 2026. Per the Q3 planning notes, work starts October 5, 2026 with Daniel Brooks as lead. The first milestone is distributed tracing for the Atlas search API and Beacon consumers.
  - _Judge:_ The candidate includes all key facts: paused March 1, 2026, superseded by the June 15 decision, resuming October 5, 2026 with Daniel Brooks as lead; extra details do not contradict the reference.

### q07 (aggregation): Which people have both Python and LLM evaluation skills?

- **Vector** (0/2): The context doesn't say anything about anyone's Python or LLM evaluation skills. It names Arjun Patel and Lena Okafor as authors of the Atlas search relevance report, Sam Whitfield as product owner, and Fatima Al-Sayed as author of the security policy. None of these entries lists skills, so I can't tell who has both.
  - _Judge:_ The candidate says it cannot determine who has both skills and names no one with them, whereas the reference answer is Lena Okafor and Priya Nair.
- **Graph** (2/2): Lena Okafor (Python: expert, LLM evaluation: advanced) and Priya Nair (Python: advanced, LLM evaluation: advanced) have both skills. Arjun Patel and Hana Kobayashi have Python but no listed LLM evaluation skill.
  - _Judge:_ The candidate names both Lena Okafor and Priya Nair as having both skills, matching the reference, and the extra details about others lacking LLM evaluation do not contradict it.

### q08 (passage_detail): What incident happened during the Citadel rollout?

- **Vector** (2/2): During the Citadel rollout, on May 6, 2026, a rotation of the Airflow metadata credentials broke Beacon's Airflow connections for about three hours. The old secret was revoked before workers had picked up the new one.
  - _Judge:_ The candidate matches the reference on the date, the Airflow metadata credential rotation, Beacon's connections breaking, the three-hour duration, and the early revocation of the old secret, with no contradictions.
- **Graph** (2/2): During the Citadel rollout, on May 6, 2026, a rotation of the Airflow metadata credentials broke Beacon's Airflow connections for about three hours. The old secret was revoked before workers picked up the new one. As a result, rotations now happen in two stages with an overlap window (per the Citadel Retrospective).
  - _Judge:_ The candidate matches all key facts in the reference (May 6, 2026, Airflow metadata credential rotation, Beacon's Airflow connections broken ~3 hours, old secret revoked too early) and adds consistent extra detail without contradiction.

### q09 (multi_hop): Which tools does Echo rely on, directly or through its project dependencies?

- **Vector** (1/2): Based on the Echo Product Requirements, Echo relies on:

- **Atlas embedding service**, which Echo reuses for embeddings.
- **Weaviate**, where Echo stores its index.
- **Airflow**, which runs the ingestion jobs.
- **Vault**, which issues Echo's model API keys under the Citadel standard.

The context doesn't say which tools Atlas itself depends on, so any indirect dependencies beyond these aren't covered.
  - _Judge:_ The candidate correctly lists Weaviate and Airflow as direct tools and Vault via Citadel, but omits PostgreSQL via Atlas, AWS EKS and GitHub Actions via Citadel, and wrongly claims Atlas's dependencies are not covered.
- **Graph** (2/2): Echo uses two tools directly: Weaviate (vector store) and Airflow (ingestion jobs).

Through its project dependencies, it also relies on:
- **Atlas**, which Echo depends on for the embedding service. Atlas uses Weaviate and PostgreSQL.
- **Citadel**, which Echo depends on for model API keys issued through Vault. Citadel uses HashiCorp Vault, AWS EKS and GitHub Actions.

Atlas in turn depends on Beacon for click events, and Beacon uses Airflow. The Beacon Kafka topics are mentioned in the Atlas design doc, and Kafka and dbt are tied to Beacon through decisions, though the graph doesn't list them as Beacon's tools. That makes Kafka and dbt a looser, third-level link.

Altogether, the tools are Weaviate, Airflow, PostgreSQL, HashiCorp Vault, AWS EKS and GitHub Actions, with Kafka and dbt as indirect extras via Beacon.
  - _Judge:_ The candidate includes all reference facts: direct Weaviate and Airflow, via Atlas PostgreSQL and Weaviate, via Citadel Vault, AWS EKS and GitHub Actions; the extra Beacon/Kafka/dbt details are hedged additions that do not contradict the reference.

### q10 (passage_detail): Can Echo answer questions about parental leave?

- **Vector** (2/2): No. HR, compensation, and performance documents are excluded from Echo's index, a decision Priya Nair made on May 12, 2026 after consulting Fatima Al-Sayed on privacy risk. Questions about benefits or leave policy, including parental leave, should be redirected to the HR portal.
  - _Judge:_ The candidate matches all key facts in the reference (No; HR/compensation/performance docs excluded from index; redirected to HR portal) and the extra details about who decided and when do not contradict it.
- **Graph** (2/2): No. Echo excludes HR, compensation, and performance documents from its index, a decision Priya Nair made on May 12, 2026 after consulting Fatima Al-Sayed on privacy risk. Questions about benefits or leave policy are meant to be redirected to the HR portal.
  - _Judge:_ The candidate says No, states that HR, compensation, and performance documents are excluded from the index, and says leave questions are redirected to the HR portal. This matches every key fact in the reference, and the extra details about who made the decision and when do not contradict it.

### q11 (single_hop): Who approved the move from RabbitMQ to Kafka?

- **Vector** (0/2): The context doesn't say who approved the move from RabbitMQ to Kafka. The Beacon Migration Runbook only describes how the cutover works, and it names Hana Kobayashi as primary contact, Arjun Patel as secondary for consumer lag issues, and Daniel Brooks as owner of the EKS deployment of the Kafka Connect workers. None of them is identified as the approver.
  - _Judge:_ The candidate says the approver is not identified and never names Priya Nair, so it misses the key fact in the reference answer.
- **Graph** (2/2): Priya Nair approved the decision to migrate the event pipeline from RabbitMQ to Kafka on 2026-01-15. Hana Kobayashi proposed it.
  - _Judge:_ The candidate names Priya Nair as the approver, matching the reference, and the added details (date, proposer) do not contradict it.

### q12 (multi_hop): Which of Maya Chen's direct reports work on Atlas?

- **Vector** (0/2): The context doesn't say which people on Atlas report to Maya Chen. It states only that the Platform team reports to Maya Chen (doc09) and that Fatima Al-Sayed handles Vault access. Atlas is staffed by Arjun Patel (search API), Tomás Rivera (React search UI), Owen Gallagher (UX research), and Sam Whitfield (product owner), with Lena Okafor co-authoring the relevance experiment report. Nothing confirms that any of them are on the Platform team or are Maya's direct reports, though Tomás Rivera and Owen Gallagher are mentioned in the Platform onboarding guide as keeping the shared component library in sync.
  - _Judge:_ The candidate says the context does not confirm which Atlas staff report to Maya Chen and never identifies Arjun Patel and Tomás Rivera as her direct reports, so it misses the point of the reference answer.
- **Graph** (2/2): Two of Maya Chen's direct reports work on Atlas: Arjun Patel, who is the Search API owner, and Tomás Rivera, who works on the Search UI.

Her other direct reports, Daniel Brooks and Fatima Al-Sayed, work on Beacon, Citadel and Echo, but not on Atlas.
  - _Judge:_ The candidate names both Arjun Patel and Tomás Rivera as Maya Chen's direct reports on Atlas, matching the reference; the extra details do not contradict it.
