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
        ORDER BY r.report_date DESC LIMIT 3
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

def fetch_category_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT expense_ctgry, SUM(expense_amt) AS total_expense FROM expense GROUP BY expense_ctgry''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_expense_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM expense ORDER BY expense_date DESC LIMIT 5''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_report_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM report ORDER BY report_date DESC LIMIT 5''')
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
    all_approval_data = fetch_all_approval_data()
    all_expense_data = fetch_all_expense_data()
    data = fetch_expense_data()
    all_report_data = fetch_all_report_data()
    # Process data for plotting
    departments = [row[0] for row in data]
    total_expense = [row[1] for row in data]

    # Create Plotly bar graph
    bar_graph = go.Bar(x=departments, y=total_expense, marker = dict(color = 'rgb(82, 205, 255)'))

    # Plot layout
    layout = go.Layout(xaxis=dict(automargin = False), width = 720, plot_bgcolor='rgba(0,0,0,0)', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='rgb(244,245,247)', xaxis_gridcolor='rgb(200,200,200)')

    # Combine data and layout into a figure
    graph = go.Figure(data=bar_graph, layout=layout)
    graphJSON = json.dumps(graph, cls = plotly.utils.PlotlyJSONEncoder)

    category_data = fetch_category_data()
    categories = [row[0] for row in category_data]
    category_expenses = [row[1] for row in category_data]

    # Create Plotly doughnut chart
    doughnut_graph = go.Pie(labels=categories, values=category_expenses, hole=0.3)

    # Plot layout for doughnut chart
    doughnut_layout = go.Layout(height = 400, width = 300, legend=dict(orientation="h", x=-0.5, y=2))

    doughnut_fig = go.Figure(data=[doughnut_graph], layout=doughnut_layout)

    doughnut_graphJSON = json.dumps(doughnut_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', pname = pname, graphJSON = graphJSON, doughnut_graphJSON=doughnut_graphJSON, all_expense_data=all_expense_data, all_report_data = all_report_data, all_approval_data = all_approval_data)

if __name__ == '__main__':
    app.run(debug = True, port = 5001)