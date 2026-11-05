# Enfoque C — voraz por rareza

Cada categoría pendiente vale 1/f(c), donde f(c) es cuántas interacciones la cubren: las raras valen más.
En cada paso se elige la interacción de mayor puntaje (suma de esos valores sobre lo que aún falta).
Desempates fijos: más categorías nuevas y, después, menor índice j.

- Código: `rareza.py` (`frecuencias`, `paso_rareza`, `voraz_rareza`). El paso guarda los puntajes (`PasoRareza`).
- Costo: T(n, r) = O(Σ|S_j|) + min(n, r)·O(n·r) = O(n·r·min(n, r)), igual que el voraz base.
- Garantía: H(d) **no** se demuestra; solo hay evidencia empírica (`comparacion/`).
- Límite: si todas las categorías son igual de raras (por ejemplo, la familia de cebos del caso 05), su puntaje es
  proporcional a la cantidad de categorías y se comporta como el voraz base.
- No reemplaza al voraz base.
