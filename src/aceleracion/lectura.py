"""Lectura de casos de la Parte 1 (aceleración de la cadena).

Formato JSON (ejemplo ``entrada_G3_mochila_20_nodos.json``)
-----------------------------------------------------------
Un solo archivo trae las dos partes del proyecto; la Parte 1 solo usa:

* ``parametros.presupuesto_aceleracion_B``: el presupuesto B (entero >= 0).
* ``etapas``: lista de objetos, en el orden de la cadena, con
  ``id``, ``duracion_normal`` (t_i), ``costo_aceleracion`` (c_i) y
  ``reduccion_tiempo_si_acelera`` (d_i).
* ``parametros.numero_etapas`` (si está) se comprueba contra la lista.

Lo demás (categorías de riesgo, riesgos cubiertos, variaciones de auditoría,
flujo, presupuesto conjunto) es de la Parte 2 o de variantes y se ignora. En
particular ``flujo`` solo importa en la variante de etapas en paralelo, que
está fuera de esta entrega: aquí la cadena es la lista ``etapas`` en orden.

Se valida: enteros no negativos, 0 <= d_i <= t_i, ids repetidos y coherencia
con ``parametros``. El nombre del caso es el nombre del archivo sin extensión.

Si el formato real de la profesora cambia, se adapta ÚNICAMENTE este módulo
(skill adaptar-lectura-casos); el algoritmo no se toca.

Costo de la lectura: T(n) = O(n): se recorren las n etapas una sola vez.

Variables: n = etapas del caso, L = caracteres del archivo.
"""

import json
from pathlib import Path
from typing import List, Union

from .resolver import InstanciaAceleracion


class ErrorDeLectura(ValueError):
    """Error de formato con el nombre del caso y la etapa donde se rompió."""


CAMPOS_PARTE1 = ("duracion_normal", "costo_aceleracion", "reduccion_tiempo_si_acelera")


def trae_datos(ruta: Union[str, Path]) -> bool:
    """¿El archivo trae datos de la Parte 1? Si no, el caso es «no aplica» para esta parte (no es un error).

    Un .json trae la Parte 1 si tiene `parametros.presupuesto_aceleracion_B` o algún campo de aceleración en las
    etapas (duración, costo o reducción). Un JSON ilegible se deja pasar: `leer_instancia` informa el error de formato.
    Si trae algunos campos y le faltan otros, tampoco es «no aplica»: `leer_instancia` dice cuáles faltan.
    """
    camino = Path(ruta)
    if camino.suffix.lower() != ".json":
        return False
    try:
        with open(camino, encoding="utf-8") as f:
            datos = json.load(f)
    except (OSError, ValueError):
        return True
    if not isinstance(datos, dict):
        return True
    parametros, etapas = datos.get("parametros"), datos.get("etapas")
    if isinstance(parametros, dict) and "presupuesto_aceleracion_B" in parametros:
        return True
    return isinstance(etapas, list) and any(
        isinstance(e, dict) and any(c in e for c in CAMPOS_PARTE1) for e in etapas)


def _entero(valor, minimo: int = 0) -> bool:
    """True si es un entero (no booleano) mayor o igual que `minimo`."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo


def leer_instancia(ruta: Union[str, Path]) -> InstanciaAceleracion:
    """Lee un caso `.json` de la Parte 1.  T = O(n)."""
    camino = Path(ruta)
    nombre = camino.stem
    if camino.suffix.lower() != ".json":
        raise ErrorDeLectura("%s: la Parte 1 solo lee archivos .json" % camino.name)
    try:
        with open(camino, encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ErrorDeLectura("%s: JSON inválido (línea %d, columna %d): %s"
                             % (nombre, e.lineno, e.colno, e.msg))
    except UnicodeDecodeError:
        raise ErrorDeLectura("%s: el archivo no está en UTF-8" % nombre)
    if not isinstance(datos, dict):
        raise ErrorDeLectura("%s: el JSON debe ser un objeto con 'parametros' y 'etapas'" % nombre)

    parametros = datos.get("parametros")
    if not isinstance(parametros, dict) or not _entero(parametros.get("presupuesto_aceleracion_B")):
        raise ErrorDeLectura("%s: falta 'parametros.presupuesto_aceleracion_B' o no es un entero >= 0" % nombre)
    B = parametros["presupuesto_aceleracion_B"]

    etapas = datos.get("etapas")
    if not isinstance(etapas, list) or not etapas:
        raise ErrorDeLectura("%s: falta 'etapas' o no es una lista con elementos" % nombre)

    t: List[int] = []
    c: List[int] = []
    d: List[int] = []
    ids: List[str] = []
    for k, e in enumerate(etapas, start=1):
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):
            raise ErrorDeLectura("%s: la etapa número %d no tiene 'id' de texto" % (nombre, k))
        eid = e["id"]
        for clave in ("duracion_normal", "costo_aceleracion", "reduccion_tiempo_si_acelera"):
            if not _entero(e.get(clave)):
                raise ErrorDeLectura("%s, etapa %s: falta '%s' o no es un entero >= 0" % (nombre, eid, clave))
        ti, ci, di = (e["duracion_normal"], e["costo_aceleracion"],
                      e["reduccion_tiempo_si_acelera"])
        if di > ti:  # debe cumplirse 0 <= d_i <= t_i
            raise ErrorDeLectura("%s, etapa %s: la reducción (%d) supera la duración (%d)" % (nombre, eid, di, ti))
        ids.append(eid)
        t.append(ti)
        c.append(ci)
        d.append(di)
    if len(set(ids)) != len(ids):  # ids repetidos
        raise ErrorDeLectura("%s: hay ids de etapa repetidos" % nombre)

    declarado = parametros.get("numero_etapas")  # coherencia opcional con la lista
    if declarado is not None and declarado != len(t):
        raise ErrorDeLectura("%s: 'numero_etapas' dice %s pero hay %d" % (nombre, declarado, len(t)))

    return InstanciaAceleracion(nombre, t, c, d, B, tuple(ids))


def leer_casos(directorio: Union[str, Path]) -> List[InstanciaAceleracion]:
    """Lee todos los `.json` de un directorio, ordenados por nombre.  T = O(casos·n)."""
    dirp = Path(directorio)
    if not dirp.is_dir():
        raise ErrorDeLectura("%s no es un directorio" % directorio)
    archivos = sorted(p for p in dirp.iterdir() if p.suffix.lower() == ".json")
    return [leer_instancia(p) for p in archivos]
