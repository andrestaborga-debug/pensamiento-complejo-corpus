<%*
const autor = await tp.system.prompt("¿Quién es el autor de origen?");
const tradicion = await tp.system.suggester(
  ["pensamiento complejo", "autopoiesis", "termodinámica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"],
  ["morin", "autopoiesis", "termodinamica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"]
);
const obra = await tp.system.prompt("¿En qué obra principal aparece?");
-%>
---
tipo: concepto
autor_origen: <% autor %>
tradicion: <% tradicion %>
sinonimos: 
creado: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - tipo/concepto
  - tradicion/<% tradicion %>
---

# <% tp.file.title %>

> Definición esencial en una línea.

## Origen

- Autor: [[<% autor %>]]
- Obra: [[<% obra %>]]

## Explicación

Dos o tres párrafos en lenguaje accesible.

## Cita fundadora

> "Cita literal del autor."  
> — *Obra*, p. XX

## Cómo se relaciona con otros conceptos

- **Implica a** [[Concepto A]] — porque…
- **Se contrapone a** [[Concepto B]] — porque…
- **Complementa a** [[Concepto C]] — porque…

## Aplicaciones / ejemplos

Ejemplo concreto que ayude a fijar la idea.
