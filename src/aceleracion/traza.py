"""Parte 1: escritura de la traza de la DP (separada del algoritmo).

Las funciones devuelven texto; no calculan nada del problema. La evidencia de
un caso es `formatear_caso(resultado)`, que recibe un `ResultadoCaso`.

Costo por línea: `# costo: OE × veces`, con el modelo del curso explicado al inicio de
`aceleracion.py` (cada asignación, comparación, operación aritmética, acceso a un atributo
o a una lista, return o llamada cuesta 1; la cabecera de un `for` de m vueltas cuesta
3 × (m + 1) y su cuerpo m veces; un `if` dentro de un `for` se evalúa en todas las vueltas y
su cuerpo entre 0 y todas; el cuerpo de una función llamada se analiza aparte). Para el texto
se agrega: dar formato a una cadena con q valores cuesta q; añadir una línea a la lista cuesta
1; `"\\n".join` de s líneas cuesta 1 + s; convertir en texto una lista de q números cuesta q.
Variables: n = etapas, B = presupuesto, k = etapas aceleradas.
Al final de cada función se arma T(n); al final del archivo están el resumen del mejor caso,
el peor y el promedio, y el invariante de ciclo.
"""

from .resolver import ResultadoCaso

# La tabla DP tiene (n+1) x (B+1) celdas: solo se imprime completa si B es pequeño.
B_MAX_TABLA = 100                                         # costo: 1 × 1 (una vez, al importar)


def formatear_tabla(DP):
    """Una línea por etapa i con DP[i][b] para b = 0..B (ahorro máximo)."""
    return "\n".join("i=%d: %s" % (i, fila) for i, fila in enumerate(DP))   # costo: 3 × (n+2) + (2 + (B+1) + 1) × (n+1) + 1 + (n+1) + 1   (la tabla tiene n+1 filas: cabecera n+2 veces; por fila: 2 valores de formato, convertir la fila de B+1 números, guardar; llamar join y unir las n+1 líneas; return)
    # Suma de costos:  T = 3(n+2) + (B+4)(n+1) + 1 + (n+1) + 1
    # Expansión:       T = (3n + 6) + (nB + 4n + B + 4) + 1 + n + 1 + 1
    # Agrupación:      T(n,B) = n·B + 8n + B + 13          -> Θ(n·B)


def formatear_decisiones(DP, c, d, B, etiqueta=str):
    """Recorre la tabla desde DP[n][B] y dice, etapa por etapa, qué se decidió y por qué.

    `etiqueta(i)` da el nombre de la etapa i (por defecto, su número).
    """
    lineas = []                                           # costo: 1 × 1
    b = B                                                 # costo: 1 × 1
    for i in range(len(c), 0, -1):                        # costo: 3 × (n+1) + 1 × 1   (cabecera n+1 veces; la llamada len(c), una vez)
        nombre = "Etapa %d (%s)" % (i, etiqueta(i)) if etiqueta(i) != str(i) else "Etapa %d" % i   # costo: 9 × n sin ids, 19 × n con ids   (cuerpo del for: n vueltas; con ids se llama dos veces a etiqueta)
        if DP[i][b] != DP[i - 1][b]:                      # costo: 6 × n   (el if está dentro del for: se evalúa las n vueltas; DP[i], [b], i-1, DP[i-1], [b], comparación)
            lineas.append("%s: acelerada, costo %d, ahorro %d; presupuesto restante %d -> %d"
                          % (nombre, c[i - 1], d[i - 1], b, b - c[i - 1]))   # costo: 13 × k   (solo cuando la etapa se acelera: k veces, con 0 <= k <= n; c[i-1] 2, d[i-1] 2, b - c[i-1] 3, formato 5, agregar 1)
            b -= c[i - 1]                                 # costo: 4 × k   (i-1, c[..], resta, asignación; también k veces)
        else:
            lineas.append("%s: no se acelera (DP[%d][%d] = DP[%d][%d] = %d)"
                          % (nombre, i, b, i - 1, b, DP[i][b]))   # costo: 10 × (n − k)   (las vueltas restantes, en que NO se acelera: i-1 1, DP[i][b] 2, formato 6, agregar 1)
    return "\n".join(lineas)                              # costo: 1 + n + 1   (llamar join, unir las n líneas, return)
    # Suma de costos:  T = 1 + 1 + [3(n+1) + 1] + (9..19)n + 6n + 13k + 4k + 10(n − k) + (n + 2)
    # Expansión:       T = 2 + 3n + 4 + (9..19)n + 6n + 17k + 10n − 10k + n + 2
    # Agrupación:      T(n) = (29..39)n + 7k + 8      (29 sin ids, 39 con ids)   con 0 <= k <= n
    # Orden de crecimiento: Θ(n)


