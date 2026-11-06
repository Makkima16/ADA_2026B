"""Lectura de los costos de auditoría a_j para la Variante 1.  [Integrante 3]

La Parte 2 ya lee las categorías con `lectura.leer_instancia` (no se toca).
Este módulo solo agrega los costos, leyendo el MISMO archivo del caso:

* ``.json`` de la profesora: cada etapa trae ``variaciones_auditoria``, una lista de
  opciones de auditar esa interacción: ``completa`` (cubre todo lo que cubre la interacción)
  y, en algunas etapas, ``parcial`` (cubre menos y cuesta menos). Cada opción tiene
  ``costo`` y ``riesgos_cubiertos``. `leer_opciones` convierte cada opción en un "conjunto con
  costo" y el voraz ponderado se corre sin cambios sobre esa lista (la adaptación está
  en la lectura, no en el algoritmo).
* ``.json`` propio con el campo ``costo_auditoria`` por etapa (forma anterior, una sola opción).
* ``.txt``: una línea de comentario ``# costos: a_1 a_2 ... a_n`` (el lector de la Parte 2 ignora
  los comentarios, así que el archivo sigue siendo válido para ella).

Si el caso no trae costos, `leer_opciones` y `leer_costos` devuelven None: la variante no se
ejecuta para ese caso y la evidencia lo dice (no se inventan costos).

Costo de la lectura: T(n) = O(L), con L = caracteres del archivo.
"""

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Union

from .resolver import Instancia

CAMPO_COSTO_JSON = "costo_auditoria"   # forma anterior (una sola opción por interacción)
CAMPO_VARIACIONES_JSON = "variaciones_auditoria"   # forma del JSON de la profesora
PREFIJO_TXT = "costos:"


class ErrorDeCostos(ValueError):
    """Los costos existen pero están mal escritos (cantidad o valores inválidos)."""


