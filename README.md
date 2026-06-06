# Nova — Order & Returns Support Assistant for Nestwell

**AAI-510 Final Project · Group 7**
An AI customer-support agent that answers Nestwell's routine order and policy
questions, built and evaluated on Databricks with MLflow.

---

## Overview

Nestwell is a (fictional) home-and-lifestyle online retailer handling ~10,000
support tickets a month. **Nova** automates the routine ones — "where is my
order," "can I return this," "how long does a refund take," "what does shipping
cost" — so human agents can focus on the harder cases.

Nova is a single **ReAct** agent (reason → act → observe → respond). The model
handles the language; two governed tools handle the facts, so Nova cannot invent
order details. Out-of-scope requests are politely declined.

## Architecture

# (ATTACH)


## Repository contents

| File | What it is |
|------|------------|
| `01_data_pipeline.ipynb` / `.html` | Loads the CSVs, builds the orders table in Unity Catalog, registers both tools, runs unit tests. (DE) |
| `02_agent_definition.ipynb` / `.html` | System prompt, ReAct loop, MLflow tracing, 5 traces incl. a dual-LLM comparison and two out-of-scope refusals. (AIE) |
| `03_evaluation.ipynb` / `.html` | 12-question eval, MLflow judges, documented human review, model comparison, ROI, written commentary. (AIE) |
| `nestwell_orders.csv` · `nestwell_order_items.csv` · `nestwell_customers.csv` | Synthetic Olist-style data (800 orders / 1,207 items / 300 customers). |
| `nestwell_policy.txt` | The return & shipping policy the `policy_lookup` tool reads. |

> `.html` exports include all cell outputs, so reviewers without a Databricks
> workspace can see the traces, scores, and results.

## Tools

- **`order_lookup(order_id)`** — SQL Unity Catalog function returning an order's
  status, delivery dates, item count, total, and a return-eligible flag.
- **`policy_lookup(topic)`** — Python Unity Catalog function returning the
  relevant section of the policy via keyword match (the doc is short enough that
  no vector search is needed).

## Models compared

| Model | Role |
|-------|------|
| `databricks-gpt-oss-20b` | Smaller / baseline |
| `databricks-gpt-oss-120b` | Larger / reasoning |

Both are run on identical inputs so the only variable is model size — the
cleanest basis for the cost-vs-effectiveness (ROI) comparison.

## Evaluation

Every answer is scored by five MLflow judges:

- **Correctness** and **Safety** (built-in)
- **Grounded-in-tools** and **Scope-control** (Guidelines, pass/fail)
- **nova_grounding_judge** (custom `make_judge`)

A human then reviews the flagged cases and records agreement/disagreement with
the judge — the human-in-the-loop step. Results, the model comparison, and an
ROI analysis are in Notebook 3, with a written commentary cell.

**Headline result:** both models scored 1.00 on safety and scope and 0.86 on
grounding; correctness was 0.70 (20b) vs 0.86 (120b). On the ROI, the larger
model costs only a few dollars more per month but produces materially more
correctly-resolved tickets, so it pays for itself many times over.

## How to run (Databricks)

1. Create schema/volume and upload the four data files:
   `main.nestwell.data` ← the three CSVs + `nestwell_policy.txt`.
2. Run the notebooks in order: **01 → 02 → 03**.
3. Set `EXPERIMENT`/paths to your own workspace where noted in the first cells.
4. View traces and eval results via the notebook's MLflow experiment.

**Environment:** Databricks Free Edition (serverless compute), MLflow ≥ 3.9.

## Design decisions & deviations

- **Scoped to order-ID lookups.** The raw Olist data uses Portuguese product
  names/codes, so we kept Nova focused on order-ID lookups + a short English
  policy doc, keeping every answer grounded in clean tool output.
- **Keyword policy lookup, not vector search.** The ~500-word policy fits in
  context; vector search would add infrastructure the use case doesn't need.
- **Plain-text replies.** A system-prompt rule removes emojis/markdown after
  evaluation showed they hurt readability and tripped the grounding judge.
- **Simple human-in-the-loop.** A documented manual review of flagged cases,
  rather than an automated alignment routine — more transparent for this size.

## Team

Group 7 — Wael Alhathal (AI Engineer), Idrees Khan (Data Engineer) and Francisco Felix (PM)
