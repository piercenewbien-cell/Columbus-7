import time
import random
from datetime import datetime
from typing import List

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
        self.timestamp = datetime.now()
        self.quantum_signature = f"QKS-{random.randint(10000000, 99999999):08d}"

    def __str__(self):
        keys_str = ", ".join(self.approving_keys)
        return f"""
TRANSACTION RECEIPT
TX-{self.tx_id}
Amount: {self.amount} BTC
Guardian Keys: {keys_str}
Quantum Signature: {self.quantum_signature}
Status: {self.status}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

class GuardianTreasury:
    def __init__(self):
        # Initialize 7 Guardian Keys
        self.keys = [
            GuardianKey("Guardian Key I", "Ω1COL7GUARDIANAX3F4", 3000000),
            GuardianKey("Guardian Key II", "Ω2COL7TREASURYB92KD", 3000000),
            GuardianKey("Guardian Key III", "Ω3COL7NODECORE91LK", 3000000),
            GuardianKey("Guardian Key IV", "Ω4COL7VAULTSEALQ8P", 3000000),
            GuardianKey("Guardian Key V", "Ω5COL7FRAUDLOCKW2Z", 3000000),
            GuardianKey("Guardian Key VI", "Ω6COL7ANTISPAMT9X", 3000000),
            GuardianKey("Guardian Key VII", "Ω7COL7NEXUSCORE7AB", 3000000),
        ]
        
        # Initialize 4-Layer Vault Architecture
        self.vaults = [
            VaultLayer("Public Monitoring Wallet", 1, "Visible address for transparency - Read-only"),
            VaultLayer("Operational Reserve", 2, "Multi-signature authorization - Active operations"),
            VaultLayer("Deep Reserve Vault", 3, "Long-term security - Restricted access"),
            VaultLayer("Quantum Cold Vault", 4, "Offline cryptographic storage - Emergency only"),
        ]
        
        # Distribute balance across vaults
        self.vaults[0].balance = 1000000  # Public
        self.vaults[1].balance = 8000000  # Operational
        self.vaults[2].balance = 12000000  # Deep Reserve
        self.vaults[3].balance = 2000000  # Quantum Cold
        
        self.transaction_log = []
        self.receipts = []

    def process_transaction_multi_key(self, amount, approving_keys):
        # 3-of-7 multi-signature requirement
        if len(approving_keys) < 3:
            msg = "Transaction failed: Not enough keys approved (minimum 3-of-7 required)"
            self.transaction_log.append(msg)
            return False, msg

        # Verify all keys exist
        valid_keys = [k.name for k in self.keys]
        for key in approving_keys:
            if key not in valid_keys:
                msg = f"Transaction failed: Invalid key '{key}'"
                self.transaction_log.append(msg)
                return False, msg

        # Check combined balance from approving keys
        total_available = 0
        for key_name in approving_keys:
            for k in self.keys:
                if k.name == key_name:
                    total_available += k.balance

        if total_available < amount:
            msg = f"Transaction failed: Insufficient combined balance ({total_available} BTC available, {amount} BTC requested)"
            self.transaction_log.append(msg)
            return False, msg

        # Deduct proportionally from keys
        remaining = amount
        for key_name in approving_keys:
            for k in self.keys:
                if k.name == key_name and remaining > 0:
                    deduction = min(k.balance, remaining)
                    k.balance -= deduction
                    remaining -= deduction

        # Create transaction receipt
        tx_id = f"{random.randint(10000000, 99999999):08x}"
        receipt = TransactionReceipt(tx_id, amount, approving_keys, "APPROVED")
        self.receipts.append(receipt)

        msg = f"TX Approved by Keys {approving_keys} | Amount: {amount} BTC"
        self.transaction_log.append(msg)
        return True, receipt

    def total_balance(self):
        return sum(k.balance for k in self.keys)

    def vault_balance(self):
        return sum(v.balance for v in self.vaults)

    def display_treasury_status(self):
        print("\n" + "=" * 60)
        print("COLUMBUS-Ω TREASURY STATUS")
        print("=" * 60)
        print(f"\nTotal Key Balance: {self.total_balance():,.0f} BTC")
        print(f"Total Vault Balance: {self.vault_balance():,.0f} BTC")
        
        print("\n4-LAYER VAULT ARCHITECTURE:")
        for i, vault in enumerate(self.vaults, 1):
            print(f"  Layer {i} - {vault.name}: {vault.balance:,.0f} BTC")
            print(f"    {vault.description}")
        
        print("\n7 GUARDIAN KEYS:")
        for i, key in enumerate(self.keys, 1):
            print(f"  Key {i}: {key.name} | Balance: {key.balance:,.0f} BTC")
        print("=" * 60)

class ColumbusOmega:
    def __init__(self):
        self.treasury = GuardianTreasury()
        self.running = True

    def interactive_menu(self):
        while self.running:
            print("\n" + "=" * 60)
            print("COLUMBUS-Ω TREASURY MANAGEMENT SYSTEM")
            print("=" * 60)
            print("1. Process Multi-Key Transaction (3-of-7)")
            print("2. View Treasury Status")
            print("3. View Transaction Receipts")
            print("4. View Transaction Log")
            print("0. Exit System")
            print("=" * 60)
            
            try:
                choice = input("Choose an option: ").strip()
            except EOFError:
                break

            if choice == "1":
                self.process_transaction()
            elif choice == "2":
                self.treasury.display_treasury_status()
            elif choice == "3":
                self.view_receipts()
            elif choice == "4":
                self.view_log()
            elif choice == "0":
                print("Exiting Columbus-Ω Treasury System...")
                self.running = False
            else:
                print("Invalid option.")

    def process_transaction(self):
        print("\nMULTI-KEY TRANSACTION PROCESSOR")
        print("(Requires 3-of-7 guardian key approval)")
        
        try:
            amount = float(input("Enter transaction amount (BTC): "))
        except ValueError:
            print("Invalid amount.")
            return

        print("\nSelect approving keys (enter key numbers, comma-separated):")
        for i, key in enumerate(self.treasury.keys, 1):
            print(f"  {i}. {key.name}")
        
        try:
            selections = input("Enter key numbers (e.g., 1,3,5): ").split(",")
            approving_keys = []
            for sel in selections:
                idx = int(sel.strip()) - 1
                if 0 <= idx < len(self.treasury.keys):
                    approving_keys.append(self.treasury.keys[idx].name)
                else:
                    print(f"Invalid key selection: {sel}")
                    return
            
            success, result = self.treasury.process_transaction_multi_key(amount, approving_keys)
            
            if success:
                print(result)
            else:
                print(result)
        except (ValueError, IndexError) as e:
            print(f"Error processing transaction: {e}")

    def view_receipts(self):
        if not self.treasury.receipts:
            print("No transaction receipts available.")
            return
        
        print("\nTRANSACTION RECEIPTS:")
        for receipt in self.treasury.receipts:
            print(receipt)

    def view_log(self):
        if not self.treasury.transaction_log:
            print("No transaction log entries.")
            return
        
        print("\nTRANSACTION LOG:")
        for entry in self.treasury.transaction_log:
            print(f"  {entry}")

if __name__ == "__main__":
    columbus = ColumbusOmega()
    columbus.interactive_menu()
