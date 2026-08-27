# -*- coding: utf-8 -*-
"""Contenu éditorial du site. Chaque fonction renvoie un dict de spécification de page."""

import re
from html import escape
import dossiers as DOSSIERS


# --------------------------------------------------------------- helpers
def section(inner, cls="", wrap="wrap", el="section", attrs=""):
    return f'<{el} class="{cls}" {attrs}><div class="{wrap}">{inner}</div></{el}>'


def eyebrow(t):
    return f'<p class="eyebrow">{t}</p>'


def stat(value, label, count=None, pre="", suf=""):
    if count is not None:
        return (f'<div class="stat"><b data-count="{count}" data-pre="{pre}" data-suf="{suf}">{pre}0{suf}</b>'
                f"<span>{label}</span></div>")
    return f'<div class="stat"><b>{value}</b><span>{label}</span></div>'


TEAM = [
    ("decoorebyter", "Vincent de Coorebyter", "Président",
     "Philosophe et politologue, il préside le conseil d'administration. On lui doit la relecture socio-historique de la théorie des clivages qui structure aujourd'hui la lecture francophone de l'offre partisane : un clivage n'est pas une opposition d'opinions mais un processus en trois temps — prise de conscience d'un déséquilibre, auto-organisation dans la société civile, création de partis.",
     ["Théorie des clivages", "Philosophie politique", "Laïcité"]),
    ("faniel", "Jean Faniel", "Directeur général · secteur socio-politique",
     "Politologue. Son terrain : l'argent et les rouages. Financement de la vie politique et des partis, mécanismes électoraux, concertation sociale, chômage et politiques de l'emploi, formation des gouvernements fédéraux — des coalitions Vivaldi à Arizona —, évolution de la société civile, rôle du kern. C'est la voix que les rédactions appellent quand une crise gouvernementale s'ouvre.",
     ["Financement des partis", "Concertation sociale", "Formation des gouvernements", "Dépilarisation"]),
    ("blaise", "Pierre Blaise", "Secrétaire général · secteur socio-politique",
     "Sociologue. Il travaille la démocratie là où on l'observe le moins : dans l'entreprise. Élections sociales, rôle réel des syndicats — ce qu'il a appelé « l'illusion de la puissance » —, organisations patronales, relations entre le tissu associatif et l'agenda politique, citoyenneté et sécurité sociale.",
     ["Élections sociales", "Syndicats", "Monde associatif", "Sécurité sociale"]),
    ("istasse", "Cédric Istasse", "Rédacteur en chef du <em>Courrier hebdomadaire</em>",
     "Gardien des conventions éditoriales — celles qui interdisent l'illustration et imposent l'appellation constitutionnelle « Communauté française ». Ses propres travaux portent sur les questions linguistiques, l'architecture institutionnelle, l'abolition annoncée du Sénat, l'histoire des euphémismes politiques, la Communauté germanophone, et l'analyse électorale menée commune par commune, à l'échelle de la Wallonie entière.",
     ["Réformes de l'État", "Sénat", "Ostbelgien", "Élections locales"]),
    ("biard", "Benjamin Biard", "Chercheur · secteur socio-politique",
     "Spécialiste de l'extrême droite et des idéologies. Il documente l'exception belge : un Vlaams Belang massif au nord, un échec structurel au sud — le cas <em>Chez Nous</em> —, et un cordon sanitaire dont il mesure patiemment l'usure. Également auteur de l'ouverture de la « boîte noire » des services d'études des partis francophones.",
     ["Extrême droite", "Cordon sanitaire", "Services d'études", "Partis frères"]),
    ("sagesser", "Caroline Sägesser", "Chercheuse · secteur socio-politique",
     "Historienne. Relations Église-État et régime des cultes, laïcité face à une société plurielle, cours philosophiques dans l'enseignement officiel, fonctionnement du fédéralisme en situation de crise, stratégies électorales néerlandophones à Bruxelles. Autrice de l'autopsie des 239 jours de la formation De Wever.",
     ["Laïcité", "Cultes", "Formation gouvernementale", "Bruxelles néerlandophone"]),
    ("lefebve", "Vincent Lefebve", "Chercheur · secteur socio-politique",
     "Juriste et philosophe. Il suit un déplacement de fond : le pouvoir démocratique glisse des parlements vers les prétoires. Réformes de la justice et État de droit, usages politiques du droit par les mouvements sociaux — la <em>Klimaatzaak</em> en est le cas d'école —, évolution du système pénal, représentations de la justice dans la culture de masse.",
     ["État de droit", "Judiciarisation", "Système pénal", "Klimaatzaak"]),
    ("nassaux", "Jean-Paul Nassaux", "Collaborateur scientifique · socio-politique",
     "La mémoire bruxelloise du centre. Institutions de la Région capitale, relations communautaires, trajectoire déclinante de DéFI, et surtout le dossier de la fusion des six zones de police pour dix-neuf communes — un cas d'école de la vulnérabilité institutionnelle bruxelloise face au fédéral.",
     ["Institutions bruxelloises", "Zones de police", "Relations communautaires"]),
    ("vdabbeel", "David Van Den Abbeel", "Coordinateur · secteur Économie",
     "Il pilote la cartographie du pouvoir économique : actionnariat public, puissance des intercommunales, acteurs de l'informatique électorale, investissements étrangers, dépendances macroéconomiques. Le postulat qu'il opérationnalise : on n'analyse pas valablement une politique publique sans connaître qui détient le capital.",
     ["Actionnariat", "Intercommunales", "Vote automatisé", "Capitaux étrangers"]),
    ("collard", "Fabienne Collard", "Chercheuse · secteur Économie",
     "Économiste de la transition. Éolien offshore et zone Princesse Élisabeth, parcs photovoltaïques, certificats verts, loi sur la sortie du nucléaire et prolongation de Doel et Tihange, électrification de l'industrie automobile, économie du cinéma, agences de notation.",
     ["Transition énergétique", "Nucléaire", "Éolien offshore", "Industrie culturelle"]),
]

