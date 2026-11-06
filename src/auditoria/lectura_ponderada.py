"""Lectura de los costos de auditoría a_j para la Variante 1.  [Integrante 3]

La Parte 2 ya lee las categorías con `lectura.leer_instancia` (no se toca).
Este módulo solo agrega los costos, leyendo el MISMO archivo del caso:

* ``.json``: cada etapa (interacción) puede traer el campo ``costo_auditoria``
  (número > 0).  >>> PROVISIONAL <<<  El ejemplo de la profesora todavía no
  confirma en qué campo vienen los costos. Cuando se confirme, se cambia
  ÚNICAMENTE la constante `CAMPO_COSTO_JSON` (o esta función); el algoritmo
  de `ponderada.py` no se toca.
* ``.txt``: una línea de comentario ``# costos: a_1 a_2 ... a_n`` (el lector
  de la Parte 2 ignora los comentarios, así que el archivo sigue siendo válido
  para ella).

Si el caso no trae costos, `leer_costos` devuelve None: la variante no se
ejecuta para ese caso y la evidencia lo dice (no se inventan costos).

Costo de la lectura: T(n) = O(L), con L = caracteres del archivo.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

CAMPO_COSTO_JSON = "costo_auditoria"   # PROVISIONAL: confirmar con el JSON de la profesora
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
