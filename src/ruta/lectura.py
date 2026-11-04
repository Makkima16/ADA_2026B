"""Lectura de casos de la Parte 2 (auditoría).

Formato propio provisional
--------------------------
Los casos de la profesora todavía no llegaron, así que los casos de prueba
propios usan este formato de texto (un archivo por caso, extensión .txt):

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

Cuando se conozca el formato real de la profesora, se adapta ÚNICAMENTE este
módulo (skill adaptar-lectura-casos); los algoritmos no se tocan.

Costo de la lectura: T(n, r) = O(n·r): se leen n líneas con a lo sumo r enteros.
"""

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


def leer_instancia(ruta: Union[str, Path]) -> Instancia:
    """Lee un archivo de caso y devuelve una `Instancia`.  T = O(n·r)."""
    camino = Path(ruta)                                       # C (1)
    nombre = camino.stem                                      # C (1): nombre del caso = archivo sin extensión
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
    """Lee todos los .txt de un directorio, ordenados por nombre.  T = O(casos·n·r)."""
    dirp = Path(directorio)                                   # C (1)
    if not dirp.is_dir():                                     # C (1): comparación
        raise ErrorDeLectura("%s no es un directorio" % directorio)   # C: ruta inválida
    return [leer_instancia(p) for p in sorted(dirp.glob("*.txt"))]    # O(casos · n · r): leer cada caso
