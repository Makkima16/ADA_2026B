#!/usr/bin/env python3
"""Corre TODOS los casos y regenera TODAS las evidencias.  [Integrante 3]

    python3 run_all.py --casos casos/ --salida resultados/

Por cada archivo de `--casos` (.json del formato de la profesora o .txt provisional):

* Parte 1 (solo .json): `aceleracion.lectura.leer_instancia` -> `aceleracion.resolver.resolver_caso`
  -> `aceleracion.traza.formatear_caso`                       => <caso>_parte1.txt
* Parte 2: `auditoria.lectura.leer_instancia` -> `auditoria.resolver.resolver_caso`
  -> `auditoria.traza.formatear_resultado`                    => <caso>_parte2.txt
* Variante 1 (si el caso trae costos a_j): `auditoria.lectura_ponderada.leer_costos`
  -> `auditoria.resolver_ponderada.resolver_caso_ponderado`
  -> `auditoria.traza_ponderada.formatear_resultado_ponderado` => <caso>_variante1.txt

Además escribe `resumen.csv` (caso, parte, resultado, tiempo en segundos, traza),
`version.txt` (commit de git, fecha y comando), para probar que todas las evidencias
salen de la misma versión del código, y `comparacion.md`: tablas que comparan todos los
casos (Parte 1: DP contra fuerza bruta; Parte 2 contra Variante 1: tamaño, costo, razón
contra el óptimo y H(d), y cuánto ahorra la variante). La tabla también se imprime en la
terminal (se puede apagar con --sin-tabla).

Reglas que cumple (CLAUDE.md):
* No reimplementa algoritmos ni lectura: solo llama a las funciones públicas de cada parte.
  Se lee archivo por archivo con `leer_instancia` (la función que usa `leer_casos` por
  dentro) para que un caso mal formado no detenga los demás: el error queda en su evidencia.
* No escribe nada en `--casos`.
* Regenera todo `--salida`: antes de escribir borra SOLO los archivos que este script
  genera (*_parte1.txt, *_parte2.txt, *_variante1.txt, resumen.csv, version.txt).
"""

import argparse
import csv
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from aceleracion import lectura as lectura_p1          # noqa: E402
from aceleracion.resolver import resolver_caso as resolver_p1     # noqa: E402
from aceleracion.traza import formatear_caso           # noqa: E402
from auditoria import lectura as lectura_p2            # noqa: E402
from auditoria.lectura_ponderada import CAMPO_COSTO_JSON, leer_costos   # noqa: E402
from auditoria.resolver import resolver_caso as resolver_p2       # noqa: E402
from auditoria.traza import formatear_resultado        # noqa: E402
from auditoria.resolver_ponderada import resolver_caso_ponderado       # noqa: E402
from auditoria.traza_ponderada import formatear_resultado_ponderado     # noqa: E402

EXTENSIONES = (".json", ".txt")
SUFIJOS_GENERADOS = ("_parte1.txt", "_parte2.txt", "_variante1.txt")
ARCHIVOS_GENERADOS = ("resumen.csv", "version.txt", "comparacion.md")


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


def correr_parte1(archivo, encabezado, salida, datos):
    destino = salida / (archivo.stem + "_parte1.txt")
    try:
        inst = lectura_p1.leer_instancia(archivo)
        res = resolver_p1(inst)
        datos["p1"] = res
        texto = formatear_caso(res)
        fila = ("A=%s costo=%d ahorro=%d duración %d -> %d"
                % (res.aceleradas, res.costo, res.ahorro, res.duracion_original, res.duracion_final),
                "%.6f" % res.tiempo_s)
    except ValueError as e:                     # ErrorDeLectura / ErrorDeEntrada heredan de ValueError
        texto = "Caso: %s\nERROR en la Parte 1: %s\n" % (archivo.stem, e)
        fila = ("ERROR: %s" % e, "")
    destino.write_text(encabezado + texto, encoding="utf-8")
    return fila, destino


