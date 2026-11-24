import { useEffect, useState } from "react";

import { type WeekSchedule, fetchWeekSchedule } from "./api";
import { ViolationList } from "./ViolationList";
import { WeekGrid } from "./WeekGrid";
import { type IsoDate, addWeeks, formatDate, mondayOf, weekDays } from "./week";

type AppProps = {
  initialDate: IsoDate;
};

/** Planning de la semaine qui contient la date de départ, avec ses infractions. */
export default function App({ initialDate }: AppProps) {
  const [monday, setMonday] = useState(() => mondayOf(initialDate));
  const [schedule, setSchedule] = useState<WeekSchedule | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    // Une réponse arrivée après un changement de semaine est ignorée
    let ignore = false;
    fetchWeekSchedule(monday)
      .then((result) => {
        if (!ignore) setSchedule(result);
      })
      .catch(() => {
        if (!ignore) setFailed(true);
      });
    return () => {
      ignore = true;
    };
  }, [monday]);

  function goToWeek(weeks: number) {
    setMonday(addWeeks(monday, weeks));
    setSchedule(null);
  }

  const days = weekDays(monday);

  return (
    <main>
      <h1>Planning de gardes</h1>
      <nav>
        <button type="button" onClick={() => goToWeek(-1)}>
          Semaine précédente
        </button>
        <h2>
          Semaine du {formatDate(days[0])} au {formatDate(days[6])}
        </h2>
        <button type="button" onClick={() => goToWeek(1)}>
          Semaine suivante
        </button>
      </nav>
      {failed && <p role="alert">Impossible de charger le planning.</p>}
      {!failed && schedule === null && <p>Chargement…</p>}
      {schedule !== null && (
        <>
          <WeekGrid days={days} {...schedule} />
          <ViolationList violations={schedule.violations} />
        </>
      )}
    </main>
  );
}
