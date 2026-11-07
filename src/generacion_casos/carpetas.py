"""Carpetas temporales: `pruebas/casos_temporales/` y `pruebas/resultados_temporales/` en la raíz del proyecto.

Se vacían y se reescriben cada vez, para no acumular información, y están en `.gitignore`.
El borrado es deliberadamente estrecho: solo archivos sueltos con extensión conocida, dentro de
una carpeta que se llame exactamente como una de las dos temporales. Nunca recursivo.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

RAIZ = Path(__file__).resolve().parents[2]
NOMBRE_CASOS = "casos_temporales"
NOMBRE_RESULTADOS = "resultados_temporales"
CASOS_TEMPORALES = RAIZ / "pruebas" / NOMBRE_CASOS
RESULTADOS_TEMPORALES = RAIZ / "pruebas" / NOMBRE_RESULTADOS
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


MAX_ARCHIVOS_SUBIDOS = 200


class ErrorDeArchivos(ValueError):
    """Los archivos que se quieren subir no sirven (vacíos, demasiados o JSON mal formado)."""


def nombre_seguro(nombre: str) -> str:
    """Nombre de caso saneado: sin carpetas, sin extensión y solo con letras, dígitos, '_', '-' y '.'."""
    base = Path(str(nombre).replace("\\", "/")).name
    if base.lower().endswith(".json"):
        base = base[:-5]
    return re.sub(r"[^A-Za-z0-9_.-]", "_", base).strip(".")[:80] or "caso"


def escribir_archivos(archivos: List[Tuple[str, str]], carpeta: Path = CASOS_TEMPORALES) -> List[str]:
    """Vacía `carpeta` y guarda los .json subidos (pares nombre, texto). Devuelve los nombres guardados.

    Antes de borrar nada comprueba que haya entre 1 y 200 archivos y que cada uno sea un objeto JSON válido;
    así un archivo malo no deja la carpeta vacía. Los nombres repetidos se numeran.
    """
    if not 1 <= len(archivos) <= MAX_ARCHIVOS_SUBIDOS:
        raise ErrorDeArchivos("hay que subir entre 1 y %d archivos .json" % MAX_ARCHIVOS_SUBIDOS)
    nombres, usados = [], set()
    for nombre, texto in archivos:
        try:
            if not isinstance(json.loads(texto), dict):
                raise ValueError("no es un objeto JSON")
        except ValueError as e:
            raise ErrorDeArchivos("%s no es un JSON válido (%s)" % (nombre, e))
        base = nombre_seguro(nombre)
        final, k = base, 2
        while final in usados:
            final, k = "%s_%d" % (base, k), k + 1
        usados.add(final)
        nombres.append(final)
    vaciar(carpeta)
    for nombre, (_, texto) in zip(nombres, archivos):
        (Path(carpeta) / (nombre + ".json")).write_text(texto, encoding="utf-8")
    return nombres


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
