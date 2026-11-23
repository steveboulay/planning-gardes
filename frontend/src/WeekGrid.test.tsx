import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { StaffMember } from "./api";
import { WeekGrid } from "./WeekGrid";
import { weekDays } from "./week";

const DAYS = weekDays("2026-11-02");

const STAFF: StaffMember[] = [
  { code: "nurse-1", full_name: "Alice Martin" },
  { code: "nurse-2", full_name: "Bruno Petit" },
];

describe("WeekGrid", () => {
  it("shows one column per day of the week", () => {
    render(<WeekGrid days={DAYS} staff={STAFF} shifts={[]} violations={[]} />);

    const headers = screen.getAllByRole("columnheader").map((header) => header.textContent);
    expect(headers).toEqual([
      "Soignant",
      "lun. 02/11",
      "mar. 03/11",
      "mer. 04/11",
      "jeu. 05/11",
      "ven. 06/11",
      "sam. 07/11",
      "dim. 08/11",
    ]);
  });

  it("shows one row per staff member, in the given order", () => {
    const staff = [STAFF[1], STAFF[0]];

    render(<WeekGrid days={DAYS} staff={staff} shifts={[]} violations={[]} />);

    const names = screen.getAllByRole("rowheader").map((header) => header.textContent);
    expect(names).toEqual(["Bruno Petit", "Alice Martin"]);
  });
});
