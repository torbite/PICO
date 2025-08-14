from flask import Flask, jsonify, request
import pico_main
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



@app.route("/pico/prompt", methods=["POST", "GET"])
def hi():
    data = request.get_json(force=True)
    prompt = data["prompt"]
    response = pico_main.sendUserInput(prompt)
    print(response)
    return jsonify(response)

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json()
    user_message = data["message"]
    pico_main.sendUserInput()

print("LOADED")

if __name__ == "__main__":
    app.run(debug=True)