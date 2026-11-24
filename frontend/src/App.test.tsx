import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "./App";

const STAFF = [{ code: "nurse-1", full_name: "Alice Martin" }];

/** Remplace fetch : chaque adresse connue reçoit son JSON, les autres une erreur 404 comme DRF. */
function mockApi(responses: Record<string, unknown>) {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const body = responses[String(input)];
    return body === undefined
      ? Response.json({ detail: "Introuvable." }, { status: 404 })
      : Response.json(body);
  });
}

/** Réponses de l'API pour une semaine sans poste ni infraction. */
function weekResponses(start: string, end: string) {
  return {
    "/api/staff/": STAFF,
    [`/api/shifts/?start=${start}&end=${end}`]: [],
    [`/api/schedule/violations/?start=${start}&end=${end}`]: { violations: [] },
  };
}

describe("App", () => {
  it("shows the week of the initial date", async () => {
    const fetchMock = mockApi(weekResponses("2026-11-02", "2026-11-08"));

    render(<App initialDate="2026-11-04" />);

    expect(await screen.findByRole("rowheader", { name: "Alice Martin" })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Semaine du 02/11/2026 au 08/11/2026" }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/shifts/?start=2026-11-02&end=2026-11-08");
  });
});
