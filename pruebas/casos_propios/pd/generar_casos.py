#!/usr/bin/env python3
"""Genera los casos propios de la Parte 1 (programación dinámica) en esta carpeta.

Formato: el JSON del ejemplo de la profesora (`parametros.presupuesto_aceleracion_B` y `etapas` con
`id`, `duracion_normal`, `costo_aceleracion` y `reduccion_tiempo_si_acelera`), más una clave
`descripcion` (el lector la ignora) con qué prueba el caso y el resultado calculado con el código del
proyecto. Todo con semilla fija: mismo código = mismos archivos.

Uso (desde la raíz del proyecto):

    python3 pruebas/casos_propios/pd/generar_casos.py [--salida CARPETA]

Por defecto escribe en la misma carpeta del script, junto con un README.md con la tabla de casos.
"""

import argparse
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from aceleracion.aceleracion import MAX_CELDAS_TABLA, ErrorDeEntrada, resolver  # noqa: E402
from aceleracion.enfoques.dp_por_valor.dp_por_valor import resolver_valor  # noqa: E402
from aceleracion.enfoques.seleccion import elegir_enfoque, tamanos_de_tablas  # noqa: E402
from aceleracion.resolver import InstanciaAceleracion  # noqa: E402
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA, fuerza_bruta  # noqa: E402

CASO_DE_ERROR = "19_n400_ninguna_tabla_cabe"
CELDAS_PARA_CRUZAR = 1_000_000   # solo se corre la otra DP si su tabla tiene a lo sumo estas celdas


def aleatorio(semilla, n, rango_c, rango_d, extra_t=20):
    """n etapas (t, c, d) con c y d en los rangos dados y 0 <= d <= t. Semilla fija."""
    rng = random.Random(semilla)
    c = [rng.randint(*rango_c) for _ in range(n)]
    d = [rng.randint(*rango_d) for _ in range(n)]
    t = [x + rng.randint(0, extra_t) for x in d]
    return list(zip(t, c, d))


