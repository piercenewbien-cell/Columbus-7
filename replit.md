# Columbus-Ω Treasury System V2

## Login Credentials
- **Username:** admin
- **Password:** columbus2026

## Features

### Treasury & Blockchain
- **Dashboard** — Live ticker (block height, TX count, balance, fraud flags), vault charts, Guardian Key status, live node feed, one-click TX generation and block mining
- **Guardian Node Panel** — 7 Guardian Keys with 3-of-7 multi-sig policy, per-key TX signature counts, live activity feed
- **4-Layer Vault Architecture** — Public Monitoring, Operational Reserve, Deep Reserve, Quantum Cold — each with QR wallet code
- **Transaction Ledger** — Full paginated history, type filtering, AI risk scores and fraud badges
- **Transaction Detail** — Full TXID, block confirmation, SHA-256 hash chain data, AI analysis panel, Guardian Key approvals
- **Block Explorer** — Full SHA-256 hash chain, block hashes, prev-hash linking, nonces, merkle roots, miners
- **New Transaction** — Multi-sig form requiring 3-of-7 Guardian Key selection, auto-mines a block on submit
- **Receipt Generator** — Printable receipts with quantum signature, guardian keys used, and QR code
- **QR Wallet Generator** — Per-vault green-on-black QR codes

### Tools
- **BTC Converter** — Live USD ↔ BTC conversion with simulated real-time price ticker, 24h high/low, multi-currency panel (USD/EUR/GBP/JPY/CAD/INR), animated price chart, conversion history
- **National Population Ledger** — Citizen registry with IDs, gender, country, DOB, age, status (Active/Migrant/Deceased/Pending); add/register citizens; one-click status changes; live population event feed; breakdown charts

### Background Services
- **Auto-miner thread** — Mines pending transactions every 10 seconds automatically
- **BTC price ticker** — Simulates live price movement every 4 seconds

## Architecture
- `main.py` — Flask backend, all routes, DB models, blockchain logic, background threads
- `templates/` — base, login, dashboard, transactions, tx_detail, guardian_nodes, blockchain, vaults, new_transaction, receipt, converter, population
- `static/css/style.css` — Full cyberpunk dark theme (Orbitron + Share Tech Mono fonts)
- `instance/columbus_omega.db` — SQLite persistent DB (auto-created on first run)

## Tech Stack
- Flask · Flask-SQLAlchemy · Flask-Login
- SQLite · hashlib (SHA-256) · qrcode · Pillow
- Pure CSS cyberpunk UI · Port 5000

## Running
```bash
python main.py
```
