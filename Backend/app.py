# ===============================
# IMPORTS AND INITIAL SETUP
# ===============================
from flask import Flask, jsonify, request   # Flask handles web routing and requests/responses
from flask_cors import CORS                 # Allows requests from different domains (e.g. frontend)
import random                               # Used for chance-based gameplay (e.g. critical hits, random choices)

# Create a Flask web app instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing so the frontend can access the backend
CORS(app)


# ===============================
# GAME STATE VARIABLES
# ===============================

# Player stats dictionary: tracks all important player attributes
player = {
    "hp": 100,          # Player health points
    "attack": 20,       # Base attack damage
    "defense": 10,      # Base defense value (reduces damage)
    "crit": 0.1,        # 10% chance to deal double damage
    "buffs": {},        # Temporary stat boosts (e.g. +attack, +defense)
    "shield": 0         # Reduces incoming damage when active (0.5 = 50%)
}

# Enemy stats dictionary: similar structure to player but with fewer attributes
enemy = {
    "hp": 100,
    "attack": 15,
    "defense": 8,
    "buffs": {}
}

# Keeps track of whose turn it is — alternates between "player" and "enemy"
turn = "player"


# ===============================
# UTILITY FUNCTION: APPLY BUFFS
# ===============================
def apply_buffs(character):
    """
    Combines a character's base stats with any temporary buff effects.

    Args:
        character (dict): The character whose stats are being calculated (player or enemy).

    Returns:
        tuple: (atk, defense, crit)
            atk     -> total attack value after buffs
            defense -> total defense value after buffs
            crit    -> total crit rate after buffs
    """
    # Add buffs to each stat if they exist, otherwise default to 0
    atk = character["attack"] + character["buffs"].get("attack", 0)
    defense = character["defense"] + character["buffs"].get("defense", 0)
    crit = character.get("crit", 0) + character["buffs"].get("crit", 0)
    return atk, defense, crit


# ===============================
# ENEMY ACTION LOGIC
# ===============================
def enemy_action():
    """
    Determines what the enemy does during its turn.
    Randomly chooses between 'attack', 'heavy_attack', or 'defend'.

    Returns:
        str: A message describing what the enemy did.
    """
    global player, enemy  # Access and modify the global player/enemy data

    # If the enemy is dead, do nothing
    if enemy["hp"] <= 0:
        return "Enemy defeated!"

    # Enemy picks a random action
    choice = random.choice(["attack", "heavy_attack", "defend"])
    message = ""

    # --- Normal attack ---
    if choice == "attack":
        dmg = max(0, enemy["attack"] - player["defense"])  # Calculate net damage
        if player["shield"]:  # If shield is active, reduce damage
            dmg = int(dmg * (1 - player["shield"]))
            player["shield"] = 0  # Shield only works once
        player["hp"] = max(0, player["hp"] - dmg)
        message = f"Enemy attacks for {dmg} damage!"

    # --- Heavy attack (stronger than normal) ---
    elif choice == "heavy_attack":
        dmg = max(0, enemy["attack"] + 5 - player["defense"])
        if player["shield"]:
            dmg = int(dmg * (1 - player["shield"]))
            player["shield"] = 0
        player["hp"] = max(0, player["hp"] - dmg)
        message = f"Enemy uses Heavy Strike for {dmg} damage!"

    # --- Defensive stance (raises defense temporarily) ---
    else:
        enemy["buffs"]["defense"] = 5
        message = "Enemy braces for defense."

    return message


# ===============================
# ROUTE: GET GAME STATE
# ===============================
@app.route("/api/state", methods=["GET"])
def get_state():
    """
    API endpoint to retrieve the current state of the game.

    Returns:
        JSON: The player stats, enemy stats, and whose turn it is.
    """
    return jsonify({"player": player, "enemy": enemy, "turn": turn})


