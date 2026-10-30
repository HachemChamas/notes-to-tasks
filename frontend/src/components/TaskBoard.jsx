// Step 3: the shared board. Three columns, a filter, and a quick "add" form.
import { useState } from "react";

import { todayString } from "../dates.js";
import TaskCard from "./TaskCard.jsx";

// The order here is the order of the columns, left to right.
export const COLUMNS = [
  { status: "todo", title: "To do" },
  { status: "in_progress", title: "In progress" },
  { status: "done", title: "Done" },
];

export default function TaskBoard({ tasks, onMove, onDelete, onAdd, today = todayString() }) {
  const [ownerFilter, setOwnerFilter] = useState("all");
  const [newTitle, setNewTitle] = useState("");

  // Everyone who owns at least one task, for the filter dropdown.
  // A Map keyed by id removes duplicates.
  const owners = [
    ...new Map(tasks.filter((t) => t.owner).map((t) => [t.owner.id, t.owner])).values(),
  ].sort((a, b) => a.name.localeCompare(b.name));

  const visible = tasks.filter((task) => {
    if (ownerFilter === "all") return true;
    if (ownerFilter === "none") return !task.owner;
    return task.owner?.id === Number(ownerFilter);
  });

  function handleAdd(event) {
    event.preventDefault();
    if (!newTitle.trim()) return;
    onAdd({ title: newTitle.trim() });
    setNewTitle("");
  }

  // Columns move by index, so "forward" from column 0 is COLUMNS[1].
  function moveTo(task, index) {
    onMove(task, COLUMNS[index].status);
  }

  return (
    <section className="board-section">
      <div className="board-toolbar">
        <h2>3. Task board</h2>
        <form className="row" onSubmit={handleAdd}>
          <input
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
            placeholder="Add a task by hand"
            aria-label="New task title"
          />
          <button type="submit" disabled={!newTitle.trim()}>
            Add
          </button>
        </form>
        <label className="inline">
          Show
          <select value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)}>
            <option value="all">Everyone</option>
            <option value="none">Unassigned</option>
            {owners.map((owner) => (
              <option key={owner.id} value={owner.id}>
                {owner.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="board">
        {COLUMNS.map((column, columnIndex) => {
          const columnTasks = visible.filter((task) => task.status === column.status);
          return (
            <div key={column.status} className="column" aria-label={column.title}>
              <h3>
                {column.title} <span className="count">{columnTasks.length}</span>
              </h3>
              {columnTasks.length === 0 && <p className="empty">Nothing here</p>}
              <ul>
                {columnTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    columnIndex={columnIndex}
                    columnCount={COLUMNS.length}
                    today={today}
                    onMove={moveTo}
                    onDelete={onDelete}
                  />
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </section>
  );
}