def correr_parte2_y_variante(archivo, encabezado, salida, datos):
    filas = []
    destino2 = salida / (archivo.stem + "_parte2.txt")
    destinov = salida / (archivo.stem + "_variante1.txt")
    try:
        inst = lectura_p2.leer_instancia(archivo)
    except ValueError as e:
        msg = "Caso: %s\nERROR al leer la instancia de auditoría: %s\n" % (archivo.stem, e)
        destino2.write_text(encabezado + msg, encoding="utf-8")
        destinov.write_text(encabezado + msg, encoding="utf-8")
        return [("parte2", ("ERROR: %s" % e, ""), destino2), ("variante1", ("ERROR: %s" % e, ""), destinov)]

    # Parte 2
    res = resolver_p2(inst)
    datos["inst"], datos["p2"] = inst, res
    destino2.write_text(encabezado + formatear_resultado(res), encoding="utf-8")
    if res.factible:
        txt = "J=%s (%d interacciones)" % (res.J, len(res.J))
        if res.optimo is not None:
            txt += " | óptimo %d | razón %.4f | H(d) %.4f" % (len(res.optimo), len(res.J) / max(len(res.optimo), 1), res.cota)
        filas.append(("parte2", (txt, "%.6f" % res.tiempo_s), destino2))
    else:
        filas.append(("parte2", ("no factible: sin cubrir %s" % sorted(res.sin_cubrir), ""), destino2))

    # Variante 1
    try:
        costos = leer_costos(archivo, len(inst.S))
        if costos is None:
            texto = ("Caso: %s\nEl caso no trae costos de auditoría a_j (campo '%s' en cada etapa del .json "
                     "o línea '# costos: ...' en el .txt). La variante ponderada no se ejecutó.\n"
                     % (archivo.stem, CAMPO_COSTO_JSON))
            fila = ("sin costos de auditoría: no se ejecuta", "")
        else:
            rv = resolver_caso_ponderado(inst, costos)
            datos["v1"] = rv
            texto = formatear_resultado_ponderado(rv)
            if rv.factible:
                txt = "J=%s costo=%g" % (rv.J, rv.costo)
                if rv.optimo_costo is not None:
                    txt += " | óptimo %g | razón %.4f | H(d) %.4f" % (rv.optimo_costo, rv.costo / rv.optimo_costo, rv.cota)
                fila = (txt, "%.6f" % rv.tiempo_s)
            else:
                fila = ("no factible: sin cubrir %s" % sorted(rv.sin_cubrir), "")
    except ValueError as e:                     # ErrorDeLectura de los costos o costos inválidos
        texto = "Caso: %s\nERROR en la variante ponderada: %s\n" % (archivo.stem, e)
        fila = ("ERROR: %s" % e, "")
    destinov.write_text(encabezado + texto, encoding="utf-8")
    filas.append(("variante1", fila, destinov))
    return filas


def _ms(segundos):
    return "%.3f" % (segundos * 1000)


def _g(x):
    return "%g" % x


