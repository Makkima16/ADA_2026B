"""Generador de casos propios con el formato JSON del ejemplo de la profesora.

Cada caso trae las tres partes, así que `run_all.py` puede correrlo completo:

* Parte 1: `parametros.presupuesto_aceleracion_B` y, por etapa, `duracion_normal` (t_i),
  `costo_aceleracion` (c_i) y `reduccion_tiempo_si_acelera` (d_i), con 0 <= d_i <= t_i.
* Parte 2: `categorias_riesgo` (r categorías) y, por etapa, `riesgos_cubiertos_auditoria_completa` (S_j).
* Variante 1: por etapa, `variaciones_auditoria` como en el JSON de la profesora: una variación
  `completa` (cubre S_j y cuesta a_j > 0) y, en cerca de tres de cada cuatro etapas con al menos dos
  riesgos, una `parcial` (cubre un subconjunto de S_j y cuesta menos).

Reproducible: misma semilla y mismos parámetros dan los mismos casos. Todos los casos son
factibles (cada categoría la cubre al menos una interacción).

Este módulo solo genera datos (diccionarios). Escribirlos en disco está en `carpetas.py`.
"""

import random
from typing import Dict, List, Optional, Tuple

NOMBRES_RIESGO = ["sesgo", "privacidad", "formato", "toxicidad", "alucinacion", "seguridad",
                  "derechos_autor", "fuga_datos", "suplantacion", "desinformacion", "discriminacion",
                  "manipulacion", "salud", "legal", "financiero"]

# Densidad = probabilidad de que una interacción cubra una categoría dada.
DENSIDADES = {"ralo": 0.25, "medio": 0.33, "denso": 0.40}

# Topes para que una petición del visor no deje colgado el servidor.
MAX_CASOS = 500
MAX_N = 100
MAX_R = 60


class ErrorDeParametros(ValueError):
    """Los parámetros de generación son inválidos."""


def _nombre_categoria(k: int) -> str:
    return NOMBRES_RIESGO[k - 1] if k <= len(NOMBRES_RIESGO) else "categoria_%d" % k


def generar_caso(nombre: str, n: int, r: int, semilla: int, densidad: float) -> Dict:
    """Un caso factible con n etapas/interacciones y r categorías."""
    rng = random.Random(semilla)

    # Parte 1: etapas de la cadena
    t = [rng.randint(2, 12) for _ in range(n)]
    d = [rng.randint(0, ti) for ti in t]                       # 0 <= d_i <= t_i
    c = [rng.randint(1, 9) for _ in range(n)]
    B = max(1, int(sum(c) * rng.uniform(0.3, 0.5)))            # alcanza para acelerar ~ un tercio

    # Parte 2: qué categorías cubre cada interacción
    S = [{k for k in range(1, r + 1) if rng.random() < densidad} for _ in range(n)]
    for k in range(1, r + 1):                                  # factibilidad garantizada
        if not any(k in s for s in S):
            S[rng.randrange(n)].add(k)
    for s in S:                                                # ninguna interacción vacía
        if not s:
            s.add(rng.randint(1, r))

    # Variante 1: costo de auditar, mayor en promedio si la interacción cubre más
    a = [max(1, len(s) * rng.randint(1, 4) + rng.randint(-2, 3)) for s in S]

    # Variaciones de auditoría: generador aparte, para no cambiar los datos de las Partes 1 y 2 de cada semilla
    rng_v = random.Random(semilla + 7919)
    variaciones = []
    for s, costo in zip(S, a):
        var = [{"id": "completa", "costo": costo, "riesgos_cubiertos": ["R%02d" % k for k in sorted(s)]}]
        if len(s) >= 2 and rng_v.random() < 0.75:
            sub = sorted(rng_v.sample(sorted(s), rng_v.randint(1, len(s) - 1)))
            var.insert(0, {"id": "parcial", "costo": max(1, round(costo * len(sub) / len(s))),
                           "riesgos_cubiertos": ["R%02d" % k for k in sub]})
        variaciones.append(var)

    return {
        "nombre": nombre,
        "semilla": semilla,
        "parametros": {"numero_etapas": n, "numero_categorias_riesgo": r, "presupuesto_aceleracion_B": B},
        "categorias_riesgo": [{"id": "R%02d" % k, "categoria": _nombre_categoria(k), "importancia": rng.randint(1, 5)}
                              for k in range(1, r + 1)],
        "etapas": [{"id": "E%02d" % (i + 1),
                    "duracion_normal": t[i],
                    "costo_aceleracion": c[i],
                    "reduccion_tiempo_si_acelera": d[i],
                    "riesgos_cubiertos_auditoria_completa": ["R%02d" % k for k in sorted(S[i])],
                    "variaciones_auditoria": variaciones[i]}
                   for i in range(n)],
    }


