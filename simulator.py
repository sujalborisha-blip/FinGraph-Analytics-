import json
import time
import random
from faker import Faker
from datetime import datetime

# Initialize Faker to generate realistic fake data
fake = Faker()

def generate_account():
    """Generate a fake bank account"""
    return {
        "account_id": fake.bban(),
        "owner_name": fake.name(),
        "bank_name": random.choice(["Chase", "Bank of America", "Wells Fargo", "CitiBank", "HSBC"]),
        "country": "USA"
    }

def generate_transaction(sender, receiver):
    """Generate a fake transaction between two accounts"""
    return {
        "transaction_id": fake.uuid4(),
        "timestamp": datetime.now().isoformat(),
        "sender_account": sender["account_id"],
        "receiver_account": receiver["account_id"],
        "amount": round(random.uniform(10.0, 5000.0), 2), # Random amount between $10 and $5000
        "currency": "USD"
    }

def main():
    print("🚀 Starting FinGraph Data Simulator...")
    print("Generating 100 fake accounts...\n")
    
    # Pre-generate 100 random accounts
    accounts = [generate_account() for _ in range(100)]
    
    try:
        print("Streaming transactions (Press Ctrl+C to stop)...\n")
        while True:
            # Pick a random sender and receiver
            sender = random.choice(accounts)
            receiver = random.choice(accounts)
            
            # Ensure sender is not sending to themselves
            if sender != receiver:
                tx = generate_transaction(sender, receiver)
                # In Week 2, we will send this to Kafka. For now, print to console.
                print(json.dumps(tx))
                
            time.sleep(1) # Wait 1 second before the next transaction
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")

if __name__ == "__main__":
    main()
