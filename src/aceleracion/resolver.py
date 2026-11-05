"""Orquesta la Parte 1 sobre una instancia: validación, DP, tiempo y verificación.

No lee archivos ni escribe nada: recibe una `InstanciaAceleracion` ya
construida (la produce `lectura.py`) y devuelve un `ResultadoCaso` con datos
puros. La escritura del texto vive en `traza.py`.

Es el equivalente de `auditoria/resolver.py` de la Parte 2: lo que usa el
programa que corre todos los casos.

Costo por línea: `# costo: OE × veces`, con el modelo del curso explicado al inicio de
`aceleracion.py` (cada asignación, comparación, operación aritmética, acceso a un
atributo o a una lista, return o llamada cuesta 1; la cabecera de un `for` de m vueltas
cuesta 3 × (m + 1) y su cuerpo m veces; el cuerpo de una función llamada se analiza
aparte). Variables: n = etapas, B = presupuesto, k = etapas aceleradas. Al final de cada
función se arma T(n) (suma de costos -> agrupación) y al final del archivo está el resumen
del mejor caso, el peor y el promedio.
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
        return self.ids_etapa[i - 1] if self.ids_etapa else str(i)   # costo: 4 × 1 sin ids (condición 2, str 1, return 1) o 6 × 1 con ids (condición 2, atributo + i-1 + acceso 3, return 1)  -> constante


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
    n = len(inst.c)                                                 # costo: 3 × 1   (atributo, len, asignación)
    sin_repetir = len(set(aceleradas)) == len(aceleradas)           # costo: 1 + k + 4   (llamar set y recorrer los k elementos; 2 len, comparación, asignación)
    en_rango = all(1 <= i <= n for i in aceleradas)                 # costo: 1 + 3 × (k+1) + 2 × k + 1   (llamar all; cabecera del generador k+1 veces; 2 comparaciones por elemento; asignar)   (si falla el primero, all corta: ≈ 8)
    if not (sin_repetir and en_rango):                              # costo: 3 × 1   (and, not, prueba)
        return False                                                # costo: solo si es inválida (termina aquí)
    costo_real = sum(inst.c[i - 1] for i in aceleradas)             # costo: 1 + 3 × (k+1) + 4 × k + 1   (llamar sum; cabecera k+1 veces; por elemento: atributo, i-1, acceso, acumular; asignar)
    ahorro_real = sum(inst.d[i - 1] for i in aceleradas)            # costo: 1 + 3 × (k+1) + 4 × k + 1
    return costo_real == costo and ahorro_real == ahorro and costo_real <= inst.B   # costo: 7 × 1   (3 comparaciones, 2 and, atributo, return)
    # Suma de costos:  T = 3 + (k + 5) + (5k + 5) + 3 + (7k + 5) + (7k + 5) + 7
    # Agrupación:      T(k) = 20k + 33          con 0 <= k <= n
    # Orden de crecimiento: Θ(n)  (mejor caso k = 0: 33; peor caso k = n: 20n + 33)


def resolver_caso(inst: InstanciaAceleracion, comparar_con_optimo: bool = True) -> ResultadoCaso:
    """Resuelve un caso con la DP y arma el resultado para la evidencia.

    Lanza ErrorDeEntrada si la instancia no cumple las restricciones. El
    tiempo medido (perf_counter) es solo el de la DP, no el de la lectura ni
    el de la fuerza bruta. Con n <= 12 compara el ahorro con la fuerza bruta.
    """
    t0 = time.perf_counter()                                        # costo: 3 × 1   (atributo, llamada, asignación)
    res = resolver(inst.t, inst.c, inst.d, inst.B)                  # costo: 6 × 1 + T_resolver   (4 atributos, llamada, asignación)   # T = O(n·B): validación, tabla y reconstrucción
    tiempo = time.perf_counter() - t0                               # costo: 4 × 1   (atributo, llamada, resta, asignación)

    optimo = None                                                   # costo: 1 × 1
    if comparar_con_optimo and len(inst.c) <= N_MAX_FUERZA_BRUTA:   # costo: 5 × 1   (prueba, and, atributo, len, comparación)
        optimo = fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"]   # costo: 7 × 1 + T_fuerza_bruta, solo si n <= 12   # O(2^n·n), solo n <= 12
    return ResultadoCaso(                                           # costo: n + 33 × 1   (sum(inst.t) cuesta 1 + 1 + n; el resto son ~30 accesos, llamadas y asignaciones del constructor), más:
        inst.nombre, len(inst.c), inst.B, res["aceleradas"], res["costo"], res["ahorro"],
        sum(inst.t), res["duracion_final"], tiempo, res["tabla"],
        solucion_valida(inst, res["aceleradas"], res["costo"], res["ahorro"]), optimo, inst)   # costo: 20k + 33   (solucion_valida)
    # Suma de costos:  T = 3 + (6 + T_resolver) + 4 + 1 + 5 + [7 + T_fuerza_bruta si n <= 12] + (n + 33) + (20k + 33)
    # Agrupación:      T = T_resolver + n + 20k + 85   (+ 7 + T_fuerza_bruta si n <= 12)
    # Orden de crecimiento: Θ(n·B)  (lo domina T_resolver)


# =============================================================================
# RESUMEN DE COSTO DEL ARCHIVO
# n = etapas, B = presupuesto, k = etapas aceleradas (0 <= k <= n), p = fracción de celdas de la
# tabla donde la etapa cabe en el presupuesto (0 <= p <= 1).
# T_resolver sale de `aceleracion.py`: mejor 12nB + 76n + B + 73; peor 26nB + 102n + B + 73.
#
# Función                Mejor caso                   Peor caso                    Promedio
# ---------------------  ---------------------------  ---------------------------  ------------------------------
# etiqueta_etapa         4                            6                            4 a 6
# solucion_valida        33  (k = 0)                  20n + 33  (k = n)            20k + 33, k típico ~ n/2    -> Θ(n)
# resolver_caso          12nB + 77n + B + 158         26nB + 123n + B + 158        (12+14p)·nB + ...           -> Θ(n·B)
#
# Con n <= 12 se suma además la fuerza bruta (≈ (9n + 11)·2^n operaciones). Como n está acotado
# por 12, es una constante (≈ 492 mil como máximo) y no cambia el orden Θ(n·B).
# `solucion_valida` y la fuerza bruta están FUERA de la medición de tiempo (`tiempo_s`),
# que mide solo `resolver`.
#
# Conclusión: el costo de resolver un caso lo domina la DP (n·B), igual en el mejor, el peor y el
# promedio (Θ(n·B)); todo lo que agrega este archivo (validar, comparar, armar el resultado)
# es Θ(n) o constante.
#
# Este archivo no tiene ciclos con estado que requieran invariante: los únicos ciclos son los
# generadores de `solucion_valida`, que solo acumulan una suma. La correctitud de la solución la
# aseguran los invariantes de `aceleracion.py` (llenar_tabla y reconstruir).
# =============================================================================
