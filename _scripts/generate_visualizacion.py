"""
Genera una visualización HTML autocontenida del corpus del glosario.

Salida: Visualizaciones/corpus.html

Componentes:
1. Timeline scatter — X=año, Y=tradición, color por tradición, tooltip al hover
2. Chord diagram — autores conectados por conceptos compartidos vía refs cruzadas
3. Leyenda interactiva — clic para filtrar por tradición
"""

import html
import json
import re
from collections import defaultdict
from pathlib import Path

# Rutas
GLOSARIO_HTML = Path(
    r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\Memoria Activa del Pensamiento Complejo\Glosario - Pensamiento Complejo.html"
)
VAULT = Path(r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\ObsidianDemo")
DEST = VAULT / "Visualizaciones" / "corpus.html"

# Paleta granate/dorado coincidente con el HTML del glosario
TRADICIONES = {
    "morin":         {"label": "Pensamiento complejo (Morin)",     "color": "#7a2e2e"},
    "autopoiesis":   {"label": "Autopoiesis",                       "color": "#4a6b3c"},
    "cybernetics":   {"label": "Cibernética 2do orden",             "color": "#3c5b6b"},
    "embodied":      {"label": "Cognición encarnada",               "color": "#6b4a3c"},
    "predictive":    {"label": "Mente predictiva",                  "color": "#6b3c5b"},
    "iit":           {"label": "Información integrada (IIT)",       "color": "#5b3c6b"},
    "panpsiquismo":  {"label": "Panpsiquismo",                      "color": "#6b5b3c"},
    "termodinamica": {"label": "Termodinámica del no-equilibrio",   "color": "#b8851f"},
    "proceso":       {"label": "Filosofía del proceso (Whitehead)", "color": "#3c6b5b"},
    "social":        {"label": "Complejidad social",                "color": "#8b6b3a"},
}

# Mapa work → año. Si una obra no está aquí, fallbacks por tradición.
WORK_YEAR = {
    # Morin El Método (volúmenes)
    "El Método I — La naturaleza de la Naturaleza":  1977,
    "El Método II — La vida de la Vida":              1980,
    "El Método III — El conocimiento del Conocimiento": 1986,
    "El Método IV — Las ideas":                       1991,
    "El Método V — La humanidad de la Humanidad":     2001,
    "El Método VI — Ética":                           2004,
    "Introducción al pensamiento complejo":           1990,
    "La cabeza bien puesta":                          1999,
    "Tierra-Patria":                                  1993,
    "Los siete saberes":                              1999,
    # Autopoiesis
    "De máquinas y seres vivos":                      1972,
    "El árbol del conocimiento":                      1984,
    "The Tree of Knowledge":                          1984,
    "Autopoiesis and Cognition":                      1980,
    # Embodied / enactivismo
    "The Embodied Mind":                              1991,
    "Fenomenología de la percepción":                 1945,
    "Phenomenology of Perception":                    1945,
    # Cibernética 2do orden
    "On Constructing a Reality":                      1973,
    "Observing Systems":                              1981,
    # Predictive
    "The Free-Energy Principle":                      2009,
    "Whatever Next: Predictive Brains and Situated Agents": 2013,
    "Surfing Uncertainty":                            2016,
    # IIT
    "An Information Integration Theory of Consciousness": 2004,
    "Phi: A Voyage from the Brain to the Soul":       2012,
    # Panpsiquismo
    "The Routledge Handbook of Panpsychism":          2019,
    "One Self: The Logic of Experience":              1990,
    "Finding Myself Beyond the False Boundaries":     2008,
    # Termodinámica
    "La nueva alianza":                               1979,
    "Order Out of Chaos":                             1984,
    "At Home in the Universe":                        1995,
    "The Origins of Order":                           1993,
    # Proceso
    "Process and Reality":                            1929,
    # Social
    "La revolución contemporánea del saber y la complejidad social": 2006,
}

# Año por defecto cuando no se encuentra el work
TRADICION_FALLBACK_YEAR = {
    "morin": 1990,
    "autopoiesis": 1980,
    "embodied": 1991,
    "cybernetics": 1973,
    "predictive": 2010,
    "iit": 2008,
    "panpsiquismo": 2010,
    "termodinamica": 1985,
    "proceso": 1929,
    "social": 2006,
}


def clean_text(s):
    if s is None:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def extract_data(html_text):
    m = re.search(r"const\s+DATA\s*=\s*(\[.*?\]);", html_text, re.DOTALL)
    if not m:
        raise RuntimeError("No se encontró const DATA en el HTML")
    return json.loads(m.group(1))


def year_for(entry):
    work = clean_text(entry.get("work", ""))
    # Intento directo
    if work in WORK_YEAR:
        return WORK_YEAR[work]
    # Match parcial por substring (para variantes con/sin subtítulo)
    for k, y in WORK_YEAR.items():
        if k in work or work in k:
            return y
    # Caso especial Morin con `volume` numérico
    morin_vols = {1: 1977, 2: 1980, 3: 1986, 4: 1991, 5: 2001, 6: 2004}
    if entry.get("tradition") == "morin" and entry.get("volume") in morin_vols:
        return morin_vols[entry["volume"]]
    # Fallback por tradición
    return TRADICION_FALLBACK_YEAR.get(entry.get("tradition", ""), 1990)


def build_visualization_data(entries):
    """Devuelve un dict con toda la data lista para inyectar en el HTML."""
    # 1) Lista para timeline scatter
    timeline = []
    for e in entries:
        tradicion = e.get("tradition", "otra")
        timeline.append({
            "term": clean_text(e["term"]),
            "slug": e["slug"],
            "year": year_for(e),
            "tradition": tradicion,
            "tradition_label": TRADICIONES.get(tradicion, {}).get("label", tradicion),
            "author": clean_text(e.get("author", "")),
            "work": clean_text(e.get("work", "")),
            "essence": clean_text(e.get("essence", "")),
        })

    # 2) Matriz para chord diagram: autores → autores compartidos por refs
    slug_to_author = {e["slug"]: clean_text(e.get("author", "")) for e in entries}
    slug_to_tradition = {e["slug"]: e.get("tradition", "") for e in entries}
    slug_to_term = {e["slug"]: clean_text(e["term"]) for e in entries}

    authors = sorted({a for a in slug_to_author.values() if a})
    author_idx = {a: i for i, a in enumerate(authors)}

    n = len(authors)
    matrix = [[0] * n for _ in range(n)]

    for e in entries:
        src_author = clean_text(e.get("author", ""))
        if not src_author:
            continue
        for ref_slug in (e.get("ref_slugs") or []):
            tgt_author = slug_to_author.get(ref_slug, "")
            if not tgt_author or tgt_author == src_author:
                continue
            i, j = author_idx[src_author], author_idx[tgt_author]
            matrix[i][j] += 1

    author_tradicion = {}
    author_tradicion_count = defaultdict(lambda: defaultdict(int))
    for e in entries:
        a = clean_text(e.get("author", ""))
        if not a:
            continue
        author_tradicion_count[a][e.get("tradition", "")] += 1
    for a, counts in author_tradicion_count.items():
        author_tradicion[a] = max(counts.items(), key=lambda kv: kv[1])[0]

    chord = {
        "authors": authors,
        "author_tradition": [author_tradicion.get(a, "") for a in authors],
        "matrix": matrix,
    }

    # 3) Sunburst — jerarquía tradición → autor → concepto
    sunburst_root = {"name": "Corpus", "children": []}
    by_trad_author = defaultdict(lambda: defaultdict(list))
    for e in entries:
        trad = e.get("tradition", "otra")
        author = clean_text(e.get("author", "")) or "(sin autor)"
        by_trad_author[trad][author].append({
            "name": clean_text(e["term"]),
            "value": 1,
            "tradition": trad,
            "essence": clean_text(e.get("essence", "")),
            "year": year_for(e),
        })
    for trad in TRADICIONES:
        if trad not in by_trad_author:
            continue
        trad_node = {
            "name": TRADICIONES[trad]["label"],
            "tradition": trad,
            "children": []
        }
        for author, concepts in by_trad_author[trad].items():
            trad_node["children"].append({
                "name": author,
                "tradition": trad,
                "children": concepts,
            })
        sunburst_root["children"].append(trad_node)

    # 4) Sankey — flujo de refs entre tradiciones (origen → destino)
    sankey_links_dict = defaultdict(int)
    for e in entries:
        src_trad = e.get("tradition", "")
        if not src_trad:
            continue
        for ref_slug in (e.get("ref_slugs") or []):
            tgt_trad = slug_to_tradition.get(ref_slug, "")
            if not tgt_trad:
                continue
            # Renombramos el destino con sufijo " (ref)" para que el sankey
            # tenga columnas separadas y no haga ciclos
            sankey_links_dict[(f"src::{src_trad}", f"tgt::{tgt_trad}")] += 1

    # Nodos: dos columnas (origen y destino)
    sankey_nodes = []
    sankey_node_idx = {}
    for trad in TRADICIONES:
        for prefix in ("src", "tgt"):
            key = f"{prefix}::{trad}"
            if any(key == s or key == t for (s, t) in sankey_links_dict):
                sankey_node_idx[key] = len(sankey_nodes)
                sankey_nodes.append({
                    "name": TRADICIONES[trad]["label"],
                    "tradition": trad,
                    "side": prefix,
                })
    sankey_links = []
    for (src, tgt), v in sankey_links_dict.items():
        if src in sankey_node_idx and tgt in sankey_node_idx:
            sankey_links.append({
                "source": sankey_node_idx[src],
                "target": sankey_node_idx[tgt],
                "value": v,
            })

    sankey = {"nodes": sankey_nodes, "links": sankey_links}

    # 5) Bubble — conceptos por # de menciones entrantes (popularidad por refs)
    inbound = defaultdict(int)
    for e in entries:
        for ref_slug in (e.get("ref_slugs") or []):
            inbound[ref_slug] += 1
    bubble = []
    for e in entries:
        v = inbound.get(e["slug"], 0)
        if v > 0:
            bubble.append({
                "name": clean_text(e["term"]),
                "value": v,
                "tradition": e.get("tradition", ""),
                "author": clean_text(e.get("author", "")),
                "essence": clean_text(e.get("essence", "")),
            })

    # 6) Network — grafo concepto-concepto vía refs
    network_nodes = []
    network_links = []
    in_deg = defaultdict(int)
    out_deg = defaultdict(int)
    valid_slugs = set(slug_to_term.keys())
    for e in entries:
        for r in (e.get("ref_slugs") or []):
            if r in valid_slugs:
                in_deg[r] += 1
                out_deg[e["slug"]] += 1
    for e in entries:
        slug = e["slug"]
        network_nodes.append({
            "id": slug,
            "name": clean_text(e["term"]),
            "tradition": e.get("tradition", ""),
            "author": clean_text(e.get("author", "")),
            "essence": clean_text(e.get("essence", "")),
            "indegree": in_deg.get(slug, 0),
            "outdegree": out_deg.get(slug, 0),
        })
    seen_pairs = set()
    for e in entries:
        src = e["slug"]
        for r in (e.get("ref_slugs") or []):
            if r in valid_slugs and r != src:
                key = tuple(sorted([src, r]))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                network_links.append({"source": src, "target": r})
    network = {"nodes": network_nodes, "links": network_links}

    # 7) Chord de conceptos — top N más conectados
    TOP_N = 28
    deg_total = {s: in_deg.get(s, 0) + out_deg.get(s, 0) for s in valid_slugs}
    top_slugs = sorted(deg_total.keys(), key=lambda s: -deg_total[s])[:TOP_N]
    top_idx = {s: i for i, s in enumerate(top_slugs)}
    nC = len(top_slugs)
    cmat = [[0] * nC for _ in range(nC)]
    for e in entries:
        src = e["slug"]
        if src not in top_idx:
            continue
        for r in (e.get("ref_slugs") or []):
            if r in top_idx and r != src:
                cmat[top_idx[src]][top_idx[r]] += 1
    concept_chord = {
        "concepts": [slug_to_term[s] for s in top_slugs],
        "tradition": [slug_to_tradition[s] for s in top_slugs],
        "matrix": cmat,
    }

    # 8) Heatmap concepto × concepto, ordenado por tradición → autor → término
    sorted_entries = sorted(
        entries,
        key=lambda e: (
            list(TRADICIONES.keys()).index(e.get("tradition", "social"))
                if e.get("tradition", "") in TRADICIONES else 99,
            clean_text(e.get("author", "")),
            clean_text(e["term"])
        )
    )
    hm_slugs = [e["slug"] for e in sorted_entries]
    hm_idx = {s: i for i, s in enumerate(hm_slugs)}
    nH = len(hm_slugs)
    hmat = [[0] * nH for _ in range(nH)]
    for e in entries:
        src = e["slug"]
        if src not in hm_idx:
            continue
        for r in (e.get("ref_slugs") or []):
            if r in hm_idx and r != src:
                hmat[hm_idx[src]][hm_idx[r]] = 1
                hmat[hm_idx[r]][hm_idx[src]] = 1  # simétrico para legibilidad
    heatmap = {
        "labels": [clean_text(slug_to_term[s]) for s in hm_slugs],
        "tradition": [slug_to_tradition[s] for s in hm_slugs],
        "matrix": hmat,
    }

    # 9) Dendrograma radial — reusa la jerarquía del sunburst
    # (La data ya está en sunburst_root; D3 hace el layout)

    # Conteos por tradición
    by_tradicion = defaultdict(int)
    for e in entries:
        by_tradicion[e.get("tradition", "")] += 1

    return {
        "timeline": timeline,
        "chord": chord,
        "sunburst": sunburst_root,
        "sankey": sankey,
        "bubble": bubble,
        "network": network,
        "concept_chord": concept_chord,
        "heatmap": heatmap,
        "tradiciones": TRADICIONES,
        "counts": dict(by_tradicion),
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pensamiento Complejo · Visualización del corpus</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://unpkg.com/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
<style>
  :root {
    --bg: #faf7f2;
    --paper: #ffffff;
    --ink: #1b1b1b;
    --ink-soft: #3a3a3a;
    --muted: #6b6b6b;
    --accent: #7a2e2e;
    --accent-soft: #f3e8e8;
    --rule: #e3ddd0;
    --gold: #b8851f;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    font-family: 'Iowan Old Style', 'Palatino Linotype', Georgia, serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }
  header {
    max-width: 1280px;
    margin: 0 auto;
    padding: 56px 32px 28px;
    border-bottom: 1px solid var(--rule);
  }
  h1 {
    font-family: 'Cormorant Garamond', 'Iowan Old Style', Georgia, serif;
    font-size: 2.4em;
    font-weight: 600;
    margin: 0 0 8px 0;
    letter-spacing: -0.01em;
  }
  h1 em { font-style: italic; color: var(--accent); }
  header p {
    margin: 0;
    color: var(--muted);
    font-size: 1.05em;
    max-width: 720px;
  }
  main {
    max-width: 1280px;
    margin: 0 auto;
    padding: 32px;
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 32px;
  }
  @media (max-width: 900px) {
    main { grid-template-columns: 1fr; }
    nav.toc { position: static !important; max-height: none !important; }
  }
  nav.toc {
    position: sticky;
    top: 24px;
    align-self: start;
    max-height: calc(100vh - 48px);
    overflow-y: auto;
    padding: 16px 0;
    font-family: -apple-system, 'Segoe UI', Inter, sans-serif;
    font-size: 0.86em;
  }
  nav.toc h3 {
    text-transform: uppercase;
    font-size: 0.78em;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 0 0 10px 0;
    font-weight: 600;
  }
  nav.toc a {
    display: block;
    padding: 6px 10px;
    color: var(--ink-soft);
    text-decoration: none;
    border-left: 2px solid transparent;
    transition: all 0.12s;
  }
  nav.toc a:hover {
    color: var(--accent);
    background: var(--accent-soft);
    border-left-color: var(--accent);
  }
  .content { min-width: 0; }
  section {
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 6px;
    padding: 28px 32px 32px;
    margin-bottom: 32px;
  }
  section h2 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.6em;
    font-weight: 600;
    margin: 0 0 6px 0;
    color: var(--accent);
  }
  section .desc {
    color: var(--muted);
    margin: 0 0 24px 0;
    font-size: 0.96em;
    max-width: 760px;
  }
  /* Leyenda */
  .legend {
    display: flex; flex-wrap: wrap; gap: 6px;
    margin: 0 0 18px 0;
  }
  .legend-item {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px;
    border: 1px solid var(--rule);
    border-radius: 14px;
    font-size: 0.84em;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s, border-color 0.15s;
  }
  .legend-item:hover { background: var(--accent-soft); }
  .legend-item.dim { opacity: 0.35; }
  .legend-swatch {
    width: 11px; height: 11px; border-radius: 50%;
    flex-shrink: 0;
  }
  .legend-count {
    color: var(--muted);
    font-size: 0.92em;
  }
  /* Tooltip */
  .tooltip {
    position: absolute;
    pointer-events: none;
    background: var(--ink);
    color: var(--bg);
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 0.86em;
    line-height: 1.4;
    max-width: 320px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.20);
    opacity: 0;
    transition: opacity 0.12s;
    z-index: 1000;
    font-family: -apple-system, 'Segoe UI', Inter, sans-serif;
  }
  .tooltip strong { color: var(--gold); display: block; margin-bottom: 2px; font-size: 1.05em; }
  .tooltip .meta { color: rgba(250,247,242,0.72); font-size: 0.92em; }
  .tooltip .essence { margin-top: 6px; font-style: italic; }
  /* SVG */
  svg { display: block; max-width: 100%; height: auto; }
  .axis text { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 11px; fill: var(--ink-soft); }
  .axis line, .axis path { stroke: var(--rule); }
  .axis-label { font-family: 'Cormorant Garamond', Georgia, serif; font-style: italic; font-size: 13px; fill: var(--ink-soft); }
  .lane-label { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 13px; fill: var(--ink-soft); }
  .gridline { stroke: var(--rule); stroke-dasharray: 2 3; opacity: 0.5; }
  /* Chord */
  .chord-group text { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 11px; fill: var(--ink); }
  .chord-ribbon { fill-opacity: 0.55; mix-blend-mode: multiply; cursor: pointer; }
  .chord-ribbon:hover { fill-opacity: 0.9; }
  .chord-arc { stroke: var(--bg); stroke-width: 1; cursor: pointer; }
  /* Sunburst */
  .sun-arc { stroke: var(--bg); stroke-width: 1; cursor: pointer; transition: opacity 0.15s; }
  .sun-arc:hover { opacity: 0.85; }
  .sun-label { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 10px; fill: var(--ink); pointer-events: none; }
  /* Sankey */
  .sankey-node rect { stroke: var(--bg); stroke-width: 1; cursor: pointer; }
  .sankey-link { fill: none; stroke-opacity: 0.35; cursor: pointer; }
  .sankey-link:hover { stroke-opacity: 0.65; }
  .sankey-label { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 12px; fill: var(--ink-soft); }
  /* Bubble */
  .bubble-circle { stroke: var(--bg); stroke-width: 1.2; cursor: pointer; transition: opacity 0.15s; }
  .bubble-circle:hover { opacity: 0.85; }
  .bubble-label { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 10px; fill: #fff; pointer-events: none; text-anchor: middle; }
  /* Network */
  .net-node { stroke: var(--bg); stroke-width: 1.2; cursor: grab; transition: opacity 0.15s; }
  .net-node:active { cursor: grabbing; }
  .net-node.dim { opacity: 0.18; }
  .net-link { stroke: var(--ink-soft); stroke-opacity: 0.18; stroke-width: 0.8px; }
  .net-link.dim { stroke-opacity: 0.05; }
  .net-link.bright { stroke-opacity: 0.7; }
  .net-label { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 9px; fill: var(--ink); pointer-events: none; }
  /* Heatmap */
  .heat-cell { shape-rendering: crispEdges; }
  .heat-divider { stroke: var(--ink); stroke-width: 0.5; opacity: 0.4; }
  .heat-tlabel { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 9px; fill: var(--ink-soft); }
  /* Dendrogram */
  .dend-link { fill: none; stroke: var(--ink-soft); stroke-opacity: 0.35; stroke-width: 1; }
  .dend-node circle { stroke: var(--bg); stroke-width: 1; }
  .dend-label { font-family: -apple-system, 'Segoe UI', sans-serif; font-size: 9px; fill: var(--ink); }
  /* Footer */
  footer {
    max-width: 1280px;
    margin: 0 auto;
    padding: 24px 32px 56px;
    color: var(--muted);
    font-size: 0.86em;
    text-align: center;
    border-top: 1px solid var(--rule);
  }
  footer a { color: var(--accent); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
</style>
</head>
<body>
<header>
  <h1>Pensamiento <em>complejo</em> · visualización del corpus</h1>
  <p>__INTRO__</p>
</header>

<main>
  <nav class="toc">
    <h3>Visualizaciones</h3>
    <a href="#timeline-section">1 · Cronología</a>
    <a href="#chord-section">2 · Diálogo entre autores</a>
    <a href="#sunburst-section">3 · Jerarquía del corpus</a>
    <a href="#sankey-section">4 · Flujo entre tradiciones</a>
    <a href="#bubble-section">5 · Conceptos más citados</a>
    <a href="#network-section">6 · Red de conceptos</a>
    <a href="#concept-chord-section">7 · Diálogo entre conceptos</a>
    <a href="#heatmap-section">8 · Matriz de co-referencias</a>
    <a href="#dendrogram-section">9 · Dendrograma radial</a>
    <a href="#metrics-section">10 · Análisis de centralidad</a>
  </nav>

  <div class="content">
    <section id="timeline-section">
      <h2>1 · Cronología de las ideas</h2>
      <p class="desc">Cada punto es un concepto del glosario, ubicado por <strong>año</strong> de la obra que lo introduce y agrupado por <strong>tradición</strong>. Pasa el cursor para detalle. Clic en una etiqueta de la leyenda para filtrar.</p>
      <div id="legend-timeline" class="legend"></div>
      <div id="timeline"></div>
    </section>

    <section id="chord-section">
      <h2>2 · Diálogo entre autores</h2>
      <p class="desc">Cada arco es un autor. Las cintas conectan autores que <strong>comparten conceptos</strong> en sus refs cruzadas. Más cinta = más diálogo conceptual.</p>
      <div id="chord"></div>
    </section>

    <section id="sunburst-section">
      <h2>3 · Jerarquía del corpus</h2>
      <p class="desc">Anillos concéntricos: <strong>tradición → autor → concepto</strong>. El tamaño de cada porción es proporcional al número de conceptos. Pasa el cursor para detalle.</p>
      <div id="sunburst"></div>
    </section>

    <section id="sankey-section">
      <h2>4 · Flujo de refs entre tradiciones</h2>
      <p class="desc">Cómo circula el discurso. Cada cinta indica que un concepto de la tradición de la <strong>izquierda</strong> referencia (vía <code>refs</code>) un concepto de la tradición de la <strong>derecha</strong>. Más grosor = más densidad de citaciones cruzadas.</p>
      <div id="sankey"></div>
    </section>

    <section id="bubble-section">
      <h2>5 · Conceptos más citados</h2>
      <p class="desc">Burbujas dimensionadas por número de <strong>refs entrantes</strong> — los puentes intelectuales que más conceptos otros señalan como base. Color por tradición.</p>
      <div id="bubble"></div>
    </section>

    <section id="network-section">
      <h2>6 · Red de conceptos</h2>
      <p class="desc">Grafo concepto-concepto: cada nodo es un concepto del glosario, cada arista es un ref cruzado. Tamaño por # de menciones, color por tradición. <strong>Arrastra los nodos</strong>, <strong>scroll para zoom</strong>, <strong>busca</strong> con el campo abajo.</p>
      <input type="text" id="network-search" placeholder="Buscar concepto…" style="margin-bottom: 12px; padding: 6px 12px; font-family: inherit; font-size: 0.92em; width: 240px; border: 1px solid var(--rule); border-radius: 14px;">
      <div id="network"></div>
    </section>

    <section id="concept-chord-section">
      <h2>7 · Diálogo entre conceptos (top 28)</h2>
      <p class="desc">Como el chord de autores, pero entre los <strong>28 conceptos más conectados</strong>. Cintas = co-referencias. Útil para ver qué ideas se citan más entre sí — los <em>conceptos bisagra</em> del corpus.</p>
      <div id="concept-chord"></div>
    </section>

    <section id="heatmap-section">
      <h2>8 · Matriz de co-referencias</h2>
      <p class="desc">Cuadrícula concepto×concepto (91×91). Los conceptos están <strong>ordenados por tradición</strong> — los cuadrados densos cerca de la diagonal son comunidades intra-tradición; los puntos lejos de la diagonal son <strong>puentes inter-tradición</strong>.</p>
      <div id="heatmap"></div>
    </section>

    <section id="dendrogram-section">
      <h2>9 · Dendrograma radial</h2>
      <p class="desc">Misma jerarquía que el sunburst pero como árbol radial. Útil para presentar el corpus en una imagen única: el centro es el corpus, las ramas son tradiciones, las hojas son conceptos.</p>
      <div id="dendrogram"></div>
    </section>

    <section id="metrics-section">
      <h2>10 · Análisis de centralidad (NetworkX)</h2>
      <p class="desc">Rankings calculados con algoritmos de teoría de redes. <strong>Betweenness</strong> identifica los conceptos puente; <strong>eigenvector</strong> los conectados a otros importantes; <strong>closeness</strong> los más accesibles desde todo el corpus. <strong>Modularity</strong> = <span id="metric-modularity"></span> con <span id="metric-n-communities"></span> comunidades algorítmicas.</p>
      <div id="metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 18px;"></div>
    </section>
  </div>
</main>

<footer>
  Generado a partir del Glosario unificado del Pensamiento Complejo · paleta y datos coherentes con el corpus original.<br>
  Vault Obsidian: <code>Conocimiento/ObsidianDemo</code>
</footer>

<div class="tooltip" id="tooltip"></div>

<script>
const DATA = __DATA_JSON__;
const TRADICIONES = DATA.tradiciones;

/* ============================================================
   Tooltip helpers
   ============================================================ */
const tip = d3.select("#tooltip");
function showTip(html, ev) {
  tip.html(html).style("opacity", 1);
  moveTip(ev);
}
function moveTip(ev) {
  const pad = 16;
  tip.style("left", (ev.pageX + pad) + "px")
     .style("top",  (ev.pageY + pad) + "px");
}
function hideTip() { tip.style("opacity", 0); }

/* ============================================================
   Leyenda con estado de filtro
   ============================================================ */
const filterState = new Set(Object.keys(TRADICIONES));

function renderLegend() {
  const wrap = d3.select("#legend-timeline").html("");
  Object.entries(TRADICIONES).forEach(([key, t]) => {
    const count = DATA.counts[key] || 0;
    const item = wrap.append("div")
      .attr("class", "legend-item" + (filterState.has(key) ? "" : " dim"))
      .on("click", function () {
        if (filterState.has(key)) filterState.delete(key);
        else filterState.add(key);
        renderLegend();
        renderTimeline();
      });
    item.append("span").attr("class", "legend-swatch")
        .style("background", t.color);
    item.append("span").text(t.label);
    item.append("span").attr("class", "legend-count").text("(" + count + ")");
  });
}

/* ============================================================
   Timeline scatter
   ============================================================ */
const TL_W = 1180, TL_M = {top: 24, right: 32, bottom: 48, left: 220};
const TL_LANES = Object.keys(TRADICIONES);
const LANE_H = 38;
const TL_H = TL_M.top + TL_M.bottom + LANE_H * TL_LANES.length;

const tlSvg = d3.select("#timeline").append("svg")
  .attr("viewBox", `0 0 ${TL_W} ${TL_H}`)
  .attr("preserveAspectRatio", "xMidYMid meet");

const yearExtent = d3.extent(DATA.timeline, d => d.year);
const xScale = d3.scaleLinear()
  .domain([Math.floor(yearExtent[0] / 10) * 10 - 5, Math.ceil(yearExtent[1] / 10) * 10 + 5])
  .range([TL_M.left, TL_W - TL_M.right]);

const yScale = d3.scaleBand()
  .domain(TL_LANES)
  .range([TL_M.top, TL_H - TL_M.bottom])
  .padding(0.25);

// Axis X
const xAxis = d3.axisBottom(xScale).tickFormat(d3.format("d")).ticks(10);
tlSvg.append("g").attr("class", "axis")
  .attr("transform", `translate(0, ${TL_H - TL_M.bottom})`)
  .call(xAxis);

// Etiqueta eje X
tlSvg.append("text").attr("class", "axis-label")
  .attr("x", (TL_M.left + TL_W - TL_M.right) / 2)
  .attr("y", TL_H - 12)
  .attr("text-anchor", "middle")
  .text("año de la obra que introduce el concepto");

// Carriles
const lanes = tlSvg.append("g").attr("class", "lanes");
TL_LANES.forEach(key => {
  const t = TRADICIONES[key];
  const y = yScale(key) + yScale.bandwidth() / 2;
  lanes.append("line").attr("class", "gridline")
    .attr("x1", TL_M.left).attr("x2", TL_W - TL_M.right)
    .attr("y1", y).attr("y2", y);
  lanes.append("text").attr("class", "lane-label")
    .attr("x", TL_M.left - 12).attr("y", y + 4)
    .attr("text-anchor", "end")
    .text(t.label);
});

const dotsLayer = tlSvg.append("g").attr("class", "dots");

function renderTimeline() {
  const filtered = DATA.timeline.filter(d => filterState.has(d.tradition));

  // Pequeño jitter horizontal para evitar superposición exacta
  const grouped = d3.group(filtered, d => `${d.year}__${d.tradition}`);
  const positioned = [];
  for (const [key, items] of grouped) {
    items.forEach((d, i) => {
      const offset = (i - (items.length - 1) / 2) * 6;
      positioned.push({...d, x: xScale(d.year) + offset, y: yScale(d.tradition) + yScale.bandwidth() / 2});
    });
  }

  const sel = dotsLayer.selectAll("circle").data(positioned, d => d.slug);
  sel.exit().transition().duration(220).attr("r", 0).remove();
  sel.enter().append("circle")
    .attr("r", 0)
    .attr("cx", d => d.x).attr("cy", d => d.y)
    .attr("fill", d => TRADICIONES[d.tradition]?.color || "#888")
    .attr("stroke", "rgba(0,0,0,0.18)")
    .attr("stroke-width", 0.6)
    .style("cursor", "pointer")
    .on("mouseenter", (ev, d) => {
      const yr = d.year ? `<span class="meta">${d.year} · ${TRADICIONES[d.tradition]?.label}</span>` : "";
      const auth = d.author ? `<span class="meta">${d.author}${d.work ? " — " + d.work : ""}</span>` : "";
      showTip(`<strong>${d.term}</strong>${yr}${auth}<div class="essence">${d.essence}</div>`, ev);
    })
    .on("mousemove", moveTip).on("mouseleave", hideTip)
    .merge(sel)
    .transition().duration(360)
    .attr("cx", d => d.x).attr("cy", d => d.y)
    .attr("r", 6.5);
}

renderLegend();
renderTimeline();

/* ============================================================
   Chord diagram (autores)
   ============================================================ */
const CH_SIZE = 720, CH_MARGIN = 140;
const CH_RADIUS = (CH_SIZE - CH_MARGIN * 2) / 2;
const innerR = CH_RADIUS - 14;
const outerR = CH_RADIUS;

const chSvg = d3.select("#chord").append("svg")
  .attr("viewBox", `0 0 ${CH_SIZE} ${CH_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "780px")
  .style("margin", "0 auto");

const g = chSvg.append("g").attr("transform", `translate(${CH_SIZE/2}, ${CH_SIZE/2})`);

const matrix = DATA.chord.matrix;
const authors = DATA.chord.authors;
const authorTrad = DATA.chord.author_tradition;

const chord = d3.chordDirected().padAngle(0.04).sortSubgroups(d3.descending);
const chords = chord(matrix);

const arc  = d3.arc().innerRadius(innerR).outerRadius(outerR);
const ribbon = d3.ribbon().radius(innerR);

// Arcs (autores)
const groups = g.append("g").selectAll("g")
  .data(chords.groups).enter().append("g").attr("class", "chord-group");

groups.append("path").attr("class", "chord-arc")
  .attr("d", arc)
  .attr("fill", d => TRADICIONES[authorTrad[d.index]]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    const a = authors[d.index];
    const t = TRADICIONES[authorTrad[d.index]];
    showTip(`<strong>${a}</strong><span class="meta">${t ? t.label : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

groups.append("text")
  .each(function(d) { d.angle = (d.startAngle + d.endAngle) / 2; })
  .attr("dy", "0.35em")
  .attr("transform", d =>
    `rotate(${(d.angle * 180 / Math.PI - 90)}) translate(${outerR + 8}) ${d.angle > Math.PI ? "rotate(180)" : ""}`)
  .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
  .text(d => authors[d.index]);

// Ribbons (refs cruzadas autor↔autor)
g.append("g").selectAll("path")
  .data(chords).enter().append("path")
  .attr("class", "chord-ribbon")
  .attr("d", ribbon)
  .attr("fill", d => TRADICIONES[authorTrad[d.source.index]]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    const src = authors[d.source.index];
    const tgt = authors[d.target.index];
    const v = matrix[d.source.index][d.target.index];
    showTip(`<strong>${src} → ${tgt}</strong><span class="meta">${v} concepto${v > 1 ? "s" : ""} compartido${v > 1 ? "s" : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

/* ============================================================
   Sunburst — tradición → autor → concepto
   ============================================================ */
const SB_SIZE = 720;
const sbSvg = d3.select("#sunburst").append("svg")
  .attr("viewBox", `0 0 ${SB_SIZE} ${SB_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "780px")
  .style("margin", "0 auto");

const sbG = sbSvg.append("g").attr("transform", `translate(${SB_SIZE/2}, ${SB_SIZE/2})`);
const sbRadius = SB_SIZE / 2 - 4;

const sbRoot = d3.hierarchy(DATA.sunburst).sum(d => d.value || 0);
d3.partition().size([2 * Math.PI, sbRadius])(sbRoot);

const sbArc = d3.arc()
  .startAngle(d => d.x0)
  .endAngle(d => d.x1)
  .padAngle(0.003)
  .padRadius(sbRadius / 2)
  .innerRadius(d => d.y0)
  .outerRadius(d => d.y1 - 1);

function sbColor(d) {
  let n = d;
  while (n.depth > 1) n = n.parent;
  const trad = n.data.tradition;
  const base = TRADICIONES[trad]?.color || "#888";
  // Más profundo = más claro (mezclando con bg)
  const c = d3.color(base);
  if (!c) return base;
  if (d.depth === 1) return c.formatHex();
  if (d.depth === 2) { c.opacity = 1; return c.brighter(0.3).formatHex(); }
  return c.brighter(0.7).formatHex();
}

sbG.selectAll("path")
  .data(sbRoot.descendants().filter(d => d.depth > 0))
  .enter().append("path")
  .attr("class", "sun-arc")
  .attr("d", sbArc)
  .attr("fill", sbColor)
  .on("mouseenter", (ev, d) => {
    const path = d.ancestors().map(a => a.data.name).reverse().slice(1).join(" → ");
    let extra = "";
    if (d.depth === 3) extra = `<div class="essence">${d.data.essence || ""}</div>`;
    if (d.depth === 1) extra = `<span class="meta">${d.value} conceptos</span>`;
    showTip(`<strong>${d.data.name}</strong><span class="meta">${path}</span>${extra}`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

// Etiquetas en el primer anillo (tradiciones) si caben
sbG.selectAll("text.sb-tradicion")
  .data(sbRoot.descendants().filter(d => d.depth === 1 && (d.x1 - d.x0) > 0.18))
  .enter().append("text")
  .attr("class", "sun-label")
  .attr("transform", d => {
    const a = (d.x0 + d.x1) / 2 - Math.PI / 2;
    const r = (d.y0 + d.y1) / 2;
    const rotate = a * 180 / Math.PI;
    const flip = (rotate > 90 || rotate < -90) ? 180 : 0;
    return `rotate(${rotate}) translate(${r},0) rotate(${flip})`;
  })
  .attr("text-anchor", "middle")
  .attr("dy", "0.35em")
  .style("fill", "#fff")
  .style("font-weight", "600")
  .text(d => d.data.name.length > 22 ? d.data.name.slice(0, 20) + "…" : d.data.name);

/* ============================================================
   Sankey — flujo entre tradiciones
   ============================================================ */
const SK_W = 1180, SK_H = 460;
const skSvg = d3.select("#sankey").append("svg")
  .attr("viewBox", `0 0 ${SK_W} ${SK_H}`)
  .attr("preserveAspectRatio", "xMidYMid meet");

const sankeyData = {
  nodes: DATA.sankey.nodes.map(d => ({...d})),
  links: DATA.sankey.links.map(d => ({...d}))
};

const sankeyLayout = d3.sankey()
  .nodeWidth(16)
  .nodePadding(12)
  .nodeSort(null)
  .extent([[180, 24], [SK_W - 180, SK_H - 24]]);

const sk = sankeyLayout(sankeyData);

skSvg.append("g").selectAll("rect")
  .data(sk.nodes).enter().append("rect")
  .attr("class", "sankey-node")
  .attr("x", d => d.x0).attr("y", d => d.y0)
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => TRADICIONES[d.tradition]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    const total = d.side === "src"
      ? d.sourceLinks.reduce((a, l) => a + l.value, 0)
      : d.targetLinks.reduce((a, l) => a + l.value, 0);
    const dir = d.side === "src" ? "→ refs salientes" : "← refs entrantes";
    showTip(`<strong>${d.name}</strong><span class="meta">${dir}: ${total}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

skSvg.append("g")
  .attr("fill", "none")
  .selectAll("path")
  .data(sk.links).enter().append("path")
  .attr("class", "sankey-link")
  .attr("d", d3.sankeyLinkHorizontal())
  .attr("stroke", d => TRADICIONES[d.source.tradition]?.color || "#888")
  .attr("stroke-width", d => Math.max(1, d.width))
  .on("mouseenter", (ev, d) => {
    showTip(`<strong>${d.source.name} → ${d.target.name}</strong><span class="meta">${d.value} ref${d.value > 1 ? "s" : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

skSvg.append("g").selectAll("text")
  .data(sk.nodes).enter().append("text")
  .attr("class", "sankey-label")
  .attr("x", d => d.side === "src" ? d.x0 - 8 : d.x1 + 8)
  .attr("y", d => (d.y0 + d.y1) / 2)
  .attr("dy", "0.35em")
  .attr("text-anchor", d => d.side === "src" ? "end" : "start")
  .text(d => d.name);

/* ============================================================
   Bubble — conceptos más citados
   ============================================================ */
const BB_SIZE = 760;
const bbSvg = d3.select("#bubble").append("svg")
  .attr("viewBox", `0 0 ${BB_SIZE} ${BB_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "820px")
  .style("margin", "0 auto");

const bbRoot = d3.hierarchy({children: DATA.bubble}).sum(d => d.value || 0);
d3.pack().size([BB_SIZE, BB_SIZE]).padding(3)(bbRoot);

const bbNode = bbSvg.append("g").selectAll("g")
  .data(bbRoot.leaves()).enter().append("g")
  .attr("transform", d => `translate(${d.x},${d.y})`);

bbNode.append("circle")
  .attr("class", "bubble-circle")
  .attr("r", d => d.r)
  .attr("fill", d => TRADICIONES[d.data.tradition]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    showTip(`<strong>${d.data.name}</strong><span class="meta">${d.data.author} · ${TRADICIONES[d.data.tradition]?.label || d.data.tradition}</span><div class="essence">${d.data.essence}</div><span class="meta" style="margin-top:4px;display:block;">Citado por ${d.value} concepto${d.value > 1 ? "s" : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

bbNode.filter(d => d.r > 22).append("text")
  .attr("class", "bubble-label")
  .attr("dy", "0.35em")
  .text(d => {
    const max = Math.floor(d.r / 4);
    return d.data.name.length > max ? d.data.name.slice(0, max - 1) + "…" : d.data.name;
  });

/* ============================================================
   6 · Red force-directed de conceptos
   ============================================================ */
const NET_W = 1180, NET_H = 720;
const netSvg = d3.select("#network").append("svg")
  .attr("viewBox", `0 0 ${NET_W} ${NET_H}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("background", "#fdfbf6")
  .style("border-radius", "4px");

const netZoom = netSvg.append("g");

const nodes = DATA.network.nodes.map(d => ({...d}));
const links = DATA.network.links.map(d => ({...d}));

const radiusScale = d3.scaleSqrt()
  .domain([0, d3.max(nodes, d => d.indegree) || 1])
  .range([3, 16]);

const sim = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(40).strength(0.45))
  .force("charge", d3.forceManyBody().strength(-110))
  .force("center", d3.forceCenter(NET_W/2, NET_H/2))
  .force("collide", d3.forceCollide().radius(d => radiusScale(d.indegree) + 2));

const linkSel = netZoom.append("g").selectAll("line")
  .data(links).enter().append("line")
  .attr("class", "net-link");

const nodeSel = netZoom.append("g").selectAll("circle")
  .data(nodes).enter().append("circle")
  .attr("class", "net-node")
  .attr("r", d => radiusScale(d.indegree))
  .attr("fill", d => TRADICIONES[d.tradition]?.color || "#888")
  .call(d3.drag()
    .on("start", (ev, d) => { if (!ev.active) sim.alphaTarget(0.2).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
    .on("end", (ev, d) => { if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }))
  .on("mouseenter", (ev, d) => {
    showTip(`<strong>${d.name}</strong><span class="meta">${d.author} · ${TRADICIONES[d.tradition]?.label || d.tradition}</span><span class="meta">${d.indegree} entrantes · ${d.outdegree} salientes</span><div class="essence">${d.essence}</div>`, ev);
    // resaltar vecinos
    const neighbors = new Set([d.id]);
    links.forEach(l => {
      if (l.source.id === d.id) neighbors.add(l.target.id);
      if (l.target.id === d.id) neighbors.add(l.source.id);
    });
    nodeSel.classed("dim", n => !neighbors.has(n.id));
    linkSel.classed("dim", l => l.source.id !== d.id && l.target.id !== d.id);
    linkSel.classed("bright", l => l.source.id === d.id || l.target.id === d.id);
  })
  .on("mousemove", moveTip)
  .on("mouseleave", () => {
    hideTip();
    nodeSel.classed("dim", false);
    linkSel.classed("dim", false).classed("bright", false);
  });

sim.on("tick", () => {
  linkSel
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  nodeSel.attr("cx", d => d.x).attr("cy", d => d.y);
});

// Zoom
netSvg.call(d3.zoom().scaleExtent([0.4, 4]).on("zoom", (ev) => {
  netZoom.attr("transform", ev.transform);
}));

// Búsqueda
d3.select("#network-search").on("input", function () {
  const q = this.value.toLowerCase().trim();
  if (!q) {
    nodeSel.classed("dim", false);
    linkSel.classed("dim", false);
    return;
  }
  const matched = new Set(nodes.filter(n => n.name.toLowerCase().includes(q)).map(n => n.id));
  nodeSel.classed("dim", n => !matched.has(n.id));
  linkSel.classed("dim", true);
});

/* ============================================================
   7 · Chord de conceptos (top 28)
   ============================================================ */
const CC_SIZE = 760, CC_MARGIN = 160;
const CC_RADIUS = (CC_SIZE - CC_MARGIN * 2) / 2;
const ccInnerR = CC_RADIUS - 12;
const ccOuterR = CC_RADIUS;

const ccSvg = d3.select("#concept-chord").append("svg")
  .attr("viewBox", `0 0 ${CC_SIZE} ${CC_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "820px").style("margin", "0 auto");

const ccG = ccSvg.append("g").attr("transform", `translate(${CC_SIZE/2}, ${CC_SIZE/2})`);

const ccChord = d3.chord().padAngle(0.025).sortSubgroups(d3.descending);
const ccChords = ccChord(DATA.concept_chord.matrix);
const ccArc = d3.arc().innerRadius(ccInnerR).outerRadius(ccOuterR);
const ccRibbon = d3.ribbon().radius(ccInnerR);

const ccGroups = ccG.append("g").selectAll("g")
  .data(ccChords.groups).enter().append("g");

ccGroups.append("path").attr("class", "chord-arc")
  .attr("d", ccArc)
  .attr("fill", d => TRADICIONES[DATA.concept_chord.tradition[d.index]]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    const c = DATA.concept_chord.concepts[d.index];
    const t = TRADICIONES[DATA.concept_chord.tradition[d.index]];
    showTip(`<strong>${c}</strong><span class="meta">${t ? t.label : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

ccGroups.append("text")
  .each(function(d) { d.angle = (d.startAngle + d.endAngle) / 2; })
  .attr("dy", "0.35em")
  .style("font-family", "-apple-system, sans-serif")
  .style("font-size", "10px")
  .attr("transform", d =>
    `rotate(${(d.angle * 180 / Math.PI - 90)}) translate(${ccOuterR + 6}) ${d.angle > Math.PI ? "rotate(180)" : ""}`)
  .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
  .text(d => DATA.concept_chord.concepts[d.index]);

ccG.append("g").selectAll("path")
  .data(ccChords).enter().append("path")
  .attr("class", "chord-ribbon")
  .attr("d", ccRibbon)
  .attr("fill", d => TRADICIONES[DATA.concept_chord.tradition[d.source.index]]?.color || "#888")
  .on("mouseenter", (ev, d) => {
    const a = DATA.concept_chord.concepts[d.source.index];
    const b = DATA.concept_chord.concepts[d.target.index];
    const v = DATA.concept_chord.matrix[d.source.index][d.target.index];
    showTip(`<strong>${a} ↔ ${b}</strong><span class="meta">${v} co-ref${v > 1 ? "s" : ""}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

/* ============================================================
   8 · Heatmap concepto × concepto
   ============================================================ */
const HM_SIZE = 880, HM_MARGIN = 8;
const N = DATA.heatmap.labels.length;
const cellSize = (HM_SIZE - HM_MARGIN * 2) / N;

const hmSvg = d3.select("#heatmap").append("svg")
  .attr("viewBox", `0 0 ${HM_SIZE} ${HM_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("background", "#fdfbf6")
  .style("border-radius", "4px");

const hmG = hmSvg.append("g").attr("transform", `translate(${HM_MARGIN},${HM_MARGIN})`);

// Celdas — solo dibuja las que tienen ref (1)
const cells = [];
for (let i = 0; i < N; i++) {
  for (let j = 0; j < N; j++) {
    if (DATA.heatmap.matrix[i][j]) cells.push({i, j});
  }
}
hmG.selectAll("rect.heat-cell").data(cells).enter().append("rect")
  .attr("class", "heat-cell")
  .attr("x", d => d.j * cellSize)
  .attr("y", d => d.i * cellSize)
  .attr("width", cellSize).attr("height", cellSize)
  .attr("fill", d => TRADICIONES[DATA.heatmap.tradition[d.i]]?.color || "#888")
  .attr("opacity", 0.85)
  .on("mouseenter", (ev, d) => {
    const a = DATA.heatmap.labels[d.i];
    const b = DATA.heatmap.labels[d.j];
    showTip(`<strong>${a}</strong><span class="meta">↔ ${b}</span>`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

// Divisores entre tradiciones
const divisorPositions = [];
for (let i = 1; i < N; i++) {
  if (DATA.heatmap.tradition[i] !== DATA.heatmap.tradition[i-1]) {
    divisorPositions.push(i);
  }
}
divisorPositions.forEach(p => {
  hmG.append("line").attr("class", "heat-divider")
    .attr("x1", 0).attr("x2", N * cellSize)
    .attr("y1", p * cellSize).attr("y2", p * cellSize);
  hmG.append("line").attr("class", "heat-divider")
    .attr("y1", 0).attr("y2", N * cellSize)
    .attr("x1", p * cellSize).attr("x2", p * cellSize);
});

// Etiquetas de tradición — un label por bloque
const tradStartIdx = {};
DATA.heatmap.tradition.forEach((t, i) => {
  if (!(t in tradStartIdx)) tradStartIdx[t] = i;
});
Object.entries(tradStartIdx).forEach(([trad, startIdx]) => {
  let endIdx = startIdx;
  while (endIdx < N && DATA.heatmap.tradition[endIdx] === trad) endIdx++;
  const center = ((startIdx + endIdx) / 2) * cellSize;
  hmG.append("text")
    .attr("class", "heat-tlabel")
    .attr("x", -4).attr("y", center).attr("dy", "0.32em")
    .attr("text-anchor", "end")
    .style("font-weight", "600")
    .style("fill", TRADICIONES[trad]?.color || "#888")
    .text((TRADICIONES[trad]?.label || trad).split(" ")[0]);
});

/* ============================================================
   9 · Dendrograma radial
   ============================================================ */
const DD_SIZE = 880;
const ddSvg = d3.select("#dendrogram").append("svg")
  .attr("viewBox", `0 0 ${DD_SIZE} ${DD_SIZE}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("max-width", "920px").style("margin", "0 auto");

const ddG = ddSvg.append("g").attr("transform", `translate(${DD_SIZE/2}, ${DD_SIZE/2})`);

const ddRoot = d3.hierarchy(DATA.sunburst);
const ddRadius = DD_SIZE / 2 - 80;

d3.cluster().size([2 * Math.PI, ddRadius])(ddRoot);

function radial(angle, radius) {
  return [Math.cos(angle - Math.PI/2) * radius, Math.sin(angle - Math.PI/2) * radius];
}

ddG.append("g")
  .attr("fill", "none")
  .selectAll("path")
  .data(ddRoot.links())
  .enter().append("path")
  .attr("class", "dend-link")
  .attr("d", d3.linkRadial().angle(d => d.x).radius(d => d.y));

const ddNode = ddG.append("g").selectAll("g")
  .data(ddRoot.descendants())
  .enter().append("g")
  .attr("class", "dend-node")
  .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`);

ddNode.append("circle")
  .attr("r", d => d.children ? 3 : 4)
  .attr("fill", d => {
    if (d.depth === 0) return "#1b1b1b";
    let n = d;
    while (n.depth > 1) n = n.parent;
    return TRADICIONES[n.data.tradition]?.color || "#888";
  })
  .style("cursor", d => d.children ? "default" : "pointer")
  .on("mouseenter", (ev, d) => {
    if (d.depth === 0) return;
    const path = d.ancestors().map(a => a.data.name).reverse().slice(1).join(" → ");
    let extra = "";
    if (d.depth === 3) extra = `<div class="essence">${d.data.essence || ""}</div>`;
    showTip(`<strong>${d.data.name}</strong><span class="meta">${path}</span>${extra}`, ev);
  })
  .on("mousemove", moveTip).on("mouseleave", hideTip);

// Etiquetas solo en el nivel 1 (tradiciones) y hojas con espacio
ddNode.filter(d => d.depth === 3).append("text")
  .attr("class", "dend-label")
  .attr("dy", "0.32em")
  .attr("x", d => d.x < Math.PI ? 7 : -7)
  .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
  .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
  .text(d => d.data.name.length > 22 ? d.data.name.slice(0,20)+"…" : d.data.name);

</script>
</body>
</html>
"""

INTRO = (
    "El corpus contiene 91 conceptos de 13 autores en 10 tradiciones intelectuales — desde Whitehead (1929) "
    "hasta el principio de energía libre (2009). Estas dos visualizaciones invitan a leerlo de dos modos: "
    "<strong>el tiempo</strong> (cuándo apareció cada idea) y <strong>el diálogo</strong> (qué autores se cruzan "
    "vía conceptos compartidos)."
)


def main():
    html_text = GLOSARIO_HTML.read_text(encoding="utf-8")
    entries = extract_data(html_text)
    print(f"Entradas leídas: {len(entries)}")

    viz_data = build_visualization_data(entries)
    print(f"Autores en chord diagram: {len(viz_data['chord']['authors'])}")
    print(f"Conexiones autor-autor: {sum(sum(row) for row in viz_data['chord']['matrix'])}")

    out = HTML_TEMPLATE.replace("__INTRO__", INTRO)
    out = out.replace("__DATA_JSON__", json.dumps(viz_data, ensure_ascii=False))

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(out, encoding="utf-8")
    size_kb = DEST.stat().st_size // 1024
    print(f"\nGenerado: {DEST}")
    print(f"Tamaño: {size_kb} KB")


if __name__ == "__main__":
    main()
