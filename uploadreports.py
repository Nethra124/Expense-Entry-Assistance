from flask import Flask, render_template, request, redirect, url_for
import csv
import io
import psycopg2

app = Flask(__name__)

def get_user_name():
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT name FROM user_sessions ORDER BY created_at DESC LIMIT 1")
    pname = cur.fetchone()
    cur.close()
    conn.close()
    return pname[0] if pname else 'None'

# Function to parse and insert report details from CSV file into database
def insert_report_and_expense_data(csv_data):
    conn = psycopg2.connect(database="expense_entry", user="postgres", password="nethra14", host="localhost", port="5432")
    cur = conn.cursor()
    csv_reader = csv.reader(io.StringIO(csv_data))
    try:
        # Skip header rows for report and expense tables
        next(csv_reader)  # Skip report table header row
        for row in csv_reader:
            report_id, report_name, report_date, report_dept, user_id = row[:5]  # Assuming first 4 columns are report details
            cur.execute("INSERT INTO report (report_id, report_name, report_date, report_dept, user_id) VALUES (%s, %s, %s, %s, %s)", (report_id, report_name, report_date, report_dept, user_id))
            break  # Only insert the first row (assuming it's the report details)
        cur.execute('''INSERT INTO approval (report_id, status) VALUES (%s, %s)''', (report_id, 'Pending'))
        next(csv_reader)
        next(csv_reader)
        # Iterate over remaining rows to insert data
        for row in csv_reader:
            expense_id, report_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt = row
            cur.execute("INSERT INTO expense (expense_id, report_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt) VALUES (%s, %s, %s, %s, %s, %s, %s)", (expense_id, report_id, expense_date, expense_vendor, expense_ctgry, expense_pay, expense_amt))
        
        conn.commit()
        return True
    except Exception as e:
        print("Error:", e)
        conn.rollback()  # Rollback changes if there's an error
        return False  # Return False if there was an error during insertion
    finally:
        cur.close()
        conn.close()
    cur.close()
    conn.close()

@app.route('/')
def insert():
    pname = get_user_name()
    return render_template('uploadreports.html', pname = pname)

@app.route('/upload', methods=['GET', 'POST'])
def uploadreports():
    pname = get_user_name()
    message = None
    if request.method == 'POST':
        report_file = request.files['report_file']
        if report_file.filename == '':
            message = "No file selected."
        elif report_file:
            csv_data = report_file.read().decode('utf-8')
            success = insert_report_and_expense_data(csv_data)
            if success:
                message = "Report data uploaded successfully."
            else:
                message = "Failed to upload report data."
    return render_template('uploadreports.html', message=message, pname = pname)

if __name__ == '__main__':
    app.run(debug=True, port=5006)
