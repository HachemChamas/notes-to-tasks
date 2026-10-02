// Tests for the App component. Run them with: npm test
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { fetchHealth } from "./api.js";

// Replace the real api.js with a fake version, so tests never need a
// running backend. Each test decides what the fake fetchHealth returns.
vi.mock("./api.js", () => ({
  fetchHealth: vi.fn(),
}));

describe("App", () => {
  it("shows the backend and database status from /health", async () => {
    // Pretend the backend answered with this JSON.
    fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });

    render(<App />);

    // findByText waits until the text appears, because the health check
    // finishes a moment after the first render.
    expect(await screen.findByText(/API:/)).toHaveTextContent("API: ok");
    expect(screen.getByText(/Database:/)).toHaveTextContent("Database: ok");
    expect(fetchHealth).toHaveBeenCalledTimes(1);
  });
});
