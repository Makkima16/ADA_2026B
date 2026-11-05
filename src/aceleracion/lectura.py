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

Costo por línea: `# costo: OE × veces`, con el modelo del curso explicado al inicio de
`aceleracion.py` (cada asignación, comparación, operación aritmética, acceso a una lista
o a una clave de diccionario, return o llamada cuesta 1; la cabecera de un `for` de m
vueltas cuesta 3 × (m + 1) y su cuerpo m veces; un `if` dentro de un `for` se evalúa en
todas las vueltas; el cuerpo de una función llamada se analiza aparte).
Variables: n = etapas del caso, L = caracteres del archivo (en un archivo normal L es
proporcional a n), m = archivos de la carpeta, c = casos .json de la carpeta.
Al final de cada función se arma T(n); al final del archivo están el resumen del mejor
caso, el peor y el promedio, y el invariante del ciclo de lectura.
"""

import json
from pathlib import Path
from typing import List, Union

from .resolver import InstanciaAceleracion


class ErrorDeLectura(ValueError):
    """Error de formato con el nombre del caso y la etapa donde se rompió."""


def _entero(valor, minimo: int = 0) -> bool:
    """True si es un entero (no booleano) mayor o igual que `minimo`."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo   # costo: 7 × 1 por llamada   (isinstance, and, isinstance, not, and, comparación, return; si no es entero: 3)


def leer_instancia(ruta: Union[str, Path]) -> InstanciaAceleracion:
    """Lee un caso `.json` de la Parte 1.  T = O(n)."""
    camino = Path(ruta)                                       # costo: 2 × 1   (llamada + asignación)
    nombre = camino.stem                                      # costo: 2 × 1
    if camino.suffix.lower() != ".json":                      # costo: 3 × 1   (atributo, lower, comparación)
        raise ErrorDeLectura("%s: la Parte 1 solo lee archivos .json" % camino.name)   # costo: solo si la extensión es otra (termina aquí)
    try:                                                      # costo: 0 (solo marca el bloque)
        with open(camino, encoding="utf-8") as f:             # costo: 2 × 1, más el acceso al disco
            datos = json.load(f)                              # costo: 2 × 1 + L   (llamada + asignación; leer y analizar los L caracteres del archivo)
    except json.JSONDecodeError as e:                         # costo: solo si el JSON está mal escrito (termina aquí)
        raise ErrorDeLectura("%s: JSON inválido (línea %d, columna %d): %s"
                             % (nombre, e.lineno, e.colno, e.msg))
    except UnicodeDecodeError:                                # costo: solo si no es UTF-8 (termina aquí)
        raise ErrorDeLectura("%s: el archivo no está en UTF-8" % nombre)
    if not isinstance(datos, dict):                           # costo: 2 × 1
        raise ErrorDeLectura("%s: el JSON debe ser un objeto con 'parametros' y 'etapas'" % nombre)   # costo: solo si hay error

    parametros = datos.get("parametros")                      # costo: 2 × 1
    if not isinstance(parametros, dict) or not _entero(parametros.get("presupuesto_aceleracion_B")):   # costo: 13 × 1   (isinstance, not, or, get, llamada + 7 de su cuerpo, not)
        raise ErrorDeLectura("%s: falta 'parametros.presupuesto_aceleracion_B' o no es un entero >= 0" % nombre)   # costo: solo si hay error
    B = parametros["presupuesto_aceleracion_B"]               # costo: 2 × 1

    etapas = datos.get("etapas")                              # costo: 2 × 1
    if not isinstance(etapas, list) or not etapas:            # costo: 4 × 1
        raise ErrorDeLectura("%s: falta 'etapas' o no es una lista con elementos" % nombre)   # costo: solo si hay error

    t: List[int] = []                                         # costo: 1 × 1
    c: List[int] = []                                         # costo: 1 × 1
    d: List[int] = []                                         # costo: 1 × 1
    ids: List[str] = []                                       # costo: 1 × 1
    for k, e in enumerate(etapas, start=1):                   # costo: 3 × (n+1)   (cabecera: n+1 veces)
        if not isinstance(e, dict) or not isinstance(e.get("id"), str):   # costo: 6 × n   (el if está dentro del for: se evalúa las n vueltas; isinstance, not, or, get, isinstance, not)
            raise ErrorDeLectura("%s: la etapa número %d no tiene 'id' de texto" % (nombre, k))   # costo: solo si hay error
        eid = e["id"]                                         # costo: 2 × n
        for clave in ("duracion_normal", "costo_aceleracion", "reduccion_tiempo_si_acelera"):   # costo: 3 × 4n   (este ciclo siempre tiene 3 vueltas: su cabecera se ejecuta 4 veces por cada una de las n etapas)
            if not _entero(e.get(clave)):                     # costo: 10 × 3n   (cuerpo del ciclo interno: 3 vueltas por etapa; get, llamada + 7 de su cuerpo, not)
                raise ErrorDeLectura("%s, etapa %s: falta '%s' o no es un entero >= 0" % (nombre, eid, clave))   # costo: solo si hay error
        ti, ci, di = (e["duracion_normal"], e["costo_aceleracion"],
                      e["reduccion_tiempo_si_acelera"])       # costo: 6 × n   (3 accesos + 3 asignaciones)
        if di > ti:                                           # costo: 1 × n   # debe cumplirse 0 <= d_i <= t_i
            raise ErrorDeLectura("%s, etapa %s: la reducción (%d) supera la duración (%d)" % (nombre, eid, di, ti))   # costo: solo si hay error
        ids.append(eid)                                       # costo: 1 × n
        t.append(ti)                                          # costo: 1 × n
        c.append(ci)                                          # costo: 1 × n
        d.append(di)                                          # costo: 1 × n
    if len(set(ids)) != len(ids):                             # costo: 1 + n + 3   (llamar set y recorrer n ids; 2 len y la comparación)   # ids repetidos
        raise ErrorDeLectura("%s: hay ids de etapa repetidos" % nombre)   # costo: solo si hay error

    declarado = parametros.get("numero_etapas")               # costo: 2 × 1   # coherencia opcional con la lista
    if declarado is not None and declarado != len(t):         # costo: 4 × 1   (comparación, and, len, comparación)
        raise ErrorDeLectura("%s: 'numero_etapas' dice %s pero hay %d" % (nombre, declarado, len(t)))   # costo: solo si hay error

    return InstanciaAceleracion(nombre, t, c, d, B, tuple(ids))   # costo: 1 + n + 1 + 6 + 1   (llamar tuple y recorrer n ids; llamar al constructor, 6 asignaciones de campos, return) = n + 9
    # Suma de costos:
    #   T(n) = [2+2+3+2+(2+L)+2] + [2+13+2] + [2+4] + 4 + 3(n+1) + 6n + 2n + 3·4n + 10·3n + 6n + n + 4n
    #          + (n + 4) + 2 + 4 + (n + 9)
    # Expansión (los ciclos se resuelven con sumatorias de constantes: Σ_{e=1}^{n} 61 = 61n):
    #   T(n) = (13 + L) + 17 + 6 + 4 + 3n + 3 + 61n + n + 4 + 2 + 4 + n + 9
    # Agrupación:
    #   T(n) = 66n + 62 + L          y como L es proporcional a n  -> Θ(n)


