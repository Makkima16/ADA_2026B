"""Pruebas de las pruebas aleatorias (sección 4 de los visores): la de la PD, la del voraz y sus rutas del servidor."""

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
    estado, d = _post(url, "/api/auditoria/experimento", {"instancias": 30, "semilla": 2026, "familias": ["ralo", "medio"]})
    assert estado == 200 and d["instancias"] == 60 and [c["nombre"] for c in d["combinaciones"]][0] == "Voraz base"
    assert len(d["combinaciones"]) == 8 and set(d["por_familia"]) == {"ralo", "medio"}


@pytest.mark.parametrize("datos, texto", [({"instancias": 0}, "entre 1 y"), ({"instancias": 99999}, "entre 1 y"),
                                          ({"instancias": 5, "familias": []}, "al menos una densidad"),
                                          ({"instancias": "x"}, "números")])
def test_ruta_del_voraz_valida(url, datos, texto):
    estado, d = _post(url, "/api/auditoria/experimento", datos)
    assert estado == 400 and texto in d["error"]


def test_ruta_de_la_pd(url):
    estado, d = _post(url, "/api/aceleracion/experimento", {"instancias": 15, "n_max": 12})
    assert estado == 200 and d["hechas"] == 15 and d["ambas"]["coinciden"] == d["ambas"]["corridas"]


@pytest.mark.parametrize("datos", [{"instancias": 0}, {"n_min": 9, "n_max": 3}, {"instancias": "x"}])
def test_ruta_de_la_pd_valida(url, datos):
    estado, d = _post(url, "/api/aceleracion/experimento", datos)
    assert estado == 400 and d["error"]
