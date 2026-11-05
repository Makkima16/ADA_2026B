"""Parte 1: aceleración de la cadena bajo presupuesto (Mochila 0/1).

Problema: n etapas en serie con duración t_i, costo de aceleración c_i y
reducción d_i. Con presupuesto B se elige un subconjunto A a acelerar
para minimizar la duración total D(A) = sum(t) - sum(d_i, i en A).
Eso equivale a maximizar el ahorro sum(d_i) con sum(c_i) <= B.

Eficiencia: T(n, B) = O(n * B) en tiempo y espacio (pseudo-polinomial).

COSTO POR LÍNEA — cómo se cuenta (modelo RAM del curso; la misma regla en todos los
archivos de la Parte 1)
--------------------------------------------------------------------------------
Cada comentario `# costo: OE × veces` dice cuánto cuesta la línea:

  OE (operaciones elementales por ejecución): cuesta 1 una asignación, una
      comparación, una suma, resta, multiplicación o desplazamiento de bits, un
      and/or/not, leer o escribir una posición de una lista (A[i]), un return y
      llamar a una función (len, max, sum, append...). El cuerpo de la función
      llamada se analiza aparte (por ejemplo, sum(t) cuesta 1 por la llamada y n
      por recorrer la lista).
  veces: cuántas veces se ejecuta la línea, en términos de n (y B, k, q).

Cómo se obtienen las "veces":
  - Línea suelta (fuera de ciclos): 1 vez.
  - `for` de m vueltas: la CABECERA se ejecuta m + 1 veces (una más que el cuerpo: la
    evaluación que sale del ciclo) y vale 3 OE (asignar la variable, hacerla avanzar y
    comparar): 3 × (m + 1). Escribir `range`, `zip`, `enumerate` o desempaquetar varias
    variables en la cabecera no suma OE: sigue siendo la misma cabecera de 3 OE. El
    CUERPO se ejecuta m veces.
  - `for` dentro de otro `for`: el cuerpo del interno se ejecuta (vueltas del externo) ×
    (vueltas del interno) veces; su cabecera, (vueltas del externo) × (vueltas internas + 1).
  - `if` dentro de un `for`: la condición se evalúa en todas las vueltas, o sea las mismas
    veces que el cuerpo del `for`. Lo que está DENTRO del `if` solo se ejecuta cuando la
    condición es cierta: entre 0 veces (mejor caso) y todas las vueltas (peor caso). La
    rama `else` se ejecuta las vueltas restantes.
  - `while`: la condición se evalúa (vueltas + 1) veces; cuántas vueltas hay depende de
    cómo cambian las variables de la condición (por ejemplo, j <- j*2 da log₂(n) + 1
    vueltas). En estos archivos no hay ningún `while`.
  - Una línea que solo se ejecuta si hay un error (`raise`) termina el programa: no cuenta
    en el caso normal.

Después de las líneas, al final de cada función, se arma T(n) como en el curso:
suma de costos -> expansión -> agrupación -> orden de crecimiento.

Variables: n = número de etapas, B = presupuesto, k = |A| (etapas aceleradas),
q = veces que la etapa cabe en el presupuesto dentro de la tabla.
Al final del archivo están el resumen del costo (mejor caso, peor y promedio) y los
invariantes de ciclo (correctitud).
"""


# Tope de memoria de la tabla DP: (n + 1) * (B + 1) celdas. Medido: en el peor caso
# cada celda ocupa ~38 bytes, así que 10 millones de celdas son ~380 MB.
MAX_CELDAS_TABLA = 10_000_000                         # costo: 1 × 1 (una sola vez, al importar)


class ErrorDeEntrada(ValueError):
    """La instancia no cumple las restricciones del problema."""


