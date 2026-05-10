<%*
const nacimiento = await tp.system.prompt("Año de nacimiento");
const muerte = await tp.system.prompt("Año de muerte (vacío si vivo)");
const nacionalidad = await tp.system.prompt("Nacionalidad");
const tradicion = await tp.system.suggester(
  ["pensamiento complejo", "autopoiesis", "termodinámica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"],
  ["morin", "autopoiesis", "termodinamica", "embodied", "predictive", "iit", "panpsiquismo", "proceso", "social"]
);
-%>
---
tipo: autor
nacimiento: <% nacimiento %>
muerte: <% muerte %>
nacionalidad: <% nacionalidad %>
tradicion: <% tradicion %>
creado: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - tipo/autor
  - tradicion/<% tradicion %>
---

# <% tp.file.title %>

> Una línea que capture su aporte central.

## Contexto

Breve párrafo: dónde y cuándo trabajó, qué buscaba responder.

## Obras en este vault

- [[Obra 1]]

## Conceptos que introduce o desarrolla

- [[Concepto 1]]

## Diálogos con

- [[Autor X]] — en qué punto se cruzan

## Citas representativas

> "Cita literal."  
> — *Obra*, p. XX
