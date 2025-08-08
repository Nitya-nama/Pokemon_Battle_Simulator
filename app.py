from flask import Flask, request, jsonify
from flask_cors import CORS
from battle_simulator import simulate_battle

app = Flask(__name__)
CORS(app)  

@app.route("/tool/simulate", methods=["POST"])
def simulate():
    data = request.json
    p1 = data.get("pokemon1")
    p2 = data.get("pokemon2")

    result = simulate_battle(p1, p2)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
