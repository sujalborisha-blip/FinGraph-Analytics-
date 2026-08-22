// ============================================================================
// FinGraph: Week 4 Query Optimization
// Description: Adding database indexes to speed up graph traversals
// ============================================================================

// Index for faster Account lookups
CREATE INDEX account_id_index IF NOT EXISTS FOR (a:Account) ON (a.account_id);

// Index for faster Transaction lookups
CREATE INDEX tx_id_index IF NOT EXISTS FOR (t:Transaction) ON (t.transaction_id);

// Verify index creation
SHOW INDEXES;
