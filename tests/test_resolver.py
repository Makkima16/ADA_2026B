"""Pruebas de la salida por caso (resolver + formato de la evidencia)."""

from ruta.auditoria import N_MAX_FUERZA_BRUTA
from ruta.resolver import Instancia, resolver_caso
from ruta.traza import formatear_resultado

CLASICA = Instancia("clasica", 6, [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}])


def test_resultado_caso_factible():
    res = resolver_caso(CLASICA)
    assert res.factible and res.cubre
    assert res.J == [1, 2, 3]
    assert res.tiempo_s >= 0.0
    assert len(res.optimo) == 2
    assert len(res.J) <= res.cota * len(res.optimo) + 1e-9


def test_caso_no_factible_no_ejecuta_el_voraz():
    res = resolver_caso(Instancia("sin_cobertura", 4, [{1, 2}, {2, 3}]))
    assert not res.factible
    assert res.sin_cubrir == {4}
    assert res.J == [] and res.pasos == []
    assert "NO factible" in formatear_resultado(res)


def test_sin_optimo_si_n_supera_el_limite_o_no_se_pide():
    grande = Instancia("grande", 1, [{1}] * (N_MAX_FUERZA_BRUTA + 1))
    assert resolver_caso(grande).optimo is None
    assert resolver_caso(CLASICA, comparar_con_optimo=False).optimo is None


def test_formatear_resultado_incluye_lo_pedido_por_la_guia():
    texto = formatear_resultado(resolver_caso(CLASICA))
    assert "Caso: clasica" in texto
    assert "Paso 1: interacción 1" in texto
    assert "Interacciones auditadas: [1, 2, 3] (3)" in texto
    assert "Cubre todas las categorías: sí" in texto
    assert "Tiempo:" in texto
    assert "Óptimo por fuerza bruta: [2, 3] (2)" in texto
    assert "Cota H(d):" in texto
