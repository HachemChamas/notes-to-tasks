// All calls to the backend live in this file, so components never have to
// know URLs or how fetch() works. Every function returns parsed JSON or
// throws an Error with a message that is safe to show to the user.

// The backend's address, from VITE_API_URL in the root .env file.
// Vite replaces import.meta.env.VITE_... with the real value at build time.
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Shared helper: send a request, turn failures into readable errors.
async function request(path, { method = "GET", body } = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    // fetch() only throws when there is no answer at all (server down,
    // wrong URL, CORS blocked). Replace its vague message with a useful one.
    throw new Error(`Could not reach the backend at ${API_URL}. Is it running?`);
  }

  if (!response.ok) {
    // FastAPI puts error messages in {"detail": ...}. For validation
    // errors (422) detail is a list, so fall back to a generic message.
    let message = `The backend answered with HTTP ${response.status}.`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch {
      // The body wasn't JSON; keep the generic message.
    }
    throw new Error(message);
  }

  // 204 No Content (e.g. after DELETE) has no body to parse.
  return response.status === 204 ? null : response.json();
}

// GET /health -> { status: "ok", database: "ok" | "unavailable" }
export function fetchHealth() {
  return request("/health");
}

// POST /extract -> { note_id, tasks: [{ title, description, owner_name, due_date }] }
export function extractTasks(text, meetingDate) {
  return request("/extract", {
    method: "POST",
    body: { text, meeting_date: meetingDate || null },
  });
}

// POST /tasks/bulk -> the saved tasks
export function approveTasks(noteId, tasks) {
  return request("/tasks/bulk", { method: "POST", body: { note_id: noteId, tasks } });
}

// POST /tasks -> the saved task
export function createTask(task) {
  return request("/tasks", { method: "POST", body: task });
}

// GET /tasks -> every task on the board
export function fetchTasks() {
  return request("/tasks");
}

// PATCH /tasks/:id -> the updated task. Only the fields in `changes` change.
export function updateTask(id, changes) {
  return request(`/tasks/${id}`, { method: "PATCH", body: changes });
}

// DELETE /tasks/:id
export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: "DELETE" });
}
