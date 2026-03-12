import os
import hashlib
import random
import json
import io
import base64
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'columbus-omega-secret-key-v2-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///columbus_omega.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Access denied. Authentication required.'

# ─── DATABASE MODELS ──────────────────────────────────────────────────────────

GUARDIAN_WALLET = "bc1qguardianwallet2026node-columbus-omega-v2"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='operator')
    balance = db.Column(db.Float, default=1000.0)
    wallet_address = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_number = db.Column(db.Integer, unique=True, nullable=False)
    block_hash = db.Column(db.String(64), unique=True, nullable=False)
    prev_hash = db.Column(db.String(64), nullable=False)
    merkle_root = db.Column(db.String(64), nullable=False)
    nonce = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.Integer, default=4)
    miner = db.Column(db.String(100), default='Columbus-Ω Node')
    reward = db.Column(db.Float, default=6.25)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tx_count = db.Column(db.Integer, default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txid = db.Column(db.String(64), unique=True, nullable=False)
    block_number = db.Column(db.Integer, db.ForeignKey('block.block_number'), nullable=True)
    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    tx_type = db.Column(db.String(30), default='TRANSFER')
    status = db.Column(db.String(20), default='CONFIRMED')
    guardian_keys = db.Column(db.Text, default='[]')
    quantum_sig = db.Column(db.String(50), nullable=False)
    ai_risk_score = db.Column(db.Float, default=0.0)
    ai_analysis = db.Column(db.Text, default='')
    fraud_flag = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class GuardianKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    identifier = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=3000000)
    status = db.Column(db.String(20), default='ACTIVE')
    tx_signed = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

class VaultLayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    wallet_address = db.Column(db.String(50), nullable=False)

class NodeActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(30), nullable=False)
    event = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(30), default='INFO')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(1), default='M')
    country = db.Column(db.String(80), default='Columbus Nation')
    birth_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='ACTIVE')
    notes = db.Column(db.String(200), default='')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def make_txid(data_str):
    return hashlib.sha256(data_str.encode()).hexdigest()

def make_block_hash(block_number, prev_hash, merkle_root, nonce):
    data = f"{block_number}{prev_hash}{merkle_root}{nonce}"
    return hashlib.sha256(data.encode()).hexdigest()

def make_merkle_root(txids):
    if not txids:
        return hashlib.sha256(b'genesis').hexdigest()
    combined = ''.join(txids)
    return hashlib.sha256(combined.encode()).hexdigest()

def make_quantum_sig():
    parts = [
        f"QKS-{random.randint(10000000, 99999999):08X}",
        f"Ω{random.randint(1000, 9999)}",
        f"COL{random.randint(100000, 999999)}"
    ]
    return '-'.join(parts)

def make_wallet_address(seed):
    h = hashlib.sha256(seed.encode()).hexdigest()
    return f"COL1{h[:38].upper()}"

def ai_analyze_transaction(amount, sender, receiver, tx_type):
    risk = 0.0
    flags = []
    if amount > 500000:
        risk += 35
        flags.append("Large amount")
    if amount > 1000000:
        risk += 25
        flags.append("Very large transfer")
    if tx_type == 'EMERGENCY':
        risk += 20
        flags.append("Emergency type")
    if sender == receiver:
        risk += 40
        flags.append("Self-transfer")
    risk += random.uniform(0, 10)
    risk = min(risk, 99.9)
    if flags:
        analysis = f"AI Guardian detected: {', '.join(flags)}. Risk score: {risk:.1f}%"
    else:
        analysis = f"Transaction appears normal. Risk score: {risk:.1f}%"
    fraud = risk > 70
    return round(risk, 2), analysis, fraud

def log_node_event(node_id, event, event_type='INFO'):
    entry = NodeActivity(node_id=node_id, event=event, event_type=event_type)
    db.session.add(entry)
    db.session.commit()

# ─── BTC PRICE SIMULATION ─────────────────────────────────────────────────────

