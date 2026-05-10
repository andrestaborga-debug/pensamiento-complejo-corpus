<%*
moment.locale("es");
const fecha = tp.date.now("YYYY-MM-DD");
const dia = tp.date.now("dddd", 0, tp.file.title, "YYYY-MM-DD");
const semana = tp.date.now("[Semana] w");
-%>
---
tipo: diario
fecha: <% fecha %>
dia: <% dia %>
tags:
  - tipo/diario
---

# <% fecha %> · <% dia %>

> <% semana %>

## ☀ Apertura

¿Con qué llega el día? Una frase, una imagen, una pregunta abierta.

## 📚 Lectura del día

Qué leí (libro, artículo, fragmento).

- **Fuente**: [[Obra]]
- **Idea que me detuvo**: 
- **Vínculo con un concepto del vault**: [[Concepto]]

## 💭 Pensamiento

Lo que se viene mientras camino, cocino, escucho.

## 🛠 Trabajo en talleres

- [ ] 

## 🔗 Conexiones del día

Notas que toqué hoy, ideas nuevas que conecto.

## 🌙 Cierre

Una línea sobre el día.

---

## Notas que enlazan a este día

```dataview
LIST FROM [[<% tp.file.title %>]]
```
