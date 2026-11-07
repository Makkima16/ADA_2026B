"""Parte 2: mide todos los enfoques del voraz sobre un mismo caso.

Corre las ocho combinaciones de ingredientes (voraz base, esenciales, rareza, parejas y sus
combinaciones, la última es «todo junto») y, si n <= 12, las compara con el óptimo por fuerza
bruta. Es lo que usan `run_all.py` y el visor para que los enfoques queden medidos y comparables,
no solo el voraz base. No reemplaza a `auditoria.resolver.resolver_caso`: aquel da la solución
base de la entrega y este da la comparación.

No lee archivos ni escribe nada. Costo de un caso: la suma de las ocho combinaciones, la más cara
(parejas) es O(n²·r·min(n, r)); el mínimo real (fuerza bruta con n <= 12; si no, subconjuntos de categorías con r <= 16) queda fuera de la medición de tiempo.
"""

from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Sequence

from auditoria.auditoria import cota_aproximacion, cubre_todo, verificar_factibilidad
from auditoria.verificacion_exacta import optimo_de_referencia
from auditoria.enfoques.comparacion.ablacion import COMBINACIONES, clave, correr_combinacion
from auditoria.resolver import Instancia

# Nombre en el CSV y el texto: (clave de ablacion, nombre legible, identificador corto).
IDENTIFICADORES = {
    "": "voraz", "e": "esenciales", "r": "rareza", "p": "parejas",
    "er": "esenciales_rareza", "ep": "esenciales_parejas", "rp": "rareza_parejas", "erp": "todo",
}
NOMBRES = {clave(e, ra, pa): nombre for nombre, e, ra, pa in COMBINACIONES}


# Etiquetas de densidad de las instancias (los umbrales quedan entre 0,25 / 0,33 / 0,40, los valores del generador).
FAMILIAS = ("ralo", "medio", "denso")
UMBRAL_RALO, UMBRAL_DENSO = 0.29, 0.365


def familia_de(densidad: float) -> str:
    return "ralo" if densidad < UMBRAL_RALO else ("medio" if densidad < UMBRAL_DENSO else "denso")


@dataclass(frozen=True)
class MedidaVoraz:
    clave: str                       # '', e, r, p, er, ep, rp o erp
    nombre: str
    J: List[int]                     # interacciones elegidas, en orden de elección
    pasos: list
    esenciales: Optional[List[int]]  # interacciones esenciales (si el ingrediente está encendido)
    tiempo_s: float
    cubre: bool                      # comprobación independiente de la cobertura

    @property
    def identificador(self) -> str:
        return IDENTIFICADORES[self.clave]


@dataclass(frozen=True)
class ComparacionP2:
    nombre: str
    n: int
    r: int
    factible: bool
    sin_cubrir: frozenset
    medidas: List[MedidaVoraz]
    optimo: Optional[List[int]]      # mínimo real (fuerza bruta o subconjuntos de categorías); None si no se puede calcular
    cota: float                      # H(d)
    instancia: Optional[Instancia] = None
    densidad: float = 0.0            # suma de |S_j| entre n·r: qué tan «llena» está la matriz de incidencia

    @property
    def familia(self) -> str:
        return familia_de(self.densidad)

    @property
    def base(self) -> Optional[MedidaVoraz]:
        return next((m for m in self.medidas if m.clave == ""), None)

    def razon(self, m: MedidaVoraz) -> Optional[float]:
        return None if self.optimo is None else len(m.J) / max(len(self.optimo), 1)

    def liviano(self) -> "ComparacionP2":
        """Sin las trazas (pesan): lo que hace falta para armar las tablas de todos los casos."""
        return replace(self, medidas=[replace(m, pasos=[]) for m in self.medidas])


def resolver_enfoques_p2(inst: Instancia, optimo: Optional[Sequence[int]] = None,
                         comparar_con_optimo: bool = True) -> ComparacionP2:
    """Corre las ocho combinaciones. `optimo` permite reusar el que ya calculó la solución base."""
    n = len(inst.S)
    cota = cota_aproximacion(inst.S)
    factible, sin_cubrir = verificar_factibilidad(inst.r, inst.S)
    if not factible:
        return ComparacionP2(inst.nombre, n, inst.r, False, frozenset(sin_cubrir), [], None, cota, inst)
    densidad = sum(len(s) for s in inst.S) / (n * inst.r) if n and inst.r else 0.0
    medidas = []
    for nombre, e, ra, pa in COMBINACIONES:
        r = correr_combinacion(inst.r, inst.S, e, ra, pa)
        medidas.append(MedidaVoraz(clave(e, ra, pa), nombre, r["J"], r["pasos"], r["esenciales"], r["tiempo_s"],
                                   cubre_todo(inst.r, inst.S, r["J"])))
    if optimo is None and comparar_con_optimo:
        ref = optimo_de_referencia(inst.r, inst.S)      # fuerza bruta (n <= 12) o subconjuntos de categorías (r <= 16)
        if ref is not None:
            optimo = ref[1]
    return ComparacionP2(inst.nombre, n, inst.r, True, frozenset(), medidas,
                         None if optimo is None else list(optimo), cota, inst, densidad)


