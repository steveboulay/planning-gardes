import { act, render, screen } from "@testing-library/react";
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

/**
 * Comme mockApi pour les semaines du 2 et du 9 novembre, sauf les infractions de la semaine
 * du 2 : elles n'arrivent que lorsque le test appelle la fonction renvoyée.
 */
function mockApiWithLateFirstWeek() {
  const responses: Record<string, unknown> = {
    ...weekResponses("2026-11-02", "2026-11-08"),
    ...weekResponses("2026-11-09", "2026-11-15"),
  };
  let answer: (response: Response) => void = () => {};
  vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = String(input);
    if (url === "/api/schedule/violations/?start=2026-11-02&end=2026-11-08") {
      return new Promise((resolve) => {
        answer = resolve;
      });
    }
    return Promise.resolve(Response.json(responses[url]));
  });
  return (response: Response) => answer(response);
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

  it("hides the previous week while the next one loads", async () => {
    const firstWeek: Record<string, unknown> = weekResponses("2026-11-02", "2026-11-08");
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const body = firstWeek[String(input)];
      // La semaine suivante ne répond jamais : la page reste en cours de chargement
      return body === undefined ? new Promise(() => {}) : Promise.resolve(Response.json(body));
    });
    render(<App initialDate="2026-11-04" />);
    await screen.findByRole("rowheader", { name: "Alice Martin" });

    await userEvent.click(screen.getByRole("button", { name: "Semaine suivante" }));

    expect(screen.getByText("Chargement…")).toBeInTheDocument();
    expect(screen.queryByRole("rowheader", { name: "Alice Martin" })).not.toBeInTheDocument();
  });

  it("loads the previous week", async () => {
    const fetchMock = mockApi({
      ...weekResponses("2026-11-02", "2026-11-08"),
      ...weekResponses("2026-11-09", "2026-11-15"),
    });
    render(<App initialDate="2026-11-09" />);
    await screen.findByRole("rowheader", { name: "Alice Martin" });

    await userEvent.click(screen.getByRole("button", { name: "Semaine précédente" }));

    expect(
      await screen.findByRole("heading", { name: "Semaine du 02/11/2026 au 08/11/2026" }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/shifts/?start=2026-11-02&end=2026-11-08");
  });

  it("shows an error when the API fails", async () => {
    mockApi({});

    render(<App initialDate="2026-11-04" />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Impossible de charger le planning.",
    );
    expect(screen.queryByText("Chargement…")).not.toBeInTheDocument();
  });

  it("clears the error when another week loads", async () => {
    mockApi(weekResponses("2026-11-09", "2026-11-15"));
    render(<App initialDate="2026-11-04" />);
    await screen.findByRole("alert");

    await userEvent.click(screen.getByRole("button", { name: "Semaine suivante" }));

    expect(await screen.findByRole("rowheader", { name: "Alice Martin" })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("ignores the late answer of a week that is no longer shown", async () => {
    const answerFirstWeek = mockApiWithLateFirstWeek();
    const lateMessage = "Infraction de la semaine du 2 novembre.";
    render(<App initialDate="2026-11-04" />);
    await userEvent.click(screen.getByRole("button", { name: "Semaine suivante" }));
    await screen.findByText("Aucune infraction cette semaine.");

    await act(async () => {
      answerFirstWeek(Response.json({ violations: [{ message: lateMessage }] }));
    });

    expect(screen.queryByText(lateMessage)).not.toBeInTheDocument();
  });

  it("ignores the late failure of a week that is no longer shown", async () => {
    const answerFirstWeek = mockApiWithLateFirstWeek();
    render(<App initialDate="2026-11-04" />);
    await userEvent.click(screen.getByRole("button", { name: "Semaine suivante" }));
    await screen.findByText("Aucune infraction cette semaine.");

    await act(async () => {
      answerFirstWeek(Response.json({ detail: "Erreur." }, { status: 500 }));
    });

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
