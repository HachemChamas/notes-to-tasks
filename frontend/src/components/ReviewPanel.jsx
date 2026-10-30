// Step 2: the user checks the AI's suggestions, edits them, and approves.
// Nothing reaches the board until "Add to board" is clicked.
import { useState } from "react";

export default function ReviewPanel({ suggestions, onApprove, onDiscard, busy }) {
  // A local, editable copy of the suggestions. `keep` is the checkbox.
  const [items, setItems] = useState(() =>
    suggestions.map((task) => ({
      ...task,
      owner_name: task.owner_name ?? "",
      due_date: task.due_date ?? "",
      keep: true,
    })),
  );

  // Change one field of one item. We build a new array instead of changing
  // the old one, because React only re-renders when state is replaced.
  function updateItem(index, field, value) {
    setItems((current) =>
      current.map((item, i) => (i === index ? { ...item, [field]: value } : item)),
    );
  }

  const kept = items.filter((item) => item.keep && item.title.trim());

  function handleApprove() {
    onApprove(
      kept.map((item) => ({
        title: item.title.trim(),
        description: item.description || null,
        owner_name: item.owner_name.trim() || null,
        due_date: item.due_date || null,
      })),
    );
  }

  if (items.length === 0) {
    return (
      <section className="card">
        <h2>2. Review</h2>
        <p>The AI didn&apos;t find any tasks in those notes.</p>
        <button onClick={onDiscard}>Try other notes</button>
      </section>
    );
  }

  return (
    <section className="card">
      <div className="card-header">
        <h2>2. Review the suggested tasks</h2>
        <span className="hint">Untick anything that isn&apos;t a real task.</span>
      </div>

      <ul className="review-list">
        {items.map((item, index) => (
          <li key={index} className={item.keep ? "" : "dropped"}>
            <input
              type="checkbox"
              checked={item.keep}
              onChange={(event) => updateItem(index, "keep", event.target.checked)}
              aria-label={`Keep "${item.title}"`}
            />
            <div className="review-fields">
              <input
                className="title-input"
                value={item.title}
                onChange={(event) => updateItem(index, "title", event.target.value)}
                aria-label="Title"
              />
              {item.description && <p className="hint">{item.description}</p>}
              <div className="row">
                <input
                  value={item.owner_name}
                  onChange={(event) => updateItem(index, "owner_name", event.target.value)}
                  placeholder="Unassigned"
                  aria-label="Owner"
                />
                <input
                  type="date"
                  value={item.due_date}
                  onChange={(event) => updateItem(index, "due_date", event.target.value)}
                  aria-label="Due date"
                />
              </div>
            </div>
          </li>
        ))}
      </ul>

      <div className="row end">
        <button onClick={onDiscard} disabled={busy}>
          Discard
        </button>
        <button className="primary" onClick={handleApprove} disabled={busy || kept.length === 0}>
          {busy ? "Saving…" : `Add ${kept.length} ${kept.length === 1 ? "task" : "tasks"} to board`}
        </button>
      </div>
    </section>
  );
}
