"""Enfoque aparte (Parte 1): programación dinámica por valor (por ahorro).

NO reemplaza a la DP base de `aceleracion.aceleracion.resolver`: es un algoritmo
aparte, exacto como ella, que indexa la tabla por otro parámetro.

Idea: la DP base indexa por presupuesto b y guarda el mayor ahorro. Esta indexa por
ahorro v y guarda el menor costo:

    C[i][v] = menor costo para lograr exactamente un ahorro v usando solo las
              primeras i etapas (INF si no se puede o si el costo pasa de B).

    C[0][0] = 0,  C[0][v] = INF  para v > 0
    C[i][v] = mín( C[i-1][v] ,  c_i + C[i-1][v - d_i] )     (segunda opción solo si v >= d_i)

Todo valor mayor que B se guarda como INF (= B + 1). El ahorro óptimo es el mayor v
con C[n][v] <= B. La solución se reconstruye hacia atrás desde ese v.

Notación del proyecto: n, B, t_i, c_i, d_i, A y D = Σ d_i (ahorro máximo posible).

Al final del archivo están el costo y por qué sale, y los invariantes de ciclo.
"""

from typing import Dict, List, Sequence

from aceleracion.aceleracion import ErrorDeEntrada, MAX_CELDAS_TABLA, validar_entrada


def verificar_tamano_tabla_valor(n: int, D: int) -> None:
    """Avisa con un error claro si la tabla por valor no cabe en memoria, antes de reservarla."""
    celdas = (n + 1) * (D + 1)
    if celdas > MAX_CELDAS_TABLA:
        raise ErrorDeEntrada(
            "la tabla por valor tendría %d x %d = %d celdas y el límite es %d; "
            "el algoritmo es O(n·D) en memoria, con D = suma de los ahorros: con un D tan grande no cabe"
            % (n + 1, D + 1, celdas, MAX_CELDAS_TABLA))


def llenar_tabla_valor(c: Sequence[int], d: Sequence[int], B: int) -> List[List[int]]:
    """C[i][v] = menor costo para lograr exactamente el ahorro v con las primeras i etapas (INF = B + 1)."""
    n = len(c)
    D = sum(d)
    INF = B + 1
    C = [[INF] * (D + 1) for _ in range(n + 1)]
    C[0][0] = 0
    for i in range(1, n + 1):
        for v in range(D + 1):
            C[i][v] = C[i - 1][v]                           # no acelerar la etapa i
            if v >= d[i - 1]:
                candidato = C[i - 1][v - d[i - 1]] + c[i - 1]   # acelerarla
                if candidato < C[i][v] and candidato <= B:
                    C[i][v] = candidato
    return C


def mejor_ahorro(C: Sequence[Sequence[int]], B: int) -> int:
    """El mayor ahorro v cuyo costo mínimo cabe en el presupuesto."""
    v = len(C[-1]) - 1
    while C[-1][v] > B:
        v -= 1
    return v


def reconstruir_valor(C: Sequence[Sequence[int]], d: Sequence[int], ahorro: int) -> List[int]:
    """Recorre la tabla desde C[n][ahorro]; si el valor cambia respecto de la fila anterior, esa etapa se aceleró."""
    aceleradas = []
    v = ahorro
    for i in range(len(d), 0, -1):
        if C[i][v] != C[i - 1][v]:
            aceleradas.append(i)
            v -= d[i - 1]
    aceleradas.reverse()
    return aceleradas


def resolver_valor(t: Sequence[int], c: Sequence[int], d: Sequence[int], B: int) -> Dict:
    """Resuelve la instancia de forma exacta con la DP por valor. Mismas claves que `resolver` de la DP base."""
    validar_entrada(t, c, d, B)
    verificar_tamano_tabla_valor(len(c), sum(d))
    C = llenar_tabla_valor(c, d, B)
    ahorro = mejor_ahorro(C, B)
    A = reconstruir_valor(C, d, ahorro)
    return {
        "aceleradas": A,
        "costo": sum(c[i - 1] for i in A),
        "ahorro": ahorro,
        "duracion_final": sum(t) - ahorro,
        "tabla": C,
    }


# =============================================================================
# COSTO DE LA DP POR VALOR
# n = etapas, B = presupuesto, D = Σ d_i (ahorro máximo), k = etapas aceleradas.
#
# llenar_tabla_valor -> Θ(n·D) en tiempo y en memoria, en el mejor, el peor y el promedio.
#   Por qué: la tabla tiene (n+1)·(D+1) celdas y los dos ciclos la recorren SIEMPRE completa;
#   cada celda cuesta una cantidad constante de operaciones. No depende de B.
#
# mejor_ahorro -> O(D): un recorrido de la última fila.
# reconstruir_valor -> Θ(n): un solo ciclo de n vueltas hacia atrás.
#
# resolver_valor (todo) -> T(n, D) = Θ(n·D)
#   Por qué: validar (n) + llenar (n·D) + reconstruir (n); domina n·D.
#
# Frente a la DP base, Θ(n·B): conviene esta cuando D < B (la tabla por valor tiene menos
# columnas) y la base cuando B < D. Entre las dos se paga Θ(n·mín(B, D)). Es exacta, pero
# sigue siendo pseudo-polinomial: D se escribe con log₂ D bits.
# =============================================================================


# =============================================================================
# INVARIANTES DE CICLO (inicialización / mantenimiento / finalización)
#
# llenar_tabla_valor, ciclo `for i`:
#   Invariante: antes de la vuelta i, las filas 0..i-1 son correctas: C[i'][v] es el menor
#   costo (<= B) para lograr exactamente el ahorro v con las primeras i' etapas, o INF.
#   - Inicio: la fila 0 solo logra el ahorro 0, con costo 0.
#   - Mantenimiento: la fila i sale solo de la fila i-1, como el mínimo entre no acelerar la
#     etapa i (C[i-1][v]) y acelerarla si v >= d_i (c_i + C[i-1][v-d_i]); lo que pase de B se
#     descarta. Al leer la fila i-1, cada etapa se usa a lo sumo una vez.
#   - Fin: las filas 0..n son correctas; el mayor v con C[n][v] <= B es el óptimo.
#
# reconstruir_valor, ciclo `for i` hacia atrás:
#   Invariante: C[i][v] es el costo mínimo de lograr el ahorro v que falta con las etapas 1..i,
#   y las etapas ya elegidas (i+1..n) logran ahorro - v.
#   - Inicio: nada elegido, v = ahorro.
#   - Mantenimiento: si C[i][v] != C[i-1][v], el mínimo viene de acelerar i: se agrega y v baja d_i.
#     Si es igual, no hace falta acelerarla.
#   - Fin: con i = 0 queda v = 0, así que lo elegido logra exactamente el ahorro, con costo C[n][ahorro] <= B.
# =============================================================================
