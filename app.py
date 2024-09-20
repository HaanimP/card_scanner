from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database connection parameters
DB_HOST = os.getenv("host")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_NAME = os.getenv("database")


# Create database connection
def get_db_connection():
    try:
        port = int(os.getenv("PORT", 3306))  # Ensure port is an integer
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=port
        )
        if conn.is_connected():
            print("Database connection established.")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/')
def home():
    return "Server is running"

@app.route('/store_qr_data', methods=['POST'])
def store_qr_data():
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, department)
            VALUES (%s, %s, %s)
        """, (data['first_name'], data['last_name'], data['department']))

        conn.commit()
        return jsonify({"message": "QR data stored successfully"}), 200
    except Error as e:
        return jsonify({"message": f"Error storing QR data: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
