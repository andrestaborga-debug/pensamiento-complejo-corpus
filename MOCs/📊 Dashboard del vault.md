---
tipo: MOC
tags:
  - tipo/moc
---

# 📊 Dashboard del vault

> Esta nota usa **Dataview**. Si solo ves bloques de código grises, todavía no tienes el plugin activado. Ve a Settings → Community plugins → Browse → instala "Dataview" y actívalo.

---

## Inventario por tipo

```dataview
TABLE length(rows) as "Cantidad"
FROM "" AND !"_templates"
WHERE tipo
GROUP BY tipo
SORT length(rows) DESC
```

## Inventario por tradición

```dataview
TABLE length(rows) as "Cantidad"
FROM "" AND !"_templates"
WHERE tradicion
GROUP BY tradicion
SORT length(rows) DESC
```

## Conceptos del glosario por autor

```dataview
TABLE length(rows) as "Cantidad", rows.file.link as "Conceptos"
FROM "Glosario"
GROUP BY autor_origen
SORT length(rows) DESC
```

## Todos los conceptos curados (originales)

```dataview
TABLE autor_origen as "Autor", tradicion as "Tradición"
FROM "Conceptos"
SORT tradicion ASC, file.name ASC
```

## Obras curadas

```dataview
TABLE autor as "Autor", ano as "Año", tradicion as "Tradición"
FROM "Obras"
SORT ano ASC
```

## Ranking — conceptos más referenciados (los "puentes" intelectuales)

```dataview
TABLE WITHOUT ID 
  file.link as "Concepto",
  length(file.inlinks) as "Veces mencionado",
  tradicion as "Tradición"
FROM "Conceptos" OR "Glosario"
WHERE length(file.inlinks) > 0
SORT length(file.inlinks) DESC
LIMIT 20
```

## Notas por tradición

### Pensamiento complejo (Morin)

```dataview
LIST
FROM #tradicion/morin
SORT file.name ASC
```

### Autopoiesis (Maturana, Varela)

```dataview
LIST
FROM #tradicion/autopoiesis
SORT file.name ASC
```

### Termodinámica del no-equilibrio (Prigogine, Kauffman)

```dataview
LIST
FROM #tradicion/termodinamica
SORT file.name ASC
```

### Cognición encarnada (embodied)

```dataview
LIST
FROM #tradicion/embodied
SORT file.name ASC
```

### Cibernética de segundo orden

```dataview
LIST
FROM #tradicion/cibernetica
SORT file.name ASC
```

### Mente predictiva

```dataview
LIST
FROM #tradicion/predictive
SORT file.name ASC
```

### IIT (información integrada)

```dataview
LIST
FROM #tradicion/iit
SORT file.name ASC
```

### Panpsiquismo

```dataview
LIST
FROM #tradicion/panpsiquismo
SORT file.name ASC
```

### Filosofía del proceso (Whitehead)

```dataview
LIST
FROM #tradicion/proceso
SORT file.name ASC
```

### Complejidad social

```dataview
LIST
FROM #tradicion/social
SORT file.name ASC
```

---

## Cómo modificar estas consultas

Cada bloque empieza con ` ```dataview ` y termina con ` ``` `. Edítalos en modo edición (`Ctrl+E` para alternar). El lenguaje (DQL) tiene cuatro comandos principales:

- `LIST` — lista simple de notas
- `TABLE` — tabla con columnas
- `TASK` — extrae checkboxes `- [ ]`
- `CALENDAR` — vista de calendario por fecha

Filtros: `FROM "Carpeta"`, `FROM #tag`, `WHERE campo = "valor"`, `SORT campo DESC`, `GROUP BY campo`, `LIMIT N`.

> Documentación oficial: https://blacksmithgu.github.io/obsidian-dataview/