_btc_state = {
    'price': 67420.00,
    'open': 66000.00,
    'high': 68200.00,
    'low': 65800.00,
    'change_pct': 2.14,
}

def _tick_btc_price():
    while True:
        p = _btc_state['price']
        p = p * (1 + (random.random() - 0.495) * 0.003)
        p = round(p, 2)
        if p > _btc_state['high']:
            _btc_state['high'] = p
        if p < _btc_state['low']:
            _btc_state['low'] = p
        _btc_state['price'] = p
        _btc_state['change_pct'] = round((p - _btc_state['open']) / _btc_state['open'] * 100, 2)
        time.sleep(4)

# ─── BACKGROUND AUTO-MINER ───────────────────────────────────────────────────

def _auto_miner():
    time.sleep(20)
    while True:
        try:
            with app.app_context():
                # Process vault pending TXs
                pending = Transaction.query.filter_by(block_number=None, status='CONFIRMED').limit(5).all()
                all_txids = [t.txid for t in pending]
                # Process user-to-user pending TXs
                while pending_user_tx:
                    utx = pending_user_tx.pop(0)
                    keys_used = [k.name for k in GuardianKey.query.limit(3).all()]
                    risk, analysis, fraud = ai_analyze_transaction(
                        utx['amount'], utx['sender_wallet'], utx['receiver_wallet'], 'TRANSFER')
                    t = Transaction(
                        txid=utx['txid'],
                        sender=utx['sender_wallet'],
                        receiver=utx['receiver_wallet'],
                        amount=utx['amount'],
                        fee=utx['fee'],
                        tx_type='USER-TRANSFER',
                        status='CONFIRMED',
                        guardian_keys=json.dumps(keys_used),
                        quantum_sig=make_quantum_sig(),
                        ai_risk_score=risk,
                        ai_analysis=analysis,
                        fraud_flag=fraud
                    )
                    db.session.add(t)
                    # Credit receiver if they're a registered user
                    rv = utx.get('receiver_user')
                    if rv:
                        recv_db = User.query.get(rv.id)
                        if recv_db:
                            recv_db.balance += utx['amount']
                    db.session.commit()
                    all_txids.append(utx['txid'])
                    log_node_event('TX-Node',
                        f"User TX confirmed: {utx['sender']} → {utx['receiver']} | {utx['amount']:,.4f} COL",
                        'TX')
                if all_txids:
                    miner = f"Columbus-Ω Node-{random.randint(1, 3)}"
                    block = mine_block(all_txids, miner=miner)
                    for t in pending:
                        t.block_number = block.block_number
                    db.session.commit()
        except Exception:
            pass
        time.sleep(10)

def get_latest_block():
    return Block.query.order_by(Block.block_number.desc()).first()

def mine_block(txids, miner='Columbus-Ω Node-1'):
    latest = get_latest_block()
    block_num = (latest.block_number + 1) if latest else 1
    prev_hash = latest.block_hash if latest else '0' * 64
    merkle = make_merkle_root(txids)
    difficulty = 4
    nonce = 0
    target = '0' * difficulty
    while True:
        candidate = make_block_hash(block_num, prev_hash, merkle, nonce)
        if candidate.startswith(target):
            break
        nonce += 1
        if nonce > 500000:
            break
    block = Block(
        block_number=block_num,
        block_hash=candidate,
        prev_hash=prev_hash,
        merkle_root=merkle,
        nonce=nonce,
        difficulty=difficulty,
        miner=miner,
        reward=6.25,
        tx_count=len(txids)
    )
    db.session.add(block)
    db.session.commit()
    log_node_event(miner, f"Block #{block_num} mined | Hash: {candidate[:16]}... | Nonce: {nonce}", 'BLOCK')
    return block

pending_user_tx = []

