from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import plotly.express
import json

app = Flask(__name__)

def fetch_all_approval_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''
        SELECT a.report_id, r.report_name, r.report_date, r.report_dept, a.status
        FROM approval a
        JOIN report r ON a.report_id = r.report_id
        WHERE a.status = 'Pending'
        ORDER BY a.report_id LIMIT 3
    ''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_expense_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT report_dept, SUM(expense_amt) AS total_expense FROM report 
                   JOIN expense ON report.report_id = expense.report_id 
                   GROUP BY report_dept''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_category_data(user_name):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()

    # Retrieve the user_id based on the user_name
    cur.execute("SELECT user_id FROM users WHERE CONCAT(first_name, ' ', last_name) = %s", (user_name,))
    user_id = cur.fetchone()[0]

    # Fetch category data for expenses belonging to the specified user
    cur.execute("""
        SELECT e.expense_ctgry, SUM(e.expense_amt) AS total_expense
        FROM expense e
        JOIN report r ON e.report_id = r.report_id
        WHERE r.user_id = %s
        GROUP BY e.expense_ctgry
    """, (user_id,))
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data

def fetch_all_expense_data(user_name):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE CONCAT(first_name, ' ', last_name) = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("""
        SELECT e.*
        FROM expense e
        JOIN report r ON e.report_id = r.report_id
        WHERE r.user_id = %s
        ORDER BY e.expense_date DESC LIMIT 5
    """, (user_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_report_data(user_name):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE CONCAT(first_name, ' ', last_name) = %s", (user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("""
        SELECT r.report_id, r.report_name, r.report_date, r.report_dept, a.status
        FROM report r
        JOIN approval a ON r.report_id = a.report_id
        WHERE r.user_id = %s AND a.status = 'Pending'
        ORDER BY r.report_id
    """, (user_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_user_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_sessions ORDER BY created_at DESC LIMIT 1")
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

@app.route('/')
def index():
    pname = get_user_name()
    # all_approval_data = fetch_all_approval_data()
    all_expense_data = fetch_all_expense_data(pname)
    user_name = get_user_name()
    all_report_data = fetch_all_report_data(user_name)
    category_data = fetch_category_data(pname)
    categories = [row[0] for row in category_data]
    category_expenses = [row[1] for row in category_data]
    # Create Plotly doughnut chart
    doughnut_graph = go.Pie(labels=categories, values=category_expenses, hole=0.3)
    # Plot layout for doughnut chart
    doughnut_layout = go.Layout(height = 400, width = 760, legend=dict(orientation="h", x=-0.5, y=2))
    doughnut_fig = go.Figure(data=[doughnut_graph], layout=doughnut_layout)
    doughnut_graphJSON = json.dumps(doughnut_fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Process data for plotting
    return render_template('pendingreports_user.html', pname = pname, all_report_data = all_report_data, all_expense_data = all_expense_data, doughnut_graphJSON=doughnut_graphJSON)

if __name__ == '__main__':
    app.run(debug = True, port = 5013)