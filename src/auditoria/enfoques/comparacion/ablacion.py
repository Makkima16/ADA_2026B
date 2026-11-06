"""Contribución de cada ingrediente (Parte 2, auditoría).

Un voraz configurable con tres ingredientes que se encienden o apagan:
    esenciales   primero las interacciones que son la única que cubre alguna categoría.
    rareza       cada categoría pendiente vale 1/f(c) en vez de 1.
    parejas      se mira el mejor par de interacciones en vez de una sola.
Las 8 combinaciones dan el voraz base, los tres enfoques por separado, las tres
combinaciones de a dos y el enfoque combinado con los tres. Sirve para medir qué
aporta cada ingrediente. Todo con semilla fija.

Las combinaciones sin `parejas` cuestan O(n·r·min(n, r)); las que llevan `parejas`,
O(n²·r·min(n, r)).

Uso (desde la raíz del proyecto), con la tabla de las ocho combinaciones:

    python3 src/auditoria/enfoques/comparacion/ablacion.py [--instancias N] [--semilla S]

Genera N instancias aleatorias por familia de densidad (ralo, medio, denso; n <= 12 para poder
calcular el mínimo real por fuerza bruta) y cuenta, por combinación, cuántas veces no llega al
mínimo, cuántas mejora, empata o empeora al voraz base y cuánto se aleja del mínimo.
"""

import argparse
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

SRC = Path(__file__).resolve().parents[3]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from auditoria.enfoques.combinado.combinado import paso_parejas_rareza
from auditoria.enfoques.rareza.rareza import frecuencias, paso_rareza
from auditoria.enfoques.esenciales.esenciales import interacciones_esenciales
from auditoria.enfoques.vision_futuro.vision_futuro import paso_futuro
from auditoria.auditoria import Paso, paso_voraz, verificar_factibilidad

# (nombre, esenciales, rareza, parejas)
COMBINACIONES = [
    ("Voraz base", False, False, False),
    ("Esenciales", True, False, False),
    ("Rareza", False, True, False),
    ("Parejas", False, False, True),
    ("Esenciales + rareza", True, True, False),
    ("Esenciales + parejas", True, False, True),
    ("Rareza + parejas", False, True, True),
    ("Los tres (enfoque D)", True, True, True),
]


def clave(esenciales: bool, rareza: bool, parejas: bool) -> str:
    """Nombre corto de una combinación: letras e (esenciales), r (rareza), p (parejas); '' es el voraz base."""
    return ("e" if esenciales else "") + ("r" if rareza else "") + ("p" if parejas else "")