# ===============================
# ROUTE: PLAYER CASTS A SPELL
# ===============================
@app.route("/api/spell", methods=["POST"])
def use_spell():
    """
    Handles all player actions (spells/attacks).

    Reads 'spell' from the request body and updates the game state accordingly.
    Handles healing, buffs, attacks, and shields.

    Returns:
        JSON: Updated player/enemy states, a message, and whose turn it is next.
    """
    global player, enemy, turn

    # Parse JSON data sent from frontend
    data = request.json
    spell = data.get("spell")  # Extract which spell was used
    message = ""

    # --- Reset game state ---
    if spell == "reset":
        player.update({"hp": 100, "attack": 20, "defense": 10, "crit": 0.1, "buffs": {}, "shield": 0})
        enemy.update({"hp": 100, "attack": 15, "defense": 8, "buffs": {}})
        turn = "player"
        return jsonify({"player": player, "enemy": enemy, "message": "Game reset!", "turn": turn})

    # Prevent the player from acting out of turn
    if turn != "player":
        return jsonify({"player": player, "enemy": enemy, "message": "Wait for your turn!", "turn": turn})


    # --- Spell logic (each branch handles one spell type) ---

    # Heal restores a random amount of HP
    if spell == "heal":
        heal_amt = random.randint(20, 30)
        player["hp"] = min(100, player["hp"] + heal_amt)
        message = f"You healed for {heal_amt} HP!"

    # Temporary attack boost
    elif spell == "dmg_boost":
        player["buffs"]["attack"] = 10
        message = "Your attack increased by 10 for 3 turns!"

    # Temporary critical hit chance boost
    elif spell == "crit_boost":
        player["buffs"]["crit"] = 0.3
        message = "Your critical hit rate increased for 3 turns!"

    # Temporary defense boost
    elif spell == "def_boost":
        player["buffs"]["defense"] = 10
        message = "Your defense increased by 10 for 3 turns!"

    # Basic attack (punch)
    elif spell == "punch":
        atk, _, crit = apply_buffs(player)
        dmg = max(0, atk - enemy["defense"] + random.randint(-3, 3))
        if random.random() < crit:
            dmg *= 2
            message = f"Critical Punch! You dealt {dmg} damage!"
        else:
            message = f"You punched the enemy for {dmg} damage."
        enemy["hp"] = max(0, enemy["hp"] - dmg)

    # Stronger ranged attack (spear throw)
    elif spell == "spear_throw":
        atk, _, crit = apply_buffs(player)
        dmg = max(0, atk + 5 - enemy["defense"])
        if random.random() < crit + 0.2:  # 20% bonus crit chance
            dmg *= 2
            message = f"Critical Spear Throw! You dealt {dmg} damage!"
        else:
            message = f"You threw a spear for {dmg} damage."
        enemy["hp"] = max(0, enemy["hp"] - dmg)

    # Area spell with a chance to miss
    elif spell == "tornado":
        if random.random() < 0.2:
            message = "Your tornado missed!"
        else:
            dmg = random.randint(30, 45)
            enemy["hp"] = max(0, enemy["hp"] - dmg)
            message = f"You unleashed a tornado for {dmg} damage!"

    # Defensive spell that halves next attack damage
    elif spell == "shield_block":
        player["shield"] = 0.5
        message = "You brace your shield! Next attack damage halved."

    # End player's turn — next turn goes to enemy
    turn = "enemy"
    return jsonify({"player": player, "enemy": enemy, "message": message, "turn": turn})


# ===============================
# ROUTE: ENEMY TURN HANDLER
# ===============================
@app.route("/api/enemy_turn", methods=["POST"])
def enemy_turn():
    """
    Handles the enemy's turn.
    The frontend calls this after the player's turn ends.

    Returns:
        JSON: Updated player/enemy states, action message, and next turn ("player").
    """
    global player, enemy, turn

    # Prevent the enemy from acting if it’s not their turn
    if turn != "enemy":
        return jsonify({"player": player, "enemy": enemy, "message": "Not enemy's turn!", "turn": turn})

    # Enemy takes action
    message = enemy_action()

    # Pass control back to player
    turn = "player"

    return jsonify({"player": player, "enemy": enemy, "message": message, "turn": turn})


# ===============================
# MAIN ENTRY POINT
# ===============================
if __name__ == "__main__":
    # Runs the Flask development server with debug mode enabled.
    # Debug mode auto-restarts the server on code changes and shows errors in the browser.
    app.run(debug=True)
