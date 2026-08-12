CREATE (p:Person {person_id: "P1", name: "Test User"})
   CREATE (a:Account {account_id: "A1", account_type: "savings", balance: 1000})
   CREATE (b:Bank {bank_id: "B1", bank_name: "Test Bank", country: "IN"})
   CREATE (p)-[:OWNS]->(a)
   CREATE (a)-[:BELONGS_TO]->(b);

   CREATE (a2:Account {account_id: "A2", account_type: "savings", balance: 500})
   CREATE (b2:Bank {bank_id: "B2", bank_name: "Second Bank", country: "IN"})
   CREATE (a2)-[:BELONGS_TO]->(b2)
   WITH a2
   MATCH (a1:Account {account_id: "A1"})
   CREATE (a1)-[:TRANSFERRED_TO {amount: 200, timestamp: datetime(), currency: "INR"}]->(a2);