def voraz_ablacion_traza(r: int, S: Sequence[Set[int]], esenciales: bool, rareza: bool, parejas: bool
                         ) -> Tuple[List[int], List[Paso], Optional[List[int]]]:
    """Devuelve (J, traza como lista de Paso, esenciales) del voraz con los ingredientes indicados.

    Los pasos conservan el detalle de cada ingrediente: `PasoFuturo` (par ganador),
    `PasoRareza` (puntajes) o `PasoCombinado` (par y puntajes). `esenciales` es None si ese
    ingrediente está apagado. Lanza ValueError si la instancia no es factible.
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)
    if not factible:
        raise ValueError("instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir))
    f = frecuencias(r, S)
    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[Paso] = []
    ese = None
    if esenciales:
        ese = interacciones_esenciales(r, S)
        for j in ese:
            nuevas = set(S[j - 1]) & faltan
            faltan -= nuevas
            J.append(j)
            traza.append(Paso(j, frozenset(nuevas), frozenset(faltan)))
    while faltan:
        if parejas and rareza:
            paso = paso_parejas_rareza(S, faltan, f)
        elif parejas:
            paso = paso_futuro(S, faltan)
        elif rareza:
            paso = paso_rareza(S, faltan, f)
        else:
            paso = paso_voraz(S, faltan)
        J.append(paso.j)
        traza.append(paso)
    return J, traza, ese


def voraz_ablacion(r: int, S: Sequence[Set[int]], esenciales: bool, rareza: bool, parejas: bool) -> List[int]:
    """J del voraz con los ingredientes indicados. Lanza ValueError si no es factible."""
    return voraz_ablacion_traza(r, S, esenciales, rareza, parejas)[0]


def correr_combinacion(r: int, S: Sequence[Set[int]], esenciales: bool, rareza: bool, parejas: bool) -> dict:
    """Corre una combinación y devuelve J, pasos, esenciales y el tiempo (para el visor)."""
    t0 = time.perf_counter()
    J, pasos, ese = voraz_ablacion_traza(r, S, esenciales, rareza, parejas)
    return {"J": J, "pasos": pasos, "esenciales": ese, "tiempo_s": time.perf_counter() - t0}


def ablacion(cantidad: int, semilla: int) -> Dict[str, dict]:
    """Por familia (ralo, medio, denso) y en total: cuántas veces cada combinación no llega al óptimo."""
    from auditoria.enfoques.comparacion.experimento import FAMILIAS, TAMANOS, instancia_aleatoria, optimo_de
    (n_min, n_max), (r_min, r_max) = TAMANOS["pequenos"]
    salida: Dict[str, dict] = {}
    for fam, p in FAMILIAS.items():
        rng = random.Random(semilla)
        cuentas = {nombre: 0 for nombre, *_ in COMBINACIONES}
        for _ in range(cantidad):
            n = rng.randint(n_min, n_max)
            r = rng.randint(r_min, r_max)
            rr, S = instancia_aleatoria(rng, n, r, p)
            opt = len(optimo_de(rr, S))
            for nombre, e, ra, pa in COMBINACIONES:
                if len(voraz_ablacion(rr, S, e, ra, pa)) > opt:
                    cuentas[nombre] += 1
        salida[fam] = cuentas
    salida["total"] = {nombre: sum(salida[fam][nombre] for fam in FAMILIAS) for nombre, *_ in COMBINACIONES}
    return salida


def ablacion_detalle(cantidad: int, semilla: int, familias: Optional[Sequence[str]] = None,
                     ejemplos: int = 0) -> Dict[str, dict]:
    """Por combinación (suma de las familias): cuántas veces no llega al óptimo, cuántas mejora, empata o
    empeora al voraz base, la razón máxima respecto del óptimo y cuántas veces se pasa de H(d) veces el óptimo.

    `familias` elige las densidades (por defecto, ralo, medio y denso). Con `ejemplos` > 0 guarda, por combinación,
    hasta esa cantidad de las instancias más chicas donde empeoró al voraz base (clave `ejemplos`). `por_familia`
    desglosa `no_optimo`. Usa las mismas instancias que `ablacion` (misma semilla y mismo orden), así que
    `no_optimo` coincide con ella.
    """
    from auditoria.auditoria import cota_aproximacion
    from auditoria.enfoques.comparacion.experimento import FAMILIAS, TAMANOS, instancia_aleatoria, optimo_de
    (n_min, n_max), (r_min, r_max) = TAMANOS["pequenos"]
    elegidas = list(FAMILIAS) if familias is None else [f for f in FAMILIAS if f in familias]
    salida = {nombre: {"clave": clave(e, ra, pa), "no_optimo": 0, "mejora": 0, "igual": 0, "peor": 0,
                       "razon_max": 0.0, "viola_cota": 0} for nombre, e, ra, pa in COMBINACIONES}
    por_familia = {fam: {nombre: 0 for nombre, *_ in COMBINACIONES} for fam in elegidas}
    peores: Dict[str, list] = {nombre: [] for nombre, *_ in COMBINACIONES}
    total = 0
    for fam in elegidas:
        p = FAMILIAS[fam]
        rng = random.Random(semilla)
        for _ in range(cantidad):
            n = rng.randint(n_min, n_max)
            r = rng.randint(r_min, r_max)
            rr, S = instancia_aleatoria(rng, n, r, p)
            optimo = optimo_de(rr, S)
            opt = len(optimo)
            cota = cota_aproximacion(S)
            J_base = voraz_ablacion(rr, S, False, False, False)
            total += 1
            for nombre, e, ra, pa in COMBINACIONES:
                J = J_base if nombre == "Voraz base" else voraz_ablacion(rr, S, e, ra, pa)
                tam = len(J)
                d = salida[nombre]
                d["no_optimo"] += tam > opt
                por_familia[fam][nombre] += tam > opt
                d["razon_max"] = max(d["razon_max"], tam / opt)
                d["viola_cota"] += tam > cota * opt + 1e-9
                if nombre != "Voraz base":
                    d["mejora" if tam < len(J_base) else "peor" if tam > len(J_base) else "igual"] += 1
                    if tam > len(J_base) and ejemplos:
                        peores[nombre].append((n * rr, {"r": rr, "S": [sorted(s) for s in S], "familia": fam,
                                                        "voraz": list(J_base), "combinacion": list(J),
                                                        "optimo": list(optimo)}))
    salida["instancias"] = total
    salida["por_familia"] = por_familia
    if ejemplos:
        salida["ejemplos"] = {nombre: [x for _, x in sorted(lista, key=lambda y: y[0])[:ejemplos]]
                              for nombre, lista in peores.items() if lista}
    return salida


def formatear_detalle(d: Dict[str, dict], cantidad: int, semilla: int) -> str:
    """Tabla de texto con el resultado de `ablacion_detalle`."""
    total = d["instancias"]
    lineas = ["Ocho combinaciones sobre %d instancias aleatorias (3 familias x %d, n <= 12, semilla %d)." % (total, cantidad, semilla),
              "'Llega al mínimo' = usa tantas interacciones como el mínimo real (fuerza bruta). 'Frente al voraz base' = en cuántas usa menos / igual / más.",
              "",
              "%-22s %14s %9s | %8s %8s %8s | %10s %10s" % ("Combinación", "no llega al", "% de", "mejora", "igual", "peor", "razón", "pasa"),
              "%-22s %14s %9s | %8s %8s %8s | %10s %10s" % ("", "mínimo", "casos", "", "", "", "máxima", "H(d)")]
    for nombre, *_ in COMBINACIONES:
        x = d[nombre]
        base = nombre == "Voraz base"
        lineas.append("%-22s %14d %8.2f%% | %8s %8s %8s | %10.2f %10d" % (
            nombre, x["no_optimo"], x["no_optimo"] / total * 100,
            "-" if base else x["mejora"], "-" if base else x["igual"], "-" if base else x["peor"],
            x["razon_max"], x["viola_cota"]))
    lineas += ["", "Llegan al mínimo: " + ", ".join("%s %d" % (nombre, total - d[nombre]["no_optimo"]) for nombre, *_ in COMBINACIONES)]
    return "\n".join(lineas)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Tabla de las ocho combinaciones de ingredientes (Parte 2).")
    ap.add_argument("--instancias", type=int, default=3000, help="instancias aleatorias por familia (por defecto 3000)")
    ap.add_argument("--semilla", type=int, default=2026, help="semilla fija (por defecto 2026)")
    args = ap.parse_args(argv)
    print(formatear_detalle(ablacion_detalle(args.instancias, args.semilla), args.instancias, args.semilla))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
