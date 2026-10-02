// Configuration for Vite (the dev server and build tool) and Vitest
// (the test runner, which reuses Vite's settings).
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Lets Vite understand JSX and React features.
  plugins: [react()],

  // Read .env from the repo root (one folder up) instead of from frontend/,
  // so the whole project shares a single .env file.
  envDir: "..",

  server: {
    port: 5173,
  },

  test: {
    // Tests run in Node, not a real browser. jsdom fakes a browser page
    // (document, window, ...) so React components can render in tests.
    environment: "jsdom",
    // Runs before every test file. Adds matchers like toBeInTheDocument().
    setupFiles: "./src/setupTests.js",
  },
});
