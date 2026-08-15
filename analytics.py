import json
import os

LOG_FILE = "transactions.log"

def main():
    print("FinGraph Data Analytics Engine Started...\n")
    
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} not found. Please run simulator.py first.")
        return
        
    total_tx = 0
    total_fraud_tx = 0
    total_fraud_amount = 0.0
    
    fraud_types = ["FRAUD_SMURFING", "FRAUD_PLACEMENT", "FRAUD_LAYERING"]
    
    print(f"Reading data from {LOG_FILE}...\n")
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            try:
                tx = json.loads(line)
                total_tx += 1
                
                if tx.get("type") in fraud_types:
                    total_fraud_tx += 1
                    total_fraud_amount += float(tx.get("amount", 0.0))
            except json.JSONDecodeError:
                continue 
                
    print("\n--- WEEK 2: SYNDICATE FRAUD ANALYSIS REPORT ---")
    print(f"Total Transactions Processed: {total_tx:,}")
    print(f"Total Fraudulent Transactions: {total_fraud_tx:,}")
    print(f"Total Fraud Money Laundered: ${total_fraud_amount:,.2f}\n")
    
    if total_tx > 0 and total_fraud_tx > 0:
        fraud_percentage = (total_fraud_tx / total_tx) * 100
        print(f"CRITICAL ALERT: {fraud_percentage:.2f}% of all transactions are part of a money laundering syndicate!")
    elif total_tx > 0:
        print("System is currently clean. No fraud detected.")
    else:
        print("No data to analyze.")

if __name__ == "__main__":
    main()
