"""Pruebas de los casos propios de la Parte 2 (`Casos/casos_propios/voraz/`): son 20 archivos JSON."""

from pathlib import Path

import pytest

from auditoria.lectura import leer_casos
from auditoria.resolver import resolver_caso

CARPETA = Path(__file__).resolve().parents[1] / "Casos" / "casos_propios" / "voraz"


def test_la_carpeta_solo_tiene_json_y_hay_20_casos():
    assert not list(CARPETA.glob("*.txt"))
    assert len(list(CARPETA.glob("*.json"))) == 20 == len(leer_casos(CARPETA))


@pytest.mark.parametrize("inst", leer_casos(CARPETA), ids=lambda i: i.nombre)
def test_cada_caso_se_lee_con_ids_y_se_resuelve(inst):
    assert inst.ids_interaccion[0] == "E01" and inst.ids_categoria[0] == "R01"
    res = resolver_caso(inst)
    if inst.nombre == "01_no_factible":
        assert not res.factible
    else:
        assert res.factible and res.J
