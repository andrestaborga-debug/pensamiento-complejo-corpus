"""
Importa el glosario HTML al vault de Obsidian como notas .md.

Lee 'Glosario - Pensamiento Complejo.html', extrae el array JS DATA,
y genera una nota markdown por cada entrada en /Glosario/.
"""

import html
import json
import re
import unicodedata
from pathlib import Path


def clean_meta(value):
    """Limpia un campo de metadatos: decodifica entidades HTML, quita tags HTML
    y elimina caracteres que rompen YAML. Devuelve string vacío para None."""
    if value is None:
        return ""
    s = str(value)
    # Decodifica todas las entidades HTML (&amp; → &, &nbsp; → espacio, etc.)
    s = html.unescape(s)
    # Elimina cualquier tag HTML residual
    s = re.sub(r"<[^>]+>", "", s)
    # Colapsa espacios múltiples
    s = re.sub(r"\s+", " ", s).strip()
    return s


def yaml_quote(value: str) -> str:
    """Devuelve un string YAML-safe. Si contiene caracteres especiales, lo cita."""
    if not value:
        return '""'
    # Caracteres que requieren citado en YAML
    needs_quote = any(c in value for c in ":#&*?|>!%@`,[]{}")
    if needs_quote or value != value.strip() or value.startswith(("-", "?", ":")):
        # Escapa comillas dobles
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value

# Rutas
GLOSARIO_HTML = Path(
    r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\Memoria Activa del Pensamiento Complejo\Glosario - Pensamiento Complejo.html"
)
VAULT = Path(r"C:\Users\andre\OneDrive\Escritorio\CLAUDE\Conocimiento\ObsidianDemo")
DEST = VAULT / "Glosario"

# Mapeo de tradición → etiqueta corta para tags
TRADICION_TAG = {
    "morin": "morin",
    "autopoiesis": "autopoiesis",
    "cybernetics": "cibernetica",
    "embodied": "embodied",
    "predictive": "predictive",
    "iit": "iit",
    "panpsiquismo": "panpsiquismo",
    "termodinamica": "termodinamica",
    "proceso": "proceso",
    "social": "social",
}


def slug_to_title(slug: str, term: str) -> str:
    """Usa el term como título (es legible y único)."""
    return term


def safe_filename(term: str) -> str:
    """Elimina caracteres no permitidos en nombres de archivo Windows."""
    bad = '<>:"/\\|?*'
    out = "".join(c for c in term if c not in bad)
    return out.strip()


