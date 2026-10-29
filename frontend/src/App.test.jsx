// End-to-end flow of the page, with the backend faked.
// Run all frontend tests with: npm test
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import * as api from "./api.js";

// Replace every function in api.js with a fake (vi.fn), so tests never
// need a running backend. Each test decides what the fakes return.
vi.mock("./api.js", () => ({
  fetchHealth: vi.fn(),
  extractTasks: vi.fn(),
  approveTasks: vi.fn(),
  createTask: vi.fn(),
  fetchTasks: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
}));

const savedTask = {
  id: 1,
  title: "Send the budget",
  description: null,
  status: "todo",
  due_date: "2099-11-06",
  owner: { id: 7, name: "Ada" },
  note_id: 3,
};

beforeEach(() => {
  vi.resetAllMocks();
  api.fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });
  api.fetchTasks.mockResolvedValue([]);
});

describe("App", () => {
  it("goes from pasted notes to tasks on the board", async () => {
    const user = userEvent.setup();
    api.extractTasks.mockResolvedValue({
      note_id: 3,
      tasks: [
        { title: "Send the budget", description: null, owner_name: "Ada", due_date: "2099-11-06" },
        { title: "Not really a task", description: null, owner_name: null, due_date: null },
      ],
    });
    api.approveTasks.mockResolvedValue([savedTask]);

    render(<App />);

    // 1. Paste notes and ask for tasks.
    await user.type(screen.getByLabelText(/meeting notes/i), "Ada sends the budget");
    await user.click(screen.getByRole("button", { name: "Find tasks" }));
    expect(api.extractTasks).toHaveBeenCalledWith("Ada sends the budget", expect.any(String));

    // 2. Untick the second suggestion, then approve.
    await user.click(await screen.findByLabelText('Keep "Not really a task"'));
    await user.click(screen.getByRole("button", { name: "Add 1 task to board" }));
    expect(api.approveTasks).toHaveBeenCalledWith(3, [
      { title: "Send the budget", description: null, owner_name: "Ada", due_date: "2099-11-06" },
    ]);

    // 3. The saved task is on the board, in the "To do" column.
    const todo = await screen.findByLabelText("To do");
    expect(within(todo).getByText("Send the budget")).toBeInTheDocument();
    expect(within(todo).getByText("Ada")).toBeInTheDocument();
    // And we're back at step 1, ready for the next notes.
    expect(screen.getByRole("button", { name: "Find tasks" })).toBeInTheDocument();
  });

  it("shows the backend's error message when extraction fails", async () => {
    const user = userEvent.setup();
    api.extractTasks.mockRejectedValue(new Error("The AI service is busy."));

    render(<App />);
    await user.type(screen.getByLabelText(/meeting notes/i), "some notes");
    await user.click(screen.getByRole("button", { name: "Find tasks" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("The AI service is busy.");
  });

  it("moves a task to the next column", async () => {
    const user = userEvent.setup();
    api.fetchTasks.mockResolvedValue([savedTask]);
    api.updateTask.mockResolvedValue({ ...savedTask, status: "in_progress" });

    render(<App />);
    await user.click(await screen.findByLabelText('Move "Send the budget" forward'));

    expect(api.updateTask).toHaveBeenCalledWith(1, { status: "in_progress" });
    const inProgress = screen.getByLabelText("In progress");
    expect(await within(inProgress).findByText("Send the budget")).toBeInTheDocument();
  });
});
