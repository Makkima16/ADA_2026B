# Comparación de resultados

Versión del código: e42e041 (con cambios sin commit) · Generado: 2026-11-06 17:39:59 · Casos: 20

El mínimo real (óptimo) de la Parte 2 y de la variante se calcula por fuerza bruta con n ≤ 12 y, si no, por subconjuntos de categorías con r ≤ 16; en la Parte 1 solo por fuerza bruta con n ≤ 12. Donde no se puede calcular aparece «—».

No aplica la Parte 1 en 20 casos (no traen sus datos; se analizan solo con la otra parte): 01_no_factible, 02_todos_optimos, 03_clasico_no_optimo, 04_solo_esenciales, 05_solo_parejas, 06_solo_todo, 07_ninguno_acierta, 08_esenciales_empeora ….

## Resumen

- **Parte 2:** el voraz fue óptimo en 5 de 15 casos con mínimo real; razón máxima 2.000; casos que superan H(d): 0.


### Parte 2 — los ocho enfoques del voraz

- **19 casos factibles**, 15 con mínimo real (fuerza bruta con n ≤ 12; si no, subconjuntos de categorías con r ≤ 16). Comprobación independiente de la cobertura: 0 de 152 ejecuciones no cubrieron todas las categorías (debe ser 0).

«No llegó al mínimo» cuenta los casos con óptimo en que el enfoque usó más interacciones que el mínimo. «Contra el voraz base» cuenta en cuántos casos usó menos (mejor), igual o más (peor).

| Enfoque | No llegó al mínimo | Contra el voraz base (mejor / igual / peor) | Razón máxima al óptimo | Pasó de H(d) | Tiempo medio (ms) |
| --- | :---: | :---: | ---: | ---: | ---: |
| Voraz base | 10 de 15 | — (es la referencia) | 2.000 | 0 | 0.044 |
| Esenciales | 9 de 15 | 6 / 11 / 2 | 2.000 | 0 | 0.037 |
| Rareza | 7 de 15 | 6 / 12 / 1 | 2.000 | 0 | 0.144 |
| Parejas | 6 de 15 | 7 / 9 / 3 | 1.333 | 0 | 0.217 |
| Esenciales + rareza | 6 de 15 | 8 / 9 / 2 | 2.000 | 0 | 0.104 |
| Esenciales + parejas | 3 de 15 | 11 / 6 / 2 | 1.333 | 0 | 0.152 |
| Rareza + parejas | 1 de 15 | 12 / 6 / 1 | 1.333 | 0 | 0.776 |
| Los tres (enfoque D) | 1 de 15 | 12 / 6 / 1 | 1.333 | 0 | 0.554 |

No llegó al mínimo, según la densidad (casos con óptimo de cada una):

| Enfoque | ralo (9 casos) | medio (4 casos) | denso (6 casos) |
| --- | :---: | :---: | :---: |
| Voraz base | 3 | 3 | 4 |
| Esenciales | 3 | 4 | 2 |
| Rareza | 1 | 2 | 4 |
| Parejas | 2 | 2 | 2 |
| Esenciales + rareza | 2 | 2 | 2 |
| Esenciales + parejas | 2 | 1 | 0 |
| Rareza + parejas | 1 | 0 | 0 |
| Los tres (enfoque D) | 1 | 0 | 0 |



## Detalle por caso

## Parte 2 (mínimo número) vs Variante 1 (mínimo costo)

«Costo del J de la Parte 2» = lo que costaría auditar, con los costos a_j, las interacciones que elige el voraz de la Parte 2. «Ahorro» = cuánto más barato sale el voraz ponderado.

