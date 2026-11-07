"""Escritura de la traza de la Variante 1 (voraz ponderado).  [Integrante 3]

Solo formatea; no calcula nada del algoritmo. Sigue el mismo estilo de
`traza.py` (Parte 2) y agrega por paso: costo, costo por categoría nueva y
costo acumulado.

Anotación de costos: C (k) es una línea de costo constante con k operaciones
elementales; O(...) es el costo asintótico de la línea o de la función.
"""

from typing import Iterable, Optional

from .resolver import Instancia
from .resolver_ponderada import ResultadoPonderado


def _lista(conjunto: Iterable[int], inst: Optional[Instancia] = None) -> str:
    """Conjunto de categorías en orden numérico; con nombres (R01...) si la instancia los trae."""
    nombre = inst.etiqueta_categoria if inst else str                # C (1)
    return "{" + ", ".join(nombre(x) for x in sorted(conjunto)) + "}"   # O(k log k), k <= r


def _num(x: float) -> str:
    """Número sin ceros de más: 6 en vez de 6.0."""
    return ("%d" % x) if float(x).is_integer() else ("%.4g" % x)    # C (3)


def formatear_resultado_ponderado(res: ResultadoPonderado) -> str:
    """Texto completo de un caso de la variante.  O(n·r)."""
    if not res.factible:                                             # C (1)
        return (
            "Caso: %s\nInstancia NO factible: nadie cubre las categorías %s. "
            "No se ejecutó el voraz ponderado.\n" % (res.nombre, sorted(res.sin_cubrir))
        )
    inst = res.instancia                                             # C (1)
    etq_j = inst.etiqueta_interaccion if inst else str               # C (1)
    con_ids = bool(inst and inst.ids_interaccion)                    # C (1)

    def rotulo(j: int) -> str:
        return str(j) + (" (%s)" % etq_j(j) if con_ids else "")     # C (3)

    lineas = ["Caso: %s" % res.nombre, "Voraz ponderado — traza de elecciones"]   # C (2)
    for i, p in enumerate(res.pasos, start=1):                       # |J| <= min(n, r) vueltas
        lineas.append(
            "  Paso %d: interacción %s | costo %s | categorías nuevas %s (%d) | costo por categoría %.4f"
            " | acumulado %s | faltan %s"
            % (i, rotulo(p.j), _num(p.costo), _lista(p.nuevas, inst), len(p.nuevas),
               p.costo_por_categoria, _num(p.acumulado), _lista(p.faltan, inst))
        )                                                            # |J| veces · O(r)
    lineas.append("Cobertura final (categoría -> interacción):")     # C (1)
    for c in sorted(res.cobertura):                                  # O(r log r)
        if inst and inst.ids_categoria:                              # C (1)
            nom = inst.nombres_categoria[c - 1] if inst.nombres_categoria else ""
            rot = inst.etiqueta_categoria(c) + (" (%s)" % nom if nom else "")
        else:
            rot = str(c)
        lineas.append("  categoría %s -> interacción %s" % (rot, etq_j(res.cobertura[c])))
    lineas.append("Interacciones auditadas: %s (%d)" % (res.J, len(res.J)) +
                  (": " + ", ".join(etq_j(j) for j in res.J) if con_ids else ""))   # O(|J|)
    lineas.append("Costo total: %s" % _num(res.costo))               # C (1)
    lineas.append("Cubre todas las categorías: %s" % ("sí" if res.cubre else "NO"))   # C (1)
    lineas.append("Tiempo: %.6f s" % res.tiempo_s)                   # C (1)
    if res.optimo_costo is not None:                                 # C (1)
        lineas.append("Óptimo (%s): costo %s con %s" % (res.optimo_metodo or "fuerza bruta", _num(res.optimo_costo), res.optimo_J) +
                      (": " + ", ".join(etq_j(j) for j in res.optimo_J) if con_ids else ""))
        lineas.append("Razón voraz / óptimo: %.4f" % (res.costo / res.optimo_costo))
    lineas.append("Cota H(d): %.4f" % res.cota)                      # C (1)
    return "\n".join(lineas) + "\n"                                  # O(L)
