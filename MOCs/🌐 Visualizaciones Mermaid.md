---
tipo: MOC
tags:
  - tipo/moc
  - tipo/showcase
---

# 🌐 Visualizaciones Mermaid

> Catálogo de diagramas embebidos directamente en notas. Mermaid se renderiza nativamente en Obsidian sin plugins. Todo lo de aquí lo puedes copiar y pegar a tus propias notas.

## ¿Cuándo usar Mermaid?

- Cuando quieres una **visualización inline** que viaje con la nota.
- Para diagramas **versionables** en git (es texto plano, no binario).
- Cuando quieres que se rendericen en **Quartz** publicado, en **GitHub**, en cualquier viewer Markdown — sin instalar nada.

## ¿Cuándo NO usar Mermaid?

- Si necesitas dibujo libre con curvas o texto manuscrito → **Excalidraw**.
- Si necesitas layout espacial flexible para un taller → **Canvas**.
- Si necesitas grafo dinámico de cientos de nodos → **Graph view + plugins**.

---

## 1. Timeline — Cronología del pensamiento complejo

```mermaid
timeline
    title Cronología del pensamiento complejo
    1929 : Whitehead — Process and Reality
    1948 : Wiener — Cibernética
    1969 : Prigogine — Estructuras disipativas (Premio Nobel 1977)
    1972 : Maturana & Varela — Autopoiesis
    1977 : Morin — El Método I
    1979 : Prigogine & Stengers — La nueva alianza
    1984 : Maturana & Varela — El árbol del conocimiento
    1991 : Varela, Thompson, Rosch — The Embodied Mind
    1995 : Kauffman — At Home in the Universe
    2004 : Tononi — Información integrada (IIT)
    2009 : Friston — Free Energy Principle
    2013 : Andy Clark — Predictive brains
```

---

## 2. Mindmap — Pensamiento complejo (Morin)

```mermaid
mindmap
  root((Pensamiento complejo))
    Principios
      Dialógico
        Orden + desorden
      Hologramático
        Parte en todo
        Todo en parte
      Recursivo
        Productos producen al productor
    Anclaje
      Termodinámica
        Estructuras disipativas
      Cibernética
        Causalidad circular
      Sistémica
        Sistema abierto
    Aplicaciones
      Educación
      Reforma del pensamiento
      Antropolítica
      Tierra-Patria
```

---

## 3. Flowchart — Lógica de la autopoiesis

```mermaid
flowchart TD
    A[Sistema vivo] --> B{¿Produce sus propios componentes?}
    B -->|Sí| C[Autopoiético]
    B -->|No| D[Allopoiético]
    C --> E[Clausura organizacional]
    E --> F[Acoplamiento estructural<br/>con el medio]
    F --> G[Deriva natural]
    G --> H[Cognición = vivir]
    H --> I[Todo conocer es hacer]
    
    style C fill:#4a6b3c,stroke:#2d4422,color:#fff
    style I fill:#7a2e2e,stroke:#5b1f1f,color:#fff
```

---

## 4. Flowchart — Los tres principios de la complejidad

```mermaid
flowchart LR
    C[Complejidad<br/>moriniana]
    C --> D[Dialógico]
    C --> H[Hologramático]
    C --> R[Recursivo]
    
    D -->|"orden + desorden<br/>conviven"| EX1[Vida + muerte<br/>en lo viviente]
    H -->|"todo↔parte"| EX2[Genoma en cada<br/>célula del cuerpo]
    R -->|"causa↔efecto"| EX3[Individuos producen<br/>la sociedad que los produce]
    
    style C fill:#7a2e2e,stroke:#5b1f1f,color:#fff
    style D fill:#b8851f,stroke:#8c6418,color:#fff
    style H fill:#b8851f,stroke:#8c6418,color:#fff
    style R fill:#b8851f,stroke:#8c6418,color:#fff
```

---

## 5. Graph — Linaje intelectual (qué autor influye en quién)

```mermaid
graph LR
    W[Whitehead<br/>1929] -.proceso.-> M[Morin]
    P[Prigogine<br/>1977 Nobel] -->|estructuras disipativas| M
    W2[Wiener<br/>1948] -->|cibernética| F[von Foerster<br/>2do orden]
    F --> MV[Maturana & Varela<br/>autopoiesis]
    MV --> V[Varela<br/>enacción]
    V --> CL[Clark<br/>predictive]
    V --> T[Tononi<br/>IIT]
    M -.-> S[Sotolongo & Delgado<br/>complejidad social]
    P --> K[Kauffman<br/>orden gratis]
    
    style M fill:#7a2e2e,stroke:#5b1f1f,color:#fff
    style MV fill:#4a6b3c,stroke:#2d4422,color:#fff
    style P fill:#b8851f,stroke:#8c6418,color:#fff
```

---

## 6. Quadrant — Posicionamiento epistemológico

```mermaid
quadrantChart
    title Posicionamiento de tradiciones
    x-axis "Reduccionista" --> "Holista"
    y-axis "Mecanicista" --> "Procesual"
    quadrant-1 Procesual-Holista
    quadrant-2 Procesual-Reduccionista
    quadrant-3 Mecanicista-Reduccionista
    quadrant-4 Mecanicista-Holista
    "Morin": [0.85, 0.85]
    "Maturana-Varela": [0.75, 0.80]
    "Prigogine": [0.60, 0.90]
    "Whitehead": [0.70, 0.95]
    "IIT (Tononi)": [0.40, 0.50]
    "Friston (FEP)": [0.45, 0.65]
    "Cibernética 1er orden": [0.30, 0.40]
```

---

## 7. Sequence — Cómo emerge una estructura disipativa

```mermaid
sequenceDiagram
    participant E as Entorno
    participant S as Sistema
    participant D as Disipación
    
    E->>S: Flujo de energía/materia
    Note over S: Estado lejos del equilibrio
    S->>S: Fluctuaciones aleatorias
    S->>D: Exporta entropía
    Note over S: Patrón estable emerge
    S-->>E: Forma macroscópica<br/>(remolino, célula de Bénard, vida)
    Note over E,D: Orden por fluctuaciones
```

---

## 8. Class — Estructura conceptual de un sistema autopoiético

```mermaid
classDiagram
    class SistemaAutopoietico {
        +componentes
        +red_de_procesos
        +membrana
        +producir_componentes()
        +mantener_organizacion()
    }
    class SistemaVivo {
        +metabolismo
        +reproducir()
    }
    class Cognicion {
        +acoplamiento_estructural
        +deriva_natural
        +conocer()
    }
    SistemaAutopoietico <|-- SistemaVivo
    SistemaVivo *-- Cognicion : indistinguibles
```

---

## Cómo embedear en tus propias notas

Cualquier nota markdown:

````markdown
```mermaid
mindmap
  root((Mi tema))
    Idea 1
      Detalle
    Idea 2
```
````

## Recursos

- Sintaxis completa: <https://mermaid.js.org/intro/>
- Editor en vivo: <https://mermaid.live/>