def init_db():
    db.create_all()
    # Migrate: add balance/wallet_address columns if missing (existing DB)
    import sqlite3 as _sqlite3
    try:
        _con = _sqlite3.connect('instance/columbus_omega.db')
        _cur = _con.cursor()
        _cur.execute("ALTER TABLE user ADD COLUMN balance REAL DEFAULT 1000.0")
        _con.commit()
        _con.close()
    except Exception:
        pass
    try:
        _con = _sqlite3.connect('instance/columbus_omega.db')
        _cur = _con.cursor()
        _cur.execute("ALTER TABLE user ADD COLUMN wallet_address TEXT DEFAULT ''")
        _con.commit()
        _con.close()
    except Exception:
        pass

    if not User.query.first():
        admin = User(username='admin', role='admin', balance=10000.0)
        admin.set_password('columbus2026')
        admin.wallet_address = make_wallet_address('admin-guardian-2026')
        db.session.add(admin)
        db.session.commit()
    else:
        # Ensure existing users have wallet addresses
        for u in User.query.all():
            if not u.wallet_address:
                u.wallet_address = make_wallet_address(u.username + str(u.id))
        db.session.commit()

    if not GuardianKey.query.first():
        keys_data = [
            ("Guardian Key I",   "Ω1COL7GUARDIANAX3F4", 3000000),
            ("Guardian Key II",  "Ω2COL7TREASURYB92KD", 3000000),
            ("Guardian Key III", "Ω3COL7NODECORE91LK",  3000000),
            ("Guardian Key IV",  "Ω4COL7VAULTSEALQ8P",  3000000),
            ("Guardian Key V",   "Ω5COL7FRAUDLOCKW2Z",  3000000),
            ("Guardian Key VI",  "Ω6COL7ANTISPAMT9X",   3000000),
            ("Guardian Key VII", "Ω7COL7NEXUSCORE7AB",  3000000),
        ]
        for name, ident, bal in keys_data:
            db.session.add(GuardianKey(name=name, identifier=ident, balance=bal))
        db.session.commit()

    if not VaultLayer.query.first():
        vaults_data = [
            ("Public Monitoring Wallet",   1, "Visible address for transparency - Read-only",           1000000),
            ("Operational Reserve",        2, "Multi-signature authorization - Active operations",      8000000),
            ("Deep Reserve Vault",         3, "Long-term security - Restricted access",                12000000),
            ("Quantum Cold Vault",         4, "Offline cryptographic storage - Emergency only",         2000000),
        ]
        for name, lvl, desc, bal in vaults_data:
            addr = make_wallet_address(name + str(lvl))
            db.session.add(VaultLayer(name=name, access_level=lvl, description=desc, balance=bal, wallet_address=addr))
        db.session.commit()

    if not Block.query.first():
        genesis = Block(
            block_number=0,
            block_hash=hashlib.sha256(b'COLUMBUS-OMEGA-GENESIS-BLOCK').hexdigest(),
            prev_hash='0' * 64,
            merkle_root=hashlib.sha256(b'genesis').hexdigest(),
            nonce=0,
            difficulty=0,
            miner='Satoshi-Columbus',
            reward=50.0,
            tx_count=0,
            timestamp=datetime(2024, 1, 1)
        )
        db.session.add(genesis)
        db.session.commit()
        log_node_event('Genesis-Node', 'Columbus-Ω blockchain initialized. Genesis block created.', 'SYSTEM')

    if Transaction.query.count() < 15:
        seed_transactions()

    if Citizen.query.count() < 20:
        seed_citizens()

