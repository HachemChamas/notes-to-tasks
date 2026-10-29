import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import ReviewPanel from "./ReviewPanel.jsx";

const suggestions = [
  { title: "Book a room", description: "For the retro", owner_name: null, due_date: null },
  { title: "Fix login bug", description: null, owner_name: "Alan", due_date: "2026-11-04" },
];

describe("ReviewPanel", () => {
  it("sends the edited tasks the user kept", async () => {
    const user = userEvent.setup();
    const onApprove = vi.fn();
    render(<ReviewPanel suggestions={suggestions} onApprove={onApprove} onDiscard={vi.fn()} />);

    // Give the first task an owner, and drop the second one.
    const [firstOwner] = screen.getAllByLabelText("Owner");
    await user.type(firstOwner, "Grace");
    await user.click(screen.getByLabelText('Keep "Fix login bug"'));
    await user.click(screen.getByRole("button", { name: "Add 1 task to board" }));

    expect(onApprove).toHaveBeenCalledWith([
      { title: "Book a room", description: "For the retro", owner_name: "Grace", due_date: null },
    ]);
  });

  it("can't approve when every task is unticked", async () => {
    const user = userEvent.setup();
    render(<ReviewPanel suggestions={[suggestions[0]]} onApprove={vi.fn()} onDiscard={vi.fn()} />);

    await user.click(screen.getByLabelText('Keep "Book a room"'));

    expect(screen.getByRole("button", { name: "Add 0 tasks to board" })).toBeDisabled();
  });

  it("explains when no tasks were found", () => {
    render(<ReviewPanel suggestions={[]} onApprove={vi.fn()} onDiscard={vi.fn()} />);

    expect(screen.getByText(/didn.t find any tasks/)).toBeInTheDocument();
  });
});
