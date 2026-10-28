"""Pruebas del enfoque exploratorio de interacciones esenciales (ver src/enfoques/esenciales/README.md)."""

import random

import pytest

from enfoques.esenciales.esenciales import interacciones_esenciales, voraz_esenciales
from ruta.auditoria import cota_aproximacion, cubre_todo, fuerza_bruta, voraz

# Instancia clásica: G = {1,2,4,5}, P = {1,2,3}, Q = {4,5,6}
R_MALA = 6
S_MALA = [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}]


def _instancia_aleatoria(rng, n, r):
    S = [set() for _ in range(n)]
    for c in range(1, r + 1):
        S[rng.randrange(n)].add(c)
    for s in S:
        for c in range(1, r + 1):
            if rng.random() < 0.3:
                s.add(c)
    return S


def _sin_categorias_unicas():
    """Dos conjuntos óptimos A, B y tres cebos (8, 4 y 2 categorías).

    Ninguna categoría es única (cada una está en A o B y en un cebo), así que
    la regla de esenciales no hace nada y el resultado es igual al del voraz.
    """
    a = list(range(1, 8))
    b = list(range(8, 15))
    cebo1 = set(a[:4]) | set(b[:4])
    cebo2 = set(a[4:6]) | set(b[4:6])
    cebo3 = {a[6], b[6]}
    return 14, [cebo1, cebo2, cebo3, set(a), set(b)]


def test_esenciales_en_instancia_clasica():
    assert interacciones_esenciales(R_MALA, S_MALA) == [2, 3]  # P y Q
    J, pasos = voraz_esenciales(R_MALA, S_MALA)
    assert J == [2, 3]                      # el óptimo
    assert all(p.motivo == "esencial" for p in pasos)


def test_esenciales_no_arregla_si_no_hay_categorias_unicas():
    r, S = _sin_categorias_unicas()
    assert interacciones_esenciales(r, S) == []
    assert voraz_esenciales(r, S)[0] == voraz(r, S)[0] == [1, 2, 3]
    assert len(fuerza_bruta(r, S)) == 2     # el óptimo sigue siendo 2


def test_esenciales_rechaza_instancia_no_factible():
    with pytest.raises(ValueError):
        voraz_esenciales(4, [{1, 2}, {2, 3}])


def test_esenciales_cubre_incluye_esenciales_y_cumple_cota():
    rng = random.Random(2026)
    for _ in range(200):
        n = rng.randint(1, 10)
        r = rng.randint(1, 10)
        S = _instancia_aleatoria(rng, n, r)
        J, _ = voraz_esenciales(r, S)
        opt = fuerza_bruta(r, S)
        assert cubre_todo(r, S, J)
        assert set(interacciones_esenciales(r, S)) <= set(J)
        assert len(J) <= cota_aproximacion(S) * len(opt) + 1e-9
