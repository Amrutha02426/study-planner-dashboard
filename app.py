print("AMRUTHA TEST")
from flask import Flask, render_template, request,redirect,url_for
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM study_logs")
    data = cursor.fetchall()

    conn.close()
    return render_template("index.html",logs=data)


@app.route("/add", methods=["POST"])
def add():

    subject = request.form["subject"]
    hours = request.form["hours"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO study_logs (subject, hours) VALUES (?, ?)",
        (subject, hours)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))
@app.route("/analytics")
def analytics():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, SUM(hours)
        FROM study_logs
        GROUP BY subject
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template("analytics.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)