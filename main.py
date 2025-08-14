from flask import Flask, request, jsonify
import sqlite3
from utils import is_valid_email, slow_hash_password

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('users.db')
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email'}), 400

    hashed_pw = slow_hash_password(password)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_pw))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()


    if row and slow_hash_password(password) == row[0]:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users')
def list_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT username, email FROM users")
    users = cur.fetchall()
    conn.close()

    return jsonify({'users': users})

@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    username = data['username']
    current_password = data['current_password']
    new_password = data['new_password']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    
    if slow_hash_password(current_password) != row[0]:
        conn.close()
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    new_hashed_pw = slow_hash_password(new_password)
    cur.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed_pw, username))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Password updated successfully'})

if __name__ == '__main__':
    app.run(debug=True) 