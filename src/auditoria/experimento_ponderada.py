#!/usr/bin/env python3
"""Verificación experimental de la variante 1 (voraz ponderado): cota H(d) y tiempos.

Uso (desde la raíz del proyecto):

    python3 src/auditoria/experimento_ponderada.py [--instancias N] [--semilla S] [--sin-tiempos]

Con las mismas tres familias de densidad que el experimento de la Parte 2 (rala p = 0,10; media p = 0,25; densa p = 0,45)
genera N instancias por familia (por defecto 1000) con n entre 3 y 12, r entre 3 y 14 y costos enteros entre 1 y 20. En cada
una compara el costo del voraz ponderado con el costo mínimo real por fuerza bruta y con la cota H(d): debe cumplirse
costo(voraz) <= H(d) · costo(óptimo) siempre (Chvátal, 1979). Después mide el tiempo del voraz con n = r (mediana de 5
corridas) y lo divide entre n·r·min(n, r), que es lo que se deduce en la complejidad.

Semilla fija: mismo código y misma semilla dan los mismos resultados (los tiempos dependen de la máquina). Las tres
familias comparten UN solo generador aleatorio (se siembra una vez y se recorren rala, media y densa en ese orden): con la
semilla 2026 y 1000 instancias por familia da 735, 645 y 650 óptimos (2030 de 3000, 67,7 %), peor razón 1,909 y ninguna
instancia por encima de H(d), que son las cifras del documento de la variante 1.
"""

import argparse
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence

SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from auditoria.auditoria import cota_aproximacion                                          # noqa: E402
from auditoria.enfoques.comparacion.experimento import FAMILIAS, instancia_aleatoria      # noqa: E402
from auditoria.ponderada import fuerza_bruta_ponderada, voraz_ponderado                   # noqa: E402

N_RANGO = (3, 12)
R_RANGO = (3, 14)
COSTO_RANGO = (1, 20)
TAMANOS_TIEMPO = (20, 40, 80, 160, 320)
REPETICIONES = 5


def experimento(familia: str, cantidad: int, rng: random.Random) -> Dict:
    """Corre `cantidad` instancias de una familia con el generador `rng` (que se comparte entre familias).

    Devuelve cuántas veces el voraz fue óptimo, la razón media y máxima y cuántas veces superó H(d).
    """
    p = FAMILIAS[familia]
    razones: List[float] = []
    violan = 0
    for _ in range(cantidad):
        n, r = rng.randint(*N_RANGO), rng.randint(*R_RANGO)
        rr, S = instancia_aleatoria(rng, n, r, p)
        a = [rng.randint(*COSTO_RANGO) for _ in range(n)]
        _, costo, _ = voraz_ponderado(rr, S, a)
        optimo, _ = fuerza_bruta_ponderada(rr, S, a)
        razon = costo / optimo
        razones.append(razon)
        violan += razon > cota_aproximacion(S) + 1e-9
    return {"familia": familia, "p": p, "instancias": cantidad, "optimas": sum(abs(x - 1) < 1e-9 for x in razones),
            "razon_media": sum(razones) / cantidad, "razon_max": max(razones), "superan_cota": violan}


def correr(cantidad: int = 1000, semilla: int = 2026) -> List[Dict]:
    """Las tres familias con un único generador sembrado una vez."""
    rng = random.Random(semilla)
    return [experimento(f, cantidad, rng) for f in FAMILIAS]


def medir_tiempos(tamanos: Sequence[int] = TAMANOS_TIEMPO, semilla: int = 2026, repeticiones: int = REPETICIONES) -> List[Dict]:
    """Tiempo del voraz ponderado con n = r (familia rala), mediana de varias corridas, y su cociente con n·r·min(n, r)."""
    filas = []
    for n in tamanos:
        rng = random.Random(semilla)
        rr, S = instancia_aleatoria(rng, n, n, FAMILIAS["ralo"])
        a = [rng.randint(*COSTO_RANGO) for _ in range(n)]
        tiempos = []
        for _ in range(repeticiones):
            t0 = time.perf_counter()
            J, _, pasos = voraz_ponderado(rr, S, a)
            tiempos.append(time.perf_counter() - t0)
        t = statistics.median(tiempos)
        filas.append({"n": n, "pasos": len(pasos), "tiempo_ms": t * 1000, "cociente": t / (n * n * min(n, n))})
    return filas


def formatear(resultados: Sequence[Dict], tiempos: Sequence[Dict] = ()) -> str:
    total = sum(r["instancias"] for r in resultados)
    optimas = sum(r["optimas"] for r in resultados)
    L = ["Voraz ponderado contra el óptimo por fuerza bruta (%d instancias; n %d–%d, r %d–%d, costos %d–%d)." % (
        total, N_RANGO[0], N_RANGO[1], R_RANGO[0], R_RANGO[1], COSTO_RANGO[0], COSTO_RANGO[1]), "",
        "%-8s %-5s %10s %14s %12s %13s %13s" % ("Familia", "p", "Instancias", "Voraz óptimo", "Razón media", "Razón máxima", "Superan H(d)")]
    for r in resultados:
        L.append("%-8s %-5.2f %10d %8d (%4.1f%%) %12.3f %13.3f %13d" % (
            r["familia"], r["p"], r["instancias"], r["optimas"], 100.0 * r["optimas"] / r["instancias"],
            r["razon_media"], r["razon_max"], r["superan_cota"]))
    L += ["", "Total: óptimo en %d de %d (%.1f %%); peor razón %.3f; instancias que superan H(d): %d." % (
        optimas, total, 100.0 * optimas / total, max(r["razon_max"] for r in resultados), sum(r["superan_cota"] for r in resultados))]
    if tiempos:
        L += ["", "Tiempo del voraz con n = r (familia rala, mediana de %d corridas):" % REPETICIONES, "",
              "%6s %7s %13s %26s" % ("n = r", "Pasos", "Tiempo (ms)", "Tiempo / (n·r·min(n, r)) s")]
        for f in tiempos:
            L.append("%6d %7d %13.4f %26.2e" % (f["n"], f["pasos"], f["tiempo_ms"], f["cociente"]))
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Verificación experimental de la variante 1 (voraz ponderado).")
    ap.add_argument("--instancias", type=int, default=1000, help="instancias por familia (por defecto 1000)")
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--sin-tiempos", action="store_true", help="no medir los tiempos")
    a = ap.parse_args(argv)
    if a.instancias < 1:
        print("error: hace falta al menos una instancia por familia", file=sys.stderr)
        return 2
    resultados = correr(a.instancias, a.semilla)
    print(formatear(resultados, [] if a.sin_tiempos else medir_tiempos(semilla=a.semilla)))
    return 1 if any(r["superan_cota"] for r in resultados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
