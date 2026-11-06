"""Óptimo exacto por subconjuntos de categorías: coincide con la fuerza bruta y llega donde la fuerza bruta no."""

import random
from pathlib import Path

import pytest

from auditoria.auditoria import cubre_todo, fuerza_bruta
from auditoria.lectura import leer_instancia
from auditoria.lectura_ponderada import leer_opciones
from auditoria.ponderada import fuerza_bruta_ponderada
from auditoria.resolver import resolver_caso
from auditoria.resolver_ponderada import resolver_caso_ponderado
from auditoria.verificacion_exacta import (METODO_FUERZA_BRUTA, METODO_SUBCONJUNTOS, R_MAX_EXACTO, minimo_por_subconjuntos,
                                           optimo_de_referencia)

PROFESORA = Path(__file__).resolve().parents[1] / "Casos" / "casos_propios" / "pd" / "entrada_G3_mochila_20_nodos.json"


def _instancia(rng, n, r, p=0.3):
    S = [{k for k in range(1, r + 1) if rng.random() < p} or {rng.randint(1, r)} for _ in range(n)]
    for k in range(1, r + 1):
        if not any(k in s for s in S):
            S[rng.randrange(n)].add(k)
    return S


def test_coincide_con_la_fuerza_bruta_en_instancias_al_azar():
    rng = random.Random(7)
    for _ in range(300):
        n, r = rng.randint(2, 11), rng.randint(2, 12)
        S = _instancia(rng, n, r)
        a = [rng.randint(1, 9) for _ in range(n)]
        cuenta, J = minimo_por_subconjuntos(r, S)
        costo, Jp = minimo_por_subconjuntos(r, S, a)
        assert cuenta == len(fuerza_bruta(r, S)) and costo == fuerza_bruta_ponderada(r, S, a)[0]
        assert cubre_todo(r, S, J) and cubre_todo(r, S, Jp) and sum(a[j - 1] for j in Jp) == costo


def test_el_ejemplo_clasico_y_los_errores():
    S = [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}]
    assert minimo_por_subconjuntos(6, S)[0] == 2                                   # el óptimo es {P, Q}, el voraz usa 3
    with pytest.raises(ValueError, match="no factible"):
        minimo_por_subconjuntos(3, [{1}, {2}])
    with pytest.raises(ValueError, match="r <= 16"):
        minimo_por_subconjuntos(R_MAX_EXACTO + 1, [set(range(1, R_MAX_EXACTO + 2))])


def test_optimo_de_referencia_elige_el_metodo():
    rng = random.Random(3)
    chica = _instancia(rng, 8, 6)
    assert optimo_de_referencia(6, chica)[2] == METODO_FUERZA_BRUTA                # n <= 12: la fuerza bruta de siempre
    grande = _instancia(rng, 25, 10)
    costo, J, metodo = optimo_de_referencia(10, grande)
    assert metodo == METODO_SUBCONJUNTOS and cubre_todo(10, grande, J) and costo == len(J)
    assert optimo_de_referencia(R_MAX_EXACTO + 1, _instancia(rng, 14, R_MAX_EXACTO + 1)) is None


def test_el_ejemplo_de_la_profesora_ya_tiene_minimo_real():
    inst = leer_instancia(PROFESORA)                                               # n = 20 > 12, r = 12
    res = resolver_caso(inst)
    assert len(res.J) == 4 and len(res.optimo) == 4 and res.optimo_metodo == METODO_SUBCONJUNTOS   # el voraz acierta
    op = leer_opciones(PROFESORA, inst)                                            # 35 opciones > 12
    rv = resolver_caso_ponderado(op.instancia, op.costos)
    assert rv.optimo_costo == 24 and rv.costo == 26 and rv.optimo_metodo == METODO_SUBCONJUNTOS
    assert rv.costo / rv.optimo_costo <= rv.cota                                   # 26/24 ≈ 1,083 <= H(4) ≈ 2,083
