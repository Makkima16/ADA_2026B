"""Parte 1: mide las dos tablas de la DP (por presupuesto y por valor) sobre un mismo caso.

Es lo que usa `run_all.py` y el visor para que los dos enfoques queden medidos y comparables,
no solo la DP base. No reemplaza a `aceleracion.resolver.resolver_caso`: lo llama, igual que a
`resolver_caso_valor`, y se limita a decidir cuáles caben en memoria y a juntar los resultados.

Regla de la solución del caso:
* si la tabla por presupuesto cabe, esa es la solución (la DP base de la entrega);
* si no cabe pero la de valor sí, se resuelve solo por valor y la evidencia lo dice;
* si ninguna cabe, no se corre nada y el motivo es que la tabla es demasiado grande.

No lee archivos ni escribe nada. Costo: el de las dos DP, Θ(n·B) y Θ(n·D); el resto es O(n).
"""

from dataclasses import dataclass, replace
from typing import Dict, List, Optional

from aceleracion.aceleracion import MAX_CELDAS_TABLA
from aceleracion.resolver import InstanciaAceleracion, ResultadoCaso, resolver_caso
from aceleracion.traza import formatear_caso

from .dp_por_valor.resolver import resolver_caso_valor
from .dp_por_valor.traza import formatear_caso_valor
from .seleccion import PRESUPUESTO, VALOR, tamanos_de_tablas

NOMBRE_ENFOQUE = {PRESUPUESTO: "DP por presupuesto (base)", VALOR: "DP por valor"}


@dataclass(frozen=True)
class MedidaTabla:
    """Una de las dos tablas: cuántas celdas tendría, si cabe y, si se corrió, su resultado."""

    enfoque: str                              # PRESUPUESTO o VALOR
    celdas: int                               # (n+1)(B+1) o (n+1)(D+1)
    cabe: bool                                # celdas <= MAX_CELDAS_TABLA
    resultado: Optional[ResultadoCaso]        # None si no cabe

    def liviano(self) -> "MedidaTabla":
        """Igual pero sin la tabla (que puede pesar mucho) para guardarlo hasta armar las comparaciones."""
        if self.resultado is None:
            return self
        return replace(self, resultado=replace(self.resultado, tabla=[]))


@dataclass(frozen=True)
class ComparacionP1:
    nombre: str
    n: int
    B: int
    D: int                                    # suma de los ahorros d_i
    presupuesto: MedidaTabla
    valor: MedidaTabla

    @property
    def usada(self) -> Optional[str]:
        """Enfoque que da la solución del caso: la base si cabe; si no, la de valor; si no, ninguno."""
        if self.presupuesto.resultado is not None:
            return PRESUPUESTO
        if self.valor.resultado is not None:
            return VALOR
        return None

    @property
    def resultado(self) -> Optional[ResultadoCaso]:
        medida = {PRESUPUESTO: self.presupuesto, VALOR: self.valor}.get(self.usada)
        return medida.resultado if medida else None

    @property
    def coinciden(self) -> Optional[bool]:
        """¿Las dos tablas dieron el mismo ahorro? None si no se corrieron las dos."""
        if self.presupuesto.resultado is None or self.valor.resultado is None:
            return None
        return self.presupuesto.resultado.ahorro == self.valor.resultado.ahorro

    @property
    def mas_rapida(self) -> Optional[str]:
        if self.coinciden is None:
            return None
        a, b = self.presupuesto.resultado.tiempo_s, self.valor.resultado.tiempo_s
        return PRESUPUESTO if a <= b else VALOR

    def mensaje_no_cabe(self) -> str:
        return ("la tabla es demasiado grande y no cabe: por presupuesto tendría %d celdas, por valor %d "
                "y el límite es %d" % (self.presupuesto.celdas, self.valor.celdas, MAX_CELDAS_TABLA))

    def liviano(self) -> "ComparacionP1":
        return replace(self, presupuesto=self.presupuesto.liviano(), valor=self.valor.liviano())


def resolver_enfoques_p1(inst: InstanciaAceleracion) -> ComparacionP1:
    """Corre cada tabla que quepa en memoria. Lanza ErrorDeEntrada si la instancia no cumple las restricciones."""
    celdas = tamanos_de_tablas(inst)
    medidas = {}
    for enfoque, resolver in ((PRESUPUESTO, resolver_caso), (VALOR, resolver_caso_valor)):
        cabe = celdas[enfoque] <= MAX_CELDAS_TABLA
        medidas[enfoque] = MedidaTabla(enfoque, celdas[enfoque], cabe, resolver(inst) if cabe else None)
    return ComparacionP1(inst.nombre, len(inst.c), inst.B, sum(inst.d), medidas[PRESUPUESTO], medidas[VALOR])


