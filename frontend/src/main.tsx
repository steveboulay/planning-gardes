import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { isIsoDate, toIsoDate } from "./week";

// Semaine de ?date=AAAA-MM-JJ quand cette date est valide, sinon semaine du jour
const requested = new URLSearchParams(window.location.search).get("date");
const initialDate = requested !== null && isIsoDate(requested) ? requested : toIsoDate(new Date());

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App initialDate={initialDate} />
  </StrictMode>,
);
