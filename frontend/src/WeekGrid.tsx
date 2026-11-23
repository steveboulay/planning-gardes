import type { StaffMember, StoredShift, Violation } from "./api";
import { type IsoDate, formatDayHeader } from "./week";

type WeekGridProps = {
  days: IsoDate[];
  staff: StaffMember[];
  shifts: StoredShift[];
  violations: Violation[];
};

/** Grille de la semaine : une ligne par soignant, une colonne par jour. */
export function WeekGrid({ days }: WeekGridProps) {
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
    </table>
  );
}
