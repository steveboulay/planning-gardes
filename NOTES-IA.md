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

## 2026-11-12 · Étape 1 : moteur de règles

- **Demandé à l'IA :** le découpage de l'étape en tests, un accompagnement pas à pas pour le premier, car je n'avais jamais écrit de Python, puis une revue de chaque test et de chaque règle, sans la solution : l'IA donnait les notions et les pistes, j'écrivais le code.
- **Proposé :**
  - le premier test et la classe `Shift`, expliqués ligne par ligne avec leurs équivalents PHP ;
  - pour la suite, des noms de tests, des pistes (tri, regroupement, ensembles, semaines ISO) et les cas limites à couvrir ;
  - pour chaque test vert dès le premier lancement, l'erreur à réintroduire pour vérifier qu'il sait échouer ;
  - le premier jet du README, rédigé à partir du code.
- **Gardé / corrigé :**
  - Plusieurs de mes choix ont remplacé les pistes de l'IA : un tri unique sur `attrgetter("staff_id", "start")` au lieu d'un regroupement, `isocalendar()` au lieu de `weekday()`, une infraction par demande de repos plutôt que par poste, un plafond hebdomadaire exprimé en `timedelta`.
  - L'IA s'est trompée au moins deux fois : elle a invoqué la règle B008 à tort pour un `timedelta`, et elle a compté une longueur de ligne en octets au lieu de caractères.
  - Deux règles ont été écrites avant leurs tests (nuits consécutives, heures hebdomadaires). La première a été rattrapée par des tests vérifiés un à un ; la seconde, mise de côté jusqu'à l'échec de son test.
  - La revue a trouvé plusieurs tests qui ne pouvaient pas échouer : données mal choisies, mauvais soignant, poste de jour à la place d'une nuit. Tous ont été corrigés.
  - Limite conservée : les postes qui se chevauchent. Deux approches ont été envisagées, refuser le planning ou créer une règle dédiée ; le choix est reporté.
