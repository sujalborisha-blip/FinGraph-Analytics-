import time
import json
import os

def send_alert(transaction, reason):
    """Simulate sending an Email/Slack alert for high-risk fraud"""
    print(f"\n[ALERT TRIGGERED] 🔴 HIGH RISK SYNDICATE DETECTED!", flush=True)
    print(f"Reason: {reason}", flush=True)
    print(f"Transaction ID: {transaction.get('transaction_id')}", flush=True)
    print(f"Amount: ${transaction.get('amount')}", flush=True)
    print(f"Sending automated Slack notification to AML Investigation Team...\n", flush=True)

def run_rules_engine():
    print("--- FinGraph Automation Rules & Alerting Engine ---")
    log_file = "transactions.log"
    
    if not os.path.exists(log_file):
        print("Error: transactions.log not found.")
        return

    print("Monitoring transactions for high-risk patterns in real-time...\n")
    
    try:
        with open(log_file, 'r') as f:
            # Go to end of file to read only new real-time logs
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    tx = json.loads(line)
                    tx_type = tx.get("type", "")
                    amount = float(tx.get("amount", 0))
                    
                    # Rule 1: Layering Pattern Detected
                    if tx_type == "FRAUD_LAYERING":
                        send_alert(tx, "Layering Pattern (Multi-hop offshore transfer)")
                        
                    # Rule 2: Unusually large transaction near reporting limits
                    elif amount > 9000 and tx_type != "NORMAL":
                        send_alert(tx, "High-value suspicious transfer nearing $10k limit")
                        
                except Exception as e:
                    print(f"Debug Error: {e} on line: {line}", flush=True)
                    pass
                    
    except KeyboardInterrupt:
        print("\nRules Engine stopped.", flush=True)

if __name__ == "__main__":
    run_rules_engine()
