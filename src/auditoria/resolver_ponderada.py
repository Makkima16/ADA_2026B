"""Orquesta la Variante 1 sobre una instancia: factibilidad, voraz ponderado, tiempo y verificación.

Reutiliza la `Instancia` de la Parte 2 (categorías y nombres) y recibe aparte la
lista de costos a_j. No lee archivos ni escribe nada: devuelve datos puros.
La escritura vive en `traza_ponderada.py`.  [Integrante 3]

Anotación de costos: C (k) es una línea de costo constante con k operaciones
elementales; O(...) es el costo asintótico de la línea o de la función.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .auditoria import cobertura_final, cota_aproximacion, cubre_todo, verificar_factibilidad
from .ponderada import PasoPonderado, validar_costos, voraz_ponderado
from .resolver import Instancia
from .verificacion_exacta import optimo_de_referencia


@dataclass(frozen=True)
class ResultadoPonderado:
    nombre: str
    n: int
    r: int
    factible: bool
    sin_cubrir: frozenset                 # categorías que nadie cubre (si no es factible)
    costos: List[float]                   # a_1..a_n
    J: List[int]                          # interacciones auditadas, en orden de elección
    costo: float                          # sum_{j en J} a_j
    pasos: List[PasoPonderado]
    cobertura: Dict[int, int]             # categoría -> interacción que la cubre
    cubre: bool                           # comprobación independiente de la cobertura
    tiempo_s: float                       # solo el voraz ponderado (incluye su factibilidad)
    cota: float                           # H(d), d = máx |S_j|
    optimo_costo: Optional[float]         # mínimo real; None si no se puede calcular
    optimo_J: Optional[List[int]]
    instancia: Optional[Instancia] = None  # para que la traza muestre los nombres
    optimo_metodo: str = ""                # cómo se obtuvo el óptimo: fuerza bruta (<= 12 opciones) o subconjuntos de categorías (r <= 16)


def resolver_caso_ponderado(inst: Instancia, costos: Sequence[float],
                            comparar_con_optimo: bool = True) -> ResultadoPonderado:
    """Resuelve un caso con el voraz ponderado y arma el resultado para la evidencia.

    Si la instancia no es factible no corre el voraz: informa las categorías sin cubrir.
    """
    n = len(inst.S)                                                  # C (1)
    a = list(costos)                                                 # O(n)
    validar_costos(inst.S, a)                                        # O(n): a_j > 0, uno por interacción
    factible, sin_cubrir = verificar_factibilidad(inst.r, inst.S)    # O(n·r)
    cota = cota_aproximacion(inst.S)                                 # O(n + r)
    if not factible:                                                 # C (1)
        return ResultadoPonderado(inst.nombre, n, inst.r, False, frozenset(sin_cubrir), a,
                                  [], 0, [], {}, False, 0.0, cota, None, None, inst)

    t0 = time.perf_counter()                                         # C (1)
    J, costo, pasos = voraz_ponderado(inst.r, inst.S, a)             # O(n·r·min(n, r)): el algoritmo, dentro de la medición
    tiempo = time.perf_counter() - t0                                # C (1)

    opt_costo, opt_J, metodo = None, None, ""                        # C (3)
    if comparar_con_optimo:                                          # C (1)
        ref = optimo_de_referencia(inst.r, inst.S, a)                # fuerza bruta (n <= 12) o subconjuntos de categorías (r <= 16)
        if ref is not None:
            opt_costo, opt_J, metodo = ref
    return ResultadoPonderado(inst.nombre, n, inst.r, True, frozenset(), a, J, costo, pasos,
                              cobertura_final(inst.S, J), cubre_todo(inst.r, inst.S, J),
                              tiempo, cota, opt_costo, opt_J, inst, metodo)  # O(n·r)
