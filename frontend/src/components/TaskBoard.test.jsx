import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import TaskBoard from "./TaskBoard.jsx";

const ada = { id: 1, name: "Ada" };
const tasks = [
  { id: 1, title: "Write report", status: "todo", due_date: "2026-10-01", owner: ada },
  { id: 2, title: "Review PR", status: "in_progress", due_date: null, owner: null },
  { id: 3, title: "Ship v1", status: "done", due_date: "2026-09-01", owner: ada },
];

function renderBoard(props = {}) {
  const handlers = { onMove: vi.fn(), onDelete: vi.fn(), onAdd: vi.fn() };
  render(<TaskBoard tasks={tasks} today="2026-10-15" {...handlers} {...props} />);
  return handlers;
}

describe("TaskBoard", () => {
  it("puts each task in the column for its status", () => {
    renderBoard();

    expect(within(screen.getByLabelText("To do")).getByText("Write report")).toBeInTheDocument();
    expect(within(screen.getByLabelText("In progress")).getByText("Review PR")).toBeInTheDocument();
    expect(within(screen.getByLabelText("Done")).getByText("Ship v1")).toBeInTheDocument();
  });

  it("marks late tasks as overdue, but not finished ones", () => {
    renderBoard();

    expect(screen.getByText(/Overdue/)).toHaveTextContent("Overdue · Thu, Oct 1");
    expect(screen.getAllByText(/Overdue/)).toHaveLength(1); // "Ship v1" is done
  });

  it("moves tasks forward and back", async () => {
    const user = userEvent.setup();
    const { onMove } = renderBoard();

    await user.click(screen.getByLabelText('Move "Review PR" forward'));
    await user.click(screen.getByLabelText('Move "Review PR" back'));

    expect(onMove).toHaveBeenNthCalledWith(1, tasks[1], "done");
    expect(onMove).toHaveBeenNthCalledWith(2, tasks[1], "todo");
    // The first column can't go back and the last can't go forward.
    expect(screen.getByLabelText('Move "Write report" back')).toBeDisabled();
    expect(screen.getByLabelText('Move "Ship v1" forward')).toBeDisabled();
  });

  it("filters by owner", async () => {
    const user = userEvent.setup();
    renderBoard();

    await user.selectOptions(screen.getByLabelText("Show"), "Unassigned");

    expect(screen.getByText("Review PR")).toBeInTheDocument();
    expect(screen.queryByText("Write report")).not.toBeInTheDocument();
  });

  it("adds a task typed by hand", async () => {
    const user = userEvent.setup();
    const { onAdd } = renderBoard();

    await user.type(screen.getByLabelText("New task title"), "Order pizza{Enter}");

    expect(onAdd).toHaveBeenCalledWith({ title: "Order pizza" });
    expect(screen.getByLabelText("New task title")).toHaveValue("");
  });
});
