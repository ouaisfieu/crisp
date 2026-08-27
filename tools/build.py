#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur statique — fan club non officiel du CRISP.

Ne demande rien d'autre que Python 3 (bibliothèque standard).
Le résultat, dans site/, est du HTML/CSS/JS pur : aucun runtime,
aucune dépendance, déployable tel quel sur n'importe quel hébergeur.

    python3 tools/build.py
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
SITE = os.path.join(ROOT, "site")

sys.path.insert(0, CONTENT)
import pages as PAGES  # noqa: E402

# ----------------------------------------------------------------- config
CONF = {
    "name": "CRISP — Fan club non officiel",
    "short": "CRISP · fan club",
    "tagline": "Cartographier le pouvoir en Belgique",
    "desc": ("Encyclopédie visuelle et graphe de connaissances consacrés au CRISP, "
             "le Centre de recherche et d'information socio-politiques : son histoire depuis 1958, "
             "ses chercheurs, ses collections et les grands dossiers de la politique belge contemporaine. "
             "Site hommage indépendant, sans lien officiel avec le CRISP."),
    "base": os.environ.get("CRISP_BASE", "/crisp/"),
    "origin": os.environ.get("CRISP_ORIGIN", "https://ouaisfieu.github.io"),
    "lang": "fr-BE",
    "author": "Claude (Anthropic) — pour un mainteneur anonyme",
    "repo": "https://github.com/ouaisfieu/crisp",
    "brol": "https://dl.ouaisfi.eu/usba/",
    "official": "https://www.crisp.be/fr/",
}
CONF["url"] = CONF["origin"].rstrip("/") + CONF["base"]
BUILD_DATE = datetime.now(timezone.utc)

NAV = [
    ("", "Accueil"),
    ("graphe/", "Graphe"),
    ("histoire/", "Histoire"),
    ("equipe/", "Équipe"),
    ("collections/", "Collections"),
    ("publications/", "Publications"),
    ("dossiers/", "Dossiers"),
    ("glossaire/", "Glossaire"),
    ("chronologie/", "Chronologie"),
    ("a-propos/", "À propos"),
]

# ----------------------------------------------------------------- helpers
def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as fh:
        return json.load(fh)


def u(path=""):
    """URL absolue depuis la racine du site (tient compte du sous-répertoire)."""
    return CONF["base"] + path.lstrip("/")


def full(path=""):
    return CONF["origin"].rstrip("/") + u(path)


ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    "minus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2"/></svg>',
    "share": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.5-1.5"/></svg>',
    "mastodon": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.3 8.3c0-4.2-2.8-5.4-2.8-5.4C17.1 2.2 14.7 2 12.2 2h-.1c-2.5 0-4.9.2-6.3.9 0 0-2.8 1.2-2.8 5.4v3.1c0 4.7.3 8.4 4.9 9.6 2.1.5 3.9.6 5.4.6 2.7 0 4.2-.8 4.2-.8l-.1-2s-1.9.6-4.1.5c-2.1-.1-4.4-.2-4.7-2.8v-.5s2.1.5 4.8.6c1.6.1 3.2-.1 4.8-.3 3.4-.4 6.3-2.5 6.7-4.4.6-3 .5-7.6.5-7.6zm-3.5 5.9h-2.2V8.9c0-1.1-.5-1.7-1.4-1.7-1 0-1.6.7-1.6 1.9v2.8h-2.1V9.1c0-1.2-.5-1.9-1.6-1.9-.9 0-1.4.6-1.4 1.7v5.3H5.3V8.7c0-1.1.3-2 .9-2.6.6-.7 1.4-1 2.4-1 1.1 0 2 .4 2.6 1.3l.5.9.5-.9c.6-.9 1.5-1.3 2.6-1.3 1 0 1.8.3 2.4 1 .6.6.9 1.5.9 2.6v5.5z"/></svg>',
    "bluesky": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5.8 3.7C8.5 5.7 11.3 9.8 12 12c.7-2.2 3.5-6.3 6.2-8.3C20.2 2.3 23 1.2 23 4.4c0 .6-.4 5.3-.6 6-.7 2.7-3.4 3.4-5.9 3 4.3.7 5.4 3.2 3 5.6-4.5 4.6-6.4-1.1-6.9-2.6l-.6-1.5-.6 1.5c-.5 1.5-2.4 7.2-6.9 2.6-2.3-2.4-1.2-4.9 3-5.6-2.4.4-5.1-.3-5.8-3-.2-.7-.6-5.4-.6-6C1 1.2 3.8 2.3 5.8 3.7z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 3h3.2l-7 8 8.2 10h-6.4l-5-6.1-5.7 6.1H1.6l7.5-8.6L1.2 3h6.6l4.5 5.6L17.5 3zm-1.1 16.1h1.8L7.7 4.8H5.8l10.6 14.3z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.5c0-1.31-.02-3-1.83-3-1.84 0-2.12 1.43-2.12 2.9V21H9z"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg>',
    "rss": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1.5" fill="currentColor"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48l-.01-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.36 1.09 2.93.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.5 9.5 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.93.36.31.68.92.68 1.85l-.01 2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>',
}


