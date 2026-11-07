"""Parte 2 — Cobertura mínima de auditoría (Set Cover).

Notación del proyecto:
    n   número de interacciones
    r   número de categorías de riesgo, U = {1, ..., r}
    S_j subconjunto de categorías que cubre la interacción j (j = 1, ..., n)
    J   conjunto de interacciones auditadas

Convención: la instancia se recibe como `r` y una lista `S` de n conjuntos;
la interacción j es `S[j - 1]`. Todas las funciones devuelven datos puros:
no leen archivos ni imprimen (eso vive en otros módulos).

Al final del archivo está el costo del voraz y por qué sale ese costo.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Sequence, Set, Tuple

# La fuerza bruta es O(2^n * n * r): solo se permite para verificar.
N_MAX_FUERZA_BRUTA = 12


@dataclass(frozen=True)
class Paso:
    """Un paso del voraz: qué se eligió y cómo quedó la cobertura."""

    j: int                # interacción elegida (1..n)
    nuevas: frozenset     # categorías nuevas que cubrió
    faltan: frozenset     # categorías que todavía faltan después del paso


def verificar_factibilidad(r: int, S: Sequence[Set[int]]) -> Tuple[bool, Set[int]]:
    """¿La unión de todos los S_j es U?  Devuelve (factible, categorías sin cubrir).

    T(n, r) = O(n·r): se recorren las n interacciones y se une cada S_j (<= r).
    """
    cubiertas: Set[int] = set()
    for s in S:
        cubiertas |= s
    sin_cubrir = set(range(1, r + 1)) - cubiertas
    return (not sin_cubrir, sin_cubrir)


def voraz(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[Paso]]:
    """Voraz de Johnson/Chvátal: elige la interacción que cubre más categorías nuevas.

    Desempate fijo (reproducible): gana la de menor índice j.
    Devuelve (J en orden de elección, traza como lista de Paso).
    Lanza ValueError si la instancia no es factible.

    T(n, r) = O(n·r·min(n, r)): a lo sumo min(n, r) pasos (cada paso cubre
    >= 1 categoría nueva y usa una interacción distinta) y cada paso revisa
    n interacciones contando categorías nuevas en O(r).
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )

    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[Paso] = []
    while faltan:
        paso = paso_voraz(S, faltan)
        J.append(paso.j)
        traza.append(paso)
    return J, traza


def paso_voraz(S: Sequence[Set[int]], faltan: Set[int]) -> Paso:
    """Un paso del voraz: elige la interacción con más categorías nuevas.

    Modifica `faltan` (le quita las categorías que cubre la elegida).
    Desempate fijo: gana la de menor índice j ('>' estricto).
    """
    mejor_j, mejor_nuevas = 0, set()
    for j, s in enumerate(S, start=1):
        nuevas = s & faltan
        if len(nuevas) > len(mejor_nuevas):
            mejor_j, mejor_nuevas = j, nuevas
    faltan -= mejor_nuevas
    return Paso(mejor_j, frozenset(mejor_nuevas), frozenset(faltan))


def cobertura_final(S: Sequence[Set[int]], J: Sequence[int]) -> Dict[int, int]:
    """Para cada categoría, la primera interacción de J (en orden) que la cubre."""
    cobertura: Dict[int, int] = {}
    for j in J:
        for c in sorted(S[j - 1]):                        # |S_j|+1 pruebas; sorted cuesta O(|S_j| log |S_j|)
            cobertura.setdefault(c, j)
    return cobertura


def cubre_todo(r: int, S: Sequence[Set[int]], J: Sequence[int]) -> bool:
    """Comprobación independiente: ¿las interacciones de J cubren U?"""
    return set(cobertura_final(S, J)) == set(range(1, r + 1))


