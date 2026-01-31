from flask import Flask
import os
import mysql.connector

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask + Docker + Jenkins 🚀"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

