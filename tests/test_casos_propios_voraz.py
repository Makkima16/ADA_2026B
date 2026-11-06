"""Pruebas de los casos propios de la Parte 2 (`casos_propios/voraz/`): están en JSON y equivalen a los `.txt` originales."""

import sys
from pathlib import Path

import pytest

from auditoria.lectura import leer_casos, leer_instancia
from auditoria.resolver import resolver_caso

CARPETA = Path(__file__).resolve().parents[1] / "casos_propios" / "voraz"
sys.path.insert(0, str(CARPETA))
import convertir_a_json  # noqa: E402

TXT = sorted((CARPETA / "txt_originales").glob("*.txt"))


def test_la_carpeta_solo_tiene_json_y_hay_20_casos():
    assert not list(CARPETA.glob("*.txt"))
    assert len(list(CARPETA.glob("*.json"))) == 20 == len(TXT) == len(leer_casos(CARPETA))


@pytest.mark.parametrize("txt", TXT, ids=lambda p: p.stem)
def test_cada_json_equivale_a_su_txt_original(txt):
    original = leer_instancia(txt)
    convertido = leer_instancia(CARPETA / (txt.stem + ".json"))
    assert (convertido.nombre, convertido.r, convertido.S) == (original.nombre, original.r, original.S)
    assert convertido.ids_interaccion[0] == "E01" and convertido.ids_categoria[0] == "R01"


@pytest.mark.parametrize("inst", leer_casos(CARPETA), ids=lambda i: i.nombre)
def test_cada_caso_se_resuelve(inst):
    res = resolver_caso(inst)
    if inst.nombre == "01_no_factible":
        assert not res.factible
    else:
        assert res.factible and res.J


def test_el_conversor_reproduce_los_archivos(tmp_path):
    convertir_a_json.convertir(salida=tmp_path)
    for generado in tmp_path.iterdir():
        assert generado.read_bytes() == (CARPETA / generado.name).read_bytes(), generado.name
