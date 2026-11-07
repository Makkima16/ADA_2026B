"""Escritura de la traza de la DP por valor (separada del algoritmo).

Devuelve texto; no calcula nada del problema. La evidencia de un caso es
`formatear_caso_valor(resultado)`, con un `ResultadoCaso` de `resolver_caso_valor`.
"""

from aceleracion.resolver import ResultadoCaso

# La tabla tiene (n+1) x (D+1) celdas: solo se imprime completa si D es pequeño.
D_MAX_TABLA = 100


def formatear_decisiones_valor(C, c, d, ahorro, B, etiqueta=str):
    """Recorre la tabla desde C[n][ahorro] y dice, etapa por etapa, qué se decidió y por qué."""
    lineas = []
    v = ahorro
    for i in range(len(c), 0, -1):
        nombre = "Etapa %d (%s)" % (i, etiqueta(i)) if etiqueta(i) != str(i) else "Etapa %d" % i
        if C[i][v] != C[i - 1][v]:
            lineas.append("%s: acelerada, costo %d, ahorro %d; ahorro por lograr %d -> %d"
                          % (nombre, c[i - 1], d[i - 1], v, v - d[i - 1]))
            v -= d[i - 1]
        else:
            lineas.append("%s: no se acelera (C[%d][%d] = C[%d][%d] = %d)" % (nombre, i, v, i - 1, v, C[i][v]))
    return "\n".join(lineas)


def formatear_tabla_valor(C, B):
    """Una línea por etapa i con C[i][v] para v = 0..D ('-' = no se puede o pasa de B)."""
    return "\n".join("i=%d: %s" % (i, [x if x <= B else "-" for x in fila]) for i, fila in enumerate(C))


def formatear_caso_valor(rc: ResultadoCaso) -> str:
    """Texto completo de un caso resuelto con la DP por valor."""
    inst = rc.instancia
    etiqueta = inst.etiqueta_etapa if inst is not None else str
    D = len(rc.tabla[0]) - 1
    nombres = [etiqueta(i) for i in rc.aceleradas]
    lineas = [
        "Caso: %s   (n = %d etapas, B = %d)   [DP por valor, D = %d]" % (rc.nombre, rc.n, rc.B, D),
        "",
        "Etapas aceleradas: %s   (%s)" % (rc.aceleradas, ", ".join(nombres) if nombres else "ninguna"),
        "Costo usado: %d de B = %d" % (rc.costo, rc.B),
        "Ahorro: %d" % rc.ahorro,
        "Duración final: %d (original %d)" % (rc.duracion_final, rc.duracion_original),
        "Tiempo de la DP por valor: %.6f s" % rc.tiempo_s,
        "Solución válida (costo <= B y sumas coherentes): %s" % ("sí" if rc.valida else "NO"),
    ]
    if rc.optimo_ahorro is not None:
        lineas.append("Ahorro por fuerza bruta: %d (%s)" % (
            rc.optimo_ahorro, "coincide" if rc.optimo_ahorro == rc.ahorro else "NO COINCIDE"))
    else:
        lineas.append("Fuerza bruta: no se corre (n > 12)")
    lineas += ["", "Decisiones (de la última etapa a la primera):"]
    if inst is not None:
        lineas.append(formatear_decisiones_valor(rc.tabla, inst.c, inst.d, rc.ahorro, rc.B, etiqueta))
    if D <= D_MAX_TABLA:
        lineas += ["", "Tabla por valor (menor costo; fila i = primeras i etapas, columna v = ahorro v):",
                   formatear_tabla_valor(rc.tabla, rc.B)]
    else:
        lineas += ["", "Tabla por valor omitida: D = %d > %d (tendría %d x %d celdas)."
                   % (D, D_MAX_TABLA, rc.n + 1, D + 1)]
    return "\n".join(lineas)
