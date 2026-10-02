// The one page of the app (for now): it asks the backend "are you healthy?"
// and shows the answer.
import { useEffect, useState } from "react";

import { fetchHealth } from "./api.js";

export default function App() {
  // State: values that, when changed, make React re-draw the page.
  const [health, setHealth] = useState(null); // JSON from /health, or null
  const [error, setError] = useState(null); // error message, or null
  const [loading, setLoading] = useState(true); // true while waiting

  // Ask the backend for its health and store the result in state.
  async function checkHealth() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      setHealth(null);
      setError(err.message);
    } finally {
      // `finally` runs whether the request worked or failed.
      setLoading(false);
    }
  }

  // useEffect with an empty list [] runs once, right after the page first
  // appears. That is when we do the first health check.
  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <main className="page">
      <h1>notes-to-tasks</h1>
      <p className="subtitle">
        Paste meeting notes, get tasks on a shared board. (Coming soon!)
      </p>

      <section className="card">
        <h2>Backend health</h2>

        {/* Show exactly one of: loading, error, or the result. */}
        {loading && <p>Checking…</p>}

        {!loading && error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        {!loading && health && (
          <ul className="status-list">
            <li>
              API: <strong>{health.status}</strong>
            </li>
            <li>
              Database: <strong>{health.database}</strong>
            </li>
          </ul>
        )}

        {/*
          ------------------------------------------------------------------
          TODO (frontend): add a "Check again" button here.

          What it should do:
            - Clicking it runs the health check again (call checkHealth).
            - While a check is running (`loading` is true), the button is
              disabled, so people can't click it many times in a row.

          Hints:
            - Look up the `onClick` and `disabled` props of a <button>.
            - Pass the function itself to onClick: onClick={checkHealth},
              not onClick={checkHealth()}. Do you know why?
            - You don't need any new state; `loading` already exists.

          How to check it works:
            Start the backend and frontend, click the button, and watch
            the Network tab in your browser's dev tools: each click should
            send one new request to /health. Then stop the backend, click
            again, and you should see the error message.
          ------------------------------------------------------------------
        */}
      </section>
    </main>
  );
}