def _etiqueta(inst: Optional[Instancia], j: int) -> str:
    return str(j) + (" (%s)" % inst.etiqueta_interaccion(j) if inst and inst.ids_interaccion else "")


def _categorias(inst: Optional[Instancia], conjunto) -> str:
    nombre = inst.etiqueta_categoria if inst else str
    return "{" + ", ".join(nombre(x) for x in sorted(conjunto)) + "}"


def _ms(s: float) -> str:
    return "%.3f" % (s * 1000)


def formatear_enfoques_p2(c: ComparacionP2) -> str:
    """Evidencia de todos los enfoques de un caso: la traza de cada uno y la comparación con el óptimo."""
    inst = c.instancia
    L = ["Caso: %s   (n = %d interacciones, r = %d categorías)" % (c.nombre, c.n, c.r), ""]
    if not c.factible:
        L.append("El caso no es factible: ninguna interacción cubre %s. No se corrió ningún enfoque."
                 % _categorias(inst, c.sin_cubrir))
        return "\n".join(L) + "\n"
    L.append("Cota H(d): %.4f" % c.cota)
    if c.optimo is not None:
        L.append("Óptimo exacto: %d interacciones %s" % (len(c.optimo), c.optimo))
    else:
        L.append("Óptimo exacto: no se calcula (n > 12 y r > 16)")
    base = c.base
    for m in c.medidas:
        L += ["", "=" * 78, "Enfoque: %s   [clave %s]" % (m.nombre, m.clave or "voraz base"), "=" * 78]
        if m.esenciales is not None:
            L.append("Interacciones esenciales (únicas de alguna categoría): %s"
                     % (", ".join(_etiqueta(inst, j) for j in m.esenciales) if m.esenciales else "ninguna"))
        for i, p in enumerate(m.pasos, start=1):
            par = getattr(p, "par", None)
            extra = " | pareja (%s, %s)" % par if par and par[0] != par[1] else ""
            L.append("  Paso %d: interacción %s | categorías nuevas %s | faltan %s%s"
                     % (i, _etiqueta(inst, p.j), _categorias(inst, p.nuevas), _categorias(inst, p.faltan), extra))
        resumen = "Interacciones auditadas: %s (%d) | cubre todo: %s | tiempo %s ms" % (
            m.J, len(m.J), "sí" if m.cubre else "NO", _ms(m.tiempo_s))
        if c.optimo is not None:
            resumen += " | razón al óptimo %.3f" % c.razon(m)
        L.append(resumen)
        if base is not None and m is not base:
            d = len(m.J) - len(base.J)
            L.append("Contra el voraz base: %s" % ("igual" if d == 0 else ("%d interacciones menos (mejor)" % -d if d < 0
                                                                         else "%d interacciones más (peor)" % d)))
    return "\n".join(L) + "\n"


def tabla_enfoques_p2(comparaciones: List[ComparacionP2]) -> str:
    """Markdown con el tamaño de J de cada enfoque y el tiempo, caso por caso (detalle). El resumen está en `resumen_md_p2`."""
    validas = [c for c in comparaciones if c.factible]
    if not validas:
        return ""
    orden = [(clave(e, ra, pa), nombre) for nombre, e, ra, pa in COMBINACIONES]
    L = ["### Parte 2 — tamaño de J de cada enfoque, caso por caso", "",
         "Cada celda es el número de interacciones que eligió el enfoque; menos es mejor. «Óptimo» es el mínimo real por fuerza "
         "bruta (solo con n ≤ 12). Las claves son los ingredientes: e = esenciales, r = rareza, p = parejas; «todo» = los tres.", "",
         "| Caso | n | r | H(d) | Óptimo | " + " | ".join(n for _, n in orden) + " |",
         "| --- | ---: | ---: | ---: | ---: | " + " | ".join("---:" for _ in orden) + " |"]
    for c in validas:
        celdas = [str(len(next(x for x in c.medidas if x.clave == k).J)) for k, _ in orden]
        L.append("| %s | %d | %d | %.3f | %s | %s |" % (c.nombre, c.n, c.r, c.cota,
                                                       "—" if c.optimo is None else len(c.optimo), " | ".join(celdas)))
    L += ["", "### Parte 2 — tiempo de cada enfoque (ms), caso por caso", "",
          "| Caso | " + " | ".join(n for _, n in orden) + " |", "| --- | " + " | ".join("---:" for _ in orden) + " |"]
    for c in validas:
        L.append("| %s | %s |" % (c.nombre, " | ".join(_ms(next(x for x in c.medidas if x.clave == k).tiempo_s) for k, _ in orden)))
    L.append("")
    return "\n".join(L)


