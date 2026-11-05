"""Escritura de la traza de la Parte 2 (voraz).

Solo formatea y escribe; no calcula nada del algoritmo. Se separa de
`auditoria.py` para poder reutilizarla en la variante ponderada.

Anotación de costos: C (k) es una línea de costo constante con k operaciones
elementales; O(...) es el costo asintótico de la línea o de la función.
"""

from typing import Dict, Iterable, List, Optional

from .auditoria import Paso
from .resolver import Instancia, ResultadoCaso


def _lista(conjunto: Iterable[int], inst: Optional[Instancia] = None) -> str:
    """Conjunto de categorías en orden numérico; con nombres (R01...) si la instancia los trae."""
    nombre = inst.etiqueta_categoria if inst else str                # C (1)
    return "{" + ", ".join(nombre(x) for x in sorted(conjunto)) + "}"   # O(k log k): k = |conjunto| <= r


def formatear_traza(
    nombre_caso: str,
    pasos: List[Paso],
    cobertura: Dict[int, int],
    cubre: bool,
    tiempo_s: float,
    optimo: Optional[List[int]] = None,
    cota: Optional[float] = None,
    inst: Optional[Instancia] = None,
) -> str:
    """Texto de la traza: un renglón por paso, cobertura final y comprobación."""
    lineas = ["Caso: %s" % nombre_caso, "Voraz — traza de elecciones"]  # C (2): lista inicial
    etq_j = inst.etiqueta_interaccion if inst else str                 # C (1): nombre de interacción (número si no hay ids)
    con_ids = bool(inst and inst.ids_interaccion)                      # C (1): ¿el archivo trae ids?
    for i, p in enumerate(pasos, start=1):                             # |J|+1 pruebas de ciclo; |J| <= min(n, r)
        lineas.append(
            "  Paso %d: interacción %s | categorías nuevas %s | faltan %s"
            % (i, str(p.j) + (" (%s)" % etq_j(p.j) if con_ids else ""),
               _lista(p.nuevas, inst), _lista(p.faltan, inst))
        )                                                              # |J| veces · O(r) por formatear conjuntos -> O(n·r)
    lineas.append("Cobertura final (categoría -> interacción):")       # C (1)
    for c in sorted(cobertura):                                        # O(r log r): ordenar y recorrer a lo sumo r categorías
        if inst and inst.ids_categoria:                                # C (1): ¿hay nombres de categoría?
            nom = inst.nombres_categoria[c - 1] if inst.nombres_categoria else ""   # C (2)
            rotulo = inst.etiqueta_categoria(c) + (" (%s)" % nom if nom else "")    # C (2)
        else:
            rotulo = str(c)                                            # C (1)
        lineas.append("  categoría %s -> interacción %s" % (rotulo, etq_j(cobertura[c])))  # r veces · C (1) -> O(r)
    J = [p.j for p in pasos]                                           # O(|J|): extraer los índices elegidos
    lineas.append("Interacciones auditadas: %s (%d)" % (J, len(J)) +
                  (": " + ", ".join(etq_j(j) for j in J) if con_ids else ""))  # O(|J|)
    lineas.append("Cubre todas las categorías: %s" % ("sí" if cubre else "NO"))  # C (1)
    lineas.append("Tiempo: %.6f s" % tiempo_s)                         # C (1)
    if optimo is not None:                                             # C (1): comparación
        lineas.append("Óptimo por fuerza bruta: %s (%d)" % (optimo, len(optimo)) +
                      (": " + ", ".join(etq_j(j) for j in optimo) if con_ids else ""))  # O(|óptimo|)
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
                           res.tiempo_s, res.optimo, res.cota, res.instancia)  # O(n·r): delega en formatear_traza