def verificar_tamano_tabla(n, B):
    """Avisa con un error claro si la tabla DP no cabe en memoria, antes de reservarla."""
    celdas = (n + 1) * (B + 1)                        # costo: 4 × 1   (2 sumas + 1 multiplicación + 1 asignación)
    if celdas > MAX_CELDAS_TABLA:                     # costo: 1 × 1
        raise ErrorDeEntrada(                         # costo: solo si no cabe (termina el programa): no cuenta
            "la tabla DP tendría %d x %d = %d celdas y el límite es %d (≈ %d MB); "
            "el algoritmo es O(n·B) en memoria: con un B tan grande no cabe"
            % (n + 1, B + 1, celdas, MAX_CELDAS_TABLA, MAX_CELDAS_TABLA * 38 // 10**6))
    # Suma de costos: T = 4·1 + 1·1 = 5   -> constante: Θ(1)


def _entero_no_negativo(x):
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0   # costo: 7 × 1 por llamada   (isinstance, and, isinstance, not, and, comparación, return; si x no es entero: 3)


def validar_entrada(t, c, d, B):
    """Comprueba las restricciones de la guía: enteros no negativos y 0 <= d_i <= t_i.

    Lanza ErrorDeEntrada con un mensaje claro. Costo: O(n).
    """
    if not (len(t) == len(c) == len(d)):              # costo: 6 × 1   (3 len + 2 comparaciones + 1 not)
        raise ErrorDeEntrada("t, c y d deben tener el mismo largo (n); llegaron %d, %d y %d"   # costo: solo si hay error
                             % (len(t), len(c), len(d)))
    if not _entero_no_negativo(B):                    # costo: 9 × 1   (1 llamada + 7 de su cuerpo + 1 not)
        raise ErrorDeEntrada("el presupuesto B debe ser un entero >= 0 (llegó %r)" % (B,))   # costo: solo si hay error
    for i, (ti, ci, di) in enumerate(zip(t, c, d), start=1):   # costo: 3 × (n+1)   (cabecera: n+1 veces)
        for nombre, valor in (("t", ti), ("c", ci), ("d", di)):   # costo: 3 × 4n   (este ciclo siempre tiene 3 vueltas: su cabecera se ejecuta 4 veces por cada una de las n etapas)
            if not _entero_no_negativo(valor):        # costo: 9 × 3n   (cuerpo del ciclo interno: 3 vueltas por etapa; 1 llamada + 7 + 1 not)
                raise ErrorDeEntrada("etapa %d: %s_%d debe ser un entero >= 0 (llegó %r)"   # costo: solo si hay error
                                     % (i, nombre, i, valor))
        if di > ti:                                   # costo: 1 × n   (una comparación por etapa)
            raise ErrorDeEntrada("etapa %d: la reducción d_%d = %d supera la duración t_%d = %d"   # costo: solo si hay error
                                 % (i, i, di, i, ti))
    # Suma de costos:  T(n) = 6 + 9 + 3(n+1) + 3·4n + 9·3n + n
    # Expansión:       T(n) = 15 + 3n + 3 + 12n + 27n + n
    # Agrupación:      T(n) = 43n + 18
    # Orden de crecimiento: Θ(n)   (igual en mejor, peor y promedio con datos válidos)


def llenar_tabla(c, d, B):
    """DP[i][b] = mayor ahorro usando solo las primeras i etapas y gastando a lo sumo b."""
    n = len(c)                                        # costo: 2 × 1   (1 len + 1 asignación)
    DP = [[0] * (B + 1) for _ in range(n + 1)]        # costo: 3 × (n+2) + (B+3) × (n+1) + 1 × 1   (cabecera de la comprensión: n+2 veces; por cada una de las n+1 filas: B+1, crear [0]*(B+1) que recorre B+1 celdas, guardar la fila = B+3; asignar DP)   = Θ(n·B)
    for i in range(1, n + 1):                         # costo: 3 × (n+1)   (cabecera: n+1 veces)
        for b in range(B + 1):                        # costo: 3 × n(B+2)   (cabecera interna: B+2 veces por cada una de las n vueltas del externo)
            DP[i][b] = DP[i - 1][b]                   # costo: 5 × n(B+1)   (cuerpo del ciclo interno: i-1, DP[i-1], [b], DP[i], asignar)   # no acelerar la etapa i
            if c[i - 1] <= b:                         # costo: 3 × n(B+1)   (el if está dentro del for: se evalúa en todas las vueltas; i-1, c[..], comparación)   # acelerarla, si cabe
                DP[i][b] = max(DP[i][b], DP[i - 1][b - c[i - 1]] + d[i - 1])   # costo: 14 × q   (solo cuando la etapa cabe: q veces, con 0 <= q <= n(B+1))
    return DP                                         # costo: 1 × 1
    # Suma de costos:
    #   T(n,B) = 2 + [3(n+2) + (B+3)(n+1) + 1] + 3(n+1) + 3n(B+2) + 5n(B+1) + 3n(B+1) + 14q + 1
    # Con sumatorias, el bloque de los dos ciclos anidados es:
    #   Σ_{i=1}^{n} Σ_{b=0}^{B} (5 + 3) = 8·n·(B+1)        y, aparte, 14 por cada celda donde cabe (14q)
    # Expansión:
    #   T = 2 + (3n + 6 + nB + B + 3n + 3 + 1) + (3n + 3) + (3nB + 6n) + (8nB + 8n) + 14q + 1
    # Agrupación:
    #   T(n,B) = 12·n·B + 23·n + B + 16 + 14q            con 0 <= q <= n(B+1)
    # Orden de crecimiento: Θ(n·B)  en el mejor, el peor y el promedio (solo cambia la constante de n·B)


def reconstruir(DP, c, B):
    """Recorre la tabla desde DP[n][B]; si el valor cambia, esa etapa se aceleró."""
    aceleradas = []                                   # costo: 1 × 1
    b = B                                             # costo: 1 × 1
    for i in range(len(c), 0, -1):                    # costo: 3 × (n+1) + 1 × 1   (cabecera n+1 veces; la llamada len(c), una vez)
        if DP[i][b] != DP[i - 1][b]:                  # costo: 6 × n   (el if está dentro del for: se evalúa las n vueltas; DP[i], [b], i-1, DP[i-1], [b], comparación)
            aceleradas.append(i)                      # costo: 1 × k   (solo cuando el valor cambia: k veces, con 0 <= k <= n)
            b -= c[i - 1]                             # costo: 4 × k   (i-1, c[..], resta, asignación; también k veces)
    aceleradas.reverse()                              # costo: 1 + k   (la llamada, y el cuerpo que invierte k elementos)
    return aceleradas                                 # costo: 1 × 1
    # Suma de costos:  T = 1 + 1 + [3(n+1) + 1] + 6n + k + 4k + (1 + k) + 1
    # Expansión:       T = 2 + 3n + 4 + 6n + 6k + 2
    # Agrupación:      T(n) = 9n + 6k + 8          con 0 <= k <= n
    # Orden de crecimiento: Θ(n)


def resolver(t, c, d, B):
    """Resuelve la instancia de forma exacta con programación dinámica."""
    validar_entrada(t, c, d, B)                       # costo: 1 × 1 + T_validar_entrada   (la llamada + 43n + 18)
    verificar_tamano_tabla(len(c), B)                 # costo: 2 × 1 + 5   (len y la llamada, más el cuerpo)
    DP = llenar_tabla(c, d, B)                        # costo: 2 × 1 + T_llenar_tabla   (llamada + asignación)
    A = reconstruir(DP, c, B)                         # costo: 2 × 1 + T_reconstruir   (llamada + asignación)
    ahorro = DP[len(c)][B]                            # costo: 4 × 1   (len, 2 accesos, asignación)
    return {                                          # costo: 6 × 1   (5 escrituras del diccionario + return); más lo de cada valor:
        "aceleradas": A,                              # costo: 1 × 1
        "costo": sum(c[i - 1] for i in A),            # costo: 1 + 3 × (k+1) + 3 × k   (llamar sum; cabecera del generador k+1 veces; por cada etapa de A: i-1, c[..], acumular)
        "ahorro": ahorro,                             # costo: 1 × 1
        "duracion_final": sum(t) - ahorro,            # costo: 1 + n + 1   (llamar sum, recorrer las n duraciones, restar)
        "tabla": DP,                                  # costo: 1 × 1
    }
    # Suma de costos:
    #   T = (1 + 43n + 18) + 7 + (2 + T_ll) + (2 + 9n + 6k + 8) + 4 + [6 + 1 + (6k + 4) + 1 + (n + 2) + 1]
    # Agrupación (T_ll = T_llenar_tabla):
    #   T = T_ll + 53n + 12k + 57
    # Orden de crecimiento: Θ(n·B)  (lo domina llenar_tabla)


# =============================================================================
# RESUMEN DE COSTO DEL ARCHIVO
# n = etapas, B = presupuesto, k = etapas aceleradas (0 <= k <= n), q = celdas de la tabla donde
# la etapa cabe en el presupuesto (0 <= q <= n(B+1)); p = q / (n(B+1)) es la fracción de celdas
# donde cabe (0 <= p <= 1).
#
# Función                 Mejor caso                    Peor caso                      Promedio
# ----------------------  ----------------------------  -----------------------------  -----------------------------------
# verificar_tamano_tabla  5                             5                              5
# _entero_no_negativo     3  (x no es entero)           7                              7  (los datos válidos son enteros)
# validar_entrada         43n + 18                      43n + 18                       43n + 18                  -> Θ(n)
# llenar_tabla            12nB + 23n + B + 16           26nB + 37n + B + 16            (12+14p)·nB + (23+14p)·n + B + 16   -> Θ(n·B)
# reconstruir             9n + 8  (k = 0)               15n + 8  (k = n)               9n + 6k + 8, k típico ~ n/2         -> Θ(n)
# resolver (todo)         12nB + 76n + B + 73           26nB + 102n + B + 73           (12+14p)·nB + ...                   -> Θ(n·B)
#
# Cuándo ocurre cada caso:
#  - Mejor caso de llenar_tabla: ningún costo cabe en el presupuesto (c_i > B para todo i), o sea
#    q = 0: el `if` se evalúa siempre pero su cuerpo nunca se ejecuta.
#  - Peor caso: la etapa cabe en todas las celdas (por ejemplo c_i = 0), o sea q = n(B+1): el
#    cuerpo del `if` se ejecuta en todas las vueltas.
#  - Mejor caso de reconstruir: ninguna etapa se acelera (k = 0); peor: todas (k = n).
#  - Promedio: p depende de los costos. Con costos aleatorios entre 1 y C y B mucho mayor que C,
#    p se acerca a 1; con costos del tamaño de B, p ronda 1/2.
#
# Conclusión: el algoritmo NO tiene un mejor caso asintóticamente mejor que el peor. Los dos ciclos
# anidados de llenar_tabla recorren siempre las n·(B+1) celdas, así que el mejor, el peor y el
# promedio son los tres Θ(n·B); solo cambia la constante que multiplica a n·B (de 12 a 26, según
# cuántas veces entre el cuerpo del `if`). Memoria: Θ(n·B) por la tabla (de ahí el tope MAX_CELDAS_TABLA).
# =============================================================================


# =============================================================================
# INVARIANTES DE CICLO (correctitud)
# Cada invariante se demuestra en los 3 momentos: inicialización, mantenimiento y finalización.
#
# --- llenar_tabla, ciclo externo `for i in range(1, n + 1)` -------------------
# Invariante: antes de cada iteración i, para todo 0 <= i' < i y todo 0 <= b <= B,
#   DP[i'][b] = el mayor ahorro Σ d_j que se logra eligiendo un subconjunto de las primeras i'
#   etapas con costo total Σ c_j <= b.
#  - Inicialización (i = 1): solo existe la fila 0, que se creó llena de ceros. Con 0 etapas no se
#    puede acelerar nada, así que el mejor ahorro es 0 para cualquier presupuesto b: se cumple.
#  - Mantenimiento: se supone el invariante antes de la iteración i (las filas 0..i-1 son correctas)
#    y se calcula la fila i usando SOLO la fila i-1. Un subconjunto óptimo de las etapas 1..i con
#    presupuesto b puede ser de dos tipos:
#      (a) no contiene la etapa i: su ahorro es el óptimo de 1..i-1 con presupuesto b = DP[i-1][b]
#          (es la línea `DP[i][b] = DP[i-1][b]`);
#      (b) contiene la etapa i (solo si c_i <= b, que es la condición del `if`): ahorra d_i y lo que
#          queda es un subconjunto de 1..i-1 con presupuesto b - c_i, que debe ser óptimo para ese
#          presupuesto (si no lo fuera, se podría mejorar el total) = d_i + DP[i-1][b-c_i].
#    DP[i][b] guarda el máximo de las dos opciones, así que la fila i es correcta. Como en (b) se lee
#    la fila i-1 y no la i, cada etapa se usa a lo sumo una vez (es una mochila 0/1, aunque c_i = 0).
#    Al terminar la iteración, las filas 0..i son correctas: el invariante vale para i + 1.
#  - Finalización: el ciclo termina con i = n + 1. El invariante dice que las filas 0..n son
#    correctas; en particular DP[n][B] es el máximo ahorro con las n etapas y presupuesto B, que es
#    exactamente lo que pide el problema.
# Ciclo interno `for b`: antes de cada b, las celdas DP[i][0..b-1] ya son correctas. Cada celda solo
# depende de la fila i-1 (ya correcta) y no de las celdas de su misma fila, así que calcularlas
# una por una, en cualquier orden, mantiene esa propiedad; al terminar, la fila i completa es correcta.
#
# --- reconstruir, ciclo `for i in range(len(c), 0, -1)` -----------------------
# Invariante: antes de procesar la etapa i, `aceleradas` contiene las etapas aceleradas entre
#   i+1 y n, el presupuesto restante es b = B - Σ c_j de esas etapas, y
#   (Σ d_j de las etapas elegidas) + DP[i][b] = DP[n][B].
#  - Inicialización (i = n): no se eligió ninguna etapa, b = B: la suma de ahorros es 0 y
#    0 + DP[n][B] = DP[n][B]. Se cumple.
#  - Mantenimiento: hay dos casos.
#      * DP[i][b] != DP[i-1][b]: no acelerar la etapa i da DP[i-1][b], que es distinto del óptimo,
#        así que el óptimo viene de acelerarla: DP[i][b] = DP[i-1][b - c_i] + d_i. Se agrega i y
#        b pasa a b - c_i: el ahorro elegido sube d_i y DP[i-1][b - c_i] = DP[i][b] - d_i, así que
#        la suma no cambia y el invariante vale para i - 1.
#      * DP[i][b] == DP[i-1][b]: no acelerar la etapa i ya alcanza el óptimo; no se cambia nada y
#        DP[i][b] = DP[i-1][b], así que el invariante vale para i - 1.
#  - Finalización: el ciclo termina con i = 0. Como DP[0][b] = 0, el ahorro de `aceleradas` es
#    exactamente DP[n][B] (el óptimo), y su costo es B - b <= B porque b nunca queda negativo:
#    solo se resta c_i cuando DP cambió, y eso solo puede pasar si c_i <= b. Por tanto A es
#    factible y óptimo.
#
# --- validar_entrada, ciclo `for i, (ti, ci, di) in enumerate(...)` -----------
# Invariante: antes de revisar la etapa i, las etapas 1..i-1 tienen t, c, d enteros >= 0 y d <= t.
#  - Inicialización (i = 1): no hay etapas revisadas; la afirmación sobre un conjunto vacío es cierta.
#  - Mantenimiento: si la etapa i incumple una comprobación, se lanza ErrorDeEntrada y no se llega
#    a i + 1; si las cumple, 1..i cumplen y el invariante vale para i + 1.
#  - Finalización: al terminar, las n etapas cumplen las restricciones: la instancia es válida.
# =============================================================================
