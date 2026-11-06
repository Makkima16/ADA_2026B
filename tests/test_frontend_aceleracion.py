"""Pruebas del visor local: páginas y rutas de la Parte 1 (aceleración, DP)."""

import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "frontend"))
import servidor  # noqa: E402

from aceleracion.verificacion import fuerza_bruta  # noqa: E402

ETAPAS = [(10, 5, 6), (8, 4, 5), (7, 3, 4), (9, 6, 7), (6, 2, 3)]   # (t, c, d)


def _caso(B=10, etapas=ETAPAS):
    return json.dumps({
        "parametros": {"presupuesto_aceleracion_B": B},
        "etapas": [{"id": "E%02d" % (k + 1), "duracion_normal": t, "costo_aceleracion": c,
                    "reduccion_tiempo_si_acelera": d} for k, (t, c, d) in enumerate(etapas)],
    })


@pytest.fixture(scope="module")
def url():
    http = ThreadingHTTPServer(("127.0.0.1", 0), servidor.Visor)
    hilo = threading.Thread(target=http.serve_forever, daemon=True)
    hilo.start()
    yield "http://127.0.0.1:%d" % http.server_address[1]
    http.shutdown()
    http.server_close()


def _get(url, ruta):
    with urllib.request.urlopen(url + ruta) as r:
        return r.status, r.read().decode("utf-8")


def _post(url, ruta, texto, nombre="caso"):
    pedido = urllib.request.Request(url + ruta, data=json.dumps({"texto": texto, "nombre": nombre}).encode("utf-8"),
                                    headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(pedido) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


@pytest.mark.parametrize("ruta, fragmento", [
    ("/", "¿Qué quieres explicar hoy?"),
    ("/aceleracion", "¿Qué conviene acelerar?"),
    ("/auditoria", "¿Qué conviene auditar?"),
    ("/index.html", "¿Qué conviene auditar?"),
])
def test_paginas(url, ruta, fragmento):
    estado, cuerpo = _get(url, ruta)
    assert estado == 200 and fragmento in cuerpo


@pytest.mark.parametrize("archivo", ["aceleracion.js", "aceleracion.css", "inicio.css", "estilos.css", "app.js", "explicacion.js", "combinador.js", "pruebas.js", "pruebas_pd.js"])
def test_estaticos(url, archivo):
    assert _get(url, "/estatico/" + archivo)[0] == 200


def test_resolver_coincide_con_dp_y_fuerza_bruta(url):
    estado, d = _post(url, "/api/aceleracion/resolver", _caso())
    assert estado == 200
    t, c, dd = [e[0] for e in ETAPAS], [e[1] for e in ETAPAS], [e[2] for e in ETAPAS]
    optimo = fuerza_bruta(t, c, dd, 10)["ahorro"]
    assert d["ahorro"] == optimo == d["fuerza_bruta"]["ahorro"]
    assert d["costo"] <= d["B"] and d["valida"]
    assert d["duracion_final"] == sum(t) - d["ahorro"]
    assert len(d["tabla"]) == d["n"] + 1 and len(d["tabla"][0]) == d["B"] + 1


def test_decisiones_coherentes_con_la_solucion(url):
    _, d = _post(url, "/api/aceleracion/resolver", _caso())
    assert [x["i"] for x in d["decisiones"]] == list(range(d["n"], 0, -1))
    assert sorted(x["i"] for x in d["decisiones"] if x["acelerada"]) == d["aceleradas"]
    assert d["decisiones"][0]["b"] == d["B"]
    gastado = d["B"] - d["decisiones"][-1]["b_despues"]
    assert gastado == d["costo"]


def test_previsualizar_no_resuelve(url):
    estado, d = _post(url, "/api/aceleracion/previsualizar", _caso())
    assert estado == 200 and d["n"] == 5 and d["B"] == 10 and "tabla" not in d


def _post_enfoque(url, texto, enfoque):
    pedido = urllib.request.Request(url + "/api/aceleracion/resolver", headers={"Content-Type": "application/json"},
                                    data=json.dumps({"texto": texto, "nombre": "caso", "enfoque": enfoque}).encode("utf-8"))
    try:
        with urllib.request.urlopen(pedido) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def test_error_de_lectura(url):
    estado, d = _post(url, "/api/aceleracion/resolver", "{malo")
    assert estado == 400 and "JSON inválido" in d["error"]


def test_previsualizar_trae_tamanos_de_las_dos_tablas(url):
    _, d = _post(url, "/api/aceleracion/previsualizar", _caso())
    assert d["celdas_presupuesto"] == 6 * 11 and d["celdas_valor"] == 6 * 26
    assert d["recomendado"] == "presupuesto" and d["limite_celdas"] == 10_000_000


@pytest.mark.parametrize("enfoque", ["presupuesto", "valor", "auto"])
def test_los_dos_enfoques_dan_el_mismo_ahorro(url, enfoque):
    estado, d = _post_enfoque(url, _caso(), enfoque)
    assert estado == 200 and d["ahorro"] == 13 and d["valida"] and d["fuerza_bruta"]["ahorro"] == 13
    assert d["enfoque"] == ("presupuesto" if enfoque == "auto" else enfoque)


def test_enfoque_valor_tiene_tabla_por_ahorro_con_nulos(url):
    _, d = _post_enfoque(url, _caso(), "valor")
    assert d["D"] == 25 and len(d["tabla"][0]) == 26 and d["tabla"][0][0] == 0 and d["tabla"][0][1] is None
    assert d["tabla"][-1][d["ahorro"]] == d["costo"]
    dec = d["decisiones"]
    assert dec[0]["b"] == d["ahorro"] and dec[-1]["b_despues"] == 0
    assert sorted(x["i"] for x in dec if x["acelerada"]) == d["aceleradas"]
    assert "DP por valor" in d["evidencia"]


def test_enfoque_desconocido(url):
    estado, d = _post_enfoque(url, _caso(), "magico")
    assert estado == 400 and "enfoque desconocido" in d["error"]


def test_auto_usa_valor_con_B_enorme_y_la_base_da_error(url):
    estado, d = _post_enfoque(url, _caso(B=10 ** 9), "auto")
    assert estado == 200 and d["enfoque"] == "valor" and d["ahorro"] == 25
    estado, d = _post_enfoque(url, _caso(B=10 ** 9), "presupuesto")
    assert estado == 400 and "no cabe" in d["error"]


def test_error_si_ninguna_tabla_cabe(url):
    caso = _caso(B=10 ** 9, etapas=[(10 ** 7, 1, 10 ** 7)] * 2)
    estado, d = _post_enfoque(url, caso, "auto")
    assert estado == 400 and "ninguna tabla cabe" in d["error"]


def test_tabla_grande_se_omite_pero_se_dan_las_decisiones(url):
    estado, d = _post_enfoque(url, _caso(B=2000, etapas=ETAPAS * 6), "presupuesto")
    assert estado == 200 and d["tabla"] is None and d["celdas"] > servidor.MAX_CELDAS_VISIBLES
    assert len(d["decisiones"]) == d["n"] and d["fuerza_bruta"] is None
