import type { Violation } from "./api";

type ViolationListProps = {
  violations: Violation[];
};

/** Messages des infractions de la semaine, dans l'ordre renvoyé par l'API. */
export function ViolationList({ violations }: ViolationListProps) {
  return (
    <section>
      <h2>Infractions</h2>
      {violations.length === 0 ? (
        <p>Aucune infraction cette semaine.</p>
      ) : (
        <ul>
          {/* Clé par position : deux messages peuvent être identiques */}
          {violations.map((violation, index) => (
            <li key={index}>{violation.message}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
