#!/usr/bin/env python3
"""Pruebas aleatorias de la Parte 1: cuándo conviene cada tabla (por presupuesto o por valor).

Genera instancias aleatorias con semilla fija y, para cada una, mide el tamaño de las dos tablas, corre las dos
DP (si caben en el tope de este experimento) y las compara entre sí y, con n <= 12, con la fuerza bruta. Las dos
DP son exactas: siempre deben dar el mismo ahorro. Lo que se mide es cuántas celdas y cuánto tiempo gasta cada una
según la relación entre B y D = suma de los ahorros.

Uso (desde la raíz del proyecto):

    python3 src/aceleracion/enfoques/dp_por_valor/pruebas_aleatorias.py [--instancias N] [--semilla S]
        [--n-min A --n-max B] [--costo-min A --costo-max B] [--ahorro-min A --ahorro-max B] [--presupuesto-pct P]
"""

import argparse
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

SRC = Path(__file__).resolve().parents[3]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada, resolver  # noqa: E402
from aceleracion.enfoques.dp_por_valor.dp_por_valor import resolver_valor  # noqa: E402
from aceleracion.enfoques.seleccion import PRESUPUESTO, VALOR, elegir_enfoque, tamanos_de_tablas  # noqa: E402
from aceleracion.resolver import InstanciaAceleracion  # noqa: E402
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA, fuerza_bruta  # noqa: E402

# Una tabla solo se corre en el experimento si tiene a lo sumo estas celdas (para no tardar minutos).
CELDAS_EXPERIMENTO = 1_500_000
MAX_INSTANCIAS = 500
PRESUPUESTO_DE_TIEMPO_S = 25.0
REGIONES = ("B menor que D", "B igual a D", "B mayor que D")


class ErrorDeParametros(ValueError):
    """Parámetros fuera de rango."""


def validar(instancias, n_min, n_max, costo_min, costo_max, ahorro_min, ahorro_max, presupuesto_pct):
    if not 1 <= instancias <= MAX_INSTANCIAS:
        raise ErrorDeParametros("la cantidad de instancias debe estar entre 1 y %d" % MAX_INSTANCIAS)
    if not 1 <= n_min <= n_max <= 400:
        raise ErrorDeParametros("n debe cumplir 1 <= mínimo <= máximo <= 400")
    if not 0 <= costo_min <= costo_max <= 10 ** 7:
        raise ErrorDeParametros("los costos deben cumplir 0 <= mínimo <= máximo <= 10.000.000")
    if not 0 <= ahorro_min <= ahorro_max <= 10 ** 5:
        raise ErrorDeParametros("los ahorros deben cumplir 0 <= mínimo <= máximo <= 100.000")
    if not 0 <= presupuesto_pct <= 500:
        raise ErrorDeParametros("el presupuesto debe ser entre 0 % y 500 % del costo total")


def _generar(rng: random.Random, n_min, n_max, costo_min, costo_max, ahorro_min, ahorro_max, pct) -> InstanciaAceleracion:
    n = rng.randint(n_min, n_max)
    c = [rng.randint(costo_min, costo_max) for _ in range(n)]
    d = [rng.randint(ahorro_min, ahorro_max) for _ in range(n)]
    t = [x + rng.randint(0, 10) for x in d]
    return InstanciaAceleracion("aleatoria", t, c, d, int(sum(c) * pct / 100))


def _medir(f, inst):
    t0 = time.perf_counter()
    r = f(inst.t, inst.c, inst.d, inst.B)
    return r["ahorro"], time.perf_counter() - t0


