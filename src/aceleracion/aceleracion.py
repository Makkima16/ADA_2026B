"""Parte 1: aceleración de la cadena bajo presupuesto (Mochila 0/1).

Problema: n etapas en serie con duración t_i, costo de aceleración c_i y
reducción d_i. Con presupuesto B se elige un subconjunto A a acelerar
para minimizar la duración total D(A) = sum(t) - sum(d_i, i en A).
Eso equivale a maximizar el ahorro sum(d_i) con sum(c_i) <= B.

Eficiencia: T(n, B) = O(n * B) en tiempo y espacio (pseudo-polinomial).

Variables: n = número de etapas, B = presupuesto, k = |A| (etapas aceleradas).
Al final del archivo está el costo de la DP y por qué sale ese costo.
"""


# Tope de memoria de la tabla DP: (n + 1) * (B + 1) celdas. Medido: en el peor caso
# cada celda ocupa ~38 bytes, así que 10 millones de celdas son ~380 MB.
MAX_CELDAS_TABLA = 10_000_000


class ErrorDeEntrada(ValueError):
    """La instancia no cumple las restricciones del problema."""


def verificar_tamano_tabla(n, B):
    """Avisa con un error claro si la tabla DP no cabe en memoria, antes de reservarla."""
    celdas = (n + 1) * (B + 1)
    if celdas > MAX_CELDAS_TABLA:
        raise ErrorDeEntrada(
            "la tabla DP tendría %d x %d = %d celdas y el límite es %d (≈ %d MB); "
            "el algoritmo es O(n·B) en memoria: con un B tan grande no cabe"
            % (n + 1, B + 1, celdas, MAX_CELDAS_TABLA, MAX_CELDAS_TABLA * 38 // 10**6))


def _entero_no_negativo(x):
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def validar_entrada(t, c, d, B):
    """Comprueba las restricciones de la guía: enteros no negativos y 0 <= d_i <= t_i.

    Lanza ErrorDeEntrada con un mensaje claro. Costo: O(n).
    """
    if not (len(t) == len(c) == len(d)):
        raise ErrorDeEntrada("t, c y d deben tener el mismo largo (n); llegaron %d, %d y %d"
                             % (len(t), len(c), len(d)))
    if not _entero_no_negativo(B):
        raise ErrorDeEntrada("el presupuesto B debe ser un entero >= 0 (llegó %r)" % (B,))
    for i, (ti, ci, di) in enumerate(zip(t, c, d), start=1):
        for nombre, valor in (("t", ti), ("c", ci), ("d", di)):
            if not _entero_no_negativo(valor):
                raise ErrorDeEntrada("etapa %d: %s_%d debe ser un entero >= 0 (llegó %r)"
                                     % (i, nombre, i, valor))
        if di > ti:
            raise ErrorDeEntrada("etapa %d: la reducción d_%d = %d supera la duración t_%d = %d"
                                 % (i, i, di, i, ti))


def llenar_tabla(c, d, B):
    """DP[i][b] = mayor ahorro usando solo las primeras i etapas y gastando a lo sumo b."""
    n = len(c)
    DP = [[0] * (B + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for b in range(B + 1):
            DP[i][b] = DP[i - 1][b]  # no acelerar la etapa i
            if c[i - 1] <= b:  # acelerarla, si cabe
                DP[i][b] = max(DP[i][b], DP[i - 1][b - c[i - 1]] + d[i - 1])
    return DP


def reconstruir(DP, c, B):
    """Recorre la tabla desde DP[n][B]; si el valor cambia, esa etapa se aceleró."""
    aceleradas = []
    b = B
    for i in range(len(c), 0, -1):
        if DP[i][b] != DP[i - 1][b]:
            aceleradas.append(i)
            b -= c[i - 1]
    aceleradas.reverse()
    return aceleradas


def resolver(t, c, d, B):
    """Resuelve la instancia de forma exacta con programación dinámica."""
    validar_entrada(t, c, d, B)
    verificar_tamano_tabla(len(c), B)
    DP = llenar_tabla(c, d, B)
    A = reconstruir(DP, c, B)
    ahorro = DP[len(c)][B]
    return {
        "aceleradas": A,
        "costo": sum(c[i - 1] for i in A),
        "ahorro": ahorro,
        "duracion_final": sum(t) - ahorro,
        "tabla": DP,
    }


# =============================================================================
# COSTO DE LA PROGRAMACIÓN DINÁMICA
# n = etapas, B = presupuesto, k = etapas aceleradas (0 <= k <= n).
#
# llenar_tabla -> Θ(n·B) en tiempo y en memoria, en el mejor, el peor y el promedio.
#   Por qué: la tabla tiene (n+1)·(B+1) celdas y los dos ciclos anidados la recorren
#   SIEMPRE completa (n vueltas del externo × B+1 del interno); el costo no depende de
#   los datos. Cada celda cuesta una cantidad constante de operaciones (copiar la celda
#   de arriba, comparar c_i <= b y, si cabe, un max y una suma). Lo único que varía con
#   los datos es esa constante: entre ≈ 12·n·B (ningún costo cabe) y ≈ 26·n·B (todos caben).
#
# reconstruir -> Θ(n)
#   Por qué: un solo ciclo de n vueltas, hacia atrás, con trabajo constante por vuelta
#   (el reverse final suma k <= n).
#
# validar_entrada -> Θ(n)
#   Por qué: un ciclo de n vueltas que revisa t_i, c_i, d_i con trabajo constante.
#
# resolver (todo) -> T(n, B) = Θ(n·B)
#   Por qué: suma validar (n) + llenar_tabla (n·B) + reconstruir (n); el término n·B
#   domina. Es pseudo-polinomial: B es un valor numérico que ocupa log₂ B bits, así que
#   n·B es exponencial en el tamaño real de la entrada.
#
# Memoria: Θ(n·B) por la tabla; de ahí el tope MAX_CELDAS_TABLA.
# =============================================================================


# =============================================================================
# INVARIANTES DE CICLO (inicialización / mantenimiento / finalización)
#
# llenar_tabla, ciclo `for i`:
#   Invariante: antes de la vuelta i, las filas 0..i-1 son correctas: DP[i'][b] es el mayor
#   ahorro con las primeras i' etapas y costo <= b.
#   - Inicio: solo existe la fila 0 (ceros): sin etapas no se ahorra nada.
#   - Mantenimiento: la fila i sale solo de la fila i-1, como el máximo entre no acelerar la
#     etapa i (DP[i-1][b]) y acelerarla si c_i <= b (d_i + DP[i-1][b-c_i]). Al leer la fila
#     i-1 y no la i, cada etapa se usa a lo sumo una vez (mochila 0/1).
#   - Fin: con i = n+1 las filas 0..n son correctas; DP[n][B] es el óptimo.
#
# reconstruir, ciclo `for i` hacia atrás:
#   Invariante: (ahorro de lo elegido entre i+1..n) + DP[i][b] = DP[n][B], con b = B - costo elegido.
#   - Inicio: nada elegido, b = B: 0 + DP[n][B].
#   - Mantenimiento: si DP[i][b] != DP[i-1][b], el óptimo viene de acelerar i: se agrega i y
#     b baja c_i, la suma no cambia. Si es igual, no hace falta acelerarla y no se cambia nada.
#   - Fin: con i = 0, DP[0][b] = 0, así que el ahorro elegido es DP[n][B] y b >= 0 (A factible).
#
# validar_entrada, ciclo `for i`:
#   Invariante: las etapas 1..i-1 ya revisadas cumplen enteros >= 0 y d <= t.
#   - Inicio: no hay etapas revisadas (cierto por vacío).
#   - Mantenimiento: si la etapa i falla se lanza ErrorDeEntrada; si cumple, 1..i cumplen.
#   - Fin: las n etapas cumplen: la instancia es válida.
# =============================================================================
