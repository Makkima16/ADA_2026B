#!/usr/bin/env python3
"""Corre TODOS los casos y regenera TODAS las evidencias.  [Integrante 3]

    python3 run_all.py --casos casos/ --salida resultados/ [--lista nombres.txt] [--partes parte1 parte2 variante] [--sin-enfoques]

Por cada archivo de `--casos` (.json del formato de la profesora o .txt provisional):

* Parte 1 (solo .json): `aceleracion.lectura.leer_instancia` -> `aceleracion.enfoques.resolver_enfoques`
  (corre la DP por presupuesto y la DP por valor, cada una si cabe en memoria). La solución del caso es la de
  presupuesto; si esa tabla no cabe, se resuelve SOLO por valor y la evidencia lo dice; si ninguna cabe, el
  mensaje es que la tabla es demasiado grande          => <caso>_parte1.txt y <caso>_parte1_enfoques.txt
* Parte 2: `auditoria.lectura.leer_instancia` -> `auditoria.resolver.resolver_caso` (voraz base)
  -> `auditoria.traza.formatear_resultado`                    => <caso>_parte2.txt
  y todos los enfoques del voraz (ocho combinaciones) con `auditoria.enfoques.comparacion.resolver_enfoques`
                                                              => <caso>_parte2_enfoques.txt
* Variante 1 (si el caso trae costos): `auditoria.lectura_ponderada.leer_opciones` (formato de la profesora:
  variaciones parcial y completa; o costo_auditoria / "# costos:")
  -> `auditoria.resolver_ponderada.resolver_caso_ponderado` (sin cambios, sobre las opciones)
  -> `auditoria.opciones.depurar` (no pagar dos veces la misma interacción)
  -> `auditoria.traza_ponderada.formatear_resultado_ponderado` => <caso>_variante1.txt

Además escribe `resumen.csv` (caso, parte, resultado, tiempo en segundos, traza),
`version.txt` (commit de git, fecha y comando), para probar que todas las evidencias
salen de la misma versión del código, y `comparacion.md`: tablas que comparan todos los
casos (Parte 1: DP contra fuerza bruta; Parte 2 contra Variante 1: tamaño, costo, razón
contra el óptimo y H(d), y cuánto ahorra la variante). La tabla también se imprime en la
terminal (se puede apagar con --sin-tabla). `comparacion.md` incluye también las tablas de los enfoques de la
Parte 1 (DP por presupuesto y por valor) y de la Parte 2 (las ocho combinaciones del voraz).

Reglas que cumple (CLAUDE.md):
* No reimplementa algoritmos ni lectura: solo llama a las funciones públicas de cada parte.
  Se lee archivo por archivo con `leer_instancia` (la función que usa `leer_casos` por
  dentro) para que un caso mal formado no detenga los demás: el error queda en su evidencia.
* No escribe nada en `--casos`.
* Regenera todo `--salida`: antes de escribir borra SOLO los archivos que este script
  genera (*_parte1.txt, *_parte2.txt, *_variante1.txt, *_enfoques.txt, resumen.csv, version.txt, comparacion.md).
"""

import argparse
import csv
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from aceleracion import lectura as lectura_p1          # noqa: E402
from aceleracion.enfoques.resolver_enfoques import (   # noqa: E402
    NOMBRE_ENFOQUE, agregar_p1, formatear_enfoques_p1, formatear_solucion_p1, resolver_enfoques_p1, resumen_md_p1,
    tabla_enfoques_p1)
from aceleracion.enfoques.seleccion import VALOR       # noqa: E402
from auditoria import lectura as lectura_p2            # noqa: E402
from auditoria.enfoques.comparacion.resolver_enfoques import (   # noqa: E402
    agregar_p2, formatear_enfoques_p2, resolver_enfoques_p2, resumen_md_p2, tabla_enfoques_p2)
