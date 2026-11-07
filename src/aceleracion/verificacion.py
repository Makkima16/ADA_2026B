"""Parte 1: herramientas de verificación (no son parte del algoritmo).

Fuerza bruta para comprobar la DP con n <= 12 y generador de instancias con
semilla fija (mismo código + misma semilla = misma instancia).
"""
import random

N_MAX_FUERZA_BRUTA = 12      # la fuerza bruta es O(2^n * n): solo para verificar


def fuerza_bruta(t, c, d, B):
    """Prueba los 2^n subconjuntos. Solo para comprobar la DP (n <= 12)."""
    n = len(c)
    if n > N_MAX_FUERZA_BRUTA:
        raise ValueError("La fuerza bruta solo se usa con n <= %d" % N_MAX_FUERZA_BRUTA)
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
    d = [rng.randint(0, ti) for ti in t]  # cumple 0 <= d_i <= t_i
    B = sum(c) // 2  # presupuesto: la mitad del costo total
    return t, c, d, B


# =============================================================================
# INVARIANTES DE CICLO (inicialización / mantenimiento / finalización)
#
# fuerza_bruta, ciclo interno `for i`:
#   Invariante: antes de la vuelta i, `costo` y `ahorro` suman c_j y d_j de las etapas j < i
#   con bit en 1 en la máscara.
#   - Inicio: ambos valen 0 (suma vacía). - Mantenimiento: si el bit i está en 1 se suman
#   c[i] y d[i]; si no, nada. - Fin: son el costo y el ahorro exactos del subconjunto.
#
# fuerza_bruta, ciclo externo `for mascara`:
#   Invariante: `mejor_ahorro` es el máximo ahorro entre los subconjuntos factibles de las
#   máscaras 0..m-1.
#   - Inicio: vale 0, correcto porque el subconjunto vacío siempre es factible.
#   - Mantenimiento: la máscara m aporta su costo y ahorro exactos; si es factible y mejora,
#   se actualiza. - Fin: se revisaron los 2^n subconjuntos: es el óptimo exacto.
# =============================================================================