def _numero_positivo(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0      # C (5)


def leer_costos(ruta: Union[str, Path], n: int) -> Optional[List[float]]:
    """Costos a_1..a_n del caso, o None si el archivo no los trae.  O(L)."""
    camino = Path(ruta)                                       # C (1)
    nombre = camino.stem                                      # C (1)
    if camino.suffix.lower() == ".json":                      # C (2)
        with open(camino, encoding="utf-8") as f:             # C
            datos = json.load(f)                              # O(L)
        etapas = datos.get("etapas", []) if isinstance(datos, dict) else []   # C (3)
        if not any(isinstance(e, dict) and CAMPO_COSTO_JSON in e for e in etapas):   # O(n)
            return None                                       # el caso no trae costos
        costos = []                                           # C (1)
        for k, e in enumerate(etapas, start=1):               # n+1 pruebas de ciclo -> O(n)
            valor = e.get(CAMPO_COSTO_JSON) if isinstance(e, dict) else None   # C (3)
            if not _numero_positivo(valor):                   # C (5)
                raise ErrorDeCostos("%s, etapa %d: '%s' debe ser un número > 0 (recibido %r)"
                                    % (nombre, k, CAMPO_COSTO_JSON, valor))
            costos.append(valor)                              # C (1) amortizado
    else:
        costos = None                                         # C (1)
        with open(camino, encoding="utf-8") as f:             # C
            for num, cruda in enumerate(f, start=1):          # L+1 pruebas de ciclo -> O(L)
                texto = cruda.strip()                         # O(longitud de la línea)
                if not texto.startswith("#"):                 # C (1)
                    continue
                resto = texto[1:].strip()                     # C (2)
                if resto.lower().startswith(PREFIJO_TXT):     # C (2)
                    try:
                        costos = [float(x) if "." in x else int(x)
                                  for x in resto[len(PREFIJO_TXT):].split()]   # O(n)
                    except ValueError:
                        raise ErrorDeCostos("%s, línea %d: los costos deben ser números" % (nombre, num))
                    break
        if costos is None:                                    # C (1)
            return None
        malos = [x for x in costos if not _numero_positivo(x)]   # O(n)
        if malos:                                             # C (1)
            raise ErrorDeCostos("%s: hay costos que no son > 0: %s" % (nombre, malos))
    if len(costos) != n:                                      # C (2)
        raise ErrorDeCostos("%s: hay %d costos para %d interacciones" % (nombre, len(costos), n))
    return costos                                             # C (1)


# --------------------------------------------------------------- opciones de auditoría (parcial / completa)

TIPO_COMPLETA, TIPO_PARCIAL, TIPO_UNICA = "completa", "parcial", "única"


@dataclass(frozen=True)
class OpcionesAuditoria:
    """Lo que lee la variante: una "interacción" por opción, lista para el voraz ponderado.

    Las opciones 1..n son las completas (misma numeración que las interacciones) y las parciales
    van después (n+1, n+2, ...), así el desempate por menor índice prefiere la completa.
    """

    instancia: Instancia           # una interacción por opción, con etiquetas "E01 (completa)"
    costos: List[float]            # costo de cada opción
    interaccion: List[int]         # opción k (1..m) -> interacción original (1..n)
    tipo: List[str]                # completa, parcial o única (forma anterior)
    n: int                         # interacciones originales
    original: Optional[Instancia] = None   # la instancia sin expandir (con los ids originales)
    version: str = ""              # «con parciales», «solo completas» o «única»
    n_parciales: int = 0           # variaciones parciales que trae el archivo (aunque la versión «solo completas» no las use)

    @property
    def hay_parcial(self) -> bool:
        return TIPO_PARCIAL in self.tipo

    def solo_completas(self) -> "OpcionesAuditoria":
        """La misma lectura pero solo con las variaciones completas: un costo a_j por interacción (la definición de la
        variante 1). Es la versión principal; la que trae las parciales es una extensión que se mide aparte."""
        if not self.hay_parcial:
            return self
        n = self.n
        base = replace(self.original, S=[set(s) for s in self.instancia.S[:n]])
        return OpcionesAuditoria(base, self.costos[:n], self.interaccion[:n], self.tipo[:n], n, self.original, "solo completas", self.n_parciales)


def _ids_de(inst: Instancia, ids, nombre: str, k: int) -> List[int]:
    """Convierte ids de categoría (R01...) en números 1..r, validando que existan."""
    indice = {c: i for i, c in enumerate(inst.ids_categoria or (), start=1)}
    salida = []
    for c in ids:
        if c not in indice:
            raise ErrorDeCostos("%s, etapa %d: la categoría %r de una variación no está en categorias_riesgo" % (nombre, k, c))
        salida.append(indice[c])
    return salida


def _leer_variaciones(nombre: str, etapas: list, inst: Instancia):
    """(costos, conjuntos, interaccion, tipo) de las opciones del formato de la profesora."""
    n = len(etapas)
    if n != len(inst.S):
        raise ErrorDeCostos("%s: hay %d etapas con variaciones para %d interacciones" % (nombre, n, len(inst.S)))
    completas, parciales = [], []
    for k, e in enumerate(etapas, start=1):
        variaciones = e.get(CAMPO_VARIACIONES_JSON) if isinstance(e, dict) else None
        if not isinstance(variaciones, list) or not variaciones:
            raise ErrorDeCostos("%s, etapa %d: falta '%s' (otras etapas sí la traen)" % (nombre, k, CAMPO_VARIACIONES_JSON))
        por_id = {}
        for v in variaciones:
            vid = v.get("id") if isinstance(v, dict) else None
            if vid not in (TIPO_COMPLETA, TIPO_PARCIAL) or vid in por_id:
                raise ErrorDeCostos("%s, etapa %d: las variaciones válidas son una 'completa' y, opcionalmente, una 'parcial' "
                                    "(recibido %r)" % (nombre, k, vid))
            if not _numero_positivo(v.get("costo")):
                raise ErrorDeCostos("%s, etapa %d, variación %s: 'costo' debe ser un número > 0 (recibido %r)"
                                    % (nombre, k, vid, v.get("costo")))
            riesgos = v.get("riesgos_cubiertos")
            if not isinstance(riesgos, list) or not riesgos:
                raise ErrorDeCostos("%s, etapa %d, variación %s: 'riesgos_cubiertos' debe ser una lista con elementos" % (nombre, k, vid))
            por_id[vid] = (v["costo"], set(_ids_de(inst, riesgos, nombre, k)))
        if TIPO_COMPLETA not in por_id:
            raise ErrorDeCostos("%s, etapa %d: falta la variación 'completa'" % (nombre, k))
        costo_c, S_c = por_id[TIPO_COMPLETA]
        if S_c != set(inst.S[k - 1]):
            raise ErrorDeCostos("%s, etapa %d: la variación 'completa' no cubre lo mismo que riesgos_cubiertos_auditoria_completa"
                                % (nombre, k))
        completas.append((costo_c, S_c))
        if TIPO_PARCIAL in por_id:
            costo_p, S_p = por_id[TIPO_PARCIAL]
            if not S_p <= S_c:
                raise ErrorDeCostos("%s, etapa %d: la variación 'parcial' cubre riesgos que la 'completa' no cubre" % (nombre, k))
            parciales.append((k, costo_p, S_p))
    costos = [c for c, _ in completas] + [c for _, c, _ in parciales]
    conjuntos = [s for _, s in completas] + [s for _, _, s in parciales]
    interaccion = list(range(1, n + 1)) + [k for k, _, _ in parciales]
    tipo = [TIPO_COMPLETA] * n + [TIPO_PARCIAL] * len(parciales)
    return costos, conjuntos, interaccion, tipo


def leer_opciones(ruta: Union[str, Path], inst: Instancia) -> Optional[OpcionesAuditoria]:
    """Opciones de auditoría del caso, o None si el archivo no trae costos.  O(L + n·r).

    Con el formato de la profesora hay una opción completa por etapa y, donde exista, una parcial.
    Con `costo_auditoria` o `# costos:` hay una sola opción por interacción (sin parcial).
    """
    camino = Path(ruta)
    nombre = camino.stem
    n = len(inst.S)
    if camino.suffix.lower() == ".json":
        with open(camino, encoding="utf-8") as f:
            datos = json.load(f)
        etapas = datos.get("etapas", []) if isinstance(datos, dict) else []
        if any(isinstance(e, dict) and CAMPO_VARIACIONES_JSON in e for e in etapas):
            costos, conjuntos, interaccion, tipo = _leer_variaciones(nombre, etapas, inst)
        else:
            simples = leer_costos(camino, n)
            if simples is None:
                return None
            costos, conjuntos = simples, [set(s) for s in inst.S]
            interaccion, tipo = list(range(1, n + 1)), [TIPO_UNICA] * n
    else:
        simples = leer_costos(camino, n)
        if simples is None:
            return None
        costos, conjuntos = simples, [set(s) for s in inst.S]
        interaccion, tipo = list(range(1, n + 1)), [TIPO_UNICA] * n

    hay_parcial = TIPO_PARCIAL in tipo
    etiquetas = [inst.etiqueta_interaccion(i) + (" (%s)" % t if hay_parcial else "") for i, t in zip(interaccion, tipo)]
    expandida = replace(inst, S=conjuntos, ids_interaccion=etiquetas)
    return OpcionesAuditoria(expandida, costos, interaccion, tipo, n, inst, "con parciales" if hay_parcial else "única", tipo.count(TIPO_PARCIAL))