- **Vérifié par :** ruff et pytest en local, le pipeline GitLab à chaque push, et, pour chaque test vert dès le premier lancement, la réintroduction volontaire de l'erreur qu'il vise. La CI a rattrapé deux oublis : une règle non commitée, et un résultat attendu manquant dans un test.
- **Bilan :** quatre règles, `check_schedule` et `RulesConfig`, couverts par 41 tests.
  - Ce qui a bien marché : écrire le test d'abord, quand je l'ai fait ; vérifier chaque test en réintroduisant une erreur, ce qui a démasqué plusieurs tests inutiles ; une revue qui donne des pistes sans la solution, ce qui m'a obligé à comprendre chaque ligne.
  - Ce qui a moins bien marché : écrire le code avant le test quand l'idée était déjà en tête ; le copier-coller d'un test à l'autre, à l'origine de la plupart des erreurs (mauvais soignant, mauvaise date, mauvais type de poste) ; un fichier oublié dans un commit.
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
  - `isocalendar()` et l'année ISO : la semaine 53 de 2026 va du lundi 28 décembre 2026 au dimanche 3 janvier 2027.
  - `divmod()` découpe une durée en heures et en minutes.
  - L'ordre des arguments de `datetime` : année, mois, jour, heure, minute.
  - Ce qui n'est pas une règle va dans son propre module, et les imports partent de `backend/`, pas de la racine du dépôt.
  - Les ensembles (`set`), les compréhensions d'ensemble et l'opérateur `in`.
  - Les codes de `strftime` dans une f-string : `{jour:%d/%m/%Y}`.
  - Un commentaire explique pourquoi, pas ce que fait la ligne.
  - `git status` avant chaque push : un fichier modifié mais non commité ne part pas.
  - Une valeur par défaut n'est évaluée qu'une fois, à la définition de la fonction (règle B008) ; une constante de module rend ce partage explicite.
  - `collections.abc.Sequence` pour un paramètre qui accepte une liste ou un tuple.
  - Le tri de Python est stable : à égalité de clé, l'ordre de départ est conservé.
  - On ne remplit jamais les valeurs attendues d'un test en recopiant la sortie du code.
  - `git rm` supprime un fichier et prépare sa suppression dans le même geste.
  - Sans licence, un dépôt public peut être lu mais pas réutilisé : la licence MIT donne ce droit, sans garantie.

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
- Fonction `make_consecutive_shifts` : écrite seul, sur une suggestion de l'IA, pour tester les heures avec des postes de jour. Des tests limités aux nuits n'auraient pas vu un filtre sur les nuits recopié depuis la règle précédente. `make_consecutive_nights` l'appelle désormais.
- `test_empty_schedule_has_no_weekly_hours_violation`, `test_hours_equal_to_maximum_have_no_weekly_hours_violation` et `test_hours_above_maximum_have_a_weekly_hours_violation`, puis la règle des heures hebdomadaires : tests écrits seul, d'abord contre un squelette qui renvoyait une liste vide. J'avais écrit la règle complète trop tôt ; je l'ai mise de côté jusqu'à l'échec du test au-delà du maximum. Plafond exprimé en `timedelta` (`max_duration`) plutôt qu'en nombre entier d'heures, pour accepter une valeur comme 35 h 30. Semaine calculée avec `isocalendar()` et lundi retrouvé avec `date.fromisocalendar()`, une approche plus sûre que la piste `weekday()` donnée par l'IA, car elle tient compte de l'année ISO. Série commencée un mardi, pour que l'assertion sur le lundi prouve quelque chose. La revue a fait aligner le code de la règle sur le plan, corriger un import `backend.planning_rules` ajouté par VS Code, et aligner le message sur celui des autres règles.
- Fonction `format_duration`, dans le module `formatting.py`, et ses tests dans `test_formatting.py` : écrits seul, au format HH:MM. Le besoin est venu du message de la règle hebdomadaire, car `str()` affiche 60 heures sous la forme « 2 days, 12:00:00 ». La revue a montré qu'aucun test ne vérifiait la gestion du signe : une version sans `abs()` passait les cinq premiers tests, parce que -36 heures tombent juste. Ajout de -1 h 30, qui attend « -01:30 ». Une condition qui évite « -00:00 » pour une durée négative de moins d'une minute, écrite sans test, a reçu le sien.
- `test_shifts_spread_over_two_weeks_have_no_weekly_hours_violation`, `test_shifts_of_different_staff_have_no_weekly_hours_violation`, `test_sunday_night_counts_in_the_week_it_starts` et `test_week_spanning_new_year_is_counted_as_one_week` : écrits seul, chacun vérifié en réintroduisant l'erreur visée (semaine retirée de la clé, soignant remplacé par une constante, semaine de fin au lieu de la semaine de début, année civile au lieu de l'année ISO). La revue a fait déplacer la série des deux semaines pour qu'elle traverse le week-end, ce qui détecte aussi des semaines commençant le dimanche (`strftime("%U")`). Elle a aussi fait corriger le test de la nuit du dimanche, qui ne contenait d'abord aucune nuit, puis une nuit du jeudi.
- `test_empty_schedule_has_no_day_off_request_violation`, puis le modèle `DayOffRequest` et le squelette de `check_day_off_requests` : écrits seul, test d'abord.
- `test_shift_on_requested_day_off_has_a_day_off_request_violation`, puis la règle des desiderata : écrits seul. Un second poste un autre jour, ajouté sur une remarque de la revue, empêche une règle qui signalerait tous les postes du soignant de passer. J'ai construit l'ensemble des jours travaillés et parcouru les demandes, à l'inverse de la piste de l'IA (ensemble des demandes, parcours des postes) : la règle donne donc une infraction par demande non respectée. La revue a relevé que la docstring disait « par poste » ; choix confirmé et fixé par `test_two_shifts_on_requested_day_off_have_a_single_violation`, vérifié en faisant parcourir les postes à la règle. Commentaires numérotés retirés, ainsi qu'un préfixe `f` inutile. La règle avait été oubliée dans le commit : la CI l'a signalé, avec deux tests rouges sur GitLab, et un commit de plus a corrigé.
- `test_day_off_request_of_another_staff_has_no_violation` et `test_night_ending_on_requested_day_off_has_no_violation` : écrits seul, vérifiés en retirant le soignant des couples, puis en datant le poste de sa fin. La revue a relevé que la demande du second test était d'abord au nom d'un autre soignant, ce qui le faisait passer pour une mauvaise raison.
- `test_default_config_matches_regulatory_thresholds`, puis `RulesConfig` et `DEFAULT_CONFIG` : écrits seul, test d'abord ; vérifié en changeant une valeur par défaut.
- `test_empty_schedule_has_no_violation`, puis le squelette de `check_schedule` : écrits seul. Essai fait à la demande de l'IA : avec `config=RulesConfig()` en valeur par défaut, pytest passe, mais ruff signale B008, car une valeur par défaut n'est évaluée qu'une fois ; remplacée par la constante `DEFAULT_CONFIG`. `requests` reçoit `()` et le type `Sequence`, qui accepte les listes comme les tuples.
- `test_schedule_combines_violations_of_all_rules_sorted_by_day`, puis `check_schedule` : données construites seul, un soignant par règle, avec deux infractions le même jour. Assertion par comparaison de triplets (jour, soignant, règle), technique proposée par l'IA. Deux dates attendues d'abord mal calculées (le premier poste au lieu du second, la première nuit au lieu de la quatrième), corrigées pendant la revue. La revue a aussi relevé que la clé de tri oubliait le code de la règle, ce que le test ne pouvait pas voir : j'ai ajouté une demande de repos pour créer deux infractions le même jour chez le même soignant. Le triplet correspondant avait d'abord été oublié ; la CI l'a signalé. Vérifié en retirant une règle, le tri, puis chaque critère de la clé.
- `test_schedule_uses_given_config` : écrit seul. Un soignant par seuil, chacun exactement à la limite de la configuration reçue (11 heures de repos, 4 nuits, 60 heures), alors que la configuration par défaut donnerait trois infractions. Vérifié en remplaçant tour à tour chaque seuil reçu par celui de `DEFAULT_CONFIG` : le test échoue à chaque fois.
- Nettoyage : `format_duration` dans le message de `check_daily_rest`, à la place des durées brutes (« -2 days, 12:00:00 »), et suppression de `test_socle.py`, devenu inutile.
- README et licence MIT : premier jet du README rédigé par l'IA à partir du code, relu, et exemple exécuté pour vérifier la sortie affichée.
- `test_two_nights_starting_the_same_day_count_as_one`, puis la correction de `check_consecutive_nights` : écrits seul, pour lever une limite que je trouvais dommage de laisser dans le README. Le test passait d'abord pour une mauvaise raison : le poste ajouté était un poste de jour, ignoré par la règle ; la revue l'a relevé. Un troisième cas dans la boucle, même soignant et même jour de début, passe à la paire suivante sans toucher au compteur. Vérifié en retirant ce cas : le test échoue. Les conditions ont ensuite été simplifiées avec deux variables locales, `same_staff` et `day_gap`, sur une suggestion de la revue.

