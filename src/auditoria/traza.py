"""Escritura de la traza de la Parte 2 (voraz).

Solo formatea y escribe; no calcula nada del algoritmo. Se separa de
`auditoria.py` para poder reutilizarla en la variante ponderada.
"""

from typing import Dict, Iterable, List, Optional

from .auditoria import Paso
from .resolver import Instancia, ResultadoCaso


def _lista(conjunto: Iterable[int], inst: Optional[Instancia] = None) -> str:
    """Conjunto de categorías en orden numérico; con nombres (R01...) si la instancia los trae."""
    nombre = inst.etiqueta_categoria if inst else str
    return "{" + ", ".join(nombre(x) for x in sorted(conjunto)) + "}"


def formatear_traza(
    nombre_caso: str,
    pasos: List[Paso],
    cobertura: Dict[int, int],
    cubre: bool,
    tiempo_s: float,
    optimo: Optional[List[int]] = None,
    cota: Optional[float] = None,
    inst: Optional[Instancia] = None,
    optimo_metodo: str = "",
) -> str:
    """Texto de la traza: un renglón por paso, cobertura final y comprobación."""
    lineas = ["Caso: %s" % nombre_caso, "Voraz — traza de elecciones"]
    etq_j = inst.etiqueta_interaccion if inst else str
    con_ids = bool(inst and inst.ids_interaccion)
    for i, p in enumerate(pasos, start=1):
        lineas.append(
            "  Paso %d: interacción %s | categorías nuevas %s | faltan %s"
            % (i, str(p.j) + (" (%s)" % etq_j(p.j) if con_ids else ""),
               _lista(p.nuevas, inst), _lista(p.faltan, inst))
        )
    lineas.append("Cobertura final (categoría -> interacción):")
    for c in sorted(cobertura):
        if inst and inst.ids_categoria:
            nom = inst.nombres_categoria[c - 1] if inst.nombres_categoria else ""
            rotulo = inst.etiqueta_categoria(c) + (" (%s)" % nom if nom else "")
        else:
            rotulo = str(c)
        lineas.append("  categoría %s -> interacción %s" % (rotulo, etq_j(cobertura[c])))
    J = [p.j for p in pasos]
    lineas.append("Interacciones auditadas: %s (%d)" % (J, len(J)) +
                  (": " + ", ".join(etq_j(j) for j in J) if con_ids else ""))
    lineas.append("Cubre todas las categorías: %s" % ("sí" if cubre else "NO"))
    lineas.append("Tiempo: %.6f s" % tiempo_s)
    if optimo is not None:
        lineas.append("Óptimo (%s): %s (%d)" % (optimo_metodo or "fuerza bruta", optimo, len(optimo)) +
                      (": " + ", ".join(etq_j(j) for j in optimo) if con_ids else ""))
        lineas.append("Razón voraz / óptimo: %.4f" % (len(J) / max(len(optimo), 1)))
    if cota is not None:
        lineas.append("Cota H(d): %.4f" % cota)
    return "\n".join(lineas) + "\n"


def escribir_traza(ruta: str, texto: str) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


def formatear_resultado(res: ResultadoCaso) -> str:
    """Texto completo de un caso: traza si es factible, aviso si no lo es."""
    if not res.factible:
        return (
            "Caso: %s\nInstancia NO factible: nadie cubre las categorías %s. "
            "No se ejecutó el voraz.\n" % (res.nombre, sorted(res.sin_cubrir))
        )
    return formatear_traza(res.nombre, res.pasos, res.cobertura, res.cubre,
                           res.tiempo_s, res.optimo, res.cota, res.instancia, res.optimo_metodo)
