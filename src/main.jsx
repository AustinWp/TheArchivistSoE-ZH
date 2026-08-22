// ==============================
// Diablo 2 Items SPA (React + plain CSS)
// ==============================
//
// This is a small, static SPA with 3 tabs: Weapons, Armors, Uniques.
// It loads JSON via fetch from /data/*.json (place the provided JSON files there).
//
// Project layout (Vite recommended):
//   your-app/
//     index.html
//     src/
//       main.jsx
//       App.jsx
//       styles.css
//     public/
//       data/
//         Weapons.json
//         Armors.json
//         Uniques.json
//
// ------------------------------
// src/main.jsx
// ------------------------------
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);