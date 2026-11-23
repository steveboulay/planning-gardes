import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { StaffMember, StoredShift } from "./api";
import { WeekGrid } from "./WeekGrid";
import { weekDays } from "./week";

const DAYS = weekDays("2026-11-02");

const STAFF: StaffMember[] = [
  { code: "nurse-1", full_name: "Alice Martin" },
  { code: "nurse-2", full_name: "Bruno Petit" },
];

function shift(
  id: number,
  staff: string,
  start: string,
  end: string,
  kind: StoredShift["kind"],
): StoredShift {
  return { id, staff, start, end, kind };
}

/** Cellule d'un soignant pour un jour de la semaine, de 0 (lundi) à 6 (dimanche). */
function cellOf(fullName: string, dayIndex: number) {
  const row = screen.getByRole("rowheader", { name: fullName }).closest("tr")!;
  return within(row).getAllByRole("cell")[dayIndex];
}

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

  it("shows a shift in the cell of its staff member and start day", () => {
    const shifts = [shift(1, "nurse-2", "2026-11-03T08:00:00", "2026-11-03T20:00:00", "jour")];

    render(<WeekGrid days={DAYS} staff={STAFF} shifts={shifts} violations={[]} />);

    expect(cellOf("Bruno Petit", 1)).toHaveTextContent("Jour 08:00–20:00");
    expect(cellOf("Alice Martin", 1)).toBeEmptyDOMElement();
    expect(cellOf("Bruno Petit", 0)).toBeEmptyDOMElement();
  });
});
