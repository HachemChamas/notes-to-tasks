// One task on the board, with buttons to move it between columns.
import { formatDate, isOverdue } from "../dates.js";

export default function TaskCard({ task, columnIndex, columnCount, today, onMove, onDelete }) {
  const overdue = task.status !== "done" && isOverdue(task.due_date, today);

  return (
    <li className={`task-card ${overdue ? "overdue" : ""}`}>
      <p className="task-title">{task.title}</p>
      {task.description && <p className="hint">{task.description}</p>}

      <div className="task-meta">
        <span className="owner">{task.owner ? task.owner.name : "Unassigned"}</span>
        {task.due_date && (
          <span className="due">
            {overdue ? "Overdue · " : "Due "}
            {formatDate(task.due_date)}
          </span>
        )}
      </div>

      <div className="task-actions">
        <button
          onClick={() => onMove(task, columnIndex - 1)}
          disabled={columnIndex === 0}
          aria-label={`Move "${task.title}" back`}
        >
          ←
        </button>
        <button
          onClick={() => onMove(task, columnIndex + 1)}
          disabled={columnIndex === columnCount - 1}
          aria-label={`Move "${task.title}" forward`}
        >
          →
        </button>
        <button
          className="danger"
          onClick={() => onDelete(task)}
          aria-label={`Delete "${task.title}"`}
        >
          Delete
        </button>
      </div>
    </li>
  );
}