## 2026-11-17 · Étape 2 : API Django REST Framework

- **Demandé à l'IA :** le cahier des charges de l'étape (mise en place de Django, contrat de l'API, liste des tests), un accompagnement pas à pas pour le premier test, car je découvrais Django et Django REST Framework, puis une revue de chaque push.
- **Proposé :**
  - les commandes de mise en place, avec les pièges connus : fichiers générés inutiles à supprimer, `db.sqlite3` à ignorer, reformatage par `black` s'il est installé ;
  - le contrat de l'API et les noms des dix tests, vérifiés par l'IA sur une implémentation de référence qu'elle ne m'a pas montrée ;
  - le premier test et la vue, expliqués ligne par ligne avec leurs équivalents Symfony : `APIView` pour le contrôleur, `Serializer` pour le DTO et ses contraintes, `APIClient` pour le `KernelBrowser`, `reverse()` pour la génération d'URL ;
  - le formatage et le tri des imports par ruff à chaque enregistrement dans VS Code ;
  - le premier jet de la section API du README, avec un exemple `curl` rejoué sur le serveur de développement.
- **Gardé / corrigé :**
  - Le cahier des charges oubliait que les fichiers générés par Django ne suivent pas le format de ruff (guillemets simples) : un `uv run ruff format .` après la génération a réglé le problème, et le plan a été corrigé.
  - La clé secrète générée par Django a été retirée de `settings.py` avant le premier commit : la clé est lue dans la variable d'environnement `DJANGO_SECRET_KEY`, avec une valeur de développement par défaut.
  - Pour `test_given_config_is_used`, j'ai testé les trois seuils au lieu du seul repos quotidien prévu par le plan, sur le modèle de `test_schedule_uses_given_config`.
  - VS Code ajoutait des imports `from backend.…`, qui échouent depuis `backend/` : corrigés deux fois, puis réglés par `python.analysis.extraPaths`.
  - La vérification `manage.py check` avait été placée après `uv cache prune` dans la CI : corrigée avec `git commit --amend` et `git push --force-with-lease`, sur ma branche.
  - `test_invalid_config_is_rejected` envoyait la chaîne `"0"` au lieu de l'entier `0` : corrigé dans le commit du test lui-même, avec `git commit --fixup` et `git rebase --autosquash`.
  - La revue finale de la merge request, faite en envoyant à l'API des requêtes absentes des tests, a trouvé deux entrées acceptées à tort : une heure avec décalage, convertie en UTC sans prévenir (un poste commençant le 2 novembre à 0 h 30 passait au 1er novembre et échappait à une demande de repos), et des durées négatives dans `config`, qui empêchaient les règles de se déclencher. Deux tests et deux corrections ont suivi.
- **Vérifié par :** ruff, `manage.py check` et pytest en local, le pipeline de la merge request à chaque push, la réintroduction de l'erreur visée par chaque test, l'exemple `curl` du README rejoué sur `runserver`, et des requêtes envoyées à la main pendant la revue finale.
- **Bilan :** une route, une vue et cinq serializers, couverts par douze tests d'API ; 53 tests en tout. Le moteur n'a pas changé : l'API ne fait que l'appeler.
  - Ce qui a bien marché : le test d'abord, cette fois sans exception, chaque commit de code suivant le test qui l'a demandé ; une vue mince, qui laisse les règles au moteur : le contrôle « un poste finit après son début » reste écrit à un seul endroit, dans `Shift`, et l'API renvoie son message.
  - Ce qui a moins bien marché : des commandes lancées depuis la racine du dépôt au lieu de `backend/` (`ModuleNotFoundError`, `manage.py` introuvable) ; une assertion qui dépendait du texte exact d'un message de DRF ; un push dans le désordre, le code avant son test, remis en ordre avec `git reset` et `git restore --source` ; un push rouge, faute d'avoir lancé pytest en local avant.
- **Appris :**
  - `startproject config .` : le point final place `manage.py` directement dans le dossier courant.
  - `INSTALLED_APPS` joue le rôle de `config/bundles.php`.
  - Une `APIView` a une méthode par verbe HTTP ; les autres verbes reçoivent un 405 sans rien écrire.
  - La méthode `validate()` d'un serializer peut renvoyer un objet du domaine : la vue reçoit des `Shift` prêts à l'emploi.
  - Une erreur levée dans `validate()` arrive dans `non_field_errors`, et les erreurs d'une liste imbriquée sont rangées par index, sous forme de chaîne (`"0"`).
  - `required=False` avec `default=list` : `list` est appelée à chaque requête, ce qui donne une liste neuve à chaque fois.
  - `source="category.value"` choisit ce que le serializer lit sur l'objet.
  - `IntegerField` accepte `"0"` et le convertit : un test doit envoyer le type prévu par le contrat.
  - `USE_TZ = False` : avec `True`, DRF convertirait les dates reçues en dates avec fuseau, que Python refuse de comparer aux dates sans fuseau du moteur.
  - `raise … from error` garde l'exception d'origine (règle B904 de ruff).
  - Une fixture pytest est injectée d'après le nom du paramètre du test.
  - `response.json()` est une méthode ; `response.content` donne le corps brut.
  - pytest capture la sortie : un `print` placé après la ligne qui lève une exception ne s'exécute jamais, et l'option `-s` affiche les autres.
  - Les messages de DRF en français contiennent des espaces insécables : vérifier le nom du champ en faute est plus solide que comparer le texte.
  - `git commit --fixup` et `git rebase -i --autosquash` corrigent un commit plus ancien que le dernier ; `--force-with-lease` ne sert que sur ma propre branche, jamais sur `main`.
  - `git push -o merge_request.create` crée la merge request depuis le terminal.
  - Le sixième argument de position de `datetime` est la seconde : `tzinfo` se passe par son nom.
  - `git reset <commit>` sans option déplace la branche et garde les fichiers tels quels ; `git restore --source=<commit>` reprend un fichier depuis un autre commit.
  - Une seule requête peut vérifier plusieurs champs, puisque DRF renvoie toutes les erreurs à la fois ; `pytest.mark.parametrize`, l'équivalent des data providers de PHPUnit, sert quand les cas ne tiennent pas dans une requête.
  - Le formatage et les corrections de ruff à l'enregistrement dans VS Code (`formatOnSave`, `codeActionsOnSave`), comme PHP CS Fixer lancé à chaque sauvegarde.

### Tests

- `test_empty_schedule_returns_no_violation`, planning vide : écrit avec l'IA, pas à pas (fixture `api_client`, `reverse()`, envoi en JSON). Il a fait naître les réglages de pytest-django, la route et la vue.
- `test_get_is_not_allowed`, requête GET : vert dès le premier lancement, puisque `APIView` refuse seule les méthodes qu'elle ne définit pas. La première version envoyait un POST ; la revue l'a relevé avant le commit. Vérifié en ajoutant une méthode `get()` à la vue : il échoue.
- `test_missing_shifts_is_rejected`, requête sans `shifts` : a fait naître `CheckScheduleSerializer`. Vérifié en rendant `shifts` facultatif : il échoue.
- `test_daily_rest_violation_is_returned_as_json`, deux postes séparés de 11 heures : comparaison du JSON complet de la réponse. A fait naître `ShiftSerializer`, `ViolationSerializer` et la fonction `shift_payload`. Vérifié en renvoyant l'enum au lieu de sa valeur (`source="category"`) : il échoue.
- `test_unknown_shift_kind_is_rejected`, type de poste « soir » : vert dès le premier lancement, grâce au `ChoiceField` déjà en place. L'assertion comparait d'abord le message exact de DRF, avec ses espaces insécables ; elle vérifie maintenant que l'erreur porte sur le champ `kind`. Vérifié en remplaçant le `ChoiceField` par un `CharField` : il échoue, car l'erreur vient alors du modèle et non plus du champ.
- `test_shift_ending_before_its_start_is_rejected`, poste qui finit avant de commencer : la `ValueError` du modèle n'était pas interceptée, et le test échouait sur l'exception, qui aurait donné une erreur 500 en production. A fait naître le `try`/`except` de `ShiftSerializer`, qui la transforme en erreur 400 avec le message du modèle.
- `test_day_off_requests_are_used`, poste un jour de repos demandé : a fait naître `DayOffRequestSerializer` et la fonction `day_off_payload`. Vérifié en ne transmettant plus les demandes au moteur : il échoue.
- `test_given_config_is_used`, un soignant par seuil, chacun exactement à la limite de la configuration reçue : a fait naître `RulesConfigSerializer`. Vérifié en remplaçant la configuration reçue par `DEFAULT_CONFIG`, puis chaque seuil un par un : il échoue à chaque fois.
- `test_partial_config_keeps_other_defaults`, seul le repos quotidien est fourni et quatre nuits consécutives donnent toujours une infraction : vert dès le premier lancement. Vérifié en donnant une valeur par défaut de 99 nuits au champ du serializer : il échoue.
- `test_invalid_config_is_rejected`, zéro nuit consécutive autorisée : a fait naître `min_value=1`. Vérifié en retirant `min_value` : il échoue.
- `test_shift_with_time_zone_is_rejected`, poste dont les heures portent `+01:00` : ajouté après la revue finale. A fait naître `input_formats` sur `start` et `end`. Il ne vérifiait d'abord que `start` : la revue a montré qu'en retirant `input_formats` de `end`, il passait toujours. D'où une seconde assertion. Vérifié en retirant `input_formats` de chaque champ : il échoue.
- `test_negative_duration_config_is_rejected`, repos minimum et durée hebdomadaire négatifs : ajouté après la revue finale. Les deux champs sont envoyés dans la même requête, et le test vérifie que chacun reçoit son erreur. A fait naître `min_value=timedelta(0)` sur les deux `DurationField`. Vérifié en retirant `min_value` d'un champ, puis de l'autre : il échoue à chaque fois.

## 2026-11-17 · Étape 3 : persistance avec PostgreSQL

- **Demandé à l'IA :** le cahier des charges de l'étape (Docker Compose, modèles, contraintes en base, endpoints de lecture, admin), puis un accompagnement test par test, avec une revue de chaque push.
- **Proposé :**
  - le `compose.yaml` de PostgreSQL 18 (volume monté sur `/var/lib/postgresql`, nouveau chemin depuis l'image 18 ; port limité au poste ; `healthcheck` avec `pg_isready`) et le service PostgreSQL de la CI ;
  - les trois modèles, leurs contraintes et la conversion `to_engine()` vers les objets du moteur, qui ne sait toujours rien de Django ;
  - trois pièges relevés par l'IA sur une implémentation de référence : `TSTZRANGE` et non `TSRANGE`, puisque Django crée des colonnes `timestamp with time zone` ; l'extension `btree_gist`, à ajouter à la main dans la migration de la contrainte d'exclusion ; la `condition` de cette contrainte, sans laquelle la validation de l'admin lève une `DataError` ;
  - les extensions VS Code YAML et Container Tools, le jeu de données de démonstration et le premier jet de la section « Base de données » du README.
- **Gardé / corrigé :**
  - Le plan faisait créer l'application `schedules` dans le commit de socle : ses fichiers générés, aux imports inutilisés, auraient fait échouer `ruff check`. L'application est née avec le premier modèle. Le plan affirmait aussi que `startapp` génère des fichiers au format de ruff : c'était faux, `black`, installé dans l'espace de travail de l'IA, avait reformaté sa référence. J'ai corrigé moi-même les apostrophes de `apps.py`.
  - Mon bloc `DATABASES` n'avait pas été remplacé : `migrate` a recréé `db.sqlite3` et y a mis les tables. Trouvé en affichant `connection.vendor`.
  - Ajoutés au plan pendant l'étape : `test_staff_code_cannot_be_stored_twice`, proposé par l'IA, `test_single_day_period_is_accepted`, de moi, et trois tests pour l'affichage des modèles.
  - Deux migrations oubliées dans leur commit, la `0002` puis la `0009` : `makemigrations --check` les a signalées dans la CI, et je les ai ajoutées par amend. Les contrôles de la CI sont maintenant dans un alias, `verif`, lancé avant chaque commit.
  - Le commit de l'admin ne faisait pas passer son test : le `__str__` de `StaffMember` était arrivé un commit plus tard. Poussés ensemble, les commits n'avaient été testés par la CI que sur le dernier. J'ai réécrit l'historique de la branche pour que chaque commit de code passe seul.
- **Vérifié par :** ruff, `manage.py check`, `makemigrations --check` et pytest en local et dans la CI, avec PostgreSQL 18 en service ; la réintroduction de l'erreur visée par chaque test vert dès son premier lancement, dans la migration quand l'erreur porte sur une contrainte ; la démonstration du README, rejouée par l'IA sur mon code dans une base neuve (`migrate`, `loaddata`, `runserver`, `curl`).
- **Bilan :** trois modèles, quatre contraintes en base, trois endpoints de lecture et l'admin, couverts par 23 nouveaux tests ; 76 tests en tout. Le moteur n'a pas changé.
  - Ce qui a bien marché : les deux limites ouvertes depuis l'étape 1, les chevauchements et les demandes en double, sont réglées pour les données enregistrées, par la base elle-même ; la contrainte d'exclusion, propre à PostgreSQL, justifie le choix de cette base ; chaque test vert d'emblée a été vérifié.
  - Ce qui a moins bien marché : les migrations oubliées ; plusieurs commits poussés d'un coup, ce qui a caché un commit rouge ; des erreurs de copier-coller dans les tests (`Shift.objects.get` pour relire une demande de repos) et dans les modèles (`models.Mode`, `CharFiled`, une annotation `-> engine.Shift` sur la conversion d'une demande) ; une première vue des infractions qui reprenait `CheckScheduleSerializer`, lequel valide un corps JSON absent d'un GET.
- **Appris :**
  - Un modèle Django hérite de `models.Model` ; ses champs sont des attributs de classe, et ce qui concerne la table entière (tri, contraintes) va dans sa classe `Meta`.
  - `makemigrations` écrit une migration à chaque changement de modèle, même pour une option sans effet en base comme `ordering` ; elle se commite avec le modèle.
  - Une migration est un fichier Python qu'on peut modifier, comme une migration Doctrine : `BtreeGistExtension()` doit y précéder la contrainte d'exclusion.
  - Sur PostgreSQL, Django crée des colonnes `timestamp with time zone` même avec `USE_TZ = False`, et règle le fuseau de la connexion sur `TIME_ZONE`.
  - `CheckConstraint` et `UniqueConstraint` sont dans `django.db.models`, `ExclusionConstraint` dans `django.contrib.postgres` ; depuis Django 6.0, une `CheckConstraint` prend `condition` et non `check`.
  - `F("start")` désigne une colonne de la même ligne ; `start__date__range` filtre sur la date d'une colonne de date et heure, bornes incluses.
  - Un `QuerySet` personnalisé, branché par `as_manager()`, joue le rôle des méthodes d'un repository Doctrine ; `select_related` ajoute une jointure et supprime le N+1.
  - `pytest.mark.django_db` donne accès à la base, dans une transaction annulée après chaque test ; une `IntegrityError` casse cette transaction, donc le test doit s'arrêter là.
  - pytest-django fournit `admin_client` et `django_assert_num_queries` ; une fixture s'injecte par le nom du paramètre et ne s'importe jamais ; `conftest.py` partage les fixtures entre les fichiers de tests.
  - Un `ModelSerializer` déduit ses champs du modèle, à condition que `fields` soit dans sa `Meta` ; `SlugRelatedField` affiche une clé étrangère par un autre champ que son identifiant ; une `ValidationError` levée dans `get_queryset()` donne une réponse 400.
  - `full_clean()` vérifie les contraintes en Python avant l'enregistrement, et c'est ce que fait l'admin ; `violation_error_message` remplace le message par défaut.
  - Deux chaînes écrites l'une après l'autre sont collées par Python, mais une virgule entre elles crée un tuple.
  - `return a, b` renvoie un tuple que l'appelant décompose avec `start, end = ...` ; `self` ne s'annote jamais.
  - `git rebase --autostash` met de côté les modifications en cours le temps du rebase.
  - Plusieurs commits poussés d'un coup ne sont testés par la CI que sur le dernier.

### Tests

- `test_stored_shift_converts_to_engine_shift`, une nuit enregistrée et relue depuis la base : écrit pas à pas avec l'IA. A fait naître l'application `schedules`, `StaffMember`, `Shift`, `to_engine()` et la première migration. La revue du modèle a relevé l'héritage de `models.Model` oublié, `CharFiled`, `engine.ShiftKind()` appelé au lieu d'être parcouru, un `@property` sur `to_engine`, puis `models.Mode`.
- `test_shift_ending_before_its_start_cannot_be_stored` : a fait naître la `CheckConstraint`.
- `test_staff_code_cannot_be_stored_twice` : a fait naître `unique=True` sur le code, qui sert de `staff_id` au moteur.
- `test_stored_day_off_request_converts_to_engine_request` : a fait naître `DayOffRequest`. Le test relisait d'abord la demande avec `Shift.objects.get` : corrigé avant le code.
- `test_day_off_request_cannot_be_stored_twice` : a fait naître la `UniqueConstraint`.
- `test_overlapping_shifts_of_the_same_staff_cannot_be_stored` : a fait naître l'`ExclusionConstraint`, la fonction `TsTzRange` et l'extension `btree_gist`. Une variable inutilisée, signalée par ruff, a été retirée par un fixup.
- `test_back_to_back_shifts_can_be_stored` : vert dès le premier lancement. Vérifié en écrivant `RangeBoundary(inclusive_upper=True)` dans la migration : il échoue.
- `test_overlapping_shifts_of_different_staff_can_be_stored` : vert dès le premier lancement. Vérifié en retirant `("staff", "=")` de la migration : il échoue.
- Remaniement, fixtures `api_client` et `nurse` déplacées dans `conftest.py` : aucune assertion modifiée.
- `test_staff_members_are_listed`, soignants créés dans le désordre pour que le tri compte : a fait naître `StaffMemberSerializer`, `StaffMemberListView` et le tri par code. Vérifié en inversant le tri : il échoue. Retirer le tri ne suffit pas : PostgreSQL peut renvoyer le bon ordre par hasard.
- `test_shifts_of_the_period_are_listed` : a fait naître `PeriodSerializer`, `StoredShiftSerializer`, `starting_between()`, `ShiftListView` et le tri des postes. La liste `fields` était d'abord hors de la `Meta`. Vérifié en inversant le tri, puis avec `start__range` au lieu de `start__date__range` : il échoue à chaque fois.
- `test_period_is_required` : vert dès le premier lancement. Vérifié en passant les deux champs à `required=False` : il échoue.
- `test_period_ending_before_its_start_is_rejected` : a fait naître `validate()` dans `PeriodSerializer`.
- `test_single_day_period_is_accepted` : idée et test de moi, pour fixer la borne. Vérifié en remplaçant `<` par `<=` : il échoue.
- Remaniement, fonction `store_shift` dans les tests de l'API : aucune assertion modifiée.
- `test_stored_violations_of_the_period_are_returned` : a fait naître `StoredViolationsView`. Ma première version reprenait `CheckScheduleSerializer` et jetait la liste des postes convertis : corrigée avant le commit.
- `test_stored_day_off_requests_are_used` : a fait naître `between()` et la transmission des demandes au moteur.
- `test_violations_ignore_shifts_outside_the_period` : vert dès le premier lancement. Vérifié en remplaçant `starting_between()` par `Shift.objects.all()` dans la vue : il échoue. Il fixe aussi une limite notée dans le README.
- `test_violations_are_computed_with_two_queries` : huit requêtes avant le code ; a fait naître les deux `select_related`. La première version ne créait aucune demande de repos, et le `select_related` des demandes n'était donc pas couvert : trouvé par l'IA en le retirant, corrigé par un fixup. Vérifié en retirant chaque `select_related` : il échoue à chaque fois.
- `test_admin_lists_stored_shifts` : a fait naître `admin.py`, la route `admin/` et le `__str__` de `StaffMember`. La fixture `admin_client` était d'abord utilisée sans être en paramètre du test.
- `test_staff_member_is_displayed_with_its_code_and_name`, `test_shift_is_displayed_with_its_staff_kind_and_slot` et `test_day_off_request_is_displayed_with_its_staff_and_day` : ajoutés pour les `__str__` des modèles. Le premier, vert d'emblée, a été vérifié en changeant le format ; les deux autres ont fait naître leur `__str__`. Celui des postes renvoyait d'abord un tuple, à cause d'une virgule entre deux f-strings.
- `test_overlapping_shift_is_reported_by_validation` : a fait naître le message de la contrainte d'exclusion.
- `test_shift_ending_before_its_start_is_reported_by_validation` : échouait sur une `DataError` de PostgreSQL ; a fait naître la `condition` de la contrainte d'exclusion et le message de la `CheckConstraint`. Vérifié en retirant chacun : il échoue à chaque fois.