def mark(w=30, h=30):
    """Logo : un petit graphe — trois nœuds, trois liens."""
    return (
        '<svg class="mark" width="%d" height="%d" viewBox="0 0 32 32" fill="none" aria-hidden="true">'
        '<path d="M16 6 6 24M16 6l10 18M6 24h20" stroke="currentColor" stroke-opacity=".32" stroke-width="1.4"/>'
        '<circle cx="16" cy="6" r="4" fill="#f2c14e"/>'
        '<circle cx="6" cy="24" r="3.4" fill="#e4483d"/>'
        '<circle cx="26" cy="24" r="3.4" fill="#7aa2f7"/>'
        "</svg>" % (w, h)
    )


def share_block(path, title):
    url = full(path)
    t = escape(title, quote=True)
    q = url.replace("&", "%26")
    return f"""
<div class="share">
  <span class="label">Partager</span>
  <a href="https://bsky.app/intent/compose?text={escape(title)}%20{q}" target="_blank" rel="noopener" aria-label="Partager sur Bluesky" title="Bluesky">{ICONS['bluesky']}</a>
  <a href="https://mastodonshare.com/?text={escape(title)}&url={q}" target="_blank" rel="noopener" aria-label="Partager sur Mastodon" title="Mastodon">{ICONS['mastodon']}</a>
  <a href="https://twitter.com/intent/tweet?text={escape(title)}&url={q}" target="_blank" rel="noopener" aria-label="Partager sur X" title="X">{ICONS['x']}</a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url={q}" target="_blank" rel="noopener" aria-label="Partager sur LinkedIn" title="LinkedIn">{ICONS['linkedin']}</a>
  <a href="https://www.facebook.com/sharer/sharer.php?u={q}" target="_blank" rel="noopener" aria-label="Partager sur Facebook" title="Facebook">{ICONS['fb']}</a>
  <button data-share="copy" aria-label="Copier le lien" title="Copier le lien">{ICONS['link']}</button>
  <button data-share="native" aria-label="Partager…" title="Partager…">{ICONS['share']}</button>
</div>"""


def breadcrumbs(trail):
    """trail = [(href, label), ...] — dernier élément = page courante."""
    if len(trail) < 2:
        return ""
    parts = []
    items = []
    for i, (href, label) in enumerate(trail):
        if i < len(trail) - 1:
            parts.append(f'<a href="{u(href)}">{escape(label)}</a>')
        else:
            parts.append(f"<span>{escape(label)}</span>")
        items.append({
            "@type": "ListItem", "position": i + 1, "name": label, "item": full(href)
        })
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
    return ('<nav class="breadcrumb" aria-label="Fil d\'Ariane">' + " / ".join(parts) + "</nav>"
            + jsonld(ld))


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


ORG_LD = {
    "@type": "Organization",
    "@id": "https://www.crisp.be/#organization",
    "name": "Centre de recherche et d'information socio-politiques",
    "alternateName": "CRISP",
    "url": "https://www.crisp.be/fr/",
    "foundingDate": "1958",
    "founder": {"@type": "Person", "name": "Jules Gérard-Libois"},
    "address": {"@type": "PostalAddress", "streetAddress": "Place Quetelet 1A",
                "postalCode": "1210", "addressLocality": "Saint-Josse-ten-Noode",
                "addressCountry": "BE"},
    "sameAs": ["https://fr.wikipedia.org/wiki/Centre_de_recherche_et_d%27information_socio-politiques",
               "https://www.vocabulairepolitique.be/", "https://actionnariatwallon.be/"],
}


