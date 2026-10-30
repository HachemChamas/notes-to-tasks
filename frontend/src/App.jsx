// The whole app: paste notes -> review suggestions -> shared task board.
// This component owns the data (tasks, suggestions) and passes it down to
// smaller components as props, along with functions they call to change it.
import { useCallback, useEffect, useState } from "react";

import * as api from "./api.js";
import HealthBadge from "./components/HealthBadge.jsx";
import NotesForm from "./components/NotesForm.jsx";
import ReviewPanel from "./components/ReviewPanel.jsx";
import TaskBoard from "./components/TaskBoard.jsx";

// How often to reload the board, so changes made by teammates show up.
const REFRESH_MS = 15_000;

export default function App() {
  const [tasks, setTasks] = useState([]);
  // null, or { noteId, tasks } while the user is reviewing AI suggestions.
  const [review, setReview] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // useCallback keeps the same function between renders, so the effect
  // below doesn't restart its timer every time the page re-renders.
  const loadTasks = useCallback(async () => {
    try {
      setTasks(await api.fetchTasks());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Load the board once, then refresh it every REFRESH_MS.
  // The function we return runs when the component goes away: it stops the timer.
  useEffect(() => {
    loadTasks();
    const timer = setInterval(loadTasks, REFRESH_MS);
    return () => clearInterval(timer);
  }, [loadTasks]);

  // Run an API call, show its error message if it fails.
  async function attempt(action) {
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleExtract(text, meetingDate) {
    setExtracting(true);
    await attempt(async () => {
      const result = await api.extractTasks(text, meetingDate);
      setReview({ noteId: result.note_id, tasks: result.tasks });
    });
    setExtracting(false);
  }

  async function handleApprove(approved) {
    setSaving(true);
    await attempt(async () => {
      const saved = await api.approveTasks(review.noteId, approved);
      setTasks((current) => [...current, ...saved]);
      setReview(null);
    });
    setSaving(false);
  }

  async function handleAdd(task) {
    await attempt(async () => {
      const saved = await api.createTask(task);
      setTasks((current) => [...current, saved]);
    });
  }

  async function handleMove(task, status) {
    await attempt(async () => {
      const updated = await api.updateTask(task.id, { status });
      setTasks((current) => current.map((t) => (t.id === updated.id ? updated : t)));
    });
  }

  async function handleDelete(task) {
    if (!window.confirm(`Delete "${task.title}"?`)) return;
    await attempt(async () => {
      await api.deleteTask(task.id);
      setTasks((current) => current.filter((t) => t.id !== task.id));
    });
  }

  return (
    <div className="page">
      <header className="top-bar">
        <div>
          <h1>notes-to-tasks</h1>
          <p className="subtitle">Paste meeting notes. Get tasks on a shared board.</p>
        </div>
        <HealthBadge />
      </header>

      {error && (
        <p className="error-banner" role="alert">
          {error}
          <button className="link-button" onClick={() => setError(null)}>
            Dismiss
          </button>
        </p>
      )}

      <div className="steps">
        {review ? (
          <ReviewPanel
            // A new key for each note resets the panel's editable copy.
            key={review.noteId}
            suggestions={review.tasks}
            onApprove={handleApprove}
            onDiscard={() => setReview(null)}
            busy={saving}
          />
        ) : (
          <NotesForm onExtract={handleExtract} busy={extracting} />
        )}
      </div>

      <TaskBoard tasks={tasks} onMove={handleMove} onDelete={handleDelete} onAdd={handleAdd} />
    </div>
  );
}
