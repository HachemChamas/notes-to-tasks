import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchHealth } from "../api.js";
import HealthBadge from "./HealthBadge.jsx";

vi.mock("../api.js", () => ({ fetchHealth: vi.fn() }));

beforeEach(() => vi.resetAllMocks());

describe("HealthBadge", () => {
  it("says all is well when the API and database are up", async () => {
    fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });

    render(<HealthBadge />);

    expect(await screen.findByText("All systems ok")).toBeInTheDocument();
  });

  it("reports a database problem", async () => {
    fetchHealth.mockResolvedValue({ status: "ok", database: "unavailable" });

    render(<HealthBadge />);

    expect(await screen.findByText("Database: unavailable")).toBeInTheDocument();
  });

  it("checks again when the button is clicked", async () => {
    const user = userEvent.setup();
    fetchHealth.mockRejectedValueOnce(new Error("Could not reach the backend"));
    fetchHealth.mockResolvedValueOnce({ status: "ok", database: "ok" });

    render(<HealthBadge />);
    expect(await screen.findByText("Could not reach the backend")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Check again" }));

    expect(await screen.findByText("All systems ok")).toBeInTheDocument();
    expect(fetchHealth).toHaveBeenCalledTimes(2);
  });
});