def experimento(instancias=200, semilla=2026, n_min=5, n_max=30, costo_min=1, costo_max=30,
                ahorro_min=1, ahorro_max=30, presupuesto_pct=50.0,
                presupuesto_de_tiempo_s: Optional[float] = PRESUPUESTO_DE_TIEMPO_S) -> Dict:
    """Corre el experimento y devuelve los conteos. Con semilla fija y sin corte por tiempo es reproducible."""
    validar(instancias, n_min, n_max, costo_min, costo_max, ahorro_min, ahorro_max, presupuesto_pct)
    rng = random.Random(semilla)
    inicio = time.perf_counter()
    recomendado = {PRESUPUESTO: 0, VALOR: 0, "empate": 0, "ninguna": 0}
    regiones = {nombre: {"casos": 0, "corridas": 0, "celdas_presupuesto": 0, "celdas_valor": 0,
                         "tiempo_presupuesto": 0.0, "tiempo_valor": 0.0, "regla_mas_rapida": 0, "regla_valida": 0}
                for nombre in REGIONES}
    ambas = {"corridas": 0, "coinciden": 0}
    fb = {"comparadas": 0, "presupuesto_ok": 0, "valor_ok": 0}
    no_corridas = {PRESUPUESTO: 0, VALOR: 0}
    hechas = 0
    detenido = False
    for _ in range(instancias):
        if presupuesto_de_tiempo_s is not None and time.perf_counter() - inicio > presupuesto_de_tiempo_s:
            detenido = True
            break
        inst = _generar(rng, n_min, n_max, costo_min, costo_max, ahorro_min, ahorro_max, presupuesto_pct)
        hechas += 1
        celdas = tamanos_de_tablas(inst)
        D = sum(inst.d)
        region = REGIONES[0] if inst.B < D else REGIONES[1] if inst.B == D else REGIONES[2]
        reg = regiones[region]
        reg["casos"] += 1
        try:
            elegido = elegir_enfoque(inst)
            recomendado["empate" if celdas[PRESUPUESTO] == celdas[VALOR] else elegido] += 1
        except ErrorDeEntrada:
            elegido = None
            recomendado["ninguna"] += 1
        correr = {k: celdas[k] <= min(CELDAS_EXPERIMENTO, MAX_CELDAS_TABLA) for k in (PRESUPUESTO, VALOR)}
        resultado = {}
        if correr[PRESUPUESTO]:
            resultado[PRESUPUESTO] = _medir(resolver, inst)
        else:
            no_corridas[PRESUPUESTO] += 1
        if correr[VALOR]:
            resultado[VALOR] = _medir(resolver_valor, inst)
        else:
            no_corridas[VALOR] += 1
        if len(resultado) == 2:
            (ap, tp), (av, tv) = resultado[PRESUPUESTO], resultado[VALOR]
            ambas["corridas"] += 1
            ambas["coinciden"] += ap == av
            reg["corridas"] += 1
            reg["celdas_presupuesto"] += celdas[PRESUPUESTO]
            reg["celdas_valor"] += celdas[VALOR]
            reg["tiempo_presupuesto"] += tp
            reg["tiempo_valor"] += tv
            if celdas[PRESUPUESTO] != celdas[VALOR]:
                reg["regla_valida"] += 1
                mas_rapida = PRESUPUESTO if tp < tv else VALOR
                reg["regla_mas_rapida"] += mas_rapida == (PRESUPUESTO if celdas[PRESUPUESTO] < celdas[VALOR] else VALOR)
        if len(inst.c) <= N_MAX_FUERZA_BRUTA and resultado:
            optimo = fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"]
            fb["comparadas"] += 1
            fb["presupuesto_ok"] += PRESUPUESTO in resultado and resultado[PRESUPUESTO][0] == optimo
            fb["valor_ok"] += VALOR in resultado and resultado[VALOR][0] == optimo
    return {"parametros": {"instancias": instancias, "semilla": semilla, "n": [n_min, n_max], "costo": [costo_min, costo_max],
                           "ahorro": [ahorro_min, ahorro_max], "presupuesto_pct": presupuesto_pct},
            "hechas": hechas, "detenido_por_tiempo": detenido, "recomendado": recomendado, "ambas": ambas,
            "fuerza_bruta": fb, "no_corridas": no_corridas, "regiones": regiones,
            "limite_celdas": min(CELDAS_EXPERIMENTO, MAX_CELDAS_TABLA)}


def formatear(r: Dict) -> str:
    """Informe de texto del experimento."""
    p = r["parametros"]
    L = ["%d instancias aleatorias (semilla %d): n en %s, costos en %s, ahorros en %s, B = %s %% del costo total." % (
        r["hechas"], p["semilla"], p["n"], p["costo"], p["ahorro"], p["presupuesto_pct"])]
    if r["detenido_por_tiempo"]:
        L.append("(Se detuvo por tiempo antes de las %d pedidas.)" % p["instancias"])
    rec = r["recomendado"]
    L += ["", "Tabla más chica (la que recomienda la selección): presupuesto %d · valor %d · empate %d · ninguna cabe %d" % (
        rec[PRESUPUESTO], rec[VALOR], rec["empate"], rec["ninguna"]),
        "Se corrieron las dos DP en %d instancias; dieron el mismo ahorro en %d." % (r["ambas"]["corridas"], r["ambas"]["coinciden"]),
        "Contra la fuerza bruta (n <= 12), %d instancias: presupuesto acertó %d, valor acertó %d." % (
            r["fuerza_bruta"]["comparadas"], r["fuerza_bruta"]["presupuesto_ok"], r["fuerza_bruta"]["valor_ok"]),
        "No se corrieron por pasarse de %d celdas: presupuesto %d veces, valor %d veces." % (
            r["limite_celdas"], r["no_corridas"][PRESUPUESTO], r["no_corridas"][VALOR]), "",
        "%-16s %7s %9s | %14s %14s | %10s %10s | %s" % ("Relación", "casos", "con 2 DP", "celdas presup.", "celdas valor",
                                                     "ms presup.", "ms valor", "la de menos celdas fue más rápida")]
    for nombre in REGIONES:
        g = r["regiones"][nombre]
        k = g["corridas"] or 1
        regla = "%d de %d" % (g["regla_mas_rapida"], g["regla_valida"]) if g["regla_valida"] else "-"
        L.append("%-16s %7d %9d | %14.0f %14.0f | %10.3f %10.3f | %s" % (
            nombre, g["casos"], g["corridas"], g["celdas_presupuesto"] / k, g["celdas_valor"] / k,
            g["tiempo_presupuesto"] / k * 1000, g["tiempo_valor"] / k * 1000, regla))
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pruebas aleatorias: cuándo conviene cada tabla de la DP (Parte 1).")
    ap.add_argument("--instancias", type=int, default=200)
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--n-min", type=int, default=5)
    ap.add_argument("--n-max", type=int, default=30)
    ap.add_argument("--costo-min", type=int, default=1)
    ap.add_argument("--costo-max", type=int, default=30)
    ap.add_argument("--ahorro-min", type=int, default=1)
    ap.add_argument("--ahorro-max", type=int, default=30)
    ap.add_argument("--presupuesto-pct", type=float, default=50.0, help="B como %% del costo total (por defecto 50)")
    a = ap.parse_args(argv)
    try:
        print(formatear(experimento(a.instancias, a.semilla, a.n_min, a.n_max, a.costo_min, a.costo_max,
                                    a.ahorro_min, a.ahorro_max, a.presupuesto_pct)))
    except ErrorDeParametros as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
