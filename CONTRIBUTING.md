# Contribuer

## Corriger un fait

C'est la contribution la plus utile. Les faits comptent plus que l'effet.

1. Ouvrez une [issue](https://github.com/ouaisfieu/crisp/issues) en indiquant la page, l'affirmation contestée et la source qui la contredit.
2. Ou proposez directement une *pull request* : le contenu vit dans `content/`, jamais dans `site/` (qui est régénéré).

Règle du projet : **en cas de divergence entre une source secondaire et une source officielle du CRISP, la source officielle l'emporte.**

## Modifier le contenu

| Vous voulez… | Fichier |
|---|---|
| ajouter une publication | `content/publications.json` |
| ajouter une notion au glossaire | `content/glossary.json` |
| ajouter un nœud ou une relation au graphe | `content/entities.json` |
| ajouter un jalon à la chronologie | `content/timeline.json` |
| modifier une page | `content/pages.py` |
| modifier ou ajouter un dossier | `content/dossiers.py` |

Puis :

```bash
python3 tools/build.py
python3 tools/check.py
```

`tools/check.py` doit se terminer sans erreur — c'est aussi ce que vérifie la CI.

## Style

- Français de Belgique, espaces insécables avant `: ; ! ?` (`&nbsp;`), guillemets français.
- Pas de superlatif non sourcé. Un chiffre sans source ne passe pas.
- Aucun texte du CRISP n'est reproduit : on résume, on cite, on renvoie.
