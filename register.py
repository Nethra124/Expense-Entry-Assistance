from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)

def create_user(firstname, lastname, mailid, department, password, repassword):
    if password == repassword:
        conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute('''INSERT INTO users (first_name, last_name, email, department, pw) VALUES (%s, %s, %s, %s, %s)''', (firstname, lastname, mailid, department, password))
        conn.commit()
        cur.close()
        conn.close()
        return True
    else:
        return False

@app.route('/create', methods=['POST'])
def create():
    firstname = request.form['fname']
    lastname = request.form['lname']
    mailid = request.form['mail']
    department = request.form['dept']
    password = request.form['pw']
    repassword = request.form['rpw']

    # Create the report
    ans = create_user(firstname, lastname, mailid, department, password, repassword)
    if ans:
        return redirect('http://127.0.0.1:5008')
    else:
        error_message = "Passwords do not match. Please try again."
        return render_template('register.html', error=error_message)

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
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug = True, port = 5007)