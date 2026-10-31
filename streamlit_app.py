"""
FinGraph - Financial Fraud Syndicate & Graph Network Analytics
==============================================================
Interactive Streamlit Application & Cloud Deployment Platform
Lead Analyst: Sujal | Infotact Solutions Virtual Internship Project 1
"""

import os
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="FinGraph | Financial Fraud Network Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "transactions.log"
ACCOUNTS_FILE = BASE_DIR / "accounts.json"

# Custom Styling
st.markdown("""
<style>
    .stApp {
        background-color: #070b14;
        color: #f1f5f9;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(7, 11, 20, 0.9);
    }
    section[data-testid="stSidebar"] {
        background-color: #0c1222;
        border-right: 1px solid #1e293b;
    }
    .metric-card {
        background: #0f172a;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_transaction_data():
    transactions = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and line.startswith("{"):
                    try:
                        transactions.append(json.loads(line))
                    except Exception:
                        pass
    
    df = pd.DataFrame(transactions)
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    accounts = {}
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            accounts = json.load(f)

    return df, accounts

df_tx, accounts_data = load_transaction_data()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="margin: 0; color: #38bdf8; font-weight: 900; letter-spacing: 1px;">🛡️ FinGraph</h2>
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">Financial Fraud Syndicate & Network Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav = st.radio(
        "Navigation Menu",
        [
            "⚡ Executive Fraud Console",
            "🕸️ Network Graph Topology",
            "🚨 Real-Time Alert Ledger",
            "📊 Syndicate Community Metrics",
            "📑 Neo4j Cypher Schema"
        ]
    )

    st.divider()
    st.markdown("""
    **Lead Analyst:** Sujal  
    **Program:** Infotact Solutions Virtual Internship (Project 1)  
    **Stack:** Python, NetworkX, Neo4j, Apache Kafka/Flink, Streamlit
    """)

# Top Overview KPI Computation
total_tx = len(df_tx)
fraud_mask = df_tx["type"].isin(["FRAUD_SMURFING", "FRAUD_LAYERING", "FRAUD_PLACEMENT"]) if "type" in df_tx.columns else pd.Series(False, index=df_tx.index)
fraud_count = int(fraud_mask.sum())
fraud_amount = float(df_tx[fraud_mask]["amount"].sum()) if fraud_count > 0 else 0.0
clean_count = total_tx - fraud_count

if nav == "⚡ Executive Fraud Console":
    st.markdown("# 🛡️ FinGraph Anti-Money Laundering (AML) Operations Center")
    st.markdown("Automated graph network stream processing identifying coordinated money laundering rings and shell company transfers.")

    # KPI Strip
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Scanned Transactions", f"{total_tx:,}")
    with c2:
        st.metric("Flagged Fraud Transactions", f"{fraud_count:,}", delta=f"{(fraud_count/total_tx*100):.1f}% Risk" if total_tx else "0%")
    with c3:
        st.metric("Intercepted Illicit Capital", f"${fraud_amount:,.2f}")
    with c4:
        st.metric("Offshore Havens Monitored", "4 Jurisdictions")

    st.divider()

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📈 Real-Time Transaction Volume & Fraud Distribution")
        if not df_tx.empty:
            type_counts = df_tx["type"].value_counts()
            st.bar_chart(type_counts)

    with col_right:
        st.subheader("🚨 High-Priority AML Fraud Types")
        st.markdown("""
        * **FRAUD_SMURFING (Structuring):** Multiple micro-deposits deliberately capped under $\$10,000$ to evade mandatory BSA/AML currency reporting.
        * **FRAUD_LAYERING:** Rapid multi-hop transfers through intermediate mule accounts to sever audit trails.
        * **FRAUD_PLACEMENT:** Integration of illicit funds directly from non-verified cash sources into financial institutions.
        """)
        if fraud_count > 0:
            st.error(f"⚠️ CRITICAL ALERT: {fraud_count} suspicious transactions detected requiring immediate regulatory intervention.")
        else:
            st.success("✅ System Status: Active Stream Clean. No anomalies detected.")

elif nav == "🕸️ Network Graph Topology":
    st.markdown("## 🕸️ Financial Transaction Graph Network")
    st.markdown("Directed graph $G=(V, E)$ showing inter-account transactions. Node colors represent risk categories.")

    if not df_tx.empty:
        # Sample for clean rendering
        sample_size = st.slider("Select Transaction Sample Size for Graph", min_value=20, max_value=250, value=75, step=15)
        df_sample = df_tx.head(sample_size)

        G = nx.DiGraph()
        for _, row in df_sample.iterrows():
            sender = row["sender_account"][:8]
            receiver = row["receiver_account"][:8]
            tx_type = row.get("type", "NORMAL")
            amt = row.get("amount", 0)
            G.add_edge(sender, receiver, weight=amt, tx_type=tx_type)

        fig, ax = plt.subplots(figsize=(10, 6), facecolor="#070b14")
        ax.set_facecolor("#070b14")

        pos = nx.spring_layout(G, seed=42, k=0.35)
        edge_colors = ["#ef4444" if G[u][v].get("tx_type") != "NORMAL" else "#3b82f6" for u, v in G.edges()]
        
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#38bdf8", node_size=280, alpha=0.9)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=1.4, alpha=0.75, arrows=True, arrowsize=12)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=7, font_color="#ffffff", font_family="sans-serif")

        ax.axis("off")
        st.pyplot(fig)

        st.caption("🔴 Red Edges = Flagged Fraudulent Transits | 🔵 Blue Edges = Normal Peer-to-Peer Transactions")
    else:
        st.info("No transaction data available.")

elif nav == "🚨 Real-Time Alert Ledger":
    st.markdown("## 🚨 Real-Time Suspicious Transaction Ledger")
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        selected_type = st.selectbox("Filter by Pattern", ["ALL"] + sorted(df_tx["type"].unique().tolist()))
    with col_f2:
        search_acc = st.text_input("Search by Account ID (Sender or Receiver)")

    df_filtered = df_tx.copy()
    if selected_type != "ALL":
        df_filtered = df_filtered[df_filtered["type"] == selected_type]
    if search_acc:
        df_filtered = df_filtered[
            df_filtered["sender_account"].str.contains(search_acc, case=False, na=False) |
            df_filtered["receiver_account"].str.contains(search_acc, case=False, na=False)
        ]

    st.dataframe(df_filtered.head(100), use_container_width=True)

    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Suspicious Activity Report (SAR CSV)",
        data=csv_data,
        file_name="FinGraph_SAR_Report.csv",
        mime="text/csv"
    )

elif nav == "📊 Syndicate Community Metrics":
    st.markdown("## 📊 Graph Community & Centrality Analysis")
    st.markdown("Ranking accounts based on degree centrality (incoming vs. outgoing transactions) and fan-out ratios.")

    if not df_tx.empty:
        sender_counts = df_tx["sender_account"].value_counts().rename("out_degree")
        receiver_counts = df_tx["receiver_account"].value_counts().rename("in_degree")
        degrees = pd.concat([sender_counts, receiver_counts], axis=1).fillna(0)
        degrees["total_activity"] = degrees["out_degree"] + degrees["in_degree"]
        degrees = degrees.sort_values(by="total_activity", ascending=False)

        st.markdown("### Top 15 Highly Active Accounts (Potential Mules / Hubs)")
        st.dataframe(degrees.head(15), use_container_width=True)

elif nav == "📑 Neo4j Cypher Schema":
    st.markdown("## 📑 Production Neo4j Cypher Schema & GDS Queries")
    st.markdown("Pre-configured Cypher scripts executed on the graph engine.")

    st.code("""
// 1. Create Constraints
CREATE CONSTRAINT FOR (p:Person) REQUIRE p.person_id IS UNIQUE;
CREATE CONSTRAINT FOR (a:Account) REQUIRE a.account_id IS UNIQUE;
CREATE CONSTRAINT FOR (b:Bank) REQUIRE b.bank_id IS UNIQUE;

// 2. Identify Circular Layering Rings (A -> B -> C -> A)
MATCH (a:Account)-[r1:TRANSFERRED_TO]->(b:Account)
MATCH (b)-[r2:TRANSFERRED_TO]->(c:Account)
MATCH (c)-[r3:TRANSFERRED_TO]->(a)
WHERE r1.timestamp < r2.timestamp AND r2.timestamp < r3.timestamp
RETURN a.account_id, b.account_id, c.account_id, r1.amount + r2.amount + r3.amount AS total_cycle_volume;

// 3. Louvain Community Detection (Identify Syndicate Clusters)
CALL gds.louvain.stream('transactionGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).account_id AS account, communityId
ORDER BY communityId ASC;
    """, language="cypher")