| Caso | n | r | d | H(d) | P2: \|J\| | P2: óptimo | P2: razón | V1: \|J\| | V1: costo | V1: óptimo | V1: razón | Costo del J de la P2 | Ahorro de la V1 | P2 (ms) | V1 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 02_todos_optimos | 3 | 4 | 2 | 1.500 | 2 | 2 | 1.000 | — | — | — | — | — | sin costos | 0.019 | — |
| 03_clasico_no_optimo | 3 | 6 | 4 | 2.083 | 3 | 2 | 1.500 | — | — | — | — | — | sin costos | 0.014 | — |
| 04_solo_esenciales | 4 | 6 | 3 | 1.833 | 4 | 3 | 1.333 | — | — | — | — | — | sin costos | 0.017 | — |
| 05_solo_parejas | 5 | 14 | 8 | 2.718 | 3 | 2 | 1.500 | — | — | — | — | — | sin costos | 0.018 | — |
| 06_solo_todo | 7 | 7 | 3 | 1.833 | 4 | 3 | 1.333 | — | — | — | — | — | sin costos | 0.019 | — |
| 07_ninguno_acierta | 7 | 7 | 3 | 1.833 | 4 | 3 | 1.333 | — | — | — | — | — | sin costos | 0.021 | — |
| 08_esenciales_empeora | 7 | 7 | 3 | 1.833 | 3 | 3 | 1.000 | — | — | — | — | — | sin costos | 0.017 | — |
| 09_parejas_empeora | 4 | 8 | 4 | 2.083 | 3 | 3 | 1.000 | — | — | — | — | — | sin costos | 0.014 | — |
| 10_esenciales_y_parejas_empeoran | 9 | 9 | 4 | 2.083 | 4 | 4 | 1.000 | — | — | — | — | — | sin costos | 0.023 | — |
| 11_cebos_k4 | 6 | 30 | 16 | 3.381 | 4 | 2 | 2.000 | — | — | — | — | — | sin costos | 0.030 | — |
| 12_limite_n12 | 12 | 10 | 3 | 1.833 | 7 | 6 | 1.167 | — | — | — | — | — | sin costos | 0.036 | — |
| 13_n15_r10 | 15 | 10 | 6 | 2.450 | 3 | 2 | 1.500 | — | — | — | — | — | sin costos | 0.026 | — |
| 14_n20_r20_ralo | 20 | 20 | 5 | 2.283 | 11 | — | — | — | — | — | — | — | sin costos | 0.090 | — |
| 15_n20_r40 | 20 | 40 | 8 | 2.718 | 12 | — | — | — | — | — | — | — | sin costos | 0.122 | — |
| 16_n25_r15 | 25 | 15 | 6 | 2.450 | 5 | 4 | 1.250 | — | — | — | — | — | sin costos | 0.051 | — |
| 17_n30_r10 | 30 | 10 | 5 | 2.283 | 4 | 4 | 1.000 | — | — | — | — | — | sin costos | 0.043 | — |
| 18_n30_r30_parejas_peor | 30 | 30 | 11 | 3.020 | 6 | — | — | — | — | — | — | — | sin costos | 0.098 | — |
| 19_n24_plantado | 24 | 24 | 4 | 2.083 | 9 | — | — | — | — | — | — | — | sin costos | 0.093 | — |
| 20_rareza_acierta | 7 | 7 | 3 | 1.833 | 4 | 3 | 1.333 | — | — | — | — | — | sin costos | 0.019 | — |



### Parte 2 — tamaño de J de cada enfoque, caso por caso

Cada celda es el número de interacciones que eligió el enfoque; menos es mejor. «Óptimo» es el mínimo real por fuerza bruta (solo con n ≤ 12). Las claves son los ingredientes: e = esenciales, r = rareza, p = parejas; «todo» = los tres.

