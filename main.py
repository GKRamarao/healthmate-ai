import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# -------- CONFIG --------
MODEL_ID = "gemini-2.5-flash"   # <--- ONLY CHANGE THIS IF NEEDED

app = Flask(__name__)


# Sample data
health_logs = [
    {
        "date": "2025-11-17",
        "user_id": "user1",
        "symptoms": "Headache, Mild fever",
        "mood": "Tired",
        "medications": "Paracetamol",
        "sleep_hours": 6
    }
]


@app.route("/", methods=["GET"])
def home():
    return f"HealthMate AI – using model: {MODEL_ID}", 200


@app.route("/ask", methods=["GET", "POST"])
def ask():
    try:
        # Read question
        if request.method == "GET":
            question = request.args.get("question", "")
        else:
            data = request.get_json(silent=True) or {}
            question = data.get("question", "")

        if not question:
            return jsonify({"error": "Please provide 'question'"}), 400

        # Read API key
        api_key = os.environ.get("GOOGLE_API_KEY")
        print("DEBUG GOOGLE_API_KEY set?:", bool(api_key))
        print("DEBUG MODEL_ID:", MODEL_ID)

        if not api_key:
            return jsonify({
                "question": question,
                "answer": f"(Placeholder) I received your question: '{question}'. No API key set."
            }), 200

        # Configure Gemini and call
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_ID)

        prompt = (
            "You are a friendly health & wellness assistant. "
            "Give only general lifestyle suggestions, NOT diagnosis or prescriptions. "
            "Always suggest seeing a doctor for serious or persistent issues.\n\n"
            f"User question: {question}"
        )

        response = model.generate_content(prompt)

        # Extract text
        answer_text = ""
        try:
            answer_text = response.text.strip()
        except AttributeError:
            if getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts
                answer_text = "".join(getattr(p, "text", "") for p in parts).strip()

        if not answer_text:
            answer_text = "Gemini returned an empty response. Please rephrase your question."

        return jsonify({"question": question, "answer": answer_text}), 200

    except Exception as e:
        print("ERROR in /ask:", repr(e))
        return jsonify({
            "error": "Internal server error in /ask",
            "details": str(e),
            "model_used": MODEL_ID
        }), 500


@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(health_logs), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("Starting app on port", port, "with MODEL_ID =", MODEL_ID)
    app.run(host="0.0.0.0", port=port)
