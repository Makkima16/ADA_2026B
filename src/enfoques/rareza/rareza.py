"""Enfoque C — voraz por rareza de las categorías (Parte 2, auditoría).

NO reemplaza al voraz base de `ruta.auditoria.voraz`: es un algoritmo aparte
para compararlo con él.

Idea: no todas las categorías valen lo mismo. Una categoría que solo cubren
pocas interacciones es "rara" y conviene cubrirla pronto, porque después puede
no haber con qué. Si f(c) es cuántas interacciones cubren la categoría c, cada
categoría pendiente aporta 1/f(c) a la puntuación de una interacción:

    puntaje(j) = suma de 1/f(c) para c en S_j que aún falta

En cada paso se elige la de mayor puntaje. Desempates fijos: más categorías
nuevas y, si siguen empatadas, menor índice j. Las esenciales (f = 1) aportan 1
cada una, el máximo posible, pero no se eligen por fuerza primero.

Notación del proyecto: n interacciones, r categorías, S_j, J.

Eficiencia: contar f(c) cuesta O(Σ|S_j|) <= O(n·r); cada paso revisa las n
interacciones y puntuar una cuesta O(r): O(n·r) por paso, a lo sumo min(n, r) pasos.
    T(n, r) = O(n·r·min(n, r)),   igual que el voraz base.

Garantía: NO se demuestra H(d) para este enfoque; solo hay evidencia empírica
(ver `comparacion/`). El puntaje se compara redondeado a 9 decimales para que
el resultado no dependa del orden en que se suman los decimales.
"""

from dataclasses import dataclass
from typing import List, Sequence, Set, Tuple

from ruta.auditoria import Paso, verificar_factibilidad


@dataclass(frozen=True)
class PasoRareza(Paso):
    """Un `Paso` que además guarda el puntaje que tenía cada interacción antes de elegir."""

    puntajes: Tuple[float, ...] = ()      # puntaje de cada interacción 1..n (en ese orden)


def frecuencias(r: int, S: Sequence[Set[int]]) -> List[int]:
    """f[c] = cuántas interacciones cubren la categoría c (c = 1..r). T = O(Σ|S_j|)."""
    f = [0] * (r + 1)
    for s in S:                                   # n iteraciones
        for c in s:                               # |S_j| <= r
            f[c] += 1
    return f


def paso_rareza(S: Sequence[Set[int]], faltan: Set[int], f: Sequence[int]) -> PasoRareza:
    """Un paso: elige la interacción de mayor puntaje. Modifica `faltan`. T = O(n·r)."""
    puntajes = []
    mejor_clave, mejor_j, mejor_nuevas = None, 0, set()
    for j, s in enumerate(S, start=1):            # n iteraciones
        nuevas = set(s) & faltan                  # O(r)
        puntaje = round(sum(1.0 / f[c] for c in nuevas), 9)    # O(r)
        puntajes.append(puntaje)
        clave = (puntaje, len(nuevas), -j)        # más puntaje, más nuevas, menor índice
        if nuevas and (mejor_clave is None or clave > mejor_clave):
            mejor_clave, mejor_j, mejor_nuevas = clave, j, nuevas
    faltan -= mejor_nuevas                        # O(r)
    return PasoRareza(mejor_j, frozenset(mejor_nuevas), frozenset(faltan), tuple(puntajes))


def voraz_rareza(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[PasoRareza]]:
    """Devuelve (J en orden de elección, traza como lista de PasoRareza).

    Lanza ValueError si la instancia no es factible.
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)       # O(n·r)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    f = frecuencias(r, S)                                     # O(n·r)
    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[PasoRareza] = []
    while faltan:                                             # a lo sumo min(n, r) pasos
        paso = paso_rareza(S, faltan, f)                      # O(n·r) por paso
        J.append(paso.j)
        traza.append(paso)
    return J, traza
