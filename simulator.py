import json
import time
import random
import os
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
ACCOUNTS_FILE = "accounts.json"
LOG_FILE = "transactions.log"

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

def load_or_generate_accounts():
    """Load existing accounts from file or generate new ones if file doesn't exist"""
    if os.path.exists(ACCOUNTS_FILE):
        print(f"📦 Loading existing accounts from {ACCOUNTS_FILE}...")
        with open(ACCOUNTS_FILE, 'r') as f:
            data = json.load(f)
            return data["normal_accounts"], data["offshore_account"], data["smurfs"]
    
    print("🆕 Generating new accounts and saving to file...")
    normal_accounts = [generate_account() for _ in range(100)]
    offshore_account = generate_account(is_offshore=True)
    smurfs = random.sample(normal_accounts, 20)
    
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump({
            "normal_accounts": normal_accounts,
            "offshore_account": offshore_account,
            "smurfs": smurfs
        }, f, indent=4)
        
    return normal_accounts, offshore_account, smurfs

def main():
    print("🚀 Starting FinGraph Data Simulator v4 (With Data Persistence)...\n")
    
    # Initialize Kafka Producer if available
    producer = None
    if KAFKA_AVAILABLE:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_block_ms=2000 # Added 2-second timeout so it doesn't hang
            )
            print("✅ Successfully connected to Kafka on localhost:9092")
        except Exception as e:
            print(f"⚠️ Could not connect to Kafka broker. Running in Console-Only mode.")
            producer = None

    # Load or generate our network of accounts
    normal_accounts, offshore_account, smurfs = load_or_generate_accounts()
    
    try:
        print(f"Streaming transactions... Logs will be saved to {LOG_FILE} (Press Ctrl+C to stop)\n")
        with open(LOG_FILE, 'a') as log_file:
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
                        
                        log_file.write(json.dumps(tx) + "\n")
                        print(json.dumps(tx))
                else:
                    sender = random.choice(smurfs)
                    tx = generate_transaction(sender, offshore_account, amount=9900.00)
                    tx["type"] = "FRAUD_SMURFING"
                    if producer:
                        producer.send('bank_transactions', value=tx)
                    
                    log_file.write(json.dumps(tx) + "\n")
                    print(f"[🚨 SUSPICIOUS] {json.dumps(tx)}")
                    
                # Flush the file buffer so we don't lose data if script is stopped
                log_file.flush()
                time.sleep(1) # Wait 1 second
            
    except KeyboardInterrupt:
        if producer:
            producer.close()
        print("\n🛑 Simulator stopped.")

if __name__ == "__main__":
    main()
