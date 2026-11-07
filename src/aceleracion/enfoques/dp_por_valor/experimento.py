#!/usr/bin/env python3
"""Comparación de la DP base (por presupuesto) con la DP por valor (Parte 1).

Muestra dónde se cruzan: la base cuesta Θ(n·B) y la de valor Θ(n·D), con D = Σ d_i. Para cada familia
de instancias da el tamaño de cada tabla, el tiempo de cada una (donde cabe en memoria), si dan el mismo
ahorro y cuál elige `elegir_enfoque`. Todo con semilla fija: mismo código = mismos resultados.

Uso (desde la raíz del proyecto):

    python3 src/aceleracion/enfoques/dp_por_valor/experimento.py [--semilla S]
"""

import argparse
import random
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parents[3]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada  # noqa: E402
from aceleracion.enfoques.dp_por_valor.dp_por_valor import resolver_valor  # noqa: E402
from aceleracion.enfoques.seleccion import elegir_enfoque, tamanos_de_tablas  # noqa: E402
from aceleracion.aceleracion import resolver  # noqa: E402
from aceleracion.resolver import InstanciaAceleracion  # noqa: E402


def _instancia(rng, n, max_c, max_d, B):
    c = [rng.randint(1, max_c) for _ in range(n)]
    d = [rng.randint(1, max_d) for _ in range(n)]
    t = [x + rng.randint(0, 5) for x in d]
    return InstanciaAceleracion("exp", t, c, d, B)


def _medir(f, inst):
    t0 = time.perf_counter()
    r = f(inst.t, inst.c, inst.d, inst.B)
    return r["ahorro"], time.perf_counter() - t0


def _fila(nombre, inst):
    celdas = tamanos_de_tablas(inst)
    try:
        elegido = elegir_enfoque(inst)
    except ErrorDeEntrada:
        elegido = "ninguna cabe"
    ahorro_p = ahorro_v = t_p = t_v = None
    if celdas["presupuesto"] <= MAX_CELDAS_TABLA:
        ahorro_p, t_p = _medir(resolver, inst)
    if celdas["valor"] <= MAX_CELDAS_TABLA:
        ahorro_v, t_v = _medir(resolver_valor, inst)
    igual = "—" if ahorro_p is None or ahorro_v is None else ("sí" if ahorro_p == ahorro_v else "NO")
    ms = lambda x: "no cabe" if x is None else "%.1f ms" % (x * 1000)  # noqa: E731
    print("%-34s n=%-5d B=%-8d D=%-7d | celdas base %-11d valor %-11d | tiempo base %-9s valor %-9s | mismo ahorro: %-3s | elige: %s"
          % (nombre, len(inst.c), inst.B, sum(inst.d), celdas["presupuesto"], celdas["valor"], ms(t_p), ms(t_v), igual, elegido))


def main(argv=None):
    parser = argparse.ArgumentParser(description="DP base (por presupuesto) contra DP por valor.")
    parser.add_argument("--semilla", type=int, default=2026, help="semilla fija (por defecto 2026)")
    args = parser.parse_args(argv)
    rng = random.Random(args.semilla)

    print("DP base: Θ(n·B)   DP por valor: Θ(n·D), D = Σ d_i   (tope de memoria: %d celdas)\n" % MAX_CELDAS_TABLA)
    _fila("B grande, D chica", _instancia(rng, 60, 10, 3, 20000))
    _fila("B grande, D chica (más grande)", _instancia(rng, 200, 10, 3, 40000))
    _fila("B y D parecidos", _instancia(rng, 60, 10, 10, 300))
    _fila("B chico, D grande", _instancia(rng, 60, 10, 300, 40))
    _fila("B chico, D grande (más grande)", _instancia(rng, 200, 10, 300, 100))
    _fila("B enorme, D chica (base no cabe)", _instancia(rng, 50, 10, 3, 5_000_000))
    _fila("B y D enormes (nadie cabe)", _instancia(rng, 2000, 10, 300, 1_000_000))
    print("\nLa base gana cuando B < D, la de valor cuando D < B, y con B y D enormes ninguna cabe: "
          "entre las dos se paga Θ(n·mín(B, D)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