def agregar_p2(comparaciones: List[ComparacionP2], ejemplos: int = 3) -> Dict:
    """Resume una lista de casos con el mismo formato que `ablacion_detalle` (el motor en memoria).

    Por enfoque: cuántas veces no llegó al mínimo (solo donde hay óptimo, n <= 12), cuántas mejora, empata o empeora al
    voraz base, la razón máxima al óptimo, cuántas veces superó H(d) veces el óptimo y el tiempo medio. `por_familia`
    desglosa por densidad y `ejemplos` guarda, por enfoque, los casos más chicos donde empeoró al voraz base.
    """
    validas = [c for c in comparaciones if c.factible]
    con_opt = [c for c in validas if c.optimo is not None]
    salida = {nombre: {"clave": clave(e, ra, pa), "no_optimo": 0, "mejora": 0, "igual": 0, "peor": 0,
                       "razon_max": 0.0, "viola_cota": 0, "tiempo_medio_s": 0.0} for nombre, e, ra, pa in COMBINACIONES}
    por_familia = {f: {nombre: 0 for nombre, *_ in COMBINACIONES} for f in FAMILIAS}
    casos_por_familia = {f: 0 for f in FAMILIAS}
    peores: Dict[str, list] = {nombre: [] for nombre, *_ in COMBINACIONES}
    fallan = 0
    for c in validas:
        casos_por_familia[c.familia] += 1
        base = len(c.base.J)
        for (nombre, e, ra, pa), m in zip(COMBINACIONES, c.medidas):
            d, tam = salida[nombre], len(m.J)
            d["tiempo_medio_s"] += m.tiempo_s / len(validas)
            fallan += not m.cubre
            if c.optimo is not None:
                opt = len(c.optimo)
                d["no_optimo"] += tam > opt
                por_familia[c.familia][nombre] += tam > opt
                d["razon_max"] = max(d["razon_max"], tam / opt)
                d["viola_cota"] += tam > c.cota * opt + 1e-9
            if nombre != "Voraz base":
                d["mejora" if tam < base else "peor" if tam > base else "igual"] += 1
                if tam > base:
                    peores[nombre].append((c.n * c.r, {
                        "caso": c.nombre, "archivo": c.nombre + "_parte2_enfoques.txt", "n": c.n, "r": c.r, "familia": c.familia,
                        "voraz": list(c.base.J), "combinacion": list(m.J), "optimo": None if c.optimo is None else list(c.optimo)}))
    salida["instancias"] = len(validas)
    salida["con_optimo"] = len(con_opt)
    salida["por_familia"] = por_familia
    salida["casos_por_familia"] = casos_por_familia
    salida["fallan_cobertura"] = fallan
    salida["ejemplos"] = {nombre: [x for _, x in sorted(lista, key=lambda y: y[0])[:ejemplos]]
                          for nombre, lista in peores.items() if lista}
    return salida


def resumen_md_p2(agg: Dict) -> str:
    """Markdown del resumen de la Parte 2: una fila por enfoque y el desglose por densidad."""
    if not agg or not agg["instancias"]:
        return ""
    L = ["### Parte 2 — los ocho enfoques del voraz", "",
         "- **%d casos factibles**, %d con mínimo real (fuerza bruta con n ≤ 12; si no, subconjuntos de categorías con r ≤ 16). Comprobación independiente de la cobertura: "
         "%d de %d ejecuciones no cubrieron todas las categorías (debe ser 0)." % (
             agg["instancias"], agg["con_optimo"], agg["fallan_cobertura"], agg["instancias"] * len(COMBINACIONES)),
         "", "«No llegó al mínimo» cuenta los casos con óptimo en que el enfoque usó más interacciones que el mínimo. "
         "«Contra el voraz base» cuenta en cuántos casos usó menos (mejor), igual o más (peor).", "",
         "| Enfoque | No llegó al mínimo | Contra el voraz base (mejor / igual / peor) | Razón máxima al óptimo | Pasó de H(d) | Tiempo medio (ms) |",
         "| --- | :---: | :---: | ---: | ---: | ---: |"]
    for nombre, *_ in COMBINACIONES:
        d = agg[nombre]
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            nombre, "—" if not agg["con_optimo"] else "%d de %d" % (d["no_optimo"], agg["con_optimo"]),
            "— (es la referencia)" if nombre == "Voraz base" else "%d / %d / %d" % (d["mejora"], d["igual"], d["peor"]),
            "—" if not agg["con_optimo"] else "%.3f" % d["razon_max"],
            "—" if not agg["con_optimo"] else str(d["viola_cota"]), _ms(d["tiempo_medio_s"])))
    L += ["", "No llegó al mínimo, según la densidad (casos con óptimo de cada una):", "",
          "| Enfoque | " + " | ".join("%s (%d casos)" % (f, agg["casos_por_familia"][f]) for f in FAMILIAS) + " |",
          "| --- | " + " | ".join(":---:" for _ in FAMILIAS) + " |"]
    for nombre, *_ in COMBINACIONES:
        L.append("| %s | %s |" % (nombre, " | ".join(str(agg["por_familia"][f][nombre]) for f in FAMILIAS)))
    L.append("")
    return "\n".join(L)
