#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôle qualité du site généré : liens internes, JSON-LD, métadonnées, graphe."""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE = os.environ.get("CRISP_BASE", "/crisp/")

errors, warnings = [], []


def pages_set():
    known = set()
    for dp, _, fs in os.walk(SITE):
        for f in fs:
            rel = "/" + os.path.relpath(os.path.join(dp, f), SITE).replace(os.sep, "/")
            known.add(BASE.rstrip("/") + rel)
            if f == "index.html":
                known.add(BASE.rstrip("/") + rel[: -len("index.html")])
    return known


def main():
    known = pages_set()
    n_html = 0
    for dp, _, fs in os.walk(SITE):
        for f in fs:
            if not f.endswith(".html"):
                continue
            n_html += 1
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, ROOT)
            html = open(path, encoding="utf-8").read()

            # liens internes
            for m in re.finditer(r'(?:href|src)="([^"]+)"', html):
                h = m.group(1)
                if h.startswith(("http", "mailto:", "#", "data:")):
                    continue
                target = h.split("#")[0].split("?")[0]
                if target and target not in known:
                    errors.append("%s → lien mort %s" % (rel, h))

            # JSON-LD
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
                try:
                    json.loads(m.group(1))
                except Exception as exc:
                    errors.append("%s → JSON-LD invalide (%s)" % (rel, exc))

            # métadonnées
            for tag, pattern, limit in (
                ("title", r"<title>(.*?)</title>", 65),
                ("description", r'name="description" content="(.*?)"', 170),
            ):
                mm = re.search(pattern, html, re.S)
                if not mm:
                    errors.append("%s → %s manquant" % (rel, tag))
                elif len(mm.group(1)) > limit:
                    warnings.append("%s → %s de %d caractères" % (rel, tag, len(mm.group(1))))

            for needed in ('property="og:image"', 'rel="canonical"', 'lang="fr"'):
                if needed not in html:
                    errors.append("%s → %s manquant" % (rel, needed))

    # graphe
    gp = os.path.join(SITE, "assets", "data", "graph.json")
    if os.path.exists(gp):
        g = json.load(open(gp, encoding="utf-8"))
        ids = {n["id"] for n in g["nodes"]}
        deg = {i: 0 for i in ids}
        for e in g["edges"]:
            if e[0] not in ids or e[1] not in ids:
                errors.append("graphe → arête orpheline %s" % (e,))
            else:
                deg[e[0]] += 1
                deg[e[1]] += 1
        for i, d in deg.items():
            if d == 0:
                warnings.append("graphe → nœud isolé : %s" % i)
        print("graphe : %d nœuds, %d liens" % (len(g["nodes"]), len(g["edges"])))
    else:
        errors.append("graphe → assets/data/graph.json absent")

    for f in ("sitemap.xml", "robots.txt", "feed.xml", "manifest.webmanifest", "sw.js", ".nojekyll"):
        if not os.path.exists(os.path.join(SITE, f)):
            errors.append("fichier manquant : %s" % f)

    print("%d pages HTML contrôlées" % n_html)
    for w in warnings:
        print("  ⚠ %s" % w)
    if errors:
        for e in errors:
            print("  ✗ %s" % e)
        print("\n%d erreur(s)." % len(errors))
        sys.exit(1)
    print("✓ tout est en ordre (%d avertissement(s))" % len(warnings))


if __name__ == "__main__":
    main()