def html_to_md(html_src: str) -> str:
    """Convierte el HTML simple del campo explanation a markdown."""
    text = html_src
    # párrafos: cada <p>...</p> en una línea
    text = re.sub(r"<p[^>]*>", "", text)
    text = re.sub(r"</p>", "\n\n", text)
    # énfasis
    text = re.sub(r"<em[^>]*>", "*", text)
    text = re.sub(r"</em>", "*", text)
    text = re.sub(r"<strong[^>]*>", "**", text)
    text = re.sub(r"</strong>", "**", text)
    # enlaces internos del glosario: <a href="#slug">label</a> → [[label]]
    text = re.sub(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', r"[[\2]]", text)
    # cualquier otro <a>: extraer texto
    text = re.sub(r"<a[^>]*>([^<]+)</a>", r"\1", text)
    # listas básicas
    text = re.sub(r"<ul[^>]*>", "\n", text)
    text = re.sub(r"</ul>", "\n", text)
    text = re.sub(r"<li[^>]*>", "- ", text)
    text = re.sub(r"</li>", "\n", text)
    # br
    text = re.sub(r"<br\s*/?>", "\n", text)
    # cualquier otro tag: quitar
    text = re.sub(r"<[^>]+>", "", text)
    # entidades
    text = text.replace("&laquo;", "«").replace("&raquo;", "»")
    text = text.replace("&aacute;", "á").replace("&eacute;", "é")
    text = text.replace("&iacute;", "í").replace("&oacute;", "ó")
    text = text.replace("&uacute;", "ú").replace("&ntilde;", "ñ")
    text = text.replace("&Aacute;", "Á").replace("&Eacute;", "É")
    text = text.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&mdash;", "—").replace("&ndash;", "–")
    text = text.replace("&hellip;", "…").replace("&rsquo;", "'").replace("&lsquo;", "'")
    text = text.replace("&ldquo;", '"').replace("&rdquo;", '"')
    # red de seguridad: cualquier otra entidad HTML
    text = html.unescape(text)
    # múltiples saltos
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slug_to_term_map(entries):
    """Construye {slug: term} para resolver wikilinks de refs."""
    m = {}
    for e in entries:
        m[e["slug"]] = e["term"]
        # los slugs con prefijo morin: también tienen forma sin prefijo
        if e["slug"].startswith("morin:"):
            m[e["slug"].split(":", 1)[1]] = e["term"]
    return m


def render_note(e, slug_map):
    # Limpia entidades HTML y tags residuales en TODOS los campos string
    term = clean_meta(e["term"])
    title = slug_to_title(e["slug"], term)
    tradicion_raw = e.get("tradition", "")
    tradicion_tag = TRADICION_TAG.get(tradicion_raw, tradicion_raw or "otra")
    tradicion_label = clean_meta(e.get("tradition_label", ""))
    author = clean_meta(e.get("author", ""))
    work = clean_meta(e.get("work", ""))
    theme = clean_meta(e.get("theme", ""))
    volume = e.get("volume")
    source = clean_meta(e.get("source", ""))
    chip = clean_meta(e.get("chip_label", ""))
    essence = clean_meta(e.get("essence", ""))
    explanation_md = html_to_md(e.get("explanation", ""))
    quote = clean_meta(e.get("quote", ""))

    # refs → wikilinks usando ref_slugs para resolver el term real
    refs = e.get("refs", []) or []
    ref_slugs = e.get("ref_slugs", []) or []
    ref_links = []
    for label, sl in zip(refs, ref_slugs):
        label = clean_meta(label)
        target = slug_map.get(sl, label)
        target = clean_meta(target)
        if target == label:
            ref_links.append(f"[[{label}]]")
        else:
            ref_links.append(f"[[{target}|{label}]]")

    # frontmatter (todos los strings citados con yaml_quote para evitar romper YAML)
    fm_lines = [
        "---",
        "tipo: concepto",
        f"autor_origen: {yaml_quote(author)}",
        f"obra: {yaml_quote(work)}",
        f"tradicion: {tradicion_tag}",
        f"tradicion_label: {yaml_quote(tradicion_label)}",
    ]
    if theme:
        fm_lines.append(f"tema: {yaml_quote(theme)}")
    if volume:
        fm_lines.append(f"volumen: {volume}")
    if source:
        fm_lines.append(f"fuente: {yaml_quote(source)}")
    if chip:
        fm_lines.append(f"chip: {yaml_quote(chip)}")
    fm_lines += [
        "tags:",
        "  - tipo/concepto",
        f"  - tradicion/{tradicion_tag}",
        "  - origen/glosario",
        "---",
        "",
    ]

    body = [f"# {title}", "", f"> {essence}", "", "## Origen", ""]
    if author:
        body.append(f"- Autor: [[{author}]]")
    if work:
        body.append(f"- Obra: [[{work}]]")
    if source and source != work:
        body.append(f"- Fuente: {source}")
    body += ["", "## Explicación", "", explanation_md, ""]

    if quote:
        body += ["## Cita fundadora", "", f"> {quote}", ""]

    if ref_links:
        body += ["## Conceptos relacionados", ""]
        body += [f"- {lnk}" for lnk in ref_links]
        body += [""]

    return "\n".join(fm_lines + body)


def extract_data_array(html_text: str) -> list:
    # Buscamos const DATA = [ ... ];
    m = re.search(r"const\s+DATA\s*=\s*(\[.*?\]);", html_text, re.DOTALL)
    if not m:
        raise RuntimeError("No se encontró const DATA = [...]; en el HTML")
    raw = m.group(1)
    # El array ya está en JSON estricto (claves entre comillas), debería parsear directo.
    return json.loads(raw)


def main():
    html_text = GLOSARIO_HTML.read_text(encoding="utf-8")
    entries = extract_data_array(html_text)
    print(f"Entradas encontradas: {len(entries)}")

    DEST.mkdir(parents=True, exist_ok=True)
    slug_map = slug_to_term_map(entries)

    written = 0
    for e in entries:
        fname = safe_filename(e["term"]) + ".md"
        fpath = DEST / fname
        fpath.write_text(render_note(e, slug_map), encoding="utf-8")
        written += 1

    # Resumen por tradición
    from collections import Counter
    by_trad = Counter(e.get("tradition", "?") for e in entries)
    print(f"\nNotas escritas: {written} en {DEST}")
    print("\nPor tradición:")
    for trad, n in by_trad.most_common():
        print(f"  {trad}: {n}")


if __name__ == "__main__":
    main()
