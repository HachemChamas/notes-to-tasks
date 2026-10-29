import { describe, expect, it } from "vitest";

import { formatDate, isOverdue } from "./dates.js";

describe("dates", () => {
  it("formats a date without shifting it a day", () => {
    expect(formatDate("2026-11-06")).toBe("Fri, Nov 6");
  });

  it("knows when a date is in the past", () => {
    expect(isOverdue("2026-10-14", "2026-10-15")).toBe(true);
    expect(isOverdue("2026-10-15", "2026-10-15")).toBe(false); // due today is fine
    expect(isOverdue(null, "2026-10-15")).toBe(false);
  });
});
