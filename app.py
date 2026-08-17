from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash
import sqlite3
import re
import secrets
import string

app = Flask(__name__)

DATABASE = "password_history.db"


# DATABASE

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# PASSWORD ANALYZER 

COMMON_PASSWORDS = {
    "password",
    "password123",
    "123456",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "welcome",
    "letmein",
    "abc123"
}


def analyze_password(password):

    score = 0
    checks = []

    # Length

    length_ok = len(password) >= 12

    if length_ok:
        score += 2

    checks.append({
        "name": "At least 12 characters",
        "passed": length_ok
    })

    # Uppercase

    uppercase_ok = bool(re.search(r"[A-Z]", password))

    if uppercase_ok:
        score += 1

    checks.append({
        "name": "Uppercase letter",
        "passed": uppercase_ok
    })

    # Lowercase

    lowercase_ok = bool(re.search(r"[a-z]", password))

    if lowercase_ok:
        score += 1

    checks.append({
        "name": "Lowercase letter",
        "passed": lowercase_ok
    })

    # Number

    number_ok = bool(re.search(r"[0-9]", password))

    if number_ok:
        score += 1

    checks.append({
        "name": "Number",
        "passed": number_ok
    })

    # Special character

    special_ok = bool(re.search(r"[^A-Za-z0-9]", password))

    if special_ok:
        score += 1

    checks.append({
        "name": "Special character",
        "passed": special_ok
    })

    # Common password

    common_ok = password.lower() not in COMMON_PASSWORDS

    if common_ok:
        score += 1

    checks.append({
        "name": "Not a common password",
        "passed": common_ok
    })

    # Repeated characters

    repeated_ok = not bool(re.search(r"(.)\1\1", password))

    if repeated_ok:
        score += 1

    checks.append({
        "name": "No repeated characters",
        "passed": repeated_ok
    })

    # Strength

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    elif score <= 6:
        strength = "Strong"
    else:
        strength = "Very Strong"

    # Suggestions
    suggestions = []

    if not length_ok:
        suggestions.append("Use at least 12 characters.")

    if not uppercase_ok:
        suggestions.append("Add uppercase letters.")

    if not lowercase_ok:
        suggestions.append("Add lowercase letters.")

    if not number_ok:
        suggestions.append("Add numbers.")

    if not special_ok:
        suggestions.append("Add special characters.")

    if not common_ok:
        suggestions.append("Avoid commonly used passwords.")

    if not repeated_ok:
        suggestions.append("Avoid repeated characters.")

    if not suggestions:
        suggestions.append("Excellent! Your password meets the basic security requirements.")

    return {
        "score": score,
        "strength": strength,
        "checks": checks,
        "suggestions": suggestions
    }


# PASSWORD GENERATOR 

def generate_strong_password():

    characters = (
        string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits +
        string.punctuation
    )

    while True:

        password = ''.join(
            secrets.choice(characters)
            for _ in range(16)
        )

        if (
            re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r"[^A-Za-z0-9]", password)
        ):
            return password


# ROUTES 

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    password = data.get("password", "")

    if not password:
        return jsonify({
            "error": "Please enter a password."
        }), 400

    result = analyze_password(password)

    return jsonify(result)


@app.route("/generate", methods=["GET"])
def generate():

    password = generate_strong_password()

    return jsonify({
        "password": password
    })


# SAVE HASH 

@app.route("/save-password", methods=["POST"])
def save_password():

    data = request.get_json()

    password = data.get("password", "")

    if not password:
        return jsonify({
            "error": "Password cannot be empty."
        }), 400

    # Store only the hash, never the actual password
    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "INSERT INTO password_history (password_hash) VALUES (?)",
        (password_hash,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Password hash stored securely."
    })


# START SERVER 

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )