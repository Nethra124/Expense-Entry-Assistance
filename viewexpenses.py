from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
import base64
import psycopg2
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import plotly.express
import json
import io

app = Flask(__name__)

def get_image_from_database(receipt_id):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT bill FROM receipts WHERE receipt_id = %s", (receipt_id, ))
    image_data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return image_data

@app.route('/display_image/<int:report_id>/<int:expense_id>')
def display_image(report_id, expense_id):
    image_data = get_image_from_database(report_id, expense_id)
    # Assuming the image data is stored as bytes in the database
    # Convert the bytes to base64 encoding
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    return encoded_image

@app.route('/download_receipt/<int:receipt_id>/<int:report_id>')
def download_receipt(receipt_id, report_id):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS row_count FROM receipts")
    row_count = cur.fetchone()[0]
    if row_count == 1:
        receipt_id = 1
    elif row_count > 1:
        receipt_id = receipt_id
    filename = 'receipt_{}.png'.format(receipt_id)
    receipt_data = "D:/SAP_Final/{}".format(filename)
    return send_file(
        receipt_data,
        as_attachment=True,
        download_name='receipt_image.png',  # Adjust filename as needed
        mimetype='image/png'  # Adjust mimetype based on the type of receipt file
)

def get_user_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_sessions ORDER BY created_at DESC LIMIT 1")
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

def fetch_all_receipt_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''
        SELECT
            r.receipt_id,
            r.report_id,
            e.expense_date AS receipt_date,
            e.expense_vendor AS receipt_vendor,
            e.expense_amt AS receipt_amount
        FROM
            receipts r
        JOIN
            expense e ON r.expense_id = e.expense_id
        ORDER BY e.expense_date DESC
    ''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def fetch_all_expense_data():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute('''SELECT * FROM expense''')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.route('/')
def viewexpenses():
    all_expense_data = fetch_all_expense_data()
    all_receipt_data = fetch_all_receipt_data()
    pname = get_user_name()
    return render_template('viewexpenses.html', all_expense_data = all_expense_data, pname = pname, all_receipt_data = all_receipt_data)

if __name__ == '__main__':
    app.run(debug = True, port = 5005)