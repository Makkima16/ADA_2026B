"""Parte 1: herramientas de verificación (no son parte del algoritmo).

Fuerza bruta para comprobar la DP con n <= 12 y generador de instancias con
semilla fija (mismo código + misma semilla = misma instancia).
"""
import random


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
