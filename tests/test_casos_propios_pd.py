"""Pruebas de los casos propios de la Parte 1 (`casos_propios/pd/`)."""

import os
import sys
from pathlib import Path

import pytest

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada, resolver
from aceleracion.enfoques.dp_por_valor.dp_por_valor import resolver_valor
from aceleracion.enfoques.seleccion import elegir_enfoque, resolver_auto, tamanos_de_tablas
from aceleracion.lectura import leer_casos
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA, fuerza_bruta

CARPETA = Path(__file__).resolve().parents[1] / "casos_propios" / "pd"
sys.path.insert(0, str(CARPETA))
import generar_casos  # noqa: E402

CASOS = leer_casos(CARPETA)


def test_hay_los_casos_propios_y_el_ejemplo_de_la_profesora():
    nombres = {c.nombre for c in CASOS}
    assert len(CASOS) == 45 and "entrada_G3_mochila_20_nodos" in nombres and generar_casos.CASO_DE_ERROR in nombres


@pytest.mark.parametrize("inst", [c for c in CASOS if c.nombre != generar_casos.CASO_DE_ERROR], ids=lambda c: c.nombre)
def test_cada_caso_se_resuelve_y_coincide_con_el_optimo(inst):
    rc, _ = resolver_auto(inst)
    assert rc.valida and rc.costo <= inst.B
    celdas = tamanos_de_tablas(inst)
    if len(inst.c) <= N_MAX_FUERZA_BRUTA:
        assert rc.ahorro == fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"]
    if celdas["presupuesto"] <= generar_casos.CELDAS_PARA_CRUZAR and celdas["valor"] <= generar_casos.CELDAS_PARA_CRUZAR:
        assert resolver(inst.t, inst.c, inst.d, inst.B)["ahorro"] == resolver_valor(inst.t, inst.c, inst.d, inst.B)["ahorro"]


def test_los_casos_valor_gana_y_presupuesto_gana_recomiendan_lo_que_dice_su_nombre():
    valor = [c for c in CASOS if "valor_gana" in c.nombre]
    presupuesto = [c for c in CASOS if "presupuesto_gana" in c.nombre]
    assert len(valor) >= 8 and len(presupuesto) >= 6
    assert all(elegir_enfoque(c) == "valor" for c in valor)
    assert all(elegir_enfoque(c) == "presupuesto" for c in presupuesto)


def test_valor_gana_pero_la_base_tambien_cabe_y_da_lo_mismo():
    casos = [c for c in CASOS if "base_si_cabe" in c.nombre]
    assert len(casos) >= 8
    for inst in casos:
        celdas = tamanos_de_tablas(inst)
        assert celdas["valor"] < celdas["presupuesto"] <= MAX_CELDAS_TABLA, inst.nombre   # la base cabe, pero la de valor es más chica
        if celdas["presupuesto"] <= 1_200_000:                                           # y donde es razonable, se corre la base de verdad
            assert resolver(inst.t, inst.c, inst.d, inst.B)["ahorro"] == resolver_valor(inst.t, inst.c, inst.d, inst.B)["ahorro"], inst.nombre


def test_el_empate_se_resuelve_con_la_tabla_base():
    inst = next(c for c in CASOS if c.nombre.startswith("28_"))
    celdas = tamanos_de_tablas(inst)
    assert celdas["presupuesto"] == celdas["valor"] and elegir_enfoque(inst) == "presupuesto"


def test_el_caso_de_error_avisa_que_ninguna_tabla_cabe():
    inst = next(c for c in CASOS if c.nombre == generar_casos.CASO_DE_ERROR)
    with pytest.raises(ErrorDeEntrada, match="ninguna tabla cabe"):
        resolver_auto(inst)


def test_el_caso_17_solo_se_resuelve_por_valor():
    inst = next(c for c in CASOS if c.nombre.startswith("17_"))
    with pytest.raises(ErrorDeEntrada):
        resolver(inst.t, inst.c, inst.d, inst.B)
    assert resolver_auto(inst)[1] == "valor"


def test_el_generador_reproduce_exactamente_los_archivos(tmp_path):
    generar_casos.generar(tmp_path)
    for generado in tmp_path.iterdir():
        assert generado.read_bytes() == (CARPETA / generado.name).read_bytes(), generado.name
