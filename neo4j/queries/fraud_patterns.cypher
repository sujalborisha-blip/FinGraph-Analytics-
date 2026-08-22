// FinGraph — fraud pattern queries
// These back the FastAPI endpoints in ../../api/main.py

// 1. Fraud rings: cyclical money movement between 3-6 accounts
// :name ring_detection
MATCH path = (a:Account)-[:TRANSACTED_TO*3..6]->(a)
WITH path, [n IN nodes(path) | n.accountID] AS ring, reduce(s = 0.0, r IN relationships(path) | s + r.totalAmount) AS ringVolume
RETURN DISTINCT ring, ringVolume
ORDER BY ringVolume DESC
LIMIT 25;

// 2. Mule accounts: high in-degree, high out-degree, low dwell time (pass-through accounts)
// :name mule_accounts
MATCH (a:Account)
WHERE a.internalExternal = 'Internal'
OPTIONAL MATCH (a)<-[:TRANSACTED_TO]-(inbound:Account)
OPTIONAL MATCH (a)-[:TRANSACTED_TO]->(outbound:Account)
WITH a, count(DISTINCT inbound) AS inDegree, count(DISTINCT outbound) AS outDegree
WHERE inDegree >= 3 AND outDegree >= 3
RETURN a.accountID AS accountID, a.accountNumber AS accountNumber, inDegree, outDegree, a.pagerank AS pagerank
ORDER BY (inDegree + outDegree) DESC
LIMIT 25;

// 3. High-risk jurisdiction exposure
// :name high_risk_exposure
MATCH (c:Customer)-[:RESIDES_AT]->(:Address)-[:LOCATED_IN]->(j:Jurisdiction {riskLevel: 'High'})
MATCH (c)-[:HAS_ACCOUNT]->(a:Account)
RETURN c.customerID AS customerID, c.name AS name, j.name AS jurisdiction, a.accountID AS accountID
ORDER BY c.name
LIMIT 50;

// 4. Shared identifiers: distinct customers linked through the same email/phone/address (synthetic identity risk)
// :name shared_identifiers
MATCH (c1:Customer)-[:SHARED_IDENTIFIERS]->(c2:Customer)
RETURN c1.customerID AS customerA, c1.name AS nameA, c2.customerID AS customerB, c2.name AS nameB
LIMIT 50;

// 5. Community risk rollup (Louvain communities pre-computed on import)
// :name community_risk
MATCH (a:Account)
WHERE a.louvainCommunity IS NOT NULL
RETURN a.louvainCommunity AS community, count(a) AS accounts,
       sum(CASE WHEN a.highRiskJurisdiction THEN 1 ELSE 0 END) AS highRiskAccounts,
       avg(a.pagerank) AS avgPagerank
ORDER BY highRiskAccounts DESC
LIMIT 25;

// 6. Ego network for the graph visualization panel (2-hop neighbourhood of one account)
// :name account_ego_network params: {accountID: "..."}
MATCH (center:Account {accountID: $accountID})
CALL apoc.path.subgraphAll(center, {maxLevel: 2, relationshipFilter: 'TRANSACTED_TO'})
YIELD nodes, relationships
RETURN nodes, relationships;

// 7. Realtime alert write-back (used by the Flink → Neo4j sink)
// :name write_alert params: {alertId, accountID, scenario, severity, score, ts}
MERGE (al:Alert {alertId: $alertId})
SET al.scenario = $scenario,
    al.severity = $severity,
    al.score = $score,
    al.createdAt = datetime($ts)
WITH al
MATCH (a:Account {accountID: $accountID})
MERGE (al)-[:ON]->(a)
SET a.riskScore = CASE WHEN $score > a.riskScore THEN $score ELSE a.riskScore END;