from auditoria.lectura_ponderada import CAMPO_COSTO_JSON, CAMPO_VARIACIONES_JSON, leer_opciones   # noqa: E402
from auditoria.opciones import agregar_variante, depurar, formatear_opciones, resumen_md_variante   # noqa: E402
from auditoria.resolver import resolver_caso as resolver_p2       # noqa: E402
from auditoria.traza import formatear_resultado        # noqa: E402
from auditoria.resolver_ponderada import resolver_caso_ponderado       # noqa: E402
from auditoria.traza_ponderada import formatear_resultado_ponderado     # noqa: E402

EXTENSIONES = (".json", ".txt")
PARTES = ("parte1", "parte2", "variante")      # lo que se puede elegir revisar con --partes
SUFIJOS_GENERADOS = ("_parte1.txt", "_parte2.txt", "_variante1.txt", "_variante1_parcial.txt", "_enfoques.txt")
ARCHIVOS_GENERADOS = ("resumen.csv", "version.txt", "comparacion.md", "resumen_enfoques.json")


def version_codigo():
    """Hash corto del commit y si hay cambios sin guardar en src/ o run_all.py."""
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
                           capture_output=True, text=True)
        if h.returncode != 0:
            return "sin git", False
        sucio = subprocess.run(["git", "status", "--porcelain", "--", "src", "run_all.py"], cwd=RAIZ,
                               capture_output=True, text=True).stdout.strip()
        return h.stdout.strip(), bool(sucio)
    except FileNotFoundError:
        return "sin git", False


def limpiar_salida(salida):
    """Borra solo lo que este script genera, para regenerarlo completo."""
    for p in salida.iterdir():
        if p.is_file() and (p.name in ARCHIVOS_GENERADOS or p.name.endswith(SUFIJOS_GENERADOS)):
            p.unlink()


def correr_parte1(archivo, encabezado, salida, datos, enfoques=True):
    """Parte 1: las dos tablas de la DP. Devuelve las filas (parte, (resultado, tiempo), destino) del resumen."""
    destino = salida / (archivo.stem + "_parte1.txt")
    destino_e = salida / (archivo.stem + "_parte1_enfoques.txt")
    if not lectura_p1.trae_datos(archivo):      # un caso de una sola parte: lo que no trae no es un error
        if not lectura_p2.trae_datos(archivo):
            motivo = "el archivo no trae datos de ninguna de las dos partes"
            destino.write_text(encabezado + "Caso: %s\nERROR: %s\n" % (archivo.stem, motivo), encoding="utf-8")
            return [("parte1", ("ERROR: %s" % motivo, ""), destino)]
        datos["sin_p1"] = True
        # No se crea archivo de traza: la fila queda en resumen.csv, con la columna de la traza vacía.
        return [("parte1", ("no aplica: el caso no trae datos de la Parte 1", ""), None)]
    try:
        inst = lectura_p1.leer_instancia(archivo)
        comp = resolver_enfoques_p1(inst)
    except ValueError as e:                     # ErrorDeLectura / ErrorDeEntrada heredan de ValueError
        texto = "Caso: %s\nERROR en la Parte 1: %s\n" % (archivo.stem, e)
        destino.write_text(encabezado + texto, encoding="utf-8")
        destino_e.write_text(encabezado + texto, encoding="utf-8")
        return [("parte1", ("ERROR: %s" % e, ""), destino)]

    destino.write_text(encabezado + formatear_solucion_p1(comp), encoding="utf-8")
    liviano = comp.liviano()                    # las tablas pueden pesar mucho: no se guardan hasta el final
    datos["p1"] = liviano.resultado
    if enfoques:                                # con --sin-enfoques no se escribe ni se compara el detalle de las dos tablas
        destino_e.write_text(encabezado + formatear_enfoques_p1(comp), encoding="utf-8")
        datos["p1_enf"] = liviano

    res = comp.resultado
    if res is None:
        fila = ("ERROR: %s" % comp.mensaje_no_cabe(), "")
    else:
        txt = ("A=%s costo=%d ahorro=%d duración %d -> %d"
               % (res.aceleradas, res.costo, res.ahorro, res.duracion_original, res.duracion_final))
        if comp.usada == VALOR:
            txt += " [solo por valor: la tabla por presupuesto no cabe]"
        fila = (txt, "%.6f" % res.tiempo_s)
    filas = [("parte1", fila, destino)]
    for nombre, medida in ((("presupuesto", comp.presupuesto), ("valor", comp.valor)) if enfoques else ()):
        r = medida.resultado
        if r is None:
            filas.append(("parte1_" + nombre, ("no cabe: %d celdas > límite" % medida.celdas, ""), destino_e))
        else:
            filas.append(("parte1_" + nombre, ("ahorro=%d costo=%d celdas=%d" % (r.ahorro, r.costo, medida.celdas),
                                               "%.6f" % r.tiempo_s), destino_e))
    return filas


