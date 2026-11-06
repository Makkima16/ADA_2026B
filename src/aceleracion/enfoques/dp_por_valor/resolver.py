"""Orquesta el enfoque de la DP por valor sobre una instancia (Parte 1).

Mismo papel que `aceleracion.resolver.resolver_caso` para la DP base y devuelve el
mismo `ResultadoCaso`; la diferencia es que `tabla` guarda C[i][v] (menor costo por
ahorro v), no DP[i][b]. No lee archivos ni escribe nada.
"""

import time

from aceleracion.resolver import InstanciaAceleracion, ResultadoCaso, solucion_valida
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA, fuerza_bruta

from .dp_por_valor import resolver_valor


def resolver_caso_valor(inst: InstanciaAceleracion, comparar_con_optimo: bool = True) -> ResultadoCaso:
    """Resuelve un caso con la DP por valor y arma el resultado para la evidencia.

    Lanza ErrorDeEntrada si la instancia no cumple las restricciones o si la tabla no cabe.
    El tiempo medido (perf_counter) es solo el del algoritmo. Con n <= 12 compara con la fuerza bruta.
    """
    t0 = time.perf_counter()
    res = resolver_valor(inst.t, inst.c, inst.d, inst.B)
    tiempo = time.perf_counter() - t0

    optimo = None
    if comparar_con_optimo and len(inst.c) <= N_MAX_FUERZA_BRUTA:
        optimo = fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"]
    return ResultadoCaso(
        inst.nombre, len(inst.c), inst.B, res["aceleradas"], res["costo"], res["ahorro"],
        sum(inst.t), res["duracion_final"], tiempo, res["tabla"],
        solucion_valida(inst, res["aceleradas"], res["costo"], res["ahorro"]), optimo, inst)
