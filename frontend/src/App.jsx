// ===============================
// IMPORTS
// ===============================
import React, { useState, useEffect } from "react"; // useState manages state, useEffect handles side effects
import "./App.css"; // Import custom CSS styles


// ===============================
// MAIN APP COMPONENT
// ===============================
function App() {
  // -------------------------------
  // STATE VARIABLES
  // -------------------------------
  const [player, setPlayer] = useState({ hp: 100 }); // Stores player stats (currently only HP)
  const [enemy, setEnemy] = useState({ hp: 100 });   // Stores enemy stats (currently only HP)
  const [message, setMessage] = useState("The battle begins!"); // Stores current battle message for display
  const [turn, setTurn] = useState("player");       // Tracks whose turn it is: "player" or "enemy"
  const [waiting, setWaiting] = useState(false);    // Prevents spamming clicks while waiting for enemy turn

  // -------------------------------
  // EFFECT: INITIAL GAME STATE
  // -------------------------------
  useEffect(() => {
    // Fetch initial game state from backend when component mounts
    fetch("http://127.0.0.1:5000/api/state")
      .then((res) => res.json()) // Convert response to JSON
      .then((data) => {
        setPlayer(data.player); // Set player stats
        setEnemy(data.enemy);   // Set enemy stats
        setTurn(data.turn);     // Set initial turn
      });
  }, []); // Empty dependency array ensures this runs only once when the component mounts

  // -------------------------------
  // FUNCTION: CAST SPELL / PLAYER ACTION
  // -------------------------------
  const castSpell = async (spell) => {
    // Prevent action if it's not the player's turn or if we're waiting for enemy
    if (turn !== "player" || waiting) return;

    setWaiting(true); // Block further clicks until action completes

    // --- Player action: send spell to backend ---
    const response = await fetch("http://127.0.0.1:5000/api/spell", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ spell }), // Send spell name to backend
    });

    const data = await response.json(); // Get response JSON from backend
    setPlayer(data.player); // Update player stats based on backend response
    setEnemy(data.enemy);   // Update enemy stats
    setMessage(data.message); // Update battle message
    setTurn(data.turn);       // Update whose turn it is

    // --- Handle enemy turn if backend says it's enemy's turn ---
    if (data.turn === "enemy") {
      // Add delay to simulate enemy thinking
      setTimeout(async () => {
        const enemyResponse = await fetch(
          "http://127.0.0.1:5000/api/enemy_turn",
          { method: "POST" }
        );
        const enemyData = await enemyResponse.json();
        setPlayer(enemyData.player);   // Update player stats after enemy attack
        setEnemy(enemyData.enemy);     // Update enemy stats
        setMessage((prev) => prev + " " + enemyData.message); // Append enemy message
        setTurn(enemyData.turn);       // Update turn back to player
        setWaiting(false);             // Re-enable player actions
      }, 1500); // 1.5 second delay to simulate enemy thinking
    } else {
      // If player gets another turn or game reset, stop waiting
      setWaiting(false);
    }
  };

  // -------------------------------
  // JSX: RENDER THE UI
  // -------------------------------
  return (
    <div className="battle-container">
      <h1>Turn Based RPG</h1>

      {/* ===============================
          BATTLEFIELD
      =============================== */}
      <div className="battlefield">
        {/* Enemy Section */}
        <div className="character-section">
          <h2>Enemy</h2>
          <img src="/images/enemy.png" alt="Enemy" className="sprite" />
          <div className="hp-bar">
            <div
              className="hp-fill enemy"
              style={{ width: `${enemy.hp}%` }} // Fill bar proportional to HP
            ></div>
          </div>
          <p>HP: {enemy.hp}</p>
        </div>

        {/* Player Section */}
        <div className="character-section">
          <h2>Player</h2>
          <img src="/images/player.png" alt="Player" className="sprite" />
          <div className="hp-bar">
            <div
              className="hp-fill player"
              style={{ width: `${player.hp}%` }} // Fill bar proportional to HP
            ></div>
          </div>
          <p>HP: {player.hp}</p>
        </div>
      </div>

      {/* ===============================
          SPELL BUTTONS / CONTROLS
      =============================== */}
      <div className="controls">
        <h3>Support</h3>
        <button onClick={() => castSpell("heal")}>Heal ❤️</button>
        <button onClick={() => castSpell("dmg_boost")}>Attack Boost ⚡</button>
        <button onClick={() => castSpell("crit_boost")}>Crit Boost ✨</button>
        <button onClick={() => castSpell("def_boost")}>Defense Boost 🛡️</button>

        <h3>Attack</h3>
        <button onClick={() => castSpell("punch")}>Punch 👊</button>
        <button onClick={() => castSpell("spear_throw")}>Spear Throw 🗡️</button>
        <button onClick={() => castSpell("tornado")}>Tornado 🌪️</button>

        <h3>Defense</h3>
        <button onClick={() => castSpell("shield_block")}>Shield Block 🛡️</button>

        <h3>Reset</h3>
        <button onClick={() => castSpell("reset")}>Reset 🔄</button>
      </div>

      {/* ===============================
          BATTLE MESSAGE BOX
      =============================== */}
      <div className="message-box">
        {/* Show waiting message if enemy is thinking */}
        {turn === "enemy" && <p>Enemy is thinking...</p>}
        <p>{message}</p>
      </div>
    </div>
  );
}

// Export the component so it can be used by index.js
export default App;