def page(slug, title, desc, body, *, trail=None, extra_head="", extra_ld=None,
         og_image=None, body_class="", scripts=(), article=None):
    """Assemble une page complète."""
    body = body.replace('href="~/', 'href="' + CONF["base"])
    canonical = full(slug)
    og = og_image or u("assets/img/og-default.png")
    og_abs = og if og.startswith("http") else CONF["origin"].rstrip("/") + og
    nav_html = "".join(
        '<a href="%s"%s>%s</a>' % (u(h), ' aria-current="page"' if h == slug else "", escape(l))
        for h, l in NAV
    )

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": CONF["url"] + "#website",
                "url": CONF["url"],
                "name": CONF["name"],
                "description": CONF["desc"],
                "inLanguage": "fr-BE",
                "publisher": {"@id": CONF["url"] + "#publisher"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": {"@type": "EntryPoint", "urlTemplate": full("glossaire/") + "?q={search_term_string}"},
                    "query-input": "required name=search_term_string",
                },
            },
            {
                "@type": "Organization",
                "@id": CONF["url"] + "#publisher",
                "name": "Fan club non officiel du CRISP",
                "url": CONF["url"],
                "description": "Projet indépendant d'hommage documentaire, sans lien officiel avec le CRISP.",
            },
            ORG_LD,
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": title,
                "description": desc,
                "isPartOf": {"@id": CONF["url"] + "#website"},
                "about": {"@id": "https://www.crisp.be/#organization"},
                "inLanguage": "fr-BE",
                "datePublished": "2026-08-27",
                "dateModified": BUILD_DATE.strftime("%Y-%m-%d"),
            },
        ],
    }
    if article:
        graph["@graph"].append(article)
    if extra_ld:
        graph["@graph"].extend(extra_ld if isinstance(extra_ld, list) else [extra_ld])

    js = "".join('<script src="%s" defer></script>' % u(s) for s in scripts)

    return f"""<!doctype html>
<html lang="fr" data-base="{CONF['base']}" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc, quote=True)}">
<link rel="canonical" href="{canonical}">
<meta name="author" content="{escape(CONF['author'])}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#08090c" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f5f0" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">

<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:site_name" content="{escape(CONF['name'])}">
<meta property="og:locale" content="fr_BE">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(desc, quote=True)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_abs}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape(title, quote=True)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title, quote=True)}">
<meta name="twitter:description" content="{escape(desc, quote=True)}">
<meta name="twitter:image" content="{og_abs}">

<link rel="icon" href="{u('assets/img/favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{u('assets/img/icon-180.png')}">
<link rel="manifest" href="{u('manifest.webmanifest')}">
<link rel="alternate" type="application/rss+xml" title="Fan club CRISP — flux" href="{u('feed.xml')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700&family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{u('assets/css/site.css')}">
{extra_head}
{jsonld(graph)}
<script>(function(){{try{{var t=localStorage.getItem('crisp-fc-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
</head>
<body class="{body_class}">
<a class="skip" href="#main">Aller au contenu</a>
<div class="progress" aria-hidden="true"></div>

<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{u('')}">
      {mark()}
      <span><b>CRISP</b><small>fan club non officiel</small></span>
    </a>
    <button class="icon-btn nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Ouvrir le menu">{ICONS['menu']}</button>
    <nav class="nav" id="primary-nav" aria-label="Navigation principale">{nav_html}</nav>
    <div class="tools">
      <button class="icon-btn" data-omni-open aria-label="Rechercher (Ctrl+K)" title="Rechercher — Ctrl+K">{ICONS['search']}</button>
      <button class="icon-btn" data-theme-toggle aria-label="Changer de thème" title="Changer de thème">{ICONS['sun']}</button>
    </div>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="{u('')}" style="margin-bottom:1rem">{mark(26,26)}<span><b>CRISP</b><small>fan club non officiel</small></span></a>
        <p class="disclaimer">Site hommage indépendant. Ce projet n'est <strong>pas</strong> édité par le CRISP, n'engage en rien l'institution et ne reproduit aucune de ses publications. Toutes les analyses sources restent la propriété de leurs auteurs. Pour la référence, allez à la source&nbsp;: <a href="{CONF['official']}" target="_blank" rel="noopener">crisp.be</a>.</p>
      </div>
      <div>
        <h4>Explorer</h4>
        <ul>
          <li><a href="{u('graphe/')}">Graphe de connaissances</a></li>
          <li><a href="{u('chronologie/')}">Chronologie 1958→2026</a></li>
          <li><a href="{u('glossaire/')}">Glossaire du pouvoir belge</a></li>
          <li><a href="{u('publications/')}">Publications récentes</a></li>
          <li><a href="{u('dossiers/')}">Dossiers thématiques</a></li>
        </ul>
      </div>
      <div>
        <h4>Sources officielles</h4>
        <ul>
          <li><a href="https://www.crisp.be/fr/" target="_blank" rel="noopener">crisp.be ↗</a></li>
          <li><a href="https://www.vocabulairepolitique.be/" target="_blank" rel="noopener">vocabulairepolitique.be ↗</a></li>
          <li><a href="https://actionnariatwallon.be/" target="_blank" rel="noopener">actionnariatwallon.be ↗</a></li>
          <li><a href="https://shs.cairn.info/revue-courrier-hebdomadaire-du-crisp?lang=fr" target="_blank" rel="noopener">Courrier hebdo. sur Cairn ↗</a></li>
        </ul>
      </div>
      <div>
        <h4>Ce projet</h4>
        <ul>
          <li><a href="{CONF['repo']}" target="_blank" rel="noopener">Code source (GitHub) ↗</a></li>
          <li><a href="{u('feed.xml')}">Flux RSS</a></li>
          <li><a href="{u('a-propos/')}">Méthode &amp; sources</a></li>
          <li><a href="{CONF['brol']}" target="_blank" rel="noopener">BROL 2.0 — dashboard ↗</a></li>
        </ul>
      </div>
    </div>
    <div class="colophon">
      <span>Contenu sous licence CC BY-SA 4.0 · code sous licence MIT · construit le {BUILD_DATE.strftime('%d/%m/%Y')}</span>
      <span>Conçu et rédigé par <strong>Claude</strong> (Anthropic) pour un mainteneur qui préfère l'anonymat.</span>
    </div>
  </div>
</footer>

<div class="omni" id="omni" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Recherche">
  <div class="omni-box">
    <div class="omni-input">{ICONS['search']}<input id="omni-input" type="search" placeholder="Chercher une notion, un chercheur, une publication…" autocomplete="off" spellcheck="false" aria-label="Rechercher sur le site"></div>
    <div class="omni-results" id="omni-results"></div>
    <div class="omni-foot"><span><kbd>↑</kbd><kbd>↓</kbd> naviguer</span><span><kbd>↵</kbd> ouvrir</span><span><kbd>esc</kbd> fermer</span></div>
  </div>
</div>

<script src="{u('assets/js/app.js')}" defer></script>
{js}
</body>
</html>
"""


