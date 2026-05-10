# Export Gephi del corpus

Tres archivos generados por [`_scripts/export_gephi.py`](../../_scripts/export_gephi.py):

## `corpus.gexf`
Formato nativo de Gephi (XML). **Importarlo directamente** abre el grafo con todos los atributos, colores y tamaños ya configurados.

## `nodes.csv`
Tabla de nodos. 91 filas, 11 columnas:
- `Id` (slug del concepto)
- `Label` (nombre legible)
- `tradition`, `tradition_label`
- `author`, `work`, `year`, `theme`
- `indegree`, `outdegree`, `totaldegree`

## `edges.csv`
297 aristas no dirigidas. Columnas:
- `Source`, `Target` (slugs)
- `Type` = `Undirected`
- `Weight` (cuántas refs cruzadas comparten)

---

## Cómo abrir en Gephi

1. **Instalar Gephi** desde <https://gephi.org/users/download/> (Java incluido).
2. Abrir Gephi → **File → Open** → seleccionar `corpus.gexf`.
3. Aparece el grafo (probablemente desordenado al inicio).

## Workflow recomendado

### Paso 1 — Aplicar layout

En el panel **Layout** (abajo izquierda):
1. Elegir **"ForceAtlas 2"** del dropdown.
2. Configurar:
   - **Scaling**: `5-10`
   - **Stronger Gravity**: ✓
   - **Prevent Overlap**: ✓ (activar después de ~10s de ejecución)
3. Click en **Run**. Dejar correr 30-60 segundos. **Stop** cuando se estabilice.

### Paso 2 — Calcular métricas

Panel **Statistics** (derecha):
- **Modularity** → detecta comunidades (clusters automáticos por densidad de conexiones).
  - Resolution: `1.0`
  - Run.
- **Average Degree** → cuántas conexiones promedio.
- **Network Diameter** → calcula betweenness centrality (los nodos puente).
- **Eigenvector Centrality** → importancia estructural.

### Paso 3 — Colorear por modularidad

Panel **Appearance** (arriba izquierda):
- **Nodes** → **Color** → **Partition** → atributo `Modularity Class`.
- Click **Apply**.

Ahora el grafo muestra los **clusters reales** detectados algorítmicamente, no los que asumimos por tradición. Compáralos: ¿coinciden? ¿algunos conceptos pertenecen a una comunidad distinta de su tradición declarada?

### Paso 4 — Tamaño por centralidad

- **Nodes** → **Size** → **Ranking** → atributo `Betweenness Centrality`.
- Min: `5`, Max: `30`. Apply.

Los nodos más grandes son los **puentes intelectuales** del corpus.

### Paso 5 — Exportar imagen editorial

**File → Export → SVG/PNG/PDF file**:
- **Margin**: `5%`
- **Width**: `2000` px (alta resolución)
- **Include node labels**: ✓
- Output: imagen lista para imprimir o usar en presentación.

---

## Análisis sugeridos

| Pregunta | Métrica Gephi | Cómo leer |
|---|---|---|
| ¿Cuál es el concepto puente del corpus? | Betweenness Centrality | El más alto |
| ¿Qué clusters reales hay? | Modularity | Comunidades coloreadas |
| ¿Hay conceptos huérfanos? | Degree = 0 | Aparecen aislados |
| ¿Cuántos saltos entre dos ideas? | Path → Shortest Path | Distancia conceptual |
| ¿Qué tradición está más conectada al resto? | Promedio del betweenness por tradición | Filtra y promedia |

---

## Si quieres datos más limpios o filtrados

Edita el script [`_scripts/export_gephi.py`](../../_scripts/export_gephi.py):
- Filtrar solo conceptos con degree > N
- Excluir tradiciones específicas
- Cambiar tamaños base
- Pesar las aristas de forma distinta (por tema, por autor, etc.)

Re-ejecuta y reimporta en Gephi.
