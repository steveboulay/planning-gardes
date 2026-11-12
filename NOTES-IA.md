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
