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
    return redirect(url_for('viewreports'))

@app.route('/decline_report/<int:report_id>')
def decline_report(report_id):
    update_approval_status(report_id, "Declined")
    return redirect(url_for('viewreports'))

def fetch_all_expense_data(report_id):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM expense WHERE report_id = %s ORDER BY expense_id''', (report_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_report_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT r.report_id, r.report_name, r.report_date, r.report_dept, r.user_id, a.status
        FROM report r
        JOIN approval a ON r.report_id = a.report_id
        ORDER BY r.report_date DESC''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_report_data(report_id):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM report WHERE report_id = %s''', (report_id,))
    data = cur.fetchone()  # Assuming report_id is unique, fetch one row
    cur.close()
    conn.close()
    return data

@app.route('/')
def viewreports():
    all_report_data = fetch_all_report_data()
    pname = get_user_name()
    return render_template('viewreports.html', all_report_data = all_report_data, pname = pname)

@app.route('/download_report/<int:report_id>')
def download_report(report_id):
    report_data = fetch_report_data(report_id)  # Replace this with your function to fetch report data
    expense_data = fetch_all_expense_data(report_id)  # Replace this with your function to fetch expense data

    # Create a CSV string with report data and expense data
    csv_data = "Report ID, Report Name, Report Date, Report Department, User ID\n"
    csv_data += ",".join(map(str, report_data)) + "\n\n"
    csv_data += "Expense ID, Report ID, Expense Date, Expense Vendor, Expense Category, Expense Pay, Expense Amount\n"
    for expense in expense_data:
        csv_data += ",".join(map(str, expense)) + "\n"

    # Create a response with the CSV data
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=report_{}.csv".format(report_id)
    response.headers["Content-type"] = "text/csv"

    return response

if __name__ == '__main__':
    app.run(debug = True, port = 5003)