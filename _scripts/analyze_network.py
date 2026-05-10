"""
Análisis de red sobre el corpus del glosario, equivalente a lo que harías en Gephi
pero en Python con NetworkX. Calcula:

- Degree centrality (in, out, total)
- Betweenness centrality (los puentes intelectuales)
- Closeness centrality (qué tan central está cada concepto)
- Eigenvector centrality (importancia por prestigio)
- Comunidades por modularity (Louvain)

Salida:
- Visualizaciones/gephi/corpus_metrics.gexf — GEXF enriquecido para Gephi
- Visualizaciones/gephi/metrics.json — JSON con métricas para el HTML
- Visualizaciones/gephi/ranking.txt — Ranking legible en consola

Uso:
    python _scripts/analyze_network.py
"""

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

import networkx as nx

GLOSARIO_HTML = Path(
    r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\Memoria Activa del Pensamiento Complejo\Glosario - Pensamiento Complejo.html"
)
VAULT = Path(r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\ObsidianDemo")
OUT = VAULT / "Visualizaciones" / "gephi"

TRADICIONES = {
    "morin":         {"label": "Pensamiento complejo (Morin)",     "color": "#7a2e2e"},
    "autopoiesis":   {"label": "Autopoiesis",                       "color": "#4a6b3c"},
    "cybernetics":   {"label": "Cibernetica 2do orden",             "color": "#3c5b6b"},
    "embodied":      {"label": "Cognicion encarnada",               "color": "#6b4a3c"},
    "predictive":    {"label": "Mente predictiva",                  "color": "#6b3c5b"},
    "iit":           {"label": "Informacion integrada (IIT)",       "color": "#5b3c6b"},
    "panpsiquismo":  {"label": "Panpsiquismo",                      "color": "#6b5b3c"},
    "termodinamica": {"label": "Termodinamica del no-equilibrio",   "color": "#b8851f"},
    "proceso":       {"label": "Filosofia del proceso (Whitehead)", "color": "#3c6b5b"},
    "social":        {"label": "Complejidad social",                "color": "#8b6b3a"},
}


def clean(s):
    if s is None:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def main():
    text = GLOSARIO_HTML.read_text(encoding="utf-8")
    m = re.search(r"const\s+DATA\s*=\s*(\[.*?\]);", text, re.DOTALL)
    entries = json.loads(m.group(1))

    valid_slugs = {e["slug"] for e in entries}
    slug_to_term = {e["slug"]: clean(e["term"]) for e in entries}
    slug_to_tradition = {e["slug"]: e.get("tradition", "") for e in entries}
    slug_to_author = {e["slug"]: clean(e.get("author", "")) for e in entries}

    # Construye grafo NO dirigido con peso = #refs compartidas
    G = nx.Graph()
    for e in entries:
        G.add_node(
            e["slug"],
            label=clean(e["term"]),
            tradition=e.get("tradition", ""),
            tradition_label=TRADICIONES.get(e.get("tradition", ""), {}).get("label", ""),
            author=clean(e.get("author", "")),
            essence=clean(e.get("essence", "")),
        )

    edge_weights = defaultdict(int)
    for e in entries:
        src = e["slug"]
        for r in (e.get("ref_slugs") or []):
            if r in valid_slugs and r != src:
                pair = tuple(sorted([src, r]))
                edge_weights[pair] += 1
    for (a, b), w in edge_weights.items():
        G.add_edge(a, b, weight=w)

    print(f"Grafo: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

    # ============================================================
    # METRICAS
    # ============================================================
    print("\nCalculando metricas...")

    # Degree (ya las teniamos pero las ponemos completas)
    deg = dict(G.degree(weight="weight"))
    deg_unweighted = dict(G.degree())

    # Betweenness centrality (puentes)
    bw = nx.betweenness_centrality(G, weight="weight", normalized=True)

    # Closeness centrality (que tan accesible esta cada nodo)
    cl = nx.closeness_centrality(G, distance="weight")

    # Eigenvector centrality (importancia por prestigio)
    # Usamos la version pura Python (no requiere scipy)
    ev = nx.eigenvector_centrality(G, weight="weight", max_iter=2000, tol=1e-6)

    # Skipped: pagerank (requiere scipy)
    pr = {n: 0.0 for n in G.nodes}

    # Modularidad (Louvain)
    try:
        from networkx.algorithms.community import louvain_communities
        communities = louvain_communities(G, weight="weight", seed=42)
    except ImportError:
        communities = list(nx.community.greedy_modularity_communities(G, weight="weight"))

    node_to_community = {}
    for i, comm in enumerate(communities):
        for n in comm:
            node_to_community[n] = i

    modularity_score = nx.community.modularity(G, communities, weight="weight")
    print(f"Modularity: {modularity_score:.3f} con {len(communities)} comunidades")

    # ============================================================
    # ASIGNAR ATRIBUTOS AL GRAFO
    # ============================================================
    for n in G.nodes:
        G.nodes[n]["degree"] = deg_unweighted.get(n, 0)
        G.nodes[n]["weighted_degree"] = float(deg.get(n, 0))
        G.nodes[n]["betweenness"] = float(bw.get(n, 0))
        G.nodes[n]["closeness"] = float(cl.get(n, 0))
        G.nodes[n]["eigenvector"] = float(ev.get(n, 0))
        G.nodes[n]["pagerank"] = float(pr.get(n, 0))
        G.nodes[n]["community"] = int(node_to_community.get(n, -1))

    # ============================================================
    # RANKINGS
    # ============================================================
    def top(metric, k=10):
        sorted_n = sorted(G.nodes, key=lambda n: G.nodes[n][metric], reverse=True)[:k]
        return [(slug_to_term[n], G.nodes[n][metric], slug_to_tradition[n]) for n in sorted_n]

    rankings_text = []

    def add_section(title, metric, fmt="{:.4f}"):
        rankings_text.append(f"\n{'=' * 64}")
        rankings_text.append(f"  {title}")
        rankings_text.append(f"{'=' * 64}")
        for i, (term, val, trad) in enumerate(top(metric, 12), 1):
            line = f"{i:2d}. {term:<40} {fmt.format(val):>10}  {trad}"
            rankings_text.append(line)

    add_section("BETWEENNESS CENTRALITY (puentes intelectuales)", "betweenness")
    add_section("EIGENVECTOR CENTRALITY (importancia por prestigio)", "eigenvector")
    add_section("CLOSENESS CENTRALITY (que tan central es cada concepto)", "closeness")
    add_section("DEGREE (cantidad bruta de conexiones)", "degree", fmt="{:.0f}")

    rankings_text.append(f"\n{'=' * 64}")
    rankings_text.append(f"  COMUNIDADES (Louvain, modularidad = {modularity_score:.3f})")
    rankings_text.append(f"{'=' * 64}")
    for i, comm in enumerate(communities):
        terms = sorted([slug_to_term[n] for n in comm])
        rankings_text.append(f"\nComunidad {i+1} ({len(comm)} nodos):")
        for t in terms:
            rankings_text.append(f"  - {t}")

    output = "\n".join(rankings_text)
    # Imprime de forma resistente al encoding de Windows console
    try:
        print(output)
    except UnicodeEncodeError:
        import sys
        sys.stdout.buffer.write(output.encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")

    # ============================================================
    # SALIDA
    # ============================================================
    OUT.mkdir(parents=True, exist_ok=True)

    # Guardar GEXF enriquecido. NetworkX exporta GEXF nativo.
    gexf_path = OUT / "corpus_metrics.gexf"
    # Agregamos viz: color y size por tradición y betweenness para Gephi
    for n in G.nodes:
        trad = G.nodes[n].get("tradition", "")
        color = TRADICIONES.get(trad, {}).get("color", "#888888")
        r, g, b = hex_to_rgb(color)
        G.nodes[n]["viz"] = {
            "color": {"r": r, "g": g, "b": b, "a": 1.0},
            "size": 10 + G.nodes[n]["betweenness"] * 200,
        }
    nx.write_gexf(G, gexf_path)
    print(f"\nGEXF enriquecido: {gexf_path}")

    # Guardar JSON con metricas para el HTML
    metrics_data = {
        "modularity": modularity_score,
        "n_communities": len(communities),
        "rankings": {
            "betweenness": top("betweenness", 15),
            "eigenvector": top("eigenvector", 15),
            "closeness": top("closeness", 15),
            "degree": top("degree", 15),
        },
        "communities": [
            {
                "id": i,
                "size": len(comm),
                "members": sorted([slug_to_term[n] for n in comm]),
                "dominant_tradition": max(
                    set([slug_to_tradition[n] for n in comm]),
                    key=lambda t: sum(1 for n in comm if slug_to_tradition[n] == t),
                ),
            }
            for i, comm in enumerate(communities)
        ],
    }
    metrics_json = OUT / "metrics.json"
    metrics_json.write_text(json.dumps(metrics_data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    print(f"Metricas JSON: {metrics_json}")

    # Texto plano para inspeccion rapida
    ranking_path = OUT / "ranking.txt"
    ranking_path.write_text(output, encoding="utf-8")
    print(f"Ranking plano: {ranking_path}")


if __name__ == "__main__":
    main()
