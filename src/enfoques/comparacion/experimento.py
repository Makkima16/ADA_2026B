#!/usr/bin/env python3
"""Comparación de los enfoques con el voraz base (Parte 2, auditoría).

Compara, sobre las mismas instancias:
    voraz           el voraz base de `ruta.auditoria` (el de la entrega).
    esenciales      Enfoque A: primero las interacciones esenciales.
    vision_futuro   Enfoque B: vista al futuro de profundidad 2 (parejas).
    rareza          Enfoque C: puntúa cada categoría por 1/(cuántas la cubren).
    combinado       Enfoque D: esenciales + rareza + parejas (todo junto).
contra el óptimo exacto calculado por fuerza bruta (solo con n <= 12). Todo con semilla fija: mismo código = mismos resultados.

Uso (desde la raíz del proyecto):

    python3 src/enfoques/comparacion/experimento.py [--instancias 3000] [--semilla 2026]

El mismo módulo lo usa el visor local (`frontend/servidor.py`).
"""

import argparse
import random
import sys
import time
from math import comb
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from enfoques.combinado.combinado import voraz_combinado                      # noqa: E402
from enfoques.comparacion.ablacion import COMBINACIONES, clave, correr_combinacion  # noqa: E402
from enfoques.esenciales.esenciales import voraz_esenciales                    # noqa: E402
from enfoques.rareza.rareza import voraz_rareza                                # noqa: E402
from enfoques.vision_futuro.vision_futuro import voraz_futuro                  # noqa: E402
from ruta.auditoria import N_MAX_FUERZA_BRUTA, cota_aproximacion, fuerza_bruta, voraz  # noqa: E402

Instancia = Tuple[int, List[Set[int]]]    # (r, S)

NOMBRES = {
    "voraz": "Voraz normal",
    "esenciales": "Con esenciales",
    "vision_futuro": "Con parejas",
    "rareza": "Con rareza",
    "combinado": "Con todo",
}
ORDEN = ["voraz", "esenciales", "vision_futuro", "rareza", "combinado"]


# ---------------------------------------------------------------- ejecución

def _correr(nombre: str, r: int, S: Sequence[Set[int]]) -> dict:
    """Corre un método y devuelve J, la traza, las esenciales (si aplica) y el tiempo."""
    t0 = time.perf_counter()
    esenciales = None
    if nombre == "voraz":
        J, pasos = voraz(r, S)
    elif nombre == "esenciales":
        J, pasos, esenciales = voraz_esenciales(r, S)
    elif nombre == "combinado":
        J, pasos, esenciales = voraz_combinado(r, S)
    elif nombre == "rareza":
        J, pasos = voraz_rareza(r, S)
    else:
        J, pasos = voraz_futuro(r, S)
    return {"J": J, "pasos": pasos, "esenciales": esenciales, "tiempo_s": time.perf_counter() - t0}


def optimo_de(r: int, S: Sequence[Set[int]]) -> Optional[List[int]]:
    """Óptimo exacto por fuerza bruta si n <= 12; si no, None (no se calcula)."""
    return fuerza_bruta(r, S) if len(S) <= N_MAX_FUERZA_BRUTA else None


