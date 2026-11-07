# Comparación de resultados

Versión del código: deceef6 (con cambios sin commit) · Generado: 2026-11-06 22:39:29 · Casos: 1

El mínimo real (óptimo) de la Parte 2 y de la variante se calcula por fuerza bruta con n ≤ 12 y, si no, por subconjuntos de categorías con r ≤ 16; en la Parte 1 solo por fuerza bruta con n ≤ 12. Donde no se puede calcular aparece «—».

## Resumen

- **Parte 1:** La duración de la cadena bajó en promedio 11.0 % (entre 11.0 % y 11.0 %), usando en promedio el 100 % del presupuesto B.
- **Parte 2:** el voraz fue óptimo en 1 de 1 casos con mínimo real; razón máxima 1.000; casos que superan H(d): 0.
- **Variante 1:** el voraz ponderado fue óptimo en 0 de 1 casos con mínimo real; razón máxima 1.038; casos que superan H(d): 0.
- **Parte 2 vs Variante 1:** la variante salió más barata que el J de la Parte 2 en 1 de 1 casos (ahorro medio 7 %), igual en 0 y más cara en 0.

### Parte 1 — las dos tablas de la DP

- **1 casos.** Las dos tablas cupieron en 1 y dieron el mismo ahorro en 1 (debe ser siempre: las dos son exactas).
- **Solo por valor:** 0 casos (la tabla por presupuesto no cabe). **Ninguna cabe:** 0 (se informa que la tabla es demasiado grande).

| Relación | Casos | Con las dos tablas | Celdas (presupuesto) | Celdas (valor) | Tiempo presupuesto (ms) | Tiempo valor (ms) | La de menos celdas fue más rápida |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| B menor que D | 1 | 1 | 1533 | 3486 | 0.658 | 0.717 | 1 de 1 |
| B igual a D | 0 | 0 | — | — | — | — | — |
| B mayor que D | 0 | 0 | — | — | — | — | — |

### Parte 2 — los ocho enfoques del voraz

- **1 casos factibles**, 1 con mínimo real (fuerza bruta con n ≤ 12; si no, subconjuntos de categorías con r ≤ 16). Comprobación independiente de la cobertura: 0 de 8 ejecuciones no cubrieron todas las categorías (debe ser 0).

«No llegó al mínimo» cuenta los casos con óptimo en que el enfoque usó más interacciones que el mínimo. «Contra el voraz base» cuenta en cuántos casos usó menos (mejor), igual o más (peor).

| Enfoque | No llegó al mínimo | Contra el voraz base (mejor / igual / peor) | Razón máxima al óptimo | Pasó de H(d) | Tiempo medio (ms) |
| --- | :---: | :---: | ---: | ---: | ---: |
| Voraz base | 0 de 1 | — (es la referencia) | 1.000 | 0 | 0.079 |
| Esenciales | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.091 |
| Rareza | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.348 |
| Parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.425 |
| Esenciales + rareza | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.254 |
| Esenciales + parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.403 |
| Rareza + parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 2.040 |
| Los tres (enfoque D) | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 2.005 |

No llegó al mínimo, según la densidad (casos con óptimo de cada una):

| Enfoque | ralo (0 casos) | medio (1 casos) | denso (0 casos) |
| --- | :---: | :---: | :---: |
| Voraz base | 0 | 0 | 0 |
| Esenciales | 0 | 0 | 0 |
| Rareza | 0 | 0 | 0 |
| Parejas | 0 | 0 | 0 |
| Esenciales + rareza | 0 | 0 | 0 |
| Esenciales + parejas | 0 | 0 | 0 |
| Rareza + parejas | 0 | 0 | 0 |
| Los tres (enfoque D) | 0 | 0 | 0 |

### Variante 1 — voraz ponderado, solo completas

- **1 casos**.
- **Contra el mínimo real** (1 casos con mínimo calculado): llegó al mínimo en 0; razón máxima 1.038; casos que superan H(d): 0.
- **Contra el J de la Parte 2:** salió más barata en 1 casos (ahorro medio 7 %), igual en 0 y más cara en 0.

### Variante 1 — voraz ponderado, con parciales (extensión)

- **1 casos**; en 0 el voraz eligió la parcial y la completa de una misma interacción y se depuró.
- **Contra el mínimo real** (1 casos con mínimo calculado): llegó al mínimo en 0; razón máxima 1.083; casos que superan H(d): 0.
- **Contra la versión solo completas:** salió más barata en 1 casos (ahorro medio 4 %), igual en 0 y más cara en 0.

## Detalle por caso

## Parte 1 — Aceleración de la cadena (DP exacta)

La DP es exacta: su ahorro debe coincidir siempre con el de la fuerza bruta (que solo se calcula con n ≤ 12). «Tabla usada» es la que da la solución del caso: la de presupuesto si cabe en memoria; si no, la de valor. «Reducción» = cuánto bajó la duración de la cadena; «Presupuesto usado» = costo de las etapas aceleradas sobre B.

| Caso | n | B | Tabla usada | Etapas aceleradas | Costo usado | Presupuesto usado | Ahorro DP | Ahorro fuerza bruta | ¿Coinciden? | Duración inicial → final | Reducción | Tiempo DP (ms) |
| --- | ---: | ---: | :---: | --- | ---: | ---: | ---: | ---: | :---: | --- | ---: | ---: |
| entrada_G3_mochila_20_nodos | 20 | 72 | presupuesto | [2, 3, 4, 6, 8, 12] | 72 | 100 % | 55 | — | — | 501 → 446 | 11.0 % | 0.658 |

## Parte 2 (mínimo número) vs Variante 1 (mínimo costo)

«Costo del J de la Parte 2» = lo que costaría auditar, con los costos a_j, las interacciones que elige el voraz de la Parte 2. «Ahorro» = cuánto más barato sale el voraz ponderado.

| Caso | n | r | d | H(d) | P2: \|J\| | P2: óptimo | P2: razón | V1: \|J\| | V1: costo | V1: óptimo | V1: razón | Costo del J de la P2 | Ahorro de la V1 | P2 (ms) | V1 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 20 | 12 | 4 | 2.083 | 4 | 4 | 1.000 | 4 | 27 | 26 | 1.038 | 29 | 2 (7 %) | 0.066 | 0.123 |


### Parte 1 — DP por presupuesto y por valor, caso por caso

Las dos tablas son exactas: cuando las dos caben deben dar el mismo ahorro. «Celdas» es el tamaño de cada tabla; «—» = no cabe (límite 10000000 celdas) y no se corrió. La solución del caso es la tabla por presupuesto si cabe; si no, la de valor.

| Caso | n | B | D | Celdas presupuesto | Celdas valor | Ahorro presupuesto | Ahorro valor | ¿Coinciden? | Tiempo presupuesto (ms) | Tiempo valor (ms) | Solución del caso |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | --- |
| entrada_G3_mochila_20_nodos | 20 | 72 | 165 | 1533 | 3486 | 55 | 55 | sí | 0.658 | 0.717 | por presupuesto |

### Parte 2 — tamaño de J de cada enfoque, caso por caso

Cada celda es el número de interacciones que eligió el enfoque; menos es mejor. «Óptimo» es el mínimo real por fuerza bruta (solo con n ≤ 12). Las claves son los ingredientes: e = esenciales, r = rareza, p = parejas; «todo» = los tres.

| Caso | n | r | H(d) | Óptimo | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 20 | 12 | 2.083 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Parte 2 — tiempo de cada enfoque (ms), caso por caso

| Caso | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 0.079 | 0.091 | 0.348 | 0.425 | 0.254 | 0.403 | 2.040 | 2.005 |

