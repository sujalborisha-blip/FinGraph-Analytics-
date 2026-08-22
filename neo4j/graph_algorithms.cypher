// Neo4j Graph Algorithms for Fraud Detection

// 1. Calculate PageRank to find highly central accounts (potential money mules)
CALL gds.pageRank.stream({
  nodeQuery: 'MATCH (a:Account) RETURN id(a) AS id',
  relationshipQuery: 'MATCH (a1:Account)-[:TRANSFERRED_TO]->(a2:Account) RETURN id(a1) AS source, id(a2) AS target'
})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS account, score
// Update the Graph Risk Score based on PageRank centrality
SET account.graph_risk_score = score * 10
RETURN account.account_id, account.graph_risk_score
ORDER BY account.graph_risk_score DESC
LIMIT 10;

// 2. Weakly Connected Components (WCC) to detect isolated syndicates
CALL gds.wcc.stream({
  nodeQuery: 'MATCH (a:Account) RETURN id(a) AS id',
  relationshipQuery: 'MATCH (a1:Account)-[:TRANSFERRED_TO]->(a2:Account) RETURN id(a1) AS source, id(a2) AS target'
})
YIELD nodeId, componentId
WITH gds.util.asNode(nodeId) AS account, componentId
SET account.syndicate_cluster_id = componentId
RETURN componentId, count(account) AS cluster_size
ORDER BY cluster_size DESC;

// 3. Flagging high-risk accounts based on the combination of algorithms
MATCH (a:Account)
WHERE a.graph_risk_score > 50 AND a.syndicate_cluster_id IS NOT NULL
SET a.status = 'SUSPENDED_FRAUD_RING'
RETURN a.account_id, a.status;
