#!/usr/bin/env python3
"""Genera casos aleatorios y los prueba de inmediato, todo desde la terminal.

Escribe los casos en `pruebas/casos_temporales/` y las evidencias en `pruebas/resultados_temporales/` (las dos se
vacían y se reescriben en cada corrida y están en .gitignore). Las evidencias las produce
`run_all.py`: aquí solo se generan los casos y se le pasa la carpeta.

    python3 probar_aleatorios.py                              # 20 casos aleatorios y los prueba
    python3 probar_aleatorios.py --cantidad 50 --semilla 7
    python3 probar_aleatorios.py --n-min 5 --n-max 12 --r-min 6 --r-max 10 --densidades ralo denso
    python3 probar_aleatorios.py --fijo                       # el juego fijo de 22 casos (n 10..20)
    python3 probar_aleatorios.py --fijo --malla               # 110 casos: todo n de 10..20 con todo r de 6..15
    python3 probar_aleatorios.py --solo-generar               # solo escribe los casos, no los prueba

Con n <= 12 también se compara contra el óptimo por fuerza bruta. Misma semilla = mismos casos.
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from generacion_casos import carpetas, generador, probar   # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera casos aleatorios en pruebas/casos_temporales/ y los prueba.")
    ap.add_argument("--cantidad", type=int, default=20, help="cuántos casos (por defecto 20)")
    ap.add_argument("--semilla", type=int, default=2026, help="semilla (por defecto 2026)")
    ap.add_argument("--n-min", type=int, default=8)
    ap.add_argument("--n-max", type=int, default=16)
    ap.add_argument("--r-min", type=int, default=6)
    ap.add_argument("--r-max", type=int, default=15)
    ap.add_argument("--densidades", nargs="+", default=list(generador.DENSIDADES), choices=list(generador.DENSIDADES),
                    help="densidades a sortear (por defecto todas)")
    ap.add_argument("--fijo", action="store_true", help="usar el juego fijo de 22 casos en vez de sortear")
    ap.add_argument("--malla", action="store_true", help="con --fijo: las 110 combinaciones n x r")
    ap.add_argument("--solo-generar", action="store_true", help="no probar, solo escribir los casos")
    args = ap.parse_args(argv)

    try:
        if args.fijo:
            lote = generador.generar_juego_fijo(args.semilla, args.malla)
        else:
            lote = generador.generar_lote(args.cantidad, args.semilla, args.n_min, args.n_max,
                                          args.r_min, args.r_max, args.densidades)
    except generador.ErrorDeParametros as e:
        sys.exit("Parámetros inválidos: %s" % e)
    carpetas.escribir_casos(lote)
    print("Generados %d casos en %s/ (semilla %d)." % (len(lote), carpetas.NOMBRE_CASOS, args.semilla))
    if args.solo_generar:
        return 0

    print("Probando con run_all.py ...")
    proceso = probar.probar()
    print(proceso.stdout.rstrip())
    if proceso.returncode not in (0, 1):               # 1 = algún caso dio ERROR (queda en su evidencia)
        print(proceso.stderr.rstrip(), file=sys.stderr)
        return proceso.returncode
    print()
    print(probar.leer_comparacion())
    print("Evidencias en %s/ (resumen.csv, comparacion.md y una traza por caso)." % carpetas.NOMBRE_RESULTADOS)
    return proceso.returncode


if __name__ == "__main__":
    sys.exit(main())
