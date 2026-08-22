// FinGraph — schema constraints & indexes
// Run once against a fresh Neo4j database before importing data.

CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.accountID IS UNIQUE;
CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.customerID IS UNIQUE;
CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transactionID IS UNIQUE;
CREATE CONSTRAINT address_id IF NOT EXISTS FOR (a:Address) REQUIRE a.addressID IS UNIQUE;
CREATE CONSTRAINT jurisdiction_id IF NOT EXISTS FOR (j:Jurisdiction) REQUIRE j.jurisdictionID IS UNIQUE;
CREATE CONSTRAINT alert_id IF NOT EXISTS FOR (al:Alert) REQUIRE al.alertId IS UNIQUE;

CREATE INDEX account_risk IF NOT EXISTS FOR (a:Account) ON (a.riskScore);
CREATE INDEX transaction_date IF NOT EXISTS FOR (t:Transaction) ON (t.date);
CREATE INDEX transaction_status IF NOT EXISTS FOR (t:Transaction) ON (t.status);