def tabla_comparacion(casos_datos, version, fecha):
    """Tablas en Markdown que comparan los resultados de todos los casos.

    Solo lee los resultados que ya calcularon las funciones públicas de cada parte;
    no vuelve a correr ningún algoritmo. Devuelve el texto completo.
    """
    L = ["# Comparación de resultados", "",
         "Versión del código: %s · Generado: %s · Casos: %d" % (version, fecha, len(casos_datos)), "",
         "La fuerza bruta (óptimo real) solo se calcula con n ≤ 12; con n mayor aparece «—».", ""]

    # ---------------- Parte 1 ----------------
    filas1 = [(nombre, d["p1"]) for nombre, d in casos_datos if "p1" in d]
    if filas1:
        L += ["## Parte 1 — Aceleración de la cadena (DP exacta)", "",
              "La DP es exacta: su ahorro debe coincidir siempre con el de la fuerza bruta (que solo se calcula con n ≤ 12). "
              "«Reducción» = cuánto bajó la duración de la cadena; «Presupuesto usado» = costo de las etapas aceleradas sobre B.", "",
              "| Caso | n | B | Etapas aceleradas | Costo usado | Presupuesto usado | Ahorro DP | Ahorro fuerza bruta | ¿Coinciden? | Duración inicial → final | Reducción | Tiempo DP (ms) |",
              "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | :---: | --- | ---: | ---: |"]
        for nombre, p in filas1:
            fb = "—" if p.optimo_ahorro is None else str(p.optimo_ahorro)
            ok = "—" if p.optimo_ahorro is None else ("sí" if p.optimo_ahorro == p.ahorro else "NO")
            uso = "%.0f %%" % (100.0 * p.costo / p.B) if p.B else "—"
            red = "%.1f %%" % (100.0 * p.ahorro / p.duracion_original) if p.duracion_original else "—"
            L.append("| %s | %d | %d | %s | %d | %s | %d | %s | %s | %d → %d | %s | %s |"
                     % (nombre, p.n, p.B, p.aceleradas, p.costo, uso, p.ahorro, fb, ok,
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
                costo_p2 = sum(v.costos[j - 1] for j in p2.J)
                ahorro = costo_p2 - v.costo
                optv = "—" if v.optimo_costo is None else _g(v.optimo_costo)
                razv = "—" if v.optimo_costo is None else "%.3f" % (v.costo / v.optimo_costo)
                cols_v = (str(len(v.J)), _g(v.costo), optv, razv, _g(costo_p2),
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
        L += ["## Resumen", ""] + resumen
        resumen = []
        if con_opt2:
            razones = [len(p.J) / len(p.optimo) for p in con_opt2]
            L.append("- **Parte 2:** el voraz fue óptimo en %d de %d casos con fuerza bruta; razón máxima %.3f; "
                     "casos que superan H(d): %d."
                     % (sum(abs(x - 1) < 1e-9 for x in razones), len(razones), max(razones),
                        sum(len(p.J) / len(p.optimo) > p.cota + 1e-9 for p in con_opt2)))
        if con_optv:
            razones = [v.costo / v.optimo_costo for v in con_optv]
            L.append("- **Variante 1:** el voraz ponderado fue óptimo en %d de %d casos con fuerza bruta; razón máxima %.3f; "
                     "casos que superan H(d): %d."
                     % (sum(abs(x - 1) < 1e-9 for x in razones), len(razones), max(razones),
                        sum(v.costo / v.optimo_costo > v.cota + 1e-9 for v in con_optv)))
        if vs:
            ahorros = []
            for _, d in filas2:
                v = d.get("v1")
                if v is not None and v.factible:
                    cp2 = sum(v.costos[j - 1] for j in d["p2"].J)
                    ahorros.append((cp2 - v.costo) / cp2)
            L.append("- **Parte 2 vs Variante 1:** la variante salió más barata que el J de la Parte 2 en %d de %d casos "
                     "(ahorro medio %.0f %%), igual en %d y más cara en %d."
                     % (sum(x > 1e-9 for x in ahorros), len(ahorros), 100.0 * sum(ahorros) / len(ahorros),
                        sum(abs(x) <= 1e-9 for x in ahorros), sum(x < -1e-9 for x in ahorros)))
        L.append("")
    if resumen:                                 # solo hubo Parte 1 (ningún caso de auditoría factible)
        L += ["## Resumen", ""] + resumen + [""]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Corre todos los casos y genera las evidencias.")
    ap.add_argument("--casos", required=True, help="directorio de casos (solo lectura)")
    ap.add_argument("--salida", required=True, help="directorio donde se regeneran las evidencias")
    ap.add_argument("--sin-tabla", "--sin_tabla", dest="sin_tabla", action="store_true",
                    help="no imprimir la tabla de comparación en la terminal (igual se guarda en comparacion.md)")
    args = ap.parse_args(argv)
    sin_tabla = args.sin_tabla

    casos = Path(args.casos).resolve()
    salida = Path(args.salida).resolve()
    if not casos.is_dir():
        sys.exit("No existe el directorio de casos: %s" % args.casos)
    if salida == casos:
        sys.exit("--salida no puede ser el mismo directorio que --casos (casos/ es de solo lectura).")
    archivos = sorted(p for p in casos.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONES)
    if not archivos:
        sys.exit("No hay casos .json ni .txt en %s" % args.casos)

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
        if archivo.suffix.lower() == ".json":
            fila, destino = correr_parte1(archivo, encabezado, salida, datos)
            filas.append((archivo.stem, "parte1", fila[0], fila[1], destino.name))
        for parte, fila, destino in correr_parte2_y_variante(archivo, encabezado, salida, datos):
            filas.append((archivo.stem, parte, fila[0], fila[1], destino.name))
        casos_datos.append((archivo.stem, datos))
        print("[%s] evidencias generadas" % archivo.stem)

    comparacion = tabla_comparacion(casos_datos, version, fecha)
    (salida / "comparacion.md").write_text(comparacion, encoding="utf-8")
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
           "python3 run_all.py --casos %s --salida %s" % (args.casos, args.salida), len(archivos)),
        encoding="utf-8")

    errores = sum(1 for f in filas if f[2].startswith("ERROR"))
    print("Listo: %d casos, %d evidencias, %d errores. Resumen en %s"
          % (len(archivos), len(filas), errores, Path(args.salida) / "resumen.csv"))
    if sucio:
        print("Aviso: hay cambios sin commit; para la entrega, haz commit y vuelve a correr.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())