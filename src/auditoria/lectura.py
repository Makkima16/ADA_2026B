"""Lectura de casos de la Parte 2 (auditoría).

Se aceptan dos formatos, elegidos por la extensión del archivo:

* ``.json``: el formato del ejemplo de la profesora (ver más abajo).
* ``.txt``: el formato propio provisional de los casos de prueba.

Formato JSON (ejemplo ``entrada_G3_mochila_20_nodos.json``)
-----------------------------------------------------------
Un solo archivo trae las dos partes del proyecto; la Parte 2 solo usa:

* ``categorias_riesgo``: lista de ``{id, categoria, importancia}``. El orden de
  la lista define la numeración 1..r (R01 -> 1, R02 -> 2, ...).
* ``etapas``: lista de objetos con ``id`` y ``riesgos_cubiertos_auditoria_completa``
  (ids de categorías). Cada etapa es una interacción; ese campo es su S_j.
* ``parametros.numero_etapas`` y ``parametros.numero_categorias_riesgo`` (si
  están) se comprueban contra las listas.

Lo demás (duraciones, costos, flujo, variaciones de auditoría, presupuestos)
es de la Parte 1 o de variantes y se ignora. ``importancia`` se guarda en la
instancia pero el voraz base no la usa.

Formato propio provisional (.txt)
---------------------------------
Los casos de prueba propios usan este formato de texto (un archivo por caso):

    # las líneas que empiezan con '#' son comentarios y se ignoran
    r n
    c1 c2 ... ck        <- categorías que cubre la interacción 1
    c1 c2 ... ck        <- categorías que cubre la interacción 2
    ...                 (exactamente n líneas)

- La primera línea de datos trae dos enteros: r (categorías, U = {1..r}) y
  n (interacciones).
- Siguen exactamente n líneas; la línea i trae las categorías de S_i,
  separadas por espacios, enteras en 1..r y sin repetir. Cada interacción
  cubre al menos una categoría (en este formato provisional no se admiten
  interacciones vacías).
- El nombre del caso es el nombre del archivo sin la extensión.

Si el formato real de la profesora cambia, se adapta ÚNICAMENTE este módulo
(skill adaptar-lectura-casos); los algoritmos no se tocan.

Costo de la lectura: T(n, r) = O(n·r): se leen n líneas con a lo sumo r enteros.
"""

import json
from pathlib import Path
from typing import List, Set, Union

from .resolver import Instancia


class ErrorDeLectura(ValueError):
    """Error de formato con el nombre del caso y la línea donde se rompió."""


def trae_datos(ruta: Union[str, Path]) -> bool:
    """¿El archivo trae datos de la Parte 2? Si no, el caso es «no aplica» para esta parte (no es un error).

    Un .txt siempre es de la Parte 2. Un .json la trae si tiene `categorias_riesgo` o algún
    `riesgos_cubiertos_auditoria_completa` en las etapas. Un JSON ilegible se deja pasar: `leer_instancia`
    informa el error de formato.
    """
    camino = Path(ruta)
    if camino.suffix.lower() != ".json":
        return True
    try:
        with open(camino, encoding="utf-8") as f:
            datos = json.load(f)
    except (OSError, ValueError):
        return True
    if not isinstance(datos, dict):
        return True
    etapas = datos.get("etapas")
    return "categorias_riesgo" in datos or (isinstance(etapas, list) and any(
        isinstance(e, dict) and "riesgos_cubiertos_auditoria_completa" in e for e in etapas))


def _lineas_utiles(camino: Path) -> List[tuple]:
    """(número de línea, texto) sin comentarios ni líneas vacías."""
    utiles: List[tuple] = []
    with open(camino, encoding="utf-8") as f:
        for num, cruda in enumerate(f, start=1):
            texto = cruda.split("#", 1)[0].strip()
            if texto:
                utiles.append((num, texto))
    return utiles


def _lista_de(datos: dict, clave: str, nombre: str) -> list:
    """Campo obligatorio que debe ser una lista no vacía."""
    valor = datos.get(clave)
    if not isinstance(valor, list) or not valor:
        raise ErrorDeLectura("%s: falta '%s' o no es una lista con elementos" % (nombre, clave))
    return valor


