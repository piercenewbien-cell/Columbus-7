# Columbus-Ω Treasury System V2

## Overview
A full-stack cyberpunk-themed blockchain treasury management dashboard built with Flask. Features a dark cyberpunk UI, real blockchain ledger with SHA-256 hash chaining, AI-powered fraud detection, 3-of-7 multi-signature Guardian Key system, and a persistent SQLite database.

## Login Credentials
- **Username:** admin
- **Password:** columbus2026

## Features
- **Login System** — Secure authentication with Flask-Login, all access logged
- **Dashboard** — Real-time stats, vault balances, Guardian Key status, live node activity feed
- **Guardian Node Panel** — 7 Guardian Keys with 3-of-7 multi-sig policy enforcement
- **4-Layer Vault Architecture** — Public Monitoring, Operational Reserve, Deep Reserve, Quantum Cold
- **Blockchain Ledger** — SHA-256 hash chaining, real block explorer with block numbers, nonces, merkle roots
- **Transaction Engine** — Multi-sig transaction processor with fee calculation
- **AI Guardian** — Risk scoring and fraud detection on every transaction
- **Mining Simulation** — Proof-of-work block mining (difficulty 4, leading zeros)
- **Receipt Generator** — Printable crypto-style receipts with QR codes
- **QR Wallet Generator** — Per-vault QR codes using the qrcode library
- **Live Node Feed** — Real-time node activity ticker and activity feed
- **Auto-generate TX** — One-click random transaction generation

## Architecture
- `main.py` — Flask backend, all routes, database models, blockchain logic
- `templates/` — Jinja2 HTML templates (base, login, dashboard, transactions, tx_detail, guardian_nodes, blockchain, vaults, new_transaction, receipt)
- `static/css/style.css` — Full cyberpunk dark theme CSS
- `columbus_omega.db` — SQLite persistent database (auto-created)

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite (via SQLAlchemy ORM)
- **Crypto:** hashlib (SHA-256), qrcode, pillow
- **UI:** Pure CSS cyberpunk theme with Orbitron + Share Tech Mono fonts
- **Port:** 5000

## Running
```bash
python main.py
```
