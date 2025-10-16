from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# -------------------------------
# Game State
# -------------------------------
player = {
    "hp": 100,
    "attack": 20,
    "defense": 10,
    "crit": 0.1,
    "buffs": {},
    "shield": 0
}
enemy = {
    "hp": 100,
    "attack": 15,
    "defense": 8,
    "buffs": {}
}

turn = "player"  # track whose turn it is

# -------------------------------
# Utility Functions
# -------------------------------
def apply_buffs(character):
    atk = character["attack"] + character["buffs"].get("attack", 0)
    defense = character["defense"] + character["buffs"].get("defense", 0)
    crit = character["crit"] + character["buffs"].get("crit", 0)
    return atk, defense, crit

def enemy_action():
    global player, enemy
    if enemy["hp"] <= 0:
        return "Enemy defeated!"

    choice = random.choice(["attack", "heavy_attack", "defend"])
    message = ""

    if choice == "attack":
        dmg = max(0, enemy["attack"] - player["defense"])
        if player["shield"]:
            dmg = int(dmg * (1 - player["shield"]))
            player["shield"] = 0
        player["hp"] = max(0, player["hp"] - dmg)
        message = f"Enemy attacks for {dmg} damage!"
    elif choice == "heavy_attack":
        dmg = max(0, enemy["attack"] + 5 - player["defense"])
        if player["shield"]:
            dmg = int(dmg * (1 - player["shield"]))
            player["shield"] = 0
        player["hp"] = max(0, player["hp"] - dmg)
        message = f"Enemy uses Heavy Strike for {dmg} damage!"
    else:
        enemy["buffs"]["defense"] = 5
        message = "Enemy braces for defense."

    return message

# -------------------------------
# Routes
# -------------------------------
@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify({"player": player, "enemy": enemy, "turn": turn})

@app.route("/api/spell", methods=["POST"])
def use_spell():
    global player, enemy, turn
    data = request.json
    spell = data.get("spell")
    message = ""

    if spell == "reset":
        player.update({"hp": 100, "attack": 20, "defense": 10, "crit": 0.1, "buffs": {}, "shield": 0})
        enemy.update({"hp": 100, "attack": 15, "defense": 8, "buffs": {}})
        turn = "player"
        return jsonify({"player": player, "enemy": enemy, "message": "Game reset!", "turn": turn})

    if turn != "player":
        return jsonify({"player": player, "enemy": enemy, "message": "Wait for your turn!", "turn": turn})

    # -------------------------------
    # Player Spells
    # -------------------------------
    if spell == "heal":
        heal_amt = random.randint(20, 30)
        player["hp"] = min(100, player["hp"] + heal_amt)
        message = f"You healed for {heal_amt} HP!"
    elif spell == "dmg_boost":
        player["buffs"]["attack"] = 10
        message = "Your attack increased by 10 for 3 turns!"
    elif spell == "crit_boost":
        player["buffs"]["crit"] = 0.3
        message = "Your critical hit rate increased for 3 turns!"
    elif spell == "def_boost":
        player["buffs"]["defense"] = 10
        message = "Your defense increased by 10 for 3 turns!"
    elif spell == "punch":
        atk, _, crit = apply_buffs(player)
        dmg = max(0, atk - enemy["defense"] + random.randint(-3,3))
        if random.random() < crit:
            dmg *= 2
            message = f"Critical Punch! You dealt {dmg} damage!"
        else:
            message = f"You punched the enemy for {dmg} damage."
        enemy["hp"] = max(0, enemy["hp"] - dmg)
    elif spell == "spear_throw":
        atk, _, crit = apply_buffs(player)
        dmg = max(0, atk + 5 - enemy["defense"])
        if random.random() < crit + 0.2:
            dmg *= 2
            message = f"Critical Spear Throw! You dealt {dmg} damage!"
        else:
            message = f"You threw a spear for {dmg} damage."
        enemy["hp"] = max(0, enemy["hp"] - dmg)
    elif spell == "tornado":
        if random.random() < 0.2:
            message = "Your tornado missed!"
        else:
            dmg = random.randint(30, 45)
            enemy["hp"] = max(0, enemy["hp"] - dmg)
            message = f"You unleashed a tornado for {dmg} damage!"
    elif spell == "shield_block":
        player["shield"] = 0.5
        message = "You brace your shield! Next attack damage halved."

    # -------------------------------
    # Switch turn to enemy
    # -------------------------------
    turn = "enemy"
    return jsonify({"player": player, "enemy": enemy, "message": message, "turn": turn})

# -------------------------------
# Enemy Turn Route
# -------------------------------
@app.route("/api/enemy_turn", methods=["POST"])
def enemy_turn():
    global player, enemy, turn
    if turn != "enemy":
        return jsonify({"player": player, "enemy": enemy, "message": "Not enemy's turn!", "turn": turn})

    message = enemy_action()
    turn = "player"
    return jsonify({"player": player, "enemy": enemy, "message": message, "turn": turn})

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
