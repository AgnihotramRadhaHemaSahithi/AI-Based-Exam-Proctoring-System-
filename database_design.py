from flask import Flask, request, jsonify 
import psycopg2
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# =============== Database Configuration ====================== # 

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "2525"

def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

    # =============== Database Schema Design ================== #
def create_roles_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    role_name TEXT NOT NULL,
   role_description TEXT NOT NULL);
    """)
    connection.commit()
    cursor.close()
    connection.close()
def create_users_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users(
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
   role_id INT REFERENCES roles(role_id),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    account_status TEXT NOT NULL);
 """)
    connection.commit()
    cursor.close()
    connection.close()
create_roles_table_if_not_exists()
create_users_table()

if __name__ == '__main__':
    app.run(debug=True)