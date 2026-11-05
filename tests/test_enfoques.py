"""Pruebas de los enfoques sobre el voraz (src/auditoria/enfoques/): esenciales, parejas (vista al futuro) y ambas.

El voraz base no se toca; estos enfoques se prueban aparte y se comparan contra él.
"""

import random

import pytest

from auditoria.enfoques.comparacion.experimento import experimento, instancia_aleatoria, instancia_cebos
from auditoria.enfoques.combinado.combinado import PasoCombinado, voraz_combinado
from auditoria.enfoques.comparacion.ablacion import COMBINACIONES, clave, voraz_ablacion, voraz_ablacion_traza
from auditoria.enfoques.esenciales.esenciales import interacciones_esenciales, voraz_esenciales
from auditoria.enfoques.rareza.rareza import PasoRareza, frecuencias, voraz_rareza
from auditoria.enfoques.vision_futuro.vision_futuro import PasoFuturo, voraz_futuro
from auditoria.auditoria import cota_aproximacion, cubre_todo, fuerza_bruta, voraz

R_MALA = 6
S_MALA = [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}]  # G, P, Q: el voraz base usa 3, el óptimo 2


def test_esenciales_en_la_instancia_clasica():
    assert interacciones_esenciales(R_MALA, S_MALA) == [2, 3]      # la 3 solo está en P y la 6 solo en Q
    J, pasos, esenciales = voraz_esenciales(R_MALA, S_MALA)
    assert J == [2, 3] and esenciales == [2, 3]
    assert pasos[-1].faltan == frozenset()


def test_vision_futuro_en_la_instancia_clasica():
    J, _ = voraz_futuro(R_MALA, S_MALA)
    assert sorted(J) == [2, 3]


def test_vision_futuro_prefiere_una_sola_interaccion_si_cubre_lo_mismo():
    # Regresión: una versión previa elegía un par (2 interacciones) donde la 3 sola bastaba.
    J, _ = voraz_futuro(3, [{2, 3}, {1}, {1, 2, 3}])
    assert J == [3]


def test_familia_de_cebos():
    r, S = instancia_cebos(3)                                       # r = 14, óptimo 2
    assert len(voraz(r, S)[0]) == 3
    assert interacciones_esenciales(r, S) == []                     # cada categoría está en un conjunto y en un cebo
    assert len(voraz_esenciales(r, S)[0]) == 3                      # las esenciales no ayudan: no hay
    assert len(voraz_futuro(r, S)[0]) == 2                          # el par (A, B) sí
    assert len(fuerza_bruta(r, S)) == 2


@pytest.mark.parametrize("funcion", [voraz_esenciales, voraz_futuro, voraz_combinado, voraz_rareza])
def test_enfoques_rechazan_instancia_no_factible(funcion):
    with pytest.raises(ValueError):
        funcion(3, [{1}, {2}])


def test_combinado_en_clasica_y_en_cebos():
    J, _, esenciales = voraz_combinado(R_MALA, S_MALA)
    assert J == [2, 3] and esenciales == [2, 3]
    r, S = instancia_cebos(3)                      # sin esenciales: actúa como las parejas
    assert voraz_combinado(r, S)[2] == [] and len(voraz_combinado(r, S)[0]) == 2


def test_combinado_cubre_todo_y_contiene_a_las_esenciales():
    rng = random.Random(2026)
    for _ in range(200):
        n, r = rng.randint(1, 10), rng.randint(1, 10)
        rr, S = instancia_aleatoria(rng, n, r, rng.choice([0.1, 0.3, 0.5]))
        J, _, esenciales = voraz_combinado(rr, S)
        assert cubre_todo(rr, S, J) and set(esenciales) <= set(J)
        assert len(J) >= len(fuerza_bruta(rr, S))


def test_enfoques_cubren_todo_y_esenciales_conservan_la_cota():
    rng = random.Random(2026)
    for _ in range(300):
        n, r = rng.randint(1, 10), rng.randint(1, 10)
        rr, S = instancia_aleatoria(rng, n, r, rng.choice([0.1, 0.3, 0.5]))
        opt = len(fuerza_bruta(rr, S))
        Je, _, esenciales = voraz_esenciales(rr, S)
        Jf, _ = voraz_futuro(rr, S)
        assert cubre_todo(rr, S, Je) and cubre_todo(rr, S, Jf)
        assert set(esenciales) <= set(Je) and len(set(Je)) == len(Je)
        assert opt <= len(Je) <= cota_aproximacion(S) * opt + 1e-9   # la garantía H(d) del enfoque A
        assert len(Jf) >= opt                                        # ninguno baja del óptimo


