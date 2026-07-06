import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, render_template, request,jsonify,redirect,url_for
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
print("API KEY FOUND:", os.getenv("GEMINI_API_KEY") is not None)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
app = Flask(__name__)

@app.route("/")
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM study_logs")
    data = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(DISTINCT subject) FROM study_logs")
    total_subjects = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(hours) FROM study_logs")
    total_hours = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM study_logs")
    total_logs = cursor.fetchone()[0]

    cursor.execute("""
        SELECT subject
        FROM study_logs
        GROUP BY subject
        ORDER BY SUM(hours) DESC
        LIMIT 1
    """)
    top_subject = cursor.fetchone()
    if top_subject:
        top_subject = top_subject[0]
    else:
        top_subject = "No data available"
    

    conn.close()
    print("Subjects:", total_subjects)
    print("Hours:", total_hours)
    print("Logs:", total_logs)
    print("Top Subject:", top_subject)
    return render_template("index.html",logs=data, total_subjects=total_subjects, total_hours=total_hours, total_logs=total_logs, top_subject=top_subject)



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

    subjects = []
    hours = []

    for row in data:
        subjects.append(row[0])
        hours.append(row[1])

    plt.figure(figsize=(8,5))
    plt.bar(subjects, hours,color='skyblue')
    plt.xlabel("Subjects")
    plt.ylabel("Hours Studied")
    plt.title("Study Hours by Subject")
    plt.savefig("static/chart.png")
    plt.close()

    conn.close()

    return render_template(
        "analytics.html",
        data=data,
        chart="chart.png"
    )

@app.route("/clear", methods=["POST"])
def clear_logs():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM study_logs")

    conn.commit()
    conn.close()

    return redirect(url_for("home"))
@app.route("/ai-advice", methods=["POST"])
def ai_advice():

    data = request.json

    logs = data.get("logs", [])

    if not logs:
        return jsonify({"advice": "No study logs available."})

    study_data = ""

    for log in logs:
        study_data += f"{log['subject']} - {log['hours']} hours\n"
    prompt = f"""
    You are an experienced academic study mentor.

    The student has studied:

    {study_data}

    Analyze the study pattern and respond with exactly 3 bullet points.

    Rules:
    - Do NOT use markdown.
    - Do NOT use **, #, or any formatting symbols.
    - Start every point with the bullet character •
    - Keep the total response under 120 words.
    - Use simple, friendly English.

    Include:
    • Strongest subject
    • Subject needing more attention
    • One practical improvement
   
    Then on a new line write:
    <MOTIVATION>
    your motivational sentence here
    </MOTIVATION>

    
    """

    response = model.generate_content(prompt)

    return jsonify({
        "advice": response.text
    })
@app.route("/test-ai")
def test_ai():

    response = model.generate_content(
        "Give one motivational study quote in one sentence."
    )

    return response.text
    

import os


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)