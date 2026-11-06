#!/usr/bin/env python3
"""Convierte los casos propios de la Parte 2 de `.txt` a `.json` (formato del ejemplo de la profesora).

Lee `txt_originales/*.txt` con el lector del proyecto y escribe un `.json` por caso en esta carpeta:
`categorias_riesgo` (R01..Rr), `etapas` (E01..En, cada una con `riesgos_cubiertos_auditoria_completa`) y
`descripcion` (los comentarios del `.txt`; el lector la ignora). Los ids siguen el orden de la numeración
1..r y 1..n del `.txt`, así que la instancia leída es idéntica a la original.

Uso (desde la raíz del proyecto):

    python3 Casos/casos_propios/voraz/convertir_a_json.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from auditoria.lectura import leer_instancia  # noqa: E402

CARPETA = Path(__file__).resolve().parent


def _comentarios(ruta: Path) -> str:
    lineas = [l.strip().lstrip("#").strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip().startswith("#")]
    return " ".join(l for l in lineas if l)


def _texto_json(descripcion, r, S):
    n = len(S)
    L = ["{", '  "descripcion": %s,' % json.dumps(descripcion, ensure_ascii=False),
         '  "parametros": {"numero_etapas": %d, "numero_categorias_riesgo": %d},' % (n, r),
         '  "categorias_riesgo": [']
    for c in range(1, r + 1):
        L.append('    {"id": "R%02d", "categoria": "Riesgo %d"}%s' % (c, c, "," if c < r else ""))
    L += ["  ],", '  "etapas": [']
    for j, s in enumerate(S, start=1):
        riesgos = ", ".join('"R%02d"' % c for c in sorted(s))
        L.append('    {"id": "E%02d", "riesgos_cubiertos_auditoria_completa": [%s]}%s' % (j, riesgos, "," if j < n else ""))
    L += ["  ]", "}"]
    return "\n".join(L) + "\n"


def convertir(origen: Path = CARPETA / "txt_originales", salida: Path = CARPETA) -> list:
    nombres = []
    for txt in sorted(origen.glob("*.txt")):
        inst = leer_instancia(txt)
        (salida / (txt.stem + ".json")).write_text(
            _texto_json(_comentarios(txt), inst.r, inst.S), encoding="utf-8")
        nombres.append(txt.stem)
    return nombres


if __name__ == "__main__":
    hechos = convertir()
    print("Convertí %d casos a .json en %s" % (len(hechos), CARPETA))
