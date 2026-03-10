# Columbus-Ω Treasury System

## Project Overview
An interactive Python CLI simulation implementing a sophisticated cybersecurity/governance treasury system with multi-signature authentication and a 4-layer vault architecture.

## Core Architecture

### Treasury Structure
- **7 Guardian Keys** with unique identifiers and individual balances (3,000,000 BTC each)
  - Guardian Key I (Ω1COL7GUARDIANAX3F4)
  - Guardian Key II (Ω2COL7TREASURYB92KD)
  - Guardian Key III (Ω3COL7NODECORE91LK)
  - Guardian Key IV (Ω4COL7VAULTSEALQ8P)
  - Guardian Key V (Ω5COL7FRAUDLOCKW2Z)
  - Guardian Key VI (Ω6COL7ANTISPAMT9X)
  - Guardian Key VII (Ω7COL7NEXUSCORE7AB)

### 4-Layer Vault Architecture
1. **Layer 1 - Public Monitoring Wallet** (1M BTC)
   - Visible address for transparency
   - Read-only observation point

2. **Layer 2 - Operational Reserve** (8M BTC)
   - Multi-signature authorization required
   - Connected to Columbus-7 node network

3. **Layer 3 - Deep Reserve Vault** (12M BTC)
   - Long-term security reserve
   - Restricted access through multi-node approval

4. **Layer 4 - Quantum Cold Vault** (2M BTC)
   - Completely offline cryptographic storage
   - Key fragments distributed across secure facilities
   - Protected by quantum-resistant encryption

### Multi-Key Transaction System
- **Requirement**: 3-of-7 guardian key approval (multi-signature)
- **Validation**: Combined balance check before execution
- **Execution**: Proportional deduction from approving keys
- **Receipt Generation**: Automatic with quantum signatures (QKS-XXXXXXXX format)

### Transaction Receipt Format
```
TX-ID: Unique hexadecimal identifier
Amount: Transaction amount in BTC
Guardian Keys: List of approving keys
Quantum Signature: QKS-XXXXXXXX
Status: APPROVED
Timestamp: Date and time of transaction
```

## Features Implemented
- ✓ Interactive CLI menu system
- ✓ Multi-key transaction processor (3-of-7)
- ✓ Treasury status dashboard with vault breakdown
- ✓ Transaction receipt generation with quantum signatures
- ✓ Transaction logging and audit trail
- ✓ Guardian key balance management
- ✓ Proportional fund deduction across approving keys
- ✓ Error handling for invalid transactions

## Running the Simulation
The system runs as a continuous CLI application via the "Columbus-Ω Simulation" workflow:
```bash
python main.py
```

## Menu Options
1. **Process Multi-Key Transaction** - Execute 3-of-7 approved treasury transactions
2. **View Treasury Status** - Display vault architecture and guardian key balances
3. **View Transaction Receipts** - List all processed transactions with details
4. **View Transaction Log** - Display transaction history and audit trail
0. **Exit System** - Gracefully shut down the simulation

## Total System Assets
- **Guardian Key Balance**: 21,000,000 BTC (7 keys × 3M each)
- **Vault Balance**: 23,000,000 BTC (distributed across 4 layers)
- **Total Treasury**: 44,000,000 BTC equivalent

## Technical Stack
- Language: Python 3
- Architecture: Class-based with clear separation of concerns
- No external dependencies required
- Workflow: Configured as console-type background process
