import { describe, expect, it } from "vitest";

import { toIsoDate } from "./week";

describe("toIsoDate", () => {
  it("pads the month and the day with zeros", () => {
    expect(toIsoDate(new Date(2026, 0, 5))).toBe("2026-01-05");
  });
});
