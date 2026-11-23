import type { StaffMember, StoredShift, Violation } from "./api";
import { type IsoDate, formatDayHeader } from "./week";

const KIND_LABELS: Record<StoredShift["kind"], string> = {
  jour: "Jour",
  nuit: "Nuit",
};

/** "Jour 08:00–20:00" : l'API renvoie des heures sans fuseau, lues telles quelles. */
function shiftLabel(shift: StoredShift): string {
  return `${KIND_LABELS[shift.kind]} ${shift.start.slice(11, 16)}–${shift.end.slice(11, 16)}`;
}

type WeekGridProps = {
  days: IsoDate[];
  staff: StaffMember[];
  shifts: StoredShift[];
  violations: Violation[];
};

/** Grille de la semaine : une ligne par soignant, une colonne par jour. */
export function WeekGrid({ days, staff, shifts }: WeekGridProps) {
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
            {days.map((day) => {
              const dayShifts = shifts.filter(
                (shift) => shift.staff === member.code && shift.start.startsWith(day),
              );
              return (
                <td key={day}>
                  {dayShifts.map((shift) => (
                    <div key={shift.id}>{shiftLabel(shift)}</div>
                  ))}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
