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
def create_users_table_if_not_exists():
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
def create_exams_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS exams(
    exam_id SERIAL PRIMARY KEY,
    exam_title TEXT NOT NULL,
    academic_year INT NOT NULL,
    exam_date TIMESTAMP NOT NULL,
    exam_duration INT NOT NULL,
    exam_conducted_by INT REFERENCES users(user_id),
    exam_status TEXT NOT NULL);
    """)
    connection.commit()
    cursor.close()
    connection.close()
def create_questions_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS questions(
    question_id SERIAL PRIMARY KEY,
    exam_id INT REFERENCES exams(exam_id),
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL,
    marks INT NOT NULL );
    """)
    connection.commit()
    cursor.close()
    connection.close()
def create_monitoring_logs_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS monitoring_logs(
    log_id SERIAL PRIMARY KEY,
    exam_id INT REFERENCES exams(exam_id),
    student_id INT REFERENCES users(user_id),
    event_type TEXT NOT NULL,
    severity_level TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_taken TEXT NULL);
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_roles_table_if_not_exists()
create_users_table_if_not_exists()
create_exams_table_if_not_exists()
create_questions_table_if_not_exists()
create_monitoring_logs_table_if_not_exists()

if __name__ == '__main__':
    app.run(debug=True)