COLLECTIONS = [
    ("ch", "Courrier hebdomadaire", "1959 →", "2 600+ numéros · 40 par an",
     "La clé de voûte. Chaque livraison est une monographie sur un objet circonscrit, relue par des pairs bénévoles choisis selon la thématique. Le cahier des charges est d'une sévérité rare : introduction générale, chapitres numérotés, conclusion générale, et <strong>interdiction formelle de l'iconographie et des encadrés</strong>. Toute information pertinente doit être intégrée au corps du texte ou aux notes infrapaginales. Seuls tolérés : tableaux, graphiques, schémas et cartes. Depuis 2018, les versions numériques passent en accès libre un an après parution.",
     "https://www.crisp.be/fr/20-catalogue/s-1/filtrer_par_collection-courrier_hebdomadaire"),
    ("dossiers", "Les Dossiers du CRISP", "1969 →", "une centaine de titres",
     "Le pendant pédagogique. Pagination réduite, langue clarifiée, résumés marginaux, encadrés et glossaires : tout ce que le <em>Courrier hebdomadaire</em> s'interdit, les <em>Dossiers</em> se l'autorisent, parce que le public visé n'est pas le même — enseignants, étudiants, formateurs syndicaux.",
     "https://www.crisp.be/fr/3-ressources"),
    ("livres", "Les Livres", "1960 →", "ouvrages de référence",
     "Ouvrages volumineux portant les thèses majeures du centre, dans la tradition inaugurée par les travaux congolais de 1960. Fédéralisme financier comparé, règles de l'Organisation mondiale du commerce, histoire politique de la Belgique.",
     "https://www.crisp.be/fr/3-ressources"),
    ("analyses", "Les @nalyses en ligne", "2011 →", "~20 articles par an · accès libre",
     "Le canal réactif, né du besoin d'intervenir dans l'actualité brûlante sans attendre le calendrier d'une monographie. Format court, gratuit, adossé aux missions d'éducation permanente. C'est là qu'on trouve les décodages les plus rapides : fusion des zones de police, recomposition des partis libéraux, campagne publicitaire clivante.",
     "https://www.crisp.be/fr/14-analyses-en-ligne"),
    ("vocabulaire", "Vocabulaire politique", "en ligne", "~600 notions · accès libre",
     "Abécédaire numérique du pouvoir belge. Chaque entrée propose une définition synthétique immédiate, puis un développement qui replace la notion dans son histoire et son droit. Certaines notices sont enrichies de capsules sonores. Les entrées restent en français sauf usage établi — <em>greenwashing</em>, <em>ombudsman</em> —, le site renvoyant vers la banque terminologique du Service central de traduction allemande pour les correspondances néerlandaises et allemandes.",
     "https://www.vocabulairepolitique.be/"),
    ("actionnariat", "Actionnariat wallon", "1983 →", "100 000+ sociétés",
     "Base de données soutenue par la Région wallonne, en accès libre. Elle couvre les sociétés présentes en Wallonie publiant des comptes annuels et employant au moins un équivalent temps plein, et croise quotidiennement Banque-Carrefour des Entreprises, Centrale des bilans de la BNB, répertoire ONSS et sources privées pour générer des organigrammes qui lèvent le voile sur les cascades de holdings.",
     "https://actionnariatwallon.be/"),
    ("docpol", "Documents politiques", "en ligne", "gouvernements depuis 1944",
     "Archive vivante de l'exécutif belge : composition exacte de tous les gouvernements fédéraux, régionaux et communautaires depuis l'après-guerre, présidents d'assemblée, déclarations gouvernementales, calendrier électoral depuis 1946.",
     "https://www.crisp.be/fr/3-ressources"),
    ("podcasts", "Podcasts &amp; capsules", "en cours", "1 à 2 par mois",
     "Émissions radio, télé et web où les chercheurs présentent une publication ou décryptent un dossier — notamment en partenariat avec La Première et Radio Panik.",
     "https://www.crisp.be/fr/3-ressources"),
    ("ep", "Études d'éducation permanente", "en cours", "outils citoyens",
     "La traduction des recherches en outils d'éducation populaire, dans le cadre du décret du 7 juillet 2003. L'objectif fixé par le législateur : « rapprocher les lieux de décision et les personnes ».",
     "https://www.crisp.be/fr/3-ressources"),
]


