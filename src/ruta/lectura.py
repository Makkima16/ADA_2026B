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


def _lineas_utiles(camino: Path) -> List[tuple]:
    """(número de línea, texto) sin comentarios ni líneas vacías."""
    utiles: List[tuple] = []                                  # C (1): lista vacía
    with open(camino, encoding="utf-8") as f:                 # C: abrir el archivo (una vez)
        for num, cruda in enumerate(f, start=1):              # L+1 pruebas de ciclo; L = líneas del archivo
            texto = cruda.split("#", 1)[0].strip()            # C (4) por línea: split, indexar, strip -> O(L)
            if texto:                                         # C (1) por línea -> O(L)
                utiles.append((num, texto))                   # C (1) cuando la línea es útil -> O(L)
    return utiles                                             # O(L): la lista de líneas útiles


def _lista_de(datos: dict, clave: str, nombre: str) -> list:
    """Campo obligatorio que debe ser una lista no vacía."""
    valor = datos.get(clave)                                  # C (1)
    if not isinstance(valor, list) or not valor:              # C (2)
        raise ErrorDeLectura("%s: falta '%s' o no es una lista con elementos" % (nombre, clave))
    return valor                                              # C (1)


def _leer_json(camino: Path, nombre: str) -> Instancia:
    """Lee el formato JSON de la profesora.  T = O(n·r)."""
    try:                                                      # C: inicio del bloque
        with open(camino, encoding="utf-8") as f:             # C: abrir el archivo (una vez)
            datos = json.load(f)                              # O(L): leer y analizar L caracteres
    except json.JSONDecodeError as e:                         # C: solo si el JSON está mal escrito
        raise ErrorDeLectura("%s: JSON inválido (línea %d, columna %d): %s"
                             % (nombre, e.lineno, e.colno, e.msg))
    except UnicodeDecodeError:                                # C: solo si no es UTF-8
        raise ErrorDeLectura("%s: el archivo no está en UTF-8" % nombre)
    if not isinstance(datos, dict):                           # C (1)
        raise ErrorDeLectura("%s: el JSON debe ser un objeto con 'categorias_riesgo' y 'etapas'" % nombre)

    categorias = _lista_de(datos, "categorias_riesgo", nombre)    # C (1)
    etapas = _lista_de(datos, "etapas", nombre)               # C (1)
    ids_cat: List[str] = []                                   # C (1)
    nombres_cat: List[str] = []                               # C (1)
    importancias: List[int] = []                              # C (1)
    for k, c in enumerate(categorias, start=1):               # r+1 pruebas de ciclo -> O(r)
        if not isinstance(c, dict) or not isinstance(c.get("id"), str):   # C (3)
            raise ErrorDeLectura("%s: la categoría número %d no tiene 'id' de texto" % (nombre, k))
        ids_cat.append(c["id"])                               # C (1) amortizado
        nombres_cat.append(str(c.get("categoria", "")))       # C (2)
        importancias.append(c.get("importancia"))             # C (1)
    if len(set(ids_cat)) != len(ids_cat):                     # C (3): conjunto de r ids -> O(r)
        raise ErrorDeLectura("%s: hay ids de categoría repetidos" % nombre)
    numero = {cid: k for k, cid in enumerate(ids_cat, start=1)}   # O(r): id -> número 1..r
    r = len(ids_cat)                                          # C (1)

    ids_int: List[str] = []                                   # C (1)
    S: List[Set[int]] = []                                    # C (1)
    for k, e in enumerate(etapas, start=1):                   # n+1 pruebas de ciclo -> O(n)
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):   # C (3)
            raise ErrorDeLectura("%s: la etapa número %d no tiene 'id' de texto" % (nombre, k))
        eid = e["id"]                                         # C (1)
        riesgos = e.get("riesgos_cubiertos_auditoria_completa")   # C (1)
        if not isinstance(riesgos, list):                     # C (1)
            raise ErrorDeLectura("%s, etapa %s: falta 'riesgos_cubiertos_auditoria_completa'" % (nombre, eid))
        desconocidos = [x for x in riesgos if x not in numero]    # O(r): ids que no existen
        if desconocidos:                                      # C (1)
            raise ErrorDeLectura("%s, etapa %s: categorías no definidas: %s" % (nombre, eid, desconocidos))
        s = {numero[x] for x in riesgos}                      # O(r): números 1..r
        if len(s) != len(riesgos):                            # C (2)
            raise ErrorDeLectura("%s, etapa %s: hay categorías repetidas" % (nombre, eid))
        ids_int.append(eid)                                   # C (1) amortizado
        S.append(s)                                           # C (1) amortizado -> O(n)
    if len(set(ids_int)) != len(ids_int):                     # O(n): ids de etapa repetidos
        raise ErrorDeLectura("%s: hay ids de etapa repetidos" % nombre)

    parametros = datos.get("parametros")                      # C (1)
    if isinstance(parametros, dict):                          # C (1): coherencia opcional con las listas
        for clave, real in (("numero_etapas", len(S)), ("numero_categorias_riesgo", r)):   # C (2)
            declarado = parametros.get(clave)                 # C (1)
            if declarado is not None and declarado != real:   # C (2)
                raise ErrorDeLectura("%s: '%s' dice %s pero hay %d" % (nombre, clave, declarado, real))

    todas = all(isinstance(x, int) and not isinstance(x, bool) for x in importancias)   # O(r)
    return Instancia(nombre, r, S, tuple(ids_int), tuple(ids_cat), tuple(nombres_cat),
                     tuple(importancias) if todas else None)  # O(n + r): armar la instancia


