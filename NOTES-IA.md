# Journal d'utilisation de l'IA

Ce projet est développé avec l'aide de Claude (Anthropic). J'écris le code et les tests ; l'IA prépare le socle, découpe les étapes et relit mes merge requests. Ce journal note, étape par étape, ce que l'IA a proposé, ce que j'ai gardé ou corrigé, et comment je l'ai vérifié.

## 2026-11-12 · Étape 0 : socle

- **Demandé à l'IA :** un socle Python avec uv, pytest et ruff, et une CI GitLab qui lance les mêmes contrôles qu'en local.
- **Proposé :** les commandes d'initialisation, la configuration de pytest et ruff dans `pyproject.toml`, un test minimal et le fichier `.gitlab-ci.yml`.
- **Gardé / corrigé :**
  - La commande `uv init --app` proposée créait un projet empaqueté (dossier `src/`) avec uv 0.13.7. Corrigée en `uv init --app --no-package`.
  - J'avais placé `.gitignore` et `.gitlab-ci.yml` dans `backend/` : aucun pipeline ne se lançait. Déplacés à la racine avec `git mv`.
  - Une règle de ma configuration Git globale ignorait `.vscode/` sur un seul de mes deux postes. Retirée.
- **Vérifié par :** `ruff check`, `ruff format --check` et `pytest` en local, puis le pipeline GitLab, vert après la vérification d'identité du compte.

## 2026-11-12 · Étape 1 : moteur de règles (en cours)

