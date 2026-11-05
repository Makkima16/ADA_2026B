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


@pytest.mark.parametrize("archivo", ["aceleracion.js", "aceleracion.css", "inicio.css", "estilos.css", "app.js"])
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


def test_error_de_lectura_y_de_memoria(url):
    estado, d = _post(url, "/api/aceleracion/resolver", "{malo")
    assert estado == 400 and "JSON inválido" in d["error"]
    estado, d = _post(url, "/api/aceleracion/resolver", _caso(B=10 ** 9))
    assert estado == 400 and "no cabe" in d["error"]


def test_tabla_grande_se_omite_pero_se_dan_las_decisiones(url):
    estado, d = _post(url, "/api/aceleracion/resolver", _caso(B=2000, etapas=ETAPAS * 6))
    assert estado == 200 and d["tabla"] is None and d["celdas"] > servidor.MAX_CELDAS_VISIBLES
    assert len(d["decisiones"]) == d["n"] and d["fuerza_bruta"] is None
