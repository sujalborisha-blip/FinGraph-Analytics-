# FinGraph — Graph Database & Algorithms

**Role:** Graph Database & Algorithms Expert
**Stack:** Neo4j, Cypher, Neo4j Graph Data Science (GDS)

This is my contribution to the FinGraph real-time fraud analytics project — the
graph schema, data model, and fraud-detection algorithms that the rest of the
pipeline (Kafka/Flink ingestion, React/D3 dashboard) is built on top of.

## Why a graph, not a relational table

Fraud isn't visible in a single transaction row — it's visible in the *shape* of
how money moves between accounts: cycles, hubs, and clusters that a relational
`JOIN` makes expensive and awkward to query. Modeling accounts, customers, and
transactions as a graph makes those patterns a native, cheap traversal instead.

## Graph schema

| Node | Key properties |
|---|---|
| `Account` | accountID, accountType, balance, riskScore, pagerank, louvainCommunity |
| `Customer` | customerID, name, fraudFlag, betweenness |
| `Transaction` | transactionID, amount, type, status, date |
| `Alert` | alertId, severity, score, reasons |
| `Jurisdiction` | jurisdictionID, riskLevel |
| `Address` | addressID, country, city |

| Relationship | Meaning |
|---|---|
| `(Account)-[:SENT]->(Transaction)-[:RECEIVED]->(Account)` | the actual money movement |
| `(Account)-[:TRANSACTED_TO {totalAmount, transactionCount}]->(Account)` | pre-aggregated account-to-account flow, used for fast cycle/pattern detection |
| `(Customer)-[:HAS_ACCOUNT]->(Account)` | ownership |
| `(Customer)-[:RESIDES_AT]->(Address)-[:LOCATED_IN]->(Jurisdiction)` | jurisdiction risk exposure |
| `(Customer)-[:SHARED_IDENTIFIERS]->(Customer)` | synthetic-identity signal |
| `(Alert)-[:ON]->(Account)`, `(Alert)-[:FLAGS]->(Transaction)` | links a raised alert back to what triggered it |

Full constraints and indexes: [`schema/constraints.cypher`](./schema/constraints.cypher).
Full import from the source CSVs: [`import/load_csv.cypher`](./import/load_csv.cypher).

## Graph Data Science algorithms

Implemented in [`gds/graph_algorithms.cypher`](./gds/graph_algorithms.cypher), run
against an in-memory GDS projection of the `Account` → `TRANSACTED_TO` → `Account`
graph:

| Algorithm | What it catches |
|---|---|
| **PageRank** | Accounts that are structurally central to money flow — a high-pagerank account receiving from many low-value sources is a classic laundering-hub signature. |
| **Louvain community detection** | Tightly-connected clusters of accounts. A fraud ring shows up as a small, dense community with few edges leaving it. |
| **Betweenness centrality** | "Bridge" accounts that money routinely passes *through* to reach elsewhere, even while their own balance stays low — the classic mule-account signature. |
| **Weakly Connected Components** | Sanity-check for isolated clusters worth a closer look. |
| **Node similarity** | Accounts transacting with the same counterparties in similar proportions — a signal for coordinated, structured fraud rather than one-off transfers. |

## Fraud-pattern queries

Implemented in [`queries/fraud_patterns.cypher`](./queries/fraud_patterns.cypher),
these are what the API layer calls directly:

1. **Cyclical fraud rings** — `TRANSACTED_TO` cycles of 3–6 accounts (layering).
2. **Mule account candidates** — internal accounts with high in-degree *and*
   out-degree (pass-through behavior).
3. **High-risk jurisdiction exposure** — customers with accounts tied to
   high-risk jurisdictions.
4. **Shared identifiers** — customers linked through the same email/phone/address.
5. **Community risk rollup** — aggregates risk by Louvain community.

## How this plugs into the rest of the pipeline

The streaming side (Kafka producer → Flink scoring) writes alerts back into this
same graph via `MERGE (al:Alert)...-[:ON]->(sender:Account)`, so every real-time
alert lands as a first-class node connected to the historical graph — the ring
and mule-account queries above pick up newly-flagged accounts automatically,
no separate sync step needed.