def write(slug, html):
    path = os.path.join(SITE, slug, "index.html") if slug else os.path.join(SITE, "index.html")
    if slug.endswith(".html"):
        path = os.path.join(SITE, slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


# ----------------------------------------------------------------- OG images
def _wrap(s, per_line):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > per_line:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:4]


def og_image(slug, kicker, title, filename):
    """Génère une image Open Graph 1200x630 en SVG puis PNG."""
    lines = _wrap(title, 21)
    size = {1: 76, 2: 70, 3: 58, 4: 48}[len(lines)]
    lead = int(size * 1.16)
    top = 315 - int((len(lines) - 1) * lead / 2) + int(size * 0.34)
    tspans = "".join(
        '<tspan x="76" dy="%s">%s</tspan>' % ("0" if i == 0 else str(lead), escape(l))
        for i, l in enumerate(lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#08090c"/><stop offset="1" stop-color="#141822"/>
</linearGradient>
<radialGradient id="r1" cx="0.88" cy="0.08" r="0.75">
<stop offset="0" stop-color="#f2c14e" stop-opacity="0.26"/><stop offset="1" stop-color="#f2c14e" stop-opacity="0"/>
</radialGradient>
<radialGradient id="r2" cx="0.02" cy="1" r="0.65">
<stop offset="0" stop-color="#e4483d" stop-opacity="0.22"/><stop offset="1" stop-color="#e4483d" stop-opacity="0"/>
</radialGradient>
<pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
<path d="M60 0H0v60" fill="none" stroke="#ffffff" stroke-opacity="0.045"/>
</pattern>
</defs>
<rect width="1200" height="630" fill="url(#g)"/>
<rect width="1200" height="630" fill="url(#grid)"/>
<rect width="1200" height="630" fill="url(#r1)"/>
<rect width="1200" height="630" fill="url(#r2)"/>
<g opacity="0.9">
<g stroke="#ffffff" stroke-opacity="0.16" fill="none" stroke-width="1.4">
<path d="M1042 128 1120 250M1042 128 962 252M1120 250 962 252M962 252 1064 372M1120 250 1064 372M962 252 900 420M1064 372 900 420"/>
</g>
<circle cx="1042" cy="128" r="21" fill="#f2c14e"/>
<circle cx="1120" cy="250" r="13" fill="#7aa2f7"/>
<circle cx="962" cy="252" r="16" fill="#e4483d"/>
<circle cx="1064" cy="372" r="11" fill="#4ec9b0"/>
<circle cx="900" cy="420" r="9" fill="#c39bf5"/>
</g>
<text x="76" y="96" font-family="JetBrains Mono, DejaVu Sans Mono, monospace" font-size="21" letter-spacing="5" fill="#f2c14e">{escape(kicker.upper())}</text>
<text x="76" y="{top}" font-family="Fraunces, DejaVu Serif, Georgia, serif" font-size="{size}" font-weight="600" fill="#ffffff">{tspans}</text>
<text x="76" y="545" font-family="Inter, DejaVu Sans, sans-serif" font-size="24" fill="#98a1b3">Fan club non officiel du CRISP</text>
<text x="76" y="578" font-family="Inter, DejaVu Sans, sans-serif" font-size="24" fill="#5f6779">Cartographier le pouvoir en Belgique</text>
<rect x="76" y="112" width="96" height="3" fill="#f2c14e" opacity="0.6"/>
</svg>"""
    svg_path = os.path.join(SITE, "assets", "img", filename + ".svg")
    os.makedirs(os.path.dirname(svg_path), exist_ok=True)
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    png_rel = "assets/img/" + filename + ".png"
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=svg_path, write_to=os.path.join(SITE, png_rel),
                         output_width=1200, output_height=630)
        return u(png_rel)
    except Exception:
        return u("assets/img/" + filename + ".svg")


ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<rect width="512" height="512" rx="{r}" fill="#08090c"/>
<g transform="translate(256 256) scale({s}) translate(-256 -256)">
<path d="M256 128 136 384M256 128l120 256M136 384h240" stroke="#ffffff" stroke-opacity=".28" stroke-width="14" fill="none"/>
<circle cx="256" cy="128" r="56" fill="#f2c14e"/>
<circle cx="136" cy="384" r="44" fill="#e4483d"/>
<circle cx="376" cy="384" r="44" fill="#7aa2f7"/>
</g></svg>"""


def make_icons():
    img = os.path.join(SITE, "assets", "img")
    os.makedirs(img, exist_ok=True)
    fav = ICON_SVG.format(r=96, s=1.0)
    with open(os.path.join(img, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(fav)
    try:
        import cairosvg  # type: ignore
        for name, size, src in (("icon-192.png", 192, fav), ("icon-512.png", 512, fav),
                                ("icon-180.png", 180, fav),
                                ("maskable-512.png", 512, ICON_SVG.format(r=0, s=0.72))):
            cairosvg.svg2png(bytestring=src.encode("utf-8"),
                             write_to=os.path.join(img, name),
                             output_width=size, output_height=size)
    except Exception as exc:
        print("  (icônes PNG non générées : %s)" % exc)


# ----------------------------------------------------------------- build
def main():
    make_icons()
    entities = load("entities.json")
    pubs = load("publications.json")
    timeline = load("timeline.json")
    glossary = load("glossary.json")

    # --- données du graphe : entités + publications ---------------------
    gnodes = list(entities["nodes"])
    gedges = list(entities["edges"])
    person_ids = {n["label"]: n["id"] for n in entities["nodes"] if n["type"] == "person"}
    theme_node = {
        "elections": "volatilite", "partis": "particratie", "particratie": "particratie",
        "federalisme": "reformes-etat", "institutions": "reformes-etat",
        "gouvernement": "arizona", "concertation-sociale": "concertation",
        "economie": "actionnariat", "actionnariat": "actionnariat",
        "budget": "pouvoirs-speciaux", "social": "concertation",
        "medias": "cordon", "identite": "clivage", "extreme-droite": "cordon",
        "bruxelles": "bruxelles", "democratie": "tirage-au-sort", "local": "communales2024",
    }
    for p in pubs:
        nid = "pub-" + p["id"]
        gnodes.append({
            "id": nid, "label": p["title"][:40].rstrip() + ("…" if len(p["title"]) > 40 else ""),
            "type": "publication", "w": 6 if p.get("highlight") else 4,
            "year": p["year"], "href": "/publications/#" + p["id"], "url": p.get("url"),
            "summary": p.get("abstract", ""),
        })
        coll = {"ch": "ch", "analyses": "analyses", "livres": "livres"}.get(p["collection"], "ch")
        gedges.append([coll, nid, "n° " + str(p["num"])])
        for a in p["authors"]:
            if a in person_ids:
                gedges.append([person_ids[a], nid, "auteur"])
        for t in p.get("themes", []):
            tgt = theme_node.get(t)
            if tgt:
                gedges.append([nid, tgt, "porte sur"])

    ids = {n["id"] for n in gnodes}
    gedges = [e for e in gedges if e[0] in ids and e[1] in ids]
    # dédoublonnage
    seen, clean = set(), []
    for e in gedges:
        k = tuple(sorted(e[:2]))
        if k in seen or e[0] == e[1]:
            continue
        seen.add(k); clean.append(e)
    gedges = clean

    os.makedirs(os.path.join(SITE, "assets", "data"), exist_ok=True)
    with open(os.path.join(SITE, "assets", "data", "graph.json"), "w", encoding="utf-8") as fh:
        json.dump({"nodes": gnodes, "edges": gedges}, fh, ensure_ascii=False, separators=(",", ":"))

    ctx = {
        "conf": CONF, "u": u, "full": full, "icons": ICONS, "esc": escape,
        "entities": entities, "pubs": pubs, "timeline": timeline, "glossary": glossary,
        "nodes": gnodes, "edges": gedges, "share": share_block, "breadcrumbs": breadcrumbs,
        "jsonld": jsonld, "og_image": og_image, "mark": mark,
    }

    built = []
    for spec in PAGES.build_pages(ctx):
        html = page(
            spec["slug"], spec["title"], spec["desc"], spec["body"],
            trail=spec.get("trail"), extra_head=spec.get("head", ""),
            extra_ld=spec.get("ld"), og_image=spec.get("og"),
            body_class=spec.get("body_class", ""), scripts=spec.get("scripts", ()),
            article=spec.get("article"),
        )
        write(spec["slug"], html)
        built.append(spec)
        print("  ✓", spec["slug"] or "/")

    # --- index de recherche --------------------------------------------
    index = []
    for spec in built:
        if spec["slug"].endswith(".html"):
            continue
        index.append({"t": spec["title"].split(" — ")[0], "b": spec["desc"][:120],
                      "u": u(spec["slug"]), "k": "Page", "pin": spec.get("pin", False)})
    for g in glossary:
        index.append({"t": g["term"], "b": re.sub("<[^>]+>", "", g["def"])[:120],
                      "u": u("glossaire/") + "#" + g["id"], "k": "Notion"})
    for p in pubs:
        index.append({"t": p["title"], "b": ", ".join(p["authors"]) + " · " + str(p["year"]),
                      "u": u("publications/") + "#" + p["id"], "k": "Publication"})
    for n in entities["nodes"]:
        if n["type"] in ("person", "concept", "institution", "party", "collection", "database", "event"):
            index.append({"t": n["label"], "b": (n.get("summary") or "")[:120],
                          "u": u("graphe/") + "#n=" + n["id"], "k": "Graphe"})
    with open(os.path.join(SITE, "assets", "data", "search-index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, separators=(",", ":"))

    # --- sitemap --------------------------------------------------------
    urls = []
    for spec in built:
        if spec["slug"].endswith(".html"):
            continue
        prio = "1.0" if spec["slug"] == "" else ("0.9" if spec.get("pin") else "0.7")
        urls.append(
            f"<url><loc>{full(spec['slug'])}</loc>"
            f"<lastmod>{BUILD_DATE.strftime('%Y-%m-%d')}</lastmod>"
            f"<changefreq>monthly</changefreq><priority>{prio}</priority></url>"
        )
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap)

    with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n\nSitemap: %s\n" % full("sitemap.xml"))

    # --- flux RSS -------------------------------------------------------
    items = []
    for p in sorted(pubs, key=lambda x: (-x["year"], x["title"]))[:20]:
        link = full("publications/") + "#" + p["id"]
        items.append(
            "<item><title>%s</title><link>%s</link><guid isPermaLink=\"true\">%s</guid>"
            "<pubDate>%s</pubDate><description>%s</description></item>" % (
                escape(p["title"]), link, link,
                datetime(p["year"], 1, 1, tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
                escape(p.get("abstract", "")),
            )
        )
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f"<title>{escape(CONF['name'])}</title><link>{CONF['url']}</link>"
            f'<atom:link href="{full("feed.xml")}" rel="self" type="application/rss+xml"/>'
            f"<description>{escape(CONF['desc'])}</description><language>fr-be</language>"
            + "".join(items) + "</channel></rss>\n")
    with open(os.path.join(SITE, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(feed)

    # --- manifest & sw --------------------------------------------------
    manifest = {
        "name": CONF["name"], "short_name": "CRISP FC",
        "description": CONF["desc"][:200],
        "start_url": CONF["base"], "scope": CONF["base"],
        "display": "standalone", "background_color": "#08090c", "theme_color": "#08090c",
        "lang": "fr-BE", "categories": ["education", "news", "reference"],
        "icons": [
            {"src": u("assets/img/icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": u("assets/img/icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": u("assets/img/maskable-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "Graphe de connaissances", "url": u("graphe/")},
            {"name": "Glossaire", "url": u("glossaire/")},
            {"name": "Publications", "url": u("publications/")},
        ],
    }
    with open(os.path.join(SITE, "manifest.webmanifest"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)

    precache = [u(""), u("graphe/"), u("glossaire/"), u("assets/css/site.css"),
                u("assets/js/app.js"), u("assets/js/graph.js"),
                u("assets/data/graph.json"), u("assets/data/search-index.json"),
                u("offline.html")]
    sw = """/* Service worker — cache-first pour les ressources, réseau d'abord pour les pages. */
var V = 'crisp-fc-%s';
var PRECACHE = %s;
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return c.addAll(PRECACHE); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (n) { return n !== V; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(function (r) {
      var copy = r.clone(); caches.open(V).then(function (c) { c.put(req, copy); }); return r;
    }).catch(function () { return caches.match(req).then(function (m) { return m || caches.match('%s'); }); }));
    return;
  }
  e.respondWith(caches.match(req).then(function (m) {
    return m || fetch(req).then(function (r) {
      var copy = r.clone(); caches.open(V).then(function (c) { c.put(req, copy); }); return r;
    });
  }));
});
""" % (BUILD_DATE.strftime("%Y%m%d%H%M"), json.dumps(precache), u("offline.html"))
    with open(os.path.join(SITE, "sw.js"), "w", encoding="utf-8") as fh:
        fh.write(sw)

    with open(os.path.join(SITE, ".nojekyll"), "w") as fh:
        fh.write("")

    with open(os.path.join(SITE, "humans.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            "/* ÉQUIPE */\n"
            "Conception, rédaction, code : Claude (Anthropic)\n"
            "Commande & curation : un mainteneur anonyme\n"
            "Sujet : le CRISP — Centre de recherche et d'information socio-politiques\n\n"
            "/* SITE */\n"
            "Langue : français (Belgique)\n"
            "Standards : HTML5, CSS custom properties, JavaScript ES5+, JSON-LD, RSS 2.0\n"
            "Dépendances : aucune\n"
            "Construit le : %s\n" % BUILD_DATE.strftime("%d/%m/%Y")
        )

    print("\n%d pages · %d nœuds · %d liens · %d entrées d'index"
          % (len(built), len(gnodes), len(gedges), len(index)))


if __name__ == "__main__":
    main()
