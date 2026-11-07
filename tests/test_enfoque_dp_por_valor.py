"""Pruebas del enfoque de la DP por valor (Parte 1) y de la elección automática entre las dos DP."""

import random

import pytest

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada, resolver
from aceleracion.enfoques.dp_por_valor.dp_por_valor import (
    llenar_tabla_valor, mejor_ahorro, reconstruir_valor, resolver_valor)
from aceleracion.enfoques.dp_por_valor.resolver import resolver_caso_valor
from aceleracion.enfoques.dp_por_valor.traza import formatear_caso_valor
from aceleracion.enfoques.seleccion import PRESUPUESTO, VALOR, elegir_enfoque, resolver_auto, tamanos_de_tablas
from aceleracion.resolver import InstanciaAceleracion, resolver_caso
from aceleracion.verificacion import fuerza_bruta, generar_instancia


def _inst(t, c, d, B, nombre="x"):
    return InstanciaAceleracion(nombre, list(t), list(c), list(d), B)


def test_ejemplo_conocido():
    r = resolver_valor([10, 8, 7, 9, 6], [5, 4, 3, 6, 2], [6, 5, 4, 7, 3], 10)
    assert r["aceleradas"] == [1, 3, 5] and r["ahorro"] == 13 and r["costo"] == 10 and r["duracion_final"] == 27


@pytest.mark.parametrize("semilla", range(300))
def test_mismo_ahorro_que_la_dp_base_y_la_fuerza_bruta(semilla):
    rng = random.Random(semilla)
    n = rng.randint(1, 9)
    t, c, d, B = generar_instancia(n, semilla=semilla, max_t=rng.choice([3, 8, 20]), max_c=rng.choice([2, 6, 12]))
    B = rng.randint(0, sum(c) + 2)
    base, valor = resolver(t, c, d, B), resolver_valor(t, c, d, B)
    assert valor["ahorro"] == base["ahorro"] == fuerza_bruta(t, c, d, B)["ahorro"]
    assert valor["duracion_final"] == base["duracion_final"]
    # la solución propia es factible y logra el ahorro dicho
    assert valor["costo"] <= B
    assert sum(d[i - 1] for i in valor["aceleradas"]) == valor["ahorro"]
    assert len(set(valor["aceleradas"])) == len(valor["aceleradas"])
    # y su costo es el mínimo para ese ahorro (el de la tabla)
    assert valor["costo"] == valor["tabla"][n][valor["ahorro"]]


@pytest.mark.parametrize("t, c, d, B", [
    ([5], [3], [4], 0),                    # B = 0: no cabe nada
    ([5], [0], [4], 0),                    # acelerar es gratis
    ([5, 5], [2, 2], [0, 0], 9),           # nada ahorra
    ([4, 4, 4], [0, 0, 0], [2, 2, 2], 0),  # todo gratis
    ([6, 6], [3, 3], [5, 5], 100),         # sobra presupuesto
])
def test_casos_borde(t, c, d, B):
    assert resolver_valor(t, c, d, B)["ahorro"] == resolver(t, c, d, B)["ahorro"]


def test_la_tabla_tiene_infinito_donde_no_se_puede():
    C = llenar_tabla_valor([3], [4], 10)
    assert C[0] == [0, 11, 11, 11, 11] and C[1] == [0, 11, 11, 11, 3]   # INF = B + 1
    assert mejor_ahorro(C, 10) == 4 and reconstruir_valor(C, [4], 4) == [1]


def test_costo_pasa_de_B_se_descarta():
    assert resolver_valor([5], [9], [4], 8)["ahorro"] == 0


def test_tamano_de_la_tabla_depende_de_D_no_de_B():
    n = 4
    chico = resolver_valor([9] * n, [1] * n, [2] * n, 10 ** 6)   # B enorme, D = 8: la base no cabría
    assert chico["ahorro"] == 8
    assert len(chico["tabla"][0]) == 9


def test_error_si_la_tabla_por_valor_no_cabe():
    with pytest.raises(ErrorDeEntrada, match="tabla por valor"):
        resolver_valor([10 ** 7], [1], [10 ** 7], 5)


def test_resolver_caso_valor_arma_el_resultado_y_la_traza():
    rc = resolver_caso_valor(_inst([10, 8, 7, 9, 6], [5, 4, 3, 6, 2], [6, 5, 4, 7, 3], 10))
    assert rc.valida and rc.optimo_ahorro == rc.ahorro == 13
    texto = formatear_caso_valor(rc)
    assert "DP por valor" in texto and "coincide" in texto and "Etapa 5: acelerada" in texto


def test_traza_omite_la_tabla_si_D_es_grande():
    n = 3
    rc = resolver_caso_valor(_inst([200] * n, [1] * n, [150] * n, 5), comparar_con_optimo=False)
    assert "Tabla por valor omitida" in formatear_caso_valor(rc)


# ----------------------- elección automática -----------------------

def test_elige_la_tabla_mas_chica():
    assert elegir_enfoque(_inst([9] * 5, [1] * 5, [2] * 5, 1000)) == VALOR           # D = 10 << B = 1000
    assert elegir_enfoque(_inst([9] * 5, [1] * 5, [200] * 5, 10)) == PRESUPUESTO     # B = 10 << D = 1000
    assert elegir_enfoque(_inst([5, 5], [1, 1], [3, 3], 5)) == PRESUPUESTO           # empate (D = 6, B = 5 -> base menor)


def test_empate_va_a_la_base():
    inst = _inst([9, 9], [1, 1], [3, 3], 6)   # D = 6 = B
    assert tamanos_de_tablas(inst)[PRESUPUESTO] == tamanos_de_tablas(inst)[VALOR]
    assert elegir_enfoque(inst) == PRESUPUESTO


def test_error_si_ninguna_tabla_cabe():
    inst = _inst([10 ** 7] * 2, [1] * 2, [10 ** 7] * 2, 10 ** 8)
    with pytest.raises(ErrorDeEntrada, match="ninguna tabla cabe"):
        elegir_enfoque(inst)
    with pytest.raises(ErrorDeEntrada, match="ninguna tabla cabe"):
        resolver_auto(inst)


def test_auto_resuelve_lo_que_la_base_no_podria():
    inst = _inst([9] * 6, [1] * 6, [2] * 6, MAX_CELDAS_TABLA * 3)   # B enorme: la base no cabe
    with pytest.raises(ErrorDeEntrada):
        resolver_caso(inst)
    rc, enfoque = resolver_auto(inst, comparar_con_optimo=False)
    assert enfoque == VALOR and rc.ahorro == 12 and rc.valida


@pytest.mark.parametrize("semilla", range(40))
def test_auto_da_el_mismo_ahorro_que_la_base(semilla):
    t, c, d, B = generar_instancia(8, semilla=semilla)
    inst = _inst(t, c, d, B)
    rc, _ = resolver_auto(inst)
    assert rc.ahorro == resolver_caso(inst).ahorro and rc.valida
