import { type IsoDate, weekDays } from "./week";

/** Soignant, tel que le renvoie /api/staff/. */
export type StaffMember = {
  code: string;
  full_name: string;
};

/** Poste enregistré, tel que le renvoie /api/shifts/ : heures locales, sans fuseau. */
export type StoredShift = {
  id: number;
  staff: string;
  start: string;
  end: string;
  kind: "jour" | "nuit";
};

/** Infraction, telle que la renvoie /api/schedule/violations/. */
export type Violation = {
  rule: string;
  category: string;
  staff_id: string;
  day: IsoDate;
  message: string;
};

/** Tout ce qu'affiche la page pour une semaine. */
export type WeekSchedule = {
  staff: StaffMember[];
  shifts: StoredShift[];
  violations: Violation[];
};

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  return (await response.json()) as T;
}

/** Soignants, postes et infractions de la semaine qui commence ce lundi. */
export async function fetchWeekSchedule(monday: IsoDate): Promise<WeekSchedule> {
  const days = weekDays(monday);
  const period = new URLSearchParams({ start: days[0], end: days[6] }).toString();
  const [staff, shifts, report] = await Promise.all([
    getJson<StaffMember[]>("/api/staff/"),
    getJson<StoredShift[]>(`/api/shifts/?${period}`),
    getJson<{ violations: Violation[] }>(`/api/schedule/violations/?${period}`),
  ]);
  return { staff, shifts, violations: report.violations };
}