def _leer_json(camino: Path, nombre: str) -> Instancia:
    """Lee el formato JSON de la profesora.  T = O(n·r)."""
    try:
        with open(camino, encoding="utf-8") as f:
            datos = json.load(f)
    except json.JSONDecodeError as e:
        raise ErrorDeLectura("%s: JSON inválido (línea %d, columna %d): %s"
                             % (nombre, e.lineno, e.colno, e.msg))
    except UnicodeDecodeError:
        raise ErrorDeLectura("%s: el archivo no está en UTF-8" % nombre)
    if not isinstance(datos, dict):
        raise ErrorDeLectura("%s: el JSON debe ser un objeto con 'categorias_riesgo' y 'etapas'" % nombre)

    categorias = _lista_de(datos, "categorias_riesgo", nombre)
    etapas = _lista_de(datos, "etapas", nombre)
    ids_cat: List[str] = []
    nombres_cat: List[str] = []
    importancias: List[int] = []
    for k, c in enumerate(categorias, start=1):
        if not isinstance(c, dict) or not isinstance(c.get("id"), str):
            raise ErrorDeLectura("%s: la categoría número %d no tiene 'id' de texto" % (nombre, k))
        ids_cat.append(c["id"])
        nombres_cat.append(str(c.get("categoria", "")))
        importancias.append(c.get("importancia"))
    if len(set(ids_cat)) != len(ids_cat):
        raise ErrorDeLectura("%s: hay ids de categoría repetidos" % nombre)
    numero = {cid: k for k, cid in enumerate(ids_cat, start=1)}
    r = len(ids_cat)

    ids_int: List[str] = []
    S: List[Set[int]] = []
    for k, e in enumerate(etapas, start=1):
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):
            raise ErrorDeLectura("%s: la etapa número %d no tiene 'id' de texto" % (nombre, k))
        eid = e["id"]
        riesgos = e.get("riesgos_cubiertos_auditoria_completa")
        if not isinstance(riesgos, list):
            raise ErrorDeLectura("%s, etapa %s: falta 'riesgos_cubiertos_auditoria_completa'" % (nombre, eid))
        desconocidos = [x for x in riesgos if x not in numero]
        if desconocidos:
            raise ErrorDeLectura("%s, etapa %s: categorías no definidas: %s" % (nombre, eid, desconocidos))
        s = {numero[x] for x in riesgos}
        if len(s) != len(riesgos):
            raise ErrorDeLectura("%s, etapa %s: hay categorías repetidas" % (nombre, eid))
        ids_int.append(eid)
        S.append(s)
    if len(set(ids_int)) != len(ids_int):
        raise ErrorDeLectura("%s: hay ids de etapa repetidos" % nombre)

    parametros = datos.get("parametros")
    if isinstance(parametros, dict):
        for clave, real in (("numero_etapas", len(S)), ("numero_categorias_riesgo", r)):
            declarado = parametros.get(clave)
            if declarado is not None and declarado != real:
                raise ErrorDeLectura("%s: '%s' dice %s pero hay %d" % (nombre, clave, declarado, real))

    todas = all(isinstance(x, int) and not isinstance(x, bool) for x in importancias)
    return Instancia(nombre, r, S, tuple(ids_int), tuple(ids_cat), tuple(nombres_cat),
                     tuple(importancias) if todas else None)


def leer_instancia(ruta: Union[str, Path]) -> Instancia:
    """Lee un archivo de caso (.json o .txt) y devuelve una `Instancia`.  T = O(n·r)."""
    camino = Path(ruta)
    nombre = camino.stem
    if camino.suffix.lower() == ".json":
        return _leer_json(camino, nombre)
    lineas = _lineas_utiles(camino)
    if not lineas:
        raise ErrorDeLectura("%s: el archivo no tiene datos" % nombre)

    num_cab, cab = lineas[0]
    campos = cab.split()
    if len(campos) != 2:
        raise ErrorDeLectura("%s, línea %d: se esperaba 'r n'" % (nombre, num_cab))
    try:
        r, n = int(campos[0]), int(campos[1])
    except ValueError:
        raise ErrorDeLectura("%s, línea %d: r y n deben ser enteros" % (nombre, num_cab))
    if r < 1 or n < 1:
        raise ErrorDeLectura("%s: se exige r >= 1 y n >= 1" % nombre)

    cuerpo = lineas[1:]
    if len(cuerpo) != n:
        raise ErrorDeLectura(
            "%s: se esperaban %d interacciones y llegaron %d" % (nombre, n, len(cuerpo))
        )

    S: List[Set[int]] = []
    for num, texto in cuerpo:
        try:
            valores = [int(x) for x in texto.split()]
        except ValueError:
            raise ErrorDeLectura("%s, línea %d: las categorías deben ser enteros" % (nombre, num))
        s = set(valores)
        if len(s) != len(valores):
            raise ErrorDeLectura("%s, línea %d: hay categorías repetidas" % (nombre, num))
        malas = [c for c in s if c < 1 or c > r]
        if malas:
            raise ErrorDeLectura(
                "%s, línea %d: categorías fuera de 1..%d: %s" % (nombre, num, r, sorted(malas))
            )
        S.append(s)
    return Instancia(nombre, r, S)


def leer_casos(directorio: Union[str, Path]) -> List[Instancia]:
    """Lee todos los .txt y .json de un directorio, ordenados por nombre.  T = O(casos·n·r)."""
    dirp = Path(directorio)
    if not dirp.is_dir():
        raise ErrorDeLectura("%s no es un directorio" % directorio)
    archivos = sorted(p for p in dirp.iterdir()
                      if p.suffix.lower() in (".txt", ".json"))
    return [leer_instancia(p) for p in archivos]
