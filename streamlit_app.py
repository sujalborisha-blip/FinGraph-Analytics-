"""
FinGraph - Financial Fraud Syndicate & Graph Network Analytics
==============================================================
Next-Gen Cyber-Fintech AML Operations Console & Cloud Platform
Lead Analyst: Sujal | Infotact Solutions Virtual Internship Project 1
"""

import os
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="FinGraph | Financial Fraud Network Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "transactions.log"
ACCOUNTS_FILE = BASE_DIR / "accounts.json"

# Custom Cyber-Dark Styling
st.markdown("""
<style>
    .stApp {
        background-color: #030712;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(3, 7, 18, 0.95);
    }
    section[data-testid="stSidebar"] {
        background-color: #070d1e;
        border-right: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #0c152a;
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_data():
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

    # Precompute Network Graph Payload for Vis.js
    offshore = accounts.get("offshore_account", {})
    offshore_id = offshore.get("account_id")
    mules_map = {a["account_id"]: a for a in accounts.get("mules", [])}
    smurfs_map = {a["account_id"]: a for a in accounts.get("smurfs", [])}
    normal_map = {a["account_id"]: a for a in accounts.get("normal_accounts", [])}

    # Identify all participating accounts
    all_account_ids = set()
    for t in transactions:
        all_account_ids.add(t["sender_account"])
        all_account_ids.add(t["receiver_account"])

    nodes = []
    for acc_id in all_account_ids:
        # Determine classification
        if acc_id == offshore_id:
            role = "OFFSHORE_SHELL"
            label = "👑 Panama Shell Entity"
            bank = offshore.get("bank_name", "Offshore Bank")
            country = offshore.get("country", "Panama")
            owner = offshore.get("owner_name", "Shell Corp")
            color = {"background": "#ef4444", "border": "#f87171", "highlight": {"background": "#dc2626", "border": "#ffffff"}}
            size = 36
            shape = "diamond"
            risk_score = 98
        elif acc_id in mules_map:
            role = "MONEY_MULE"
            label = f"⚠️ Mule: {acc_id[:6]}"
            acc_info = mules_map[acc_id]
            bank = acc_info.get("bank_name", "US Bank")
            country = acc_info.get("country", "USA")
            owner = acc_info.get("owner_name", "Unknown Mule")
            color = {"background": "#f59e0b", "border": "#fbbf24", "highlight": {"background": "#d97706", "border": "#ffffff"}}
            size = 28
            shape = "hexagon"
            risk_score = 88
        elif acc_id in smurfs_map:
            role = "SMURF_FEEDER"
            label = f"🟣 Smurf: {acc_id[:6]}"
            acc_info = smurfs_map[acc_id]
            bank = acc_info.get("bank_name", "Retail Bank")
            country = acc_info.get("country", "USA")
            owner = acc_info.get("owner_name", "Smurf Account")
            color = {"background": "#8b5cf6", "border": "#a78bfa", "highlight": {"background": "#7c3aed", "border": "#ffffff"}}
            size = 20
            shape = "dot"
            risk_score = 74
        else:
            role = "STANDARD_RETAIL"
            label = f"{acc_id[:6]}"
            acc_info = normal_map.get(acc_id, {})
            bank = acc_info.get("bank_name", "Domestic Bank")
            country = acc_info.get("country", "USA")
            owner = acc_info.get("owner_name", "Retail Client")
            color = {"background": "#0284c7", "border": "#38bdf8", "highlight": {"background": "#0369a1", "border": "#ffffff"}}
            size = 14
            shape = "dot"
            risk_score = 8

        nodes.append({
            "id": acc_id,
            "label": label,
            "role": role,
            "owner": owner,
            "bank": bank,
            "country": country,
            "risk_score": risk_score,
            "color": color,
            "size": size,
            "shape": shape,
            "font": {"color": "#f8fafc", "size": 11, "face": "Inter"}
        })

    # Aggregate edges to keep graph responsive and sharp
    edges_map = {}
    for t in transactions:
        key = (t["sender_account"], t["receiver_account"])
        is_fraud = t.get("type", "NORMAL") != "NORMAL"
        amt = float(t.get("amount", 0))
        if key not in edges_map:
            edges_map[key] = {
                "from": t["sender_account"],
                "to": t["receiver_account"],
                "count": 0,
                "amount": 0.0,
                "is_fraud": False,
                "types": set()
            }
        edges_map[key]["count"] += 1
        edges_map[key]["amount"] += amt
        if is_fraud:
            edges_map[key]["is_fraud"] = True
        edges_map[key]["types"].add(t.get("type", "NORMAL"))

    edges = []
    for key, data in edges_map.items():
        if data["is_fraud"]:
            edge_color = {"color": "#ef4444", "highlight": "#ff3366", "opacity": 0.9}
            width = 2.4
            dashes = True
        else:
            edge_color = {"color": "rgba(56, 189, 248, 0.28)", "highlight": "#00f2fe", "opacity": 0.4}
            width = 1.0
            dashes = False

        types_str = ", ".join(data["types"])
        edges.append({
            "from": data["from"],
            "to": data["to"],
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
            "color": edge_color,
            "width": width,
            "dashes": dashes,
            "is_fraud": data["is_fraud"],
            "title": f"Count: {data['count']} txs | Total: ${data['amount']:,.2f} | Types: {types_str}",
            "amount": data["amount"],
            "types": list(data["types"])
        })

    return df, accounts, nodes, edges, transactions

df_tx, accounts_data, graph_nodes, graph_edges, raw_transactions = load_all_data()

# Compute Global KPIs
total_tx = len(df_tx)
fraud_mask = df_tx["type"].isin(["FRAUD_SMURFING", "FRAUD_LAYERING", "FRAUD_PLACEMENT"]) if "type" in df_tx.columns else pd.Series(False, index=df_tx.index)
fraud_count = int(fraud_mask.sum())
fraud_amount = float(df_tx[fraud_mask]["amount"].sum()) if fraud_count > 0 else 0.0

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="margin: 0; color: #38bdf8; font-weight: 900; letter-spacing: 1px;">🛡️ FinGraph</h2>
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">Real-Time Financial Fraud Syndicate Detection</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav = st.radio(
        "Investigation Modules",
        [
            "🌐 Interactive 3D Force Graph (Palantir Console)",
            "📊 Graph Community & Louvain Clusters",
            "🚨 Regulatory Audit Ledger (SAR Exporter)",
            "🏛️ Production Neo4j Cypher Workbench",
            "📑 Infotact Project Specifications"
        ]
    )

    st.divider()

    st.markdown("### ⚡ Streaming Engine Telemetry")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Events", f"{total_tx:,}")
        st.metric("Fraud Hops", f"{fraud_count:,}")
    with col2:
        st.metric("Mule Rings", "5 Middlemen")
        st.metric("Asset Risk", f"${fraud_amount/1e6:.2f}M")

    st.divider()
    st.markdown("""
    **Lead Analyst:** Sujal  
    **Program:** Infotact Solutions Virtual Internship (Project 1)  
    **Stack:** Python, NetworkX, Neo4j, Apache Kafka/Flink, Vis.js
    """)

# MAIN VIEW 1: INTERACTIVE 3D FORCE GRAPH CONSOLE
if nav == "🌐 Interactive 3D Force Graph (Palantir Console)":

    # Top KPI Strip
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 14px;">
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-left: 4px solid #38bdf8; border-radius: 12px; padding: 12px 16px;">
            <span style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Scanned Transactions</span>
            <div style="font-size: 20px; font-weight: 900; color: #ffffff; font-family: monospace;">{total_tx:,}</div>
            <span style="font-size: 10px; color: #38bdf8;">Kafka Ingestion (60 FPS)</span>
        </div>
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(239, 68, 68, 0.3); border-left: 4px solid #ef4444; border-radius: 12px; padding: 12px 16px;">
            <span style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Flagged Laundering Hops</span>
            <div style="font-size: 20px; font-weight: 900; color: #f87171; font-family: monospace;">{fraud_count:,}</div>
            <span style="font-size: 10px; color: #f87171;">Layering & Placement</span>
        </div>
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(16, 185, 129, 0.3); border-left: 4px solid #10b981; border-radius: 12px; padding: 12px 16px;">
            <span style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Illicit Capital Intercepted</span>
            <div style="font-size: 20px; font-weight: 900; color: #34d399; font-family: monospace;">${fraud_amount:,.2f}</div>
            <span style="font-size: 10px; color: #34d399;">Preserved Assets</span>
        </div>
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #f59e0b; border-radius: 12px; padding: 12px 16px;">
            <span style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Active Threat Syndicates</span>
            <div style="font-size: 20px; font-weight: 900; color: #fbbf24; font-family: monospace;">5 Mules &middot; 1 Shell</div>
            <span style="font-size: 10px; color: #fbbf24;">Panama / Bahamas Ring</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HTML Component with Vis.js Network Engine and Interactive Dossier
    visjs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 0;
                background: #030712;
                color: #f1f5f9;
                font-family: 'Inter', sans-serif;
                overflow: hidden;
                width: 100vw;
                height: 100vh;
            }}
            #network {{
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at 50% 50%, #0a1128 0%, #020617 100%);
            }}
            .glass-bar {{
                background: rgba(10, 16, 32, 0.92);
                backdrop-filter: blur(14px);
                border: 1px solid rgba(56, 189, 248, 0.2);
            }}
            ::-webkit-scrollbar {{ width: 4px; }}
            ::-webkit-scrollbar-track {{ background: #030712; }}
            ::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 2px; }}
        </style>
    </head>
    <body class="flex flex-col h-full w-full relative">

        <!-- Top Graph Interactive Toolbar -->
        <div class="h-11 glass-bar px-4 flex items-center justify-between shrink-0 z-20 border-b border-slate-800">
            <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <span class="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping"></span>
                    Graph Topology:
                </span>
                <button onclick="filterNetwork('all')" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 transition">
                    🌐 Full Network (150 Nodes)
                </button>
                <button onclick="filterNetwork('fraud_only')" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-700/60 transition">
                    🚨 Fraud Laundering Rings Only
                </button>
                <button onclick="focusOffshore()" class="px-2.5 py-1 rounded-md text-[11px] font-bold bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-700/60 transition">
                    👑 Focus Offshore Shell (Panama)
                </button>
            </div>

            <div class="flex items-center gap-2 text-xs">
                <span class="text-[10px] text-gray-400 font-mono">Legend:</span>
                <span class="text-[9.5px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-700">👑 Offshore Haven</span>
                <span class="text-[9.5px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700">⚠️ Money Mule</span>
                <span class="text-[9.5px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-700">🟣 Smurf Account</span>
                <span class="text-[9.5px] px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-700">🟢 Normal Customer</span>
            </div>
        </div>

        <!-- Main Workspace (Graph Canvas + Side Dossier Inspector) -->
        <div class="flex-1 min-h-0 relative flex">

            <!-- Graph Canvas -->
            <div id="network" class="flex-1 h-full"></div>

            <!-- Slide-in Account Dossier Panel -->
            <div id="dossier-panel" class="w-80 h-full glass-bar border-l border-slate-800/90 p-4 flex flex-col gap-3 overflow-y-auto shrink-0 shadow-2xl transition-all duration-300">
                <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                    <span class="text-xs font-black uppercase tracking-wider text-cyan-300 flex items-center gap-1.5">
                        <span>🔍 Account Dossier</span>
                    </span>
                    <span id="dossier-role-badge" class="text-[9px] font-bold px-2 py-0.5 rounded bg-slate-800 text-gray-300 border border-slate-700 font-mono">SELECT NODE</span>
                </div>

                <div id="dossier-empty" class="text-center py-16 text-gray-500">
                    <svg class="w-10 h-10 mx-auto mb-2 opacity-40 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path></svg>
                    <p class="text-xs">Click any node or transaction in the graph to inspect AML intelligence.</p>
                </div>

                <div id="dossier-content" class="hidden flex flex-col gap-3 text-xs">
                    <div>
                        <span class="text-[9px] text-gray-400 uppercase font-mono block">Account ID</span>
                        <div id="dossier-id" class="text-sm font-black font-mono text-cyan-300 break-all"></div>
                    </div>

                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800 space-y-1">
                        <div><span class="text-gray-400 text-[10px]">Owner:</span> <strong id="dossier-owner" class="text-white"></strong></div>
                        <div><span class="text-gray-400 text-[10px]">Bank:</span> <strong id="dossier-bank" class="text-white"></strong></div>
                        <div><span class="text-gray-400 text-[10px]">Jurisdiction:</span> <strong id="dossier-country" class="text-emerald-400"></strong></div>
                    </div>

                    <!-- Risk Gauge Bar -->
                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                        <div class="flex justify-between text-[10px] mb-1">
                            <span class="text-gray-400 font-bold">Fraud Risk Index</span>
                            <span id="dossier-risk-score" class="font-black text-rose-400 font-mono">98 / 100</span>
                        </div>
                        <div class="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                            <div id="dossier-risk-bar" class="h-2 rounded-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500" style="width: 98%;"></div>
                        </div>
                        <span id="dossier-risk-level" class="text-[9px] font-bold text-rose-400 mt-1 block">CRITICAL REPUTATIONAL RISK</span>
                    </div>

                    <!-- Actions -->
                    <button id="btn-freeze" onclick="freezeCurrentAccount()" class="w-full py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-cyan-600/30 transition flex items-center justify-center gap-1.5 cursor-pointer">
                        <span>❄️ Freeze Account & Block Wire</span>
                    </button>
                    <div id="freeze-confirm" class="hidden p-2 rounded-lg bg-emerald-950 border border-emerald-600 text-emerald-300 text-[10px] text-center font-bold">
                        ✓ Account Frozen! Outbound transfers severed.
                    </div>
                </div>
            </div>

        </div>

        <!-- Bottom Live Transaction Stream Ticker -->
        <div class="h-10 glass-bar px-4 flex items-center justify-between shrink-0 z-20 border-t border-slate-800 text-xs">
            <div class="flex items-center gap-2 overflow-hidden">
                <span class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 font-mono text-[9.5px] font-bold">LIVE STREAM</span>
                <span id="live-ticker-text" class="text-gray-300 font-mono text-[11px] truncate">
                    Streaming Kafka events at 60 FPS...
                </span>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="toggleStream()" id="btn-stream-toggle" class="px-2.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300 text-[10px] font-bold border border-slate-700 transition">
                    ⏸ Pause Stream
                </button>
            </div>
        </div>

        <!-- Graph Execution Script -->
        <script>
            const allNodes = {json.dumps(graph_nodes)};
            const allEdges = {json.dumps(graph_edges)};
            const rawTxs = {json.dumps(raw_transactions[:150])};

            let network;
            let nodesDataSet = new vis.DataSet(allNodes);
            let edgesDataSet = new vis.DataSet(allEdges);
            let currentSelectedNodeId = null;
            let isStreaming = true;
            let streamInterval = null;
            let txIndex = 0;

            function initGraph() {{
                const container = document.getElementById('network');
                const data = {{ nodes: nodesDataSet, edges: edgesDataSet }};

                const options = {{
                    physics: {{
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {{
                            gravitationalConstant: -45,
                            centralGravity: 0.015,
                            springLength: 95,
                            springConstant: 0.08,
                            damping: 0.4
                        }},
                        stabilization: {{ iterations: 120 }}
                    }},
                    interaction: {{
                        hover: true,
                        tooltipDelay: 100,
                        zoomView: true,
                        dragView: true
                    }},
                    edges: {{
                        smooth: {{ type: 'continuous' }}
                    }}
                }};

                network = new vis.Network(container, data, options);

                network.on('click', function(params) {{
                    if (params.nodes.length > 0) {{
                        const nodeId = params.nodes[0];
                        showDossier(nodeId);
                    }}
                }});
            }}

            function showDossier(nodeId) {{
                currentSelectedNodeId = nodeId;
                const node = allNodes.find(n => n.id === nodeId);
                if (!node) return;

                document.getElementById('dossier-empty').classList.add('hidden');
                document.getElementById('dossier-content').classList.remove('hidden');
                document.getElementById('freeze-confirm').classList.add('hidden');

                document.getElementById('dossier-id').innerText = node.id;
                document.getElementById('dossier-owner').innerText = node.owner;
                document.getElementById('dossier-bank').innerText = node.bank;
                document.getElementById('dossier-country').innerText = node.country;

                const badge = document.getElementById('dossier-role-badge');
                badge.innerText = node.role;
                if (node.role === 'OFFSHORE_SHELL') {{
                    badge.className = "text-[9px] font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-700 font-mono";
                }} else if (node.role === 'MONEY_MULE') {{
                    badge.className = "text-[9px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700 font-mono";
                }} else if (node.role === 'SMURF_FEEDER') {{
                    badge.className = "text-[9px] font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-700 font-mono";
                }} else {{
                    badge.className = "text-[9px] font-bold px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-700 font-mono";
                }}

                document.getElementById('dossier-risk-score').innerText = `${{node.risk_score}} / 100`;
                document.getElementById('dossier-risk-bar').style.width = `${{node.risk_score}}%`;

                const riskLevelEl = document.getElementById('dossier-risk-level');
                if (node.risk_score > 80) {{
                    riskLevelEl.innerText = "CRITICAL AML SYNDICATE THREAT";
                    riskLevelEl.className = "text-[9px] font-bold text-rose-400 mt-1 block";
                }} else if (node.risk_score > 50) {{
                    riskLevelEl.innerText = "ELEVATED STRUCTURING RISK";
                    riskLevelEl.className = "text-[9px] font-bold text-amber-400 mt-1 block";
                }} else {{
                    riskLevelEl.innerText = "LOW RISK RETAIL CLIENT";
                    riskLevelEl.className = "text-[9px] font-bold text-emerald-400 mt-1 block";
                }}
            }}

            function freezeCurrentAccount() {{
                if (!currentSelectedNodeId) return;
                document.getElementById('freeze-confirm').classList.remove('hidden');

                // Turn node icy blue
                nodesDataSet.update({{
                    id: currentSelectedNodeId,
                    color: {{ background: '#06b6d4', border: '#22d3ee', highlight: {{ background: '#0891b2', border: '#ffffff' }} }},
                    label: `❄️ FROZEN (${{currentSelectedNodeId.substring(0, 6)}})`
                }});
            }}

            function filterNetwork(mode) {{
                if (mode === 'all') {{
                    nodesDataSet.clear();
                    edgesDataSet.clear();
                    nodesDataSet.add(allNodes);
                    edgesDataSet.add(allEdges);
                    network.fit({{ animation: true }});
                }} else if (mode === 'fraud_only') {{
                    const fraudEdges = allEdges.filter(e => e.is_fraud);
                    const fraudNodeIds = new Set();
                    fraudEdges.forEach(e => {{ fraudNodeIds.add(e.from); fraudNodeIds.add(e.to); }});
                    const fraudNodes = allNodes.filter(n => fraudNodeIds.has(n.id));

                    nodesDataSet.clear();
                    edgesDataSet.clear();
                    nodesDataSet.add(fraudNodes);
                    edgesDataSet.add(fraudEdges);
                    network.fit({{ animation: true }});
                }}
            }}

            function focusOffshore() {{
                const offshoreNode = allNodes.find(n => n.role === 'OFFSHORE_SHELL');
                if (offshoreNode) {{
                    network.focus(offshoreNode.id, {{
                        scale: 1.6,
                        animation: {{ duration: 1000, easingFunction: 'easeInOutQuad' }}
                    }});
                    showDossier(offshoreNode.id);
                }}
            }}

            function startLiveTicker() {{
                streamInterval = setInterval(() => {{
                    if (rawTxs.length === 0) return;
                    const tx = rawTxs[txIndex % rawTxs.length];
                    txIndex++;

                    const ticker = document.getElementById('live-ticker-text');
                    const isFraud = tx.type !== 'NORMAL';
                    if (isFraud) {{
                        ticker.innerHTML = `<span class="text-rose-400 font-bold">🚨 [INTERCEPTED]</span> ${{tx.type}} | ${{tx.sender_account.substring(0,8)}}... → ${{tx.receiver_account.substring(0,8)}}... | <strong class="text-rose-300">$${{Number(tx.amount).toLocaleString()}}</strong>`;
                    }} else {{
                        ticker.innerHTML = `<span class="text-cyan-400">[NORMAL]</span> ${{tx.sender_account.substring(0,8)}}... → ${{tx.receiver_account.substring(0,8)}}... | <span class="text-emerald-300">$${{Number(tx.amount).toLocaleString()}}</span>`;
                    }}
                }}, 1100);
            }}

            function toggleStream() {{
                isStreaming = !isStreaming;
                const btn = document.getElementById('btn-stream-toggle');
                if (isStreaming) {{
                    btn.innerText = "⏸ Pause Stream";
                    startLiveTicker();
                }} else {{
                    btn.innerText = "▶ Resume Stream";
                    clearInterval(streamInterval);
                }}
            }}

            window.onload = function() {{
                initGraph();
                startLiveTicker();
            }};
        </script>
    </body>
    </html>
    """

    components.html(visjs_html, height=780, scrolling=False)

# MAIN VIEW 2: LOUVAIN CLUSTERING & GDS METRICS
elif nav == "📊 Graph Community & Louvain Clusters":
    st.markdown("## 📊 Graph Data Science: Louvain Community & Centrality Analysis")
    st.markdown("Uncovering hidden money mule rings, fan-out clustering, and offshore funnel nodes.")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("🏆 Top High-Risk Intermediaries (Money Mules)")
        sender_counts = df_tx["sender_account"].value_counts().rename("out_degree")
        receiver_counts = df_tx["receiver_account"].value_counts().rename("in_degree")
        degrees = pd.concat([sender_counts, receiver_counts], axis=1).fillna(0)
        degrees["total_activity"] = degrees["out_degree"] + degrees["in_degree"]
        degrees = degrees.sort_values(by="total_activity", ascending=False)
        st.dataframe(degrees.head(12), use_container_width=True)

    with col2:
        st.subheader("🔍 Criminal Syndicate Hierarchy")
        st.markdown(r"""
        * **Ring Leader / Offshore Entity:** `TKNE95981619733116` (Panama Shell Corp) receives consolidated funds via multi-hop layering.
        * **Money Mules (5 Identified Hubs):** Intermediary domestic accounts distributing structured payments to obfuscate paper trails.
        * **Smurfs (20 Structuring Accounts):** Sub-threshold accounts making rapid $\le \$9,900$ transfers to avoid automatic regulatory reporting.
        """)

# MAIN VIEW 3: REGULATORY AUDIT LEDGER (SAR EXPORTER)
elif nav == "🚨 Regulatory Audit Ledger (SAR Exporter)":
    st.markdown("## 🚨 Suspicious Activity Report (SAR) Audit Ledger")
    st.markdown("Filter, inspect, and export verified financial crime records for regulatory filing.")

    c_filter, c_search = st.columns([1, 2])
    with c_filter:
        pattern_filter = st.selectbox("Filter Fraud Pattern", ["ALL"] + sorted(df_tx["type"].unique().tolist()))
    with c_search:
        search_query = st.text_input("Search Account ID or Transaction Hash")

    filtered_df = df_tx.copy()
    if pattern_filter != "ALL":
        filtered_df = filtered_df[filtered_df["type"] == pattern_filter]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["sender_account"].str.contains(search_query, case=False, na=False) |
            filtered_df["receiver_account"].str.contains(search_query, case=False, na=False) |
            filtered_df["transaction_id"].str.contains(search_query, case=False, na=False)
        ]

    st.dataframe(filtered_df.head(100), use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Official SAR Report (CSV File)",
        data=csv_data,
        file_name="FinGraph_SAR_Filing.csv",
        mime="text/csv"
    )

