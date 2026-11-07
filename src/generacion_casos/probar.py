"""Prueba los casos de `pruebas/casos_temporales/` llamando a `run_all.py` (no reimplementa nada).

`run_all.py` es del integrante 3 y es el único que corre las tres partes; aquí solo se le pasa la
carpeta de casos y la de resultados temporales. Después se leen sus archivos (`resumen.csv`,
`comparacion.md` y las trazas) para mostrarlos.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from generacion_casos.carpetas import (CASOS_TEMPORALES, RAIZ, RESULTADOS_TEMPORALES, listar_casos, vaciar)

TIEMPO_MAXIMO_S = 300


def probar(casos: Path = CASOS_TEMPORALES, salida: Path = RESULTADOS_TEMPORALES) -> subprocess.CompletedProcess:
    """Vacía `salida` y corre `run_all.py` sobre `casos`. No lanza error si algún caso falla (queda en su evidencia)."""
    if not listar_casos(casos):
        raise ValueError("no hay casos que probar en %s; genera primero" % casos)
    vaciar(salida)
    return subprocess.run([sys.executable, str(RAIZ / "run_all.py"), "--casos", str(casos), "--salida", str(salida),
                           "--sin-tabla"], cwd=str(RAIZ), capture_output=True, text=True, timeout=TIEMPO_MAXIMO_S)


def leer_resumen(salida: Path = RESULTADOS_TEMPORALES) -> List[Dict[str, str]]:
    """Filas de `resumen.csv` (caso, parte, resultado, tiempo_s, traza). Lista vacía si aún no se probó."""
    ruta = Path(salida) / "resumen.csv"
    if not ruta.is_file():
        return []
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def leer_comparacion(salida: Path = RESULTADOS_TEMPORALES) -> str:
    ruta = Path(salida) / "comparacion.md"
    return ruta.read_text(encoding="utf-8") if ruta.is_file() else ""


def leer_traza(archivo: str, salida: Path = RESULTADOS_TEMPORALES) -> str:
    """Texto de una traza. Solo acepta nombres que aparezcan en `resumen.csv` (sin rutas)."""
    if not archivo or archivo not in {fila["traza"] for fila in leer_resumen(salida)}:      # las filas «no aplica» tienen la traza vacía
        raise FileNotFoundError(archivo)
    return (Path(salida) / archivo).read_text(encoding="utf-8")


def leer_resumen_enfoques(salida: Path = RESULTADOS_TEMPORALES) -> dict:
    """`resumen_enfoques.json` de la última prueba (los resúmenes por parte que arma run_all.py). {} si aún no se probó."""
    ruta = Path(salida) / "resumen_enfoques.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}
