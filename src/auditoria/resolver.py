"""Orquesta la Parte 2 sobre una instancia: factibilidad, voraz, tiempo y verificación.

No lee archivos ni escribe nada: recibe una `Instancia` ya construida (la
lectura de los casos de la profesora debe producir objetos `Instancia`) y
devuelve un `ResultadoCaso` con datos puros. La escritura vive en `traza.py`.
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
    # Etiquetas opcionales (las llena el lector si el archivo las trae; el
    # algoritmo nunca las usa, solo la traza para mostrar nombres legibles).
    ids_interaccion: Optional[Sequence[str]] = None     # p. ej. "E01" para la interacción 1
    ids_categoria: Optional[Sequence[str]] = None       # p. ej. "R01" para la categoría 1
    nombres_categoria: Optional[Sequence[str]] = None   # p. ej. "sesgo" para la categoría 1
    importancia: Optional[Sequence[int]] = None         # importancia de cada categoría (guardada, sin usar)

    def etiqueta_interaccion(self, j: int) -> str:
        """Nombre de la interacción j (1..n): su id si existe, si no el número."""
        return self.ids_interaccion[j - 1] if self.ids_interaccion else str(j)

    def etiqueta_categoria(self, c: int) -> str:
        """Nombre de la categoría c (1..r): su id si existe, si no el número."""
        return self.ids_categoria[c - 1] if self.ids_categoria else str(c)


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
    instancia: Optional[Instancia] = None  # para que la traza pueda mostrar los nombres


def resolver_caso(inst: Instancia, comparar_con_optimo: bool = True) -> ResultadoCaso:
    """Resuelve un caso con el voraz y arma el resultado para la evidencia.

    Si la instancia no es factible no corre el voraz: informa las categorías
    sin cubrir (la guía pide detenerse en ese caso).
    """
    n = len(inst.S)
    factible, sin_cubrir = verificar_factibilidad(inst.r, inst.S)
    cota = cota_aproximacion(inst.S)
    if not factible:
        return ResultadoCaso(inst.nombre, n, inst.r, False, frozenset(sin_cubrir),
                             [], [], {}, False, 0.0, cota, None, inst)

    t0 = time.perf_counter()
    J, pasos = voraz(inst.r, inst.S)
    tiempo = time.perf_counter() - t0

    optimo = None
    if comparar_con_optimo and n <= N_MAX_FUERZA_BRUTA:
        optimo = fuerza_bruta(inst.r, inst.S)
    return ResultadoCaso(inst.nombre, n, inst.r, True, frozenset(), J, pasos,
                         cobertura_final(inst.S, J), cubre_todo(inst.r, inst.S, J),
                         tiempo, cota, optimo, inst)


# Costo de resolver_caso: lo domina el voraz, O(n·r·min(n, r)); la factibilidad y la cota son
# O(n·r). La fuerza bruta (n <= 12) queda fuera de la medición de tiempo.
