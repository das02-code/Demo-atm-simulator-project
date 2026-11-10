from flask import Flask, render_template, request, jsonify, session
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = 'atm_secret_key_2024'
init_db()

def get_db():
    conn = sqlite3.connect('atm.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Home Page ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- Login (PIN Verification) ----------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    account_no = data.get('account_no', '').strip()
    pin = data.get('pin', '').strip()

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE account_no = ? AND pin = ?",
        (account_no, pin)
    ).fetchone()
    conn.close()

    if user:
        session['account_no'] = account_no
        return jsonify({
            "success": True,
            "name": user['name'],
            "account_no": account_no
        })
    return jsonify({"success": False, "message": "Invalid Account Number or PIN!"})

# ---------- Dashboard (after login) ----------
@app.route('/dashboard')
def dashboard():
    if 'account_no' not in session:
        return render_template('index.html')
    return render_template('dashboard.html')

# ---------- Get Balance ----------
@app.route('/api/balance')
def balance():
    if 'account_no' not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE account_no = ?",
        (session['account_no'],)
    ).fetchone()
    conn.close()

    return jsonify({
        "success": True,
        "name": user['name'],
        "account_no": user['account_no'],
        "balance": user['balance']
    })

# ---------- Deposit ----------
@app.route('/api/deposit', methods=['POST'])
def deposit():
    if 'account_no' not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    amount = float(request.get_json().get('amount', 0))
    if amount <= 0:
        return jsonify({"success": False, "message": "Enter a valid amount!"})

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE account_no = ?",
        (session['account_no'],)
    ).fetchone()

    new_balance = user['balance'] + amount
    conn.execute("UPDATE users SET balance = ? WHERE account_no = ?",
                 (new_balance, session['account_no']))
    conn.execute(
        "INSERT INTO transactions (account_no, type, amount, balance_after) VALUES (?, ?, ?, ?)",
        (session['account_no'], 'DEPOSIT', amount, new_balance)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "balance": new_balance, "message": f"₹{amount} deposited successfully!"})

# ---------- Withdraw ----------
@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    if 'account_no' not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    amount = float(request.get_json().get('amount', 0))
    if amount <= 0:
        return jsonify({"success": False, "message": "Enter a valid amount!"})

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE account_no = ?",
        (session['account_no'],)
    ).fetchone()

    if amount > user['balance']:
        conn.close()
        return jsonify({"success": False, "message": "Insufficient Balance!"})

    new_balance = user['balance'] - amount
    conn.execute("UPDATE users SET balance = ? WHERE account_no = ?",
                 (new_balance, session['account_no']))
    conn.execute(
        "INSERT INTO transactions (account_no, type, amount, balance_after) VALUES (?, ?, ?, ?)",
        (session['account_no'], 'WITHDRAW', amount, new_balance)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "balance": new_balance, "message": f"₹{amount} withdrawn successfully!"})

# ---------- Mini Statement ----------
@app.route('/api/statement')
def statement():
    if 'account_no' not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    conn = get_db()
    rows = conn.execute(
        "SELECT type, amount, balance_after, timestamp FROM transactions WHERE account_no = ? ORDER BY id DESC LIMIT 10",
        (session['account_no'],)
    ).fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "transactions": [dict(r) for r in rows]
    })

# ---------- Logout ----------
@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)