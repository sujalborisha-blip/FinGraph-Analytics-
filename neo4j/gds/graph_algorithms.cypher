// FinGraph — Graph Data Science algorithms
// Requires the Neo4j Graph Data Science (GDS) library plugin.
// These reproduce/refresh the pagerank, louvainCommunity, and betweenness values
// that ship pre-computed in the CSVs, and show the actual GDS calls behind them.

// ---------- 1. Project the transaction graph into GDS's in-memory graph ----------
// :name project_transaction_graph
CALL gds.graph.project(
  'fingraph-transactions',
  'Account',
  {
    TRANSACTED_TO: {
      properties: 'totalAmount'
    }
  }
);

// ---------- 2. PageRank — surfaces accounts that are structurally central to money flow ----------
// High pagerank + high in-degree is a classic laundering-hub signature.
// :name run_pagerank
CALL gds.pageRank.write('fingraph-transactions', {
  relationshipWeightProperty: 'totalAmount',
  writeProperty: 'pagerank',
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodePropertiesWritten, ranIterations;

// ---------- 3. Louvain community detection — finds tightly-connected clusters of accounts ----------
// A fraud ring usually shows up as a small, dense community with few external edges.
// :name run_louvain
CALL gds.louvain.write('fingraph-transactions', {
  relationshipWeightProperty: 'totalAmount',
  writeProperty: 'louvainCommunity'
})
YIELD communityCount, modularity;

// ---------- 4. Betweenness centrality — finds "bridge" accounts (likely mules) ----------
// High betweenness = money routinely passes *through* this account to reach others,
// even if its own balance stays low. Classic mule-account signature.
// :name run_betweenness
CALL gds.betweenness.write('fingraph-transactions', {
  writeProperty: 'betweenness'
})
YIELD minCentrality, maxCentrality, meanCentrality;

// ---------- 5. Weakly Connected Components — sanity check for isolated fraud clusters ----------
// :name run_wcc
CALL gds.wcc.stream('fingraph-transactions')
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).accountID) AS accounts
WHERE size(accounts) > 1
RETURN componentId, size(accounts) AS clusterSize, accounts
ORDER BY clusterSize DESC
LIMIT 20;

// ---------- 6. Similarity — accounts with near-identical transaction fingerprints ----------
// Flags accounts that transact with the same counterparties in similar proportions,
// a signal for coordinated/structured fraud rather than one-off transfers.
// :name run_node_similarity
CALL gds.nodeSimilarity.stream('fingraph-transactions')
YIELD node1, node2, similarity
WHERE similarity > 0.8
RETURN gds.util.asNode(node1).accountID AS accountA,
       gds.util.asNode(node2).accountID AS accountB,
       similarity
ORDER BY similarity DESC
LIMIT 25;

// ---------- cleanup ----------
// :name drop_projection
CALL gds.graph.drop('fingraph-transactions');
