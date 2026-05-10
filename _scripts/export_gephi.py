"""
Exporta el corpus del glosario a formatos para Gephi:

- nodes.csv : Id, Label, tradition, tradition_label, author, year, indegree, outdegree
- edges.csv : Source, Target, Type, Weight
- corpus.gexf : formato nativo Gephi (XML), con todo embebido + colores

Uso:
    python _scripts/export_gephi.py

Salida:
    Visualizaciones/gephi/
        nodes.csv
        edges.csv
        corpus.gexf
"""

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

GLOSARIO_HTML = Path(
    r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\Memoria Activa del Pensamiento Complejo\Glosario - Pensamiento Complejo.html"
)
VAULT = Path(r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\ObsidianDemo")
OUT = VAULT / "Visualizaciones" / "gephi"

# Misma paleta que el HTML del glosario
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

WORK_YEAR = {
    "El Método I — La naturaleza de la Naturaleza":  1977,
    "El Método II — La vida de la Vida":              1980,
    "El Método III — El conocimiento del Conocimiento": 1986,
    "El Método IV — Las ideas":                       1991,
    "El Método V — La humanidad de la Humanidad":     2001,
    "El Método VI — Ética":                           2004,
    "Introducción al pensamiento complejo":           1990,
    "El árbol del conocimiento":                      1984,
    "The Embodied Mind":                              1991,
    "Fenomenología de la percepción":                 1945,
    "On Constructing a Reality":                      1973,
    "The Free-Energy Principle":                      2009,
    "Whatever Next: Predictive Brains and Situated Agents": 2013,
    "An Information Integration Theory of Consciousness": 2004,
    "The Routledge Handbook of Panpsychism":          2019,
    "La nueva alianza":                               1979,
    "At Home in the Universe":                        1995,
    "The Origins of Order":                           1993,
    "Process and Reality":                            1929,
    "La revolución contemporánea del saber y la complejidad social": 2006,
}
TRAD_FALLBACK = {
    "morin": 1990, "autopoiesis": 1980, "embodied": 1991, "cybernetics": 1973,
    "predictive": 2010, "iit": 2008, "panpsiquismo": 2010, "termodinamica": 1985,
    "proceso": 1929, "social": 2006,
}


def clean(s):
    if s is None:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def year_for(e):
    work = clean(e.get("work", ""))
    if work in WORK_YEAR:
        return WORK_YEAR[work]
    for k, y in WORK_YEAR.items():
        if k in work or work in k:
            return y
    morin_vols = {1: 1977, 2: 1980, 3: 1986, 4: 1991, 5: 2001, 6: 2004}
    if e.get("tradition") == "morin" and e.get("volume") in morin_vols:
        return morin_vols[e["volume"]]
    return TRAD_FALLBACK.get(e.get("tradition", ""), 1990)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def main():
    html_text = GLOSARIO_HTML.read_text(encoding="utf-8")
    m = re.search(r"const\s+DATA\s*=\s*(\[.*?\]);", html_text, re.DOTALL)
    if not m:
        raise RuntimeError("No se encontró DATA")
    entries = json.loads(m.group(1))
    print(f"Entradas: {len(entries)}")

    OUT.mkdir(parents=True, exist_ok=True)

    valid_slugs = {e["slug"] for e in entries}

    # Calcular degrees
    in_deg = defaultdict(int)
    out_deg = defaultdict(int)
    for e in entries:
        for r in (e.get("ref_slugs") or []):
            if r in valid_slugs:
                in_deg[r] += 1
                out_deg[e["slug"]] += 1

    # 1) nodes.csv
    nodes_path = OUT / "nodes.csv"
    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Id", "Label", "tradition", "tradition_label", "author",
                    "work", "year", "theme", "indegree", "outdegree", "totaldegree"])
        for e in entries:
            slug = e["slug"]
            trad = e.get("tradition", "")
            w.writerow([
                slug,
                clean(e["term"]),
                trad,
                TRADICIONES.get(trad, {}).get("label", trad),
                clean(e.get("author", "")),
                clean(e.get("work", "")),
                year_for(e),
                clean(e.get("theme", "")),
                in_deg.get(slug, 0),
                out_deg.get(slug, 0),
                in_deg.get(slug, 0) + out_deg.get(slug, 0),
            ])
    print(f"  nodes.csv: {len(entries)} filas")

    # 2) edges.csv (no dirigido, una arista por par único; weight = número de refs)
    edge_weights = defaultdict(int)
    for e in entries:
        src = e["slug"]
        for r in (e.get("ref_slugs") or []):
            if r in valid_slugs and r != src:
                pair = tuple(sorted([src, r]))
                edge_weights[pair] += 1
    edges_path = OUT / "edges.csv"
    with open(edges_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Source", "Target", "Type", "Weight"])
        for (a, b), v in edge_weights.items():
            w.writerow([a, b, "Undirected", v])
    print(f"  edges.csv: {len(edge_weights)} aristas")

    # 3) corpus.gexf (XML — Gephi nativo, todo en un archivo)
    gexf = []
    gexf.append('<?xml version="1.0" encoding="UTF-8"?>')
    gexf.append('<gexf xmlns="http://www.gexf.net/1.3" '
                'xmlns:viz="http://www.gexf.net/1.3/viz" version="1.3">')
    gexf.append(f'<meta lastmodifieddate="2026-05-10">')
    gexf.append('<creator>Vault Pensamiento Complejo</creator>')
    gexf.append('<description>Corpus de pensamiento complejo: 91 conceptos, 14 autores, 10 tradiciones</description>')
    gexf.append('</meta>')
    gexf.append('<graph mode="static" defaultedgetype="undirected">')

    # Atributos de nodo
    gexf.append('<attributes class="node">')
    gexf.append('<attribute id="0" title="tradition" type="string"/>')
    gexf.append('<attribute id="1" title="tradition_label" type="string"/>')
    gexf.append('<attribute id="2" title="author" type="string"/>')
    gexf.append('<attribute id="3" title="work" type="string"/>')
    gexf.append('<attribute id="4" title="year" type="integer"/>')
    gexf.append('<attribute id="5" title="theme" type="string"/>')
    gexf.append('</attributes>')

    # Nodos
    gexf.append('<nodes>')
    for e in entries:
        slug = e["slug"]
        trad = e.get("tradition", "")
        label = clean(e["term"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        color = TRADICIONES.get(trad, {}).get("color", "#888888")
        r, g, b = hex_to_rgb(color)
        size = 10 + (in_deg.get(slug, 0) + out_deg.get(slug, 0)) * 1.2

        gexf.append(f'<node id="{slug}" label="{label}">')
        gexf.append('<attvalues>')
        gexf.append(f'<attvalue for="0" value="{trad}"/>')
        gexf.append(f'<attvalue for="1" value="{TRADICIONES.get(trad, {}).get("label", trad).replace("&", "&amp;")}"/>')
        gexf.append(f'<attvalue for="2" value="{clean(e.get("author", "")).replace("&", "&amp;")}"/>')
        gexf.append(f'<attvalue for="3" value="{clean(e.get("work", "")).replace("&", "&amp;")}"/>')
        gexf.append(f'<attvalue for="4" value="{year_for(e)}"/>')
        gexf.append(f'<attvalue for="5" value="{clean(e.get("theme", "")).replace("&", "&amp;")}"/>')
        gexf.append('</attvalues>')
        gexf.append(f'<viz:color r="{r}" g="{g}" b="{b}" a="1.0"/>')
        gexf.append(f'<viz:size value="{size:.1f}"/>')
        gexf.append('</node>')
    gexf.append('</nodes>')

    # Aristas
    gexf.append('<edges>')
    for i, ((a, b), v) in enumerate(edge_weights.items()):
        gexf.append(f'<edge id="{i}" source="{a}" target="{b}" weight="{v}"/>')
    gexf.append('</edges>')

    gexf.append('</graph>')
    gexf.append('</gexf>')

    gexf_path = OUT / "corpus.gexf"
    gexf_path.write_text("\n".join(gexf), encoding="utf-8")
    print(f"  corpus.gexf: {len(entries)} nodos + {len(edge_weights)} aristas")

    print(f"\nGenerado en: {OUT}")
    for p in [nodes_path, edges_path, gexf_path]:
        kb = p.stat().st_size // 1024
        print(f"  {p.name}: {kb} KB")


if __name__ == "__main__":
    main()
