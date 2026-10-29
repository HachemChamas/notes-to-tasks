// Small status pill in the header: is the backend (and its database) up?
import { useEffect, useState } from "react";

import { fetchHealth } from "../api.js";

export default function HealthBadge() {
  const [health, setHealth] = useState(null); // JSON from /health, or null
  const [error, setError] = useState(null); // error message, or null
  const [loading, setLoading] = useState(true); // true while waiting

  async function checkHealth() {
    setLoading(true);
    setError(null);
    try {
      setHealth(await fetchHealth());
    } catch (err) {
      setHealth(null);
      setError(err.message);
    } finally {
      // `finally` runs whether the request worked or failed.
      setLoading(false);
    }
  }

  // An empty dependency list [] means: run once, when the badge first appears.
  useEffect(() => {
    checkHealth();
  }, []);

  const allGood = health?.status === "ok" && health?.database === "ok";
  let label = "Checking…";
  if (!loading && error) label = error;
  if (!loading && health) {
    label = allGood ? "All systems ok" : `Database: ${health.database}`;
  }

  return (
    <div className="health" role="status">
      <span
        className={`dot ${loading ? "dot-wait" : allGood ? "dot-ok" : "dot-bad"}`}
        aria-hidden="true"
      />
      <span>{label}</span>
      {/* Pass the function itself; onClick={checkHealth()} would call it
          immediately on every render instead of on click. */}
      <button className="link-button" onClick={checkHealth} disabled={loading}>
        {loading ? "Checking…" : "Check again"}
      </button>
    </div>
  );
}
