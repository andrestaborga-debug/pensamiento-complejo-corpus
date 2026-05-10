---
tipo: MOC
creado: 2026-05-10
---

# 🗺️ Inicio del vault — Pensamiento complejo

Este es el **mapa raíz**. El vault tiene **dos capas**: el demo curado (autores, obras, conceptos clave hechos a mano) y el **glosario importado** (91 entradas extraídas del HTML *Glosario - Pensamiento Complejo*).

## Tipos de nota y carpetas

- **Autores/** → 4 notas biográficas mínimas curadas a mano
- **Obras/** → 3 libros con metadatos
- **Conceptos/** → 2 conceptos del demo original (Bucle recursivo, Autoorganización) — los demás se importaron del glosario
- **Glosario/** → **91 entradas** importadas masivamente (el corpus principal)
- **MOCs/** → mapas temáticos
- **_templates/** → plantillas estáticas y Templater
- **_scripts/** → scripts Python (importador, etc.)

## Mapas temáticos

- [[🧭 Mapa de tradiciones]] — agrupa autores y conceptos por escuela intelectual (con timeline + genealogía Mermaid)
- [[📊 Dashboard del vault]] — vistas dinámicas con Dataview
- [[🔌 Plugins recomendados]] — qué instalar para el siguiente nivel
- [[🌐 Visualizaciones Mermaid]] — catálogo de diagramas embebidos (timeline, mindmap, flowchart, etc.)

## Visualizaciones HTML (interactivas)

- [`Visualizaciones/corpus.html`](Visualizaciones/corpus.html) — Timeline scatter (91 conceptos × año × tradición) + chord diagram (14 autores conectados por conceptos compartidos). Autocontenido, abre con doble clic en cualquier navegador.

## Autores curados

- [[Edgar Morin]]
- [[Humberto Maturana]]
- [[Francisco Varela]]
- [[Ilya Prigogine]]

## Obras curadas

- [[El Método I - La naturaleza de la Naturaleza]]
- [[El árbol del conocimiento]]
- [[At Home in the Universe]]

> *La nueva alianza* (Prigogine & Stengers) aparece en el Glosario como concepto.

## Conceptos curados (originales)

- [[Bucle recursivo]]
- [[Autoorganización]]

> Los demás conceptos (Principio dialógico, Principio hologramático, Sistema abierto, Autopoiesis, Complejidad, Deriva natural, Estructura disipativa…) viven en el [[#Glosario importado — atajos|glosario importado]] con citas y refs cruzadas más completas.

## Glosario importado — atajos

```dataview
TABLE WITHOUT ID
  file.link as "Concepto",
  autor_origen as "Autor",
  tradicion as "Tradición"
FROM "Glosario"
SORT file.name ASC
LIMIT 15
```

Para ver las 91, abre [[📊 Dashboard del vault]].

---

## Cómo usar este vault

1. **Grafo con colores**: `Ctrl+G`. Cada tradición tiene su color (configurado en `.obsidian/graph.json`). Vas a ver clusters: rojo (Morin), verde (autopoiesis), dorado (termodinámica), etc.
2. **Backlinks**: panel derecho → "Linked mentions" en cualquier nota.
3. **Navegación**: clic en `[[wikilink]]`; `Ctrl+clic` para abrir en panel nuevo.
4. **Búsqueda por tag**: `Ctrl+Shift+F` → `tag:#tradicion/morin` o `tag:#origen/glosario`.
5. **Plantillas dinámicas**: `Ctrl+P` → "Templater: Open Insert Template modal".

> Tip: empieza por [[🧭 Mapa de tradiciones]] o [[📊 Dashboard del vault]] para ver la totalidad. Para entrar en profundidad, abre cualquier entrada del Glosario y sigue los `[[Conceptos relacionados]]` al final.


Sauna