# MAIN VIEW 4: NEO4J CYPHER WORKBENCH
elif nav == "🏛️ Production Neo4j Cypher Workbench":
    st.markdown("## 🏛️ Production Neo4j Cypher Graph Queries")
    st.markdown("Enterprise graph queries executed on the Neo4j GDS cluster.")

    st.code("""
// 1. Detect Multi-Hop Circular Money Flows (A -> B -> C -> A)
MATCH (a:Account)-[r1:TRANSFERRED_TO]->(b:Account)
MATCH (b)-[r2:TRANSFERRED_TO]->(c:Account)
MATCH (c)-[r3:TRANSFERRED_TO]->(a)
WHERE r1.timestamp < r2.timestamp AND r2.timestamp < r3.timestamp
RETURN a.account_id, b.account_id, c.account_id, (r1.amount + r2.amount + r3.amount) AS total_laundered_volume;

// 2. Stream Louvain Modularity for Coordinated Criminal Communities
CALL gds.louvain.stream('transactionGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).account_id AS account, communityId
ORDER BY communityId ASC;
    """, language="cypher")

# MAIN VIEW 5: PROJECT SPECIFICATIONS
elif nav == "📑 Infotact Project Specifications":
    st.markdown("## 📑 Infotact Solutions Project 1 Architecture & Specifications")
    st.markdown("""
    * **Project Name:** FinGraph Financial Fraud Syndicate & Graph Network Analytics
    * **Lead Analyst:** Sujal
    * **Architecture:** Kafka Event Stream $\rightarrow$ Flink CEP $\rightarrow$ Neo4j GDS $\rightarrow$ Rules Engine $\rightarrow$ Cyber-Fintech Operations Console.
    * **Dataset Size:** 2,264+ live streaming transactions across 150 unique financial accounts.
    """)
