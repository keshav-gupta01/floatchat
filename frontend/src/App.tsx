import React from "react";
import { useTheme } from "./components/ThemeContext";
import "./App.css";

function App() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div>
      <header style={{ display: "flex", justifyContent: "flex-end", padding: 16 }}>
        <button
          onClick={toggleTheme}
          style={{
            background: "none",
            border: "1px solid var(--fg)",
            borderRadius: 8,
            padding: "4px 12px",
            cursor: "pointer",
            color: "var(--fg)",
          }}
        >
          {theme === "dark" ? "🌙 Dark" : "☀️ Light"}
        </button>
      </header>
      {/* ...rest of your app... */}
    </div>
  );
}

export default App;