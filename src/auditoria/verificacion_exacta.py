"""Óptimo exacto por subconjuntos de categorías. SOLO para verificar; no es un algoritmo de la entrega.

La fuerza bruta (`auditoria.fuerza_bruta`, `ponderada.fuerza_bruta_ponderada`) recorre los 2^n subconjuntos de
interacciones, así que solo sirve con n <= 12. Esta verificación recorre en cambio los subconjuntos de CATEGORÍAS ya
cubiertas: es exponencial en r y no en n, así que da el mínimo real con n grande (por ejemplo, las 20 etapas del ejemplo
de la profesora) siempre que r sea chico (r <= 16).

Idea. D[M] = costo mínimo para cubrir exactamente el conjunto de categorías M. Desde M se toma la primera categoría que
falta, b, y se prueba cada opción que la cubre: D[M ∪ S_j] = mín(D[M ∪ S_j], D[M] + a_j). Toda solución óptima cubre b con
alguna opción, así que no se pierde ninguna. Los estados se procesan en orden creciente (M ∪ S_j > M porque agrega b).
Con costos iguales a 1 da el mínimo número de interacciones (Parte 2); con costos a_j, el mínimo costo (variante 1).

Costo: a lo sumo 2^r estados y, en cada uno, las opciones que cubren la primera categoría que falta, o sea
O(2^r · m) con m opciones (en la práctica mucho menos: solo se visitan los estados alcanzables).
"""

from typing import List, Optional, Sequence, Set, Tuple

from .auditoria import N_MAX_FUERZA_BRUTA, fuerza_bruta, verificar_factibilidad
from .ponderada import fuerza_bruta_ponderada

R_MAX_EXACTO = 16                       # con r mayor, 2^r estados ya no son razonables para una verificación
METODO_FUERZA_BRUTA = "fuerza bruta"
METODO_SUBCONJUNTOS = "subconjuntos de categorías"


def minimo_por_subconjuntos(r: int, S: Sequence[Set[int]], costos: Optional[Sequence[float]] = None) -> Tuple[float, List[int]]:
    """(costo mínimo, J) con J en el orden en que se cubrió. Sin `costos`, cada interacción cuesta 1 (mínimo |J|).

    Lanza ValueError si r > R_MAX_EXACTO o si la instancia no es factible.
    """
    if r > R_MAX_EXACTO:
        raise ValueError("verificación exacta solo con r <= %d (r = %d)" % (R_MAX_EXACTO, r))
    factible, sin_cubrir = verificar_factibilidad(r, S)
    if not factible:
        raise ValueError("instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir))
    a = [1] * len(S) if costos is None else list(costos)
    mascaras = [sum(1 << (c - 1) for c in s) for s in S]
    por_bit = [[] for _ in range(r)]                       # opciones que cubren cada categoría
    for j, m in enumerate(mascaras):
        for b in range(r):
            if m >> b & 1:
                por_bit[b].append(j)
    completo = (1 << r) - 1
    inf = float("inf")
    mejor = [inf] * (1 << r)
    previo = [0] * (1 << r)                                # estado anterior y opción usada, para reconstruir J
    opcion = [-1] * (1 << r)
    mejor[0] = 0
    for estado in range(completo):                         # orden creciente: los destinos son siempre mayores
        costo = mejor[estado]
        if costo == inf:
            continue
        falta = (~estado & completo)
        b = (falta & -falta).bit_length() - 1              # primera categoría que falta
        for j in por_bit[b]:
            destino = estado | mascaras[j]
            nuevo = costo + a[j]
            if nuevo < mejor[destino]:
                mejor[destino], previo[destino], opcion[destino] = nuevo, estado, j
    J, estado = [], completo
    while estado:
        J.append(opcion[estado] + 1)
        estado = previo[estado]
    J.reverse()
    return mejor[completo], J


def optimo_de_referencia(r: int, S: Sequence[Set[int]], costos: Optional[Sequence[float]] = None
                         ) -> Optional[Tuple[float, List[int], str]]:
    """(costo mínimo, J, método) del mínimo real, o None si no se puede calcular.

    Con n <= 12 usa la fuerza bruta de siempre; si no, y con r <= 16, los subconjuntos de categorías; si no, None.
    Sin `costos` el costo es |J|. Cuando las dos valen, dan el mismo costo (lo comprueban las pruebas).
    """
    n = len(S)
    if n <= N_MAX_FUERZA_BRUTA:
        if costos is None:
            J = fuerza_bruta(r, S)
            return float(len(J)), J, METODO_FUERZA_BRUTA
        costo, J = fuerza_bruta_ponderada(r, S, costos)
        return costo, J, METODO_FUERZA_BRUTA
    if r <= R_MAX_EXACTO:
        costo, J = minimo_por_subconjuntos(r, S, costos)
        return costo, J, METODO_SUBCONJUNTOS
    return None
