import type { IsoDate } from "./week";

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