def comparar_caso(r: int, S: Sequence[Set[int]]) -> dict:
    """Corre las 8 combinaciones de ingredientes y, si n <= 12, el óptimo por fuerza bruta (para el visor).

    Las combinaciones se identifican con letras: '' (voraz base), e, r, p, er, ep, rp, erp.
    """
    metodos = {clave(e, ra, pa): correr_combinacion(r, S, e, ra, pa) for _, e, ra, pa in COMBINACIONES}
    optimo, tiempo_opt = None, None
    if len(S) <= N_MAX_FUERZA_BRUTA:
        t0 = time.perf_counter()
        optimo = fuerza_bruta(r, S)
        tiempo_opt = time.perf_counter() - t0
    return {"metodos": metodos, "optimo": optimo, "tiempo_optimo_s": tiempo_opt,
            "cota": cota_aproximacion(S), "cota_inferior": -(-r // max((len(s) for s in S), default=1))}


# --------------------------------------------------------------- generadores

def instancia_aleatoria(rng: random.Random, n: int, r: int, p: float) -> Instancia:
    """Factible: cada categoría va a una interacción al azar y luego cada par entra con prob. p."""
    S: List[Set[int]] = [set() for _ in range(n)]
    for c in range(1, r + 1):
        S[rng.randrange(n)].add(c)
    for s in S:
        for c in range(1, r + 1):
            if rng.random() < p:
                s.add(c)
    return r, S


def instancia_cebos(k: int) -> Instancia:
    """Familia donde el voraz base se equivoca: dos conjuntos A y B (de 2^k − 1 categorías cada uno,
    óptimo = 2) y k 'cebos' que mezclan ambas mitades (2^i de cada una, i = k−1, …, 0).
    Ninguna categoría es única de un cebo, así que no hay esenciales. El voraz usa k, el óptimo 2."""
    m = 2 ** k - 1
    A = set(range(1, m + 1))
    B = set(range(m + 1, 2 * m + 1))
    S = [A, B]
    ia = ib = 0
    for i in range(k - 1, -1, -1):
        parte_a = set(range(1 + ia, 1 + ia + 2 ** i))
        parte_b = set(range(m + 1 + ib, m + 1 + ib + 2 ** i))
        S.append(parte_a | parte_b)
        ia += 2 ** i
        ib += 2 ** i
    return 2 * m, S


FAMILIAS = {          # nombre -> probabilidad de agregar cada par (interacción, categoría)
    "ralo": 0.10,
    "medio": 0.25,
    "denso": 0.45,
}


# --------------------------------------------------------------- experimento

TAMANOS = {          # nombre -> (rango de n, rango de r)
    "pequenos": ((3, 12), (3, 14)),      # con mínimo real por fuerza bruta
    "grandes": ((20, 30), (10, 40)),     # sin mínimo real: solo se comparan los métodos entre sí
}


def experimento(familia: str, cantidad: int, semilla: int, tamano: str = "pequenos") -> dict:
    """Corre `cantidad` instancias aleatorias de la familia y resume qué tan bien queda cada método.

    Con tamano = "pequenos" (n <= 12) se compara también contra el mínimo real. Con "grandes"
    (n entre 20 y 30) no hay mínimo real: solo se compara cada enfoque con el voraz base.
    """
    p = FAMILIAS[familia]
    n_rango, r_rango = TAMANOS[tamano]
    rng = random.Random(semilla)
    res = {m: {"mejora": 0, "igual": 0, "peor": 0, "no_optimo": 0, "suma_razon": 0.0, "razon_max": 0.0,
               "no_optimo_mejor_de_dos": 0, "viola_cota": 0, "tiempo_s": 0.0} for m in ORDEN}
    sin_esenciales = 0
    con_optimo = tamano == "pequenos"
    for _ in range(cantidad):
        n = rng.randint(*n_rango)
        r = rng.randint(*r_rango)
        rr, S = instancia_aleatoria(rng, n, r, p)
        optimo = optimo_de(rr, S)
        opt = len(optimo) if optimo is not None else None
        corridas = {m: _correr(m, rr, S) for m in ORDEN}
        base = len(corridas["voraz"]["J"])
        cota = cota_aproximacion(S)
        if not corridas["esenciales"]["esenciales"]:
            sin_esenciales += 1
        for m in ORDEN:
            tam = len(corridas[m]["J"])
            e = res[m]
            e["tiempo_s"] += corridas[m]["tiempo_s"]
            if opt is not None:
                e["suma_razon"] += tam / opt
                e["razon_max"] = max(e["razon_max"], tam / opt)
                if tam > opt:
                    e["no_optimo"] += 1
                if tam > cota * opt + 1e-9:               # ¿se pasó de H(d) veces el óptimo?
                    e["viola_cota"] += 1
                if min(tam, base) > opt:
                    e["no_optimo_mejor_de_dos"] += 1
            if m != "voraz":
                e["mejora" if tam < base else "peor" if tam > base else "igual"] += 1
    for m in ORDEN:
        e = res[m]
        suma = e.pop("suma_razon")
        if con_optimo:
            e["razon_media"] = suma / cantidad
        else:                                   # sin mínimo real no hay razón ni "no óptimo"
            for k in ("razon_media", "razon_max", "no_optimo", "viola_cota", "no_optimo_mejor_de_dos"):
                e[k] = None
    return {"familia": familia, "p": p, "tamano": tamano, "n_rango": list(n_rango), "r_rango": list(r_rango),
            "con_optimo": con_optimo, "cantidad": cantidad, "semilla": semilla,
            "sin_esenciales": sin_esenciales, "metodos": res}


def experimento_cebos(ks: Sequence[int] = (2, 3, 4, 5)) -> List[dict]:
    """Resultados sobre la familia de cebos (óptimo = 2 por construcción, verificado)."""
    filas = []
    for k in ks:
        r, S = instancia_cebos(k)
        opt = optimo_de(r, S)
        fila = {"k": k, "n": len(S), "r": r, "optimo": len(opt) if opt else None}
        for m in ORDEN:
            fila[m] = len(_correr(m, r, S)["J"])
        fila["esenciales_halladas"] = len(voraz_esenciales(r, S)[2])
        filas.append(fila)
    return filas


def buscar_peor(metodo: str, semilla: int, intentos: int = 20000) -> Optional[dict]:
    """La instancia más chica (por n + r, luego por tamaño de entrada) donde `metodo` usa MÁS
    interacciones que el voraz normal. Sirve para documentar un caso donde el enfoque empeora."""
    rng = random.Random(semilla)
    mejor = None
    for _ in range(intentos):
        n = rng.randint(3, 12)
        r = rng.randint(3, 14)
        p = rng.choice(list(FAMILIAS.values()))
        rr, S = instancia_aleatoria(rng, n, r, p)
        if any(not s for s in S):                 # solo casos sin interacciones vacías (legibles y válidos en .txt)
            continue
        base = voraz(rr, S)[0]
        otro = _correr(metodo, rr, S)["J"]
        if len(otro) > len(base):
            clave = (n + rr, sum(len(s) for s in S))
            if mejor is None or clave < mejor["clave"]:
                opt = optimo_de(rr, S)
                mejor = {"clave": clave, "r": rr, "S": [sorted(s) for s in S], "voraz": base,
                         "metodo": otro, "optimo": opt}
    return mejor


def medir_tiempos(tamanos: Sequence[Tuple[int, int]], semilla: int, repeticiones: int = 3) -> List[dict]:
    """Tiempo (el mejor de varias repeticiones) de cada método con instancias cada vez más grandes."""
    rng = random.Random(semilla)
    filas = []
    for n, r in tamanos:
        rr, S = instancia_aleatoria(rng, n, r, 0.05)
        fila = {"n": n, "r": r, "pasos": len(voraz(rr, S)[1])}
        for m in ORDEN:
            fila[m] = min(_correr(m, rr, S)["tiempo_s"] for _ in range(repeticiones))
        filas.append(fila)
    return filas


# ----------------------------------------------------------------------- CLI

def _tabla_familia(e: dict) -> str:
    ls = ["Familia %-6s (p = %.2f) — %d instancias, n en %s, r en %s, semilla %d; sin esenciales: %d"
          % (e["familia"], e["p"], e["cantidad"], e["n_rango"], e["r_rango"], e["semilla"], e["sin_esenciales"]),
          "  %-22s %7s %7s %7s | %10s %11s %9s %10s | %s" %
          ("método", "mejora", "igual", "peor", "no óptimo", "razón media", "razón máx", "pasa H(d)", "no óptimo si se toma el mejor de los dos")]
    for m in ORDEN:
        x = e["metodos"][m]
        ref = "-" if m == "voraz" else "%d" % x["no_optimo_mejor_de_dos"]
        mej = "-" if m == "voraz" else str(x["mejora"])
        ig = "-" if m == "voraz" else str(x["igual"])
        pe = "-" if m == "voraz" else str(x["peor"])
        ls.append("  %-22s %7s %7s %7s | %10d %11.4f %9.4f %10d | %s" %
                  (NOMBRES[m], mej, ig, pe, x["no_optimo"], x["razon_media"], x["razon_max"], x["viola_cota"], ref))
    return "\n".join(ls)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compara el voraz base con los enfoques (Parte 2).")
    ap.add_argument("--instancias", type=int, default=3000, help="instancias aleatorias por familia")
    ap.add_argument("--semilla", type=int, default=2026)
    args = ap.parse_args(argv)

    print("== 1. Instancias aleatorias (óptimo por fuerza bruta) ==\n")
    for fam in FAMILIAS:
        print(_tabla_familia(experimento(fam, args.instancias, args.semilla)))
        print()
    print("== 2. Familia de cebos (óptimo = 2) ==")
    print("  %2s %4s %4s | %7s %7s %11s %9s %7s | %s" % ("k", "n", "r", "óptimo", "voraz", "esenciales", "parejas", "rareza", "todo"))
    for f in experimento_cebos():
        print("  %2d %4d %4d | %7s %7d %11d %9d %7d | %d   (esenciales halladas: %d)" %
              (f["k"], f["n"], f["r"], f["optimo"], f["voraz"], f["esenciales"], f["vision_futuro"],
               f["rareza"], f["combinado"], f["esenciales_halladas"]))
    print("\n== 3. Una instancia donde cada enfoque empeora (la más chica hallada) ==")
    for m in ("esenciales", "vision_futuro", "rareza", "combinado"):
        x = buscar_peor(m, args.semilla)
        if x is None:
            print("  %s: no se halló ninguna en la búsqueda" % NOMBRES[m])
            continue
        print("  %s: r = %d, S = %s" % (NOMBRES[m], x["r"], x["S"]))
        print("     voraz %s (%d) · enfoque %s (%d) · óptimo %s (%d)" %
              (x["voraz"], len(x["voraz"]), x["metodo"], len(x["metodo"]), x["optimo"], len(x["optimo"])))
    print("== 4. Instancias grandes (n entre 20 y 30; sin mínimo real) ==\n")
    print("  %-8s %-22s %7s %7s %7s | %s" % ("familia", "método", "mejora", "igual", "peor", "tiempo medio por caso"))
    for fam in FAMILIAS:
        e = experimento(fam, min(args.instancias, 300), args.semilla, "grandes")
        for m in ORDEN:
            x = e["metodos"][m]
            base = m == "voraz"
            print("  %-8s %-22s %7s %7s %7s | %.6f s" % (fam if m == "voraz" else "", NOMBRES[m],
                  "-" if base else x["mejora"], "-" if base else x["igual"], "-" if base else x["peor"],
                  x["tiempo_s"] / e["cantidad"]))
    print("\n== 5. Tiempos con instancias de tamaño creciente (segundos, el mejor de 3) ==")
    print("  %5s %5s %6s | %12s %12s %12s %12s %12s | %s" % ("n", "r", "pasos", "voraz", "esenciales", "parejas", "rareza", "todo", "todo / voraz"))
    for f in medir_tiempos([(20, 20), (40, 40), (80, 80), (120, 120), (160, 160)], args.semilla):
        print("  %5d %5d %6d | %12.6f %12.6f %12.6f %12.6f %12.6f | %.1f veces" %
              (f["n"], f["r"], f["pasos"], f["voraz"], f["esenciales"], f["vision_futuro"], f["rareza"], f["combinado"],
               f["combinado"] / max(f["voraz"], 1e-9)))
    print("\n== 6. Contribución de cada ingrediente (casos no óptimos de %d por familia) ==" % args.instancias)
    from enfoques.comparacion.ablacion import ablacion
    ab = ablacion(args.instancias, args.semilla)
    print("  %-24s %6s %6s %6s | %7s" % ("combinación", "ralo", "medio", "denso", "total"))
    for nombre, *_ in COMBINACIONES:
        print("  %-24s %6d %6d %6d | %7d" % (nombre, ab["ralo"][nombre], ab["medio"][nombre], ab["denso"][nombre], ab["total"][nombre]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
