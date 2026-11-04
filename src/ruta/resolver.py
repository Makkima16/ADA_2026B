"""Orquesta la Parte 2 sobre una instancia: factibilidad, voraz, tiempo y verificación.

No lee archivos ni escribe nada: recibe una `Instancia` ya construida (la
lectura de los casos de la profesora debe producir objetos `Instancia`) y
devuelve un `ResultadoCaso` con datos puros. La escritura vive en `traza.py`.

Anotación de costos: C (k) es una línea de costo constante con k operaciones
elementales; O(...) es el costo asintótico de la línea o de la función.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set

from .auditoria import (
    N_MAX_FUERZA_BRUTA,
    Paso,
    cobertura_final,
    cota_aproximacion,
    cubre_todo,
    fuerza_bruta,
    verificar_factibilidad,
    voraz,
)


@dataclass(frozen=True)
class Instancia:
    """Una instancia de la Parte 2: nombre del caso, r categorías y n conjuntos S_j."""

    nombre: str
    r: int
    S: Sequence[Set[int]]


@dataclass(frozen=True)
class ResultadoCaso:
    nombre: str
    n: int
    r: int
    factible: bool
    sin_cubrir: frozenset                 # categorías que nadie cubre (si no es factible)
    J: List[int]                          # interacciones auditadas, en orden de elección
    pasos: List[Paso]
    cobertura: Dict[int, int]             # categoría -> interacción que la cubre
    cubre: bool                           # comprobación independiente de la cobertura
    tiempo_s: float                       # solo el voraz (incluye su factibilidad)
    cota: float                           # H(d), d = máx |S_j|
    optimo: Optional[List[int]]           # por fuerza bruta; None si n > N_MAX_FUERZA_BRUTA


def resolver_caso(inst: Instancia, comparar_con_optimo: bool = True) -> ResultadoCaso:
    """Resuelve un caso con el voraz y arma el resultado para la evidencia.

    Si la instancia no es factible no corre el voraz: informa las categorías
    sin cubrir (la guía pide detenerse en ese caso).
    """
    n = len(inst.S)                                                  # C (1)
    factible, sin_cubrir = verificar_factibilidad(inst.r, inst.S)    # O(n·r): factibilidad previa
    cota = cota_aproximacion(inst.S)                                 # O(n + r): máximo |S_j| y H(d)
    if not factible:                                                 # C (1): comparación
        return ResultadoCaso(inst.nombre, n, inst.r, False, frozenset(sin_cubrir),
                             [], [], {}, False, 0.0, cota, None)     # C: se detiene sin ejecutar el voraz

    t0 = time.perf_counter()                                         # C (1): marca de tiempo
    J, pasos = voraz(inst.r, inst.S)                                 # O(n·r·min(n, r)): el algoritmo, dentro de la medición
    tiempo = time.perf_counter() - t0                                # C (1): tiempo transcurrido

    optimo = None                                                    # C (1)
    if comparar_con_optimo and n <= N_MAX_FUERZA_BRUTA:              # C (2): comparación y umbral
        optimo = fuerza_bruta(inst.r, inst.S)                        # O(2^n·n·r) solo si n <= 12
    return ResultadoCaso(inst.nombre, n, inst.r, True, frozenset(), J, pasos,
                         cobertura_final(inst.S, J), cubre_todo(inst.r, inst.S, J),
                         tiempo, cota, optimo)                       # O(n·r): cobertura_final + cubre_todo al armar el resultado
