from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# ---- Sample in-memory health logs (your sample dataset) ----
health_logs = [
    {
        "date": "2025-11-17",
        "user_id": "user1",
        "symptoms": "Headache, Mild fever",
        "mood": "Tired",
        "medications": "Paracetamol",
        "sleep_hours": 6
    },
    {
        "date": "2025-11-16",
        "user_id": "user1",
        "symptoms": "No major symptoms",
        "mood": "Normal",
        "medications": "None",
        "sleep_hours": 7
    }
]

@app.route("/", methods=["GET"])
def home():
    return "HealthMate AI backend is running!", 200


@app.route("/ask", methods=["GET", "POST"])
def ask():
    # If called from browser with GET, read question from URL ?question=...
    if request.method == "GET":
        question = request.args.get("question", "")
        if not question:
            return (
                "Use /ask like this in browser: "
                "/ask?question=I+have+headache+what+should+I+do",
                200,
            )
    else:
        # POST: JSON body
        data = request.get_json(silent=True) or {}
        question = data.get("question", "")

    if not question:
        return jsonify({"error": "Please send a 'question' field"}), 400

    dummy_answer = (
        f"I received your question: '{question}'. "
        "This is a placeholder answer for now. Later this will be answered by Gemini AI."
    )

    return jsonify({
        "question": question,
        "answer": dummy_answer
    }), 200

@app.route("/log", methods=["POST"])
def add_log():
    data = request.get_json(silent=True) or {}

    required_fields = ["date", "user_id", "symptoms", "mood", "medications", "sleep_hours"]
    missing = [f for f in required_fields if f not in data]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing
        }), 400

    health_logs.append(data)

    return jsonify({
        "message": "Health log added successfully",
        "log": data
    }), 201


@app.route("/logs", methods=["GET"])
def get_logs():
    user_id = request.args.get("user_id")

    if user_id:
        filtered = [log for log in health_logs if log.get("user_id") == user_id]
        return jsonify(filtered), 200

    return jsonify(health_logs), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)