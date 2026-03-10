import time
import random
import sys

class Subsystem:
    def __init__(self, name):
        self.name = name
        self.threat_log = []

    def log_threat(self, threat):
        self.threat_log.append(f"Threat detected: {threat}")

class GuardianWallet:
    def __init__(self, initial_balance=10.0):
        self.balance_btc = initial_balance
        self.transaction_log = []

    def process_tx(self, tx_id, amount, source):
        self.balance_btc += amount
        self.transaction_log.append(f"ID: {tx_id}, Amount: {amount} BTC, Source: {source}")

class PopulationLedger:
    def __init__(self):
        self.citizens = {}

    def register_citizen(self, cid, info):
        self.citizens[cid] = info

    def update_activity(self, cid, activity):
        if cid in self.citizens:
            self.citizens[cid]['last_activity'] = activity
            return True
        return False

class CrimeMap:
    def __init__(self):
        self.crimes = []

    def log_crime(self, location, crime_type, severity):
        self.crimes.append({'location': location, 'type': crime_type, 'severity': severity})

class LieDetector:
    def evaluate(self, statement):
        truth_score = random.randint(0, 100)
        return f"Statement: '{statement}' - Truth Score: {truth_score}%"

class ColumbusOmega:
    def __init__(self):
        self.subsystems = [Subsystem("Network"), Subsystem("Security"), Subsystem("Infrastructure")]
        self.wallet = GuardianWallet()
        self.population_ledger = PopulationLedger()
        self.crime_map = CrimeMap()
        self.lie_detector = LieDetector()

    def process_transaction(self, tx_id, amount, source):
        self.wallet.process_tx(tx_id, amount, source)
        print(f"Processed transaction {tx_id}")

    def global_monitoring_loop(self, threats):
        for threat in threats:
            sub = random.choice(self.subsystems)
            sub.log_threat(threat)
            print(f"Monitoring: Logged threat {threat['id']} to {sub.name}")

    def update_population_activity(self, cid, activity):
        if self.population_ledger.update_activity(cid, activity):
            print(f"Updated activity for {cid}")
        else:
            print(f"Citizen {cid} not found")

    def log_crime(self, location, crime_type, severity):
        self.crime_map.log_crime(location, crime_type, severity)
        print(f"Logged {crime_type} at {location}")

    def evaluate_statement(self, statement):
        result = self.lie_detector.evaluate(statement)
        print(result)

def interactive_menu(columbus_omega: ColumbusOmega):
    while True:
        print("\n=== Columbus-Ω Simulation Menu ===")
        print("1. Process a transaction")
        print("2. Trigger a threat")
        print("3. Update citizen activity")
        print("4. Log a crime")
        print("5. Evaluate a statement")
        print("6. Show subsystem logs")
        print("7. Show Guardian Wallet balance")
        print("0. Exit simulation")
        
        try:
            choice = input("Choose an option: ").strip()
        except EOFError:
            break

        if choice == "1":
            tx_id = input("Transaction ID: ")
            try:
                amount_str = input("Amount (BTC): ")
                amount = float(amount_str)
                source = input("Source Wallet: ")
                columbus_omega.process_transaction(tx_id, amount, source)
            except ValueError:
                print("Invalid amount.")

        elif choice == "2":
            threat_id = input("Threat ID: ")
            try:
                complexity = float(input("Complexity (1-200): "))
                espionage_level = float(input("Espionage Level (0-100): "))
                columbus_omega.global_monitoring_loop([{
                    'id': threat_id,
                    'complexity': complexity,
                    'espionage_level': espionage_level
                }])
            except ValueError:
                print("Invalid numerical values.")

        elif choice == "3":
            cid = input("Citizen ID: ")
            activity = input("Activity description: ")
            columbus_omega.update_population_activity(cid, activity)

        elif choice == "4":
            location = input("Crime location: ")
            crime_type = input("Crime type: ")
            try:
                severity = int(input("Severity (1-10): "))
                columbus_omega.log_crime(location, crime_type, severity)
            except ValueError:
                print("Invalid severity.")

        elif choice == "5":
            statement = input("Enter statement to evaluate: ")
            columbus_omega.evaluate_statement(statement)

        elif choice == "6":
            for sub in columbus_omega.subsystems:
                print(f"\n[{sub.name}] Threat Log:")
                for log in sub.threat_log:
                    print(log)

        elif choice == "7":
            print(f"Guardian Wallet Balance: {columbus_omega.wallet.balance_btc} BTC")
            print("Transaction Log:")
            for tx in columbus_omega.wallet.transaction_log:
                print(tx)

        elif choice == "0":
            print("Exiting simulation...")
            break
        else:
            print("Invalid option.")

        time.sleep(0.1)

if __name__ == "__main__":
    columbus_omega = ColumbusOmega()
    columbus_omega.population_ledger.register_citizen('Citizen-001', {'name':'Alice','balance':2.5})
    columbus_omega.population_ledger.register_citizen('Citizen-002', {'name':'Bob','balance':5.0})
    interactive_menu(columbus_omega)
