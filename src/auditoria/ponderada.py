"""Variante 1 — Auditoría ponderada por costo (Set Cover ponderado).  [Integrante 3]

Notación del proyecto:
    n   número de interacciones
    r   número de categorías de riesgo, U = {1, ..., r}
    S_j subconjunto de categorías que cubre la interacción j (j = 1, ..., n)
    a_j costo de auditar la interacción j (a_j > 0)
    J   conjunto de interacciones auditadas

Problema: elegir J con unión de los S_j (j en J) = U que minimice sum_{j en J} a_j.
Si todos los a_j valen 1 queda exactamente la Parte 2, así que la variante es
NP-difícil (generaliza Set Cover; la reducción está en el informe).

Algoritmo: voraz de Chvátal (1979). En cada paso elige la interacción de menor
costo por categoría nueva, a_j / |S_j ∩ faltan|, ignorando las que no aportan
nada nuevo. Garantía: costo(voraz) <= H(d)·OPT, con d = máx |S_j|.

Convención (la misma de `auditoria.py`): la instancia se recibe como `r`, una
lista `S` de n conjuntos y una lista `a` de n costos; la interacción j es
`S[j - 1]` con costo `a[j - 1]`. Las funciones devuelven datos puros: no leen
archivos ni imprimen (la lectura de costos vive en `lectura_ponderada.py` y la
traza en `traza_ponderada.py`).

Anotación de costos (al final de cada línea), igual que en `auditoria.py`:
    C (k)   línea de costo constante, con k operaciones elementales.
    O(...)  costo asintótico de la línea o de la función.
Las operaciones sobre conjuntos de a lo sumo r elementos cuestan O(r); len() es O(1).
"""

from dataclasses import dataclass
from typing import List, Sequence, Set, Tuple

from .auditoria import N_MAX_FUERZA_BRUTA, cubre_todo, verificar_factibilidad


@dataclass(frozen=True)
class PasoPonderado:
    """Un paso del voraz ponderado: qué se eligió, cuánto costó y cómo quedó la cobertura."""

    j: int                      # interacción elegida (1..n)
    costo: float                # a_j
    nuevas: frozenset           # categorías nuevas que cubrió
    costo_por_categoria: float  # a_j / |nuevas|, el criterio de elección
    acumulado: float            # costo total después del paso
    faltan: frozenset           # categorías que todavía faltan después del paso


def validar_costos(S: Sequence[Set[int]], a: Sequence[float]) -> None:
    """Restricción de la variante: un costo a_j > 0 por cada interacción.  O(n)."""
    if len(a) != len(S):                                          # C (3): dos len() y una comparación
        raise ValueError("hay %d costos para %d interacciones" % (len(a), len(S)))
    for j, aj in enumerate(a, start=1):                           # n+1 pruebas de ciclo -> O(n)
        if isinstance(aj, bool) or not isinstance(aj, (int, float)) or not aj > 0:   # n veces · C (5)
            raise ValueError("el costo de la interacción %d debe ser > 0 (recibido %r)" % (j, aj))


def voraz_ponderado(r: int, S: Sequence[Set[int]], a: Sequence[float]) -> Tuple[List[int], float, List[PasoPonderado]]:
    """Voraz ponderado: menor costo por categoría nueva en cada paso.

    Desempate fijo (reproducible): gana la de menor índice j (comparación '<' estricta).
    Devuelve (J en orden de elección, costo total, traza como lista de PasoPonderado).
    Lanza ValueError si la instancia no es factible o algún costo no es válido.

    T(n, r) = O(n·r·min(n, r)): a lo sumo min(n, r) pasos (cada paso cubre >= 1
    categoría nueva y una interacción ya elegida no vuelve a aportar nada) y cada
    paso revisa n interacciones calculando S_j ∩ faltan en O(r).
    """
    validar_costos(S, a)                                          # O(n)
    factible, sin_cubrir = verificar_factibilidad(r, S)           # O(n·r): factibilidad previa a todo
    if not factible:                                              # C (1)
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )                                                         # C: solo si no es factible

    faltan = set(range(1, r + 1))                                 # O(r)
    J: List[int] = []                                             # C (1)
    traza: List[PasoPonderado] = []                               # C (1)
    acumulado = 0                                                 # C (1)
    while faltan:                                                 # min(n, r)+1 pruebas de ciclo
        paso = paso_ponderado(S, a, faltan, acumulado)            # min(n, r) veces · O(n·r) -> O(n·r·min(n, r))
        acumulado = paso.acumulado                                # C (1)
        J.append(paso.j)                                          # C (1) amortizado
        traza.append(paso)                                        # C (1) amortizado
    return J, acumulado, traza                                    # C (3)