def seed_citizens():
    first_names = ['James', 'Maria', 'David', 'Sofia', 'Carlos', 'Elena', 'Omar', 'Amara',
                   'Lucas', 'Leila', 'Kevin', 'Fatima', 'Andre', 'Yuki', 'Hassan', 'Nina',
                   'Samuel', 'Priya', 'Felix', 'Ingrid', 'Diego', 'Zara', 'Marcus', 'Aisha']
    last_names = ['Rivera', 'Chen', 'Okafor', 'Petrov', 'Santos', 'Ibrahim', 'Nakamura',
                  'Mueller', 'Diallo', 'Patel', 'Kowalski', 'Andersen', 'Torres', 'Nguyen',
                  'Mensah', 'Rossi', 'Yamamoto', 'Fernandez', 'Kim', 'Haile']
    countries = ['Columbus Nation', 'Columbus Nation', 'Columbus Nation', 'Columbus Nation',
                 'Abroad-North', 'Abroad-South', 'Abroad-East', 'Abroad-West']
    statuses = ['ACTIVE', 'ACTIVE', 'ACTIVE', 'ACTIVE', 'ACTIVE',
                'MIGRANT', 'MIGRANT', 'DECEASED', 'PENDING']
    genders = ['M', 'F', 'M', 'F', 'M', 'F', 'O']
    for i in range(40):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        cid = f"CIT-{random.randint(100000, 999999)}"
        status = random.choice(statuses)
        gender = random.choice(genders)
        country = random.choice(countries)
        if status == 'MIGRANT':
            country = random.choice(countries[4:])
        birth_year = random.randint(1950, 2005)
        birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
        notes_pool = ['Veteran', 'Business owner', 'Registered voter', 'Dual citizen',
                      'Student visa', 'Work permit', 'Retired', '', '', '']
        c = Citizen(
            citizen_id=cid, name=name, gender=gender, country=country,
            birth_date=birth_date, status=status,
            notes=random.choice(notes_pool),
            registered_at=datetime.utcnow() - timedelta(days=random.randint(1, 1000))
        )
        db.session.add(c)
    db.session.commit()

def seed_transactions():
    vaults = VaultLayer.query.all()
    vault_addrs = [v.wallet_address for v in vaults]
    types = ['TRANSFER', 'TRANSFER', 'TRANSFER', 'RESERVE', 'OPERATIONAL', 'EMERGENCY']
    txids = []
    for i in range(15):
        sender = random.choice(vault_addrs)
        receiver = random.choice([a for a in vault_addrs if a != sender])
        amount = round(random.uniform(1000, 500000), 2)
        fee = round(amount * 0.001, 4)
        tx_type = random.choice(types)
        keys_used = random.sample([k.name for k in GuardianKey.query.all()], k=random.randint(3, 5))
        risk, analysis, fraud = ai_analyze_transaction(amount, sender, receiver, tx_type)
        txid = make_txid(f"{sender}{receiver}{amount}{time.time()}{i}{random.random()}")
        t = Transaction(
            txid=txid,
            sender=sender,
            receiver=receiver,
            amount=amount,
            fee=fee,
            tx_type=tx_type,
            status='CONFIRMED',
            guardian_keys=json.dumps(keys_used),
            quantum_sig=make_quantum_sig(),
            ai_risk_score=risk,
            ai_analysis=analysis,
            fraud_flag=fraud,
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        )
        db.session.add(t)
        txids.append(txid)
    db.session.commit()
    for i in range(0, len(txids), 5):
        batch = txids[i:i+5]
        mine_block(batch, miner=f"Columbus-Ω Node-{random.randint(1,3)}")

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log_node_event('Auth-Node', f"User '{username}' authenticated successfully.", 'AUTH')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Access denied.')
        log_node_event('Auth-Node', f"Failed login attempt for '{username}'.", 'WARN')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_node_event('Auth-Node', f"User '{current_user.username}' logged out.", 'AUTH')
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    keys = GuardianKey.query.all()
    vaults = VaultLayer.query.all()
    latest_block = get_latest_block()
    recent_tx = Transaction.query.order_by(Transaction.timestamp.desc()).limit(8).all()
    total_key_balance = sum(k.balance for k in keys)
    total_vault_balance = sum(v.balance for v in vaults)
    total_tx = Transaction.query.count()
    fraud_count = Transaction.query.filter_by(fraud_flag=True).count()
    recent_activity = NodeActivity.query.order_by(NodeActivity.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html',
        keys=keys, vaults=vaults, latest_block=latest_block,
        recent_tx=recent_tx, total_key_balance=total_key_balance,
        total_vault_balance=total_vault_balance, total_tx=total_tx,
        fraud_count=fraud_count, recent_activity=recent_activity)

