import { describe, expect, it } from "vitest";

import { toIsoDate, isIsoDate, mondayOf, weekDays } from "./week";

describe("toIsoDate", () => {
  it("pads the month and the day with zeros", () => {
    expect(toIsoDate(new Date(2026, 0, 5))).toBe("2026-01-05");
  });
});

describe("isIsoDate", () => {
  it("accepts an existing day", () => {
    expect(isIsoDate("2026-11-02")).toBe(true);
  });

  it("rejects a malformed or impossible day", () => {
    expect(isIsoDate("2026-11-2")).toBe(false);
    expect(isIsoDate("demain")).toBe(false);
    expect(isIsoDate("2026-02-30")).toBe(false);
  });
});

describe("mondayOf", () => {
  it("returns the Monday of a Wednesday", () => {
    expect(mondayOf("2026-11-04")).toBe("2026-11-02");
  });

  it("returns the day itself for a Monday", () => {
    expect(mondayOf("2026-11-02")).toBe("2026-11-02");
  });

  it("returns the previous Monday for a Sunday", () => {
    expect(mondayOf("2026-11-08")).toBe("2026-11-02");
  });
});

describe("weekDays", () => {
  it("returns the seven days from Monday to Sunday", () => {
    expect(weekDays("2026-11-02")).toEqual([
      "2026-11-02",
      "2026-11-03",
      "2026-11-04",
      "2026-11-05",
      "2026-11-06",
      "2026-11-07",
      "2026-11-08",
    ]);
  });
});
