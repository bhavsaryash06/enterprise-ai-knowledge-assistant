# RAG Evaluation Summary

## Project

Production-Ready Enterprise AI Knowledge Assistant

This evaluation measures how well the assistant retrieves relevant company policy documents, generates grounded answers, and escalates unsupported questions when evidence is weak.

The assistant uses:

- OpenAI embeddings
- Qdrant vector search
- Query rewriting
- Metadata filtering
- Hugging Face Cross-Encoder reranking
- LangGraph workflow orchestration
- Evidence strength checking
- Citation-backed answer generation

---

## Evaluation Dataset

The evaluation dataset contains 12 curated enterprise policy questions.

| Question Type | Count |
|---|---:|
| Supported policy questions | 10 |
| Unsupported / escalation questions | 2 |
| Total questions | 12 |

The supported questions cover:

- Finance reimbursement
- Remote work
- IT security
- Data privacy
- HR leave
- Access control
- Employee onboarding
- Travel and expense
- Device usage
- Incident reporting

The unsupported questions test whether the assistant avoids hallucinating when the documents do not provide enough evidence.

---

## Retrieval Evaluation

Retrieval evaluation checks whether the system retrieves the expected source documents for each supported question.

### Retrieval Metrics

| Metric | Result |
|---|---:|
| Supported questions | 10 |
| Unsupported questions | 2 |
| Supported average source recall | 85% |
| Supported top-source accuracy | 90% |
| Retrieval pass count | 6 |
| Retrieval partial count | 4 |
| Retrieval fail count | 0 |
| Retrieval error count | 0 |

### Interpretation

The retrieval system successfully retrieved most expected source documents for supported policy questions.

A few questions were marked as partial because the assistant retrieved some, but not all, expected documents. This is expected in realistic RAG systems because many policies overlap across departments.

Unsupported questions were not scored using source recall because vector search will always return nearest chunks, even when the question is not truly supported by the knowledge base. Unsupported behavior is evaluated separately through answer and escalation evaluation.

---

## Answer Evaluation

Answer evaluation checks whether the assistant:

- answers supported policy questions
- escalates unsupported questions
- includes expected policy details
- returns source-backed answers
- avoids unsupported claims

### Answer Metrics

| Metric | Result |
|---|---:|
| Total questions | 12 |
| Passed questions | 12 |
| Failed questions | 0 |
| Behavior accuracy | 100% |
| Supported questions | 10 |
| Supported pass count | 10 |
| Unsupported questions | 2 |
| Unsupported pass count | 2 |
| Average answer point match rate | 80% |

### Interpretation

The assistant correctly answered all supported questions and escalated all unsupported questions.

The behavior accuracy of 100% means the assistant made the correct high-level decision for every evaluation case:

- supported question → answer
- unsupported question → escalation

The answer point match rate of 80% means the generated answers included most of the expected policy details such as approval requirements, deadlines, limits, responsible teams, and escalation paths.

---

## Before and After Prompt Improvement

Initial answer evaluation showed that the assistant often gave correct but incomplete answers.

The answer generation prompt was improved to require:

- direct answer
- required employee actions
- limits, deadlines, approvals, and conditions
- responsible team or escalation path
- source usage
- human review decision

### Improvement Summary

| Metric | Before | After |
|---|---:|---:|
| Passed questions | 7 / 12 | 12 / 12 |
| Failed questions | 5 / 12 | 0 / 12 |
| Behavior accuracy | 100% | 100% |
| Average answer point match rate | 50% | 80% |

---

## Example Evaluation Behaviors

### Supported Question

Question:

> Can I get reimbursed for a home office monitor?

Expected behavior:

- answer the question
- mention manager approval
- mention reimbursement limit
- cite Finance and Remote Work policy sources

Observed behavior:

- answered successfully
- included reimbursement amount
- included approval requirement
- returned policy sources

---

### Unsupported Question

Question:

> What is the company policy for buying cryptocurrency?

Expected behavior:

- do not invent policy
- escalate because evidence is weak

Observed behavior:

- escalation required
- low confidence
- assistant stated that it could not find strong enough evidence

---

## Key Findings

1. The retrieval pipeline is strong enough for a first production-style portfolio version.
2. Query rewriting and reranking improve the quality of retrieved sources.
3. Evidence checking reduces hallucination risk by escalating weak-evidence questions.
4. The answer generator improved significantly after prompt tuning.
5. The system correctly handles unsupported questions instead of forcing an answer.
6. The evaluation dataset is small and synthetic, so results should be described as performance on a curated test set, not as universal accuracy.

---

## Current Limitations

This evaluation is useful but not final.

Current limitations:

- The dataset contains only 12 questions.
- Documents are synthetic company policies.
- The answer point matcher uses keyword overlap, not human judgment.
- Some retrieval results are marked partial even when the final answer is still correct.
- The system has not yet been tested on scanned PDFs, tables, messy formatting, or real enterprise document versions.
- The evaluation does not yet include RAGAS or LLM-as-judge scoring.

---

## Next Improvements

Future evaluation improvements may include:

- expanding the dataset to 50–100 questions
- adding harder multi-document reasoning questions
- adding conflicting-policy test cases
- adding RAGAS faithfulness and context precision metrics
- adding LangSmith dataset-based evaluation
- adding human-reviewed expected answers
- testing PDF versions of the same policies
- testing document version conflicts and outdated policy handling

---

## Final Evaluation Summary

On a curated 12-question enterprise policy evaluation dataset, the assistant achieved:

- 85% supported source recall
- 90% supported top-source accuracy
- 100% behavior accuracy
- 100% answer evaluation pass rate
- 80% average answer point match rate

These results show that the assistant can retrieve relevant policy evidence, generate grounded answers, and escalate unsupported questions when evidence is weak.