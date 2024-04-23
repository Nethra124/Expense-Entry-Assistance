from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

def check_user(mailid, mode, password):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND umode = %s AND pw = %s", (mailid, mode, password))
    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if user:
        return True
    else:
        return False

def get_user_name(mailid):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT CONCAT(first_name, ' ', last_name) FROM users WHERE email = %s", (mailid,))
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

def store_user_name(mailid, name):
    # Store user's name in a database table
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("INSERT INTO user_sessions (email, name) VALUES (%s, %s)", (mailid, name))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/create', methods=['POST'])
def create():
    mailid = request.form['mail']
    mode = request.form['mode']
    password = request.form['pw']

    # Validate user credentials
    user_exists = check_user(mailid, mode, password)
    if user_exists:
        access_token = create_access_token(identity=mailid)
        store_user_name(mailid, get_user_name(mailid))
        if mode == "Admin":
            return redirect('http://127.0.0.1:5001') # admin dashboard
        else:
            return redirect('http://127.0.0.1:5012') # user dashboard
    else:
        # return {'error': 'Invalid credentials'}, 401
        error_message = "Invalid credentials. Please try again."
        return render_template('login.html', error=error_message)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return {'user': current_user}, 200

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'error': 'Missing Authorization Header'}), 401

@jwt.invalid_token_loader
def invalid_token_response(callback):
    return jsonify({'error': 'Invalid JWT Token'}), 422

@jwt.expired_token_loader
def expired_token_response(callback):
    return jsonify({'error': 'Expired JWT Token'}), 401

@app.route('/')
def login():
    error_message = request.args.get('error')
    return render_template('login.html', error = error_message)

if __name__ == '__main__':
    app.run(debug = True, port = 5008)