- **Demandé à l'IA :** le découpage de l'étape en 18 tests, et un accompagnement pas à pas pour le premier, car je n'avais jamais écrit de Python.
- **Proposé :** le premier test (`pytest.raises`) et la classe `Shift` (dataclass figée, enum `ShiftKind`, contrôle dans `__post_init__`), expliqués ligne par ligne avec leurs équivalents PHP.
- **Gardé / corrigé :** gardé tel quel. Écrit en trois temps : le test seul (échec à l'import), la classe sans contrôle (échec « DID NOT RAISE »), puis le contrôle (succès).
- **Vérifié par :** pytest et ruff en local, puis le pipeline de la merge request.
- **Appris :**
  - Python ne vérifie pas les types annotés à l'exécution, contrairement à PHP.
  - `@dataclass` génère le constructeur à partir des champs.
  - L'indentation délimite les blocs.
  - `len()` est une fonction et pas une méthode.
  - `date` et `datetime` sont deux types distincts.
  - `git reset --soft` permet de refaire un commit.
  - Les dictionnaires (`dict`) sont l'équivalent des tableaux associatifs de PHP ; `collections.defaultdict` crée automatiquement une valeur vide pour une clé absente, et `.items()` parcourt à la fois les clés et les valeurs.
  - Python compare les tuples élément par élément, ce qui permet de trier sur plusieurs critères avec `operator.attrgetter`.
  - `continue` passe directement au tour de boucle suivant.
  - Une valeur par défaut immuable comme un `timedelta` ne pose pas de problème, contrairement à une liste.
  - Les compréhensions de liste et les expressions génératrices.
  - `+` met deux listes bout à bout.
  - Un test vert ne prouve rien tant qu'on ne l'a pas vu échouer : on le vérifie en réintroduisant l'erreur qu'il vise.

### Tests

- `test_shift_ending_before_its_start_is_rejected`, poste qui finit avant de commencer : écrit avec l'IA, ligne par ligne.
- `test_overnight_shift_duration_spans_midnight`, durée d'un poste de nuit à cheval sur minuit : écrit seul. Nom traduit par l'IA ; deux corrections pendant la revue, la comparaison avec `12` au lieu d'un `timedelta`, et l'import manquant de `timedelta`.
- `test_empty_schedule_has_no_daily_rest_violation`, planning vide sans infraction de repos : écrit à partir de squelettes à trous fournis par l'IA, pour le test comme pour la fonction. Nom proposé par l'IA. La revue a montré que `assert not violations` laissait passer une fonction qui renvoie `None` : remplacé par `assert violations == []`.
- `test_rest_equal_to_minimum_has_no_daily_rest_violation`, repos égal au minimum (12 heures pile) : écrit seul, nom corrigé pendant la revue. Passé du premier coup, puisque la règle renvoyait encore une liste vide. Vérifié après le test `test_rest_below_minimum_has_daily_rest_violation` : en remplaçant `<` par `<=` dans la règle, il échoue.
- `test_rest_below_minimum_has_daily_rest_violation`, repos de 11 heures : écrit seul, puis corrigé pendant la revue sur quatre points : un nom qui contredisait l'assertion, `violations != []` trop faible (vrai aussi pour `None`), `violations.__len__` sans parenthèses au lieu de `len(violations)`, et `datetime` au lieu de `date` pour le jour. Ce test a fait naître `Violation`, `RuleCategory` et la règle, écrite avec `itertools.pairwise`.
- `test_shifts_of_different_staff_have_no_daily_rest_violation`, postes de deux soignants différents : écrit seul. Il échouait bien avec la première version de la règle, qui comparait tous les postes qui se suivent dans la liste, quel que soit le soignant.
- `test_shifts_interleaved_with_another_staff_have_a_daily_rest_violation` (ajouté au plan), postes d'un soignant intercalés avec ceux d'un autre (A, B, A) : idée venue de la revue, test écrit seul. Une simple vérification du soignant dans la boucle l'aurait laissé échouer, car les deux postes de A ne se suivent pas dans la liste. Ce test m'a obligé à revoir la conception de la règle : l'IA m'a présenté deux approches, le regroupement par soignant ou le tri, et j'ai choisi et écrit le regroupement avec `collections.defaultdict`. La revue a fait retirer une condition sur le soignant devenue inutile.
- Remaniement, fonction `make_shift` pour créer les postes dans les tests : écrite seul. Durée de 12 heures par défaut, modifiable pour créer des postes atypiques (10 h 15, par exemple). Aucune assertion modifiée ; les tests passaient avant et après. L'IA a expliqué la virgule finale « magique » de ruff, qui garde un appel déplié sur plusieurs lignes : une fois retirée, chaque création de poste tient sur une ligne. L'IA avait d'abord conseillé une valeur par défaut `None` en invoquant la règle B008 ; c'était faux, un `timedelta` est immuable et peut servir directement de valeur par défaut. Corrigé ensuite.
- `test_unsorted_shifts_have_no_daily_rest_violation`, postes dans le désordre : test et correction écrits seul. Avant la correction, le test échouait sur un repos négatif de 36 heures, que Python affiche sous la forme `-2 days, 12:00:00`. J'ai remplacé le regroupement par `defaultdict` par un tri unique avec `sorted()` et `operator.attrgetter("staff_id", "start")` : les postes de chaque soignant se suivent alors dans l'ordre chronologique, et `continue` saute les paires de deux soignants différents. L'IA a vérifié l'échec du test avant la correction et contrôlé, en modifiant volontairement le code, que les tests existants protègent le tri et le saut entre soignants.
- `test_unsorted_shifts_interleaved_with_another_staff_have_a_daily_rest_violation` (ajouté au plan), postes dans le désordre et intercalés avec ceux d'un autre soignant : idée et test de moi. Vert dès le premier lancement ; vérifié en retirant le tri : il échoue. L'IA a cherché s'il faisait doublon avec les autres. Une fausse correction du test `test_unsorted_shifts_have_no_daily_rest_violation`, qui aurait gardé le regroupement par `defaultdict` et pris la valeur absolue de la durée de repos (`abs()`) au lieu de trier, passe tous les autres tests, et seul celui-ci la détecte. Le test `test_unsorted_shifts_have_no_daily_rest_violation` vérifie que le désordre ne crée pas d'infraction, celui-ci qu'il n'en masque pas.
- `test_rest_equal_to_lower_minimum_has_no_daily_rest_violation`, seuil abaissé à 11 heures : écrit seul. Mêmes postes que `test_rest_below_minimum_has_daily_rest_violation`, seul le seuil change. Vert dès le premier lancement, puisque le seuil était déjà un paramètre ; vérifié en écrivant `timedelta(hours=12)` en dur dans la règle : seul ce test échoue, les autres utilisant tous 12 heures. Nom corrigé pendant la revue. Ce test justifie le seuil en paramètre : 12 heures dans la fonction publique hospitalière, 11 heures pour les salariés de droit privé.
- Fonction `make_night` : écrite seul, sur une suggestion de l'IA. Les appels à `make_shift` avec `kind=ShiftKind.NIGHT` dépassaient 100 caractères ; chaque nuit tient maintenant sur une ligne.
- `test_empty_schedule_has_no_consecutive_nights_violation` et `test_nights_equal_to_maximum_have_no_consecutive_nights_violation`, planning vide et trois nuits (la limite) : écrits seul. La revue a relevé que la deuxième nuit était attribuée à un autre soignant, ce qui vidait le test de son sens, et a fait corriger les noms. Le test des trois nuits a été vérifié une fois la règle écrite : avec `>=` au lieu de `>`, il échoue.
- Règle des nuits consécutives : écrite seul, avant ses tests, au lieu du simple squelette prévu. Essayée par l'IA sur plusieurs plannings, elle contenait trois erreurs que les tests existants ne voyaient pas : le compteur comptait les paires de nuits et non les nuits (quatre nuits ne donnaient aucune infraction), le changement de soignant n'était pas géré (l'écart négatif entre la dernière nuit d'un soignant et la première du suivant passait pour une continuité), et la comparaison portait sur les heures au lieu des dates (une nuit commençant à 21 h cassait la série). Corrigées seul ; les deux conditions de remise à 1 réunies ensuite avec `or`.
- Fonction `make_consecutive_nights` : écrite seul avec une compréhension de liste, sur une suggestion de l'IA, pour ne pas répéter la création des séries de nuits.
- `test_nights_above_maximum_have_a_consecutive_nights_violation`, `test_each_night_above_maximum_has_a_consecutive_nights_violation`, `test_nights_separated_by_a_day_off_have_no_consecutive_nights_violation`, `test_nights_of_different_staff_have_no_consecutive_nights_violation` et `test_nights_starting_at_different_hours_have_a_consecutive_nights_violation` : écrits seul, après la règle. Pour compenser l'ordre inversé, chaque test a été vérifié en réintroduisant l'erreur qu'il vise. Cette vérification, faite d'abord par l'IA, a montré que deux tests ne pouvaient pas échouer (les nuits des deux soignants étaient séparées par un jour libre ; la nuit décalée commençait à 19 h, soit moins de 24 heures après la précédente) et qu'un troisième laissait deux jours sans nuit au lieu d'un. Données corrigées, vérifications rejouées.
