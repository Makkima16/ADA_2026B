"""Experimento de verificación de la variante 1 (voraz ponderado contra el óptimo y la cota H(d))."""

import pytest

from auditoria import experimento_ponderada as exp


def test_nunca_supera_la_cota_y_es_reproducible():
    a, b = exp.correr(40, 2026), exp.correr(40, 2026)
    assert a == b                                                   # misma semilla, mismos resultados
    for r in a:
        assert r["instancias"] == 40 and r["superan_cota"] == 0     # costo(voraz) <= H(d)·costo(óptimo), Chvátal 1979
        assert 1.0 <= r["razon_media"] <= r["razon_max"] and 0 < r["optimas"] <= 40


def test_los_tiempos_traen_los_pasos_y_el_cociente():
    filas = exp.medir_tiempos((6, 12), repeticiones=2)
    assert [f["n"] for f in filas] == [6, 12] and all(f["pasos"] >= 1 and f["tiempo_ms"] > 0 and f["cociente"] > 0 for f in filas)


def test_formatear_y_main(capsys):
    r = exp.correr(10, 1)
    texto = exp.formatear(r, exp.medir_tiempos((6,), repeticiones=1))
    assert "30 instancias" in texto and "Superan H(d)" in texto and "Tiempo / (n·r·min(n, r))" in texto
    assert exp.main(["--instancias", "5", "--sin-tiempos"]) == 0
    assert "Total: óptimo en" in capsys.readouterr().out
    assert exp.main(["--instancias", "0"]) == 2


def test_reproduce_las_cifras_del_documento_de_la_variante():
    """Semilla 2026, 1000 instancias por familia: 735, 645 y 650 óptimos; peor razón 1,909; nunca supera H(d)."""
    r = exp.correr(1000, 2026)
    assert [x["optimas"] for x in r] == [735, 645, 650]
    assert [round(x["razon_media"], 3) for x in r] == [1.028, 1.058, 1.079]
    assert [round(x["razon_max"], 3) for x in r] == [1.421, 1.650, 1.909]
    assert sum(x["superan_cota"] for x in r) == 0
