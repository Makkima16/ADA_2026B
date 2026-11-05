"""Enfoque D — todo junto: esenciales + rareza + parejas (Parte 2, auditoría).

NO reemplaza al voraz base de `auditoria.auditoria.voraz`: es un algoritmo aparte
para compararlo con él. Junta los tres ingredientes estudiados:

  1. Primero las interacciones **esenciales** (la única que cubre alguna
     categoría), como en `esenciales/`.
  2. Con las categorías que falten, el paso con **vista al futuro** (el mejor
     par de interacciones), como en `vision_futuro/`, pero cada par se valora
     por la **rareza** de lo que cubre: cada categoría pendiente vale 1/f(c),
     con f(c) = cuántas interacciones la cubren (como en `rareza/`).

Notación del proyecto: n interacciones, r categorías, S_j, J.

Eficiencia: T(n, r) = O(n·r) [factibilidad y conteo de f(c)] + e·O(r) [esenciales]
                    + min(n, r)·O(n²·r) [parejas]  =  O(n²·r·min(n, r)),
un factor n más que el voraz base. Costo exacto, con k interacciones elegidas,
e esenciales y Σ|S_j| la suma de tamaños (cada unión o intersección = r comparaciones):

    T = n·r + Σ|S_j| + e·r + (k − e)·(n + n(n−1)/2)·r

Garantía: NO se demuestra H(d) (la parte de parejas y la de rareza no la tienen).
Solo hay evidencia empírica (ver `comparacion/`).

Desempates fijos: se prefieren menos interacciones (primero las candidatas de una
sola interacción y luego los pares), y entre iguales gana el menor (a, b) en orden
lexicográfico; dentro del par se compromete la de mayor valor por sí sola y, si
empatan, la de menor índice. El valor se compara redondeado a 9 decimales y, si
empata, por cantidad de categorías nuevas.
"""

from dataclasses import dataclass
from typing import List, Sequence, Set, Tuple

from auditoria.enfoques.esenciales.esenciales import interacciones_esenciales
from auditoria.enfoques.rareza.rareza import frecuencias
from auditoria.enfoques.vision_futuro.vision_futuro import PasoFuturo
from auditoria.auditoria import Paso, verificar_factibilidad


@dataclass(frozen=True)
class PasoCombinado(PasoFuturo):
    """`PasoFuturo` (par ganador y cuánto cubre junto) más los valores de rareza."""

    puntaje_par: float = 0.0               # puntaje de rareza del par ganador
    puntajes: Tuple[float, ...] = ()       # puntaje de cada interacción 1..n por sí sola


def paso_parejas_rareza(S: Sequence[Set[int]], faltan: Set[int], f: Sequence[int]) -> PasoCombinado:
    """Un paso: mejor pareja según el puntaje de rareza. Modifica `faltan`. T = O(n²·r).

    El valor de una pareja es valor(a) + valor(b) − valor(a ∩ b) (la intersección se cuenta una
    sola vez); así no hace falta armar la unión de cada pareja.
    """
    n = len(S)
    w = [0.0] + [1.0 / x if x else 0.0 for x in f[1:]]        # peso de cada categoría
    nuevas = [set(s) & faltan for s in S]                     # O(n·r)
    crudos = [sum(w[c] for c in nu) for nu in nuevas]         # O(n·r): valor sin redondear
    pesos = [round(x, 9) for x in crudos]
    mejor = None                                              # (clave, a, b, cobertura del par)
    for a in range(n):                                        # primero las candidatas de una sola interacción
        clave = (pesos[a], len(nuevas[a]))
        if mejor is None or clave > mejor[0]:                 # '>' estricto: ante empate, la de menor índice
            mejor = (clave, a, a, len(nuevas[a]))
    for a in range(n):                                        # luego los pares distintos: n(n−1)/2
        na = nuevas[a]
        for b in range(a + 1, n):
            comun = na & nuevas[b]                            # O(r)
            tam = len(na) + len(nuevas[b]) - len(comun)
            valor = crudos[a] + crudos[b] - (sum(w[c] for c in comun) if comun else 0.0)
            clave = (round(valor, 9), tam)
            if clave > mejor[0]:                              # solo gana un par si vale ESTRICTAMENTE más
                mejor = (clave, a, b, tam)
    clave, a, b, cobertura = mejor
    j = a if (pesos[a], len(nuevas[a])) >= (pesos[b], len(nuevas[b])) else b
    cubre = nuevas[j]
    faltan -= cubre                                           # O(r)
    return PasoCombinado(j + 1, frozenset(cubre), frozenset(faltan), (a + 1, b + 1), cobertura, clave[0], tuple(pesos))


def voraz_combinado(r: int, S: Sequence[Set[int]]) -> Tuple[List[int], List[Paso], List[int]]:
    """Devuelve (J en orden de elección, traza como lista de Paso, esenciales).

    Lanza ValueError si la instancia no es factible.
    """
    factible, sin_cubrir = verificar_factibilidad(r, S)             # O(n·r)
    if not factible:
        raise ValueError(
            "instancia no factible: nadie cubre las categorías %s" % sorted(sin_cubrir)
        )
    f = frecuencias(r, S)                                           # O(Σ|S_j|)
    esenciales = interacciones_esenciales(r, S)                     # O(n·r)
    faltan = set(range(1, r + 1))
    J: List[int] = []
    traza: List[Paso] = []
    for j in esenciales:                                            # a lo sumo min(n, r) esenciales
        nuevas = set(S[j - 1]) & faltan                             # O(r)
        faltan -= nuevas                                            # O(r)
        J.append(j)
        traza.append(Paso(j, frozenset(nuevas), frozenset(faltan)))
    while faltan:                                                   # a lo sumo min(n, r) pasos
        paso = paso_parejas_rareza(S, faltan, f)                    # O(n²·r) por paso
        J.append(paso.j)
        traza.append(paso)
    return J, traza, esenciales