def correr_parte2_y_variante(archivo, encabezado, salida, datos, partes=PARTES, enfoques=True):
    return _filtrar(_parte2_y_variante(archivo, encabezado, salida, datos, partes, enfoques), partes)


def _parte2_y_variante(archivo, encabezado, salida, datos, partes, enfoques):
    filas = []
    p2_on, var_on = "parte2" in partes, "variante" in partes
    destino2 = salida / (archivo.stem + "_parte2.txt")
    destino2e = salida / (archivo.stem + "_parte2_enfoques.txt")
    destinov = salida / (archivo.stem + "_variante1.txt")
    if not lectura_p2.trae_datos(archivo):      # un caso de una sola parte: lo que no trae no es un error
        if not lectura_p1.trae_datos(archivo):
            motivo = "el archivo no trae datos de ninguna de las dos partes"
            for d in (destino2, destinov):
                d.write_text(encabezado + "Caso: %s\nERROR: %s\n" % (archivo.stem, motivo), encoding="utf-8")
            return [("parte2", ("ERROR: %s" % motivo, ""), destino2), ("variante1", ("ERROR: %s" % motivo, ""), destinov)]
        datos["sin_p2"] = True
        # No se crean archivos de traza: las filas quedan en resumen.csv, con la columna de la traza vacía.
        return [("parte2", ("no aplica: el caso no trae datos de la Parte 2", ""), None),
                ("variante1", ("no aplica: el caso no trae datos de la Parte 2", ""), None)]
    try:
        inst = lectura_p2.leer_instancia(archivo)
    except ValueError as e:
        msg = "Caso: %s\nERROR al leer la instancia de auditoría: %s\n" % (archivo.stem, e)
        for d in (destino2, destino2e, destinov):
            d.write_text(encabezado + msg, encoding="utf-8")
        return [("parte2", ("ERROR: %s" % e, ""), destino2), ("variante1", ("ERROR: %s" % e, ""), destinov)]

    # Parte 2 (voraz base) y todos sus enfoques (solo si se pidió revisar la Parte 2)
    res = resolver_p2(inst) if p2_on else None
    if p2_on:
        datos["inst"], datos["p2"] = inst, res
        destino2.write_text(encabezado + formatear_resultado(res), encoding="utf-8")
    if not p2_on:
        pass
    elif res.factible:
        txt = "J=%s (%d interacciones)" % (res.J, len(res.J))
        if res.optimo is not None:
            txt += " | óptimo %d | razón %.4f | H(d) %.4f" % (len(res.optimo), len(res.J) / max(len(res.optimo), 1), res.cota)
        filas.append(("parte2", (txt, "%.6f" % res.tiempo_s), destino2))
    else:
        filas.append(("parte2", ("no factible: sin cubrir %s" % sorted(res.sin_cubrir), ""), destino2))
    comp2 = resolver_enfoques_p2(inst, optimo=res.optimo) if (p2_on and enfoques) else None
    if comp2 is not None:
        destino2e.write_text(encabezado + formatear_enfoques_p2(comp2), encoding="utf-8")
        datos["p2_enf"] = comp2.liviano()
    for m in (comp2.medidas if comp2 is not None else ()):
        txt = "J=%s (%d interacciones)" % (m.J, len(m.J))
        if comp2.optimo is not None:
            txt += " | óptimo %d | razón %.4f" % (len(comp2.optimo), comp2.razon(m))
        filas.append(("parte2_" + m.identificador, (txt, "%.6f" % m.tiempo_s), destino2e))

    # Variante 1: versión principal (solo completas) y, si el caso trae parciales, la extensión con parciales
    if not var_on:
        return filas
    try:
        opciones = leer_opciones(archivo, inst)
        if opciones is None:
            texto = ("Caso: %s\nEl caso no trae costos de auditoría (campo '%s' con las variaciones parcial y completa, "
                     "o '%s' en cada etapa del .json, o línea '# costos: ...' en el .txt). La variante ponderada no se ejecutó.\n"
                     % (archivo.stem, CAMPO_VARIACIONES_JSON, CAMPO_COSTO_JSON))
            destinov.write_text(encabezado + texto, encoding="utf-8")
            filas.append(("variante1", ("sin costos de auditoría: no se ejecuta", ""), destinov))
        else:
            filas.append(("variante1", _correr_variante(opciones.solo_completas(), encabezado, destinov, datos, "v1"), destinov))
            if opciones.hay_parcial:
                destinop = salida / (archivo.stem + "_variante1_parcial.txt")
                filas.append(("variante1_parcial", _correr_variante(opciones, encabezado, destinop, datos, "vp"), destinop))
    except ValueError as e:                     # ErrorDeLectura de los costos o costos inválidos
        destinov.write_text(encabezado + "Caso: %s\nERROR en la variante ponderada: %s\n" % (archivo.stem, e), encoding="utf-8")
        filas.append(("variante1", ("ERROR: %s" % e, ""), destinov))
    return filas


