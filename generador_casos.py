#!/usr/bin/env python3
"""Genera casos de prueba PROPIOS mientras llegan los de la profesora.  [Integrante 3]

    python3 generar_casos.py                          # 22 casos en casos/
    python3 generar_casos.py --malla                  # 110 casos: todo n de 10..20 con todo r de 6..15
    python3 generar_casos.py --salida otra/ --semilla 7

Cada caso usa el MISMO formato JSON del ejemplo de la profesora, así que
`run_all.py` le corre las tres partes:

* Parte 1: `parametros.presupuesto_aceleracion_B` y, por etapa, `duracion_normal` (t_i),
  `costo_aceleracion` (c_i) y `reduccion_tiempo_si_acelera` (d_i), con 0 <= d_i <= t_i.
* Parte 2: `categorias_riesgo` (r categorías) y, por etapa, `riesgos_cubiertos_auditoria_completa` (S_j).
* Variante 1: por etapa, `costo_auditoria` (a_j > 0; campo provisional).

Reproducible: misma semilla = mismos casos. Todos los casos son factibles (cada
categoría la cubre al menos una interacción). Los casos van en `casos/`,
NO en `casos/`, que es solo para los de la profesora.

Por defecto se generan 22 casos: para cada n de 10 a 20, dos valores de r que
recorren 6..15 (uno sube y otro baja), y dos densidades distintas, para que haya
instancias donde el voraz es óptimo y otras donde no.
"""

import argparse
import json
import random
from pathlib import Path

NOMBRES_RIESGO = ["sesgo", "privacidad", "formato", "toxicidad", "alucinacion", "seguridad",
                  "derechos_autor", "fuga_datos", "suplantacion", "desinformacion", "discriminacion",
                  "manipulacion", "salud", "legal", "financiero"]


def generar_caso(nombre, n, r, semilla, densidad):
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

    return {
        "nombre": nombre,
        "semilla": semilla,
        "parametros": {"numero_etapas": n, "numero_categorias_riesgo": r, "presupuesto_aceleracion_B": B},
        "categorias_riesgo": [{"id": "R%02d" % k, "categoria": NOMBRES_RIESGO[k - 1], "importancia": rng.randint(1, 5)}
                              for k in range(1, r + 1)],
        "etapas": [{"id": "E%02d" % (i + 1),
                    "duracion_normal": t[i],
                    "costo_aceleracion": c[i],
                    "reduccion_tiempo_si_acelera": d[i],
                    "riesgos_cubiertos_auditoria_completa": ["R%02d" % k for k in sorted(S[i])],
                    "costo_auditoria": a[i]}
                   for i in range(n)],
    }


def combinaciones(malla):
    """(n, r, densidad) de los casos a generar."""
    if malla:
        return [(n, r, 0.25 if (n + r) % 2 else 0.4) for n in range(10, 21) for r in range(6, 16)]
    casos = []
    for k, n in enumerate(range(10, 21)):
        casos.append((n, 6 + k % 10, 0.25))                    # r sube: 6, 7, ..., 15, 6
        casos.append((n, 15 - k % 10, 0.4))                    # r baja: 15, 14, ..., 6, 15
    return casos


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera casos de prueba propios (n = 10..20, r = 6..15).")
    ap.add_argument("--salida", default="casos", help="carpeta de salida (por defecto casos/)")
    ap.add_argument("--semilla", type=int, default=2026, help="semilla base (por defecto 2026)")
    ap.add_argument("--malla", action="store_true", help="generar todas las combinaciones n x r (110 casos)")
    args = ap.parse_args(argv)

    salida = Path(args.salida)
    if salida.resolve().name == "casos":
        raise SystemExit("casos/ es solo para los casos de la profesora; usa otra carpeta.")
    salida.mkdir(parents=True, exist_ok=True)
    for viejo in salida.glob("prueba_n*_r*.json"):             # regenerar completo
        viejo.unlink()

    lista = combinaciones(args.malla)
    for idx, (n, r, densidad) in enumerate(lista):
        nombre = "prueba_n%02d_r%02d_%s" % (n, r, "ralo" if densidad < 0.3 else "denso")
        caso = generar_caso(nombre, n, r, args.semilla + idx, densidad)
        (salida / (nombre + ".json")).write_text(json.dumps(caso, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Generados %d casos en %s/ (semilla %d). Ahora corre:" % (len(lista), salida, args.semilla))
    print("  python3 run_all.py --casos %s/ --salida resultados_prueba/" % salida)


if __name__ == "__main__":
    main()
