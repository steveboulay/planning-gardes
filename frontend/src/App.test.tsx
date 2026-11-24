import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

  it("shows a loading message until the week arrives", async () => {
    mockApi(weekResponses("2026-11-02", "2026-11-08"));

    render(<App initialDate="2026-11-04" />);

    expect(screen.getByText("Chargement…")).toBeInTheDocument();
    expect(await screen.findByRole("rowheader", { name: "Alice Martin" })).toBeInTheDocument();
    expect(screen.queryByText("Chargement…")).not.toBeInTheDocument();
  });

  it("loads the next week", async () => {
    const fetchMock = mockApi({
      ...weekResponses("2026-11-02", "2026-11-08"),
      ...weekResponses("2026-11-09", "2026-11-15"),
    });
    render(<App initialDate="2026-11-04" />);
    await screen.findByRole("rowheader", { name: "Alice Martin" });

    await userEvent.click(screen.getByRole("button", { name: "Semaine suivante" }));

    expect(
      await screen.findByRole("heading", { name: "Semaine du 09/11/2026 au 15/11/2026" }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/shifts/?start=2026-11-09&end=2026-11-15");
  });
});