| Caso | n | r | H(d) | Óptimo | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 02_todos_optimos | 3 | 4 | 1.500 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| 03_clasico_no_optimo | 3 | 6 | 2.083 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 2 |
| 04_solo_esenciales | 4 | 6 | 1.833 | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 3 |
| 05_solo_parejas | 5 | 14 | 2.718 | 2 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 2 |
| 06_solo_todo | 7 | 7 | 1.833 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 |
| 07_ninguno_acierta | 7 | 7 | 1.833 | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| 08_esenciales_empeora | 7 | 7 | 1.833 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 |
| 09_parejas_empeora | 4 | 8 | 2.083 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 |
| 10_esenciales_y_parejas_empeoran | 9 | 9 | 2.083 | 4 | 4 | 5 | 4 | 5 | 5 | 5 | 4 | 4 |
| 11_cebos_k4 | 6 | 30 | 3.381 | 2 | 4 | 4 | 4 | 2 | 4 | 2 | 2 | 2 |
| 12_limite_n12 | 12 | 10 | 1.833 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 13_n15_r10 | 15 | 10 | 2.450 | 2 | 3 | 3 | 3 | 2 | 3 | 2 | 2 | 2 |
| 14_n20_r20_ralo | 20 | 20 | 2.283 | — | 11 | 10 | 10 | 11 | 10 | 10 | 10 | 10 |
| 15_n20_r40 | 20 | 40 | 2.718 | — | 12 | 10 | 10 | 11 | 10 | 10 | 10 | 10 |
| 16_n25_r15 | 25 | 15 | 2.450 | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 4 |
| 17_n30_r10 | 30 | 10 | 2.283 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| 18_n30_r30_parejas_peor | 30 | 30 | 3.020 | — | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 |
| 19_n24_plantado | 24 | 24 | 2.083 | — | 9 | 7 | 6 | 9 | 6 | 6 | 6 | 6 |
| 20_rareza_acierta | 7 | 7 | 1.833 | 3 | 4 | 4 | 3 | 4 | 3 | 4 | 3 | 3 |

### Parte 2 — tiempo de cada enfoque (ms), caso por caso

| Caso | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 02_todos_optimos | 0.019 | 0.016 | 0.035 | 0.035 | 0.015 | 0.009 | 0.050 | 0.013 |
| 03_clasico_no_optimo | 0.017 | 0.011 | 0.032 | 0.017 | 0.010 | 0.015 | 0.040 | 0.010 |
| 04_solo_esenciales | 0.017 | 0.012 | 0.042 | 0.035 | 0.012 | 0.010 | 0.072 | 0.012 |
| 05_solo_parejas | 0.019 | 0.019 | 0.050 | 0.033 | 0.045 | 0.028 | 0.067 | 0.078 |
| 06_solo_todo | 0.021 | 0.019 | 0.061 | 0.050 | 0.045 | 0.032 | 0.124 | 0.079 |
| 07_ninguno_acierta | 0.021 | 0.020 | 0.068 | 0.047 | 0.059 | 0.056 | 0.155 | 0.152 |
| 08_esenciales_empeora | 0.018 | 0.021 | 0.056 | 0.052 | 0.036 | 0.031 | 0.130 | 0.085 |
| 09_parejas_empeora | 0.015 | 0.013 | 0.037 | 0.031 | 0.012 | 0.011 | 0.065 | 0.012 |
| 10_esenciales_y_parejas_empeoran | 0.034 | 0.029 | 0.084 | 0.091 | 0.070 | 0.063 | 0.244 | 0.230 |
| 11_cebos_k4 | 0.030 | 0.030 | 0.078 | 0.040 | 0.102 | 0.044 | 0.093 | 0.089 |
| 12_limite_n12 | 0.042 | 0.032 | 0.141 | 0.120 | 0.081 | 0.091 | 0.454 | 0.329 |
| 13_n15_r10 | 0.029 | 0.032 | 0.112 | 0.105 | 0.099 | 0.094 | 0.336 | 0.339 |
| 14_n20_r20_ralo | 0.094 | 0.084 | 0.336 | 0.464 | 0.198 | 0.269 | 1.824 | 1.119 |
| 15_n20_r40 | 0.115 | 0.060 | 0.384 | 0.647 | 0.105 | 0.120 | 2.174 | 0.401 |
| 16_n25_r15 | 0.073 | 0.059 | 0.197 | 0.353 | 0.247 | 0.386 | 1.503 | 1.377 |
| 17_n30_r10 | 0.048 | 0.050 | 0.194 | 0.373 | 0.193 | 0.384 | 1.740 | 1.746 |
| 18_n30_r30_parejas_peor | 0.114 | 0.112 | 0.464 | 0.928 | 0.439 | 0.963 | 3.570 | 3.469 |
| 19_n24_plantado | 0.098 | 0.069 | 0.298 | 0.647 | 0.154 | 0.243 | 1.969 | 0.877 |
| 20_rareza_acierta | 0.021 | 0.021 | 0.056 | 0.048 | 0.048 | 0.046 | 0.132 | 0.118 |

