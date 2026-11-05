"""Parte 1: herramientas de verificación (no son parte del algoritmo).

Fuerza bruta para comprobar la DP con n <= 12 y generador de instancias con
semilla fija (mismo código + misma semilla = misma instancia).

Costo por línea: `# costo: OE × veces`, con el modelo del curso explicado al inicio de
`aceleracion.py` (cada asignación, comparación, operación aritmética, acceso a lista,
return o llamada cuesta 1; la cabecera de un `for` de m vueltas cuesta 3 × (m + 1) y su
cuerpo m veces; un `if` dentro de un `for` se evalúa en todas las vueltas y su cuerpo entre
0 y todas). Al final de cada función se arma T(n) (suma de costos -> agrupación) y al final
del archivo están el resumen del mejor caso, el peor y el promedio, y los invariantes de ciclo.
"""
import random

N_MAX_FUERZA_BRUTA = 12      # la fuerza bruta es O(2^n * n): solo para verificar   # costo: 1 × 1 (una vez, al importar)


def fuerza_bruta(t, c, d, B):
    """Prueba los 2^n subconjuntos. Solo para comprobar la DP (n <= 12)."""
    n = len(c)                                        # costo: 2 × 1
    if n > N_MAX_FUERZA_BRUTA:                        # costo: 1 × 1
        raise ValueError("La fuerza bruta solo se usa con n <= %d" % N_MAX_FUERZA_BRUTA)   # costo: solo si n es demasiado grande
    mejor_ahorro = 0                                  # costo: 1 × 1
    for mascara in range(1 << n):                     # costo: 3 × (2^n + 1) + 1 × 1   (cabecera: 2^n + 1 veces, una por subconjunto más la que sale; el desplazamiento 1 << n, una vez)
        costo = ahorro = 0                            # costo: 2 × 2^n   (cuerpo del ciclo externo: 2 asignaciones)
        for i in range(n):                            # costo: 3 × (n+1)·2^n   (cabecera interna: n+1 veces por cada una de las 2^n máscaras)
            if mascara >> i & 1:                      # costo: 3 × n·2^n   (cuerpo del interno; desplazar, and de bits, prueba)
                costo += c[i]                         # costo: 3 × n·2^(n-1)   (solo cuando el bit i está en 1; entre todas las máscaras hay n·2^(n-1) bits en 1)
                ahorro += d[i]                        # costo: 3 × n·2^(n-1)   (igual: acceso, suma, asignación)
        if costo <= B and ahorro > mejor_ahorro:      # costo: 3 × 2^n   (cuerpo del externo, una vez por máscara; si costo > B el and corta y cuesta 2)
            mejor_ahorro = ahorro                     # costo: 1 × r   (solo cuando se encuentra una mejor solución: r veces, con 0 <= r <= 2^n)
    return {"ahorro": mejor_ahorro, "duracion_final": sum(t) - mejor_ahorro}   # costo: 1 + n + 1 + 1 + 1   (llamar sum, recorrer n elementos, restar, armar el diccionario, return) = n + 4
    # Suma de costos (con N = 2^n):
    #   T = 2 + 1 + 1 + [3(N+1) + 1] + 2N + 3(n+1)N + 3nN + 3·nN/2 + 3·nN/2 + 3N + r + (n + 4)
    # Con sumatorias, el ciclo interno completo es:
    #   Σ_{mascara=0}^{N-1} [ 3(n+1) + 3n ] = N·(6n + 3)        más 3 por cada bit en 1 (3·n·N/2 + 3·n·N/2 = 3nN)
    # Expansión:
    #   T = 4 + (3N + 4) + 2N + (3nN + 3N) + 3nN + 3nN + 3N + r + n + 4
    # Agrupación:
    #   T(n) = (9n + 11)·2^n + n + 12 + r          con 0 <= r <= 2^n
    # Orden de crecimiento: Θ(n·2^n)


