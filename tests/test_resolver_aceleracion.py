"""Pruebas de resolver_caso y de la traza de la Parte 1."""

import pytest

from aceleracion.aceleracion import ErrorDeEntrada
from aceleracion.resolver import InstanciaAceleracion, resolver_caso
from aceleracion.traza import B_MAX_TABLA, formatear_caso
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA


def _ejemplo(**cambios):
    datos = dict(nombre="ejemplo", t=[4, 3, 5, 2], c=[2, 3, 4, 1], d=[3, 2, 4, 1], B=5,
                 ids_etapa=("E01", "E02", "E03", "E04"))
    datos.update(cambios)
    return InstanciaAceleracion(**datos)


def test_resultado_del_ejemplo():
    rc = resolver_caso(_ejemplo())
    assert rc.aceleradas == [1, 2] and rc.costo == 5 and rc.ahorro == 5
    assert rc.duracion_original == 14 and rc.duracion_final == 9
    assert rc.valida and rc.optimo_ahorro == 5
    assert rc.tiempo_s >= 0 and len(rc.tabla) == 5


def test_no_corre_la_fuerza_bruta_con_n_grande():
    n = N_MAX_FUERZA_BRUTA + 1
    rc = resolver_caso(InstanciaAceleracion("grande", [3] * n, [1] * n, [2] * n, 4))
    assert rc.optimo_ahorro is None and rc.valida and rc.ahorro == 8


def test_se_puede_desactivar_la_comparacion():
    assert resolver_caso(_ejemplo(), comparar_con_optimo=False).optimo_ahorro is None


def test_instancia_invalida_da_error_claro():
    with pytest.raises(ErrorDeEntrada, match="supera la duración"):
        resolver_caso(_ejemplo(d=[3, 2, 9, 1]))


def test_traza_con_nombres_de_etapa():
    texto = formatear_caso(resolver_caso(_ejemplo()))
    assert "Caso: ejemplo   (n = 4 etapas, B = 5)" in texto
    assert "Etapas aceleradas: [1, 2]   (E01, E02)" in texto
    assert "Duración final: 9 (original 14)" in texto
    assert "Ahorro por fuerza bruta: 5 (coincide)" in texto
    assert "Etapa 4 (E04): no se acelera" in texto
    assert "Etapa 2 (E02): acelerada, costo 3, ahorro 2; presupuesto restante 5 -> 2" in texto
    assert "Tabla DP (ahorro máximo" in texto and "i=0: [0, 0, 0, 0, 0, 0]" in texto


def test_traza_sin_nombres_usa_numeros():
    texto = formatear_caso(resolver_caso(_ejemplo(ids_etapa=())))
    assert "Etapa 2: acelerada" in texto and "ninguna" not in texto


def test_traza_omite_la_tabla_si_B_es_grande():
    rc = resolver_caso(_ejemplo(B=B_MAX_TABLA + 1, ids_etapa=()))
    texto = formatear_caso(rc)
    assert "Tabla DP omitida" in texto and "i=0:" not in texto
    assert "Decisiones" in texto            # las decisiones sí se escriben siempre


def test_sin_etapas_aceleradas_dice_ninguna():
    texto = formatear_caso(resolver_caso(_ejemplo(B=0, ids_etapa=())))
    assert "Etapas aceleradas: []   (ninguna)" in texto
