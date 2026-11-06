# Enfoque — DP por valor (Parte 1)

Programación dinámica **exacta** que indexa la tabla por el **ahorro** v en vez de por el presupuesto b. No reemplaza a la
DP base (`src/aceleracion/aceleracion.py`), que sigue siendo la solución de la entrega.

- **Tabla:** `C[i][v]` = menor costo para lograr exactamente un ahorro v con las primeras i etapas; INF (= B + 1) si no
  se puede o si el costo pasa de B. Recurrencia: `C[i][v] = mín( C[i-1][v] , c_i + C[i-1][v-d_i] )` (la segunda opción solo
  si v ≥ d_i). El ahorro óptimo es el mayor v con `C[n][v] ≤ B`; la solución se reconstruye hacia atrás desde ahí.
- **Código:** `dp_por_valor.py` (algoritmo, costo e invariantes al final), `resolver.py` (`resolver_caso_valor`, mismo
  `ResultadoCaso` que la base; en `tabla` va `C[i][v]`), `traza.py` (`formatear_caso_valor`).
- **Costo:** T(n, D) = Θ(n·D) en tiempo y en memoria, con D = Σ d_i. No depende de B. La base cuesta Θ(n·B).
- **Cuándo gana:** la de valor si D < B; la base si B < D. Entre las dos se paga Θ(n·mín(B, D)). Sigue siendo
  pseudo-polinomial (D ocupa log₂ D bits).
- **Elección automática:** `../seleccion.py` compara las celdas de las dos tablas, (n+1)·(B+1) contra (n+1)·(D+1), y
  elige la menor (con empate, la base). Si ni una ni otra cabe en `MAX_CELDAS_TABLA` (10 millones de celdas), da
  `ErrorDeEntrada` con los dos tamaños. El visor local deja elegir cuál mostrar y señala cuál conviene.
- **Límites:**
  - El criterio compara celdas, no tiempo: cerca del cruce las constantes pesan (con B ≈ D la de valor salió más rápida
    aunque tenía más celdas).
  - Con B y D enormes no hay algoritmo exacto que sirva; solo aproximar (FPTAS), que no está implementado.
  - Ante empates de costo, la solución puede diferir de la de la base (mismo ahorro, distinto conjunto A); el costo de la
    solución de este enfoque es el mínimo para ese ahorro.
- **Pruebas:** `tests/test_enfoque_dp_por_valor.py` (contra la DP base y la fuerza bruta en instancias con semilla fija,
  casos borde, elección y error de memoria).
- **Experimento:** `python3 src/aceleracion/enfoques/dp_por_valor/experimento.py [--semilla S]` (desde la raíz) muestra
  dónde se cruzan las dos.
