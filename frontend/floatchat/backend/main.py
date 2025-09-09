
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Configure your OpenAI API key
openai.api_key = "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"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )
        ai_message = response.choices[0].message["content"]
        return jsonify({"message": ai_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
