import pytest

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada, resolver, verificar_tamano_tabla
from aceleracion.verificacion import fuerza_bruta, generar_instancia


def test_dp_igual_a_fuerza_bruta():
    for semilla in range(50):
        for n in range(1, 13):
            t, c, d, B = generar_instancia(n, semilla)
            dp = resolver(t, c, d, B)
            fb = fuerza_bruta(t, c, d, B)
            assert dp["ahorro"] == fb["ahorro"]
            assert dp["duracion_final"] == fb["duracion_final"]
            assert dp["costo"] <= B


def test_ejemplo_a_mano():
    res = resolver([4, 3, 5, 2], [2, 3, 4, 1], [3, 2, 4, 1], 5)
    assert res["ahorro"] == 5
    assert res["duracion_final"] == 9


def test_casos_borde():
    assert resolver([], [], [], 5)["aceleradas"] == []          # n = 0
    assert resolver([4, 3], [2, 3], [3, 2], 0)["ahorro"] == 0   # B = 0
    res = resolver([4, 3], [0, 3], [3, 2], 0)                   # c_i = 0 es gratis
    assert res["aceleradas"] == [1] and res["ahorro"] == 3


@pytest.mark.parametrize("t,c,d,B,mensaje", [
    ([4, 3], [2], [3, 2], 5, "mismo largo"),
    ([4, 3], [2, 3], [3, 2], -1, "presupuesto B"),
    ([4, 3], [2, 3], [3, 2], 2.5, "presupuesto B"),
    ([4, 3], [-2, 3], [3, 2], 5, "c_1"),
    ([4, 3], [2, 3], [3, "2"], 5, "d_2"),
    ([4, -3], [2, 3], [3, 0], 5, "t_2"),
    ([4, 3], [2, 3], [3, 4], 5, "supera la duración"),
    ([4, 3], [2, True], [3, 2], 5, "c_2"),
])
def test_resolver_rechaza_entradas_invalidas(t, c, d, B, mensaje):
    with pytest.raises(ErrorDeEntrada, match=mensaje):
        resolver(t, c, d, B)


def test_tabla_demasiado_grande_da_error_claro_sin_reservar_memoria():
    with pytest.raises(ErrorDeEntrada, match="celdas y el límite es"):
        resolver([5], [1], [3], MAX_CELDAS_TABLA)          # 2 x (10^7 + 1) celdas: falla antes de crear la tabla


def test_el_limite_es_exacto():
    verificar_tamano_tabla(9, 999_999)                      # 10 x 10^6 = 10^7 celdas: cabe
    with pytest.raises(ErrorDeEntrada):
        verificar_tamano_tabla(10, 999_999)                 # 11 x 10^6 > 10^7
