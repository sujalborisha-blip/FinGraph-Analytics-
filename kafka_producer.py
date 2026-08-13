import time
import json
import os
import random

# We simulate a Kafka Producer so it works even if Kafka is not installed locally
class MockKafkaProducer:
    def __init__(self, bootstrap_servers):
        print(f"🔌 Connected to Mock Kafka Cluster at {bootstrap_servers}")
        
    def send(self, topic, value):
        # Simulate network latency for real-time streaming effect
        time.sleep(random.uniform(0.1, 0.5))
        
        # Parse the JSON back to a dict for pretty printing
        data = json.loads(value.decode('utf-8'))
        
        # Add visual alerts for Fraud
        fraud_alert = " 🚨 FRAUD!" if "FRAUD" in data.get('type', '') else ""
        
        print(f"[{time.strftime('%H:%M:%S')}] 🚀 STREAMED TO '{topic}': ${data.get('amount')} from {data.get('source_account')} to {data.get('dest_account')} (Type: {data.get('type')}){fraud_alert}")
        return self

    def flush(self):
        print("✅ All messages flushed to Kafka.")

def stream_data():
    print("==================================================")
    print("📡 FinGraph Real-Time Kafka Streaming Engine")
    print("==================================================")
    
    log_file = "transactions.log"
    if not os.path.exists(log_file):
        print(f"❌ Error: {log_file} not found. Run simulator.py first.")
        return
        
    # Initialize our Producer (Connecting to localhost default Kafka port)
    producer = MockKafkaProducer(bootstrap_servers='localhost:9092')
    kafka_topic = "fingraph_transactions_stream"
    
    print(f"▶️ Starting stream from {log_file} to Kafka topic '{kafka_topic}'...\n")
    
    count = 0
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # In a real scenario, we send raw bytes to Kafka
                message_bytes = line.encode('utf-8')
                
                # Send to Kafka
                producer.send(kafka_topic, value=message_bytes)
                count += 1
                
                # Stop after 25 messages just for the demo 
                if count >= 25:
                    break
                    
        print("\n⏳ Flushing remaining messages in queue...")
        producer.flush()
        print(f"🎉 Successfully streamed {count} transactions to Apache Kafka!")
        
    except KeyboardInterrupt:
        print("\n🛑 Streaming stopped by user.")

if __name__ == "__main__":
    stream_data()
