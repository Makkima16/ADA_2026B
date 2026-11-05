"""Parte 1: aceleración de la cadena bajo presupuesto (Mochila 0/1).

Problema: n etapas en serie con duración t_i, costo de aceleración c_i y
reducción d_i. Con presupuesto B se elige un subconjunto A a acelerar
para minimizar la duración total D(A) = sum(t) - sum(d_i, i en A).
Eso equivale a maximizar el ahorro sum(d_i) con sum(c_i) <= B.

Eficiencia: T(n, B) = O(n * B) en tiempo y espacio (pseudo-polinomial).
"""
import random


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


def imprimir_resultado(res):
    print("Etapas aceleradas:", res["aceleradas"])
    print("Costo usado:", res["costo"])
    print("Ahorro:", res["ahorro"])
    print("Duración final:", res["duracion_final"])


def fuerza_bruta(t, c, d, B):
    """Prueba los 2^n subconjuntos. Solo para comprobar la DP (n <= 12)."""
    n = len(c)
    if n > 12:
        raise ValueError("La fuerza bruta solo se usa con n <= 12")
    mejor_ahorro = 0
    for mascara in range(1 << n):
        costo = ahorro = 0
        for i in range(n):
            if mascara >> i & 1:
                costo += c[i]
                ahorro += d[i]
        if costo <= B and ahorro > mejor_ahorro:
            mejor_ahorro = ahorro
    return {"ahorro": mejor_ahorro, "duracion_final": sum(t) - mejor_ahorro}


def generar_instancia(n, semilla=42, max_t=20, max_c=10):
    """Instancia aleatoria reproducible: con la misma semilla sale siempre igual."""
    rng = random.Random(semilla)
    t = [rng.randint(1, max_t) for _ in range(n)]
    c = [rng.randint(1, max_c) for _ in range(n)]
    d = [rng.randint(0, ti) for ti in t]      # cumple 0 <= d_i <= t_i
    B = sum(c) // 2                           # presupuesto: la mitad del costo total
    return t, c, d, B


if __name__ == "__main__":
    # Ejemplo de 4 etapas y B = 5 (el mismo del ejemplo a mano)
    t = [4, 3, 5, 2]
    c = [2, 3, 4, 1]
    d = [3, 2, 4, 1]
    B = 5

    res = resolver(t, c, d, B)
    print("Tabla DP:")
    for fila in res["tabla"]:
        print(fila)
    imprimir_resultado(res)