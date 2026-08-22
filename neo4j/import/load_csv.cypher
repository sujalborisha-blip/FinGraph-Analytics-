// FinGraph — bulk import from the CSVs in /data (as provided in demo-fraud-master.zip)
// Run with `cypher-shell` or the Neo4j Browser, with the /data folder mounted at
// $NEO4J_HOME/import (docker-compose already does this — see ../../docker-compose.yml).
// Run constraints.cypher first.

// ---------- Nodes ----------

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Account_with_labels.csv' AS row
MERGE (a:Account {accountID: row.accountID})
SET a.accountType = row.accountType,
    a.accountNumber = row.accountNumber,
    a.status = row.status,
    a.balance = toFloat(row.balance),
    a.louvainCommunity = toInteger(row.louvainCommunity),
    a.pagerank = toFloat(row.pagerank),
    a.internalExternal = row.internalExternal,
    a.highRiskJurisdiction = toBoolean(row.highRiskJurisdiction),
    a.riskScore = 0.0;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer.csv' AS row
MERGE (c:Customer {customerID: row.customerID})
SET c.name = row.name,
    c.dateOfBirth = row.dateOfBirth,
    c.fraudFlag = toBoolean(row.fraudFlag),
    c.louvainCommunity = toInteger(row.louvainCommunity),
    c.betweenness = toFloat(row.betweenness),
    c.pagerank = toFloat(row.pagerank);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Transaction.csv' AS row
MERGE (t:Transaction {transactionID: row.transactionID})
SET t.date = datetime(row.date),
    t.amount = toFloat(row.amount),
    t.type = row.type,
    t.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Address.csv' AS row
MERGE (ad:Address {addressID: row.addressID})
SET ad.country = row.country,
    ad.city = row.city,
    ad.street = row.street,
    ad.state = row.state;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Jurisdiction.csv' AS row
MERGE (j:Jurisdiction {jurisdictionID: row.jurisdictionID})
SET j.name = row.name,
    j.riskLevel = row.riskLevel;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Country.csv' AS row
MERGE (co:Country {countryID: row.countryId})
SET co.name = row.label_en,
    co.iso2 = row.iso2_code,
    co.iso3 = row.iso3_code,
    co.blackList = row.blackList,
    co.greyList = row.greyList;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Email.csv' AS row
MERGE (e:Email {emailID: row.emailID})
SET e.address = row.emailAddress;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_PhoneNumber.csv' AS row
MERGE (p:PhoneNumber {phoneID: row.phoneNumberID})
SET p.number = row.number;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_AlertStatus.csv' AS row
MERGE (s:AlertStatus {statusId: row.alertId})
SET s.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Alert.csv' AS row
MERGE (al:Alert {alertId: row.alertId});

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Scenario.csv' AS row
MERGE (sc:Scenario {name: row.name})
SET sc.listAlertsQuery = row.listAlertsQuery,
    sc.alertDetailQuery = row.alertDetailQuery,
    sc.creationDate = row.creationDate,
    sc.applicationDate = row.applicationDate,
    sc.frequency = row.frequency;

// ---------- Relationships ----------

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer_HAS_ACCOUNT_Account.csv' AS row
MATCH (c:Customer {customerID: row.start_Customer_customerID})
MATCH (a:Account {accountID: row.end_Account_accountID})
MERGE (c)-[:HAS_ACCOUNT]->(a);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer_RESIDES_AT_Address.csv' AS row
MATCH (c:Customer {customerID: row.start_Customer_customerID})
MATCH (ad:Address {addressID: row.end_Address_addressID})
MERGE (c)-[:RESIDES_AT]->(ad);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Address_LOCATED_IN_Jurisdiction.csv' AS row
MATCH (ad:Address {addressID: row.start_Address_addressID})
MATCH (j:Jurisdiction {jurisdictionID: row.end_Jurisdiction_jurisdictionID})
MERGE (ad)-[:LOCATED_IN]->(j);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Jurisdiction_ASSOCIATED_WITH_Country.csv' AS row
MATCH (j:Jurisdiction {jurisdictionID: row.start_Jurisdiction_jurisdictionID})
MATCH (co:Country {countryID: row.end_Country_countryId})
MERGE (j)-[:ASSOCIATED_WITH]->(co);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer_USES_EMAIL_Email.csv' AS row
MATCH (c:Customer {customerID: row.start_Customer_customerID})
MATCH (e:Email {emailID: row.end_Email_emailID})
MERGE (c)-[:USES_EMAIL]->(e);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer_USES_PHONE_PhoneNumber.csv' AS row
MATCH (c:Customer {customerID: row.start_Customer_customerID})
MATCH (p:PhoneNumber {phoneID: row.end_PhoneNumber_phoneID})
MERGE (c)-[:USES_PHONE]->(p);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Customer_SHARED_IDENTIFIERS_Customer.csv' AS row
MATCH (c1:Customer {customerID: row.start_Customer_customerID})
MATCH (c2:Customer {customerID: row.end_Customer_customerID})
MERGE (c1)-[:SHARED_IDENTIFIERS]->(c2);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Account_SENT_Transaction.csv' AS row
MATCH (a:Account {accountID: row.start_Account_accountID})
MATCH (t:Transaction {transactionID: row.end_Transaction_transactionID})
MERGE (a)-[:SENT]->(t);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Transaction_RECEIVED_Account.csv' AS row
MATCH (t:Transaction {transactionID: row.start_Transaction_transactionID})
MATCH (a:Account {accountID: row.end_Account_accountID})
MERGE (t)-[:RECEIVED]->(a);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Account_TRANSACTED_TO_Account.csv' AS row
MATCH (a1:Account {accountID: row.start_Account_accountID})
MATCH (a2:Account {accountID: row.end_Account_accountID})
MERGE (a1)-[r:TRANSACTED_TO]->(a2)
SET r.totalAmount = toFloat(row.totalAmount),
    r.minAmount = toFloat(row.minAmount),
    r.averageAmount = toFloat(row.averageAmount),
    r.maxAmount = toFloat(row.maxAmount),
    r.transactionCount = toInteger(row.transactionCount);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Alert_HAS_STATUS_AlertStatus.csv' AS row
MATCH (al:Alert {alertId: row.start_Alert_alertId})
MATCH (s:AlertStatus {statusId: row.end_AlertStatus_alertId})
MERGE (al)-[:HAS_STATUS]->(s);

LOAD CSV WITH HEADERS FROM 'file:///export_transactions_Scenario_HAS_ALERT_Alert.csv' AS row
MATCH (sc:Scenario {name: row.start_Scenario_name})
MATCH (al:Alert {alertId: row.end_Alert_alertId})
MERGE (sc)-[:HAS_ALERT]->(al);

// ---------- Post-processing (from src/cypher/Importer_Post_Processing.cypher) ----------
MATCH (a:Account) SET a:$(a.internalExternal);
MATCH (a:Account) WHERE a.highRiskJurisdiction = true SET a:HighRiskJurisdiction;
