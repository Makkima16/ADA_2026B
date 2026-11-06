"""Variante 1 con opciones de auditoría (parcial y completa): depuración y texto de la evidencia.

El voraz ponderado (`ponderada.py`) no se toca: corre sobre la lista de opciones que arma
`lectura_ponderada.leer_opciones`, donde cada opción es un conjunto con costo. Como las opciones
parcial y completa de una misma interacción son alternativas (se audita la interacción una vez),
puede pasar que el voraz elija la parcial y, más tarde, la completa de la misma interacción. La
cota H(d) se mantiene (el óptimo nunca elige las dos, porque la parcial está contenida en la
completa), pero pagar dos veces por auditar lo mismo no tiene sentido. Por eso, al reportar,
se deja solo la completa y el costo es el real. Esta depuración no cambia la cobertura (la parcial
está contenida en la completa; el lector lo valida) y nunca sube el costo.

No lee archivos ni escribe nada. Costo: O(|J|).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .lectura_ponderada import OpcionesAuditoria, TIPO_COMPLETA, TIPO_PARCIAL
from .resolver_ponderada import ResultadoPonderado


@dataclass(frozen=True)
class Depuracion:
    conservadas: List[int]         # opciones que se reportan, en el orden en que las eligió el voraz
    descartadas: List[int]         # parciales que se quitaron porque se eligió también la completa
    costo_real: float              # suma de los costos de las conservadas
    costo_voraz: float             # lo que sumó el voraz antes de depurar

    @property
    def ahorro(self) -> float:
        return self.costo_voraz - self.costo_real


def depurar(J: Sequence[int], opciones: OpcionesAuditoria) -> Depuracion:
    """Quita las parciales cuya interacción también quedó elegida con la completa."""
    elegidas = set(J)
    descartadas = [k for k in J if opciones.tipo[k - 1] == TIPO_PARCIAL
                   and opciones.interaccion[k - 1] in elegidas      # la completa de esa interacción tiene índice = interacción
                   and opciones.tipo[opciones.interaccion[k - 1] - 1] == TIPO_COMPLETA]
    conservadas = [k for k in J if k not in descartadas]
    return Depuracion(conservadas, descartadas, sum(opciones.costos[k - 1] for k in conservadas),
                      sum(opciones.costos[k - 1] for k in J))


def _g(x) -> str:
    return "%g" % x


def formatear_opciones(rv: ResultadoPonderado, opciones: OpcionesAuditoria, dep: Depuracion) -> str:
    """Bloque que se agrega a la traza de la variante: opciones, elecciones del voraz y costo real."""
    inst = opciones.instancia
    etq = inst.etiqueta_interaccion
    m = len(opciones.costos)
    parciales = opciones.tipo.count(TIPO_PARCIAL)
    L = ["", "-" * 78, "Opciones de auditoría"]
    if opciones.version == "solo completas":
        L += ["Versión SOLO COMPLETAS: un costo a_j por interacción, la definición de la variante 1. Las %d variaciones parciales del archivo "
              "no se usan aquí; se miden aparte, en la versión con parciales." % opciones.n_parciales,
              "Interacciones: %d | opciones: %d" % (opciones.n, m)]
    else:
        L.append("Interacciones: %d | opciones: %d (%d completas, %d parciales)" % (opciones.n, m, m - parciales, parciales))
        if parciales:
            L.append("Versión CON PARCIALES (extensión): el voraz ponderado (sin cambios) eligió entre las %d opciones; cada opción es un conjunto con su costo." % m)
        else:
            L.append("Este caso trae una sola opción de auditoría por interacción (sin parciales).")
    if not rv.factible:
        return "\n".join(L) + "\n"
    L.append("Opciones elegidas por el voraz: %s" % ", ".join(etq(k) for k in rv.J))
    if dep.descartadas:
        L.append("Depuración: se eligió también la completa de %s; la parcial se quita (no se audita dos veces la misma interacción)."
                 % ", ".join(etq(k) for k in dep.descartadas))
    L.append("Interacciones a auditar: %s" % ", ".join(etq(k) for k in dep.conservadas))
    L.append("Costo del voraz: %s | Costo real tras depurar: %s | Ahorro por depurar: %s"
             % (_g(dep.costo_voraz), _g(dep.costo_real), _g(dep.ahorro)))
    if rv.optimo_costo is not None:
        L.append("Óptimo sobre las %d opciones (%s): %s | razón costo real / óptimo: %.4f"
                 % (m, rv.optimo_metodo or "fuerza bruta", _g(rv.optimo_costo), dep.costo_real / rv.optimo_costo))
    else:
        L.append("Óptimo: no se calcula (más de 12 opciones y r > 16)")
    return "\n".join(L) + "\n"


def agregar_variante(items: Sequence[Tuple[ResultadoPonderado, Depuracion, OpcionesAuditoria, Optional[float]]]) -> Dict:
    """Resume la variante en varios casos. Cada ítem es (resultado, depuración, opciones, costo del J de la Parte 2).

    Cuenta los casos con parciales y con depuración, cuántas veces el voraz ponderado llegó al óptimo (donde hay fuerza
    bruta: hasta 12 opciones), la razón máxima, cuántas veces superó H(d) y cómo se compara contra el J de la Parte 2.
    """
    factibles = [i for i in items if i[0].factible]
    con_opt = [i for i in factibles if i[0].optimo_costo is not None]
    razones = [i[1].costo_real / i[0].optimo_costo for i in con_opt]
    vs = [(i[3] - i[1].costo_real) / i[3] for i in factibles if i[3]]
    return {
        "casos": len(factibles), "con_parcial": sum(i[2].hay_parcial for i in factibles),
        "con_depuracion": sum(bool(i[1].descartadas) for i in factibles), "con_optimo": len(con_opt),
        "optimo_ok": sum(abs(r - 1) < 1e-9 for r in razones), "razon_max": max(razones, default=0.0),
        "viola_cota": sum(r > i[0].cota + 1e-9 for r, i in zip(razones, con_opt)),
        "mas_barata": sum(x > 1e-9 for x in vs), "igual": sum(abs(x) <= 1e-9 for x in vs), "mas_cara": sum(x < -1e-9 for x in vs),
        "ahorro_medio_pct": 100.0 * sum(vs) / len(vs) if vs else 0.0,
    }


def resumen_md_variante(agg: Optional[Dict], version: str = "solo completas", contra: str = "el J de la Parte 2") -> str:
    """Markdown del resumen de una versión de la variante (varios casos). `contra` es con qué se compara el costo."""
    if not agg or not agg["casos"]:
        return ""
    L = ["### Variante 1 — voraz ponderado, %s" % version, "",
         "- **%d casos**%s." % (agg["casos"], ("; en %d el voraz eligió la parcial y la completa de una misma interacción y se depuró" % agg["con_depuracion"]) if agg["con_parcial"] else "")]
    if agg["con_optimo"]:
        L.append("- **Contra el mínimo real** (%d casos con mínimo calculado): llegó al mínimo en %d; razón máxima %.3f; casos que superan H(d): %d."
                 % (agg["con_optimo"], agg["optimo_ok"], agg["razon_max"], agg["viola_cota"]))
    else:
        L.append("- No se pudo calcular el mínimo real en ningún caso (hay más de 12 opciones y r > 16).")
    L += ["- **Contra %s:** salió más barata en %d casos (ahorro medio %.0f %%), igual en %d y más cara en %d."
          % (contra, agg["mas_barata"], agg["ahorro_medio_pct"], agg["igual"], agg["mas_cara"]), ""]
    return "\n".join(L)
