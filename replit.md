# Columbus-Ω Treasury System

## Project Overview
An interactive Python-based governance treasury system with web dashboard and REST API backend. Features multi-key transaction approval, 4-layer vault architecture, and real-time status monitoring.

### Architecture
- **Backend API**: Flask REST API (`treasury_api.py`) - Port 5000
- **Frontend**: Web Dashboard (embedded in Flask) with interactive UI
- **Legacy CLI**: Interactive menu interface (`main.py`)

## Treasury Structure

### 7 Guardian Keys
Each with unique identifier and 3,000,000 BTC balance:
- Guardian Key I (Ω1COL7GUARDIANAX3F4)
- Guardian Key II (Ω2COL7TREASURYB92KD)
- Guardian Key III (Ω3COL7NODECORE91LK)
- Guardian Key IV (Ω4COL7VAULTSEALQ8P)
- Guardian Key V (Ω5COL7FRAUDLOCKW2Z)
- Guardian Key VI (Ω6COL7ANTISPAMT9X)
- Guardian Key VII (Ω7COL7NEXUSCORE7AB)

### 4-Layer Vault Architecture
1. **Public Monitoring Wallet** (1M BTC) - Transparent, read-only
2. **Operational Reserve** (8M BTC) - Multi-sig authorized operations
3. **Deep Reserve Vault** (12M BTC) - Long-term security, restricted
4. **Quantum Cold Vault** (2M BTC) - Offline storage, emergency access

## Multi-Key Transaction System
- **Requirement**: 3-of-7 guardian key approval
- **Validation**: Combined balance verification
- **Execution**: Proportional fund deduction
- **Receipt**: Auto-generated with quantum signatures (QKS-XXXXXXXX)

## API Endpoints
- `GET /api/status` - Treasury status and balances
- `GET /api/keys` - List all guardian keys
- `GET /api/receipts` - Transaction receipt history
- `POST /api/transaction` - Process multi-key transaction

### Transaction Request
```json
{
  "amount": 0.0041,
  "keys": ["Guardian Key I", "Guardian Key III", "Guardian Key V"]
}
```

### Transaction Response
```json
{
  "success": true,
  "receipt": {
    "tx_id": "01ccaf33",
    "amount": 0.0041,
    "approving_keys": [...],
    "quantum_signature": "QKS-83756782",
    "status": "APPROVED"
  }
}
```

## Kivy UI Features
- **Dashboard Tab**: Real-time treasury status and vault breakdown
- **Transaction Tab**: Multi-key selection, transaction processing
- **Receipts Tab**: Historical transaction records

## Running the System

### Workflows (Auto-Started)
1. **Treasury API** - Flask server on port 5000
2. **Kivy Dashboard** - Desktop/Mobile UI application

### Manual CLI
```bash
python main.py
```

## Total System Assets
- **Guardian Key Balance**: 21,000,000 BTC
- **Vault Balance**: 23,000,000 BTC
- **Total Treasury**: 44,000,000 BTC

## Technical Stack
- Language: Python 3
- Backend: Flask REST API
- Frontend: Kivy (cross-platform)
- No external crypto dependencies
- Zero external data fetching (fully self-contained)
