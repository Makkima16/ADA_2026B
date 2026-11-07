"""Pruebas de la generación de casos aleatorios y su prueba inmediata (carpetas temporales)."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from generacion_casos import carpetas, generador, probar  # noqa: E402


def test_mismos_parametros_dan_los_mismos_casos():
    a = generador.generar_lote(8, semilla=5, n_min=5, n_max=9, r_min=4, r_max=8)
    b = generador.generar_lote(8, semilla=5, n_min=5, n_max=9, r_min=4, r_max=8)
    c = generador.generar_lote(8, semilla=6, n_min=5, n_max=9, r_min=4, r_max=8)
    assert a == b and a != c


def test_todos_los_casos_son_factibles_y_respetan_los_rangos():
    for caso in generador.generar_lote(60, semilla=1, n_min=3, n_max=15, r_min=2, r_max=20):
        p = caso["parametros"]
        n, r = p["numero_etapas"], p["numero_categorias_riesgo"]
        assert 3 <= n <= 15 and 2 <= r <= 20 and len(caso["etapas"]) == n
        cubiertas = set()
        for e in caso["etapas"]:
            assert e["riesgos_cubiertos_auditoria_completa"], "interacción vacía"
            assert 0 <= e["reduccion_tiempo_si_acelera"] <= e["duracion_normal"]
            ids = [v["id"] for v in e["variaciones_auditoria"]]
            assert ids in (["completa"], ["parcial", "completa"])
            comp = e["variaciones_auditoria"][-1]
            assert comp["costo"] >= 1 and comp["riesgos_cubiertos"] == e["riesgos_cubiertos_auditoria_completa"]
            if len(ids) == 2:                                    # la parcial cubre un subconjunto propio y no cuesta más
                par = e["variaciones_auditoria"][0]
                assert par["riesgos_cubiertos"] and set(par["riesgos_cubiertos"]) < set(comp["riesgos_cubiertos"])
                assert 1 <= par["costo"] <= comp["costo"]
            cubiertas.update(e["riesgos_cubiertos_auditoria_completa"])
        assert len(cubiertas) == r                              # factible: nadie queda sin cubrir


def test_el_juego_fijo_tiene_22_y_110_casos():
    assert len(generador.generar_juego_fijo()) == 22
    assert len(generador.generar_juego_fijo(malla=True)) == 110


@pytest.mark.parametrize("kw", [dict(cantidad=0), dict(cantidad=generador.MAX_CASOS + 1),
                                dict(n_min=0), dict(n_min=9, n_max=8), dict(n_max=generador.MAX_N + 1),
                                dict(r_min=5, r_max=4), dict(r_max=generador.MAX_R + 1),
                                dict(densidades=["espeso"])])
def test_parametros_invalidos_se_rechazan(kw):
    base = dict(cantidad=5, semilla=1, n_min=5, n_max=8, r_min=4, r_max=6, densidades=["ralo"])
    base.update(kw)
    with pytest.raises(generador.ErrorDeParametros):
        generador.generar_lote(**base)


def test_vaciar_solo_toca_las_carpetas_temporales(tmp_path):
    ajena = tmp_path / "casos"
    ajena.mkdir()
    (ajena / "profesora.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        carpetas.vaciar(ajena)
    assert (ajena / "profesora.json").exists()                  # la carpeta de la profesora no se toca

    temporal = tmp_path / "casos_temporales"
    temporal.mkdir()
    (temporal / "a.json").write_text("{}", encoding="utf-8")
    (temporal / "b.csv").write_text("x", encoding="utf-8")
    (temporal / "ajeno.py").write_text("x", encoding="utf-8")   # extensión no borrable
    (temporal / "sub").mkdir()
    (temporal / "sub" / "c.json").write_text("{}", encoding="utf-8")
    assert carpetas.vaciar(temporal) == 2
    assert sorted(p.name for p in temporal.iterdir()) == ["ajeno.py", "sub"]
    assert (temporal / "sub" / "c.json").exists()               # nunca recursivo


def test_generar_reemplaza_y_no_acumula(tmp_path):
    temporal = tmp_path / "casos_temporales"
    carpetas.escribir_casos(generador.generar_lote(5, semilla=1), temporal)
    assert len(carpetas.listar_casos(temporal)) == 5
    carpetas.escribir_casos(generador.generar_lote(3, semilla=2), temporal)
    assert len(carpetas.listar_casos(temporal)) == 3
    nombre = carpetas.listar_casos(temporal)[0]["nombre"]
    assert json.loads(carpetas.leer_texto_caso(nombre, temporal))["nombre"] == nombre
    with pytest.raises(FileNotFoundError):
        carpetas.leer_texto_caso("../../etc/passwd", temporal)  # solo nombres que estén en la carpeta


def test_probar_de_punta_a_punta_y_sin_acumular(tmp_path):
    casos, salida = tmp_path / "casos_temporales", tmp_path / "resultados_temporales"
    carpetas.escribir_casos(generador.generar_lote(4, semilla=3, n_min=5, n_max=8, r_min=4, r_max=7), casos)
    for _ in range(2):                                          # la segunda vez reemplaza, no acumula
        proceso = probar.probar(casos, salida)
        assert proceso.returncode == 0, proceso.stderr
        filas = probar.leer_resumen(salida)
        assert len(filas) == 4 * 14                             # por caso: parte1 (+2 tablas), parte2 (+8 enfoques), variante1 y variante1_parcial
        partes = {f["parte"] for f in filas}
        assert {"parte1", "parte1_presupuesto", "parte1_valor", "parte2", "parte2_voraz", "parte2_todo", "variante1", "variante1_parcial"} <= partes
    assert "Parte 1" in probar.leer_comparacion(salida)
    assert "Caso:" in probar.leer_traza(filas[0]["traza"], salida)
    with pytest.raises(FileNotFoundError):
        probar.leer_traza("../resumen.csv", salida)
    with pytest.raises(FileNotFoundError):
        probar.leer_traza("", salida)                          # las filas «no aplica» no tienen traza


def test_probar_sin_casos_avisa(tmp_path):
    with pytest.raises(ValueError):
        probar.probar(tmp_path / "casos_temporales", tmp_path / "resultados_temporales")


def test_subir_archivos_reemplaza_y_sanea_los_nombres(tmp_path):
    temporal = tmp_path / "casos_temporales"
    carpetas.escribir_casos(generador.generar_lote(3, semilla=1), temporal)
    nombres = carpetas.escribir_archivos([("../../etc/Caso Uno.json", "{}"), ("Caso Uno.json", '{"a": 1}'),
                                          ("otro.JSON", "{}")], temporal)
    assert nombres == ["Caso_Uno", "Caso_Uno_2", "otro"]                 # sin rutas, sin espacios, repetidos numerados
    assert sorted(p.name for p in temporal.iterdir()) == ["Caso_Uno.json", "Caso_Uno_2.json", "otro.json"]


def test_subir_archivos_malos_no_borran_lo_que_habia(tmp_path):
    temporal = tmp_path / "casos_temporales"
    carpetas.escribir_casos(generador.generar_lote(3, semilla=1), temporal)
    for malos in ([], [("a.json", "no es json")], [("a.json", "[1, 2]")], [("a.json", "{}")] * (carpetas.MAX_ARCHIVOS_SUBIDOS + 1)):
        with pytest.raises(carpetas.ErrorDeArchivos):
            carpetas.escribir_archivos(malos, temporal)
    assert len(carpetas.listar_casos(temporal)) == 3