def leer_instancia(ruta: Union[str, Path]) -> Instancia:
    """Lee un archivo de caso (.json o .txt) y devuelve una `Instancia`.  T = O(n·r)."""
    camino = Path(ruta)                                       # C (1)
    nombre = camino.stem                                      # C (1): nombre del caso = archivo sin extensión
    if camino.suffix.lower() == ".json":                      # C (2): formato según la extensión
        return _leer_json(camino, nombre)                     # O(n·r): lector JSON
    lineas = _lineas_utiles(camino)                           # O(L): leer y limpiar el archivo
    if not lineas:                                            # C (1): comparación
        raise ErrorDeLectura("%s: el archivo no tiene datos" % nombre)   # C: solo si está vacío

    num_cab, cab = lineas[0]                                  # C (2): línea de cabecera
    campos = cab.split()                                      # C (1) amortizado
    if len(campos) != 2:                                      # C (1): comparación
        raise ErrorDeLectura("%s, línea %d: se esperaba 'r n'" % (nombre, num_cab))  # C: formato roto
    try:                                                      # C: inicio del bloque
        r, n = int(campos[0]), int(campos[1])                 # C (2): conversión a entero
    except ValueError:                                        # C: solo si no son enteros
        raise ErrorDeLectura("%s, línea %d: r y n deben ser enteros" % (nombre, num_cab))
    if r < 1 or n < 1:                                        # C (2): comparaciones
        raise ErrorDeLectura("%s: se exige r >= 1 y n >= 1" % nombre)    # C: valores inválidos

    cuerpo = lineas[1:]                                       # O(1): rebanado (vista, no copia)
    if len(cuerpo) != n:                                      # C (1): comparación
        raise ErrorDeLectura(
            "%s: se esperaban %d interacciones y llegaron %d" % (nombre, n, len(cuerpo))
        )                                                     # C: conteo de líneas incorrecto

    S: List[Set[int]] = []                                    # C (1): lista vacía
    for num, texto in cuerpo:                                 # n+1 pruebas de ciclo -> O(n)
        try:                                                  # C: inicio del bloque
            valores = [int(x) for x in texto.split()]         # O(r): convertir a lo sumo r enteros por línea -> O(n·r)
        except ValueError:                                    # C: solo si hay un token no entero
            raise ErrorDeLectura("%s, línea %d: las categorías deben ser enteros" % (nombre, num))
        s = set(valores)                                      # O(r): conjunto de a lo sumo r categorías
        if len(s) != len(valores):                            # C (2): dos len() y una comparación
            raise ErrorDeLectura("%s, línea %d: hay categorías repetidas" % (nombre, num))  # C: repetidas
        malas = [c for c in s if c < 1 or c > r]              # O(r): filtrar fuera de rango
        if malas:                                             # C (1): comparación
            raise ErrorDeLectura(
                "%s, línea %d: categorías fuera de 1..%d: %s" % (nombre, num, r, sorted(malas))
            )                                                 # C: índices inválidos
        S.append(s)                                           # C (1) amortizado -> O(n)
    return Instancia(nombre, r, S)                            # C (1): armar la instancia


def leer_casos(directorio: Union[str, Path]) -> List[Instancia]:
    """Lee todos los .txt y .json de un directorio, ordenados por nombre.  T = O(casos·n·r)."""
    dirp = Path(directorio)                                   # C (1)
    if not dirp.is_dir():                                     # C (1): comparación
        raise ErrorDeLectura("%s no es un directorio" % directorio)   # C: ruta inválida
    archivos = sorted(p for p in dirp.iterdir()
                      if p.suffix.lower() in (".txt", ".json"))    # O(casos log casos): listar y ordenar
    return [leer_instancia(p) for p in archivos]              # O(casos · n · r): leer cada caso
