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
"""

import random
import time
from typing import Dict, List, Optional, Sequence, Set, Tuple

from enfoques.combinado.combinado import paso_parejas_rareza
from enfoques.rareza.rareza import frecuencias, paso_rareza
from enfoques.esenciales.esenciales import interacciones_esenciales
from enfoques.vision_futuro.vision_futuro import paso_futuro
from ruta.auditoria import Paso, paso_voraz, verificar_factibilidad

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
    from enfoques.comparacion.experimento import FAMILIAS, TAMANOS, instancia_aleatoria, optimo_de
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
