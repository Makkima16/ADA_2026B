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
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Union


class ErrorDeLectura(ValueError):
    """Error de formato con el nombre del caso y la etapa donde se rompió."""


@dataclass
class InstanciaAceleracion:
    """Lo que el lector entrega al algoritmo: t, c, d, B más los nombres de las etapas."""
    nombre: str
    t: List[int]
    c: List[int]
    d: List[int]
    B: int
    ids_etapa: Tuple[str, ...] = ()


def _entero(valor, minimo: int = 0) -> bool:
    """True si es un entero (no booleano) mayor o igual que `minimo`."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo   # C (3)


def leer_instancia(ruta: Union[str, Path]) -> InstanciaAceleracion:
    """Lee un caso `.json` de la Parte 1.  T = O(n)."""
    camino = Path(ruta)                                       # C (1)
    nombre = camino.stem                                      # C (1)
    if camino.suffix.lower() != ".json":                      # C (1)
        raise ErrorDeLectura("%s: la Parte 1 solo lee archivos .json" % camino.name)
    try:                                                      # C: inicio del bloque
        with open(camino, encoding="utf-8") as f:             # C: abrir el archivo (una vez)
            datos = json.load(f)                              # O(L): leer y analizar L caracteres
    except json.JSONDecodeError as e:                         # C: solo si el JSON está mal escrito
        raise ErrorDeLectura("%s: JSON inválido (línea %d, columna %d): %s"
                             % (nombre, e.lineno, e.colno, e.msg))
    except UnicodeDecodeError:                                # C: solo si no es UTF-8
        raise ErrorDeLectura("%s: el archivo no está en UTF-8" % nombre)
    if not isinstance(datos, dict):                           # C (1)
        raise ErrorDeLectura("%s: el JSON debe ser un objeto con 'parametros' y 'etapas'" % nombre)

    parametros = datos.get("parametros")                      # C (1)
    if not isinstance(parametros, dict) or not _entero(parametros.get("presupuesto_aceleracion_B")):
        raise ErrorDeLectura("%s: falta 'parametros.presupuesto_aceleracion_B' o no es un entero >= 0" % nombre)
    B = parametros["presupuesto_aceleracion_B"]               # C (1)

    etapas = datos.get("etapas")                              # C (1)
    if not isinstance(etapas, list) or not etapas:            # C (2)
        raise ErrorDeLectura("%s: falta 'etapas' o no es una lista con elementos" % nombre)

    t: List[int] = []                                         # C (1)
    c: List[int] = []                                         # C (1)
    d: List[int] = []                                         # C (1)
    ids: List[str] = []                                       # C (1)
    for k, e in enumerate(etapas, start=1):                   # n+1 pruebas de ciclo -> O(n)
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):   # C (3)
            raise ErrorDeLectura("%s: la etapa número %d no tiene 'id' de texto" % (nombre, k))
        eid = e["id"]                                         # C (1)
        for clave in ("duracion_normal", "costo_aceleracion", "reduccion_tiempo_si_acelera"):   # C (3)
            if not _entero(e.get(clave)):                     # C (3)
                raise ErrorDeLectura("%s, etapa %s: falta '%s' o no es un entero >= 0" % (nombre, eid, clave))
        ti, ci, di = (e["duracion_normal"], e["costo_aceleracion"],
                      e["reduccion_tiempo_si_acelera"])       # C (3)
        if di > ti:                                           # C (1): debe cumplirse 0 <= d_i <= t_i
            raise ErrorDeLectura("%s, etapa %s: la reducción (%d) supera la duración (%d)" % (nombre, eid, di, ti))
        ids.append(eid)                                       # C (1) amortizado
        t.append(ti)                                          # C (1) amortizado
        c.append(ci)                                          # C (1) amortizado
        d.append(di)                                          # C (1) amortizado -> O(n)
    if len(set(ids)) != len(ids):                             # O(n): ids repetidos
        raise ErrorDeLectura("%s: hay ids de etapa repetidos" % nombre)

    declarado = parametros.get("numero_etapas")               # C (1): coherencia opcional con la lista
    if declarado is not None and declarado != len(t):         # C (2)
        raise ErrorDeLectura("%s: 'numero_etapas' dice %s pero hay %d" % (nombre, declarado, len(t)))

    return InstanciaAceleracion(nombre, t, c, d, B, tuple(ids))   # O(n): armar la instancia


def leer_casos(directorio: Union[str, Path]) -> List[InstanciaAceleracion]:
    """Lee todos los `.json` de un directorio, ordenados por nombre.  T = O(casos·n)."""
    dirp = Path(directorio)                                   # C (1)
    if not dirp.is_dir():                                     # C (1)
        raise ErrorDeLectura("%s no es un directorio" % directorio)
    archivos = sorted(p for p in dirp.iterdir() if p.suffix.lower() == ".json")   # O(casos log casos)
    return [leer_instancia(p) for p in archivos]              # O(casos · n)