# (nombre, qué prueba, etapas (t, c, d), B). B puede ser un número o una función de las etapas.
def _casos():
    fijas = [(10, 3, 4), (8, 2, 5), (7, 4, 3), (9, 5, 6), (6, 1, 2)]
    return [
        ("01_b_cero", "Presupuesto B = 0: no cabe ninguna etapa con costo positivo; el ahorro es 0.", fijas, 0),
        ("02_todo_cabe", "El presupuesto sobra (B >= suma de costos): se aceleran todas las etapas y no hay nada que elegir.",
         fijas, 100),
        ("03_nada_cabe", "Todas las etapas cuestan más que B: ninguna se puede acelerar.",
         [(10, 30, 4), (8, 25, 5), (7, 40, 3), (9, 35, 6), (6, 50, 2)], 20),
        ("04_acelerar_gratis", "Etapas con costo 0 y ahorro positivo: siempre se aceleran; el presupuesto se reparte entre las demás.",
         [(10, 0, 4), (8, 3, 5), (7, 0, 3), (9, 6, 7), (6, 2, 3)], 5),
        ("05_sin_ahorro", "Ninguna etapa ahorra nada (d_i = 0): no conviene acelerar y el ahorro es 0 aunque el presupuesto alcance.",
         [(10, 3, 0), (8, 2, 0), (7, 4, 0)], 10),
        ("06_razon_falla", "Tomar siempre lo que más ahorra por unidad de costo NO es óptimo: toma E01 (ahorra 8) y ya no caben las otras dos, que juntas ahorran 12.",
         [(12, 6, 8), (10, 5, 6), (10, 5, 6)], 10),
        ("07_empates", "Seis etapas idénticas: hay muchas soluciones óptimas con el mismo ahorro (se aceleran 2).",
         [(6, 2, 3)] * 6, 5),
        ("08_d_igual_t", "Cada etapa que se acelera pasa a durar 0 (d_i = t_i, el máximo permitido).",
         [(5, 2, 5), (4, 3, 4), (6, 4, 6), (3, 1, 3), (7, 5, 7)], 7),
        ("09_b_grande_d_chico", "Costos grandes y ahorros chicos (D pequeña, B grande): la tabla por valor es mucho más chica que la de presupuesto.",
         aleatorio(9, 12, (5000, 9000), (1, 3), 5), 40000),
        ("10_b_chico_d_grande", "Presupuesto chico y ahorros grandes (B pequeño, D grande): la tabla por presupuesto es la más chica.",
         aleatorio(10, 12, (1, 10), (100, 300), 20), 25),
        ("11_limite_n12", "Justo en el límite de la fuerza bruta (n = 12): se puede comparar con el óptimo exacto.",
         aleatorio(11, 12, (1, 20), (1, 30)), lambda e: sum(x[1] for x in e) // 2),
        ("12_n13_sin_fuerza_bruta", "n = 13: la fuerza bruta ya no se corre (solo con n <= 12).",
         aleatorio(12, 13, (1, 20), (1, 30)), lambda e: sum(x[1] for x in e) // 2),
        ("13_n20_b_moderado", "n = 20 con presupuesto de la mitad del costo total.",
         aleatorio(13, 20, (1, 20), (1, 30)), lambda e: sum(x[1] for x in e) // 2),
        ("14_n30", "n = 30 con presupuesto de la mitad del costo total.",
         aleatorio(14, 30, (1, 25), (1, 40)), lambda e: sum(x[1] for x in e) // 2),
        ("15_n50_b_un_tercio", "n = 50 con presupuesto de un tercio del costo total.",
         aleatorio(15, 50, (1, 30), (1, 50)), lambda e: sum(x[1] for x in e) // 3),
        ("16_n100", "n = 100 con presupuesto de la mitad del costo total.",
         aleatorio(16, 100, (1, 30), (1, 50)), lambda e: sum(x[1] for x in e) // 2),
        ("17_n200_b_enorme_base_no_cabe", "Costos enormes: la tabla por presupuesto NO cabe en memoria, la tabla por valor sí. Solo se resuelve con el enfoque por valor.",
         aleatorio(17, 200, (100000, 900000), (1, 3), 5), 50_000_000),
        ("18_n300_b2000_tabla_grande", "Tabla de más de 600 mil celdas: el visor la omite y muestra solo las decisiones.",
         aleatorio(18, 300, (1, 40), (1, 60)), 2000),
        (CASO_DE_ERROR, "CASO DE ERROR ESPERADO: B y D enormes, ninguna de las dos tablas cabe en el tope de memoria y la solución lo avisa con un error.",
         aleatorio(19, 400, (1, 1000), (100, 300)), 10 ** 8),
        # ---- Más casos: donde gana la tabla por valor (costos grandes y ahorros chicos, o sea B > D) ----
        ("20_valor_gana_n8_costos_enormes", "Costos de cientos de miles y ahorros de 1 a 10: la tabla por valor es mucho más chica. Con n = 8 se puede comparar con la fuerza bruta.",
         aleatorio(20, 8, (100000, 900000), (1, 10), 10), lambda e: sum(x[1] for x in e) // 2),
        ("21_valor_gana_n12_presupuesto_en_millones", "Presupuesto de decenas de millones y ahorros de 1 a 5, con n = 12: gana la tabla por valor y se comprueba con la fuerza bruta.",
         aleatorio(21, 12, (1_000_000, 9_000_000), (1, 5), 5), lambda e: sum(x[1] for x in e) // 3),
        ("22_valor_gana_n25_costos_en_miles", "Costos de 1.000 a 9.999 (por ejemplo, dinero) y ahorros de 1 a 9 (por ejemplo, días): gana la tabla por valor.",
         aleatorio(22, 25, (1000, 9999), (1, 9), 5), lambda e: sum(x[1] for x in e) // 2),
        ("23_valor_gana_n40_dinero_contra_dias", "Costos de 1.200 a 9.800 y ahorros de 1 a 9, con n = 40: el caso típico de pagar mucho para ahorrar pocos días.",
         aleatorio(23, 40, (1200, 9800), (1, 9), 5), lambda e: sum(x[1] for x in e) // 2),
        ("24_valor_gana_n60_ahorro_unitario", "Todas las etapas ahorran exactamente 1 (D = n): la tabla por valor tiene n + 1 columnas sin importar lo grande que sea B.",
         aleatorio(24, 60, (5000, 50000), (1, 1), 5), lambda e: sum(x[1] for x in e) // 2),
        ("25_valor_gana_n100", "n = 100, costos de 10.000 a 100.000 y ahorros de 1 a 5: la tabla por presupuesto tendría cientos de millones de celdas.",
         aleatorio(25, 100, (10_000, 100_000), (1, 5), 5), lambda e: sum(x[1] for x in e) // 2),
        ("26_valor_gana_n150_base_no_cabe", "n = 150 con costos de cientos de miles: la tabla por presupuesto NO cabe en memoria y la de valor sí.",
         aleatorio(26, 150, (100_000, 1_000_000), (1, 4), 5), lambda e: sum(x[1] for x in e) // 3),
        ("27_valor_gana_n300_ahorros_chicos", "n = 300 con costos de 1.000 a 100.000 y ahorros de 1 a 3: solo se resuelve cómodamente por valor.",
         aleatorio(27, 300, (1000, 100_000), (1, 3), 5), lambda e: sum(x[1] for x in e) // 2),
        ("28_cruce_empate_b_igual_d", "El presupuesto B es exactamente la suma de los ahorros D: las dos tablas tienen el mismo tamaño y se elige la base (empate).",
         aleatorio(28, 20, (1, 40), (1, 30)), lambda e: sum(x[2] for x in e)),
        # ---- Más casos: donde gana la tabla por presupuesto (B < D, lo habitual) ----
        ("29_presupuesto_gana_n10", "n = 10, ahorros mayores que los costos y B de la mitad del costo total: gana la tabla por presupuesto. Se compara con la fuerza bruta.",
         aleatorio(29, 10, (1, 15), (10, 40)), lambda e: sum(x[1] for x in e) // 2),
        ("30_presupuesto_gana_n15", "n = 15 con costos y ahorros de escala parecida (como el ejemplo de la profesora).",
         aleatorio(30, 15, (1, 25), (1, 35)), lambda e: sum(x[1] for x in e) // 2),
        ("31_presupuesto_gana_n40_b_un_cuarto", "n = 40 con un presupuesto de un cuarto del costo total.",
         aleatorio(31, 40, (1, 30), (1, 50)), lambda e: sum(x[1] for x in e) // 4),
        ("32_presupuesto_gana_n75", "n = 75 con presupuesto de la mitad del costo total.",
         aleatorio(32, 75, (1, 40), (1, 60)), lambda e: sum(x[1] for x in e) // 2),
        ("33_presupuesto_gana_n150", "n = 150 con presupuesto de un tercio del costo total.",
         aleatorio(33, 150, (1, 40), (1, 60)), lambda e: sum(x[1] for x in e) // 3),
        ("34_presupuesto_gana_n250_b1500", "n = 250 con B = 1.500 (la tabla tiene unas 376 mil celdas: el visor muestra solo las decisiones).",
         aleatorio(34, 250, (1, 30), (1, 50)), 1500),
        # ---- Casos mixtos ----
        ("35_mezcla_d_cero_y_c_cero", "Mezcla de etapas que no ahorran nada (d = 0), etapas gratis (c = 0) y etapas normales.",
         [(10, 0, 4), (8, 3, 0), (7, 0, 0), (9, 6, 7), (6, 2, 3), (12, 5, 0), (5, 0, 5), (9, 4, 6), (8, 7, 8), (11, 3, 2)], 12),
        ("36_b_casi_todo", "El presupuesto alcanza para casi todo (B = costo total − 1): hay que dejar fuera una sola etapa, la que menos ahorra por lo que cuesta.",
         aleatorio(36, 12, (1, 20), (1, 30)), lambda e: sum(x[1] for x in e) - 1),
        # ---- Gana la tabla por valor, pero la de presupuesto TAMBIÉN cabe y puede correr (para compararlas) ----
        ("37_valor_gana_base_si_cabe_n10", "n = 10: la tabla por presupuesto tiene unas 70 mil celdas y corre sin problema, pero la de valor tiene unas 300. Se compara con la fuerza bruta.",
         aleatorio(37, 10, (800, 1500), (1, 4), 5), lambda e: sum(x[1] for x in e) // 2),
        ("38_valor_gana_base_si_cabe_n12", "n = 12: la tabla por presupuesto (unas 300 mil celdas) cabe y corre; la de valor tiene unas 700. Se compara con la fuerza bruta.",
         aleatorio(38, 12, (2000, 6000), (1, 6), 5), lambda e: sum(x[1] for x in e) // 2),
        ("39_valor_gana_base_si_cabe_n20", "n = 20: la base (unas 400 mil celdas) cabe y corre; la tabla por valor es unas 300 veces más chica.",
         aleatorio(39, 20, (1000, 3000), (1, 5), 5), lambda e: sum(x[1] for x in e) // 2),
        ("40_valor_gana_base_si_cabe_n30", "n = 30: la base tiene unas 760 mil celdas y corre; la tabla por valor, unas 4 mil.",
         aleatorio(40, 30, (1000, 4000), (1, 8), 5), lambda e: sum(x[1] for x in e) // 3),
        ("41_valor_gana_base_si_cabe_n60", "n = 60: la base tiene alrededor de un millón de celdas y corre; la tabla por valor, menos de 8 mil.",
         aleatorio(41, 60, (300, 900), (1, 3), 5), lambda e: sum(x[1] for x in e) // 2),
        ("42_valor_gana_base_si_cabe_n50_ahorro_unitario", "n = 50 y todos los ahorros valen 1: la base tiene unos 2 millones de celdas y corre (tarda menos de 1 segundo); la tabla por valor tiene solo 51 columnas.",
         aleatorio(42, 50, (500, 3000), (1, 1), 5), lambda e: sum(x[1] for x in e) // 2),
        ("43_valor_gana_base_si_cabe_n100_la_base_tarda", "n = 100: la base tiene unos 5 millones de celdas (cabe en el tope, pero tarda casi 2 segundos y ocupa unos 190 MB); la de valor tarda milésimas de segundo.",
         aleatorio(43, 100, (500, 1500), (1, 4), 5), lambda e: sum(x[1] for x in e) // 2),
        ("44_valor_gana_base_si_cabe_ventaja_chica", "Cerca del cruce: B es solo 1,5 veces la suma de los ahorros D. La tabla por valor gana, pero por poco, y las dos son chicas.",
         aleatorio(44, 20, (1, 40), (1, 30)), lambda e: int(sum(x[2] for x in e) * 1.5)),
    ]



def _resultado(nombre, inst):
    """Texto con lo que dan las dos DP y la fuerza bruta (si aplica), calculado con el código del proyecto."""
    celdas = tamanos_de_tablas(inst)
    partes = ["Celdas de la tabla: por presupuesto %d, por valor %d." % (celdas["presupuesto"], celdas["valor"])]
    try:
        partes.append("Enfoque recomendado: %s." % elegir_enfoque(inst))
    except ErrorDeEntrada:
        partes.append("Ninguna tabla cabe en el tope de %d celdas." % MAX_CELDAS_TABLA)
        return " ".join(partes)
    enfoque = elegir_enfoque(inst)
    resolver_enfoque = resolver_valor if enfoque == "valor" else resolver
    res = resolver_enfoque(inst.t, inst.c, inst.d, inst.B)
    otra = resolver if enfoque == "valor" else resolver_valor
    celdas_otra = celdas["presupuesto" if enfoque == "valor" else "valor"]
    if celdas_otra <= CELDAS_PARA_CRUZAR:       # si la otra tabla es chica, se cruza para comprobar que dan lo mismo
        assert otra(inst.t, inst.c, inst.d, inst.B)["ahorro"] == res["ahorro"], nombre
    base_txt = "ahorro %d, costo %d de B = %d, %d etapas aceleradas, duración final %d de %d" % (
        res["ahorro"], res["costo"], inst.B, len(res["aceleradas"]), res["duracion_final"], sum(inst.t))
    partes.append("Resultado: %s." % base_txt)
    if len(inst.c) <= N_MAX_FUERZA_BRUTA:
        partes.append("Fuerza bruta: ahorro %d." % fuerza_bruta(inst.t, inst.c, inst.d, inst.B)["ahorro"])
    return " ".join(partes)


def _texto_json(descripcion, B, etapas):
    n = len(etapas)
    lineas = ["{", '  "descripcion": %s,' % json.dumps(descripcion, ensure_ascii=False),
              '  "parametros": {"numero_etapas": %d, "presupuesto_aceleracion_B": %d},' % (n, B),
              '  "etapas": [']
    for k, (t, c, d) in enumerate(etapas):
        coma = "," if k < n - 1 else ""
        lineas.append('    {"id": "E%02d", "duracion_normal": %d, "costo_aceleracion": %d, '
                      '"reduccion_tiempo_si_acelera": %d}%s' % (k + 1, t, c, d, coma))
    lineas += ["  ]", "}"]
    return "\n".join(lineas) + "\n"


def generar(salida: Path) -> list:
    """Escribe los casos y el README en `salida`. Devuelve [(nombre, n, B, descripcion)]."""
    salida.mkdir(parents=True, exist_ok=True)
    resumen = []
    base_cabe = []
    for nombre, que, etapas, B in _casos():
        B = B(etapas) if callable(B) else B
        inst = InstanciaAceleracion(nombre, [e[0] for e in etapas], [e[1] for e in etapas], [e[2] for e in etapas], B)
        descripcion = "%s %s" % (que, _resultado(nombre, inst))
        (salida / (nombre + ".json")).write_text(_texto_json(descripcion, B, etapas), encoding="utf-8")
        resumen.append((nombre, len(etapas), B, que))
        c = tamanos_de_tablas(inst)
        if "valor_gana" in nombre and c["valor"] < c["presupuesto"] <= MAX_CELDAS_TABLA:
            base_cabe.append(nombre.split("_")[0])

    filas = "\n".join("| `%s.json` | %d | %d | %s |" % (nombre, n, B, que) for nombre, n, B, que in resumen)
    (salida / "README.md").write_text(
        "# Casos propios de la Parte 1 (programación dinámica)\n\n"
        "Casos de prueba propios, **no** de la profesora. Mismo formato JSON que el ejemplo de la profesora\n"
        "(`entrada_G3_mochila_20_nodos.json`, que también está en esta carpeta); la clave `descripcion` dice qué prueba cada\n"
        "caso y el resultado calculado con el código del proyecto. Se generan con semilla fija:\n\n"
        "```\npython3 pruebas/casos_propios/pd/generar_casos.py\n```\n\n"
        "| Caso | n | B | Qué prueba |\n| --- | --- | --- | --- |\n" + filas + "\n\n"
        "Los casos con `valor_gana` en el nombre son aquellos donde la tabla por valor es la más chica (en %s la tabla por presupuesto **también cabe y puede correr**, así que se pueden comparar las dos; en los demás solo cabe la de valor); los de `presupuesto_gana`, donde lo es la de presupuesto; el 28 es el empate (se elige la base).\n\nEl caso `%s` **debe dar error** (ninguna tabla cabe); todos los demás se resuelven. "
        "Las pruebas están en `tests/test_casos_propios_pd.py`.\n" % (", ".join("`%s`" % x for x in base_cabe), CASO_DE_ERROR), encoding="utf-8")
    return resumen


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera los casos propios de la Parte 1.")
    parser.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent, help="carpeta de salida")
    args = parser.parse_args(argv)
    resumen = generar(args.salida)
    print("Escribí %d casos y README.md en %s" % (len(resumen), args.salida))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
