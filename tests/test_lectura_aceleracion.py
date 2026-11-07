"""Pruebas del lector de la Parte 1 (formato JSON de la profesora)."""

import json

import pytest

from aceleracion.aceleracion import resolver
from aceleracion.lectura import ErrorDeLectura, leer_casos, leer_instancia
from aceleracion.verificacion import fuerza_bruta


def _caso(**cambios):
    datos = {
        "parametros": {"numero_etapas": 4, "presupuesto_aceleracion_B": 5},
        "etapas": [
            {"id": "E01", "duracion_normal": 4, "costo_aceleracion": 2, "reduccion_tiempo_si_acelera": 3},
            {"id": "E02", "duracion_normal": 3, "costo_aceleracion": 3, "reduccion_tiempo_si_acelera": 2},
            {"id": "E03", "duracion_normal": 5, "costo_aceleracion": 4, "reduccion_tiempo_si_acelera": 4},
            {"id": "E04", "duracion_normal": 2, "costo_aceleracion": 1, "reduccion_tiempo_si_acelera": 1},
        ],
        "categorias_riesgo": [{"id": "R01", "categoria": "x", "importancia": 1}],  # de la Parte 2: se ignora
        "flujo": [],
    }
    datos.update(cambios)
    return datos


def _escribir(tmp_path, datos, nombre="caso.json"):
    archivo = tmp_path / nombre
    archivo.write_text(json.dumps(datos), encoding="utf-8")
    return archivo


def test_lee_un_caso_y_el_dp_lo_resuelve(tmp_path):
    inst = leer_instancia(_escribir(tmp_path, _caso(), "ejemplo.json"))
    assert inst.nombre == "ejemplo" and inst.B == 5
    assert inst.t == [4, 3, 5, 2] and inst.c == [2, 3, 4, 1] and inst.d == [3, 2, 4, 1]
    assert inst.ids_etapa == ("E01", "E02", "E03", "E04")
    res = resolver(inst.t, inst.c, inst.d, inst.B)
    assert res["ahorro"] == fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"] == 5


def test_leer_casos_ordena_e_ignora_otros_formatos(tmp_path):
    _escribir(tmp_path, _caso(), "b.json")
    _escribir(tmp_path, _caso(), "a.json")
    (tmp_path / "c.txt").write_text("6 3\n", encoding="utf-8")
    assert [i.nombre for i in leer_casos(tmp_path)] == ["a", "b"]


def test_solo_acepta_json(tmp_path):
    (tmp_path / "caso.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ErrorDeLectura, match="solo lee archivos .json"):
        leer_instancia(tmp_path / "caso.txt")


def _con_etapa(**cambios):
    datos = _caso()
    datos["etapas"][0].update(cambios)
    return datos


@pytest.mark.parametrize("datos,mensaje", [
    (_caso(parametros={"numero_etapas": 4}), "presupuesto_aceleracion_B"),
    (_caso(parametros={"numero_etapas": 4, "presupuesto_aceleracion_B": -1}), "presupuesto_aceleracion_B"),
    (_caso(parametros={"numero_etapas": 7, "presupuesto_aceleracion_B": 5}), "numero_etapas"),
    (_caso(etapas=[]), "etapas"),
    (_con_etapa(reduccion_tiempo_si_acelera=9), "supera la duración"),
    (_con_etapa(costo_aceleracion=-2), "costo_aceleracion"),
    (_con_etapa(duracion_normal="4"), "duracion_normal"),
    (_con_etapa(costo_aceleracion=True), "costo_aceleracion"),
    (_con_etapa(id="E02"), "repetidos"),
])
def test_errores_de_formato(tmp_path, datos, mensaje):
    with pytest.raises(ErrorDeLectura, match=mensaje):
        leer_instancia(_escribir(tmp_path, datos))


def test_json_invalido(tmp_path):
    archivo = tmp_path / "roto.json"
    archivo.write_text("{ no es json", encoding="utf-8")
    with pytest.raises(ErrorDeLectura, match="JSON inválido"):
        leer_instancia(archivo)


def test_ejemplo_real_de_la_profesora_si_esta():
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[1] / "pruebas" / "casos_propios" / "pd" / "entrada_G3_mochila_20_nodos.json"
    if not ruta.exists():
        pytest.skip("el ejemplo está solo en el material local")
    inst = leer_instancia(ruta)
    assert len(inst.t) == 20 and inst.B == 72
    res = resolver(inst.t, inst.c, inst.d, inst.B)
    assert res["costo"] <= inst.B and sum(inst.d[i - 1] for i in res["aceleradas"]) == res["ahorro"]
