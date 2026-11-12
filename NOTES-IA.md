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
- **Appris :** Python ne vérifie pas les types annotés à l'exécution, contrairement à PHP ; `@dataclass` génère le constructeur à partir des champs ; l'indentation délimite les blocs.

### Tests

- Test 1, poste qui finit avant de commencer : écrit avec l'IA, ligne par ligne.
