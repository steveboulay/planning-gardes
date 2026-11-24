import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { Violation } from "./api";
import { ViolationList } from "./ViolationList";

describe("ViolationList", () => {
  it("lists the messages of the violations, in the given order", () => {
    const violations: Violation[] = [
      {
        rule: "desiderata",
        category: "individuelle",
        staff_id: "nurse-3",
        day: "2026-11-06",
        message: "Soignant nurse-3 : poste le 06/11/2026, jour de repos demandé.",
      },
      {
        rule: "repos_quotidien",
        category: "légale",
        staff_id: "nurse-1",
        day: "2026-11-03",
        message: "Soignant nurse-1 : repos de 11:00 inférieur à 12:00.",
      },
    ];

    render(<ViolationList violations={violations} />);

    const items = screen.getAllByRole("listitem").map((item) => item.textContent);
    expect(items).toEqual([
      "Soignant nurse-3 : poste le 06/11/2026, jour de repos demandé.",
      "Soignant nurse-1 : repos de 11:00 inférieur à 12:00.",
    ]);
  });

  it("says when the week has no violation", () => {
    render(<ViolationList violations={[]} />);

    expect(screen.getByText("Aucune infraction cette semaine.")).toBeInTheDocument();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("lists two identical messages", () => {
    const consoleError = vi.spyOn(console, "error");
    const tuesday: Violation = {
      rule: "repos_quotidien",
      category: "légale",
      staff_id: "nurse-1",
      day: "2026-11-03",
      message: "Soignant nurse-1 : repos de 11:00 inférieur à 12:00.",
    };
    const thursday = { ...tuesday, day: "2026-11-05" };

    render(<ViolationList violations={[tuesday, thursday]} />);

    expect(screen.getAllByText(tuesday.message)).toHaveLength(2);
    expect(consoleError).not.toHaveBeenCalled();
  });
});
