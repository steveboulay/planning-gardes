import { useEffect, useState } from "react";

import { type WeekSchedule, fetchWeekSchedule } from "./api";
import { ViolationList } from "./ViolationList";
import { WeekGrid } from "./WeekGrid";
import { type IsoDate, formatDate, mondayOf, weekDays } from "./week";

type AppProps = {
  initialDate: IsoDate;
};

/** Planning de la semaine qui contient la date de départ, avec ses infractions. */
export default function App({ initialDate }: AppProps) {
  const monday = mondayOf(initialDate);
  const [schedule, setSchedule] = useState<WeekSchedule | null>(null);

  useEffect(() => {
    // Une réponse arrivée après un changement de semaine est ignorée
    let ignore = false;
    fetchWeekSchedule(monday).then((result) => {
      if (!ignore) setSchedule(result);
    });
    return () => {
      ignore = true;
    };
  }, [monday]);

  const days = weekDays(monday);

  return (
    <main>
      <h1>Planning de gardes</h1>
      <h2>
        Semaine du {formatDate(days[0])} au {formatDate(days[6])}
      </h2>
      {schedule !== null && (
        <>
          <WeekGrid days={days} {...schedule} />
          <ViolationList violations={schedule.violations} />
        </>
      )}
    </main>
  );
}
