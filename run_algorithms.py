"""
Runs the GDS fraud-detection algorithms end-to-end and prints a summary
report. Also writes results to alerts.json for the frontend to poll
(a lightweight alternative to a full GraphQL/REST layer).

Member 3: Graph Database & Algorithms Expert

Usage:
    python run_algorithms.py --uri bolt://localhost:7687 --user neo4j --password fingraph123
"""

import argparse
import json
from pathlib import Path

from neo4j import GraphDatabase

PROJECT_GRAPH = """
CALL gds.graph.exists('fingraph') YIELD exists
WITH exists
CALL apoc.do.when(
  exists,
  "CALL gds.graph.drop('fingraph', false) YIELD graphName RETURN graphName",
  "RETURN null AS graphName",
  {}
) YIELD value
RETURN value
"""

# Fallback if APOC isn't installed: try/except around a simple drop-then-create.
SIMPLE_DROP = "CALL gds.graph.drop('fingraph', false) YIELD graphName RETURN graphName"
SIMPLE_PROJECT = """
CALL gds.graph.project(
  'fingraph', 'Account',
  { TRANSFERRED_TO: { orientation: 'NATURAL', properties: 'amount' } }
)
"""

PAGERANK = """
CALL gds.pageRank.stream('fingraph', { relationshipWeightProperty: 'amount' })
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS account, score
RETURN account.account_id AS account_id, score
ORDER BY score DESC LIMIT 10
"""

LOUVAIN = """
CALL gds.louvain.stream('fingraph', { relationshipWeightProperty: 'amount' })
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId).account_id) AS members
WITH communityId, members, size(members) AS community_size
WHERE community_size >= 3 AND community_size <= 8
RETURN communityId, community_size, members
ORDER BY community_size DESC LIMIT 10
"""

CIRCULAR = """
MATCH path = (a:Account)-[:TRANSFERRED_TO*3..6]->(a)
WITH path, a, [n IN nodes(path) | n.account_id] AS account_chain
RETURN a.account_id AS start_account, account_chain, length(path) AS ring_length
ORDER BY ring_length DESC LIMIT 10
"""


def run(uri, user, password, out_file):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    report = {}

    with driver.session() as session:
        try:
            session.run(SIMPLE_DROP)
        except Exception:
            pass  # graph didn't exist yet, that's fine
        session.run(SIMPLE_PROJECT)

        report["top_pagerank_accounts"] = [dict(r) for r in session.run(PAGERANK)]
        report["dense_communities"] = [dict(r) for r in session.run(LOUVAIN)]
        report["circular_rings"] = [dict(r) for r in session.run(CIRCULAR)]

        session.run("CALL gds.graph.drop('fingraph', false)")

    driver.close()

    out_path = Path(out_file)
    out_path.write_text(json.dumps(report, indent=2, default=str))

    print(f"\n=== FinGraph Fraud Detection Report ===")
    print(f"Top PageRank accounts: {len(report['top_pagerank_accounts'])}")
    print(f"Dense suspicious communities: {len(report['dense_communities'])}")
    print(f"Circular money-flow rings: {len(report['circular_rings'])}")
    print(f"Full report written to {out_path.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="fingraph123")
    parser.add_argument("--out", default="alerts.json")
    args = parser.parse_args()
    run(args.uri, args.user, args.password, args.out)