@app.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    tx_filter = request.args.get('filter', 'all')
    query = Transaction.query
    if tx_filter == 'fraud':
        query = query.filter_by(fraud_flag=True)
    elif tx_filter == 'confirmed':
        query = query.filter_by(status='CONFIRMED')
    elif tx_filter == 'pending':
        query = query.filter_by(status='PENDING')
    txs = query.order_by(Transaction.timestamp.desc()).paginate(page=page, per_page=15)
    return render_template('transactions.html', txs=txs, tx_filter=tx_filter)

@app.route('/transaction/<txid>')
@login_required
def transaction_detail(txid):
    tx = Transaction.query.filter_by(txid=txid).first_or_404()
    block = Block.query.filter_by(block_number=tx.block_number).first()
    keys_used = json.loads(tx.guardian_keys)
    return render_template('tx_detail.html', tx=tx, block=block, keys_used=keys_used)

@app.route('/guardian-nodes')
@login_required
def guardian_nodes():
    keys = GuardianKey.query.all()
    activity = NodeActivity.query.order_by(NodeActivity.timestamp.desc()).limit(30).all()
    return render_template('guardian_nodes.html', keys=keys, activity=activity)

@app.route('/blockchain')
@login_required
def blockchain():
    page = request.args.get('page', 1, type=int)
    blocks = Block.query.order_by(Block.block_number.desc()).paginate(page=page, per_page=10)
    return render_template('blockchain.html', blocks=blocks)

@app.route('/vaults')
@login_required
def vaults():
    vault_list = VaultLayer.query.all()
    return render_template('vaults.html', vaults=vault_list)

@app.route('/new-transaction', methods=['GET', 'POST'])
@login_required
def new_transaction():
    vaults = VaultLayer.query.all()
    keys = GuardianKey.query.all()
    if request.method == 'POST':
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        amount = float(request.form.get('amount', 0))
        tx_type = request.form.get('tx_type', 'TRANSFER')
        selected_keys = request.form.getlist('guardian_keys')

        if amount <= 0:
            flash('Amount must be greater than zero.')
            return render_template('new_transaction.html', vaults=vaults, keys=keys)
        if len(selected_keys) < 3:
            flash('Minimum 3 Guardian Keys required (3-of-7 multi-sig).')
            return render_template('new_transaction.html', vaults=vaults, keys=keys)
        if sender == receiver:
            flash('Sender and receiver cannot be the same vault.')
            return render_template('new_transaction.html', vaults=vaults, keys=keys)

        sender_vault = VaultLayer.query.filter_by(wallet_address=sender).first()
        if sender_vault and sender_vault.balance < amount:
            flash(f'Insufficient vault balance. Available: {sender_vault.balance:,.2f} COL')
            return render_template('new_transaction.html', vaults=vaults, keys=keys)

        fee = round(amount * 0.001, 4)
        risk, analysis, fraud = ai_analyze_transaction(amount, sender, receiver, tx_type)
        txid = make_txid(f"{sender}{receiver}{amount}{time.time()}{random.random()}")
        tx = Transaction(
            txid=txid,
            sender=sender,
            receiver=receiver,
            amount=amount,
            fee=fee,
            tx_type=tx_type,
            status='CONFIRMED',
            guardian_keys=json.dumps(selected_keys),
            quantum_sig=make_quantum_sig(),
            ai_risk_score=risk,
            ai_analysis=analysis,
            fraud_flag=fraud
        )
        db.session.add(tx)
        if sender_vault:
            sender_vault.balance -= amount
        recv_vault = VaultLayer.query.filter_by(wallet_address=receiver).first()
        if recv_vault:
            recv_vault.balance += amount
        for key_name in selected_keys:
            key = GuardianKey.query.filter_by(name=key_name).first()
            if key:
                key.tx_signed += 1
                key.last_active = datetime.utcnow()
        db.session.commit()
        block = mine_block([txid], miner=f"Columbus-Ω Node-{random.randint(1,3)}")
        tx.block_number = block.block_number
        db.session.commit()
        log_node_event('TX-Node', f"Transaction {txid[:16]}... processed. Amount: {amount:,.2f} COL. Risk: {risk}%",
                       'WARN' if fraud else 'TX')
        flash(f'Transaction submitted! TXID: {txid[:20]}...')
        return redirect(url_for('transaction_detail', txid=txid))
    return render_template('new_transaction.html', vaults=vaults, keys=keys)

