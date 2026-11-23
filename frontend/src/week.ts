/** Jour au format ISO, sans heure ni fuseau : "2026-11-02". */
export type IsoDate = string;

/** Écrit une date locale au format ISO, sans heure. */
export function toIsoDate(date: Date): IsoDate {
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}
