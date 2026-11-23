import { describe, expect, it } from "vitest";

import { toIsoDate, isIsoDate } from "./week";

describe("toIsoDate", () => {
  it("pads the month and the day with zeros", () => {
    expect(toIsoDate(new Date(2026, 0, 5))).toBe("2026-01-05");
  });
});

describe("isIsoDate", () => {
  it("accepts an existing day", () => {
    expect(isIsoDate("2026-11-02")).toBe(true);
  });
});
