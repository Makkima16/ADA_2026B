# Enfoque A — voraz con interacciones esenciales

Una interacción es **esencial** si es la única que cubre alguna categoría. Toda cobertura factible la
contiene, así que se elige primero. Con lo que falte se corre el paso del voraz base (mismo desempate:
menor índice j).

- Código: `esenciales.py` (`interacciones_esenciales`, `voraz_esenciales`).
- Costo: T(n, r) = O(n·r) + O(n·r·min(n, r)) = O(n·r·min(n, r)), igual que el voraz base.
- Garantía: se conserva H(d). |J| ≤ |E| + H(d)·(OPT − |E|) ≤ H(d)·OPT, con E el conjunto de esenciales.
- Límite: no ayuda cuando ninguna categoría es única (familia de cebos), y a veces empeora al voraz base
  porque comprometer antes una interacción cambia las elecciones siguientes.
