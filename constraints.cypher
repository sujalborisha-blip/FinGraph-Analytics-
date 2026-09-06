// FinGraph Graph Schema
// Member 3: Graph Database & Algorithms Expert
//
// Nodes:  Person, Account, Bank
// Edges:  (Person)-[:OWNS]->(Account)
//         (Account)-[:HELD_AT]->(Bank)
//         (Account)-[:TRANSFERRED_TO {amount, currency, timestamp, channel, transaction_id}]->(Account)

// --- Uniqueness constraints (also create backing indexes) ---
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.person_id IS UNIQUE;

CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;

CREATE CONSTRAINT bank_name_unique IF NOT EXISTS
FOR (b:Bank) REQUIRE b.name IS UNIQUE;

CREATE CONSTRAINT transaction_id_unique IF NOT EXISTS
FOR ()-[t:TRANSFERRED_TO]-() REQUIRE t.transaction_id IS UNIQUE;

// --- Supporting indexes for common lookups ---
CREATE INDEX person_kyc_idx IF NOT EXISTS
FOR (p:Person) ON (p.kyc_verified);

CREATE INDEX account_type_idx IF NOT EXISTS
FOR (a:Account) ON (a.account_type);

CREATE INDEX transferred_timestamp_idx IF NOT EXISTS
FOR ()-[t:TRANSFERRED_TO]-() ON (t.timestamp);

CREATE INDEX transferred_amount_idx IF NOT EXISTS
FOR ()-[t:TRANSFERRED_TO]-() ON (t.amount);
