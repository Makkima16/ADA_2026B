# Enfoques sobre la DP (Parte 1)

Algoritmos **aparte** de la DP base (`src/aceleracion/aceleracion.py`, función `resolver`), que sigue siendo la solución
de la entrega y no se modifica. A diferencia de los enfoques del voraz (Parte 2), que intentan acercarse al óptimo, estos
son **exactos**: se distinguen por cuánto cuestan según el tipo de instancia.

| Carpeta / archivo | Qué es | Costo | ¿Exacto? |
| --- | --- | --- | --- |
| (DP base, `aceleracion.py`) | Tabla por presupuesto b: mayor ahorro | Θ(n·B) | Sí |
| `dp_por_valor/` | Tabla por ahorro v: menor costo | Θ(n·D), D = Σ d_i | Sí |
| `seleccion.py` | Elige la tabla con menos celdas; error si ninguna cabe | O(n) para decidir | — |

Notación única del proyecto: n, B, t_i, c_i, d_i, A y D = Σ d_i. Pruebas: `tests/test_enfoque_dp_por_valor.py`.
