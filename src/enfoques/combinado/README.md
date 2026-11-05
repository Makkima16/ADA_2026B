# Enfoque D — todo junto: esenciales + rareza + parejas

Junta los tres ingredientes: primero las interacciones **esenciales** (la única que cubre alguna categoría)
y, con lo que falte, el paso con **parejas** de interacciones, donde cada pareja se valora por la **rareza**
de lo que cubre (cada categoría pendiente vale 1/f(c)).

- Código: `combinado.py` (`paso_parejas_rareza`, `voraz_combinado`). El paso guarda el par ganador y los puntajes (`PasoCombinado`).
- Costo: T(n, r) = O(n²·r·min(n, r)), un factor n más que el voraz base. Exacto:
  T = n·r + Σ|S_j| + e·r + (k − e)·(n + n(n−1)/2)·r.
- Garantía: H(d) **no** se demuestra; solo hay evidencia empírica (`comparacion/`).
- No reemplaza al voraz base. Las combinaciones intermedias (esenciales + rareza, esenciales + parejas,
  rareza + parejas) no son enfoques aparte: se miden en la tabla de contribución de `comparacion/ablacion.py`.
