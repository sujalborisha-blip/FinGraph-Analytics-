// FinGraph Fraud Pattern Queries (Cypher)
// Member 3: Graph Database & Algorithms Expert
// Week 2: Stream Processing & Cypher Queries

// ---------------------------------------------------------------------
// 1. Circular money flow: A -> B -> C -> ... -> A, within a time window,
//    length 3 to 6 hops. Classic "layering" pattern in money laundering.
// ---------------------------------------------------------------------
MATCH path = (a:Account)-[:TRANSFERRED_TO*3..6]->(a)
WHERE ALL(r IN relationships(path) WHERE r.timestamp > datetime() - duration('P7D'))
WITH path, a,
     [r IN relationships(path) | r.amount] AS amounts,
     [n IN nodes(path) | n.account_id] AS account_chain
RETURN a.account_id AS start_account,
       account_chain,
       amounts,
       length(path) AS ring_length
ORDER BY ring_length DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 2. Fan-out mule pattern: one account sends to many distinct accounts
//    in a short time window, then those funds move on quickly (layering).
// ---------------------------------------------------------------------
MATCH (source:Account)-[t:TRANSFERRED_TO]->(target:Account)
WHERE t.timestamp > datetime() - duration('PT1H')
WITH source, count(DISTINCT target) AS fan_out_count, collect(DISTINCT target.account_id) AS targets, sum(t.amount) AS total_sent
WHERE fan_out_count >= 4
RETURN source.account_id AS source_account, fan_out_count, targets, total_sent
ORDER BY fan_out_count DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 3. Fan-in mule pattern: many accounts converge funds into one account
//    in a short window (funnel/collector account).
// ---------------------------------------------------------------------
MATCH (source:Account)-[t:TRANSFERRED_TO]->(target:Account)
WHERE t.timestamp > datetime() - duration('PT1H')
WITH target, count(DISTINCT source) AS fan_in_count, collect(DISTINCT source.account_id) AS sources, sum(t.amount) AS total_received
WHERE fan_in_count >= 4
RETURN target.account_id AS collector_account, fan_in_count, sources, total_received
ORDER BY fan_in_count DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 4. Rapid pass-through: money enters and leaves an account within
//    minutes ("smurfing" / shell-account behaviour).
// ---------------------------------------------------------------------
MATCH (in_acc:Account)-[in_t:TRANSFERRED_TO]->(mid:Account)-[out_t:TRANSFERRED_TO]->(out_acc:Account)
WHERE out_t.timestamp > in_t.timestamp
  AND duration.between(datetime(in_t.timestamp), datetime(out_t.timestamp)).minutes < 10
  AND out_t.amount >= 0.9 * in_t.amount
RETURN mid.account_id AS pass_through_account,
       in_acc.account_id AS received_from,
       out_acc.account_id AS sent_to,
       in_t.amount AS amount_in,
       out_t.amount AS amount_out,
       in_t.timestamp AS in_time,
       out_t.timestamp AS out_time
ORDER BY in_time DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 5. Cross-bank shuffling: accounts owned by the same person moving
//    money between banks repeatedly (structuring behaviour).
// ---------------------------------------------------------------------
MATCH (p:Person)-[:OWNS]->(a1:Account)-[t:TRANSFERRED_TO]->(a2:Account)<-[:OWNS]-(p)
MATCH (a1)-[:HELD_AT]->(b1:Bank), (a2)-[:HELD_AT]->(b2:Bank)
WHERE b1 <> b2
RETURN p.person_id AS person, b1.name AS from_bank, b2.name AS to_bank,
       count(t) AS transfer_count, sum(t.amount) AS total_moved
ORDER BY total_moved DESC
LIMIT 25;


// ---------------------------------------------------------------------
// 6. Flagged by the Flink velocity detector (cross-reference with
//    stream-processor/flink_job.py's FanOutBurstDetector)
// ---------------------------------------------------------------------
MATCH (a:Account)-[t:TRANSFERRED_TO {velocity_alert: true}]->(b:Account)
RETURN a.account_id AS from_account, b.account_id AS to_account,
       t.amount AS amount, t.timestamp AS timestamp
ORDER BY t.timestamp DESC
LIMIT 50;