def combinaciones(malla: bool) -> List[Tuple[int, int, float]]:
    """(n, r, densidad) del juego fijo: 22 casos, o 110 con `malla` (todo n de 10..20 con todo r de 6..15)."""
    if malla:
        return [(n, r, 0.25 if (n + r) % 2 else 0.4) for n in range(10, 21) for r in range(6, 16)]
    casos = []
    for k, n in enumerate(range(10, 21)):
        casos.append((n, 6 + k % 10, 0.25))                    # r sube: 6, 7, ..., 15, 6
        casos.append((n, 15 - k % 10, 0.4))                    # r baja: 15, 14, ..., 6, 15
    return casos


def _nombre(prefijo: str, n: int, r: int, densidad: float) -> str:
    etiqueta = "ralo" if densidad < 0.3 else ("medio" if densidad < 0.37 else "denso")
    return "%s_n%02d_r%02d_%s" % (prefijo, n, r, etiqueta)


def generar_juego_fijo(semilla: int = 2026, malla: bool = False) -> List[Dict]:
    """Los 22 casos (o 110 con `malla`) de siempre. Nombres `prueba_nXX_rYY_<densidad>`."""
    return [generar_caso(_nombre("prueba", n, r, dens), n, r, semilla + idx, dens)
            for idx, (n, r, dens) in enumerate(combinaciones(malla))]


def validar_parametros(cantidad: int, n_min: int, n_max: int, r_min: int, r_max: int,
                       densidades: List[str]) -> None:
    if not 1 <= cantidad <= MAX_CASOS:
        raise ErrorDeParametros("la cantidad de casos debe estar entre 1 y %d" % MAX_CASOS)
    if not 1 <= n_min <= n_max <= MAX_N:
        raise ErrorDeParametros("n debe cumplir 1 <= n mínimo <= n máximo <= %d" % MAX_N)
    if not 1 <= r_min <= r_max <= MAX_R:
        raise ErrorDeParametros("r debe cumplir 1 <= r mínimo <= r máximo <= %d" % MAX_R)
    if not densidades or any(d not in DENSIDADES for d in densidades):
        raise ErrorDeParametros("las densidades válidas son: %s" % ", ".join(DENSIDADES))


def generar_lote(cantidad: int = 20, semilla: int = 2026, n_min: int = 8, n_max: int = 16,
                 r_min: int = 6, r_max: int = 15, densidades: Optional[List[str]] = None) -> List[Dict]:
    """`cantidad` casos aleatorios (n, r y densidad sorteados con la semilla). Nombres `aleatorio_NNN_...`."""
    densidades = list(densidades) if densidades else list(DENSIDADES)
    validar_parametros(cantidad, n_min, n_max, r_min, r_max, densidades)
    rng = random.Random(semilla)
    lote = []
    for idx in range(cantidad):
        n = rng.randint(n_min, n_max)
        r = rng.randint(r_min, r_max)
        dens = DENSIDADES[rng.choice(densidades)]
        lote.append(generar_caso(_nombre("aleatorio_%03d" % (idx + 1), n, r, dens), n, r,
                                 semilla * 1000 + idx, dens))
    return lote