def _correr_variante(opciones, encabezado, destino, datos, clave):
    """Corre el voraz ponderado sobre unas opciones, escribe su traza y devuelve la fila del resumen."""
    rv = resolver_caso_ponderado(opciones.instancia, opciones.costos)
    dep = depurar(rv.J, opciones) if rv.factible else None
    datos[clave], datos[clave + "_op"], datos[clave + "_dep"] = rv, opciones, dep
    destino.write_text(encabezado + formatear_resultado_ponderado(rv) + formatear_opciones(rv, opciones, dep), encoding="utf-8")
    if not rv.factible:
        return ("no factible: sin cubrir %s" % sorted(rv.sin_cubrir), "")
    txt = "J=%s costo=%g" % (dep.conservadas, dep.costo_real)
    if opciones.version == "con parciales":
        txt += " (%s)" % ", ".join(opciones.instancia.etiqueta_interaccion(k) for k in dep.conservadas)
    if rv.optimo_costo is not None:
        txt += " | óptimo %g | razón %.4f | H(d) %.4f" % (rv.optimo_costo, dep.costo_real / rv.optimo_costo, rv.cota)
    return (txt, "%.6f" % rv.tiempo_s)


def _filtrar(filas, partes):
    """Deja solo las filas de las partes elegidas (parte2* y variante1* según `partes`)."""
    return [f for f in filas if not (f[0].startswith("parte2") and "parte2" not in partes)
            and not (f[0].startswith("variante1") and "variante" not in partes)]


def _ms(segundos):
    return "%.3f" % (segundos * 1000)


def _g(x):
    return "%g" % x


