"""
FinGraph — Neo4j sink.

Consumes fingraph.alerts (scored by the Flink job) and writes each into the graph:
  - MERGEs an :Alert node linked to the flagged sender :Account via [:ON]
  - bumps the account's riskScore
  - MERGEs the underlying :Transaction + :SENT/:RECEIVED edges if they don't already
    exist (covers accounts/transactions the batch import hasn't seen yet)

This is the piece that closes the loop between the streaming layer (Kafka + Flink)
and the graph layer (Neo4j) that the React dashboard reads from.
"""

import json
import os
import time
import uuid

from kafka import KafkaConsumer
from neo4j import GraphDatabase

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.environ.get("KAFKA_ALERTS_TOPIC", "fingraph.alerts")
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "fingraph12345")

WRITE_ALERT_QUERY = """
MERGE (t:Transaction {transactionID: $transactionID})
  ON CREATE SET t.date = datetime($sourceDate), t.amount = $amount,
                t.type = $type, t.status = $status
MERGE (sender:Account {accountID: $senderAccountID})
MERGE (receiver:Account {accountID: $receiverAccountID})
MERGE (sender)-[:SENT]->(t)
MERGE (t)-[:RECEIVED]->(receiver)
MERGE (al:Alert {alertId: $alertId})
SET al.scenario = $scenario,
    al.severity = $severity,
    al.score = $score,
    al.reasons = $reasons,
    al.createdAt = datetime($createdAt)
MERGE (al)-[:ON]->(sender)
MERGE (al)-[:FLAGS]->(t)
SET sender.riskScore = CASE WHEN $score > coalesce(sender.riskScore, 0)
                             THEN $score ELSE coalesce(sender.riskScore, 0) END
"""


def run():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id="fingraph-neo4j-sink",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="latest",
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[neo4j-sink] waiting for kafka: {exc}")
            time.sleep(5)

    print(f"[neo4j-sink] listening on {TOPIC}, writing to {NEO4J_URI}")
    with driver.session() as session:
        for msg in consumer:
            event = msg.value
            params = {
                "alertId": f"{event['type']}_{event['transactionID']}_{uuid.uuid4().hex[:8]}",
                "transactionID": event["transactionID"],
                "senderAccountID": event["senderAccountID"],
                "receiverAccountID": event["receiverAccountID"],
                "amount": float(event["amount"]),
                "type": event["type"],
                "status": event.get("status", "Pending"),
                "sourceDate": event.get("sourceDate") or event.get("eventTime"),
                "scenario": ", ".join(event.get("reasons", [])) or "rule-engine",
                "severity": event.get("severity", "medium"),
                "score": event.get("riskScore", 0),
                "reasons": event.get("reasons", []),
                "createdAt": event.get("eventTime"),
            }
            session.run(WRITE_ALERT_QUERY, **params)
            print(f"[neo4j-sink] wrote alert for {params['senderAccountID']} "
                  f"(score={params['score']}, severity={params['severity']})")


if __name__ == "__main__":
    run()
