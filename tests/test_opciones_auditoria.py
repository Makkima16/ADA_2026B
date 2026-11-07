"""Variante 1 con opciones de auditoría (parcial y completa): lectura, validaciones, depuración y evidencia."""

import copy
import json
from pathlib import Path

import pytest

from auditoria.lectura import leer_instancia
from auditoria.lectura_ponderada import ErrorDeCostos, TIPO_COMPLETA, TIPO_PARCIAL, leer_opciones
from auditoria.opciones import depurar, formatear_opciones
from auditoria.resolver_ponderada import resolver_caso_ponderado
from auditoria.traza_ponderada import formatear_resultado_ponderado

PROFESORA = Path(__file__).resolve().parents[1] / "pruebas" / "casos_propios" / "pd" / "entrada_G3_mochila_20_nodos.json"


def _guardar(tmp_path, datos, nombre="caso.json"):
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def _leer(ruta):
    return leer_opciones(ruta, leer_instancia(ruta))


@pytest.fixture
def base():
    return json.loads(PROFESORA.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ el archivo de la profesora

def test_archivo_de_la_profesora_20_completas_y_15_parciales():
    o = _leer(PROFESORA)
    assert o.n == 20 and len(o.costos) == 35 and o.tipo.count(TIPO_PARCIAL) == 15 and o.hay_parcial
    assert o.tipo[:20] == [TIPO_COMPLETA] * 20                                  # las completas conservan los índices 1..n
    assert o.interaccion[:20] == list(range(1, 21))
    assert o.costos[0] == 6 and o.instancia.ids_interaccion[0] == "E01 (completa)"
    k = 20 + 1                                                                  # primera parcial: la de E01 (cuesta 3 y cubre 2 riesgos)
    assert o.instancia.ids_interaccion[k - 1] == "E01 (parcial)" and o.costos[k - 1] == 3 and len(o.instancia.S[k - 1]) == 2
    assert o.instancia.S[:20] == [set(s) for s in leer_instancia(PROFESORA).S]  # las completas son las S_j de siempre


def test_archivo_de_la_profesora_resultado_de_la_variante():
    o = _leer(PROFESORA)
    rv = resolver_caso_ponderado(o.instancia, o.costos)
    dep = depurar(rv.J, o)
    assert rv.factible and rv.cubre and rv.optimo_costo == 24                   # 35 opciones > 12: el mínimo real llega por subconjuntos (r = 12)
    assert [o.instancia.etiqueta_interaccion(k) for k in dep.conservadas] == [
        "E01 (completa)", "E16 (completa)", "E06 (completa)", "E03 (parcial)"]
    assert dep.costo_real == dep.costo_voraz == 26 and not dep.descartadas
    texto = formatear_resultado_ponderado(rv) + formatear_opciones(rv, o, dep)
    assert "Interacciones: 20 | opciones: 35 (20 completas, 15 parciales)" in texto
    assert "Costo del voraz: 26 | Costo real tras depurar: 26" in texto
    assert "(subconjuntos de categorías): 24 | razón costo real / óptimo: 1.0833" in texto


def test_la_cota_se_mantiene_con_las_parciales():
    o = _leer(PROFESORA)
    rv = resolver_caso_ponderado(o.instancia, o.costos)
    assert rv.cota == pytest.approx(2.0833, abs=1e-4)                            # H(d) con d = 4: las parciales no cambian d


# ------------------------------------------------------------------ validaciones

def test_etapa_sin_completa(tmp_path, base):
    base["etapas"][2]["variaciones_auditoria"] = [v for v in base["etapas"][2]["variaciones_auditoria"] if v["id"] != "completa"]
    with pytest.raises(ErrorDeCostos, match="etapa 3: falta la variación 'completa'"):
        _leer(_guardar(tmp_path, base))


def test_variacion_con_id_desconocido(tmp_path, base):
    base["etapas"][0]["variaciones_auditoria"][0]["id"] = "media"
    with pytest.raises(ErrorDeCostos, match="'completa' y, opcionalmente, una 'parcial'"):
        _leer(_guardar(tmp_path, base))


def test_parcial_que_cubre_mas_que_la_completa(tmp_path, base):
    e = base["etapas"][0]
    parcial = next(v for v in e["variaciones_auditoria"] if v["id"] == "parcial")
    parcial["riesgos_cubiertos"] = parcial["riesgos_cubiertos"] + ["R12"]
    with pytest.raises(ErrorDeCostos, match="'parcial' cubre riesgos que la 'completa' no cubre"):
        _leer(_guardar(tmp_path, base))


def test_completa_que_no_coincide_con_la_interaccion(tmp_path, base):
    completa = next(v for v in base["etapas"][0]["variaciones_auditoria"] if v["id"] == "completa")
    completa["riesgos_cubiertos"] = completa["riesgos_cubiertos"][:-1]
    with pytest.raises(ErrorDeCostos, match="no cubre lo mismo que riesgos_cubiertos_auditoria_completa"):
        _leer(_guardar(tmp_path, base))


def test_costo_invalido_y_categoria_inexistente(tmp_path, base):
    malo = copy.deepcopy(base)
    malo["etapas"][1]["variaciones_auditoria"][-1]["costo"] = 0
    with pytest.raises(ErrorDeCostos, match="'costo' debe ser un número > 0"):
        _leer(_guardar(tmp_path, malo))
    malo = copy.deepcopy(base)
    malo["etapas"][1]["variaciones_auditoria"][0]["riesgos_cubiertos"] = ["R99"]
    with pytest.raises(ErrorDeCostos, match="no está en categorias_riesgo"):
        _leer(_guardar(tmp_path, malo))


def test_etapas_que_traen_variaciones_y_otras_no(tmp_path, base):
    del base["etapas"][5]["variaciones_auditoria"]
    with pytest.raises(ErrorDeCostos, match="etapa 6: falta 'variaciones_auditoria'"):
        _leer(_guardar(tmp_path, base))


# ------------------------------------------------------------------ otras formas de traer costos

def test_forma_anterior_costo_auditoria_una_sola_opcion(tmp_path, base):
    for e in base["etapas"]:
        e["costo_auditoria"] = 5
        del e["variaciones_auditoria"]
    o = _leer(_guardar(tmp_path, base))
    assert o.costos == [5] * 20 and not o.hay_parcial and o.instancia.ids_interaccion[0] == "E01"


def test_sin_costos_devuelve_none(tmp_path, base):
    for e in base["etapas"]:
        del e["variaciones_auditoria"]
    assert _leer(_guardar(tmp_path, base)) is None


def test_txt_con_linea_de_costos(tmp_path):
    ruta = tmp_path / "t.txt"
    ruta.write_text("# costos: 3 4 5\n6 3\n1 2 4 5\n1 2 3\n4 5 6\n", encoding="utf-8")
    o = _leer(ruta)
    assert o.costos == [3, 4, 5] and o.tipo == ["única"] * 3


# ------------------------------------------------------------------ depuración

def _con_parcial(tmp_path):
    """Caso a mano donde el voraz toma primero una parcial barata y después la completa de la misma interacción."""
    def etapa(i, completa, costo_c, parcial=None, costo_p=None):
        var = [{"id": "completa", "costo": costo_c, "riesgos_cubiertos": completa}]
        if parcial:
            var.insert(0, {"id": "parcial", "costo": costo_p, "riesgos_cubiertos": parcial})
        return {"id": "E%02d" % i, "duracion_normal": 5, "costo_aceleracion": 1, "reduccion_tiempo_si_acelera": 1,
                "riesgos_cubiertos_auditoria_completa": completa, "variaciones_auditoria": var}
    # E01: completa {R01,R02,R03} cuesta 30; parcial {R01} cuesta 1 (ratio 1/1, la mejor al principio).
    # E02: {R02,R03} cuesta 2.  Con la parcial de E01 + E02 alcanza; el voraz escoge ese par y no repite E01.
    datos = {"parametros": {"numero_etapas": 2, "numero_categorias_riesgo": 3, "presupuesto_aceleracion_B": 1},
             "categorias_riesgo": [{"id": "R%02d" % k, "categoria": "c%d" % k} for k in (1, 2, 3)],
             "etapas": [etapa(1, ["R01", "R02", "R03"], 30, ["R01"], 1), etapa(2, ["R02", "R03"], 2)]}
    return _leer(_guardar(tmp_path, datos))


def test_el_voraz_escoge_la_parcial_cuando_conviene(tmp_path):
    o = _con_parcial(tmp_path)
    rv = resolver_caso_ponderado(o.instancia, o.costos)
    dep = depurar(rv.J, o)
    assert sorted(o.instancia.etiqueta_interaccion(k) for k in dep.conservadas) == ["E01 (parcial)", "E02 (completa)"]
    assert dep.costo_real == 3 and rv.optimo_costo == 3                          # óptimo por fuerza bruta sobre las 3 opciones


def test_depurar_quita_la_parcial_si_tambien_se_eligio_la_completa(tmp_path):
    o = _con_parcial(tmp_path)
    # Opciones: 1 = E01 completa, 2 = E02 completa, 3 = E01 parcial. Un J con la parcial y la completa de E01:
    dep = depurar([3, 1], o)
    assert dep.descartadas == [3] and dep.conservadas == [1]
    assert dep.costo_voraz == 31 and dep.costo_real == 30 and dep.ahorro == 1
    sin_repetir = depurar([3, 2], o)                                             # parcial de E01 + E02: nada que depurar
    assert sin_repetir.descartadas == [] and sin_repetir.costo_real == 3
    rv = resolver_caso_ponderado(o.instancia, o.costos)
    assert "Depuración: se eligió también la completa de E01 (parcial)" in formatear_opciones(rv, o, dep)
