"""Elección automática entre la DP base (por presupuesto) y la DP por valor.

La DP base llena (n+1)·(B+1) celdas y la DP por valor (n+1)·(D+1), con D = Σ d_i. Se elige la
tabla con menos celdas (con empate, la base). Si ni la una ni la otra caben en el tope de
memoria (`MAX_CELDAS_TABLA`), se avisa con un error y no se corre nada.

No modifica ninguna de las dos DP: solo decide cuál llamar.
"""

from typing import Dict, Tuple

from aceleracion.aceleracion import ErrorDeEntrada, MAX_CELDAS_TABLA
from aceleracion.resolver import InstanciaAceleracion, ResultadoCaso, resolver_caso

from .dp_por_valor.resolver import resolver_caso_valor

PRESUPUESTO = "presupuesto"
VALOR = "valor"


def tamanos_de_tablas(inst: InstanciaAceleracion) -> Dict[str, int]:
    """Celdas de cada tabla para la instancia: {'presupuesto': (n+1)(B+1), 'valor': (n+1)(D+1)}."""
    n = len(inst.c)
    return {PRESUPUESTO: (n + 1) * (inst.B + 1), VALOR: (n + 1) * (sum(inst.d) + 1)}


def elegir_enfoque(inst: InstanciaAceleracion) -> str:
    """'presupuesto' o 'valor', el de la tabla más chica. Lanza ErrorDeEntrada si ninguna cabe."""
    celdas = tamanos_de_tablas(inst)
    if min(celdas.values()) > MAX_CELDAS_TABLA:
        raise ErrorDeEntrada(
            "ninguna tabla cabe: por presupuesto tendría %d celdas, por valor %d y el límite es %d"
            % (celdas[PRESUPUESTO], celdas[VALOR], MAX_CELDAS_TABLA))
    return VALOR if celdas[VALOR] < celdas[PRESUPUESTO] else PRESUPUESTO


def resolver_auto(inst: InstanciaAceleracion, comparar_con_optimo: bool = True) -> Tuple[ResultadoCaso, str]:
    """Resuelve con la DP de la tabla más chica. Devuelve (resultado, enfoque usado)."""
    enfoque = elegir_enfoque(inst)
    resolver = resolver_caso_valor if enfoque == VALOR else resolver_caso
    return resolver(inst, comparar_con_optimo), enfoque
