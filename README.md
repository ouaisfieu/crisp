# CRISP — fan club non officiel

**Encyclopédie visuelle et graphe de connaissances consacrés au [CRISP](https://www.crisp.be/fr/)**, le Centre de recherche et d'information socio-politiques (Bruxelles, 1958 →).

> ⚠️ **Projet indépendant.** Ce site n'est ni édité, ni relu, ni approuvé par le CRISP. Il ne reproduit aucune de ses publications : il en résume les apports, cite ses sources et renvoie systématiquement vers elles. Pour la référence, allez à la source : **[crisp.be](https://www.crisp.be/fr/)**.

🔗 **[ouaisfieu.github.io/crisp](https://ouaisfieu.github.io/crisp/)** · [BROL 2.0 — dashboard central](https://dl.ouaisfi.eu/usba/)

---

## Ce que c'est

Un site **100 % statique**, sans framework, sans dépendance d'exécution, sans traceur et sans cookie :

| | |
|---|---|
| **22 pages** | accueil, graphe, histoire, équipe, collections, publications, chronologie, glossaire, 10 dossiers, à propos, 404, hors-ligne |
| **Graphe de connaissances** | 131 nœuds, 221 liens — simulation de forces maison en canvas, façon Obsidian |
| **Glossaire** | 44 notions du droit public et de la vie politique belges |
| **Publications** | 26 parutions récentes du CRISP (2022-2026), filtrables par thème |
| **Poids** | pas de bundle, pas de build côté client ; le graphe pèse ~60 ko de JSON |

### Fonctionnalités

- 🕸 **Graphe interactif** — zoom / pan / drag, filtres par famille de nœuds, recherche instantanée, panneau de relations, deep-linking (`/graphe/#n=crisp`), fit automatique
- ⌘ **Palette de recherche globale** (<kbd>Ctrl/⌘</kbd>+<kbd>K</kbd> ou <kbd>/</kbd>) sur l'ensemble des pages, notions, publications et nœuds
- 🌗 **Thème clair / sombre** respectant `prefers-color-scheme`, avec bascule persistée
- 📴 **PWA installable**, fonctionnelle hors ligne (service worker, page de repli dédiée)
- 🔍 **SEO & web sémantique** — JSON-LD schema.org (`WebSite`, `Organization`, `WebPage`, `BreadcrumbList`, `Article`, `ItemList`/`ScholarlyArticle`, `DefinedTermSet`), Open Graph, Twitter Cards, `sitemap.xml`, `robots.txt`, flux RSS, `humans.txt`, canoniques
- 🖼 **Images Open Graph générées** — une par page, 1200 × 630, dessinées en SVG puis rasterisées
- 📣 **Partage social** — Bluesky, Mastodon, X, LinkedIn, Facebook, Web Share API, copie du lien
- ♿ **Accessibilité** — lien d'évitement, `aria-current`, `aria-pressed`, focus visibles, `prefers-reduced-motion`, contrastes vérifiés dans les deux thèmes
- 🖨 **Feuille d'impression** dédiée

---

## Structure

```
.
├── content/            # la matière : données + texte éditorial
│   ├── entities.json       # nœuds et arêtes du graphe
│   ├── publications.json   # parutions récentes du CRISP
│   ├── glossary.json       # notions
│   ├── timeline.json       # jalons 1958 → 2026
│   ├── pages.py            # pages principales
│   └── dossiers.py         # les 10 dossiers thématiques
├── tools/
│   └── build.py        # générateur statique (bibliothèque standard Python)
├── site/               # ← SORTIE : le site déployable, versionné
│   ├── index.html, graphe/, histoire/, …
│   ├── assets/{css,js,data,img}
│   ├── sitemap.xml, robots.txt, feed.xml, manifest.webmanifest, sw.js
│   └── .nojekyll
└── .github/workflows/deploy.yml
```

Le dossier `site/` est **committé** : le dépôt est déployable tel quel, même sans exécuter le générateur.

---

## Reconstruire

```bash
python3 tools/build.py
```

Aucune dépendance obligatoire. `cairosvg` est facultatif : sans lui, les images Open Graph restent en SVG au lieu d'être rasterisées en PNG.

```bash
pip install cairosvg   # facultatif, pour les PNG Open Graph
```

### Changer d'URL

Le site est construit pour un sous-répertoire (`/crisp/`, cas d'une GitHub Page de projet). Pour un domaine racine :

```bash
CRISP_BASE=/ CRISP_ORIGIN=https://exemple.be python3 tools/build.py
```

### Servir en local

```bash
python3 tools/build.py
cd .. && python3 -m http.server 8000   # puis http://localhost:8000/crisp/
```

---

## Déploiement

Le workflow `.github/workflows/deploy.yml` reconstruit le site et le publie sur GitHub Pages à chaque `push` sur `main`.

Côté dépôt : **Settings → Pages → Source : GitHub Actions**.

---

## Sources

Tout le contenu factuel est recoupé sur les sources primaires :

- [crisp.be](https://www.crisp.be/fr/) — présentation, équipe, collections, catalogue
- [vocabulairepolitique.be](https://www.vocabulairepolitique.be/) — les notions
- [actionnariatwallon.be](https://actionnariatwallon.be/) — la base de données économique
- [Courrier hebdomadaire sur Cairn](https://shs.cairn.info/revue-courrier-hebdomadaire-du-crisp?lang=fr)

Les divergences entre notes de synthèse et sources officielles ont systématiquement été tranchées en faveur des secondes. La méthode complète est exposée sur la page [« Méthode & sources »](https://ouaisfieu.github.io/crisp/a-propos/).

**Une erreur ?** [Ouvrez une issue](https://github.com/ouaisfieu/crisp/issues) — les faits comptent plus que l'effet.

---

## Licences

- **Code** (`tools/`, `site/assets/css`, `site/assets/js`) : [MIT](LICENSE)
- **Contenu rédactionnel** (`content/`, textes des pages) : [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr)
- Les publications du CRISP citées restent la propriété de leurs auteurs et de leur éditeur.

Polices : [Fraunces](https://fonts.google.com/specimen/Fraunces), [Inter](https://fonts.google.com/specimen/Inter), [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) — via Google Fonts, avec repli système complet.

---

Conception, recherche, rédaction, design et code : **Claude** (Anthropic), pour un mainteneur qui préfère l'anonymat.