def fuerza_bruta(r: int, S: Sequence[Set[int]]) -> List[int]:
    """Óptimo exacto probando subconjuntos por tamaño creciente. Solo n <= 12."""
    n = len(S)
    if n > N_MAX_FUERZA_BRUTA:
        raise ValueError(
            "fuerza bruta solo para verificar: n=%d > %d" % (n, N_MAX_FUERZA_BRUTA)
        )
    factible, sin_cubrir = verificar_factibilidad(r, S)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    for k in range(0, n + 1):
        for J in combinations(range(1, n + 1), k):
            if cubre_todo(r, S, J):
                return list(J)
    raise AssertionError("inalcanzable: la instancia es factible")


def armonico(d: int) -> float:
    """H(d) = 1 + 1/2 + ... + 1/d."""
    return sum(1.0 / i for i in range(1, d + 1))


def cota_aproximacion(S: Sequence[Set[int]]) -> float:
    """H(d) con d = máx |S_j| (Johnson, 1974; Chvátal, 1979)."""
    d = max((len(s) for s in S), default=0)
    return armonico(d)


# =============================================================================
# COSTO DEL VORAZ
# n = interacciones, r = categorías, d = máx |S_j|.
#
# verificar_factibilidad -> O(n·r)
#   Por qué: une los n conjuntos S_j y cada unión cuesta O(r) (a lo sumo r elementos).
#
# paso_voraz -> O(n·r)
#   Por qué: revisa las n interacciones y, en cada una, calcula las categorías nuevas
#   (intersección con las que faltan), que cuesta O(r).
#
# voraz -> T(n, r) = O(n·r·min(n, r))
#   Por qué: cada paso cubre al menos 1 categoría nueva y usa una interacción distinta,
#   así que hay a lo sumo min(n, r) pasos; cada paso cuesta O(n·r). La cota más suelta
#   O(n·r²) también es correcta, pero esta es más ajustada. La factibilidad previa
#   (O(n·r)) no cambia el orden.
#
# cobertura_final / cubre_todo -> O(n·r)
#   Por qué: recorren las interacciones de J (a lo sumo min(n, r)) y sus categorías.
#
# fuerza_bruta -> O(2^n·n·r)
#   Por qué: prueba los 2^n subconjuntos y cada comprobación (cubre_todo) cuesta O(n·r).
#   Solo se usa para verificar, con n <= 12.
#
# cota_aproximacion -> O(n + r)
#   Por qué: un recorrido de las n interacciones para hallar d y d términos de H(d), d <= r.
# =============================================================================


# =============================================================================
# INVARIANTES DE CICLO (inicialización / mantenimiento / finalización)
#
# Ojo: demuestran que el resultado es FACTIBLE y que el algoritmo TERMINA, no que sea óptimo.
# El voraz no garantiza el mínimo; su calidad la da la cota |J| <= H(d)·OPT (Johnson 1974;
# Chvátal 1979), que se prueba aparte (no es un invariante) y se verifica con la fuerza bruta.
#
# voraz, ciclo `while faltan`:
#   Invariante: antes de cada vuelta, `faltan` = U menos las categorías cubiertas por las
#   interacciones de J.
#   - Inicio: J vacío y faltan = {1..r}.
#   - Mantenimiento: paso_voraz elige una j y le quita a `faltan` lo que cubre; J agrega j.
#     Como la instancia es factible, siempre existe una j con al menos una categoría nueva,
#     así que `faltan` baja al menos en 1 por vuelta y el ciclo termina.
#   - Fin: faltan vacío, o sea J cubre las r categorías.
#
# paso_voraz, ciclo `for j`:
#   Invariante: antes de revisar j, (mejor_j, mejor_nuevas) es la interacción de 1..j-1 con más
#   categorías nuevas; en empate gana la de menor índice.
#   - Inicio: no se revisó ninguna (mejor_j = 0, conjunto vacío).
#   - Mantenimiento: j reemplaza a la mejor solo si cubre estrictamente más (`>`), así el
#     empate lo gana la de menor índice.
#   - Fin: es la mejor de las n interacciones.
#
# verificar_factibilidad, ciclo `for s`:
#   Invariante: `cubiertas` es la unión de los S_j ya recorridos. Inicio: vacío. Mantenimiento:
#   se une el siguiente. Fin: es la unión de todos; la instancia es factible si contiene U.
# =============================================================================