def generar_instancia(n, semilla=42, max_t=20, max_c=10):
    """Instancia aleatoria reproducible: con la misma semilla sale siempre igual."""
    rng = random.Random(semilla)                      # costo: 2 × 1
    t = [rng.randint(1, max_t) for _ in range(n)]     # costo: 3 × (n+1) + 2 × n + 1 × 1   (cabecera n+1 veces; por vuelta: llamar randint y guardar el valor; asignar t)
    c = [rng.randint(1, max_c) for _ in range(n)]     # costo: 3 × (n+1) + 2 × n + 1 × 1
    d = [rng.randint(0, ti) for ti in t]              # costo: 3 × (n+1) + 2 × n + 1 × 1   # cumple 0 <= d_i <= t_i
    B = sum(c) // 2                                   # costo: 1 + n + 1 + 1   (llamar sum, recorrer n elementos, dividir, asignar)   # presupuesto: la mitad del costo total
    return t, c, d, B                                 # costo: 2 × 1
    # Suma de costos:  T = 2 + 3·(3(n+1) + 2n + 1) + (n + 3) + 2
    # Expansión:       T = 2 + 3·(5n + 4) + n + 3 + 2
    # Agrupación:      T(n) = 16n + 19
    # Orden de crecimiento: Θ(n)


# =============================================================================
# RESUMEN DE COSTO DEL ARCHIVO  (n = etapas; r = veces que se mejora la mejor solución)
#
# Función             Mejor caso            Peor caso             Promedio
# ------------------  --------------------  --------------------  --------------------
# fuerza_bruta        (9n + 10)·2^n + n + 12  (9n + 12)·2^n + n + 12  ≈ (9n + 11)·2^n + n + 12  -> Θ(n·2^n)
# generar_instancia   16n + 19              16n + 19              16n + 19              -> Θ(n)
#
# En fuerza_bruta no hay mejor caso asintótico: SIEMPRE se visitan las 2^n máscaras y, en cada una,
# las n posiciones (los dos ciclos no dependen de los datos). Lo único que varía es una constante
# por máscara: el `and` corta si el costo ya pasa de B (cuesta 2 en vez de 3) y la línea
# `mejor_ahorro = ahorro` (cuesta 1) se ejecuta r veces, con r entre 0 (mejor caso: ningún
# subconjunto no vacío cabe en B) y 2^n (peor caso: todos caben y cada máscara supera a la
# anterior). Por eso mejor, peor y promedio son Θ(n·2^n). Como solo se usa con n <= 12, el trabajo
# máximo es una constante: (9·12 + 12)·4096 + 24 ≈ 492 mil operaciones.
# =============================================================================


# =============================================================================
# INVARIANTES DE CICLO (correctitud)
#
# --- fuerza_bruta, ciclo interno `for i in range(n)` --------------------------
# Invariante: antes de la iteración i, `costo` y `ahorro` valen Σ c_j y Σ d_j de las etapas
#   j < i (numeradas desde 0) cuyo bit está en 1 en la máscara actual.
#  - Inicialización (i = 0): se acaba de poner costo = ahorro = 0, y no se miró ningún bit: las dos
#    sumas sobre un conjunto vacío valen 0.
#  - Mantenimiento: si el bit i está en 1, la etapa i pertenece al subconjunto y se suman c[i] y
#    d[i]; si está en 0, no se suma nada. En ambos casos las sumas cubren ahora las etapas j <= i.
#  - Finalización: con i = n, `costo` y `ahorro` son exactamente el costo y el ahorro del subconjunto
#    que codifica la máscara.
#
# --- fuerza_bruta, ciclo externo `for mascara in range(1 << n)` ---------------
# Invariante: antes de procesar la máscara m, `mejor_ahorro` es el máximo de Σ d_j entre los
#   subconjuntos factibles (Σ c_j <= B) codificados por las máscaras 0..m-1; vale 0 si m = 0.
#  - Inicialización (m = 0): no se revisó ningún subconjunto y mejor_ahorro = 0. Es el valor correcto
#    como punto de partida porque el subconjunto vacío (máscara 0) tiene ahorro 0 y costo 0 <= B
#    (B es >= 0), así que siempre es factible y el máximo nunca baja de 0.
#  - Mantenimiento: la máscara m codifica un subconjunto distinto de todas las anteriores y, por el
#    invariante del ciclo interno, se obtiene su costo y su ahorro exactos. Si es factible y mejora
#    a mejor_ahorro, se actualiza; si no, el máximo no cambia. Así, mejor_ahorro cubre 0..m.
#  - Finalización: el ciclo termina con m = 2^n: se revisaron todos los subconjuntos posibles de las
#    n etapas, de modo que mejor_ahorro es el óptimo exacto. Por eso sirve para verificar la DP.
#
# generar_instancia no tiene ciclos que acumulen estado: cada elemento de t, c y d se calcula de
# forma independiente, así que no necesita invariante.
# =============================================================================
