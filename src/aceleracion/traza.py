"""Parte 1: escritura de la traza de la DP (separada del algoritmo).

Las funciones devuelven texto; no calculan nada del problema. La evidencia de
un caso es `formatear_caso(resultado)`, que recibe un `ResultadoCaso`.
"""

from .resolver import ResultadoCaso

# La tabla DP tiene (n+1) x (B+1) celdas: solo se imprime completa si B es pequeño.
B_MAX_TABLA = 100


def formatear_tabla(DP):
    """Una línea por etapa i con DP[i][b] para b = 0..B (ahorro máximo)."""
    return "\n".join("i=%d: %s" % (i, fila) for i, fila in enumerate(DP))


def formatear_decisiones(DP, c, d, B, etiqueta=str):
    """Recorre la tabla desde DP[n][B] y dice, etapa por etapa, qué se decidió y por qué.

    `etiqueta(i)` da el nombre de la etapa i (por defecto, su número).
    """
    lineas = []
    b = B
    for i in range(len(c), 0, -1):
        nombre = "Etapa %d (%s)" % (i, etiqueta(i)) if etiqueta(i) != str(i) else "Etapa %d" % i
        if DP[i][b] != DP[i - 1][b]:
            lineas.append("%s: acelerada, costo %d, ahorro %d; presupuesto restante %d -> %d"
                          % (nombre, c[i - 1], d[i - 1], b, b - c[i - 1]))
            b -= c[i - 1]
        else:
            lineas.append("%s: no se acelera (DP[%d][%d] = DP[%d][%d] = %d)"
                          % (nombre, i, b, i - 1, b, DP[i][b]))
    return "\n".join(lineas)


def formatear_caso(rc: ResultadoCaso) -> str:
    """Texto completo de un caso: resultado, tiempo, verificación, decisiones y (si cabe) la tabla."""
    inst = rc.instancia
    etiqueta = inst.etiqueta_etapa if inst is not None else str
    nombres = [etiqueta(i) for i in rc.aceleradas]
    lineas = [
        "Caso: %s   (n = %d etapas, B = %d)" % (rc.nombre, rc.n, rc.B),
        "",
        "Etapas aceleradas: %s   (%s)" % (rc.aceleradas, ", ".join(nombres) if nombres else "ninguna"),
        "Costo usado: %d de B = %d" % (rc.costo, rc.B),
        "Ahorro: %d" % rc.ahorro,
        "Duración final: %d (original %d)" % (rc.duracion_final, rc.duracion_original),
        "Tiempo de la DP: %.6f s" % rc.tiempo_s,
        "Solución válida (costo <= B y sumas coherentes): %s" % ("sí" if rc.valida else "NO"),
    ]
    if rc.optimo_ahorro is not None:
        lineas.append("Ahorro por fuerza bruta: %d (%s)" % (
            rc.optimo_ahorro, "coincide" if rc.optimo_ahorro == rc.ahorro else "NO COINCIDE"))
    else:
        lineas.append("Fuerza bruta: no se corre (n > 12)")
    lineas += ["", "Decisiones (de la última etapa a la primera):"]
    if inst is not None:
        lineas.append(formatear_decisiones(rc.tabla, inst.c, inst.d, rc.B, etiqueta))
    if rc.B <= B_MAX_TABLA:
        lineas += ["", "Tabla DP (ahorro máximo; fila i = primeras i etapas, columna b = presupuesto b):",
                   formatear_tabla(rc.tabla)]
    else:
        lineas += ["", "Tabla DP omitida: B = %d > %d (tendría %d x %d celdas)."
                   % (rc.B, B_MAX_TABLA, rc.n + 1, rc.B + 1)]
    return "\n".join(lineas)


def escribir_traza(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto + "\n")


# =============================================================================
# INVARIANTE DE CICLO (inicialización / mantenimiento / finalización)
#
# formatear_decisiones, ciclo `for i` hacia atrás (mismo recorrido que `reconstruir`):
#   Invariante: antes de la etapa i, `lineas` tiene una línea por cada etapa n..i+1 y
#   b = B - costo de las etapas que esas líneas dicen "acelerada".
#   - Inicio: `lineas` vacía, b = B.
#   - Mantenimiento: se usa la misma condición DP[i][b] != DP[i-1][b] de `reconstruir`; se
#   agrega una línea y, si se aceleró, b baja c_i.
#   - Fin: hay una línea por etapa y describen exactamente la solución de `reconstruir`.
# =============================================================================
