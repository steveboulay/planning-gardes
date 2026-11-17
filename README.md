# Planning de gardes : vérificateur de règles

[![pipeline](https://gitlab.com/steveboulay/planning-gardes/badges/main/pipeline.svg)](https://gitlab.com/steveboulay/planning-gardes/-/pipelines)

On lui donne le planning d'un service de soins, il renvoie les règles enfreintes : repos insuffisant, trop de nuits d'affilée, trop d'heures dans la semaine, jour de repos demandé non respecté. Il ne construit pas de planning, il contrôle celui qu'on lui soumet.

Projet personnel, écrit pour apprendre Python, puis Django et React, en venant de PHP et Symfony. Le code suit la méthode « test d'abord » avec pytest (les écarts sont notés dans le journal) et la CI GitLab le vérifie à chaque push.

## Les règles

Le moteur est en Python pur, sans dépendance à Django, dans `backend/planning_rules/`. Chaque règle est une fonction qui reçoit des postes et renvoie une liste d'infractions. Les seuils sont des paramètres.

| Fonction | Code | Catégorie | Règle |
|---|---|---|---|
| `check_daily_rest(shifts, min_rest)` | `repos_quotidien` | légale | Entre deux postes d'un même soignant, le repos dure au moins `min_rest`. Infraction datée du jour du second poste. |
| `check_consecutive_nights(shifts, max_nights)` | `nuits_consecutives` | collective | Pas plus de `max_nights` nuits sur des jours qui se suivent. Une infraction pour chaque nuit au-delà de la limite. |
| `check_weekly_hours(shifts, max_duration)` | `heures_hebdomadaires` | légale | Pas plus de `max_duration` par semaine, du lundi au dimanche. Un poste compte dans la semaine où il commence. Infraction datée du lundi. |
| `check_day_off_requests(shifts, requests)` | `desiderata` | individuelle | Une infraction pour chaque demande de repos qui tombe un jour où le soignant a un poste qui commence. |

`check_schedule(shifts, requests, config)` lance les quatre règles et renvoie toutes les infractions, triées par jour, puis par soignant, puis par code de règle.

Les seuils par défaut sont regroupés dans `DEFAULT_CONFIG` (`RulesConfig`) :

- **repos quotidien : 12 heures**, le minimum de la fonction publique hospitalière (décret n° 2002-9 du 4 janvier 2002). Il peut être abaissé à 11 heures : c'est le minimum des salariés de droit privé (Code du travail, article L3131-1), et celui que la fonction publique hospitalière autorise après un accord avec les organisations syndicales (décret n° 2021-1544 du 30 novembre 2021) ;
- **nuits consécutives : 3**, une règle de service et non une règle légale ;
- **durée hebdomadaire : 48 heures** (directive européenne 2003/88/CE).

## Exemple

Depuis le dossier `backend/`, avec `uv run python` :

```python
from datetime import datetime

from planning_rules.models import Shift, ShiftKind
from planning_rules.rules import check_schedule

shifts = [
    Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 2, 8, 0),
        end=datetime(2026, 11, 2, 20, 0),
        kind=ShiftKind.DAY,
    ),
    Shift(
        staff_id="nurse-1",
        start=datetime(2026, 11, 3, 7, 0),
        end=datetime(2026, 11, 3, 19, 0),
        kind=ShiftKind.DAY,
    ),
]

for violation in check_schedule(shifts):
    print(violation.day, violation.category.value, violation.message)
```

```
2026-11-03 légale Soignant nurse-1 : repos de 11:00 inférieur à 12:00.
```

## L'API

Une API Django REST Framework expose le moteur : elle reçoit un planning en JSON et renvoie ses infractions. Elle n'a pas encore de base de données et ne conserve rien. Le code est réparti en trois dossiers de `backend/` : `planning_rules/` pour le moteur, `api/` pour les serializers et la vue, `config/` pour les réglages de Django.

Depuis `backend/`, lancer le serveur de développement :

```bash
uv run python manage.py runserver
```

Au démarrage, Django signale des migrations non appliquées : c'est sans effet, puisqu'aucune base n'est utilisée.

Puis, dans un autre terminal :

```bash
curl -X POST http://127.0.0.1:8000/api/schedule/check/ \
  -H "Content-Type: application/json" \
  -d '{
    "shifts": [
      {"staff_id": "nurse-1", "start": "2026-11-02T08:00:00", "end": "2026-11-02T20:00:00", "kind": "jour"},
      {"staff_id": "nurse-1", "start": "2026-11-03T07:00:00", "end": "2026-11-03T19:00:00", "kind": "jour"}
    ],
    "day_off_requests": [{"staff_id": "nurse-1", "day": "2026-11-03"}],
    "config": {"min_daily_rest": "12:00:00"}
  }'
```

```json
{
  "violations": [
    {
      "rule": "desiderata",
      "category": "individuelle",
      "staff_id": "nurse-1",
      "day": "2026-11-03",
      "message": "Soignant nurse-1 : poste le 03/11/2026, jour de repos demandé."
    },
    {
      "rule": "repos_quotidien",
      "category": "légale",
      "staff_id": "nurse-1",
      "day": "2026-11-03",
      "message": "Soignant nurse-1 : repos de 11:00 inférieur à 12:00."
    }
  ]
}
```

Format de la requête :

- `shifts` est obligatoire, éventuellement vide ; `day_off_requests` et `config` sont facultatifs.
- Les dates et heures sont au format `AAAA-MM-JJTHH:MM:SS`, sans fuseau horaire (`2026-11-02T08:00:00`) : une heure suivie d'un décalage (`+01:00`) ou de `Z` est refusée, comme une heure sans secondes. Les jours sont au format `2026-11-03`.
- `kind` vaut `"jour"` ou `"nuit"`.
- Dans `config`, `min_daily_rest` et `max_weekly_duration` sont des durées positives ou nulles au format `HH:MM:SS` (`"48:00:00"` est accepté), et `max_consecutive_nights` un entier au moins égal à 1. Un seuil absent garde sa valeur par défaut.

Erreurs : un code 400 avec le détail des champs en faute, par exemple `{"shifts": {"0": {"non_field_errors": ["Un poste doit se terminer après son début."]}}}` pour un poste qui finit avant de commencer, et un code 405 pour toute autre méthode que POST.

## Lancer les tests

Il faut [uv](https://docs.astral.sh/uv/), qui installe Python 3.13 si besoin.

```bash
cd backend
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
```

La CI GitLab lance les mêmes commandes à chaque push.

## Choix et limites

- Les dates n'ont pas de fuseau horaire. Une nuit qui traverse un changement d'heure dure en réalité 11 ou 13 heures.
- La durée hebdomadaire est comptée par semaine civile, du lundi au dimanche, alors que la réglementation raisonne sur toute période de sept jours.
- Deux postes qui se chevauchent apparaissent comme un repos négatif, sans règle dédiée.
- Une demande de repos saisie deux fois donne deux infractions.
- Une nuit qui commence la veille d'un jour de repos demandé et se termine ce jour-là n'est pas une infraction : la règle porte sur le jour où le poste commence.
- L'API n'a pas d'authentification : c'est une API de démonstration, sans état.

## Usage de l'IA

Le projet est développé avec l'aide de Claude (Anthropic) : découpage des étapes, explications, revue de code. Le journal [NOTES-IA.md](NOTES-IA.md) note, étape par étape, ce que l'IA a proposé, ce que j'ai gardé ou corrigé, et comment je l'ai vérifié.

## Suite

1. La persistance : modèles Django, PostgreSQL avec Docker Compose, migrations.
2. Un front React et TypeScript : la grille de la semaine, avec les infractions mises en évidence.
3. Des scénarios de bout en bout avec Playwright.

## Licence

MIT. Voir [LICENSE](LICENSE).
