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
- **Appris :** Python ne vérifie pas les types annotés à l'exécution, contrairement à PHP ; `@dataclass` génère le constructeur à partir des champs ; l'indentation délimite les blocs ;
`len()` est une fonction et pas une méthode, `date` et `datetime` sont deux types distincts, et `git reset --soft` permet de refaire un commit ;
les dictionnaires (`dict`) sont l'équivalent des tableaux associatifs de PHP, `collections.defaultdict` crée automatiquement une valeur vide pour une clé absente, et `.items()` parcourt à la fois les clés et les valeurs ;
Python compare les tuples élément par élément, ce qui permet de trier sur plusieurs critères avec `operator.attrgetter` ; `continue` passe directement au tour de boucle suivant ; une valeur par défaut immuable comme un `timedelta` ne pose pas de problème, contrairement à une liste..

### Tests

- Test 1, poste qui finit avant de commencer : écrit avec l'IA, ligne par ligne.
- Test 2, durée d'un poste de nuit à cheval sur minuit : écrit seul. Nom traduit par l'IA ; deux corrections pendant la revue, la comparaison avec `12` au lieu d'un `timedelta`, et l'import manquant de `timedelta`.
- Test 3, planning vide sans infraction de repos : écrit à partir de squelettes à trous fournis par l'IA, pour le test comme pour la fonction. Nom proposé par l'IA. La revue a montré que `assert not violations` laissait passer une fonction qui renvoie `None` : remplacé par `assert violations == []`.
- Test 4, repos égal au minimum (12 heures pile) : écrit seul, nom corrigé pendant la revue. Passé du premier coup, puisque la règle renvoyait encore une liste vide. Vérifié après le test 5 : en remplaçant `<` par `<=` dans la règle, il échoue.
- Test 5, repos de 11 heures : écrit seul, puis corrigé pendant la revue sur quatre points : un nom qui contredisait l'assertion, `violations != []` trop faible (vrai aussi pour `None`), `violations.__len__` sans parenthèses au lieu de `len(violations)`, et `datetime` au lieu de `date` pour le jour. Ce test a fait naître `Violation`, `RuleCategory` et la règle, écrite avec `itertools.pairwise`.
- Test 6, postes de deux soignants différents : écrit seul. Il échouait bien avec la première version de la règle, qui comparait tous les postes qui se suivent dans la liste, quel que soit le soignant.
- Test ajouté au plan, postes d'un soignant intercalés avec ceux d'un autre (A, B, A) : idée venue de la revue, test écrit seul. Une simple vérification du soignant dans la boucle l'aurait laissé échouer, car les deux postes de A ne se suivent pas dans la liste. Ce test m'a obligé à revoir la conception de la règle : l'IA m'a présenté deux approches, le regroupement par soignant ou le tri, et j'ai choisi et écrit le regroupement avec `collections.defaultdict`. La revue a fait retirer une condition sur le soignant devenue inutile.
- Remaniement après le test 6, fonction `make_shift` pour créer les postes dans les tests : écrite seul. Durée de 12 heures par défaut, modifiable pour créer des postes atypiques (10 h 15, par exemple). Aucune assertion modifiée ; les tests passaient avant et après. L'IA a expliqué la virgule finale « magique » de ruff, qui garde un appel déplié sur plusieurs lignes : une fois retirée, chaque création de poste tient sur une ligne. L'IA avait d'abord conseillé une valeur par défaut `None` en invoquant la règle B008 ; c'était faux, un `timedelta` est immuable et peut servir directement de valeur par défaut. Corrigé ensuite.
- Test 7, postes dans le désordre : test et correction écrits seul. Avant la correction, le test échouait sur un repos négatif de 36 heures, que Python affiche sous la forme `-2 days, 12:00:00`. J'ai remplacé le regroupement par `defaultdict` par un tri unique avec `sorted()` et `operator.attrgetter("staff_id", "start")` : les postes de chaque soignant se suivent alors dans l'ordre chronologique, et `continue` saute les paires de deux soignants différents. L'IA a vérifié l'échec du test avant la correction et contrôlé, en modifiant volontairement le code, que les tests existants protègent le tri et le saut entre soignants.
- Test ajouté au plan, postes dans le désordre et intercalés avec ceux d'un autre soignant : idée et test de moi. Vert dès le premier lancement ; vérifié en retirant le tri : il échoue. L'IA a cherché s'il faisait doublon avec les autres. Une fausse correction du test 7, qui aurait gardé le regroupement par `defaultdict` et pris la valeur absolue de la durée de repos (`abs()`) au lieu de trier, passe tous les autres tests, et seul celui-ci la détecte. Le test 7 vérifie que le désordre ne crée pas d'infraction, celui-ci qu'il n'en masque pas.
- Test 8, seuil abaissé à 11 heures : écrit seul. Mêmes postes que `test_rest_below_minimum_has_daily_rest_violation`, seul le seuil change. Vert dès le premier lancement, puisque le seuil était déjà un paramètre ; vérifié en écrivant `timedelta(hours=12)` en dur dans la règle : seul ce test échoue, les autres utilisant tous 12 heures. Nom corrigé pendant la revue. Ce test justifie le seuil en paramètre : 12 heures dans la fonction publique hospitalière, 11 heures pour les salariés de droit privé.
