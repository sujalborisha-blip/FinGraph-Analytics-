import time
import json
import os
import random

# Mock Kafka Producer
class MockKafkaProducer:
    def __init__(self, bootstrap_servers):
        print(f"Connected to Mock Kafka Cluster at {bootstrap_servers}")
        
    def send(self, topic, value):
        time.sleep(random.uniform(0.1, 0.5))
        data = json.loads(value.decode('utf-8'))
        
        fraud_alert = " FRAUD!" if "FRAUD" in data.get('type', '') else ""
        
        print(f"[{time.strftime('%H:%M:%S')}] STREAMED TO '{topic}': ${data.get('amount')} from {data.get('source_account')} to {data.get('dest_account')} (Type: {data.get('type')}){fraud_alert}")
        return self

    def flush(self):
        print("All messages flushed to Kafka.")

def stream_data():
    print("--- FinGraph Real-Time Kafka Streaming Engine (DAEMON MODE) ---")
    
    log_file = "transactions.log"
    if not os.path.exists(log_file):
        print(f"Error: {log_file} not found. Run simulator.py first.")
        return
        
    producer = MockKafkaProducer(bootstrap_servers='localhost:9092')
    kafka_topic = "fingraph_transactions_stream"
    
    print(f"Starting UNBREAKABLE stream from {log_file} to '{kafka_topic}'...")
    print("Waiting for new transactions... (Press Ctrl+C to stop)\n")
    
    try:
        with open(log_file, 'r') as f:
            # Go to the end of the file to only stream NEW transactions
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5) # Wait briefly for new data to be written by simulator
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                message_bytes = line.encode('utf-8')
                producer.send(kafka_topic, value=message_bytes)
                
    except KeyboardInterrupt:
        print("\nFlushing remaining messages in queue...")
        producer.flush()
        print("Streaming stopped by user.")

if __name__ == "__main__":
    stream_data()
