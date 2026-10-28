"""Pruebas de la Parte 2: factibilidad, voraz, fuerza bruta y cota H(d)."""

import random

import pytest

from ruta.auditoria import (
    armonico,
    cobertura_final,
    cota_aproximacion,
    cubre_todo,
    fuerza_bruta,
    verificar_factibilidad,
    voraz,
)
from ruta.traza import formatear_traza

# Instancia donde el voraz falla: toma G (4 nuevas) y luego necesita P y Q.
R_MALA = 6
S_MALA = [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}]  # G, P, Q


def test_factibilidad_detecta_categoria_sin_cubrir():
    factible, faltan = verificar_factibilidad(4, [{1, 2}, {2, 3}])
    assert not factible
    assert faltan == {4}


def test_factibilidad_ok():
    assert verificar_factibilidad(3, [{1, 2}, {3}])[0]


def test_voraz_rechaza_instancia_no_factible():
    with pytest.raises(ValueError):
        voraz(4, [{1, 2}, {2, 3}])


def test_voraz_no_es_optimo_en_instancia_clasica():
    J, _ = voraz(R_MALA, S_MALA)
    assert J == [1, 2, 3]            # 3 interacciones
    assert len(fuerza_bruta(R_MALA, S_MALA)) == 2   # el óptimo es {P, Q}


def test_voraz_desempate_menor_indice():
    # Las tres cubren 2 categorías nuevas en el primer paso: gana la j=1.
    J, pasos = voraz(4, [{1, 2}, {3, 4}, {1, 3}])
    assert pasos[0].j == 1
    assert J == [1, 2]


def test_traza_pasos_y_faltan():
    _, pasos = voraz(R_MALA, S_MALA)
    assert pasos[0].nuevas == {1, 2, 4, 5}
    assert pasos[0].faltan == {3, 6}
    assert pasos[-1].faltan == frozenset()


def test_cobertura_final_asigna_una_interaccion_por_categoria():
    J, _ = voraz(R_MALA, S_MALA)
    cob = cobertura_final(S_MALA, J)
    assert set(cob) == set(range(1, R_MALA + 1))
    for c, j in cob.items():
        assert c in S_MALA[j - 1]


def test_fuerza_bruta_rechaza_n_grande():
    with pytest.raises(ValueError):
        fuerza_bruta(1, [{1}] * 13)


def test_armonico():
    assert armonico(1) == 1.0
    assert abs(armonico(3) - (1 + 1 / 2 + 1 / 3)) < 1e-12


def _instancia_aleatoria(rng, n, r):
    """Instancia factible: cada categoría se asigna al menos a una interacción."""
    S = [set() for _ in range(n)]
    for c in range(1, r + 1):
        S[rng.randrange(n)].add(c)
    for s in S:
        for c in range(1, r + 1):
            if rng.random() < 0.3:
                s.add(c)
    return S


def test_voraz_vs_optimo_y_cota_hd_semilla_fija():
    rng = random.Random(2026)  # semilla fija: mismo código, mismos resultados
    for _ in range(200):
        n = rng.randint(1, 10)
        r = rng.randint(1, 10)
        S = _instancia_aleatoria(rng, n, r)
        J, _ = voraz(r, S)
        opt = fuerza_bruta(r, S)
        assert cubre_todo(r, S, J)
        assert len(J) >= len(opt)
        assert len(J) <= cota_aproximacion(S) * len(opt) + 1e-9


def test_formatear_traza_contiene_lo_pedido():
    J, pasos = voraz(R_MALA, S_MALA)
    texto = formatear_traza("caso_demo", pasos, cobertura_final(S_MALA, J), True, 0.0)
    assert "caso_demo" in texto
    assert "Paso 1: interacción 1" in texto
    assert "Cubre todas las categorías: sí" in texto

