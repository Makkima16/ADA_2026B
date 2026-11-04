"""Parte 2 — Cobertura mínima de auditoría (Set Cover).

Notación del proyecto:
    n   número de interacciones
    r   número de categorías de riesgo, U = {1, ..., r}
    S_j subconjunto de categorías que cubre la interacción j (j = 1, ..., n)
    J   conjunto de interacciones auditadas

Convención: la instancia se recibe como `r` y una lista `S` de n conjuntos;
la interacción j es `S[j - 1]`. Todas las funciones devuelven datos puros:
no leen archivos ni imprimen (eso vive en otros módulos).

Anotación de costos (al final de cada línea):
    C (k)   línea de costo constante, con k operaciones elementales.
    n veces la línea corre n veces (cuerpo de un ciclo o de un condicional).
    O(...)  costo asintótico de la línea o de la función.
Como los conjuntos tienen a lo sumo r elementos, las operaciones sobre ellos
(unión, intersección, diferencia, copia) cuestan O(r); len() es O(1).
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
    cubiertas: Set[int] = set()                       # C (1): conjunto vacío
    for s in S:                                       # n+1 pruebas de ciclo, C (1) cada una -> O(n)
        cubiertas |= s                                # n veces · O(r) por la unión -> O(n·r)
    sin_cubrir = set(range(1, r + 1)) - cubiertas     # O(r): construir {1..r} y restar
    return (not sin_cubrir, sin_cubrir)               # C (2): negación y tupla


def voraz(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[Paso]]:
    """Voraz de Johnson/Chvátal: elige la interacción que cubre más categorías nuevas.

    Desempate fijo (reproducible): gana la de menor índice j.
    Devuelve (J en orden de elección, traza como lista de Paso).
    Lanza ValueError si la instancia no es factible.

    T(n, r) = O(n·r·min(n, r)): a lo sumo min(n, r) pasos (cada paso cubre
    >= 1 categoría nueva y usa una interacción distinta) y cada paso revisa
    n interacciones contando categorías nuevas en O(r).
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)   # O(n·r): factibilidad previa a todo
    if not factible:                                      # C (1): comparación
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )                                                 # C: solo si no es factible (no corre en el caso normal)

    faltan = set(range(1, r + 1))                         # O(r): categorías por cubrir
    J: List[int] = []                                     # C (1): lista vacía
    traza: List[Paso] = []                                # C (1): lista vacía
    while faltan:                                         # min(n, r)+1 pruebas de ciclo, C (1) cada una -> O(min(n, r))
        paso = paso_voraz(S, faltan)                      # min(n, r) veces · O(n·r) por paso -> O(n·r·min(n, r))
        J.append(paso.j)                                  # min(n, r) veces · C (1) amortizado -> O(min(n, r))
        traza.append(paso)                                # min(n, r) veces · C (1) amortizado -> O(min(n, r))
    return J, traza                                       # C (2): retorno de tupla


def paso_voraz(S: Sequence[Set[int]], faltan: Set[int]) -> Paso:
    """Un paso del voraz: elige la interacción con más categorías nuevas.

    Modifica `faltan` (le quita las categorías que cubre la elegida).
    Desempate fijo: gana la de menor índice j ('>' estricto).
    """
    mejor_j, mejor_nuevas = 0, set()                      # C (2): dos asignaciones
    for j, s in enumerate(S, start=1):                    # n+1 pruebas de ciclo, C (1) cada una -> O(n)
        nuevas = s & faltan                               # n veces · O(r) por la intersección -> O(n·r)
        if len(nuevas) > len(mejor_nuevas):               # n veces · C (3): dos len() y una comparación -> O(n)
            mejor_j, mejor_nuevas = j, nuevas             # C (2) cuando gana; a lo sumo n veces -> O(n)
    faltan -= mejor_nuevas                                # O(r): quitar las nuevas del pendiente
    return Paso(mejor_j, frozenset(mejor_nuevas), frozenset(faltan))  # O(r): construir los frozenset


def cobertura_final(S: Sequence[Set[int]], J: Sequence[int]) -> Dict[int, int]:
    """Para cada categoría, la primera interacción de J (en orden) que la cubre."""
    cobertura: Dict[int, int] = {}                        # C (1): diccionario vacío
    for j in J:                                           # |J|+1 pruebas de ciclo; |J| <= min(n, r)
        for c in sorted(S[j - 1]):                        # |S_j|+1 pruebas; sorted cuesta O(|S_j| log |S_j|)
            cobertura.setdefault(c, j)                    # C (1) por categoría; a lo sumo n·r inserciones en total
    return cobertura                                      # O(n·r): cada interacción de J aporta <= r categorías


def cubre_todo(r: int, S: Sequence[Set[int]], J: Sequence[int]) -> bool:
    """Comprobación independiente: ¿las interacciones de J cubren U?"""
    return set(cobertura_final(S, J)) == set(range(1, r + 1))  # O(n·r): cobertura_final más comparar con {1..r}


def fuerza_bruta(r: int, S: Sequence[Set[int]]) -> List[int]:
    """Óptimo exacto probando subconjuntos por tamaño creciente. Solo n <= 12."""
    n = len(S)                                            # C (1)
    if n > N_MAX_FUERZA_BRUTA:                            # C (1): comparación
        raise ValueError(
            "fuerza bruta solo para verificar: n=%d > %d" % (n, N_MAX_FUERZA_BRUTA)
        )                                                 # C: solo si n supera el límite
    factible, sin_cubrir = verificar_factibilidad(r, S)   # O(n·r): factibilidad previa
    if not factible:                                      # C (1): comparación
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )                                                 # C: solo si no es factible
    for k in range(0, n + 1):                             # n+1 iteraciones, C (1) cada una -> O(n)
        for J in combinations(range(1, n + 1), k):        # C(n, k) iteraciones; sumadas sobre k dan 2^n -> O(2^n)
            if cubre_todo(r, S, J):                       # 2^n veces · O(n·r) por comprobación -> O(2^n·n·r)
                return list(J)                            # C (1): primera cobertura hallada (por tamaño creciente)
    raise AssertionError("inalcanzable: la instancia es factible")  # C: no debería alcanzarse


def armonico(d: int) -> float:
    """H(d) = 1 + 1/2 + ... + 1/d."""
    return sum(1.0 / i for i in range(1, d + 1))          # O(d): d términos, C (1) cada uno


def cota_aproximacion(S: Sequence[Set[int]]) -> float:
    """H(d) con d = máx |S_j| (Johnson, 1974; Chvátal, 1979)."""
    d = max((len(s) for s in S), default=0)               # O(n): recorre las n interacciones; len() es C (1)
    return armonico(d)                                    # O(d) = O(r): llamada a H(d)
