import json
import time
import random
from faker import Faker
from datetime import datetime

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("⚠️ 'kafka-python' library not found. Running in Console-Only mode.")

# Initialize Faker to generate realistic fake data
fake = Faker()

def generate_account(is_offshore=False):
    """Generate a fake bank account"""
    return {
        "account_id": fake.bban(),
        "owner_name": fake.company() if is_offshore else fake.name(),
        "bank_name": random.choice(["Chase", "Bank of America", "Wells Fargo", "CitiBank", "HSBC"]),
        "country": "Panama" if is_offshore else "USA"
    }

def generate_transaction(sender, receiver, amount=None):
    """Generate a fake transaction between two accounts"""
    return {
        "transaction_id": fake.uuid4(),
        "timestamp": datetime.now().isoformat(),
        "sender_account": sender["account_id"],
        "receiver_account": receiver["account_id"],
        "amount": amount if amount else round(random.uniform(10.0, 5000.0), 2), 
        "currency": "USD"
    }

def main():
    print("🚀 Starting FinGraph Data Simulator v3 (With Kafka Streaming)...\n")
    
    # Initialize Kafka Producer if available
    producer = None
    if KAFKA_AVAILABLE:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Successfully connected to Kafka on localhost:9092")
        except Exception as e:
            print(f"⚠️ Could not connect to Kafka broker. Running in Console-Only mode.")
            producer = None

    # 1. Create 100 Normal Accounts
    normal_accounts = [generate_account() for _ in range(100)]
    
    # 2. Create 1 Offshore Shell Company (Fraud target)
    offshore_account = generate_account(is_offshore=True)
    
    # 3. Select 20 random accounts to act as 'Smurfs' (people who send illegal money)
    smurfs = random.sample(normal_accounts, 20)
    
    try:
        print("Streaming transactions... (Press Ctrl+C to stop)\n")
        while True:
            # 80% chance of a normal transaction, 20% chance of a fraud transaction
            if random.random() < 0.8:
                sender = random.choice(normal_accounts)
                receiver = random.choice(normal_accounts)
                if sender != receiver:
                    tx = generate_transaction(sender, receiver)
                    tx["type"] = "NORMAL"
                    if producer:
                        producer.send('bank_transactions', value=tx)
                    print(json.dumps(tx))
            else:
                sender = random.choice(smurfs)
                tx = generate_transaction(sender, offshore_account, amount=9900.00)
                tx["type"] = "FRAUD_SMURFING"
                if producer:
                    producer.send('bank_transactions', value=tx)
                print(f"[🚨 SUSPICIOUS] {json.dumps(tx)}")
                
            time.sleep(1) # Wait 1 second
            
    except KeyboardInterrupt:
        if producer:
            producer.close()
        print("\n🛑 Simulator stopped.")

if __name__ == "__main__":
    main()
