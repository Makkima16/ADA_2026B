"""Pruebas aleatorias: los experimentos en memoria de la PD y del voraz y las rutas de /aleatorios (modo completo y solo una parte)."""

import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from aceleracion.enfoques.dp_por_valor import pruebas_aleatorias as pd
from auditoria.enfoques.comparacion.ablacion import COMBINACIONES, ablacion, ablacion_detalle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "frontend"))
import servidor  # noqa: E402


# ----------------------------- PD -----------------------------

def _pd(**cambios):
    datos = dict(instancias=40, semilla=2026, n_min=5, n_max=20, costo_min=1, costo_max=30, ahorro_min=1, ahorro_max=30,
                 presupuesto_pct=50.0, presupuesto_de_tiempo_s=None)
    datos.update(cambios)
    return pd.experimento(**datos)


def test_pd_las_dos_tablas_dan_siempre_lo_mismo_y_aciertan_a_la_fuerza_bruta():
    r = _pd()
    assert r["hechas"] == 40 and r["ambas"]["corridas"] == r["ambas"]["coinciden"] == 40
    fb = r["fuerza_bruta"]
    assert fb["comparadas"] > 0 and fb["presupuesto_ok"] == fb["valor_ok"] == fb["comparadas"]


def test_pd_es_reproducible_con_semilla_fija():
    a, b = _pd(), _pd()
    for r in (a, b):                       # los tiempos cambian de una corrida a otra; lo demás no
        for g in r["regiones"].values():
            g["tiempo_presupuesto"] = g["tiempo_valor"] = g["regla_mas_rapida"] = 0
    assert a == b


def test_pd_los_casos_se_reparten_en_las_tres_regiones_y_en_las_recomendaciones():
    r = _pd(instancias=60, presupuesto_pct=100)
    assert sum(g["casos"] for g in r["regiones"].values()) == r["hechas"] == 60
    assert sum(r["recomendado"].values()) == 60


def test_pd_con_costos_grandes_y_ahorros_chicos_conviene_valor():
    r = _pd(costo_min=1000, costo_max=9999, ahorro_min=1, ahorro_max=9)
    assert r["recomendado"]["valor"] == 40 and r["recomendado"]["presupuesto"] == 0
    g = r["regiones"]["B mayor que D"]
    assert g["casos"] == 40 and g["corridas"] > 0 and g["celdas_valor"] < g["celdas_presupuesto"]


def test_pd_con_escala_parecida_conviene_casi_siempre_presupuesto():
    r = _pd()
    assert r["recomendado"]["presupuesto"] >= 36                                   # es azar: alguna instancia puede tener B > D
    # propiedad exacta: la tabla por valor se recomienda justo cuando B > D, y la de presupuesto cuando B < D
    assert r["recomendado"]["valor"] == r["regiones"]["B mayor que D"]["casos"]
    assert r["recomendado"]["presupuesto"] == r["regiones"]["B menor que D"]["casos"]


@pytest.mark.parametrize("cambios", [dict(instancias=0), dict(instancias=501), dict(n_min=10, n_max=5), dict(n_max=401),
                                     dict(costo_min=5, costo_max=1), dict(ahorro_max=10 ** 6), dict(presupuesto_pct=-1)])
def test_pd_valida_los_parametros(cambios):
    with pytest.raises(pd.ErrorDeParametros):
        _pd(**cambios)


def test_pd_el_informe_de_texto_trae_las_tres_relaciones():
    texto = pd.formatear(_pd(instancias=10))
    assert "Se corrieron las dos DP" in texto and all(n in texto for n in pd.REGIONES)


# ----------------------------- voraz -----------------------------

def test_voraz_detalle_por_familia_suma_el_total_y_coincide_con_la_ablacion():
    d = ablacion_detalle(20, 2026)
    tabla = ablacion(20, 2026)
    for nombre, *_ in COMBINACIONES:
        assert sum(d["por_familia"][f][nombre] for f in d["por_familia"]) == d[nombre]["no_optimo"] == tabla["total"][nombre]


