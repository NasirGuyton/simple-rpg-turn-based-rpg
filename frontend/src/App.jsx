import { useState, useEffect } from "react";

function App() {
  const [player, setPlayer] = useState({ hp: 100 });
  const [enemy, setEnemy] = useState({ hp: 100 });
  const [message, setMessage] = useState("Battle begins!");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/state")
      .then((res) => res.json())
      .then((data) => {
        setPlayer(data.player);
        setEnemy(data.enemy);
      });
  }, []);

  const handleAction = (action) => {
    fetch(`http://127.0.0.1:5000/api/${action}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        setPlayer(data.player);
        setEnemy(data.enemy);
        setMessage(data.message);
      });
  };

  const resetGame = () => {
    fetch("http://127.0.0.1:5000/api/reset", { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        setPlayer(data.player);
        setEnemy(data.enemy);
        setMessage("Battle reset!");
      });
  };

  const renderHPBar = (hp) => {
    const width = Math.max(hp, 0);
    const color = hp > 60 ? "green" : hp > 30 ? "orange" : "red";
    return (
      <div style={{ width: "200px", height: "20px", background: "#ddd", borderRadius: "10px", margin: "auto" }}>
        <div
          style={{
            width: `${width}%`,
            height: "100%",
            background: color,
            borderRadius: "10px",
            transition: "width 0.3s ease",
          }}
        ></div>
      </div>
    );
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px", fontFamily: "Arial" }}>
      <h1>⚔️ Simple Turn-Based RPG ⚔️</h1>

      <div style={{ margin: "20px" }}>
        <h2>Player HP: {player.hp}</h2>
        {renderHPBar(player.hp)}
        <h2>Enemy HP: {enemy.hp}</h2>
        {renderHPBar(enemy.hp)}
      </div>

      <div style={{ margin: "20px" }}>
        <button onClick={() => handleAction("attack")} disabled={player.hp <= 0 || enemy.hp <= 0}>
          Attack
        </button>
        <button onClick={() => handleAction("defend")} disabled={player.hp <= 0 || enemy.hp <= 0}>
          Defend
        </button>
        <button onClick={resetGame}>Restart</button>
      </div>

      <p>{message}</p>

      {(player.hp <= 0 || enemy.hp <= 0) && (
        <h2 style={{ color: "red" }}>
          {player.hp <= 0 ? "You were defeated!" : "You won the battle!"}
        </h2>
      )}
    </div>
  );
}

export default App;
