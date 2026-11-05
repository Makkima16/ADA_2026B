# Enfoques sobre el voraz (Parte 2)

Algoritmos voraces **aparte** del voraz base (`src/auditoria/auditoria.py`, función `voraz`), que sigue siendo la
solución de la entrega y no se modifica. Sirven para estudiar qué pasa si el voraz "mira" un poco más
allá del paso actual y para medir qué tan lejos queda del óptimo.

| Carpeta | Qué es | Costo T(n, r) | Garantía |
| --- | --- | --- | --- |
| `esenciales/` (A) | Voraz que elige primero las interacciones que son la única que cubre alguna categoría | O(n·r·min(n, r)) (igual al voraz base) | Conserva H(d) (con prueba) |
| `vision_futuro/` (B) | **Parejas**: voraz que evalúa pares de interacciones juntas (profundidad 2). No es programación dinámica | O(n²·r·min(n, r)) (un factor n más) | No demostrada; solo medida |
| `rareza/` (C) | **Rareza**: cada categoría pendiente vale 1/(cuántas interacciones la cubren); se elige la de mayor puntaje | O(n·r·min(n, r)) (igual al voraz base) | No demostrada; solo medida |
| `combinado/` (D) | **Todo junto**: primero las esenciales y, con lo que falte, parejas valoradas por rareza | O(n²·r·min(n, r)) (un factor n más) | No demostrada; solo medida |
| `comparacion/` | Experimentos reproducibles (semilla fija) que comparan todo contra el óptimo | — | — |

Las combinaciones intermedias (esenciales + rareza, esenciales + parejas, rareza + parejas) no son enfoques aparte: se miden en la tabla de contribución de `comparacion/ablacion.py`.

Notación única del proyecto: n, r, S_j, J. Las pruebas están en `tests/test_enfoques.py`.

Los resultados medidos y el análisis completo (cuándo mejora, cuándo empeora, cuánto sube el costo y por
qué se justifica) están en `docs/` (documento "Enfoques sobre el voraz").

Se ejecuta desde la raíz del proyecto:

```
python3 src/auditoria/enfoques/comparacion/experimento.py --instancias 3000 --semilla 2026
```
