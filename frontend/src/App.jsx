import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [player, setPlayer] = useState({ hp: 100 });
  const [enemy, setEnemy] = useState({ hp: 100 });
  const [message, setMessage] = useState("The battle begins!");
  const [turn, setTurn] = useState("player");
  const [waiting, setWaiting] = useState(false);

  // Load initial game state
  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/state")
      .then((res) => res.json())
      .then((data) => {
        setPlayer(data.player);
        setEnemy(data.enemy);
        setTurn(data.turn);
      });
  }, []);

  const castSpell = async (spell) => {
    if (turn !== "player" || waiting) return; // prevent spam

    setWaiting(true);

    // 1️⃣ Player casts spell
    const response = await fetch("http://127.0.0.1:5000/api/spell", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ spell }),
    });

    const data = await response.json();
    setPlayer(data.player);
    setEnemy(data.enemy);
    setMessage(data.message);
    setTurn(data.turn);

    // 2️⃣ Trigger enemy turn after delay
    if (data.turn === "enemy") {
      setTimeout(async () => {
        const enemyResponse = await fetch(
          "http://127.0.0.1:5000/api/enemy_turn",
          { method: "POST" }
        );
        const enemyData = await enemyResponse.json();
        setPlayer(enemyData.player);
        setEnemy(enemyData.enemy);
        setMessage((prev) => prev + " " + enemyData.message);
        setTurn(enemyData.turn);
        setWaiting(false);
      }, 1500); // 1.5s delay to simulate thinking
    } else {
      setWaiting(false);
    }
  };

  return (
    <div className="battle-container">
      <h1>Turn Based Rpg </h1>

      <div className="battlefield">
        {/* Enemy Section */}
        <div className="character-section">
          <h2>Enemy</h2>
          <img src="/images/enemy.png" alt="Enemy" className="sprite" />
          <div className="hp-bar">
            <div
              className="hp-fill enemy"
              style={{ width: `${enemy.hp}%` }}
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
              style={{ width: `${player.hp}%` }}
            ></div>
          </div>
          <p>HP: {player.hp}</p>
        </div>
      </div>

      {/* Spell Buttons */}
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

      {/* Battle Message */}
      <div className="message-box">
        {turn === "enemy" && <p>Enemy is thinking...</p>}
        <p>{message}</p>
      </div>
    </div>
  );
}

export default App;
