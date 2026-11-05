"""Parte 1: aceleración de la cadena bajo presupuesto (Mochila 0/1).

Problema: n etapas en serie con duración t_i, costo de aceleración c_i y
reducción d_i. Con presupuesto B se elige un subconjunto A a acelerar
para minimizar la duración total D(A) = sum(t) - sum(d_i, i en A).
Eso equivale a maximizar el ahorro sum(d_i) con sum(c_i) <= B.

Eficiencia: T(n, B) = O(n * B) en tiempo y espacio (pseudo-polinomial).
"""


def llenar_tabla(c, d, B):
    """DP[i][b] = mayor ahorro usando solo las primeras i etapas y gastando a lo sumo b."""
    n = len(c)
    DP = [[0] * (B + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for b in range(B + 1):
            DP[i][b] = DP[i - 1][b]                       # no acelerar la etapa i
            if c[i - 1] <= b:                             # acelerarla, si cabe
                DP[i][b] = max(DP[i][b], DP[i - 1][b - c[i - 1]] + d[i - 1])
    return DP


def reconstruir(DP, c, B):
    """Recorre la tabla desde DP[n][B]; si el valor cambia, esa etapa se aceleró."""
    aceleradas = []
    b = B
    for i in range(len(c), 0, -1):
        if DP[i][b] != DP[i - 1][b]:
            aceleradas.append(i)
            b -= c[i - 1]
    aceleradas.reverse()
    return aceleradas


def resolver(t, c, d, B):
    """Resuelve la instancia de forma exacta con programación dinámica."""
    DP = llenar_tabla(c, d, B)
    A = reconstruir(DP, c, B)
    ahorro = DP[len(c)][B]
    return {
        "aceleradas": A,
        "costo": sum(c[i - 1] for i in A),
        "ahorro": ahorro,
        "duracion_final": sum(t) - ahorro,
        "tabla": DP,
    }
