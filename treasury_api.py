from flask import Flask, jsonify, request, render_template_string
import random
import json
from datetime import datetime

app = Flask(__name__)

# HTML Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Columbus-Ω Treasury</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: #000; 
            color: #fff; 
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; font-size: 28px; color: #0f0; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { 
            padding: 10px 20px; 
            background: #222; 
            border: 1px solid #0f0; 
            color: #0f0;
            cursor: pointer;
            font-family: monospace;
        }
        .tab-btn.active { background: #0f0; color: #000; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .vault-box { 
            background: #111; 
            border: 1px solid #0f0; 
            padding: 15px; 
            margin-bottom: 10px;
        }
        .vault-box h3 { color: #0f0; margin-bottom: 5px; }
        .input-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #0f0; }
        input, textarea { 
            width: 100%; 
            padding: 8px; 
            background: #111; 
            border: 1px solid #0f0; 
            color: #fff;
            font-family: monospace;
        }
        button { 
            padding: 10px 20px; 
            background: #0f0; 
            color: #000;
            border: none;
            cursor: pointer;
            font-weight: bold;
            font-family: monospace;
        }
        button:hover { opacity: 0.8; }
        .receipt { 
            background: #111; 
            border: 1px solid #0f0; 
            padding: 15px; 
            margin-bottom: 10px;
            font-size: 12px;
        }
        .success { color: #0f0; }
        .error { color: #f00; }
        .key-list { 
            max-height: 200px; 
            overflow-y: auto;
            background: #111;
            border: 1px solid #0f0;
            padding: 10px;
        }
        .key-item {
            padding: 8px;
            border-bottom: 1px solid #222;
            cursor: pointer;
        }
        .key-item.selected { background: #0f0; color: #000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ COLUMBUS-Ω TREASURY CONTROL PANEL ⚡</h1>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('dashboard')">Dashboard</button>
            <button class="tab-btn" onclick="switchTab('transaction')">Transaction</button>
            <button class="tab-btn" onclick="switchTab('receipts')">Receipts</button>
        </div>

        <div id="dashboard" class="tab-content active">
            <div class="status-grid">
                <div>
                    <h2 id="totalKeyBalance">Guardian Keys: Loading...</h2>
                    <p id="totalVaultBalance">Vaults: Loading...</p>
                </div>
                <div id="statsBox"></div>
            </div>
            <h2>4-Layer Vault Architecture</h2>
            <div id="vaultsContainer"></div>
            <h2 style="margin-top: 30px;">7 Guardian Keys</h2>
            <div id="keysContainer"></div>
        </div>

        <div id="transaction" class="tab-content">
            <h2>Multi-Key Transaction (3-of-7)</h2>
            <div class="input-group">
                <label>Amount (BTC):</label>
                <input type="number" id="txAmount" step="0.0001" placeholder="0.0041">
            </div>
            <div class="input-group">
                <label>Select Keys (click to toggle):</label>
                <div class="key-list" id="keySelector"></div>
            </div>
            <div class="input-group">
                <button onclick="submitTransaction()">Process Transaction</button>
            </div>
            <div id="txResult"></div>
        </div>

        <div id="receipts" class="tab-content">
            <h2>Transaction Receipts</h2>
            <div id="receiptsList"></div>
        </div>
    </div>

    <script>
        let selectedKeys = [];
        let allKeys = [];

        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            event.target.classList.add('active');
            
            if (tab === 'receipts') loadReceipts();
            if (tab === 'dashboard') loadDashboard();
        }

        async function loadDashboard() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                
                document.getElementById('totalKeyBalance').textContent = 
                    `🔐 Guardian Keys Balance: ${data.total_key_balance.toLocaleString()} BTC`;
                document.getElementById('totalVaultBalance').textContent = 
                    `💾 Total Vault Balance: ${data.total_vault_balance.toLocaleString()} BTC`;
                
                let vaultsHtml = '';
                for (const vault of data.vaults) {
                    vaultsHtml += `
                    <div class="vault-box">
                        <h3>Layer ${vault.level}: ${vault.name}</h3>
                        <p>Balance: ${vault.balance.toLocaleString()} BTC</p>
                        <p>${vault.description}</p>
                    </div>`;
                }
                document.getElementById('vaultsContainer').innerHTML = vaultsHtml;
                
                let keysHtml = '';
                for (const key of data.keys) {
                    keysHtml += `
                    <div class="vault-box">
                        <h3>${key.name}</h3>
                        <p>ID: ${key.identifier}</p>
                        <p>Balance: ${key.balance.toLocaleString()} BTC</p>
                    </div>`;
                }
                document.getElementById('keysContainer').innerHTML = keysHtml;
            } catch (e) {
                console.error(e);
            }
        }

        async function initKeys() {
            try {
                const res = await fetch('/api/keys');
                const data = await res.json();
                allKeys = data.keys;
                
                let html = '';
                for (const key of allKeys) {
                    html += `<div class="key-item" onclick="toggleKey(${key.id}, this)">${key.name}</div>`;
                }
                document.getElementById('keySelector').innerHTML = html;
            } catch (e) {
                console.error(e);
            }
        }

        function toggleKey(id, el) {
            el.classList.toggle('selected');
            if (selectedKeys.includes(id)) {
                selectedKeys = selectedKeys.filter(k => k !== id);
            } else {
                selectedKeys.push(id);
            }
        }

        async function submitTransaction() {
            const amount = parseFloat(document.getElementById('txAmount').value);
            if (!amount || selectedKeys.length < 3) {
                document.getElementById('txResult').innerHTML = 
                    '<p class="error">❌ Enter amount and select at least 3 keys</p>';
                return;
            }

            const keyNames = selectedKeys.map(id => {
                const key = allKeys.find(k => k.id === id);
                return key.name;
            });

            try {
                const res = await fetch('/api/transaction', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount, keys: keyNames })
                });
                
                if (res.ok) {
                    const data = await res.json();
                    const receipt = data.receipt;
                    document.getElementById('txResult').innerHTML = `
                    <div class="receipt success">
                        <strong>✓ TRANSACTION APPROVED</strong><br>
                        TX-ID: ${receipt.tx_id}<br>
                        Amount: ${receipt.amount} BTC<br>
                        Keys: ${receipt.approving_keys.join(', ')}<br>
                        Signature: ${receipt.quantum_signature}<br>
                        Status: ${receipt.status}
                    </div>`;
                    loadReceipts();
                } else {
                    const err = await res.json();
                    document.getElementById('txResult').innerHTML = 
                        `<p class="error">❌ ${err.error}</p>`;
                }
            } catch (e) {
                document.getElementById('txResult').innerHTML = 
                    `<p class="error">❌ Error: ${e.message}</p>`;
            }
        }

        async function loadReceipts() {
            try {
                const res = await fetch('/api/receipts');
                const data = await res.json();
                
                if (data.receipts.length === 0) {
                    document.getElementById('receiptsList').innerHTML = '<p>No receipts yet</p>';
                    return;
                }

                let html = '';
                for (const receipt of data.receipts) {
                    html += `
                    <div class="receipt success">
                        <strong>TX-${receipt.tx_id}</strong><br>
                        Amount: ${receipt.amount} BTC<br>
                        Keys: ${receipt.approving_keys.join(', ')}<br>
                        Signature: ${receipt.quantum_signature}<br>
                        Time: ${new Date(receipt.timestamp).toLocaleString()}
                    </div>`;
                }
                document.getElementById('receiptsList').innerHTML = html;
            } catch (e) {
                console.error(e);
            }
        }

        // Initialize
        initKeys();
        loadDashboard();
    </script>
