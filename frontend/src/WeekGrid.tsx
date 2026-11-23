import type { StaffMember, StoredShift, Violation } from "./api";
import { type IsoDate, formatDayHeader } from "./week";

type WeekGridProps = {
  days: IsoDate[];
  staff: StaffMember[];
  shifts: StoredShift[];
  violations: Violation[];
};

/** Grille de la semaine : une ligne par soignant, une colonne par jour. */
export function WeekGrid({ days, staff }: WeekGridProps) {
  return (
    <table className="week-grid">
      <thead>
        <tr>
          <th scope="col">Soignant</th>
          {days.map((day) => (
            <th key={day} scope="col">
              {formatDayHeader(day)}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {staff.map((member) => (
          <tr key={member.code}>
            <th scope="row">{member.full_name}</th>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
