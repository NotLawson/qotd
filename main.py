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
        if cursor.fetchone():
            return jsonify({"error": "Quote already exists"}), 400
        
        now = datetime.datetime.now(tz=pytz.timezone("Australia/Brisbane"))
        cursor.execute("INSERT INTO quotes (quote, person, created_at) VALUES (%s, %s, %s)", (quote, person, now))
        return jsonify({"message": "Quote added successfully"}), 201
    
    if request.method == 'GET':
        start = datetime.datetime.now(tz=pytz.timezone("Australia/Brisbane")).replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("SELECT * FROM quotes WHERE created_at > %s ORDER BY votes DESC", (start,))
        quotes = cursor.fetchall()
        return jsonify({"quotes":quotes}), 200
    
@app.route('/api/quote/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def quote(id):
    if request.method == 'GET':
        cursor.execute("SELECT * FROM quotes WHERE id = %s", (id,))
        quote = cursor.fetchone()
        if not quote:
            return jsonify({"error": "Quote not found"}), 404
        return jsonify({"quote": quote}), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        quote = data.get("quote")
        person = data.get("person")
        if not quote or not person:
            return jsonify({"error": "Quote and person are required"}), 400
        cursor.execute("UPDATE quotes SET quote = %s, person = %s WHERE id = %s", (quote, person, id))
        return jsonify({"message": "Quote updated successfully"}), 200
    
    if request.method == 'DELETE':
        cursor.execute("DELETE FROM quotes WHERE id = %s", (id,))
        return jsonify({"message": "Quote deleted successfully"}), 200
    
@app.route('/api/vote/<int:id>', methods=['POST', 'DELETE'])
def vote(id):
    if request.method == 'POST':
        cursor.execute("UPDATE quotes SET votes = votes + 1 WHERE id = %s", (id,))
        return jsonify({"message": "Vote added successfully"}), 200
    
    if request.method == 'DELETE':
        cursor.execute("UPDATE quotes SET votes = votes - 1 WHERE id = %s", (id,))
        return jsonify({"message": "Vote removed successfully"}), 200

@app.route('/api/all', methods=['GET'])
def all_quotes():
    cursor.execute("SELECT * FROM quotes ORDER BY created_at DESC")
    quotes = cursor.fetchall()
    return jsonify({"quotes": quotes}), 200

@app.route('/api/random', methods=['GET'])
def random_quote():
    cursor.execute("SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1")
    quote = cursor.fetchone()
    if not quote:
        return jsonify({"error": "No quotes found"}), 404
    return jsonify({"quote": quote}), 200

@app.route('/api/quotesforperson/<string:person>', methods=['GET'])
def quotes_for_person(person):
    cursor.execute("SELECT * FROM quotes WHERE person = %s", (person,))
    quotes = cursor.fetchall()
    if not quotes:
        return jsonify({"error": "No quotes found for this person"}), 404
    return jsonify({"quotes": quotes}), 200

app.run(debug=True, host="0.0.0.0", port=8080)