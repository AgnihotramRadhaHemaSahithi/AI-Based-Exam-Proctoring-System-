from flask import Flask, request, jsonify 
import psycopg2
from flask_bcrypt import Bcrypt
import jwt 
import datetime

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
# Secret Key
SECRET_KEY = "this is my secret key this is my secret key!!"

# JWT FUNCTIONS
def create_jwt(user_id, role_id):
    payload = {
        "user_id": user_id,
        "role_id":role_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
def verify_jwt(token):
    try:
        data=jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        return data
    except:
        return None

# SIGNUP API
@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password =data.get("password")


    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    DEFAULT_ROLE_ID = 2 #STUDENT 
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            INSERT INTO users (username, email, password_hash ,role_id,account_status)
            VALUES (%s, %s, %s,%s,%s)
            RETURNING user_id
        """, (username, email, hashed_password, DEFAULT_ROLE_ID,"ACTIVE" ))
    user_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()
    token = create_jwt(user_id,DEFAULT_ROLE_ID)
    return jsonify({
            "message": "Signup successful",
            "token": token
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
   

    if not email or not password:
        return jsonify({"error": "All fields required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT user_id, username, password_hash ,role_id
        FROM users
        WHERE email = %s
    """, (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id, username, hashed_password ,role = user

    # Verify password
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"error": "Invalid password"}), 401

    token = create_jwt(user_id,role)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role":role
        }
    }), 200
@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    token = request.headers.get("Authorization")
    if token :
        decoded = verify_jwt(token)
        if decoded is None:
            return jsonify({'error': 'token invalid/expired'}), 401
        else:
             if decoded ['role_id']  == 2 :
               return jsonify({
                'message':'Role matched: access granted',
                'user_id': decoded['user_id'],
                'role_id': decoded['role_id']
                }), 200

             else:
                 return jsonify ({'error':'forbidden  acccess denied'}),403
    else:
        return jsonify({'error': 'token missing '}), 401
@app.route('/examiner_dashboard', methods=['GET'])
def examiner_dashboard():
    token = request.headers.get("Authorization")
    if token :
        decoded = verify_jwt(token)
        if decoded is None:
            return jsonify({'error': 'token invalid/expired'}), 401
        else:
             if decoded ['role_id']  == 3 :
               return jsonify({
                'message':'Role matched: access granted',
                'user_id': decoded['user_id'],
                'role_id': decoded['role_id']
                }), 200

             else:
                 return jsonify ({'error':'forbidden  acccess denied'}),403
    else:
        return jsonify({'error': 'token missing '}), 401
@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    token = request.headers.get("Authorization")
    if token :
        decoded = verify_jwt(token)
        if decoded is None:
            return jsonify({'error': 'token invalid/expired'}), 401
        else:
             if decoded ['role_id']  == 1 :
               return jsonify({
                'message':'Role matched: access granted',
                'user_id': decoded['user_id'],
                'role_id': decoded['role_id']
                }), 200

             else:
                 return jsonify ({'error':'forbidden  acccess denied'}),403
    else:
        return jsonify({'error': 'token missing '}), 401


if __name__ == '__main__':
    app.run(debug=True)