import json
import logging
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

# Configure logging to look like a professional big data pipeline
logging.basicConfig(level=logging.INFO, format="%(asctime)s - FLINK_JOB - %(message)s")

def process_transaction(data_string):
    """
    Parses the JSON transaction from Kafka and prepares it for Neo4j Sink.
    """
    try:
        tx = json.loads(data_string)
        
        # Extract only the fields we need for the Graph Database nodes and edges
        graph_node_data = {
            "tx_id": tx.get("transaction_id"),
            "sender": tx.get("sender_account"),
            "receiver": tx.get("receiver_account"),
            "amount": float(tx.get("amount", 0)),
            "is_fraud": "FRAUD" in tx.get("type", "")
        }
        
        if graph_node_data["is_fraud"]:
            logging.warning(f"Flink Intercepted Fraud! Routing to Neo4j Quarantine: {graph_node_data['tx_id']}")
        else:
            logging.info(f"Processed normal transaction for Neo4j: {graph_node_data['tx_id']}")
            
        return json.dumps(graph_node_data)
        
    except Exception as e:
        logging.error(f"Failed to process stream record: {e}")
        return "{}"

def main():
    logging.info("Starting Apache Flink Streaming Job for FinGraph...")
    
    # 1. Initialize Flink Execution Environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1) 
    
    # Note for Vardhini: In Week 4, we will connect FlinkKafkaConsumer and Neo4jSink.
    # For now, we are building the core DataStream processing logic.
    
    mock_kafka_stream = [
        '{"transaction_id": "tx-1001", "sender_account": "ACC1", "receiver_account": "ACC2", "amount": 500, "type": "NORMAL"}',
        '{"transaction_id": "tx-1002", "sender_account": "SMURF1", "receiver_account": "OFFSHORE", "amount": 9900, "type": "FRAUD_LAYERING"}'
    ]
    
    # 2. Create Flink DataStream
    ds = env.from_collection(mock_kafka_stream, type_info=Types.STRING())
    
    # 3. Apply Transformations (Map function)
    processed_stream = ds.map(process_transaction, output_type=Types.STRING())
    
    # 4. Print output (Simulating the Neo4j Sink)
    processed_stream.print()
    
    # 5. Execute the Flink Job
    logging.info("Executing Flink Graph Processing Pipeline...")
    try:
        env.execute("FinGraph_Kafka_To_Neo4j_Job")
    except Exception as e:
        logging.error("PyFlink library is not installed on this machine.")
        logging.info("Please run 'pip install apache-flink' to test locally.")

if __name__ == '__main__':
    main()
