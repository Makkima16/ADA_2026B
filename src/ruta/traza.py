"""Escritura de la traza de la Parte 2 (voraz).

Solo formatea y escribe; no calcula nada del algoritmo. Se separa de
`auditoria.py` para poder reutilizarla en la variante ponderada.
"""

from typing import Dict, Iterable, List, Optional

from .auditoria import Paso
from .resolver import ResultadoCaso


def _lista(conjunto: Iterable[int]) -> str:
    return "{" + ", ".join(str(x) for x in sorted(conjunto)) + "}"


def formatear_traza(
    nombre_caso: str,
    pasos: List[Paso],
    cobertura: Dict[int, int],
    cubre: bool,
    tiempo_s: float,
    optimo: Optional[List[int]] = None,
    cota: Optional[float] = None,
) -> str:
    """Texto de la traza: un renglón por paso, cobertura final y comprobación."""
    lineas = ["Caso: %s" % nombre_caso, "Voraz — traza de elecciones"]
    for i, p in enumerate(pasos, start=1):
        lineas.append(
            "  Paso %d: interacción %d | categorías nuevas %s | faltan %s"
            % (i, p.j, _lista(p.nuevas), _lista(p.faltan))
        )
    lineas.append("Cobertura final (categoría -> interacción):")
    for c in sorted(cobertura):
        lineas.append("  categoría %d -> interacción %d" % (c, cobertura[c]))
    J = [p.j for p in pasos]
    lineas.append("Interacciones auditadas: %s (%d)" % (J, len(J)))
    lineas.append("Cubre todas las categorías: %s" % ("sí" if cubre else "NO"))
    lineas.append("Tiempo: %.6f s" % tiempo_s)
    if optimo is not None:
        lineas.append("Óptimo por fuerza bruta: %s (%d)" % (optimo, len(optimo)))
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
                           res.tiempo_s, res.optimo, res.cota)
