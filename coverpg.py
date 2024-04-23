from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('coverpg.html')

if __name__ == '__main__':
    app.run(debug = True, port = 5011)