def test_experimento_es_reproducible():
    a = experimento("medio", 40, 7)
    b = experimento("medio", 40, 7)
    for m in a["metodos"]:
        a["metodos"][m].pop("tiempo_s"), b["metodos"][m].pop("tiempo_s")   # el tiempo depende de la máquina
    assert a == b


def test_paso_futuro_guarda_la_pareja_ganadora():
    _, pasos = voraz_futuro(R_MALA, S_MALA)
    assert isinstance(pasos[0], PasoFuturo)
    assert pasos[0].par == (2, 3) and pasos[0].cobertura_par == 6     # el par (P, Q) cubre las 6 categorías
    assert pasos[0].j == 2                                           # y se compromete la que más cubre sola


def test_rareza_frecuencias_y_puntaje():
    assert frecuencias(R_MALA, S_MALA)[1:] == [2, 2, 1, 2, 2, 1]        # las categorías 3 y 6 son raras (f = 1)
    J, pasos = voraz_rareza(R_MALA, S_MALA)
    assert isinstance(pasos[0], PasoRareza) and len(pasos[0].puntajes) == len(S_MALA)
    assert pasos[0].puntajes == (2.0, 2.0, 2.0)                           # empate: gana la que cubre más nuevas (la 1)
    assert cubre_todo(R_MALA, S_MALA, J)


def test_rareza_no_resuelve_cebos_porque_todas_valen_lo_mismo():
    r, S = instancia_cebos(3)                                             # toda categoría tiene f = 2
    assert len(voraz_rareza(r, S)[0]) == len(voraz(r, S)[0]) == 3


def test_rareza_cubre_todo_con_semilla_fija():
    rng = random.Random(2026)
    for _ in range(300):
        n, r = rng.randint(1, 10), rng.randint(1, 10)
        rr, S = instancia_aleatoria(rng, n, r, rng.choice([0.1, 0.3, 0.5]))
        J, _ = voraz_rareza(rr, S)
        assert cubre_todo(rr, S, J) and len(set(J)) == len(J)
        assert len(J) >= len(fuerza_bruta(rr, S))


def test_combinado_guarda_el_par_y_los_puntajes():
    _, pasos, esenciales = voraz_combinado(R_MALA, S_MALA)
    assert esenciales == [2, 3] and len(pasos) == 2                  # las dos esenciales cubren todo: no hay pasos de parejas
    r, S = instancia_cebos(3)
    _, pasos, _ = voraz_combinado(r, S)
    assert isinstance(pasos[0], PasoCombinado) and pasos[0].par == (1, 2) and pasos[0].cobertura_par == 14
    assert len(pasos[0].puntajes) == len(S)


def test_ablacion_coincide_con_cada_enfoque():
    rng = random.Random(2026)
    for _ in range(120):
        n, r = rng.randint(1, 9), rng.randint(1, 9)
        rr, S = instancia_aleatoria(rng, n, r, rng.choice([0.1, 0.3, 0.5]))
        por_nombre = {nombre: (e, ra, pa) for nombre, e, ra, pa in COMBINACIONES}
        assert voraz_ablacion(rr, S, *por_nombre["Voraz base"]) == voraz(rr, S)[0]
        assert voraz_ablacion(rr, S, *por_nombre["Esenciales"]) == voraz_esenciales(rr, S)[0]
        assert voraz_ablacion(rr, S, *por_nombre["Rareza"]) == voraz_rareza(rr, S)[0]
        assert voraz_ablacion(rr, S, *por_nombre["Parejas"]) == voraz_futuro(rr, S)[0]
        assert voraz_ablacion(rr, S, *por_nombre["Los tres (enfoque D)"]) == voraz_combinado(rr, S)[0]


def test_ablacion_traza_coincide_con_el_combinado_y_las_claves():
    J, pasos, ese = voraz_ablacion_traza(R_MALA, S_MALA, True, True, True)
    J2, pasos2, ese2 = voraz_combinado(R_MALA, S_MALA)
    assert J == J2 and ese == ese2 == [2, 3]
    assert [(p.j, p.nuevas) for p in pasos] == [(p.j, p.nuevas) for p in pasos2]
    assert voraz_ablacion_traza(R_MALA, S_MALA, False, False, False)[2] is None      # sin esenciales encendidas
    assert [clave(e, r, p) for _, e, r, p in COMBINACIONES] == ["", "e", "r", "p", "er", "ep", "rp", "erp"]
