from flask import Flask, render_template, request, redirect, url_for, make_response
import psycopg2
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import plotly.express
import json

app = Flask(__name__)

def get_user_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_sessions ORDER BY created_at DESC LIMIT 1")
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

# Function to update the status in the approval table
def update_approval_status(report_id, status):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("UPDATE approval SET status = %s WHERE report_id = %s", (status, report_id))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/approve_report/<int:report_id>')
def approve_report(report_id):
    update_approval_status(report_id, "Approved")
    return redirect(url_for('reqapprovals'))

@app.route('/decline_report/<int:report_id>')
def decline_report(report_id):
    update_approval_status(report_id, "Declined")
    return redirect(url_for('reqapprovals'))

def fetch_all_approval_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''
        SELECT a.report_id, r.report_name, r.report_date, r.report_dept, a.status
        FROM approval a
        JOIN report r ON a.report_id = r.report_id
        WHERE a.status = 'Pending'
        ORDER BY r.report_date DESC
    ''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.route('/')
def reqapprovals():
    all_approval_data = fetch_all_approval_data()
    pname = get_user_name()
    return render_template('reqapprovals.html', all_approval_data = all_approval_data, pname = pname)

if __name__ == '__main__':
    app.run(debug = True, port = 5004)
