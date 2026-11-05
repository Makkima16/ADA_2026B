"""Parte 1: escritura de la traza de la DP (separada del algoritmo).

Las funciones devuelven texto; no calculan nada del problema.
"""


def formatear_tabla(DP):
    """Una línea por etapa i con DP[i][b] para b = 0..B (ahorro máximo)."""
    return "\n".join("i=%d: %s" % (i, fila) for i, fila in enumerate(DP))


def formatear_decisiones(DP, c, d, B):
    """Recorre la tabla desde DP[n][B] y dice, etapa por etapa, qué se decidió y por qué."""
    lineas = []
    b = B
    for i in range(len(c), 0, -1):
        if DP[i][b] != DP[i - 1][b]:
            lineas.append("Etapa %d: se acelera (c=%d, d=%d); presupuesto restante %d -> %d"
                          % (i, c[i - 1], d[i - 1], b, b - c[i - 1]))
            b -= c[i - 1]
        else:
            lineas.append("Etapa %d: no se acelera (DP[%d][%d] = DP[%d][%d] = %d)"
                          % (i, i, b, i - 1, b, DP[i][b]))
    return "\n".join(lineas)


def formatear_resultado(res, t, c, d, B):
    """Texto completo de un caso: tabla, decisiones, etapas aceleradas, costos y duración."""
    return "\n".join([
        "Tabla DP (ahorro máximo):",
        formatear_tabla(res["tabla"]),
        "",
        "Decisiones (de la última etapa a la primera):",
        formatear_decisiones(res["tabla"], c, d, B),
        "",
        "Etapas aceleradas: %s" % res["aceleradas"],
        "Costo usado: %d de B = %d" % (res["costo"], B),
        "Ahorro: %d" % res["ahorro"],
        "Duración final: %d (original %d)" % (res["duracion_final"], sum(t)),
    ])


def escribir_traza(ruta, texto):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