def formatear_solucion_p1(c: ComparacionP1) -> str:
    """Traza de la solución del caso: la de la DP base, o la de valor con el aviso de por qué."""
    if c.usada == PRESUPUESTO:
        return formatear_caso(c.presupuesto.resultado)
    if c.usada == VALOR:
        aviso = ("AVISO: la tabla por presupuesto no cabe (%d celdas > límite %d); este caso se resolvió "
                 "SOLO con la DP por valor (D = %d, %d celdas).\n\n"
                 % (c.presupuesto.celdas, MAX_CELDAS_TABLA, c.D, c.valor.celdas))
        return aviso + formatear_caso_valor(c.valor.resultado)
    return "Caso: %s\nERROR en la Parte 1: %s\n" % (c.nombre, c.mensaje_no_cabe())


def _ms(s: float) -> str:
    return "%.3f" % (s * 1000)


def formatear_enfoques_p1(c: ComparacionP1) -> str:
    """Evidencia de los dos enfoques de un caso: tamaño, resultado y tiempo de cada tabla, y si coinciden."""
    L = ["Caso: %s   (n = %d etapas, B = %d, D = suma de ahorros = %d)" % (c.nombre, c.n, c.B, c.D), "",
         "Límite de celdas por tabla: %d" % MAX_CELDAS_TABLA, ""]
    for m in (c.presupuesto, c.valor):
        L.append("%s: %d celdas, %s" % (NOMBRE_ENFOQUE[m.enfoque], m.celdas, "cabe" if m.cabe else "NO CABE (no se corrió)"))
        if m.resultado is not None:
            r = m.resultado
            L.append("    etapas aceleradas %s | costo %d de B = %d | ahorro %d | duración %d -> %d | tiempo %s ms | válida: %s"
                     % (r.aceleradas, r.costo, r.B, r.ahorro, r.duracion_original, r.duracion_final,
                        _ms(r.tiempo_s), "sí" if r.valida else "NO"))
            if r.optimo_ahorro is not None:
                L.append("    fuerza bruta (n <= 12): ahorro %d (%s)"
                         % (r.optimo_ahorro, "coincide" if r.optimo_ahorro == r.ahorro else "NO COINCIDE"))
    L.append("")
    if c.coinciden is None:
        if c.usada is None:
            L.append("Ninguna tabla cabe: " + c.mensaje_no_cabe() + ".")
        else:
            L.append("Solo se corrió la tabla por %s; la otra no cabe, así que no hay comparación entre las dos." % c.usada)
    else:
        L.append("Las dos tablas %s el mismo ahorro (%d)." % ("dieron" if c.coinciden else "NO dieron", c.presupuesto.resultado.ahorro))
        L.append("Más rápida en este caso: DP por %s. Menos celdas: DP por %s."
                 % (c.mas_rapida, PRESUPUESTO if c.presupuesto.celdas <= c.valor.celdas else VALOR))
    L.append("Solución del caso (la que se reporta en la evidencia de la Parte 1): %s."
             % ("ninguna" if c.usada is None else NOMBRE_ENFOQUE[c.usada]))
    return "\n".join(L) + "\n"


def tabla_enfoques_p1(comparaciones: List[ComparacionP1]) -> str:
    """Markdown con una fila por caso (detalle). El resumen está en `resumen_md_p1`. Solo lee resultados ya calculados."""
    if not comparaciones:
        return ""
    L = ["### Parte 1 — DP por presupuesto y por valor, caso por caso", "",
         "Las dos tablas son exactas: cuando las dos caben deben dar el mismo ahorro. «Celdas» es el tamaño de cada tabla; "
         "«—» = no cabe (límite %d celdas) y no se corrió. La solución del caso es la tabla por presupuesto si cabe; si no, la de valor." % MAX_CELDAS_TABLA, "",
         "| Caso | n | B | D | Celdas presupuesto | Celdas valor | Ahorro presupuesto | Ahorro valor | ¿Coinciden? | Tiempo presupuesto (ms) | Tiempo valor (ms) | Solución del caso |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | --- |"]
    for c in comparaciones:
        p, v = c.presupuesto.resultado, c.valor.resultado
        ok = "—" if c.coinciden is None else ("sí" if c.coinciden else "NO")
        L.append("| %s | %d | %d | %d | %d | %d | %s | %s | %s | %s | %s | %s |"
                 % (c.nombre, c.n, c.B, c.D, c.presupuesto.celdas, c.valor.celdas,
                    "—" if p is None else p.ahorro, "—" if v is None else v.ahorro, ok,
                    "—" if p is None else _ms(p.tiempo_s), "—" if v is None else _ms(v.tiempo_s),
                    "no cabe ninguna" if c.usada is None else ("por " + c.usada)))
    L.append("")
    return "\n".join(L)


REGIONES = ("B menor que D", "B igual a D", "B mayor que D")


