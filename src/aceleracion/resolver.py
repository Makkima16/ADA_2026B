"""Orquesta la Parte 1 sobre una instancia: validación, DP, tiempo y verificación.

No lee archivos ni escribe nada: recibe una `InstanciaAceleracion` ya
construida (la produce `lectura.py`) y devuelve un `ResultadoCaso` con datos
puros. La escritura del texto vive en `traza.py`.

Es el equivalente de `auditoria/resolver.py` de la Parte 2: lo que usa el
programa que corre todos los casos.
"""

import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .aceleracion import resolver, validar_entrada
from .verificacion import N_MAX_FUERZA_BRUTA, fuerza_bruta


@dataclass
class InstanciaAceleracion:
    """Una instancia de la Parte 1: nombre del caso, t, c, d (por etapa) y presupuesto B."""
    nombre: str
    t: List[int]
    c: List[int]
    d: List[int]
    B: int
    ids_etapa: Tuple[str, ...] = ()       # opcional: "E01", "E02"... para la traza

    def etiqueta_etapa(self, i: int) -> str:
        """Nombre de la etapa i (1..n): su id si existe, si no el número."""
        return self.ids_etapa[i - 1] if self.ids_etapa else str(i)


@dataclass(frozen=True)
class ResultadoCaso:
    nombre: str
    n: int
    B: int
    aceleradas: List[int]                 # etapas aceleradas (A), numeradas desde 1
    costo: int
    ahorro: int
    duracion_original: int                # suma de todos los t_i
    duracion_final: int                   # duracion_original - ahorro
    tiempo_s: float                       # solo la DP (validación + tabla + reconstrucción)
    tabla: List[List[int]]                # DP[i][b], para la traza
    valida: bool                          # comprobación independiente de la solución
    optimo_ahorro: Optional[int]          # por fuerza bruta; None si n > N_MAX_FUERZA_BRUTA
    instancia: Optional[InstanciaAceleracion] = None   # para que la traza muestre los nombres


def solucion_valida(inst: InstanciaAceleracion, aceleradas: List[int], costo: int, ahorro: int) -> bool:
    """Comprueba por separado que A es factible y que costo y ahorro son los de A.  T = O(n)."""
    n = len(inst.c)
    sin_repetir = len(set(aceleradas)) == len(aceleradas)
    en_rango = all(1 <= i <= n for i in aceleradas)
    if not (sin_repetir and en_rango):
        return False
    costo_real = sum(inst.c[i - 1] for i in aceleradas)
    ahorro_real = sum(inst.d[i - 1] for i in aceleradas)
    return costo_real == costo and ahorro_real == ahorro and costo_real <= inst.B


def resolver_caso(inst: InstanciaAceleracion, comparar_con_optimo: bool = True) -> ResultadoCaso:
    """Resuelve un caso con la DP y arma el resultado para la evidencia.

    Lanza ErrorDeEntrada si la instancia no cumple las restricciones. El
    tiempo medido (perf_counter) es solo el de la DP, no el de la lectura ni
    el de la fuerza bruta. Con n <= 12 compara el ahorro con la fuerza bruta.
    """
    t0 = time.perf_counter()
    res = resolver(inst.t, inst.c, inst.d, inst.B)  # T = O(n·B): validación, tabla y reconstrucción
    tiempo = time.perf_counter() - t0

    optimo = None
    if comparar_con_optimo and len(inst.c) <= N_MAX_FUERZA_BRUTA:
        optimo = fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"]
    return ResultadoCaso(
        inst.nombre, len(inst.c), inst.B, res["aceleradas"], res["costo"], res["ahorro"],
        sum(inst.t), res["duracion_final"], tiempo, res["tabla"],
        solucion_valida(inst, res["aceleradas"], res["costo"], res["ahorro"]), optimo, inst)


# Costo de resolver_caso: lo domina la DP, T(n, B) = Θ(n·B); validar, armar el resultado y
# comprobar la solución (solucion_valida) son Θ(n). La fuerza bruta (n <= 12) queda fuera de la
# medición de tiempo y, por estar acotada, no cambia el orden.
