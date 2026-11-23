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

/** Vrai pour un jour ISO qui existe : "2026-02-30" relu puis réécrit donne "2026-03-02". */
export function isIsoDate(value: string): boolean {
  return toIsoDate(toDate(value)) === value;
}

/** Ajoute des jours au calendrier, sans passer par des millisecondes. */
function addDays(day: IsoDate, days: number): IsoDate {
  const date = toDate(day);
  date.setDate(date.getDate() + days);
  return toIsoDate(date);
}

/** Lundi de la semaine d'un jour, du lundi au dimanche. */
export function mondayOf(day: IsoDate): IsoDate {
  const daysSinceMonday = (toDate(day).getDay() + 6) % 7;
  return addDays(day, -daysSinceMonday);
}

/** Les sept jours, du lundi au dimanche, de la semaine qui contient ce jour. */
export function weekDays(day: IsoDate): IsoDate[] {
  const monday = mondayOf(day);
  return Array.from({ length: 7 }, (_, index) => addDays(monday, index));
}