def agregar_p1(comparaciones: List[ComparacionP1]) -> Dict:
    """Resume una lista de casos con el mismo formato que `pruebas_aleatorias.experimento` (el motor en memoria).

    Agrupa por la relación entre el presupuesto B y la suma de los ahorros D: con B < D debería convenir la tabla por
    presupuesto y con B > D la de valor. Cuenta cuántas veces cupieron las dos tablas, si dieron lo mismo, si acertaron
    contra la fuerza bruta (n <= 12) y cuántas veces una tabla no cupo.
    """
    regiones = {n: {"casos": 0, "corridas": 0, "celdas_presupuesto": 0, "celdas_valor": 0, "tiempo_presupuesto": 0.0,
                    "tiempo_valor": 0.0, "regla_mas_rapida": 0, "regla_valida": 0} for n in REGIONES}
    recomendado = {PRESUPUESTO: 0, VALOR: 0, "empate": 0, "ninguna": 0}
    ambas = {"corridas": 0, "coinciden": 0}
    fb = {"comparadas": 0, "presupuesto_ok": 0, "valor_ok": 0}
    no_corridas = {PRESUPUESTO: 0, VALOR: 0}
    for c in comparaciones:
        reg = regiones[REGIONES[0] if c.B < c.D else REGIONES[1] if c.B == c.D else REGIONES[2]]
        reg["casos"] += 1
        cp, cv = c.presupuesto.celdas, c.valor.celdas
        if min(cp, cv) > MAX_CELDAS_TABLA:
            recomendado["ninguna"] += 1
        else:
            recomendado["empate" if cp == cv else (VALOR if cv < cp else PRESUPUESTO)] += 1
        for medida in (c.presupuesto, c.valor):
            if medida.resultado is None:
                no_corridas[medida.enfoque] += 1
        p, v = c.presupuesto.resultado, c.valor.resultado
        if p is not None and v is not None:
            ambas["corridas"] += 1
            ambas["coinciden"] += p.ahorro == v.ahorro
            reg["corridas"] += 1
            reg["celdas_presupuesto"] += cp
            reg["celdas_valor"] += cv
            reg["tiempo_presupuesto"] += p.tiempo_s
            reg["tiempo_valor"] += v.tiempo_s
            if cp != cv:
                reg["regla_valida"] += 1
                mas_rapida = PRESUPUESTO if p.tiempo_s < v.tiempo_s else VALOR
                reg["regla_mas_rapida"] += mas_rapida == (PRESUPUESTO if cp < cv else VALOR)
        optimo = next((r.optimo_ahorro for r in (p, v) if r is not None and r.optimo_ahorro is not None), None)
        if optimo is not None:
            fb["comparadas"] += 1
            fb["presupuesto_ok"] += p is not None and p.ahorro == optimo
            fb["valor_ok"] += v is not None and v.ahorro == optimo
    return {"parametros": {"instancias": len(comparaciones)}, "hechas": len(comparaciones), "detenido_por_tiempo": False,
            "recomendado": recomendado, "ambas": ambas, "fuerza_bruta": fb, "no_corridas": no_corridas,
            "regiones": regiones, "limite_celdas": MAX_CELDAS_TABLA,
            "solo_valor": sum(c.usada == VALOR for c in comparaciones),
            "ninguna_cabe": sum(c.usada is None for c in comparaciones)}


def resumen_md_p1(agg: Dict) -> str:
    """Markdown del resumen de la Parte 1: qué pasó con las dos tablas y la tabla por relación entre B y D."""
    if not agg or not agg["hechas"]:
        return ""
    a, fb = agg["ambas"], agg["fuerza_bruta"]
    L = ["### Parte 1 — las dos tablas de la DP", "",
         "- **%d casos.** Las dos tablas cupieron en %d y dieron el mismo ahorro en %d (debe ser siempre: las dos son exactas)." % (agg["hechas"], a["corridas"], a["coinciden"]),
         "- **Solo por valor:** %d casos (la tabla por presupuesto no cabe). **Ninguna cabe:** %d (se informa que la tabla es demasiado grande)." % (agg["solo_valor"], agg["ninguna_cabe"])]
    if fb["comparadas"]:
        L.append("- **Contra la fuerza bruta (n ≤ 12), %d casos:** por presupuesto acertó %d, por valor acertó %d." % (fb["comparadas"], fb["presupuesto_ok"], fb["valor_ok"]))
    L += ["", "| Relación | Casos | Con las dos tablas | Celdas (presupuesto) | Celdas (valor) | Tiempo presupuesto (ms) | Tiempo valor (ms) | La de menos celdas fue más rápida |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: |"]
    for nombre in REGIONES:
        g = agg["regiones"][nombre]
        k = g["corridas"] or 1
        regla = "%d de %d" % (g["regla_mas_rapida"], g["regla_valida"]) if g["regla_valida"] else "—"
        L.append("| %s | %d | %d | %s | %s | %s | %s | %s |" % (
            nombre, g["casos"], g["corridas"],
            "—" if not g["corridas"] else "%.0f" % (g["celdas_presupuesto"] / k), "—" if not g["corridas"] else "%.0f" % (g["celdas_valor"] / k),
            "—" if not g["corridas"] else _ms(g["tiempo_presupuesto"] / k), "—" if not g["corridas"] else _ms(g["tiempo_valor"] / k), regla))
    L.append("")
    return "\n".join(L)
