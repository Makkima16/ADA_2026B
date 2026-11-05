"""Verifica la DP de la Parte 1 contra métodos distintos del suyo (no contra su propia fuerza bruta).

* `mochila_1d`: la mochila clásica con un solo arreglo.
* `mitad_y_mitad`: enumera cada mitad de las etapas y las combina (sirve hasta n ~ 24).
Con semillas fijas: mismo código = mismos resultados.
"""

import bisect
import random

from aceleracion.aceleracion import resolver
from aceleracion.verificacion import fuerza_bruta


def mochila_1d(c, d, B):
    mejor = [0] * (B + 1)
    for ci, di in zip(c, d):
        for b in range(B, ci - 1, -1):
            mejor[b] = max(mejor[b], mejor[b - ci] + di)
    return mejor[B]


def mitad_y_mitad(c, d, B):
    h = len(c) // 2

    def subconjuntos(indices):
        salida = [(0, 0)]
        for i in indices:
            salida += [(costo + c[i], valor + d[i]) for costo, valor in salida]
        return salida

    izq, der = subconjuntos(range(h)), subconjuntos(range(h, len(c)))
    der.sort()
    costos, mejores, m = [x[0] for x in der], [], 0
    for _, valor in der:
        m = max(m, valor)
        mejores.append(m)
    res = 0
    for costo, valor in izq:
        if costo <= B:
            k = bisect.bisect_right(costos, B - costo) - 1
            res = max(res, valor + (mejores[k] if k >= 0 else 0))
    return res


def _solucion_coherente(t, c, d, B, r):
    A = r["aceleradas"]
    return (len(set(A)) == len(A) and A == sorted(A) and all(1 <= i <= len(c) for i in A)
            and sum(c[i - 1] for i in A) == r["costo"] <= B
            and sum(d[i - 1] for i in A) == r["ahorro"]
            and r["duracion_final"] == sum(t) - r["ahorro"])


def test_dp_contra_mochila_1d_con_casos_extremos():
    for semilla in range(400):
        rng = random.Random(semilla)
        n, tope_c = rng.randint(0, 60), rng.choice([1, 3, 10, 50])
        t = [rng.randint(0, 40) for _ in range(n)]
        c = [rng.randint(0, tope_c) for _ in range(n)]            # incluye c_i = 0
        d = [rng.choice([0, x, rng.randint(0, x)]) for x in t]    # incluye d_i = 0 y d_i = t_i
        B = rng.choice([0, 1, rng.randint(0, 200), sum(c), sum(c) + 5])
        r = resolver(t, c, d, B)
        assert r["ahorro"] == mochila_1d(c, d, B), (semilla, t, c, d, B)
        assert _solucion_coherente(t, c, d, B, r), (semilla, t, c, d, B)


def test_dp_contra_mitad_y_mitad_con_n_hasta_20():
    for semilla in range(60):
        rng = random.Random(1000 + semilla)
        n = rng.randint(14, 20)
        c = [rng.randint(1, 15) for _ in range(n)]
        d = [rng.randint(1, 30) for _ in range(n)]
        B = rng.randint(1, sum(c))
        r = resolver(d, c, d, B)       # instancia de la reducción desde Mochila: t_i = d_i = v_i, c_i = w_i, B = W
        assert r["ahorro"] == mitad_y_mitad(c, d, B)
        assert r["duracion_final"] == sum(d) - r["ahorro"]


def test_fuerza_bruta_del_repo_coincide_con_la_mochila_1d():
    for semilla in range(100):
        rng = random.Random(semilla)
        n = rng.randint(1, 12)
        t = [rng.randint(1, 20) for _ in range(n)]
        c = [rng.randint(0, 10) for _ in range(n)]
        d = [rng.randint(0, x) for x in t]
        B = rng.randint(0, sum(c))
        assert fuerza_bruta(t, c, d, B)["ahorro"] == mochila_1d(c, d, B)


def test_invariante_de_llenar_tabla_cada_fila_es_correcta():
    """Invariante del ciclo externo: tras la iteración i, la fila i es el óptimo de las primeras i etapas."""
    from aceleracion.aceleracion import llenar_tabla
    for semilla in range(80):
        rng = random.Random(2000 + semilla)
        n = rng.randint(0, 12)
        c = [rng.randint(0, 9) for _ in range(n)]
        d = [rng.randint(0, 20) for _ in range(n)]
        B = rng.randint(0, 30)
        DP = llenar_tabla(c, d, B)
        for i in range(n + 1):
            for b in range(B + 1):
                assert DP[i][b] == mochila_1d(c[:i], d[:i], b), (semilla, i, b)


def test_invariante_de_reconstruir_en_cada_paso():
    """Invariante: ahorro de lo elegido + DP[i][b] = DP[n][B], y el presupuesto restante nunca es negativo."""
    from aceleracion.aceleracion import llenar_tabla, reconstruir
    for semilla in range(80):
        rng = random.Random(3000 + semilla)
        n = rng.randint(0, 12)
        c = [rng.randint(0, 9) for _ in range(n)]
        d = [rng.randint(0, 20) for _ in range(n)]
        B = rng.randint(0, 30)
        DP = llenar_tabla(c, d, B)
        b, elegido = B, 0
        for i in range(n, 0, -1):
            assert elegido + DP[i][b] == DP[n][B] and b >= 0         # el invariante, antes de procesar la etapa i
            if DP[i][b] != DP[i - 1][b]:
                elegido += d[i - 1]
                b -= c[i - 1]
        assert elegido + DP[0][b] == DP[n][B] and b >= 0              # finalización: i = 0
        assert sum(d[i - 1] for i in reconstruir(DP, c, B)) == DP[n][B]
