# Pousser ce dépôt sur GitHub

Le dossier livré est **déjà un dépôt git** avec son historique (6 commits) et la
branche `main`. Il ne reste qu'à le relier à `ouaisfieu/crisp` et à pousser.

```bash
unzip crisp-fanclub.zip
cd crisp

git remote add origin git@github.com:ouaisfieu/crisp.git
# (ou en HTTPS : git remote add origin https://github.com/ouaisfieu/crisp.git)

git push -u origin main
```

Si le dépôt distant contient déjà quelque chose (un README créé à la volée) :

```bash
git push -u origin main --force
```

## Activer GitHub Pages

Sur GitHub : **Settings → Pages → Build and deployment → Source : GitHub Actions**.

Le workflow `.github/workflows/deploy.yml` fait le reste à chaque `push` sur
`main` : il régénère le site avec `tools/build.py`, vérifie liens et
métadonnées avec `tools/check.py`, puis publie.

Le site sera en ligne sur **https://ouaisfieu.github.io/crisp/**
(deux à trois minutes après le premier push).

## Domaine personnalisé (facultatif)

```bash
echo "crisp.ouaisfi.eu" > site/CNAME
CRISP_BASE=/ CRISP_ORIGIN=https://crisp.ouaisfi.eu python3 tools/build.py
git commit -am "Domaine personnalisé"
git push
```

Puis **Settings → Pages → Custom domain**.

## Vérifier en local avant de pousser

```bash
python3 tools/build.py && python3 tools/check.py
cd .. && python3 -m http.server 8000
# http://localhost:8000/crisp/
```