def paso_ponderado(S: Sequence[Set[int]], a: Sequence[float], faltan: Set[int], acumulado: float) -> PasoPonderado:
    """Un paso del voraz ponderado. Modifica `faltan`.

    Compara a_j / |nuevas_j| contra a_mejor / |nuevas_mejor| multiplicando en
    cruz (a_j·|nuevas_mejor| < a_mejor·|nuevas_j|), así no hay errores de
    redondeo cuando los costos son enteros.  T = O(n·r).
    """
    mejor_j, mejor_nuevas = 0, set()                              # C (2)
    for j, s in enumerate(S, start=1):                            # n+1 pruebas de ciclo -> O(n)
        nuevas = s & faltan                                       # n veces · O(r) -> O(n·r)
        if not nuevas:                                            # n veces · C (1): no aporta nada nuevo, se ignora
            continue
        if mejor_j == 0 or a[j - 1] * len(mejor_nuevas) < a[mejor_j - 1] * len(nuevas):   # n veces · C (8)
            mejor_j, mejor_nuevas = j, nuevas                     # C (2) cuando gana
    faltan -= mejor_nuevas                                        # O(r)
    aj = a[mejor_j - 1]                                           # C (2)
    return PasoPonderado(mejor_j, aj, frozenset(mejor_nuevas), aj / len(mejor_nuevas),
                         acumulado + aj, frozenset(faltan))       # O(r): construir los frozenset


def costo_de(a: Sequence[float], J: Sequence[int]) -> float:
    """Costo total de un conjunto de interacciones.  O(|J|)."""
    return sum(a[j - 1] for j in J)                               # |J| sumas


def fuerza_bruta_ponderada(r: int, S: Sequence[Set[int]], a: Sequence[float]) -> Tuple[float, List[int]]:
    """Óptimo exacto (costo mínimo) probando los 2^n subconjuntos. Solo n <= 12.

    Devuelve (costo óptimo, J óptimo). En un empate de costo se queda con el
    primero en orden de máscara.  T(n, r) = O(2^n · n · r).
    """
    n = len(S)                                                    # C (1)
    if n > N_MAX_FUERZA_BRUTA:                                    # C (1)
        raise ValueError(
            "fuerza bruta solo para verificar: n=%d > %d" % (n, N_MAX_FUERZA_BRUTA)
        )
    validar_costos(S, a)                                          # O(n)
    factible, sin_cubrir = verificar_factibilidad(r, S)           # O(n·r)
    if not factible:                                              # C (1)
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    mejor_costo, mejor_J = None, None                             # C (2)
    for mascara in range(1, 1 << n):                              # 2^n - 1 subconjuntos no vacíos -> O(2^n)
        J = [j for j in range(1, n + 1) if mascara >> (j - 1) & 1]   # 2^n veces · O(n)
        if cubre_todo(r, S, J):                                   # 2^n veces · O(n·r) -> O(2^n·n·r)
            costo = costo_de(a, J)                                # O(n)
            if mejor_costo is None or costo < mejor_costo:        # C (3)
                mejor_costo, mejor_J = costo, J                   # C (2)
    return mejor_costo, mejor_J                                   # C (2)
