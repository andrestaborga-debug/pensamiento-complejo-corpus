---
tipo: MOC
tags:
  - tipo/moc
---

# 🔌 Plugins recomendados

Plugins de comunidad que llevan este vault de "demo" a una herramienta de trabajo real.

> Cómo instalar: ⚙ Settings → **Community plugins** → **Browse** → buscar el nombre → **Install** → **Enable**.

---

## Ya instalados ✅

| Plugin | Para qué sirve | Estado |
|---|---|---|
| **Dataview** (Michael Brenan) | Consultas tipo SQL/JS sobre el vault → tablas y listas dinámicas | ✅ |
| **Templater** (SilentVoid13) | Plantillas con prompts, suggester, JS y fechas | ✅ |

---

## Para escritura periódica

### Calendar (liamcain)

Pone un calendario en la barra lateral. Click en cualquier día abre/crea la nota diaria. Visualmente impecable, muy ligero.

### Periodic Notes (liamcain)

Configura notas **diarias / semanales / mensuales / trimestrales / anuales** con plantillas distintas para cada periodicidad. Combina perfecto con Templater.

> Uso típico: nota diaria con tres bloques — "qué leí hoy", "qué pensé", "qué pendientes me quedan", todo en `Daily/2026-05-10.md` autogenerado.

---

## Para mapas conceptuales y dibujo

### Excalidraw (zsviczian)

Convierte cualquier nota en un canvas tipo pizarra digital con cajas, flechas y formas a mano alzada. Soporta wikilinks **dentro** del dibujo: cada caja puede ser un link a una nota. Perfecto para mapas conceptuales en talleres.

> Para el [[🧭 Mapa de tradiciones]] sería ideal — uno dibuja las tres tradiciones como burbujas y los puentes ([[Autoorganización]], [[Estructura disipativa]]) como líneas.

---

## Para escritura larga

### Outliner (Vinzent)

Hace que las listas con bullets se comporten como en Workflowy o LogSeq: `Tab` indenta, `Shift+Tab` desindenta, `Ctrl+↑/↓` mueve el bullet con todos sus hijos. Para tomar notas estructuradas o esquematizar capítulos.

### Linter (Victor Tao)

Limpia formato automáticamente al guardar: espacios sobrantes, frontmatter desordenado, headers sin línea en blanco antes. Útil cuando importas contenido de fuera (como hicimos con el glosario).

---

## Para conexión con material existente

### Citations (hans)

Si usas **Zotero** o **BibTeX** para gestionar referencias, este plugin importa entradas como notas con frontmatter completo (DOI, autores, año, título). Encaja perfecto con tu vault: cada entrada del glosario ya tiene `obra` como wikilink.

### Auto Note Mover (farux)

Mueve notas a la carpeta correcta según sus tags. Por ejemplo: cualquier nota con `#tipo/concepto` → carpeta `Conceptos/`. Útil cuando creas notas rápido sin pensar en dónde van.

---

## Para visualización avanzada

### Graph Analysis (SkepticMystic)

Calcula métricas sobre el grafo del vault: nodos centrales, comunidades, conceptos huérfanos, distancias. Te dice **dónde está concentrado tu pensamiento** y dónde hay vacíos.

### Juggl (HEmile)

Grafo alternativo más potente que el built-in: filtros avanzados, layouts (jerárquico, circular, force-directed), exportar como imagen.

---

## Para sincronización

### Obsidian Sync (oficial, de pago)

Sincroniza el vault encriptado entre dispositivos. ~10 USD/mes.

### Remotely Save (open source, gratis)

Sincroniza con servicios externos: Google Drive, Dropbox, OneDrive, S3, WebDAV. Gratis pero más manual.

> **Tip alternativo gratis**: como tu vault está en `OneDrive`, ya estás sincronizando entre dispositivos. Solo cuida no editar la misma nota desde dos lados al mismo tiempo.

---

## Mi top 3 si tuvieras que elegir

1. **Periodic Notes + Calendar** — para diario reflexivo del taller.
2. **Excalidraw** — para los mapas conceptuales de tus talleres asincrónicos sobre Morin.
3. **Linter** — para mantener formato limpio cuando importes más contenido.
