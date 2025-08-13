#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import webbrowser
import threading
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/time')
def get_time():
    return jsonify({'time': time.strftime('%H:%M:%S')})

def open_browser():
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("🧘 Starting Serenity Web GUI...")
    print("🌐 Opening browser at http://127.0.0.1:5000")
    
    # Open browser in a separate thread
    threading.Timer(1.5, open_browser).start()
    
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)