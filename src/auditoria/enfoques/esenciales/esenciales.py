"""Enfoque A — voraz con interacciones esenciales (Parte 2, auditoría).

NO reemplaza al voraz base de `auditoria.auditoria.voraz`: es un algoritmo aparte
para compararlo con él.

Idea: una interacción es **esencial** si es la única que cubre alguna categoría.
Toda cobertura factible contiene a las esenciales, así que se eligen primero
(en orden de índice j) y, con lo que falte, se corre el paso del voraz normal.

Notación del proyecto: n interacciones, r categorías, S_j, J.

Eficiencia: T(n, r) = O(n·r) [contar quién cubre cada categoría]
                    + O(n·r·min(n, r)) [voraz sobre el resto]
                    = O(n·r·min(n, r)), igual que el voraz base.

Garantía: se conserva H(d). Sea E el conjunto de esenciales y OPT el óptimo.
Todo óptimo contiene a E, y lo que cubre el resto de las categorías son OPT − |E|
interacciones: el óptimo del resto es a lo sumo OPT − |E|. El voraz sobre el
resto usa a lo sumo H(d) veces eso (d no crece al mirar solo categorías que
faltan). Total: |J| ≤ |E| + H(d)·(OPT − |E|) ≤ H(d)·OPT, porque H(d) ≥ 1.
"""

from typing import List, Sequence, Set, Tuple

from auditoria.auditoria import Paso, paso_voraz, verificar_factibilidad


def interacciones_esenciales(r: int, S: Sequence[Set[int]]) -> List[int]:
    """Índices j (1..n, ordenados) que son la única interacción de alguna categoría.

    T(n, r) = O(n·r): se cuenta, para cada categoría, cuántas interacciones la cubren.
    """
    cuantas = [0] * (r + 1)                      # cuántas interacciones cubren cada categoría
    ultima = [0] * (r + 1)                       # la última que la cubrió (si cuantas == 1, es la única)
    for j, s in enumerate(S, start=1):           # n iteraciones
        for c in s:                              # |S_j| <= r  -> O(n·r) en total
            cuantas[c] += 1
            ultima[c] = j
    return sorted({ultima[c] for c in range(1, r + 1) if cuantas[c] == 1})   # O(r log r)


def voraz_esenciales(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[Paso], List[int]]:
    """Devuelve (J en orden de elección, traza como lista de Paso, esenciales).

    Primero las esenciales (por índice j), después el voraz normal sobre lo que falta,
    con el mismo desempate (menor índice j). Lanza ValueError si no es factible.
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)             # O(n·r)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    esenciales = interacciones_esenciales(r, S)                     # O(n·r)
    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[Paso] = []
    for j in esenciales:                                            # a lo sumo min(n, r) esenciales
        nuevas = set(S[j - 1]) & faltan                             # O(r)
        faltan -= nuevas                                            # O(r)
        J.append(j)
        traza.append(Paso(j, frozenset(nuevas), frozenset(faltan)))
    while faltan:                                                   # voraz normal sobre el resto
        paso = paso_voraz(S, faltan)                                # O(n·r) por paso, a lo sumo min(n, r) pasos
        J.append(paso.j)
        traza.append(paso)
    return J, traza, esenciales
