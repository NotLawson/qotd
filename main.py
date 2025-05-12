# QOTD
import os, sys, time, random, json, datetime, pytz
time.sleep(5) # Wait for postgres to start

import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

connection = psycopg2.connect(
    host="postgres",
    database="qotd",
    user="postgres",
    password="password",
    port="5432"
)
connection.autocommit = True
cursor = connection.cursor()


cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            quote TEXT NOT NULL,
            person TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            votes INT DEFAULT 0
        )
    ''')

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# API
@app.route('/api/qotd', methods=['GET', 'POST'])
def qotd():
    if request.method == 'POST':
        data = request.get_json()
        quote = data.get("quote")
        person = data.get("person")
        if not quote or not person:
            return jsonify({"error": "Quote and person are required"}), 400
        cursor.execute("SELECT id FROM quotes where quote = %s and person = %s", (quote, person))
        if len(cursor.fetchone())!=0:
            return jsonify({"error": "Quote already exists"}), 400
        
        now = datetime.datetime.now(tz=pytz.timezone("Australia/Brisbane"))
        cursor.execute("INSERT INTO quotes (quote, person, created_at) VALUES (%s, %s, %s)", (quote, person, now))
        return jsonify({"message": "Quote added successfully"}), 201
    
    if request.method == 'GET':
        start = datetime.datetime.now(tz=pytz.timezone("Australia/Brisbane")).replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("SELECT * FROM quotes WHERE created_at > %s ORDER BY votes DESC", (start,))
        quotes = cursor.fetchall()
        return jsonify({"quotes":quotes}), 200
    

app.run(debug=True, port=8080)