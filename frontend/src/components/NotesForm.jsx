// Step 1: paste notes and ask the AI to find tasks.
import { useState } from "react";

import { todayString } from "../dates.js";

const EXAMPLE = `Weekly sync, Thursday
- Ada will send the updated budget to finance by Monday.
- Alan: I'll fix the login bug before the demo next Wednesday.
- We agreed the launch moves to December.
- Someone needs to book a room for the retro.`;

export default function NotesForm({ onExtract, busy }) {
  const [text, setText] = useState("");
  const [meetingDate, setMeetingDate] = useState(todayString());

  function handleSubmit(event) {
    // Stop the browser from reloading the page (the default for forms).
    event.preventDefault();
    if (text.trim()) onExtract(text, meetingDate);
  }

  return (
    <form className="card notes-form" onSubmit={handleSubmit}>
      <div className="card-header">
        <h2>1. Paste your notes</h2>
        <button type="button" className="link-button" onClick={() => setText(EXAMPLE)}>
          Use an example
        </button>
      </div>

      <label htmlFor="notes">Meeting notes or chat messages</label>
      <textarea
        id="notes"
        rows={8}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Paste meeting notes or a group chat here…"
      />

      <div className="row">
        <label className="inline">
          Meeting date
          <input
            type="date"
            value={meetingDate}
            onChange={(event) => setMeetingDate(event.target.value)}
          />
        </label>
        <button type="submit" className="primary" disabled={busy || !text.trim()}>
          {busy ? "Finding tasks…" : "Find tasks"}
        </button>
      </div>
      <p className="hint">
        The meeting date lets the AI turn &quot;by Friday&quot; into a real date.
      </p>
    </form>
  );
}
