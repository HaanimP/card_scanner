from flask import Flask, request, jsonify
import mysql.connector
from cryptography.fernet import Fernet

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="boytok4k7nshaqdvtymn-mysql.services.clever-cloud.com",
        user="ukmdmosti9gt4lav",
        password="G5dhxCDE4g54NB9OsbLW",
        database="boytok4k7nshaqdvtymn"
    )

# Load encryption key
def load_key():
    return open("secret.key", "rb").read()

# Encrypt QR data
def encrypt_data(data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

# Decrypt QR data
def decrypt_data(encrypted_data):
    key = load_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

# Root route to avoid 404 on the main page
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the QR Data API'}), 200

# Handle favicon.ico requests to prevent 404 errors
# @app.route('/favicon.ico')
# def favicon():
#     return '', 204  # No Content

# Route to store encrypted QR code data
@app.route('/store_qr_data', methods=['POST'])
def store_qr_data():
    data = request.json.get('qr_data')
    if not data:
        return jsonify({'error': 'No QR data provided'}), 400
    
    encrypted_data = encrypt_data(data)

    # Insert into MySQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (qr_code_data) VALUES (%s)", (encrypted_data,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Data stored successfully'}), 200

# Route to get decrypted QR code data
@app.route('/get_qr_data/<int:user_id>', methods=['GET'])
def get_qr_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT qr_code_data FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        decrypted_data = decrypt_data(result[0])
        return jsonify({'qr_data': decrypted_data}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