def test_voraz_detalle_con_una_sola_familia():
    d = ablacion_detalle(30, 2026, ["denso"])
    assert d["instancias"] == 30 and list(d["por_familia"]) == ["denso"]


def test_voraz_ejemplos_son_casos_donde_la_combinacion_empeora_al_voraz():
    from auditoria.auditoria import voraz
    d = ablacion_detalle(150, 2026, None, ejemplos=2)
    assert d["ejemplos"]
    for nombre, lista in d["ejemplos"].items():
        assert len(lista) <= 2 and len(lista) <= d[nombre]["peor"]
        for ej in lista:
            S = [set(s) for s in ej["S"]]
            assert len(ej["combinacion"]) > len(ej["voraz"]) >= len(ej["optimo"])
            assert len(voraz(ej["r"], S)[0]) == len(ej["voraz"])          # el voraz normal da lo que dice el ejemplo


# ----------------------------- rutas del servidor -----------------------------

@pytest.fixture(scope="module")
def url():
    http = ThreadingHTTPServer(("127.0.0.1", 0), servidor.Visor)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % http.server_address[1]
    http.shutdown()
    http.server_close()


def _post(url, ruta, datos):
    pedido = urllib.request.Request(url + ruta, data=json.dumps(datos).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(pedido) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def test_ruta_del_voraz(url):
    estado, d = _post(url, "/api/aleatorios/solo-voraz", {"instancias": 30, "semilla": 2026, "familias": ["ralo", "medio"]})
    assert estado == 200 and d["instancias"] == 60 and [c["nombre"] for c in d["combinaciones"]][0] == "Voraz base"
    assert len(d["combinaciones"]) == 8 and set(d["por_familia"]) == {"ralo", "medio"}


@pytest.mark.parametrize("datos, texto", [({"instancias": 0}, "entre 1 y"), ({"instancias": 99999}, "entre 1 y"),
                                          ({"instancias": 5, "familias": []}, "al menos una densidad"),
                                          ({"instancias": "x"}, "números")])
def test_ruta_del_voraz_valida(url, datos, texto):
    estado, d = _post(url, "/api/aleatorios/solo-voraz", datos)
    assert estado == 400 and texto in d["error"]


def test_ruta_de_la_pd(url):
    estado, d = _post(url, "/api/aleatorios/solo-pd", {"instancias": 15, "n_max": 12})
    assert estado == 200 and d["hechas"] == 15 and d["ambas"]["coinciden"] == d["ambas"]["corridas"]


@pytest.mark.parametrize("datos", [{"instancias": 0}, {"n_min": 9, "n_max": 3}, {"instancias": "x"}])
def test_ruta_de_la_pd_valida(url, datos):
    estado, d = _post(url, "/api/aleatorios/solo-pd", datos)
    assert estado == 400 and d["error"]


# ----------------------------- /aleatorios: modo completo (con carpetas temporales de la prueba) -----------------------------

@pytest.fixture
def carpetas(tmp_path, monkeypatch):
    casos, salida = tmp_path / "casos_temporales", tmp_path / "resultados_temporales"
    monkeypatch.setattr(servidor.carpetas_temporales, "CASOS_TEMPORALES", casos)
    monkeypatch.setattr(servidor.carpetas_temporales, "RESULTADOS_TEMPORALES", salida)
    return casos, salida


def _get(url, ruta):
    with urllib.request.urlopen(url + ruta) as r:
        return json.load(r)


def test_estado_vacio_y_limites(url, carpetas):
    d = _get(url, "/api/aleatorios/estado")
    assert d["casos"] == [] and d["resumen"] == [] and d["enfoques"] == {}
    assert d["limites"] == {"casos": 500, "voraz_por_densidad": 5000, "pd": 500}


def test_generar_probar_y_resumen_por_parte(url, carpetas):
    estado, d = _post(url, "/api/aleatorios/generar", {"cantidad": 6, "semilla": 3, "n_min": 5, "n_max": 9, "r_min": 4, "r_max": 7})
    assert estado == 200 and len(d["casos"]) == 6 and d["enfoques"] == {}
    estado, d = _post(url, "/api/aleatorios/probar", {})
    assert estado == 200 and len(d["resumen"]) == 6 * 14
    e = d["enfoques"]
    assert e["casos"] == 6 and e["parte1"]["hechas"] == 6 and e["parte2"]["instancias"] == 6 and e["variante"]["casos"] == 6
    assert e["variante_parcial"]["casos"] == 6 and e["variante_parcial"]["con_parcial"] > 0    # la extensión con parciales se mide aparte
    assert e["parte1"]["ambas"]["coinciden"] == e["parte1"]["ambas"]["corridas"] == 6          # las dos DP dan lo mismo
    assert e["parte2"]["con_optimo"] == 6 and e["parte2"]["fallan_cobertura"] == 0
    assert e["sin_parte1"] == [] and e["sin_parte2"] == []
    primera = d["resumen"][0]
    assert "Caso:" in _get(url, "/api/aleatorios/traza?archivo=" + primera["traza"])["texto"]


def test_generar_valida_el_tope_de_casos(url, carpetas):
    estado, d = _post(url, "/api/aleatorios/generar", {"cantidad": 501})
    assert estado == 400 and "entre 1 y 500" in d["error"]


def test_subir_archivos_de_una_sola_parte_y_no_aplica(url, carpetas):
    solo_pd = {"parametros": {"presupuesto_aceleracion_B": 5}, "etapas": [
        {"id": "E01", "duracion_normal": 5, "costo_aceleracion": 2, "reduccion_tiempo_si_acelera": 3}]}
    solo_vz = {"categorias_riesgo": [{"id": "R01", "categoria": "a"}], "etapas": [
        {"id": "E01", "riesgos_cubiertos_auditoria_completa": ["R01"]}]}
    estado, d = _post(url, "/api/aleatorios/subir", {"archivos": [{"nombre": "solo_pd.json", "texto": json.dumps(solo_pd)},
                                                                   {"nombre": "solo_voraz.json", "texto": json.dumps(solo_vz)}]})
    assert estado == 200 and [c["nombre"] for c in d["casos"]] == ["solo_pd", "solo_voraz"]
    estado, d = _post(url, "/api/aleatorios/probar", {})
    assert estado == 200 and d["enfoques"]["sin_parte1"] == ["solo_voraz"] and d["enfoques"]["sin_parte2"] == ["solo_pd"]
    assert not any(f["resultado"].startswith("ERROR") for f in d["resumen"])


@pytest.mark.parametrize("cuerpo, texto", [({"archivos": []}, "entre 1 y"), ({"archivos": [{"nombre": "x.json", "texto": "no es json"}]}, "no es un JSON válido"),
                                           ({"otra": 1}, "se esperaba")])
def test_subir_valida(url, carpetas, cuerpo, texto):
    estado, d = _post(url, "/api/aleatorios/subir", cuerpo)
    assert estado == 400 and texto in d["error"]


def test_probar_sin_casos_avisa(url, carpetas):
    estado, d = _post(url, "/api/aleatorios/probar", {})
    assert estado == 400 and "no hay casos" in d["error"]


def test_las_rutas_viejas_del_apartado_4_ya_no_existen(url):
    for ruta in ("/api/auditoria/experimento", "/api/aceleracion/experimento"):
        estado, d = _post(url, ruta, {})
        assert estado == 404


def test_los_visores_aceptan_el_caso_en_la_direccion(url):
    """/auditoria?caso=X y /aceleracion?caso=X sirven la página (el JS pide el caso al servidor y lo analiza)."""
    for ruta in ("/auditoria?caso=aleatorio_001", "/aceleracion?caso=aleatorio_001"):
        with urllib.request.urlopen(url + ruta) as r:
            assert r.status == 200
    for archivo in ("app.js", "aceleracion.js"):
        with urllib.request.urlopen(url + "/estatico/" + archivo) as r:
            assert "/api/aleatorios/caso?nombre=" in r.read().decode("utf-8")


# ----------------------------- /api/auditoria/variante: la variante ponderada paso a paso -----------------------------

def _caso_con_costos():
    from generacion_casos import generador
    return json.dumps(generador.generar_caso("v", 8, 6, 5, 0.4))


def test_variante_devuelve_las_dos_versiones_paso_a_paso(url):
    from auditoria.lectura_ponderada import leer_opciones
    from auditoria.opciones import depurar
    from auditoria.resolver_ponderada import resolver_caso_ponderado
    texto = _caso_con_costos()
    estado, d = _post(url, "/api/auditoria/variante", {"texto": texto, "nombre": "v"})
    assert estado == 200 and not d["sin_costos"] and d["n"] == 8 and d["r"] == 6 and d["n_parciales"] > 0
    c, p = d["completas"], d["parciales"]
    assert c["version"] == "solo completas" and p["version"] == "con parciales" and p["n_opciones"] == 8 + d["n_parciales"]
    assert c["n_opciones"] == 8 and c["factible"] and c["cubre"] and len(c["pasos"]) >= 1
    for v in (c, p):
        assert v["cobertura"] and v["cota"] > 1
        for paso in v["pasos"]:                                                    # cada paso trae sus candidatas, de menor a mayor razón
            razones = [x["razon"] for x in paso["candidatas"]]
            assert razones == sorted(razones) and paso["candidatas"][0]["opcion"] == paso["opcion"]
    # lo que muestra la página es lo que da el proyecto
    import tempfile, pathlib
    ruta = pathlib.Path(tempfile.mkdtemp()) / "v.json"
    ruta.write_text(texto, encoding="utf-8")
    from auditoria.lectura import leer_instancia
    op = leer_opciones(ruta, leer_instancia(ruta))
    rv = resolver_caso_ponderado(op.instancia, op.costos)
    assert p["costo_real"] == depurar(rv.J, op).costo_real and p["optimo_costo"] == rv.optimo_costo
    assert d["parte2"]["costo"] == sum(op.costos[j - 1] for j in d["parte2"]["J"])


def test_variante_con_una_sola_opcion_por_interaccion(url):
    estado, d = _post(url, "/api/auditoria/variante", {"texto": "# costos: 6 6 4\n6 3\n1 2 3\n4 5 6\n1 2 4 5\n", "nombre": "t"})
    assert estado == 200 and d["parciales"] is None and d["completas"]["costo_real"] == 16     # el ejemplo del documento: 16 contra 12
    assert d["completas"]["optimo_costo"] == 12


def test_variante_sin_costos_o_mal_formada(url):
    estado, d = _post(url, "/api/auditoria/variante", {"texto": "6 3\n1 2 4 5\n1 2 3\n4 5 6\n", "nombre": "t"})
    assert estado == 200 and d["sin_costos"] is True
    estado, d = _post(url, "/api/auditoria/variante", {"texto": "# costos: 6 0 4\n6 3\n1 2 4 5\n1 2 3\n4 5 6\n", "nombre": "t"})
    assert estado == 400 and "costos" in d["error"]
    estado, d = _post(url, "/api/auditoria/variante", {"texto": "no es un caso", "nombre": "t"})
    assert estado == 400


def test_variante_no_factible(url):
    estado, d = _post(url, "/api/auditoria/variante", {"texto": "# costos: 1 1\n3 2\n1\n2\n", "nombre": "t"})
    assert estado == 200 and not d["completas"]["factible"] and d["completas"]["sin_cubrir"] == [3]


def test_la_pagina_de_la_variante_y_su_script_se_sirven(url):
    with urllib.request.urlopen(url + "/auditoria") as r:
        cuerpo = r.read().decode("utf-8")
        assert 'id="panel-variante"' in cuerpo and 'data-vista="variante"' in cuerpo and "variante.js" in cuerpo
    with urllib.request.urlopen(url + "/estatico/variante.js") as r:
        assert "/api/auditoria/variante" in r.read().decode("utf-8")
