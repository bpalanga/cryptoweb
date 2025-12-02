#!/usr/bin/env python3
"""
Quick server test - Run this to verify Flask is working without SSL
"""
from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'test-key'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/test')
def test():
    return "<h1>Test Server Works!</h1>"

if __name__ == '__main__':
    print("=" * 60)
    print("TEST SERVER - HTTP ONLY")
    print("=" * 60)
    print("Open browser to: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)

