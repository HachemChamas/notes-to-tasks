// Entry point of the frontend: renders the <App /> component into the
// <div id="root"> element in index.html.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  // StrictMode adds extra checks while developing. One visible side effect:
  // in dev mode, effects run twice, so you will see /health called twice.
  <StrictMode>
    <App />
  </StrictMode>,
);
