from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import plotly.express
import json

app = Flask(__name__)

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
    cur.execute('''SELECT * FROM expense ORDER BY expense_id LIMIT 5''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_report_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM report ORDER BY report_id LIMIT 5''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_expense_by_day_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT to_char(expense_date, 'Day') AS day_of_week, SUM(expense_amt) AS total_expense 
                   FROM expense 
                   GROUP BY to_char(expense_date, 'Day') 
                   ORDER BY CASE 
                                WHEN to_char(expense_date, 'Day') = 'Monday' THEN 1 
                                WHEN to_char(expense_date, 'Day') = 'Tuesday' THEN 2 
                                WHEN to_char(expense_date, 'Day') = 'Wednesday' THEN 3 
                                WHEN to_char(expense_date, 'Day') = 'Thursday' THEN 4 
                                WHEN to_char(expense_date, 'Day') = 'Friday' THEN 5 
                                WHEN to_char(expense_date, 'Day') = 'Saturday' THEN 6 
                                ELSE 7 
                            END
                ''')
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
def analytics():
    data = fetch_expense_data()
    
    # Process data for plotting
    departments = [row[0] for row in data]
    total_expense = [row[1] for row in data]

    # Create Plotly bar graph
    bar_graph = go.Bar(x=departments, y=total_expense, marker = dict(color = 'rgb(82, 205, 255)'))

    # Plot layout
    layout = go.Layout(xaxis=dict(automargin = False), width = 1100, plot_bgcolor='rgba(0,0,0,0)', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='rgb(244,245,247)', xaxis_gridcolor='rgb(200,200,200)')

    # Combine data and layout into a figure
    graph = go.Figure(data=bar_graph, layout=layout)
    graphJSON = json.dumps(graph, cls = plotly.utils.PlotlyJSONEncoder)

    category_data = fetch_category_data()
    categories = [row[0] for row in category_data]
    category_expenses = [row[1] for row in category_data]

    # Create Plotly doughnut chart
    doughnut_graph = go.Pie(labels=categories, values=category_expenses, hole=0.3)

    # Plot layout for doughnut chart
    doughnut_layout = go.Layout(height = 600, width = 800, legend=dict(orientation="h", x=-0.5, y=1.5))

    doughnut_fig = go.Figure(data=[doughnut_graph], layout=doughnut_layout)

    doughnut_graphJSON = json.dumps(doughnut_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # day_data = fetch_expense_by_day_data()
    # # Process data for plotting
    # days_of_week = [row[0] for row in day_data]
    # total_expense_by_day = [row[1] for row in day_data]
    # dow = [days_of_week[5], days_of_week[1], days_of_week[0], days_of_week[4], days_of_week[2], days_of_week[6], days_of_week[3]]
    # tebd = [total_expense_by_day[5], total_expense_by_day[1], total_expense_by_day[0], total_expense_by_day[4], total_expense_by_day[2], total_expense_by_day[6], total_expense_by_day[3]]
    # daybar_graph = go.Bar(x=dow, y=tebd, marker=dict(color='rgb(82, 205, 255)'))
    # daygraph = go.Figure(data=[daybar_graph], layout=layout)
    # daygraphJSON = json.dumps(daygraph, cls=plotly.utils.PlotlyJSONEncoder)
    pname = get_user_name()

    return render_template('analytics.html', graphJSON = graphJSON, doughnut_graphJSON=doughnut_graphJSON, pname = pname)

if __name__ == '__main__':
    app.run(debug = True, port = 5002)