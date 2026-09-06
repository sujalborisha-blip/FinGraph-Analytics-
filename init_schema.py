"""
Initializes the FinGraph Neo4j schema: constraints + indexes.
Member 3: Graph Database & Algorithms Expert

Usage:
    python init_schema.py --uri bolt://localhost:7687 --user neo4j --password fingraph123
"""

import argparse
from pathlib import Path

from neo4j import GraphDatabase

SCHEMA_FILE = Path(__file__).parent / "schema" / "constraints.cypher"


def run_schema(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    statements = [
        s.strip()
        for s in SCHEMA_FILE.read_text().split(";")
        if s.strip() and not s.strip().startswith("//")
    ]
    # strip leading comment-only lines within multi-line statements
    cleaned = []
    for stmt in statements:
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("//")]
        joined = "\n".join(lines).strip()
        if joined:
            cleaned.append(joined)

    with driver.session() as session:
        for stmt in cleaned:
            print(f"[schema] running: {stmt.splitlines()[0][:70]}...")
            session.run(stmt)

    driver.close()
    print(f"[schema] done. {len(cleaned)} statements applied.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="fingraph123")
    args = parser.parse_args()
    run_schema(args.uri, args.user, args.password)
