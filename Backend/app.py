from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Initial game state
player = {"hp": 100, "attack": 20, "defense": 10}
enemy = {"hp": 100, "attack": 15, "defense": 8}

@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify({"player": player, "enemy": enemy})

@app.route("/api/attack", methods=["POST"])
def attack():
    global player, enemy
    damage = max(0, player["attack"] - enemy["defense"] + random.randint(-5, 5))
    enemy["hp"] = max(0, enemy["hp"] - damage)

    if enemy["hp"] > 0:
        enemy_damage = max(0, enemy["attack"] - player["defense"] + random.randint(-5, 5))
        player["hp"] = max(0, player["hp"] - enemy_damage)
        message = f"You dealt {damage} damage! Enemy hit back for {enemy_damage}!"
    else:
        message = f"You dealt {damage} damage! Enemy defeated!"

    return jsonify({"player": player, "enemy": enemy, "message": message})

@app.route("/api/defend", methods=["POST"])
def defend():
    global player, enemy
    defense_boost = random.randint(5, 10)
    reduced_damage = max(0, enemy["attack"] - (player["defense"] + defense_boost))
    player["hp"] = max(0, player["hp"] - reduced_damage)
    message = f"You defended! Enemy dealt only {reduced_damage} damage!"
    return jsonify({"player": player, "enemy": enemy, "message": message})

@app.route("/api/reset", methods=["POST"])
def reset():
    global player, enemy
    player = {"hp": 100, "attack": 20, "defense": 10}
    enemy = {"hp": 100, "attack": 15, "defense": 8}
    return jsonify({"player": player, "enemy": enemy})

if __name__ == "__main__":
    app.run(debug=True)