def build_pages(ctx):
    u = ctx["u"]
    share = ctx["share"]
    bc = ctx["breadcrumbs"]
    og = ctx["og_image"]
    pubs = ctx["pubs"]
    icons = ctx["icons"]
    NN, NE = len(ctx["nodes"]), len(ctx["edges"])
    P = []

    # ============================================================ ACCUEIL
    highlights = [p for p in pubs if p.get("highlight")][:4]
    hl_html = "".join(
        f"""<a class="card card-accent reveal" href="{u('publications/')}#{p['id']}">
        <p class="eyebrow">{'Courrier hebdomadaire n° ' + str(p['num']) if p['collection'] == 'ch' else ('@nalyse en ligne' if p['collection'] == 'analyses' else 'Livre')} · {p['year']}</p>
        <h3>{escape(p['title'])}</h3>
        <p>{escape(p['abstract'][:180])}…</p></a>"""
        for p in highlights
    )

    doss_cards = "".join(
        f"""<a class="card reveal" href="{u('dossiers/' + d['slug'] + '/')}">
        <p class="eyebrow">{d['kicker']}</p><h3>{d['title']}</h3><p>{d['teaser']}</p></a>"""
        for d in DOSSIERS.DOSSIERS[:6]
    )

    home_body = f"""
<section class="hero">
  <canvas id="hero-canvas" aria-hidden="true"></canvas>
  <div class="wrap hero-inner">
    {eyebrow('Fan club non officiel · depuis 1958, ils décortiquent la Belgique')}
    <h1>Cartographier le <span class="hl">pouvoir</span> en Belgique</h1>
    <p class="lede">Le CRISP étudie la décision politique là où elle se prend réellement — pas seulement au parlement, mais dans les conseils d'administration, les états-majors de partis et les assemblées syndicales. Ce site est un hommage documentaire&nbsp;: une encyclopédie visuelle de son histoire, de ses chercheurs, de ses collections et des dossiers qu'il ouvre.</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="{u('graphe/')}">{icons['share']} Explorer le graphe</a>
      <a class="btn" href="{u('dossiers/')}">Les grands dossiers</a>
      <a class="btn btn-ghost" href="https://www.crisp.be/fr/" target="_blank" rel="noopener">Le site officiel ↗</a>
    </div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="stats reveal">
      {stat(None, "années d'indépendance", count=68, suf=" ans")}
      {stat("2 600+", "numéros du Courrier hebdomadaire")}
      {stat(None, "notions au Vocabulaire politique", count=600, pre="~")}
      {stat("100 000+", "sociétés dans l'Actionnariat wallon")}
      {stat(None, "chercheurs permanents", count=9)}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    {eyebrow('Pourquoi ce site')}
    <div class="grid grid-2" style="align-items:start;gap:3rem">
      <div class="prose">
        <h2 class="mt-0">Une anomalie salutaire</h2>
        <p>Dans un paysage saturé de think tanks qui produisent des argumentaires sur commande, le CRISP tient un cap d'une austérité redoutable&nbsp;: pas d'illustration dans ses monographies, pas de concession au vocabulaire de la communication politique, un scrupule sémantique poussé jusqu'à refuser l'appellation «&nbsp;Fédération Wallonie-Bruxelles&nbsp;» faute de révision constitutionnelle.</p>
        <p>Ce n'est pas du conservatisme. C'est une position méthodologique&nbsp;: préserver un espace où la complexité du fédéralisme belge asymétrique peut être pensée sans être aussitôt traduite en éléments de langage.</p>
        <p>Ce fan club existe parce qu'une institution qui fournit depuis soixante-huit ans l'infrastructure cognitive du débat démocratique belge mérite mieux qu'une page Wikipédia. Il n'appartient pas au CRISP, ne le représente pas, et renvoie systématiquement à ses sources.</p>
      </div>
      <div class="stack">
        <div class="callout">
          {eyebrow('Le postulat fondateur')}
          <p>Le pouvoir ne réside jamais uniquement là où la Constitution l'indique. Il se niche dans les conseils d'administration des holdings, les assemblées générales de syndicats, les accords de partis — et, de plus en plus, dans l'architecture algorithmique des réseaux sociaux.</p>
        </div>
        <div class="card">
          <h3>Trois portes d'entrée</h3>
          <ul class="stack" style="list-style:none;padding:0;margin:.8rem 0 0">
            <li><a href="{u('graphe/')}"><strong>Le graphe</strong></a> — {NN} nœuds, les relations entre personnes, concepts, publications, partis et institutions.</li>
            <li><a href="{u('glossaire/')}"><strong>Le glossaire</strong></a> — {len(ctx['glossary'])} notions pour décoder la particratie, la sonnette d'alarme ou l'apparentement.</li>
            <li><a href="{u('chronologie/')}"><strong>La chronologie</strong></a> — de la fondation de 1958 au n° 2690 du <em>Courrier hebdomadaire</em>.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    {eyebrow('Le graphe de connaissances')}
    <h2>Tout est relié — et on peut le voir</h2>
    <p class="lede" style="margin-bottom:2rem">Chercheurs, collections, notions, partis, événements et publications forment un réseau. Cliquez un nœud pour dérouler ses relations, filtrez par type, cherchez un nom&nbsp;: la structure du savoir socio-politique belge se déplie sous la souris.</p>
    <a class="btn btn-primary" href="{u('graphe/')}">Ouvrir le graphe interactif →</a>
  </div>
</section>

<section>
  <div class="wrap">
    {eyebrow('Chantiers en cours · 2025-2026')}
    <h2>Ce que le CRISP publie en ce moment</h2>
    <div class="grid grid-2" style="margin-top:2rem">{hl_html}</div>
    <p style="margin-top:2rem"><a class="btn" href="{u('publications/')}">Toutes les publications récentes →</a></p>
  </div>
</section>

<section>
  <div class="wrap">
    {eyebrow('Dossiers')}
    <h2>Comprendre la Belgique de 2026</h2>
    <div class="grid grid-3" style="margin-top:2rem">{doss_cards}</div>
    <p style="margin-top:2rem"><a class="btn" href="{u('dossiers/')}">Les {len(DOSSIERS.DOSSIERS)} dossiers →</a></p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="card" style="padding:2.5rem">
      {eyebrow('Aller à la source')}
      <h2 style="margin-bottom:1rem">Ce site ne remplace rien</h2>
      <p class="muted" style="max-width:62ch">Chaque affirmation ici renvoie à une publication du CRISP ou à une source primaire. Les analyses, elles, se lisent chez leur éditeur. Abonnez-vous au <em>Courrier hebdomadaire</em>, fouillez le <em>Vocabulaire politique</em>, interrogez la base <em>Actionnariat wallon</em>&nbsp;: c'est gratuit pour l'essentiel, et c'est là que tout se trouve.</p>
      <div class="pill-row" style="margin-top:1.5rem">
        <a class="btn btn-primary" href="https://www.crisp.be/fr/" target="_blank" rel="noopener">crisp.be ↗</a>
        <a class="btn" href="https://www.vocabulairepolitique.be/" target="_blank" rel="noopener">vocabulairepolitique.be ↗</a>
        <a class="btn" href="https://actionnariatwallon.be/" target="_blank" rel="noopener">actionnariatwallon.be ↗</a>
      </div>
      {share('', 'CRISP — fan club non officiel')}
    </div>
  </div>
</section>
"""
    P.append(dict(
        slug="", title="CRISP — fan club non officiel · Cartographier le pouvoir",
        desc="Encyclopédie visuelle du CRISP : graphe de connaissances, histoire depuis 1958, chercheurs, collections et dossiers de la politique belge. Site hommage indépendant.", body=home_body, pin=True,
        og=og("", "Fan club non officiel", "Cartographier le pouvoir en Belgique", "og-default"),
        scripts=("assets/js/graph.js",),
    ))

    # ============================================================ GRAPHE
    graph_body = f"""
<section style="padding-bottom:1.5rem">
  <div class="wrap">
    {bc([("", "Accueil"), ("graphe/", "Graphe")])}
    {eyebrow(f'Obsidian-like · {NN} nœuds, {NE} liens')}
    <h1 style="margin-bottom:1rem">Le graphe de connaissances</h1>
    <p class="lede">Une carte navigable de l'écosystème CRISP. <strong>Cliquez</strong> un nœud pour ouvrir sa fiche et la liste de ses relations, <strong>double-cliquez</strong> pour le centrer, <strong>faites glisser</strong> pour déplacer la vue ou un nœud, <strong>molette</strong> pour zoomer. Les filtres de couleur masquent des familles entières.</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="graph-shell" style="height:min(78vh,760px)">
      <canvas id="graph-canvas"></canvas>
      <div class="graph-toolbar">
        <div class="graph-search">{icons['search']}<input id="graph-q" type="search" placeholder="Filtrer les nœuds…" aria-label="Filtrer les nœuds du graphe"></div>
        <div class="legend" id="graph-legend"></div>
      </div>
      <div class="graph-zoom">
        <button class="icon-btn" id="zoom-in" aria-label="Zoomer">{icons['plus']}</button>
        <button class="icon-btn" id="zoom-out" aria-label="Dézoomer">{icons['minus']}</button>
        <button class="icon-btn" id="zoom-reset" aria-label="Recentrer">{icons['target']}</button>
      </div>
      <aside class="node-panel" id="node-panel" aria-live="polite"></aside>
    </div>
    <p class="muted" style="margin-top:1rem;font-size:var(--step--1)">Le graphe est calculé dans votre navigateur par une simulation de forces écrite pour ce site — aucune bibliothèque externe, aucune donnée envoyée nulle part. Les relations sont établies à partir des publications et documents cités en <a href="{u('a-propos/')}">« méthode &amp; sources »</a>.</p>
    {share('graphe/', 'Le graphe de connaissances du CRISP')}
  </div>
</section>
"""
    P.append(dict(
        slug="graphe/", title="Graphe de connaissances du CRISP",
        desc=f"Carte interactive de l'écosystème CRISP : {NN} nœuds et {NE} liens entre chercheurs, collections, notions, partis et publications. Graphe façon Obsidian.",
        body=graph_body, pin=True, scripts=("assets/js/graph.js",),
        og=og("graphe/", "Graphe interactif", f"{NN} nœuds, {NE} liens : l'écosystème CRISP", "og-graphe"),
    ))

    # ============================================================ HISTOIRE
    hist_body = f"""
<section>
  <div class="wrap-narrow">
    {bc([("", "Accueil"), ("histoire/", "Histoire")])}
    {eyebrow('1958-1961 · genèse')}
    <h1>Naître d'un manque</h1>
    <div class="prose">
      <p>À la fin des années 1950, la Belgique clôt un cycle. Le <strong>Pacte scolaire</strong> de 1958 pacifie la Guerre des écoles et referme, pour l'essentiel, le clivage philosophique entre catholiques et laïques. Ce qu'il libère, ce sont les autres fractures&nbsp;: linguistiques, communautaires, socio-économiques. Il faut de nouveaux cadres pour les penser.</p>

      <h2>Un journaliste qui trouve que la presse ne suffit plus</h2>
      <p><strong>Jules Gérard-Libois</strong> (1923-2005) est né à Ougrée, dans le bassin industriel liégeois, fils d'un ouvrier métallurgiste licencié pour faits de grève. Sa conscience politique s'est forgée dans la Résistance. Docteur en droit et candidat en philologie germanique de l'Université de Liège, il passe brièvement par l'Union démocratique belge — cette formation progressiste et pluraliste de l'immédiat après-guerre — avant de choisir le journalisme.</p>
      <p>À vingt-cinq ans, il lance l'édition belge de <em>Témoignage chrétien</em>, qu'il dirige de 1948 à 1958 avec son épouse Andrée. Il entre à <em>La Cité</em> en 1950, correspond pour <em>Combat</em> et <em>La Croix</em>. Marqué par le personnalisme d'Emmanuel Mounier, il participe à la création des groupes «&nbsp;Esprit&nbsp;» en Belgique aux côtés du philosophe <strong>Jean Ladrière</strong> et du constitutionnaliste <strong>François Perin</strong>.</p>
      <p>Le constat qui déclenche tout est celui d'une insuffisance structurelle&nbsp;: la presse quotidienne, par nature, ne peut pas rendre compte de la complexité croissante de la décision politique. Fin 1958, avec Ladrière, Perin et le syndicaliste <strong>Hubert Dewez</strong> — devenu historien du mouvement ouvrier sous le nom de Jean Neuville —, il fonde une structure à la lisière du journalisme de fond et de la recherche académique.</p>

      <blockquote>
        <p>Pallier le manque d'outils d'analyse rigoureux et indépendants sur les réalités sociopolitiques belges.</p>
        <cite>La mission de départ, en une phrase</cite>
      </blockquote>

      <h2>Juillet 1960 : l'arrivée de Xavier Mabille</h2>
      <p>L'architecture intellectuelle se consolide avec <strong>Xavier Mabille</strong> (1933-2012). Issu d'un milieu modeste, autodidacte assumé — il n'a jamais achevé d'études supérieures formelles —, il commence comme employé de banque. Au CRISP, il gravira tous les échelons&nbsp;: rédacteur en chef du <em>Courrier hebdomadaire</em>, directeur général, président. Un demi-siècle d'incarnation de l'institution, et une <em>Histoire politique de la Belgique&nbsp;: facteurs et acteurs de changement</em> rééditée à de multiples reprises, devenue la référence de l'histoire institutionnelle du pays.</p>

      <h2>Le baptême du feu : Congo, 1960</h2>
      <p>La crédibilité du centre se forge en quelques mois. Face à l'indépendance chaotique du Congo, le CRISP publie une série de travaux fondateurs — <em>Congo 1960</em> en tête — qui marqueront l'historiographie africaine contemporaine.</p>
      <p>Ce qui devient là une marque de fabrique&nbsp;: l'investigation des réseaux d'influence informels. En documentant le <strong>Collège des commissaires généraux</strong> mis en place en 1960-1961 contre Patrice Lumumba, et en identifiant le fameux <strong>Groupe de Binza</strong>, les chercheurs théorisent la notion de <strong>pouvoir occulte</strong>. Ils reconstituent le profil sociologique des acteurs, leur formation — les diplômés de l'Université Lovanium —, et la manière dont intérêts miniers, conseillers militaires et structures coloniales ont orchestré les transitions.</p>
      <div class="callout">
        {eyebrow('Ce que le Congo a appris au CRISP')}
        <p>Le lieu formel de la décision et son lieu réel ne coïncident pas nécessairement. Cette leçon devient une méthode&nbsp;: suivre les acteurs plutôt que les organigrammes. Elle vaudra ensuite pour les holdings belges comme pour les états-majors de partis.</p>
      </div>
      <p>Gérard-Libois prolongera cette trajectoire africaniste en cofondant le Centre d'étude et de documentation africaines (CEDAF)&nbsp;; la documentation africaine du CRISP rejoindra le Musée royal de l'Afrique centrale à Tervuren en 1972.</p>

      <h2>L'hiver 1960-1961 : la morphologie d'un conflit</h2>
      <p>Le second moment fondateur se joue sur le territoire national. La grève générale contre la «&nbsp;Loi unique&nbsp;» du gouvernement Eyskens paralyse le pays et exacerbe les tensions entre Flandre et Wallonie. Le CRISP s'en empare non comme d'un fait social mais comme d'un révélateur systémique.</p>
      <p>Dans <em>Le choc de l'hiver '60-'61</em>, l'historien Jean Neuville et le syndicaliste Jacques Yerna disséquent la dynamique du mouvement&nbsp;: la fracture au sommet de la FGTB lors du vote crucial du 16 décembre 1960, le repli stratégique sur le bassin industriel wallon sous l'impulsion d'André Renard, et la mutation d'une revendication socio-économique en exigence politique de fédéralisme avec la création du Mouvement populaire wallon.</p>
      <p>En documentant les débats internes entre Fernand Demany, Robert Dussart, Ernest Davister ou Gustave Dache, le centre établit un principe qui ne le quittera plus&nbsp;: <strong>l'histoire politique belge ne s'écrit pas sans une connaissance intime des forces syndicales</strong>.</p>

      <h2>Ce qui en découle</h2>
      <p>Deux crises, deux méthodes, une doctrine. Du Congo vient l'attention aux structures parallèles et aux intérêts économiques&nbsp;; de l'hiver 61 vient l'attention aux organisations de masse et aux dynamiques régionales. Ensemble, elles définissent un objet — la décision politique saisie dans ses soubassements — et un refus&nbsp;: celui de réduire la science politique à l'exégèse des textes législatifs.</p>
    </div>
    <p style="margin-top:2rem"><a class="btn" href="{u('chronologie/')}">Voir la chronologie complète →</a> <a class="btn btn-ghost" href="{u('equipe/')}">L'équipe aujourd'hui →</a></p>
    {share('histoire/', 'Aux origines du CRISP (1958-1961)')}
  </div>
</section>
"""
    P.append(dict(
        slug="histoire/", title="Aux origines du CRISP (1958-1961)",
        desc="Gérard-Libois, Mabille, la crise congolaise de 1960 et la grève de l'hiver 60-61 : les deux crises qui ont donné au CRISP sa méthode et son objet.",
        body=hist_body, pin=True,
        og=og("histoire/", "1958-1961 · genèse", "Naître d'un manque", "og-histoire"),
        article={"@type": "Article", "headline": "Aux origines du CRISP (1958-1961)",
                 "about": {"@id": "https://www.crisp.be/#organization"},
                 "inLanguage": "fr-BE"},
    ))

    # ============================================================ ÉQUIPE
    team_html = ""
    for pid, name, role, bio, tags in TEAM:
        initials = "".join(w[0] for w in name.replace("de ", "").split()[:2]).upper()
        chips = "".join(f'<span class="chip">{t}</span>' for t in tags)
        team_html += f"""
<article class="card person-card reveal" id="{pid}">
  <div class="avatar" aria-hidden="true">{initials}</div>
  <div>
    <p class="role">{role}</p>
    <h3>{name}</h3>
    <p>{bio}</p>
    <div class="pill-row" style="margin-top:.8rem">{chips}</div>
  </div>
</article>"""

    equipe_body = f"""
<section>
  <div class="wrap">
    {bc([("", "Accueil"), ("equipe/", "Équipe")])}
    {eyebrow("Neuf chercheurs pour couvrir un pays entier")}
    <h1>L'équipe</h1>
    <p class="lede" style="margin-bottom:2.5rem">Une structure numériquement modeste — une quinzaine d'équivalents temps plein pour l'ensemble du centre —, mais une division du travail conçue pour couvrir l'intégralité du spectre&nbsp;: institutions, partis, syndicats, cultes, justice, énergie, capital. À cela s'ajoutent documentalistes, secrétariat d'édition et équipe administrative, sans lesquels rien ne paraîtrait.</p>
    <div class="grid" style="gap:1rem">{team_html}</div>
    <div class="callout" style="margin-top:2.5rem">
      {eyebrow('Le garde-fou')}
      <p>Le conseil d'administration réunit des personnalités de familles philosophiques et d'universités différentes — Els Witte, Guy Vanthemsche, Hugues Dumont, Anne Heldenbergh, Pascale Vielle, Eric Geerkens, Michel Molitor, Robert Tollet, Pierre Reman, Nadine Gouzée, Serge Govaert… Cette hétérogénéité n'est pas décorative&nbsp;: chaque travail de l'équipe permanente est relu par des pairs bénévoles choisis selon la thématique traitée.</p>
    </div>
    <p class="muted" style="margin-top:1.5rem;font-size:var(--step--1)">Composition vérifiée sur <a href="https://www.crisp.be/fr/1-nous-contacter" target="_blank" rel="noopener">crisp.be</a>. Les descriptions de domaines s'appuient sur les fiches individuelles publiées par le centre et sur les publications signées.</p>
    {share('equipe/', "L'équipe du CRISP")}
  </div>
</section>
"""
    P.append(dict(
        slug="equipe/", title="L'équipe du CRISP — qui fait quoi",
        desc="De Coorebyter, Faniel, Blaise, Istasse, Biard, Sägesser, Lefebve, Nassaux, Van Den Abbeel, Collard : les chercheurs du CRISP et leurs domaines.",
        body=equipe_body, pin=True,
        og=og("equipe/", "Qui fait quoi", "Neuf chercheurs, un pays entier", "og-equipe"),
    ))

    # ============================================================ COLLECTIONS
    coll_html = ""
    for cid, name, period, meta, desc, link in COLLECTIONS:
        coll_html += f"""
<article class="card reveal" id="{cid}">
  <p class="eyebrow">{period} · {meta}</p>
  <h3>{name}</h3>
  <p>{desc}</p>
  <p style="margin-top:1rem"><a href="{link}" target="_blank" rel="noopener">Consulter ↗</a></p>
</article>"""

    coll_body = f"""
<section>
  <div class="wrap">
    {bc([("", "Accueil"), ("collections/", "Collections")])}
    {eyebrow("Une cathédrale éditoriale")}
    <h1>Les collections</h1>
    <p class="lede" style="margin-bottom:2.5rem">La segmentation de l'offre n'est pas un accident&nbsp;: elle répond à une nécessité stratégique — adapter la granularité de l'information à des publics qui n'ont ni le même temps, ni les mêmes prérequis, ni les mêmes usages.</p>
    <div class="grid grid-2">{coll_html}</div>

    <h2 style="margin-top:4rem">Le cahier des charges du <em>Courrier hebdomadaire</em></h2>
    <p class="lede">Ce qui rend cette collection singulière tient autant à ce qu'elle s'interdit qu'à ce qu'elle publie.</p>
    <div class="table-scroll">
      <table>
        <caption class="visually-hidden">Conventions éditoriales du Courrier hebdomadaire</caption>
        <thead><tr><th>Règle</th><th>Contenu</th><th>Raison</th></tr></thead>
        <tbody>
          <tr><td>Structure</td><td>Introduction générale, chapitres titrés et numérotés séquentiellement, conclusion générale</td><td>Standard international de la publication scientifique</td></tr>
          <tr><td>Iconographie</td><td><strong>Interdite</strong> — pas de photographies, pas d'illustrations</td><td>Refus du morcellement de la lecture propre au style journalistique</td></tr>
          <tr><td>Encadrés</td><td><strong>Interdits</strong> — l'information pertinente va dans le corps du texte ou dans les notes</td><td>Préserver l'intégrité du raisonnement</td></tr>
          <tr><td>Éléments tolérés</td><td>Tableaux, graphiques, schémas, cartes haute résolution</td><td>Ils portent de la donnée, pas de l'ornement</td></tr>
          <tr><td>Terminologie</td><td>« Communauté française », jamais « Fédération Wallonie-Bruxelles »</td><td>Appellation constitutionnelle&nbsp;: le nom d'usage de 2011 n'a pas été suivi d'une révision</td></tr>
          <tr><td>Relecture</td><td>Panel de pairs bénévoles choisis selon la thématique</td><td>Contrôle scientifique indépendant de l'équipe permanente</td></tr>
        </tbody>
      </table>
    </div>
    <p class="muted" style="font-size:var(--step--1)">D'après les <a href="https://www.crisp.be/CRISP_CH_Principales_conventions_editoriales-version_mai_2022.pdf" target="_blank" rel="noopener">principales conventions éditoriales</a> publiées par le CRISP.</p>
    {share('collections/', 'Les collections du CRISP')}
  </div>
</section>
"""
    P.append(dict(
        slug="collections/", title="Les collections éditoriales du CRISP",
        desc="Courrier hebdomadaire, Dossiers, @nalyses, Vocabulaire politique, Actionnariat wallon : l'architecture éditoriale du CRISP et ses conventions de rigueur.",
        body=coll_body,
        og=og("collections/", "Architecture éditoriale", "Une cathédrale de publications", "og-collections"),
    ))

    # ============================================================ PUBLICATIONS
    THEMES = {
        "elections": "Élections", "partis": "Partis", "particratie": "Particratie",
        "federalisme": "Fédéralisme", "institutions": "Institutions", "gouvernement": "Gouvernement",
        "concertation-sociale": "Concertation sociale", "economie": "Économie",
        "actionnariat": "Actionnariat", "budget": "Budget", "social": "Social",
        "medias": "Médias", "identite": "Identité", "extreme-droite": "Extrême droite",
        "bruxelles": "Bruxelles", "democratie": "Démocratie", "local": "Local",
    }
    used = sorted({t for p in pubs for t in p.get("themes", [])})
    filters = '<button class="chip chip-btn" data-pub-filter="*" aria-pressed="true">Tout</button>' + "".join(
        f'<button class="chip chip-btn" data-pub-filter="{t}" aria-pressed="false">{THEMES.get(t, t)}</button>'
        for t in used
    )
    COLL_LABEL = {"ch": "Courrier hebdomadaire", "analyses": "@nalyse en ligne", "livres": "Livre"}
    rows = ""
    def _numkey(x):
        m = re.search(r"\d+", str(x["num"]))
        return -int(m.group()) if m else 0
    for p in sorted(pubs, key=lambda x: (-x["year"], _numkey(x))):
        tags = "".join(f'<span class="chip">{THEMES.get(t, t)}</span>' for t in p.get("themes", []))
        pg = f" · {p['pages']} p." if p.get("pages") else ""
        rows += f"""
<li class="pub" id="{p['id']}" data-themes="{' '.join(p.get('themes', []))}">
  <div class="pub-meta"><b>{COLL_LABEL.get(p['collection'], p['collection'])}</b>n° {p['num']}<br>{p['year']}{pg}</div>
  <div>
    <h3><a href="{p['url']}" target="_blank" rel="noopener">{escape(p['title'])}</a></h3>
    <p class="authors">{escape(', '.join(p['authors']))}</p>
    <p class="abstract">{escape(p.get('abstract', ''))}</p>
    <div class="tags">{tags}</div>
  </div>
</li>"""

    pub_ld = [{
        "@type": "ItemList", "name": "Publications récentes du CRISP",
        "numberOfItems": len(pubs),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "ScholarlyArticle", "name": p["title"],
                      "datePublished": str(p["year"]), "url": p["url"],
                      "author": [{"@type": "Person", "name": a} for a in p["authors"]],
                      "isPartOf": {"@type": "Periodical", "name": COLL_LABEL.get(p["collection"], "CRISP")},
                      "publisher": {"@id": "https://www.crisp.be/#organization"}}}
            for i, p in enumerate(pubs)
        ],
    }]

    pub_body = f"""
<section>
  <div class="wrap">
    {bc([("", "Accueil"), ("publications/", "Publications")])}
    {eyebrow("Sélection · 2022-2026")}
    <h1>Publications récentes</h1>
    <p class="lede">Une sélection de <span id="pub-count">{len(pubs)}</span> parutions représentatives des chantiers en cours. Le catalogue complet — plus de 2 600 numéros du seul <em>Courrier hebdomadaire</em> — se consulte sur <a href="https://www.crisp.be/fr/20-catalogue" target="_blank" rel="noopener">crisp.be</a> et sur <a href="https://shs.cairn.info/revue-courrier-hebdomadaire-du-crisp?lang=fr" target="_blank" rel="noopener">Cairn</a>.</p>
    <div class="pill-row" style="margin:2rem 0 1rem">{filters}</div>
    <ul class="pub-list">{rows}</ul>
    <div class="callout" style="margin-top:2.5rem">
      {eyebrow("Accès libre")}
      <p>Depuis 2018, les versions numériques du <em>Courrier hebdomadaire</em> sont mises à disposition gratuitement <strong>un an après leur parution</strong>. Les <em>@nalyses en ligne</em>, le <em>Vocabulaire politique</em>, les <em>Documents politiques</em> et la base <em>Actionnariat wallon</em> sont en accès libre immédiat.</p>
    </div>
    {share('publications/', 'Les publications récentes du CRISP')}
  </div>
</section>
"""
    P.append(dict(
        slug="publications/", title="Publications récentes du CRISP",
        desc="Courrier hebdomadaire n° 2621 à 2690 et @nalyses 2025-2026 : conflits d'intérêts, services d'études, pensions, budget de crise, volatilité électorale.",
        body=pub_body, ld=pub_ld, pin=True,
        og=og("publications/", "2022-2026", "Ce que le CRISP publie en ce moment", "og-publications"),
    ))

    # ============================================================ CHRONOLOGIE
    tl = ""
    for it in ctx["timeline"]:
        tl += f"""
<li class="tl-item reveal" data-cat="{it['cat']}">
  <div class="tl-year">{it['year']}</div>
  <div class="tl-body"><h3>{it['title']}</h3><p>{it['text']}</p></div>
</li>"""
    chrono_body = f"""
<section>
  <div class="wrap">
    {bc([("", "Accueil"), ("chronologie/", "Chronologie")])}
    {eyebrow("1958 → 2026")}
    <h1>Chronologie</h1>
    <p class="lede" style="margin-bottom:3rem">Les jalons du centre et ceux du pays, entremêlés — parce que l'un ne se comprend pas sans l'autre.</p>
    <div class="pill-row" style="margin-bottom:2.5rem">
      <span class="chip"><span class="dot" style="background:var(--gold)"></span>Institution</span>
      <span class="chip"><span class="dot" style="background:var(--violet)"></span>Édition</span>
      <span class="chip"><span class="dot" style="background:var(--teal)"></span>Recherche</span>
      <span class="chip"><span class="dot" style="background:var(--red)"></span>Belgique</span>
    </div>
    <ul class="timeline">{tl}</ul>
    {share('chronologie/', 'Chronologie du CRISP, 1958-2026')}
  </div>
</section>
"""
    P.append(dict(
        slug="chronologie/", title="Chronologie du CRISP, 1958-2026",
        desc="De la fondation en 1958 au n° 2690 du Courrier hebdomadaire : les jalons du CRISP et ceux de la Belgique, du Congo 1960 à la coalition Arizona.",
        body=chrono_body,
        og=og("chronologie/", "1958 → 2026", "Soixante-huit ans en trente jalons", "og-chrono"),
    ))

    # ============================================================ GLOSSAIRE
    gl = ctx["glossary"]
    cats = sorted({g["cat"] for g in gl})
    gfilters = '<button class="chip chip-btn" data-gloss-cat="*" aria-pressed="true">Tout</button>' + "".join(
        f'<button class="chip chip-btn" data-gloss-cat="{c}" aria-pressed="false">{c}</button>' for c in cats
    )
    gitems = "".join(
        f"""<article class="gloss-item" id="{g['id']}" data-cat="{g['cat']}">
        <span class="cat">{g['cat']}</span><h3>{g['term']}</h3><p>{g['def']}</p></article>"""
        for g in sorted(gl, key=lambda x: x["term"].lower())
    )
    gloss_ld = [{
        "@type": "DefinedTermSet", "name": "Glossaire du pouvoir belge",
        "description": "Notions clés pour lire la vie politique belge.",
        "hasDefinedTerm": [
            {"@type": "DefinedTerm", "name": g["term"],
             "description": re.sub(r"<[^>]+>", "", g["def"]),
             "inDefinedTermSet": ctx["full"]("glossaire/")}
            for g in gl
        ],
    }]
    gloss_body = f"""
<section>
  <div class="wrap">
    {bc([("", "Accueil"), ("glossaire/", "Glossaire")])}
    {eyebrow(f"{len(gl)} notions pour décoder un pays")}
    <h1>Glossaire du pouvoir belge</h1>
    <p class="lede">Six réformes de l'État ont engendré un jargon d'une redoutable opacité. Voici de quoi entrer dans une conversation politique belge sans hocher la tête au hasard. Pour la version canonique, exhaustive et sourcée&nbsp;: le <a href="https://www.vocabulairepolitique.be/" target="_blank" rel="noopener">Vocabulaire politique</a> du CRISP, près de 600 notions, certaines avec capsules sonores.</p>
    <div class="gloss-controls" style="margin-top:2rem">
      <div class="graph-search" style="border-radius:10px">{icons['search']}<input id="gloss-q" type="search" placeholder="Chercher une notion…" aria-label="Chercher une notion"></div>
      {gfilters}
    </div>
    <p class="muted" style="font-size:var(--step--2);font-family:var(--font-mono)"><span id="gloss-count">{len(gl)}</span> notions affichées</p>
    <div class="gloss-list">{gitems}</div>
    <p id="gloss-empty" hidden class="text-center muted" style="padding:3rem">Aucune notion ne correspond.</p>
    {share('glossaire/', 'Glossaire du pouvoir belge')}
  </div>
</section>
"""
    P.append(dict(
        slug="glossaire/", title="Glossaire du pouvoir belge",
        desc=f"Particratie, cordon sanitaire, majorité spéciale, sonnette d'alarme, confédéralisme : {len(gl)} notions pour lire la vie politique belge.",
        body=gloss_body, ld=gloss_ld, pin=True,
        og=og("glossaire/", f"{len(gl)} notions", "Décoder le jargon du pouvoir belge", "og-glossaire"),
    ))

    # ============================================================ DOSSIERS
    P.extend(DOSSIERS.build(ctx, eyebrow, section))

    # ============================================================ À PROPOS
    apropos_body = f"""
<section>
  <div class="wrap-narrow">
    {bc([("", "Accueil"), ("a-propos/", "À propos")])}
    {eyebrow("Transparence")}
    <h1>Méthode &amp; sources</h1>
    <div class="prose">
      <div class="callout callout-warn">
        {eyebrow("Avertissement")}
        <p>Ce site est un <strong>hommage indépendant</strong>. Il n'est ni édité, ni relu, ni approuvé par le Centre de recherche et d'information socio-politiques. Il ne reproduit aucune publication du CRISP&nbsp;: il en résume les apports, cite ses sources et renvoie vers elles. Toute erreur qui s'y trouverait est la nôtre, pas celle du centre.</p>
      </div>

      <h2 id="pourquoi">Pourquoi un fan club ?</h2>
      <p>Parce qu'il existe, en Belgique francophone, une institution qui produit depuis 1958 la matière première du débat démocratique — et que cette matière reste largement invisible pour qui ne sait pas où chercher. Un moteur de recherche ne montre pas les liens entre un concept, le chercheur qui le travaille, la publication qui l'expose et l'événement qui l'a rendu nécessaire. Un graphe, si.</p>

      <h2 id="methode">Comment ce site a été construit</h2>
      <ul>
        <li><strong>Corpus de départ</strong>&nbsp;: trois notes de synthèse documentaires fournies par le mainteneur, portant sur l'écosystème du CRISP, son histoire institutionnelle et ses publications 2024-2026.</li>
        <li><strong>Vérification</strong>&nbsp;: chaque chiffre, chaque date, chaque composition d'équipe et chaque référence de publication a été recoupé sur les sites officiels — crisp.be, vocabulairepolitique.be, actionnariatwallon.be — et sur les notices de catalogue. Les divergences entre le corpus initial et les sources primaires ont été tranchées en faveur des secondes.</li>
        <li><strong>Le graphe</strong>&nbsp;: les nœuds sont des entités attestées&nbsp;; les arêtes traduisent des relations documentées (auteur d'une publication, membre d'une équipe, subside, filiation conceptuelle). Aucune relation n'a été inventée pour densifier l'image.</li>
        <li><strong>Ce qui reste interprétatif</strong>&nbsp;: les résumés, les mises en perspective et le découpage en dossiers. Ils engagent ce site, pas le CRISP.</li>
      </ul>

      <h2 id="financement">Le financement du CRISP, en clair</h2>
      <p>L'indépendance du centre ne tient pas à un serment mais à une architecture. Les revenus propres — vente d'ouvrages, abonnements institutionnels, prestations — sont complétés par des subventions provenant de la <strong>Fédération Wallonie-Bruxelles</strong> (notamment au titre de l'éducation permanente), de la <strong>Région wallonne</strong> (pour l'actionnariat), de la <strong>Communauté germanophone</strong>, de l'<strong>Autorité fédérale</strong>, du <strong>F.R.S.-FNRS</strong> et de la <strong>Fondation universitaire</strong>.</p>
      <p>La logique est simple&nbsp;: aucun pouvoir subsidiant ne détient à lui seul un droit de vie ou de mort sur l'institution, et chaque financement est conditionné à l'évaluation de la qualité scientifique. C'est le fédéralisme belge retourné en garantie d'autonomie.</p>

      <h2 id="ecosysteme">L'écosystème autour</h2>
      <p>Le CRISP n'est pas seul. Il travaille avec le <a href="https://cevipol.phisoc.ulb.be/" target="_blank" rel="noopener">CEVIPOL</a> de l'ULB — l'étude sur les élus dynastiques en est le produit le plus commenté —, dialogue avec l'ISPOLE de l'UCLouvain, alimente les rédactions francophones et néerlandophones, et sert de source primaire à la recherche historiographique.</p>

      <h2 id="tech">Techniquement</h2>
      <p>HTML, CSS et JavaScript écrits à la main. Aucun framework, aucune bibliothèque, aucun traceur, aucun cookie. La simulation de forces du graphe fait environ 400 lignes. Les pages sont générées par un script Python de la bibliothèque standard&nbsp;; le résultat est du statique pur, servi par GitHub Pages. Le site fonctionne hors ligne après une première visite grâce à un service worker, s'installe comme application, respecte <code>prefers-reduced-motion</code> et <code>prefers-color-scheme</code>, et expose ses données en JSON-LD (schema.org), RSS et sitemap.</p>
      <p><a href="{ctx['conf']['repo']}" target="_blank" rel="noopener">Le code est ouvert ↗</a> — contenu sous licence CC BY-SA 4.0, code sous licence MIT.</p>

      <h2 id="brol">Hébergé chez BROL 2.0</h2>
      <p>Ce fan club fait partie de la constellation d'outils et de modules réunis sur <a href="{ctx['conf']['brol']}" target="_blank" rel="noopener"><strong>BROL 2.0 — dashboard central</strong></a>&nbsp;: dix-neuf modules allant du scanner de fichiers local aux visualisations de graphes, en passant par des intranets fictifs et des univers narratifs. Allez y jeter un œil.</p>

      <h2 id="signature">Signature</h2>
      <p>Conception, recherche documentaire, rédaction, design et code&nbsp;: <strong>Claude</strong>, modèle d'Anthropic, à la demande d'un mainteneur qui préfère rester anonyme. Le prompt tenait en trois lignes&nbsp;; le reste est du travail.</p>

      <h2 id="corriger">Une erreur ?</h2>
      <p>Les faits comptent plus que l'effet. Si quelque chose est inexact, <a href="{ctx['conf']['repo']}/issues" target="_blank" rel="noopener">ouvrez une issue sur GitHub ↗</a> — la correction sera faite.</p>
    </div>
    {share('a-propos/', 'Méthode et sources du fan club CRISP')}
  </div>
</section>
"""
    P.append(dict(
        slug="a-propos/", title="Méthode &amp; sources du fan club CRISP",
        desc="Comment ce site a été construit, ce qu'il doit aux sources officielles, comment le CRISP est financé, et pourquoi ce projet n'engage que lui-même.",
        body=apropos_body,
        og=og("a-propos/", "Transparence", "Méthode, sources et avertissements", "og-apropos"),
    ))

    # ============================================================ 404 & offline
    P.append(dict(
        slug="404.html", title="Page introuvable — fan club CRISP",
        desc="Cette page n'existe pas.",
        body=f"""
<section style="padding-block:6rem">
  <div class="wrap text-center">
    {eyebrow("Erreur 404")}
    <h1 style="max-width:none">Ce nœud n'est relié à rien</h1>
    <p class="lede" style="margin-inline:auto">La page demandée n'existe pas — ou plus. Le graphe, lui, est toujours là.</p>
    <div class="pill-row" style="justify-content:center;margin-top:2rem">
      <a class="btn btn-primary" href="{u('')}">Retour à l'accueil</a>
      <a class="btn" href="{u('graphe/')}">Explorer le graphe</a>
      <a class="btn btn-ghost" href="{u('glossaire/')}">Le glossaire</a>
    </div>
  </div>
</section>""",
    ))
    P.append(dict(
        slug="offline.html", title="Hors ligne — fan club CRISP",
        desc="Vous êtes hors ligne.",
        body=f"""
<section style="padding-block:6rem">
  <div class="wrap text-center">
    {eyebrow("Hors ligne")}
    <h1 style="max-width:none">Pas de réseau</h1>
    <p class="lede" style="margin-inline:auto">Les pages déjà visitées restent consultables. Reconnectez-vous pour le reste.</p>
    <p style="margin-top:2rem"><a class="btn btn-primary" href="{u('')}">Réessayer</a></p>
  </div>
</section>""",
    ))

    return P

