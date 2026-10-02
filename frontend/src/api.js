// All calls to the backend live in this file, so components never have to
// know URLs or how fetch() works.

// The backend's address, from VITE_API_URL in the root .env file.
// Vite replaces import.meta.env.VITE_... with the real value at build time.
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Calls GET /health and returns the JSON, e.g.
//   { status: "ok", database: "ok" }
// Throws an Error if the backend can't be reached or answers with an error.
export async function fetchHealth() {
  let response;
  try {
    response = await fetch(`${API_URL}/health`);
  } catch {
    // fetch() only throws when there is no answer at all (server down,
    // wrong URL, CORS blocked). Replace its vague message with a useful one.
    throw new Error(`Could not reach the backend at ${API_URL}. Is it running?`);
  }

  if (!response.ok) {
    throw new Error(`The backend answered with HTTP ${response.status}.`);
  }
  return response.json();
}
