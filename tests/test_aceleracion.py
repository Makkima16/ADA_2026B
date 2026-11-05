from aceleracion.aceleracion import resolver
from aceleracion.verificacion import fuerza_bruta, generar_instancia
from aceleracion.traza import formatear_resultado


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


def test_traza_del_ejemplo():
    t, c, d, B = [4, 3, 5, 2], [2, 3, 4, 1], [3, 2, 4, 1], 5
    texto = formatear_resultado(resolver(t, c, d, B), t, c, d, B)
    assert "Etapas aceleradas: [1, 2]" in texto
    assert "Duración final: 9 (original 14)" in texto