</body>
</html>
"""

class GuardianKey:
    def __init__(self, name, identifier, balance):
        self.name = name
        self.identifier = identifier
        self.balance = balance

class VaultLayer:
    def __init__(self, name, access_level, description):
        self.name = name
        self.access_level = access_level
        self.description = description
        self.balance = 0.0

class TransactionReceipt:
    def __init__(self, tx_id, amount, approving_keys, status):
        self.tx_id = tx_id
        self.amount = amount
        self.approving_keys = approving_keys
        self.status = status
        self.timestamp = datetime.now().isoformat()
        self.quantum_signature = f"QKS-{random.randint(10000000, 99999999):08d}"

    def to_dict(self):
        return {
            "tx_id": self.tx_id,
            "amount": self.amount,
            "approving_keys": self.approving_keys,
            "status": self.status,
            "timestamp": self.timestamp,
            "quantum_signature": self.quantum_signature
        }

class GuardianTreasury:
    def __init__(self):
        self.keys = [
            GuardianKey("Guardian Key I", "Ω1COL7GUARDIANAX3F4", 3000000),
            GuardianKey("Guardian Key II", "Ω2COL7TREASURYB92KD", 3000000),
            GuardianKey("Guardian Key III", "Ω3COL7NODECORE91LK", 3000000),
            GuardianKey("Guardian Key IV", "Ω4COL7VAULTSEALQ8P", 3000000),
            GuardianKey("Guardian Key V", "Ω5COL7FRAUDLOCKW2Z", 3000000),
            GuardianKey("Guardian Key VI", "Ω6COL7ANTISPAMT9X", 3000000),
            GuardianKey("Guardian Key VII", "Ω7COL7NEXUSCORE7AB", 3000000),
        ]
        
        self.vaults = [
            VaultLayer("Public Monitoring Wallet", 1, "Visible address for transparency - Read-only"),
            VaultLayer("Operational Reserve", 2, "Multi-signature authorization - Active operations"),
            VaultLayer("Deep Reserve Vault", 3, "Long-term security - Restricted access"),
            VaultLayer("Quantum Cold Vault", 4, "Offline cryptographic storage - Emergency only"),
        ]
        
        self.vaults[0].balance = 1000000
        self.vaults[1].balance = 8000000
        self.vaults[2].balance = 12000000
        self.vaults[3].balance = 2000000
        
        self.transaction_log = []
        self.receipts = []

    def process_transaction_multi_key(self, amount, approving_keys):
        if len(approving_keys) < 3:
            return False, "Not enough keys approved (minimum 3-of-7 required)"

        valid_keys = [k.name for k in self.keys]
        for key in approving_keys:
            if key not in valid_keys:
                return False, f"Invalid key '{key}'"

        total_available = 0
        for key_name in approving_keys:
            for k in self.keys:
                if k.name == key_name:
                    total_available += k.balance

        if total_available < amount:
            return False, f"Insufficient combined balance ({total_available} available)"

        remaining = amount
        for key_name in approving_keys:
            for k in self.keys:
                if k.name == key_name and remaining > 0:
                    deduction = min(k.balance, remaining)
                    k.balance -= deduction
                    remaining -= deduction

        tx_id = f"{random.randint(10000000, 99999999):08x}"
        receipt = TransactionReceipt(tx_id, amount, approving_keys, "APPROVED")
        self.receipts.append(receipt)
        
        msg = f"TX Approved by {approving_keys} | Amount: {amount} BTC"
        self.transaction_log.append(msg)
        return True, receipt.to_dict()

    def get_status(self):
        return {
            "total_key_balance": sum(k.balance for k in self.keys),
            "total_vault_balance": sum(v.balance for v in self.vaults),
            "keys": [{"name": k.name, "identifier": k.identifier, "balance": k.balance} for k in self.keys],
            "vaults": [{"name": v.name, "level": v.access_level, "balance": v.balance, "description": v.description} for v in self.vaults]
        }

    def get_receipts(self):
        return [r.to_dict() for r in self.receipts]

treasury = GuardianTreasury()

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(treasury.get_status())

@app.route('/api/transaction', methods=['POST'])
def process_transaction():
    data = request.json
    amount = data.get('amount', 0)
    keys = data.get('keys', [])
    success, result = treasury.process_transaction_multi_key(amount, keys)
    if success:
        return jsonify({"success": True, "receipt": result})
    else:
        return jsonify({"success": False, "error": result}), 400

@app.route('/api/receipts', methods=['GET'])
def get_receipts():
    return jsonify({"receipts": treasury.get_receipts()})

@app.route('/api/keys', methods=['GET'])
def get_keys():
    return jsonify({"keys": [{"id": i+1, "name": k.name} for i, k in enumerate(treasury.keys)]})

@app.route('/', methods=['GET'])
def dashboard():
    return render_template_string(DASHBOARD_HTML)

if __name__ == '__main__':
    print("Columbus-Ω Treasury API Starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
