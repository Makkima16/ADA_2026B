"""Escritura de la traza de la Parte 2 (voraz).

Solo formatea y escribe; no calcula nada del algoritmo. Se separa de
`auditoria.py` para poder reutilizarla en la variante ponderada.

Anotación de costos: C (k) es una línea de costo constante con k operaciones
elementales; O(...) es el costo asintótico de la línea o de la función.
"""

from typing import Dict, Iterable, List, Optional

from .auditoria import Paso
from .resolver import ResultadoCaso


def _lista(conjunto: Iterable[int]) -> str:
    return "{" + ", ".join(str(x) for x in sorted(conjunto)) + "}"   # O(k log k): k = |conjunto| <= r


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
    lineas = ["Caso: %s" % nombre_caso, "Voraz — traza de elecciones"]  # C (2): lista inicial
    for i, p in enumerate(pasos, start=1):                             # |J|+1 pruebas de ciclo; |J| <= min(n, r)
        lineas.append(
            "  Paso %d: interacción %d | categorías nuevas %s | faltan %s"
            % (i, p.j, _lista(p.nuevas), _lista(p.faltan))
        )                                                              # |J| veces · O(r) por formatear conjuntos -> O(n·r)
    lineas.append("Cobertura final (categoría -> interacción):")       # C (1)
    for c in sorted(cobertura):                                        # O(r log r): ordenar y recorrer a lo sumo r categorías
        lineas.append("  categoría %d -> interacción %d" % (c, cobertura[c]))  # r veces · C (1) -> O(r)
    J = [p.j for p in pasos]                                           # O(|J|): extraer los índices elegidos
    lineas.append("Interacciones auditadas: %s (%d)" % (J, len(J)))    # C (1)
    lineas.append("Cubre todas las categorías: %s" % ("sí" if cubre else "NO"))  # C (1)
    lineas.append("Tiempo: %.6f s" % tiempo_s)                         # C (1)
    if optimo is not None:                                             # C (1): comparación
        lineas.append("Óptimo por fuerza bruta: %s (%d)" % (optimo, len(optimo)))  # C (1)
        lineas.append("Razón voraz / óptimo: %.4f" % (len(J) / max(len(optimo), 1)))  # C (1)
    if cota is not None:                                               # C (1): comparación
        lineas.append("Cota H(d): %.4f" % cota)                        # C (1)
    return "\n".join(lineas) + "\n"                                    # O(L): unir las L líneas de la traza


def escribir_traza(ruta: str, texto: str) -> None:
    with open(ruta, "w", encoding="utf-8") as f:                       # C: abrir el archivo (una vez)
        f.write(texto)                                                 # O(L): escribir los L caracteres del texto


def formatear_resultado(res: ResultadoCaso) -> str:
    """Texto completo de un caso: traza si es factible, aviso si no lo es."""
    if not res.factible:                                               # C (1): comparación
        return (
            "Caso: %s\nInstancia NO factible: nadie cubre las categorías %s. "
            "No se ejecutó el voraz.\n" % (res.nombre, sorted(res.sin_cubrir))
        )                                                              # O(r): camino no factible
    return formatear_traza(res.nombre, res.pasos, res.cobertura, res.cubre,
                           res.tiempo_s, res.optimo, res.cota)         # O(n·r): delega en formatear_traza
