// FinGraph GDS Algorithms
// Member 3: Graph Database & Algorithms Expert
// Requires the Graph Data Science (GDS) plugin (already enabled in docker-compose.yml)

// ---------------------------------------------------------------------
// 0. Project the transaction graph into an in-memory GDS graph.
//    Weighted by amount so high-value flows dominate the algorithms.
// ---------------------------------------------------------------------
CALL gds.graph.project(
  'fingraph',
  'Account',
  {
    TRANSFERRED_TO: {
      orientation: 'NATURAL',
      properties: 'amount'
    }
  }
);


// ---------------------------------------------------------------------
// 1. PageRank — surfaces accounts that receive disproportionate,
//    well-connected inflow (potential collector / mule hub accounts).
// ---------------------------------------------------------------------
CALL gds.pageRank.stream('fingraph', { relationshipWeightProperty: 'amount' })
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS account, score
RETURN account.account_id AS account_id, score
ORDER BY score DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 2. Louvain community detection — clusters accounts into tightly
//    connected groups; unusually dense small clusters often correspond
//    to a fraud ring rather than an organic social/business network.
// ---------------------------------------------------------------------
CALL gds.louvain.stream('fingraph', { relationshipWeightProperty: 'amount' })
YIELD nodeId, communityId
WITH communityId, collect(gds.util.asNode(nodeId).account_id) AS members
WITH communityId, members, size(members) AS community_size
WHERE community_size >= 3 AND community_size <= 8   // small, dense clusters
RETURN communityId, community_size, members
ORDER BY community_size DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 3. Weakly Connected Components — finds isolated transaction clusters,
//    useful for scoping a ring before running the algorithms above on
//    just that subgraph.
// ---------------------------------------------------------------------
CALL gds.wcc.stream('fingraph')
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).account_id) AS members
RETURN componentId, size(members) AS component_size, members
ORDER BY component_size DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 4. Cycle detection via GDS — degree centrality as a cheap first pass
//    to shortlist candidate ring members before running the expensive
//    variable-length cycle Cypher query (queries/fraud_patterns.cypher #1)
//    only on the shortlisted subgraph.
// ---------------------------------------------------------------------
CALL gds.degree.stream('fingraph', { orientation: 'NATURAL' })
YIELD nodeId, score AS out_degree
WITH gds.util.asNode(nodeId) AS account, out_degree
WHERE out_degree >= 2
RETURN account.account_id AS account_id, out_degree
ORDER BY out_degree DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 5. Betweenness Centrality — identifies "broker" accounts that sit on
//    many shortest paths between other accounts (potential layering
//    intermediaries / money mules).
// ---------------------------------------------------------------------
CALL gds.betweenness.stream('fingraph')
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS account, score
WHERE score > 0
RETURN account.account_id AS account_id, score
ORDER BY score DESC
LIMIT 25;


// ---------------------------------------------------------------------
// Cleanup: drop the projection when done (re-run step 0 before reusing)
// ---------------------------------------------------------------------
CALL gds.graph.drop('fingraph', false);