def formatear_caso(rc: ResultadoCaso) -> str:
    """Texto completo de un caso: resultado, tiempo, verificación, decisiones y (si cabe) la tabla."""
    inst = rc.instancia                                   # costo: 2 × 1
    etiqueta = inst.etiqueta_etapa if inst is not None else str   # costo: 3 × 1
    nombres = [etiqueta(i) for i in rc.aceleradas]        # costo: 1 + 3 × (k+1) + (1 + 4..6 + 1) × k   (leer el atributo; cabecera k+1 veces; por etapa acelerada: llamar etiqueta_etapa y guardar) = (9..11)k + 4
    lineas = [                                            # costo: 3k + 45 × 1   (armar las 8 líneas de encabezado: formatos de 2 a 3 valores cada una, más convertir la lista de k etapas en texto y unir sus k nombres)
        "Caso: %s   (n = %d etapas, B = %d)" % (rc.nombre, rc.n, rc.B),
        "",
        "Etapas aceleradas: %s   (%s)" % (rc.aceleradas, ", ".join(nombres) if nombres else "ninguna"),
        "Costo usado: %d de B = %d" % (rc.costo, rc.B),
        "Ahorro: %d" % rc.ahorro,
        "Duración final: %d (original %d)" % (rc.duracion_final, rc.duracion_original),
        "Tiempo de la DP: %.6f s" % rc.tiempo_s,
        "Solución válida (costo <= B y sumas coherentes): %s" % ("sí" if rc.valida else "NO"),
    ]
    if rc.optimo_ahorro is not None:                      # costo: 2 × 1
        lineas.append("Ahorro por fuerza bruta: %d (%s)" % (
            rc.optimo_ahorro, "coincide" if rc.optimo_ahorro == rc.ahorro else "NO COINCIDE"))   # costo: 7 × 1   (solo si n <= 12: 3 atributos, comparación, 2 formatos, agregar)
    else:
        lineas.append("Fuerza bruta: no se corre (n > 12)")   # costo: 1 × 1   (solo si n > 12)
    lineas += ["", "Decisiones (de la última etapa a la primera):"]   # costo: 2 × 1
    if inst is not None:                                  # costo: 1 × 1
        lineas.append(formatear_decisiones(rc.tabla, inst.c, inst.d, rc.B, etiqueta))   # costo: 6 × 1 + T_decisiones   (4 atributos, llamada, agregar)
    if rc.B <= B_MAX_TABLA:                               # costo: 2 × 1
        lineas += ["", "Tabla DP (ahorro máximo; fila i = primeras i etapas, columna b = presupuesto b):",
                   formatear_tabla(rc.tabla)]             # costo: 4 × 1 + T_tabla   (solo si B <= 100; T_tabla = n·B + 8n + B + 13; como B <= 100, es a lo sumo 108n + 113  -> Θ(n))
    else:
        lineas += ["", "Tabla DP omitida: B = %d > %d (tendría %d x %d celdas)."
                   % (rc.B, B_MAX_TABLA, rc.n + 1, rc.B + 1)]   # costo: 10 × 1   (solo si B > 100: constante)
    return "\n".join(lineas)                              # costo: 1 + (2n + 16) + 1   (llamar join, unir ≈ 2n + 16 líneas: las n decisiones, las n+1 filas de la tabla si se imprime y ~15 de encabezado; return)
    # Suma de costos:  T = 5 + (9..11)k + 4 + (3k + 45) + (2 a 7) + 2 + 1 + (6 + T_dec) + [4 + T_tabla  o  10] + (2n + 18)
    # Agrupación aproximada:
    #   con B > 100:   T ≈ 29n + 2n + 100 = 31n + 100         (k = 0, sin ids)
    #   con B <= 100:  T ≈ (46 + 11 + 3 + 108 + 2)n + 200 = 170n + 200   (k = n, con ids, B = 100)
    # Orden de crecimiento: Θ(n) en ambos casos (el tope B_MAX_TABLA vuelve constante a B dentro de
    # esta función; sin el tope, la tabla costaría Θ(n·B))


