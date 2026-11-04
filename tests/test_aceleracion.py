from src.ruta.aceleracion import resolver, fuerza_bruta, generar_instancia


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