# flask app
from flask import Flask, render_template, request, redirect, url_for
import psycopg2 
import os

app = Flask(__name__)

def get_dept_name(user_name):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE CONCAT(first_name, ' ', last_name) = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("SELECT department FROM users WHERE user_id = %s", (user_id, ))
    dept = cur.fetchone()[0]
    cur.close()
    conn.close()
    return dept if dept else 'None'

def create_report(report_name, report_date, report_dept, user_name):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE CONCAT(first_name, ' ', last_name) = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute('''SELECT MAX(report_id) FROM report''')
    highest_report_id = cur.fetchone()[0] + 1
    cur.execute("SELECT department FROM users WHERE user_id = %s", (user_id, ))
    dept = cur.fetchone()[0]
    cur.execute('''INSERT INTO report (report_id, report_name, report_date, report_dept, user_id) VALUES (%s, %s, %s, %s, %s)''', (highest_report_id, report_name, report_date, dept, user_id))
    cur.execute('''SELECT MAX(report_id) FROM report''')
    highest_report_id = cur.fetchone()[0]
    cur.execute('''INSERT INTO approval (report_id, status) VALUES (%s, %s)''', (highest_report_id, 'Pending'))
    conn.commit()
    cur.close()
    conn.close()

def create_expense(report_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT MAX(expense_id) FROM expense")
    expense_id = cur.fetchone()[0]+1
    cur.execute('''INSERT INTO expense (report_id, expense_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (report_id, expense_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt))
    conn.commit()
    cur.close()
    conn.close()
    # return "Expense inserted successfully!"

def create_receipt(report_id, bill):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT MAX(expense_id) FROM expense")
    expense_id = cur.fetchone()[0]
    cur.execute('''INSERT INTO receipts (report_id, expense_id, bill) VALUES (%s, %s, %s)''', (report_id, expense_id, bill))
    conn.commit()
    cur.close()
    conn.close()

def get_user_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_sessions ORDER BY created_at DESC LIMIT 1")
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

def get_report_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT report_name FROM report ORDER BY report_id DESC LIMIT 1")
    rname = cur.fetchone()
    cur.close()
    conn.close()
    return rname[0] if rname else 'None'

@app.route('/')
def insert_user():
    pname = get_user_name()
    deptname = get_dept_name(pname)
    return render_template('insert_user.html', pname = pname, deptname = deptname)

@app.route('/insertexpense_user')
def insertexpense_user():
    pname = get_user_name()
    rname = get_report_name()
    return render_template('insertexpense_user.html', pname = pname, rname = rname)

@app.route('/create', methods=['POST'])
def create():
    report_name = request.form['repname']
    report_date = request.form['repdate']
    # report_ctgry = request.form['purpose']
    report_dept = request.form['dept']
    pname = get_user_name()

    # Create the report
    create_report(report_name, report_date, report_dept, pname)

    return redirect(url_for('insertexpense_user'))

@app.route('/create_expenses', methods=['POST'])
def create_expenses():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT report_id FROM report ORDER BY report_id DESC LIMIT 1''')
    report_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    expense_date = request.form['date']
    expense_vendor = request.form['vendor']
    expense_ctgry = request.form['etype']
    expense_pay = request.form['payment']
    expense_amt = request.form['amt']
    expense_bill = request.files['bill']

    # Create the expense record
    create_expense(report_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt)
    if expense_bill:
        conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT MAX(receipt_id) FROM receipts")
        receipt_id = cur.fetchone()[0]
        if receipt_id is None:
            receipt_id = 1
        else:
            receipt_id += 1
        conn.commit()
        cur.close()
        conn.close()
        filename = 'receipt_{}.png'.format(receipt_id)
        expense_bill.save(os.path.join('D:\SAP_Final', filename))
        another_bill = expense_bill.read()
        create_receipt(report_id, another_bill)

    # Redirect to some success page or wherever necessary
    return redirect(url_for('insertexpense_user'))

if __name__ == "__main__":
    app.run(debug=True, port = 5009)