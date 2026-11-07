"""Enfoque B — voraz con vista al futuro de profundidad 2 (Parte 2, auditoría).

NO reemplaza al voraz base de `auditoria.auditoria.voraz`: es un algoritmo aparte
para compararlo con él.

Idea: en cada paso no se mira solo "qué interacción cubre más ahora", sino qué
**par** de interacciones cubre más categorías nuevas juntas (un par puede ser
una sola interacción repetida: el par (a, a)). Del mejor par se compromete la
que más cubre por sí sola (empate: menor índice) y se vuelve a evaluar.

Desempates fijos y deterministas: ante igual cobertura se prefieren las
**menos interacciones** (primero las candidatas de una sola interacción y luego
los pares), y entre iguales gana el menor (a, b) en orden lexicográfico; dentro
del par, la de menor índice si cubren lo mismo. (Una primera versión preferia el
par al desempatar y quedaba peor que el voraz base en casos como
S = [{2,3}, {1}, {1,2,3}]: elegía 2 interacciones donde una bastaba.)

Notación del proyecto: n interacciones, r categorías, S_j, J.

Eficiencia: cada paso evalúa los n(n+1)/2 pares y cada unión cuesta O(r), es decir
O(n²·r) por paso. Hay a lo sumo min(n, r) pasos (cada paso cubre al menos una
categoría nueva y usa una interacción distinta). Total:
    T(n, r) = O(n²·r·min(n, r)),   un factor n más que el voraz base.

Garantía: NO se demuestra H(d) para este enfoque. Al comprometer una interacción
que no necesariamente cubre más categorías nuevas, la prueba del voraz base no
aplica. Se evalúa solo de forma empírica (ver `comparacion/`).
"""

from dataclasses import dataclass
from typing import List, Sequence, Set, Tuple

from auditoria.auditoria import Paso, verificar_factibilidad


@dataclass(frozen=True)
class PasoFuturo(Paso):
    """Un `Paso` que además guarda qué candidata ganó la evaluación (para mostrar el recorrido)."""

    par: Tuple[int, int] = (0, 0)     # (a, b) con índices 1..n; a == b si ganó una sola interacción
    cobertura_par: int = 0            # categorías nuevas que cubre ese par junto


def paso_futuro(S: Sequence[Set[int]], faltan: Set[int]) -> PasoFuturo:
    """Un paso con vista al futuro. Modifica `faltan` (le quita lo que cubre la elegida).

    T(n, r) = O(n²·r): n(n+1)/2 pares y cada unión cuesta O(r).
    """
    n = len(S)
    nuevas = [set(s) & faltan for s in S]                 # O(n·r): lo que aporta cada una ahora
    mejor_tam, mejor_par = -1, (0, 0)
    for a in range(n):                                    # primero las candidatas de una sola interacción
        if len(nuevas[a]) > mejor_tam:                    # '>' estricto: ante empate gana la de menor índice
            mejor_tam, mejor_par = len(nuevas[a]), (a, a)
    for a in range(n):                                    # luego los pares distintos: n(n-1)/2
        for b in range(a + 1, n):
            tam = len(nuevas[a] | nuevas[b])              # O(r)
            if tam > mejor_tam:                           # solo gana un par si cubre ESTRICTAMENTE más
                mejor_tam, mejor_par = tam, (a, b)
    a, b = mejor_par
    elegida = a if len(nuevas[a]) >= len(nuevas[b]) else b    # la que más cubre sola; empate: menor índice
    cubre = nuevas[elegida]
    faltan -= cubre                                       # O(r)
    return PasoFuturo(elegida + 1, frozenset(cubre), frozenset(faltan), (a + 1, b + 1), mejor_tam)


def voraz_futuro(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[Paso]]:
    """Devuelve (J en orden de elección, traza como lista de Paso).

    Lanza ValueError si la instancia no es factible.
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)   # O(n·r)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[Paso] = []
    while faltan:                                         # a lo sumo min(n, r) pasos
        paso = paso_futuro(S, faltan)                     # O(n²·r) por paso
        J.append(paso.j)
        traza.append(paso)
    return J, traza