@app.route('/receipt/<txid>')
@login_required
def receipt(txid):
    tx = Transaction.query.filter_by(txid=txid).first_or_404()
    block = Block.query.filter_by(block_number=tx.block_number).first()
    keys_used = json.loads(tx.guardian_keys)
    return render_template('receipt.html', tx=tx, block=block, keys_used=keys_used)

@app.route('/qr/<wallet_address>')
@login_required
def qr_code(wallet_address):
    qr = qrcode.QRCode(version=2, box_size=8, border=3,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(f"columbus-omega:{wallet_address}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00ff88", back_color="#0a0a0a")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/mine', methods=['POST'])
@login_required
def mine():
    pending = Transaction.query.filter_by(block_number=None, status='CONFIRMED').limit(5).all()
    txids = [t.txid for t in pending]
    if not txids:
        txids = [make_txid(f"empty-block-{time.time()}{random.random()}")]
    block = mine_block(txids, miner=f"Columbus-Ω Node-{random.randint(1,3)}")
    for t in pending:
        t.block_number = block.block_number
    db.session.commit()
    return jsonify({'success': True, 'block_number': block.block_number,
                    'block_hash': block.block_hash, 'nonce': block.nonce})

# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/stats')
@login_required
def api_stats():
    keys = GuardianKey.query.all()
    vaults = VaultLayer.query.all()
    latest_block = get_latest_block()
    return jsonify({
        'total_key_balance': sum(k.balance for k in keys),
        'total_vault_balance': sum(v.balance for v in vaults),
        'total_blocks': Block.query.count(),
        'total_tx': Transaction.query.count(),
        'fraud_count': Transaction.query.filter_by(fraud_flag=True).count(),
        'latest_block': latest_block.block_number if latest_block else 0,
        'latest_hash': latest_block.block_hash[:16] + '...' if latest_block else '',
    })

@app.route('/api/node-feed')
@login_required
def api_node_feed():
    activity = NodeActivity.query.order_by(NodeActivity.timestamp.desc()).limit(15).all()
    return jsonify([{
        'node_id': a.node_id,
        'event': a.event,
        'event_type': a.event_type,
        'timestamp': a.timestamp.strftime('%H:%M:%S')
    } for a in activity])

@app.route('/api/generate-tx')
@login_required
def api_generate_tx():
    vaults = VaultLayer.query.all()
    if len(vaults) < 2:
        return jsonify({'error': 'Not enough vaults'}), 400
    vault_addrs = [v.wallet_address for v in vaults]
    sender = random.choice(vault_addrs)
    receiver = random.choice([a for a in vault_addrs if a != sender])
    amount = round(random.uniform(500, 100000), 2)
    fee = round(amount * 0.001, 4)
    tx_type = random.choice(['TRANSFER', 'RESERVE', 'OPERATIONAL'])
    keys_used = random.sample([k.name for k in GuardianKey.query.all()], k=random.randint(3, 5))
    risk, analysis, fraud = ai_analyze_transaction(amount, sender, receiver, tx_type)
    txid = make_txid(f"{sender}{receiver}{amount}{time.time()}{random.random()}")
    tx = Transaction(
        txid=txid,
        sender=sender,
        receiver=receiver,
        amount=amount,
        fee=fee,
        tx_type=tx_type,
        status='CONFIRMED',
        guardian_keys=json.dumps(keys_used),
        quantum_sig=make_quantum_sig(),
        ai_risk_score=risk,
        ai_analysis=analysis,
        fraud_flag=fraud
    )
    db.session.add(tx)
    sv = VaultLayer.query.filter_by(wallet_address=sender).first()
    rv = VaultLayer.query.filter_by(wallet_address=receiver).first()
    if sv and sv.balance >= amount:
        sv.balance -= amount
        if rv:
            rv.balance += amount
    db.session.commit()
    block = mine_block([txid], miner=f"Columbus-Ω Node-{random.randint(1,3)}")
    tx.block_number = block.block_number
    db.session.commit()
    log_node_event('Auto-TX', f"Auto-generated TX {txid[:12]}... | {amount:,.2f} COL | Risk: {risk}%",
                   'WARN' if fraud else 'TX')
    return jsonify({
        'txid': txid, 'amount': amount, 'block': block.block_number,
        'risk': risk, 'fraud': fraud, 'analysis': analysis
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        if len(username) < 3:
            flash('Operator ID must be at least 3 characters.')
            return render_template('register.html')
        if len(password) < 6:
            flash('Access key must be at least 6 characters.')
            return render_template('register.html')
        if password != password2:
            flash('Access keys do not match.')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Operator ID already exists. Choose another.')
            return render_template('register.html')
        wallet = make_wallet_address(username + str(time.time()))
        user = User(username=username, role='operator', balance=1000.0, wallet_address=wallet)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_node_event('Auth-Node', f"New operator '{username}' registered. Wallet: {wallet[:16]}...", 'AUTH')
        flash(f'Account created! Welcome, {username}. Starting balance: 1,000 COL. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST':
        receiver_input = request.form.get('receiver', '').strip()
        amount_str = request.form.get('amount', '0')
        note = request.form.get('note', '')
        try:
            amount = float(amount_str)
        except ValueError:
            flash('Invalid amount.')
            return redirect(url_for('send'))
        if amount <= 0:
            flash('Amount must be greater than zero.')
            return redirect(url_for('send'))
        if amount > current_user.balance:
            flash(f'Insufficient balance. You have {current_user.balance:,.4f} COL.')
            return redirect(url_for('send'))
        # Resolve receiver — by username or wallet address
        receiver_user = User.query.filter_by(username=receiver_input).first()
        if not receiver_user:
            receiver_user = User.query.filter_by(wallet_address=receiver_input).first()
        receiver_addr = receiver_user.wallet_address if receiver_user else receiver_input
        if receiver_addr == current_user.wallet_address:
            flash('Cannot send to your own wallet.')
            return redirect(url_for('send'))
        fee = round(amount * 0.001, 6)
        tx_entry = {
            'txid': make_txid(f"{current_user.username}{receiver_addr}{amount}{time.time()}{random.random()}"),
            'sender': current_user.username,
            'sender_wallet': current_user.wallet_address,
            'receiver': receiver_input,
            'receiver_wallet': receiver_addr,
            'receiver_user': receiver_user,
            'amount': amount,
            'fee': fee,
            'note': note,
        }
        current_user.balance -= amount
        db.session.commit()
        pending_user_tx.append(tx_entry)
        log_node_event('TX-Node',
            f"User TX queued: {current_user.username} → {receiver_input} | {amount:,.4f} COL | Note: {note or 'None'}",
            'TX')
        flash(f'Transfer of {amount:,.4f} COL queued for mining! TXID: {tx_entry["txid"][:16]}...')
        return redirect(url_for('send'))
    my_txs = Transaction.query.filter_by(sender=current_user.wallet_address)\
        .order_by(Transaction.timestamp.desc()).limit(8).all()
    return render_template('send.html', pending=pending_user_tx,
                           my_txs=my_txs, guardian_wallet=GUARDIAN_WALLET)

@app.route('/guardian-qr')
@login_required
def guardian_qr_page():
    return render_template('guardian_qr.html', guardian_wallet=GUARDIAN_WALLET)

@app.route('/guardian-qr-image')
@login_required
def guardian_qr_image():
    qr = qrcode.QRCode(version=2, box_size=8, border=3,
                       error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(f"bitcoin:{GUARDIAN_WALLET}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00ff88", back_color="#020408")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/converter')
@login_required
def converter():
    return render_template('converter.html')

@app.route('/population')
@login_required
def population():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    query = Citizen.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    citizens = query.order_by(Citizen.registered_at.desc()).paginate(page=page, per_page=20)
    today = datetime.utcnow().date()
    stats = {
        'total': Citizen.query.count(),
        'active': Citizen.query.filter_by(status='ACTIVE').count(),
        'migrant': Citizen.query.filter_by(status='MIGRANT').count(),
        'deceased': Citizen.query.filter_by(status='DECEASED').count(),
        'pending': Citizen.query.filter_by(status='PENDING').count(),
        'births_today': Citizen.query.filter(
            Citizen.status == 'ACTIVE',
            db.func.date(Citizen.registered_at) == today
        ).count(),
        'deaths_today': Citizen.query.filter(
            Citizen.status == 'DECEASED',
            db.func.date(Citizen.registered_at) == today
        ).count(),
    }
    return render_template('population.html', citizens=citizens, stats=stats,
                           status_filter=status_filter, datetime=datetime)

@app.route('/population/add', methods=['POST'])
@login_required
def population_add():
    name = request.form.get('name', '').strip()
    country = request.form.get('country', 'Columbus Nation').strip()
    status = request.form.get('status', 'ACTIVE')
    gender = request.form.get('gender', 'M')
    notes = request.form.get('notes', '')
    birth_str = request.form.get('birth_date', '')
    birth_date = None
    if birth_str:
        try:
            birth_date = datetime.strptime(birth_str, '%Y-%m-%d')
        except ValueError:
            pass
    if not name:
        flash('Name is required.')
        return redirect(url_for('population'))
    cid = f"CIT-{random.randint(100000, 999999)}"
    while Citizen.query.filter_by(citizen_id=cid).first():
        cid = f"CIT-{random.randint(100000, 999999)}"
    c = Citizen(citizen_id=cid, name=name, gender=gender, country=country,
                birth_date=birth_date, status=status, notes=notes)
    db.session.add(c)
    db.session.commit()
    log_node_event('Pop-Registry', f"New citizen registered: {name} | ID: {cid} | Status: {status}", 'TX')
    flash(f'Citizen {name} registered with ID {cid}.')
    return redirect(url_for('population'))

@app.route('/population/update/<int:cid>')
@login_required
def population_update(cid):
    c = Citizen.query.get_or_404(cid)
    new_status = request.args.get('status', 'ACTIVE')
    old_status = c.status
    c.status = new_status
    db.session.commit()
    log_node_event('Pop-Registry', f"Citizen {c.name} status changed: {old_status} → {new_status}", 'INFO')
    flash(f'{c.name} status updated to {new_status}.')
    return redirect(url_for('population'))

@app.route('/api/btc-price')
@login_required
def api_btc_price():
    return jsonify({
        'price': round(_btc_state['price'], 2),
        'high': round(_btc_state['high'], 2),
        'low': round(_btc_state['low'], 2),
        'change_pct': _btc_state['change_pct'],
        'open': round(_btc_state['open'], 2),
    })

@app.route('/api/population/stats')
@login_required
def api_population_stats():
    today = datetime.utcnow().date()
    return jsonify({
        'total': Citizen.query.count(),
        'active': Citizen.query.filter_by(status='ACTIVE').count(),
        'migrant': Citizen.query.filter_by(status='MIGRANT').count(),
        'deceased': Citizen.query.filter_by(status='DECEASED').count(),
        'pending': Citizen.query.filter_by(status='PENDING').count(),
        'births_today': Citizen.query.filter(
            Citizen.status == 'ACTIVE',
            db.func.date(Citizen.registered_at) == today
        ).count(),
        'deaths_today': Citizen.query.filter(
            Citizen.status == 'DECEASED',
            db.func.date(Citizen.registered_at) == today
        ).count(),
    })

if __name__ == '__main__':
    with app.app_context():
        init_db()
    threading.Thread(target=_tick_btc_price, daemon=True).start()
    threading.Thread(target=_auto_miner, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