def agregados(casos_datos):
    """(Parte 1, Parte 2, variante): los resúmenes de los enfoques de todos los casos; None si no hay datos de esa parte."""
    c1 = [d["p1_enf"] for _, d in casos_datos if d.get("p1_enf") is not None]
    c2 = [d["p2_enf"] for _, d in casos_datos if d.get("p2_enf") is not None]
    items = [(d["v1"], d["v1_dep"], d["v1_op"], sum(d["v1"].costos[j - 1] for j in d["p2"].J) if d.get("p2") is not None else None)
             for _, d in casos_datos if d.get("v1") is not None and d["v1"].factible and d.get("v1_dep") is not None]
    # la extensión con parciales se compara contra la versión principal (solo completas) del mismo caso
    items_p = [(d["vp"], d["vp_dep"], d["vp_op"], d["v1_dep"].costo_real)
               for _, d in casos_datos if d.get("vp") is not None and d["vp"].factible and d.get("v1_dep") is not None]
    return (agregar_p1(c1) if c1 else None, agregar_p2(c2) if c2 else None,
            agregar_variante(items) if items else None, agregar_variante(items_p) if items_p else None)


def tabla_comparacion(casos_datos, version, fecha):
    """Tablas en Markdown que comparan los resultados de todos los casos.

    Solo lee los resultados que ya calcularon las funciones públicas de cada parte;
    no vuelve a correr ningún algoritmo. Devuelve el texto completo.
    """
    L = ["# Comparación de resultados", "",
         "Versión del código: %s · Generado: %s · Casos: %d" % (version, fecha, len(casos_datos)), "",
         "El mínimo real (óptimo) de la Parte 2 y de la variante se calcula por fuerza bruta con n ≤ 12 y, si no, por subconjuntos de categorías con r ≤ 16; "
         "en la Parte 1 solo por fuerza bruta con n ≤ 12. Donde no se puede calcular aparece «—».", ""]

    # ---------------- Parte 1 ----------------
    filas1 = [(nombre, d["p1"]) for nombre, d in casos_datos if d.get("p1") is not None]
    if filas1:
        L += ["## Parte 1 — Aceleración de la cadena (DP exacta)", "",
              "La DP es exacta: su ahorro debe coincidir siempre con el de la fuerza bruta (que solo se calcula con n ≤ 12). "
              "«Tabla usada» es la que da la solución del caso: la de presupuesto si cabe en memoria; si no, la de valor. "
              "«Reducción» = cuánto bajó la duración de la cadena; «Presupuesto usado» = costo de las etapas aceleradas sobre B.", "",
              "| Caso | n | B | Tabla usada | Etapas aceleradas | Costo usado | Presupuesto usado | Ahorro DP | Ahorro fuerza bruta | ¿Coinciden? | Duración inicial → final | Reducción | Tiempo DP (ms) |",
              "| --- | ---: | ---: | :---: | --- | ---: | ---: | ---: | ---: | :---: | --- | ---: | ---: |"]
        enf1 = dict((nombre, d.get("p1_enf")) for nombre, d in casos_datos)
        for nombre, p in filas1:
            usada = enf1[nombre].usada if enf1.get(nombre) else "presupuesto"
            fb = "—" if p.optimo_ahorro is None else str(p.optimo_ahorro)
            ok = "—" if p.optimo_ahorro is None else ("sí" if p.optimo_ahorro == p.ahorro else "NO")
            uso = "%.0f %%" % (100.0 * p.costo / p.B) if p.B else "—"
            red = "%.1f %%" % (100.0 * p.ahorro / p.duracion_original) if p.duracion_original else "—"
            L.append("| %s | %d | %d | %s | %s | %d | %s | %d | %s | %s | %d → %d | %s | %s |"
                     % (nombre, p.n, p.B, usada, p.aceleradas, p.costo, uso, p.ahorro, fb, ok,
                        p.duracion_original, p.duracion_final, red, _ms(p.tiempo_s)))
        L.append("")

    # ---------------- Parte 2 vs Variante 1 ----------------
    filas2 = [(nombre, d) for nombre, d in casos_datos if "p2" in d and d["p2"].factible]
    resumen = []                                # líneas del resumen final, en el orden Parte 1, Parte 2, Variante 1
    if filas1:
        con_fb = [p for _, p in filas1 if p.optimo_ahorro is not None]
        reducciones = [100.0 * p.ahorro / p.duracion_original for _, p in filas1 if p.duracion_original]
        usos = [100.0 * p.costo / p.B for _, p in filas1 if p.B]
        lin = "- **Parte 1:** "
        if con_fb:
            lin += ("la DP coincidió con la fuerza bruta en %d de %d casos con n ≤ 12 (debe ser siempre: es exacta). "
                    % (sum(p.optimo_ahorro == p.ahorro for p in con_fb), len(con_fb)))
        if reducciones:
            lin += ("La duración de la cadena bajó en promedio %.1f %% (entre %.1f %% y %.1f %%), usando en promedio el %.0f %% del presupuesto B."
                    % (sum(reducciones) / len(reducciones), min(reducciones), max(reducciones),
                       sum(usos) / len(usos) if usos else 0))
        resumen.append(lin)
    if filas2:
        L += ["## Parte 2 (mínimo número) vs Variante 1 (mínimo costo)", "",
              "«Costo del J de la Parte 2» = lo que costaría auditar, con los costos a_j, las interacciones que elige "
              "el voraz de la Parte 2. «Ahorro» = cuánto más barato sale el voraz ponderado.", "",
              "| Caso | n | r | d | H(d) | P2: \\|J\\| | P2: óptimo | P2: razón | V1: \\|J\\| | V1: costo | V1: óptimo | V1: razón | Costo del J de la P2 | Ahorro de la V1 | P2 (ms) | V1 (ms) |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for nombre, d in filas2:
            p2, inst = d["p2"], d["inst"]
            dmax = max(len(s) for s in inst.S)
            opt2 = "—" if p2.optimo is None else str(len(p2.optimo))
            raz2 = "—" if p2.optimo is None else "%.3f" % (len(p2.J) / len(p2.optimo))
            v = d.get("v1")
            if v is not None and v.factible:
                dv = d["v1_dep"]                          # costo real: sin pagar dos veces la misma interacción
                costo_p2 = sum(v.costos[j - 1] for j in p2.J)
                ahorro = costo_p2 - dv.costo_real
                optv = "—" if v.optimo_costo is None else _g(v.optimo_costo)
                razv = "—" if v.optimo_costo is None else "%.3f" % (dv.costo_real / v.optimo_costo)
                cols_v = (str(len(dv.conservadas)), _g(dv.costo_real), optv, razv, _g(costo_p2),
                          "%s (%.0f %%)" % (_g(ahorro), 100.0 * ahorro / costo_p2), _ms(v.tiempo_s))
            else:
                cols_v = ("—",) * 5 + ("sin costos",) + ("—",)
            L.append("| %s | %d | %d | %d | %.3f | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % ((nombre, p2.n, p2.r, dmax, p2.cota, len(p2.J), opt2, raz2) + cols_v[:5]
                        + (cols_v[5], _ms(p2.tiempo_s), cols_v[6])))
        L.append("")

        # Resumen
        con_opt2 = [d["p2"] for _, d in filas2 if d["p2"].optimo is not None]
        vs = [d["v1"] for _, d in filas2 if d.get("v1") is not None and d["v1"].factible]
        con_optv = [v for v in vs if v.optimo_costo is not None]
        if con_opt2:
            razones = [len(p.J) / len(p.optimo) for p in con_opt2]
            resumen.append("- **Parte 2:** el voraz fue óptimo en %d de %d casos con mínimo real; razón máxima %.3f; "
                     "casos que superan H(d): %d."
                     % (sum(abs(x - 1) < 1e-9 for x in razones), len(razones), max(razones),
                        sum(len(p.J) / len(p.optimo) > p.cota + 1e-9 for p in con_opt2)))
        if con_optv:
            razones = [d["v1_dep"].costo_real / d["v1"].optimo_costo for _, d in filas2
                       if d.get("v1") is not None and d["v1"].factible and d["v1"].optimo_costo is not None]
            resumen.append("- **Variante 1:** el voraz ponderado fue óptimo en %d de %d casos con mínimo real; razón máxima %.3f; "
                     "casos que superan H(d): %d."
                     % (sum(abs(x - 1) < 1e-9 for x in razones), len(razones), max(razones),
                        sum(x > v.cota + 1e-9 for x, v in zip(razones, con_optv))))
        if vs:
            ahorros = []
            for _, d in filas2:
                v = d.get("v1")
                if v is not None and v.factible:
                    cp2 = sum(v.costos[j - 1] for j in d["p2"].J)
                    ahorros.append((cp2 - d["v1_dep"].costo_real) / cp2)
            resumen.append("- **Parte 2 vs Variante 1:** la variante salió más barata que el J de la Parte 2 en %d de %d casos "
                     "(ahorro medio %.0f %%), igual en %d y más cara en %d."
                     % (sum(x > 1e-9 for x in ahorros), len(ahorros), 100.0 * sum(ahorros) / len(ahorros),
                        sum(abs(x) <= 1e-9 for x in ahorros), sum(x < -1e-9 for x in ahorros)))
        L.append("")
    # Detalle de los enfoques caso por caso (el resumen va arriba)
    detalle_enfoques = [tabla_enfoques_p1([d["p1_enf"] for _, d in casos_datos if d.get("p1_enf") is not None]),
                        tabla_enfoques_p2([d["p2_enf"] for _, d in casos_datos if d.get("p2_enf") is not None])]
    # El resumen va primero: lo que se necesita leer de un vistazo; las tablas por caso quedan abajo.
    agg1, agg2, aggv, aggvp = agregados(casos_datos)
    arriba = L[:6]
    sin1 = [n for n, d in casos_datos if d.get("sin_p1")]
    sin2 = [n for n, d in casos_datos if d.get("sin_p2")]
    for nombres, parte in ((sin1, "1"), (sin2, "2")):
        if nombres:
            arriba += ["No aplica la Parte %s en %d casos (no traen sus datos; se analizan solo con la otra parte): %s." % (
                parte, len(nombres), ", ".join(nombres[:8]) + (" …" if len(nombres) > 8 else "")), ""]
    arriba += ["## Resumen", ""] + resumen + [""]
    arriba += [resumen_md_p1(agg1) if agg1 else "", resumen_md_p2(agg2) if agg2 else "", resumen_md_variante(aggv),
               resumen_md_variante(aggvp, "con parciales (extensión)", "la versión solo completas")]
    return "\n".join(arriba + ["## Detalle por caso", ""] + L[6:] + detalle_enfoques) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Corre todos los casos y genera las evidencias.")
    ap.add_argument("--casos", required=True, help="directorio de casos (solo lectura)")
    ap.add_argument("--salida", required=True, help="directorio donde se regeneran las evidencias")
    ap.add_argument("--lista", help="archivo de texto con los nombres de los casos a correr, uno por línea (sin extensión; "
                                    "# comenta); sirve para dejar las evidencias de solo algunos casos de la carpeta")
    ap.add_argument("--partes", nargs="+", choices=PARTES, default=list(PARTES),
                    help="qué revisar: parte1 (DP), parte2 (voraz base y sus enfoques) y/o variante (por defecto, las tres)")
    ap.add_argument("--sin-enfoques", dest="sin_enfoques", action="store_true",
                    help="no correr los enfoques: de la Parte 1 solo la solución del caso (sin el detalle de las dos tablas) y "
                         "de la Parte 2 solo el voraz base (sin las ocho combinaciones)")
    ap.add_argument("--sin-tabla", "--sin_tabla", dest="sin_tabla", action="store_true",
                    help="no imprimir la tabla de comparación en la terminal (igual se guarda en comparacion.md)")
    args = ap.parse_args(argv)
    sin_tabla = args.sin_tabla
    partes = tuple(args.partes)
    enfoques = not args.sin_enfoques

    casos = Path(args.casos).resolve()
    salida = Path(args.salida).resolve()
    if not casos.is_dir():
        sys.exit("No existe el directorio de casos: %s" % args.casos)
    if salida == casos:
        sys.exit("--salida no puede ser el mismo directorio que --casos (casos/ es de solo lectura).")
    archivos = sorted(p for p in casos.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONES)
    if not archivos:
        sys.exit("No hay casos .json ni .txt en %s" % args.casos)
    if args.lista:
        try:
            pedidos = [l.split("#")[0].strip() for l in Path(args.lista).read_text(encoding="utf-8").splitlines()]
        except OSError as e:
            sys.exit("No se pudo leer la lista de casos: %s" % e)
        pedidos = [n for n in pedidos if n]
        por_nombre = {p.stem: p for p in archivos}
        faltan = [n for n in pedidos if n not in por_nombre]
        if faltan or not pedidos:
            sys.exit("La lista %s %s" % (args.lista, ("pide casos que no están en %s: %s" % (args.casos, ", ".join(faltan))) if faltan else "está vacía"))
        archivos = [por_nombre[n] for n in sorted(set(pedidos))]

    salida.mkdir(parents=True, exist_ok=True)
    limpiar_salida(salida)
    commit, sucio = version_codigo()
    version = commit + (" (con cambios sin commit)" if sucio else "")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    filas = []
    casos_datos = []                            # (nombre, {"p1", "inst", "p2", "v1"}) para la tabla de comparación
    for archivo in archivos:
        encabezado = ("Versión del código: %s | Generado: %s | Archivo: %s\n%s\n"
                      % (version, fecha, archivo.name, "=" * 78))
        datos = {}
        if archivo.suffix.lower() == ".json" and "parte1" in partes:
            for parte, fila, destino in correr_parte1(archivo, encabezado, salida, datos, enfoques):
                filas.append((archivo.stem, parte, fila[0], fila[1], destino.name if destino else ""))
        if "parte2" in partes or "variante" in partes:
            for parte, fila, destino in correr_parte2_y_variante(archivo, encabezado, salida, datos, partes, enfoques):
                filas.append((archivo.stem, parte, fila[0], fila[1], destino.name if destino else ""))
        casos_datos.append((archivo.stem, datos))
        print("[%s] evidencias generadas" % archivo.stem)

    comparacion = tabla_comparacion(casos_datos, version, fecha)
    (salida / "comparacion.md").write_text(comparacion, encoding="utf-8")
    agg1, agg2, aggv, aggvp = agregados(casos_datos)
    (salida / "resumen_enfoques.json").write_text(json.dumps({
        "version": version, "fecha": fecha, "casos": len(casos_datos), "parte1": agg1, "parte2": agg2, "variante": aggv, "variante_parcial": aggvp,
        "sin_parte1": [n for n, d in casos_datos if d.get("sin_p1")], "sin_parte2": [n for n, d in casos_datos if d.get("sin_p2")],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    if not sin_tabla:
        print()
        print(comparacion)

    with open(salida / "resumen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caso", "parte", "resultado", "tiempo_s", "traza"])
        w.writerows(filas)
    (salida / "version.txt").write_text(
        "Commit: %s\nCambios sin commit en src/ o run_all.py: %s\nFecha: %s\nPython: %s\nComando: %s\nCasos: %d\n"
        % (commit, "sí" if sucio else "no", fecha, platform.python_version(),
           "python3 run_all.py --casos %s --salida %s%s%s" % (args.casos, args.salida,
                                                                   "" if partes == PARTES else " --partes " + " ".join(partes),
                                                                   " --sin-enfoques" if args.sin_enfoques else ""), len(archivos)),
        encoding="utf-8")

    errores = sum(1 for f in filas if f[2].startswith("ERROR"))
    print("Listo: %d casos, %d evidencias, %d errores. Resumen en %s"
          % (len(archivos), len(filas), errores, Path(args.salida) / "resumen.csv"))
    if sucio:
        print("Aviso: hay cambios sin commit; para la entrega, haz commit y vuelve a correr.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())