def escribir_traza(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as f:          # costo: 2 × 1, más el acceso al disco
        f.write(texto + "\n")                             # costo: 1 + Ltexto + 1 + Ltexto   (concatenar copia el texto; llamar write y escribirlo)   (Ltexto = largo del texto de la traza)
    # Suma de costos:  T = 2 + (2·Ltexto + 2)
    # Agrupación:      T = 2·Ltexto + 4          -> Θ(Ltexto); Ltexto es Θ(n) (o Θ(n·B) si se escribiera la tabla sin tope)


# =============================================================================
# RESUMEN DE COSTO DEL ARCHIVO
# n = etapas, B = presupuesto, k = etapas aceleradas (0 <= k <= n), Ltexto = largo del texto escrito.
#
# Función               Mejor caso                 Peor caso                   Promedio
# --------------------  -------------------------  --------------------------  ------------------------
# formatear_tabla       n·B + 8n + B + 13          n·B + 8n + B + 13           igual   -> Θ(n·B)
# formatear_decisiones  29n + 8  (sin ids, k = 0)  46n + 8  (con ids, k = n)    entre ambos   -> Θ(n)
# formatear_caso        ≈ 31n + 100  (B > 100)     ≈ 170n + 200  (B <= 100)     entre ambos   -> Θ(n)
# escribir_traza        Θ(Ltexto)                  Θ(Ltexto)                    Θ(Ltexto)
#
# Cuándo ocurre cada caso:
#  - formatear_decisiones: el mejor caso es que ninguna etapa se acelere (k = 0: siempre la rama
#    `else`, más barata) y las etapas no tengan id; el peor, que todas se aceleren (k = n) y todas
#    tengan id.
#  - formatear_caso: el mejor caso es B > 100 (la tabla se omite); el peor, B <= 100 (se imprime).
#
# Conclusión: escribir la traza es Θ(n), mucho más barato que la DP (Θ(n·B)). Eso es gracias a
# B_MAX_TABLA: si se imprimiera la tabla completa con cualquier B, la traza costaría Θ(n·B) y
# pasaría a dominar el tiempo de todo el caso.
# =============================================================================


# =============================================================================
# INVARIANTE DE CICLO (correctitud)
#
# --- formatear_decisiones, ciclo `for i in range(len(c), 0, -1)` ---------------
# Es el mismo recorrido que `reconstruir` (aceleracion.py), pero escribiendo una línea por etapa.
# Invariante: antes de procesar la etapa i, `lineas` contiene exactamente una línea por cada etapa
#   n, n-1, ..., i+1 (en ese orden) con la decisión que tomó la DP, y b = B - Σ c_j de las etapas
#   que esas líneas dicen "acelerada".
#  - Inicialización (i = n): `lineas` está vacía (no hay etapas posteriores a n) y b = B: se cumple.
#  - Mantenimiento: para la etapa i, la condición DP[i][b] != DP[i-1][b] es la misma de
#    `reconstruir`; si es cierta se escribe "acelerada" y b baja c_i, y si no se escribe "no se
#    acelera" y b no cambia. En ambos casos se agrega exactamente una línea, así que `lineas` cubre
#    ahora n..i y b sigue siendo B menos el costo de las etapas aceleradas.
#  - Finalización: con i = 0 hay una línea por cada una de las n etapas, y b = B - costo(A): la
#    traza describe exactamente las decisiones de la solución que devolvió `reconstruir`.
#
# formatear_tabla y formatear_caso no tienen ciclos que acumulen estado (solo recorren para
# convertir a texto), así que no necesitan invariante.
# =============================================================================
