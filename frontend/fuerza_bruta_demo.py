#!/usr/bin/env python3
"""Demostración de la fuerza bruta (Parte 2, auditoría) para la sustentación.

Material de apoyo local, en `frontend/` (no es parte de la entrega). No
reimplementa el algoritmo: llama a `fuerza_bruta` de `src/auditoria/auditoria.py`
y solo agrega el recuento de cuántos subconjuntos se revisaron.

Uso como comando (desde la raíz del proyecto):

    python3 frontend/fuerza_bruta_demo.py CASO [CASO ...]

CASO es un archivo `.json` o `.txt` (el mismo formato que lee el proyecto).
Solo funciona con n <= 12 interacciones; con más, avisa y no ejecuta.

El mismo módulo lo usa `servidor.py` para mostrar el resultado en la página.
"""

import sys
import time
from itertools import combinations
from math import comb
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from auditoria.auditoria import N_MAX_FUERZA_BRUTA, cubre_todo, fuerza_bruta, voraz  # noqa: E402
from auditoria.lectura import ErrorDeLectura, leer_instancia                         # noqa: E402
from auditoria.resolver import Instancia                                              # noqa: E402


def analizar(inst: Instancia) -> dict:
    """Corre la fuerza bruta sobre una instancia y cuenta lo que revisó.

    Devuelve un diccionario con:
      aplica     False si n > 12 (no se ejecuta) o la instancia no es factible.
      motivo     texto explicando por qué no aplica (si aplica es False).
      optimo     el mínimo real (lista de interacciones) si aplica.
      revisados  cuántos subconjuntos se probaron hasta hallarlo.
      total      2^n, todos los subconjuntos posibles.
      tiempo_s   segundos que tardó `fuerza_bruta` (time.perf_counter()).
      tamanos    por cada tamaño k probado: k, cuántos subconjuntos hay (C(n, k)),
                 cuántos se probaron y si ahí se encontró el mínimo.
    """
    n = len(inst.S)
    if n > N_MAX_FUERZA_BRUTA:
        return {"aplica": False,
                "motivo": "la fuerza bruta solo se usa con %d interacciones o menos (este caso tiene %d)"
                          % (N_MAX_FUERZA_BRUTA, n)}
    try:
        t0 = time.perf_counter()
        optimo = fuerza_bruta(inst.r, inst.S)          # el algoritmo del proyecto, sin tocarlo
        tiempo = time.perf_counter() - t0
    except ValueError as e:                            # instancia no factible
        return {"aplica": False, "motivo": str(e)}

    # Recuento: fuerza_bruta prueba por tamaño k = 0, 1, 2, ... y, dentro de cada
    # tamaño, en el orden de itertools.combinations. Se repite ese orden solo para
    # contar cuántos subconjuntos se probaron antes de dar con el mínimo.
    k_opt = len(optimo)
    tamanos = []
    revisados = 0
    for k in range(0, k_opt):
        tamanos.append({"k": k, "subconjuntos": comb(n, k), "probados": comb(n, k), "encontrado": False})
        revisados += comb(n, k)
    probados = 0
    for J in combinations(range(1, n + 1), k_opt):
        probados += 1
        if cubre_todo(inst.r, inst.S, J):
            break
    tamanos.append({"k": k_opt, "subconjuntos": comb(n, k_opt), "probados": probados, "encontrado": True})
    revisados += probados
    return {"aplica": True, "optimo": list(optimo), "revisados": revisados, "total": 2 ** n,
            "tiempo_s": tiempo, "tamanos": tamanos}


def _nombre_j(inst: Instancia, j: int) -> str:
    return inst.etiqueta_interaccion(j)


def informe(inst: Instancia) -> str:
    """Texto de la demostración para un caso (lo imprime el comando)."""
    n = len(inst.S)
    lineas = ["Caso: %s   (n = %d interacciones, r = %d categorías)" % (inst.nombre, n, inst.r)]
    fb = analizar(inst)
    if not fb["aplica"]:
        lineas.append("  No se ejecuta la fuerza bruta: %s." % fb["motivo"])
        return "\n".join(lineas) + "\n"

    lineas.append("Fuerza bruta: prueba los subconjuntos de interacciones por tamaño creciente.")
    for t in fb["tamanos"]:
        if t["encontrado"]:
            lineas.append("  Tamaño %2d: %s de %d subconjuntos probados -> ¡este es el mínimo!"
                          % (t["k"], t["probados"], t["subconjuntos"]))
        else:
            lineas.append("  Tamaño %2d: %d de %d subconjuntos probados -> ninguno cubre todo"
                          % (t["k"], t["probados"], t["subconjuntos"]))
    opt = fb["optimo"]
    lineas.append("Mínimo real: %d interacciones: %s" % (len(opt), ", ".join(_nombre_j(inst, j) for j in opt)))
    lineas.append("Subconjuntos revisados: %d de %d posibles (2^%d)" % (fb["revisados"], fb["total"], n))
    lineas.append("Tiempo de la fuerza bruta: %.6f s" % fb["tiempo_s"])

    J, _ = voraz(inst.r, inst.S)
    lineas.append("Voraz (para comparar): %d interacciones: %s"
                  % (len(J), ", ".join(_nombre_j(inst, j) for j in J)))
    razon = len(J) / max(len(opt), 1)
    lineas.append("Razón voraz / mínimo: %.4f  (%s)"
                  % (razon, "el voraz acertó" if len(J) == len(opt) else "el voraz NO es óptimo aquí"))
    return "\n".join(lineas) + "\n"


def main(argv=None) -> int:
    argumentos = list(sys.argv[1:] if argv is None else argv)
    if not argumentos or argumentos[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argumentos else 1
    codigo = 0
    for ruta in argumentos:
        try:
            print(informe(leer_instancia(ruta)))
        except (ErrorDeLectura, OSError) as e:
            print("Error con %s: %s\n" % (ruta, e))
            codigo = 1
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
