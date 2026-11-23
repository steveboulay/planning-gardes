/** Jour au format ISO, sans heure ni fuseau : "2026-11-02". */
export type IsoDate = string;

/** Construit la date locale d'un jour ISO, à minuit. */
function toDate(day: IsoDate): Date {
  const [year, month, date] = day.split("-").map(Number);
  return new Date(year, month - 1, date);
}

/** Écrit une date locale au format ISO, sans heure. */
export function toIsoDate(date: Date): IsoDate {
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

/** Vrai pour un jour ISO qui existe : relu puis réécrit, "2026-02-30" ne redonne pas la même chaîne. */
export function isIsoDate(value: string): boolean {
  return toIsoDate(toDate(value)) === value;
}
