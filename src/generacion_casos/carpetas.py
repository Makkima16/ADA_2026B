"""Carpetas temporales: `Casos/casos_temporales/` y `Resultados/resultados_temporales/` en la raíz del proyecto.

Se vacían y se reescriben cada vez, para no acumular información, y están en `.gitignore`.
El borrado es deliberadamente estrecho: solo archivos sueltos con extensión conocida, dentro de
una carpeta que se llame exactamente como una de las dos temporales. Nunca recursivo.
"""

import json
from pathlib import Path
from typing import Dict, List

RAIZ = Path(__file__).resolve().parents[2]
NOMBRE_CASOS = "casos_temporales"
NOMBRE_RESULTADOS = "resultados_temporales"
CASOS_TEMPORALES = RAIZ / "Casos" / NOMBRE_CASOS
RESULTADOS_TEMPORALES = RAIZ / "Resultados" / NOMBRE_RESULTADOS
EXTENSIONES_BORRABLES = (".json", ".txt", ".csv", ".md")


def vaciar(carpeta: Path) -> int:
    """Borra los archivos sueltos (.json, .txt, .csv, .md) de una carpeta temporal. Devuelve cuántos borró.

    Se niega a tocar cualquier carpeta que no se llame `casos_temporales` o `resultados_temporales`.
    """
    carpeta = Path(carpeta)
    if carpeta.name not in (NOMBRE_CASOS, NOMBRE_RESULTADOS) or carpeta.is_symlink():
        raise ValueError("solo se vacían las carpetas %s y %s, no %s" % (NOMBRE_CASOS, NOMBRE_RESULTADOS, carpeta))
    carpeta.mkdir(parents=True, exist_ok=True)
    borrados = 0
    for p in carpeta.iterdir():
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTENSIONES_BORRABLES:
            p.unlink()
            borrados += 1
    return borrados


def escribir_casos(casos: List[Dict], carpeta: Path = CASOS_TEMPORALES) -> List[Path]:
    """Vacía `carpeta` y escribe un .json por caso."""
    vaciar(carpeta)
    rutas = []
    for caso in casos:
        ruta = Path(carpeta) / (caso["nombre"] + ".json")
        ruta.write_text(json.dumps(caso, ensure_ascii=False, indent=1), encoding="utf-8")
        rutas.append(ruta)
    return rutas


def listar_casos(carpeta: Path = CASOS_TEMPORALES) -> List[Dict]:
    """Resumen de los casos que hay ahora en la carpeta (nombre, n, r, B), ordenados por nombre."""
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        return []
    lista = []
    for ruta in sorted(carpeta.glob("*.json")):
        try:
            p = json.loads(ruta.read_text(encoding="utf-8"))["parametros"]
            lista.append({"nombre": ruta.stem, "n": p["numero_etapas"], "r": p["numero_categorias_riesgo"],
                          "B": p["presupuesto_aceleracion_B"]})
        except (ValueError, KeyError, TypeError):
            lista.append({"nombre": ruta.stem, "n": None, "r": None, "B": None})
    return lista


def leer_texto_caso(nombre: str, carpeta: Path = CASOS_TEMPORALES) -> str:
    """Contenido de un caso de la carpeta. Solo acepta nombres que estén en ella (sin rutas)."""
    if nombre not in {c["nombre"] for c in listar_casos(carpeta)}:
        raise FileNotFoundError(nombre)
    return (Path(carpeta) / (nombre + ".json")).read_text(encoding="utf-8")
