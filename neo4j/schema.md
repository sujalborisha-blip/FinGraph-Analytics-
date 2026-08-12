# FinGraph Neo4j Schema

## Nodes

### Person
- person_id (unique) — identifier for the person
- name — person's full name

### Account
- account_id (unique) — identifier for the account
- account_type — e.g. savings, current
- balance — current account balance

### Bank
- bank_id (unique) — identifier for the bank
- bank_name — name of the bank
- country — country the bank operates in

## Relationships

- (Person)-[:OWNS]->(Account)
  A person owns one or more accounts.

- (Account)-[:BELONGS_TO]->(Bank)
  An account belongs to a specific bank.

- (Account)-[:TRANSFERRED_TO {amount, timestamp, currency}]->(Account)
  Represents a money transfer from one account to another.
  Properties store the transaction amount, when it happened, and currency used.

## Why this design

This structure separates people, their accounts, and the banks those accounts
belong to, so we can trace money movement independently of who owns the
account. The TRANSFERRED_TO relationship is the core of fraud detection —
it lets us query chains of transactions (e.g. A → B → C → A) to detect
circular money flows, a common laundering pattern.

Constraints on person_id, account_id, and bank_id ensure no duplicate nodes
are created as data streams in from the simulator.