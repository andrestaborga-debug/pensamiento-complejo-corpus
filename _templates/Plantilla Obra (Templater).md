<%*
const autor = await tp.system.prompt("Autor (separar varios por coma)");
const ano = await tp.system.prompt("Año de publicación original");
const idioma = await tp.system.suggester(
  ["español", "francés", "inglés", "alemán", "italiano", "portugués"],
  ["español", "francés", "inglés", "alemán", "italiano", "portugués"]
);
const formato = await tp.system.suggester(
  ["EPUB", "PDF", "EPUB + PDF", "papel"],
  ["EPUB", "PDF", "EPUB + PDF", "papel"]
);
const tradicion = await tp.system.suggester(
  ["pensamiento complejo", "autopoiesis", "termodinámica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"],
  ["morin", "autopoiesis", "termodinamica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"]
);
-%>
---
tipo: obra
autor: <% autor %>
ano: <% ano %>
idioma_original: <% idioma %>
formato_local: <% formato %>
tradicion: <% tradicion %>
creado: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - tipo/obra
  - tradicion/<% tradicion %>
---

# <% tp.file.title %>

> Una línea de qué propone el libro.

## Autor

- [[<% autor %>]]

## Tesis central

Párrafo breve con la idea fundamental.

## Conceptos clave que desarrolla

- [[Concepto 1]]

## Estructura

Síntesis de capítulos o partes (opcional).

## Citas

> "Cita literal."  
> — Cap. X, p. XX

## Conexiones

- Conversa con [[Otra obra]] en el punto de [[Concepto compartido]].
