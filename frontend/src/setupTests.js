// Runs before every test file (see `setupFiles` in vite.config.js).
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Adds extra checks such as expect(element).toBeInTheDocument().
import "@testing-library/jest-dom/vitest";

// Remove whatever a test rendered, so the next test starts with an empty page.
afterEach(() => {
  cleanup();
});