def leer_casos(directorio: Union[str, Path]) -> List[InstanciaAceleracion]:
    """Lee todos los `.json` de un directorio, ordenados por nombre.  T = O(casos·n)."""
    dirp = Path(directorio)                                   # costo: 2 × 1
    if not dirp.is_dir():                                     # costo: 2 × 1
        raise ErrorDeLectura("%s no es un directorio" % directorio)   # costo: solo si no es carpeta
    archivos = sorted(p for p in dirp.iterdir() if p.suffix.lower() == ".json")   # costo: 1 + 3 × (m+1) + 3 × m + 1 + m·log₂m + 1   (llamar iterdir; cabecera del generador m+1 veces; por archivo: atributo, lower, comparación; llamar sorted y ordenar los que pasan; asignar) = 6m + m·log₂m + 6
    return [leer_instancia(p) for p in archivos]              # costo: 3 × (c+1) + 2 × c + 1 + Σ T_leer_instancia   (cabecera c+1 veces; por caso: llamada y guardar; return)
    # Suma de costos:  T = 2 + 2 + (6m + m·log₂m + 6) + (5c + 4) + Σ(66·nᵢ + 62 + Lᵢ)
    # Agrupación:      T = 6m + m·log₂m + 5c + 14 + Σ(66·nᵢ + 62 + Lᵢ)
    # Orden de crecimiento: Θ(m·log m + Σ nᵢ)


# =============================================================================
# RESUMEN DE COSTO DEL ARCHIVO
# n = etapas del caso, L = caracteres del archivo (proporcional a n), m = archivos de la carpeta,
# c = casos .json (c <= m).
#
# Función           Mejor caso               Peor caso                      Promedio
# ----------------  -----------------------  -----------------------------  -----------------------
# _entero           3                        7                              7  (los datos válidos son enteros)
# leer_instancia    7  (extensión que no     66n + 62 + L                   66n + 62 + L
#                   es .json: termina en                                    -> Θ(n)
#                   la tercera línea)
# leer_casos        14  (carpeta vacía)      6m + m·log₂m + 5c + 14 + Σ(66nᵢ + 62 + Lᵢ)   -> Θ(m·log m + Σ nᵢ)
#
# Para un archivo VÁLIDO no hay mejor caso distinto: los ciclos recorren siempre las n etapas y
# se hacen siempre las mismas comprobaciones, así que mejor, peor y promedio son Θ(n) (≈ 66n).
# Cuando el archivo tiene un error, la función se detiene en la primera línea que lo detecta: es
# el único "mejor caso", y cuesta menos de 66n.
# El costo de leer es independiente de B: B es un solo número que se lee una vez.
# =============================================================================


# =============================================================================
# INVARIANTE DE CICLO (correctitud)
#
# --- leer_instancia, ciclo `for k, e in enumerate(etapas, start=1)` ------------
# Invariante: antes de procesar la etapa k, las listas t, c, d e ids tienen exactamente k-1
#   elementos cada una, y su posición j (1 <= j <= k-1) guarda los valores ya validados de la
#   etapa j del archivo (con 0 <= d_j <= t_j y los tres enteros >= 0), en el mismo orden.
#  - Inicialización (k = 1): las cuatro listas se crearon vacías, o sea con 0 = k-1 elementos, y no
#    hay etapas procesadas: se cumple.
#  - Mantenimiento: si la etapa k incumple cualquier comprobación (id sin texto, campo no entero,
#    d > t), se lanza ErrorDeLectura y no se llega a k+1. Si las cumple, los cuatro `append` del
#    final del cuerpo agregan un elemento a cada lista, siempre juntos, así que las listas pasan a
#    tener k elementos, cada una con el valor de la etapa k en su última posición.
#  - Finalización: con k = n+1 las listas tienen n elementos: describen toda la cadena, validada y en
#    orden. Por eso las cuatro tienen el mismo largo y la instancia que se construye es consistente.
# =============================================================================
