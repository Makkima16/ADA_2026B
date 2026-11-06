# Comparación de resultados

Versión del código: e42e041 (con cambios sin commit) · Generado: 2026-11-06 17:39:58 · Casos: 20

El mínimo real (óptimo) de la Parte 2 y de la variante se calcula por fuerza bruta con n ≤ 12 y, si no, por subconjuntos de categorías con r ≤ 16; en la Parte 1 solo por fuerza bruta con n ≤ 12. Donde no se puede calcular aparece «—».

No aplica la Parte 2 en 19 casos (no traen sus datos; se analizan solo con la otra parte): 01_b_cero, 03_nada_cabe, 07_empates, 11_limite_n12, 12_n13_sin_fuerza_bruta, 13_n20_b_moderado, 15_n50_b_un_tercio, 17_n200_b_enorme_base_no_cabe ….

## Resumen

- **Parte 1:** la DP coincidió con la fuerza bruta en 8 de 8 casos con n ≤ 12 (debe ser siempre: es exacta). La duración de la cadena bajó en promedio 33.9 % (entre 0.0 % y 66.3 %), usando en promedio el 91 % del presupuesto B.
- **Parte 2:** el voraz fue óptimo en 1 de 1 casos con mínimo real; razón máxima 1.000; casos que superan H(d): 0.
- **Variante 1:** el voraz ponderado fue óptimo en 0 de 1 casos con mínimo real; razón máxima 1.038; casos que superan H(d): 0.
- **Parte 2 vs Variante 1:** la variante salió más barata que el J de la Parte 2 en 1 de 1 casos (ahorro medio 7 %), igual en 0 y más cara en 0.

### Parte 1 — las dos tablas de la DP

- **20 casos.** Las dos tablas cupieron en 14 y dieron el mismo ahorro en 14 (debe ser siempre: las dos son exactas).
- **Solo por valor:** 5 casos (la tabla por presupuesto no cabe). **Ninguna cabe:** 1 (se informa que la tabla es demasiado grande).
- **Contra la fuerza bruta (n ≤ 12), 8 casos:** por presupuesto acertó 6, por valor acertó 8.

| Relación | Casos | Con las dos tablas | Celdas (presupuesto) | Celdas (valor) | Tiempo presupuesto (ms) | Tiempo valor (ms) | La de menos celdas fue más rápida |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| B menor que D | 11 | 11 | 16555 | 71618 | 6.052 | 14.465 | 10 de 11 |
| B igual a D | 2 | 2 | 3717 | 3717 | 1.163 | 0.631 | — |
| B mayor que D | 7 | 1 | 762817 | 4154 | 247.736 | 0.732 | 1 de 1 |

### Parte 2 — los ocho enfoques del voraz

- **1 casos factibles**, 1 con mínimo real (fuerza bruta con n ≤ 12; si no, subconjuntos de categorías con r ≤ 16). Comprobación independiente de la cobertura: 0 de 8 ejecuciones no cubrieron todas las categorías (debe ser 0).

«No llegó al mínimo» cuenta los casos con óptimo en que el enfoque usó más interacciones que el mínimo. «Contra el voraz base» cuenta en cuántos casos usó menos (mejor), igual o más (peor).

| Enfoque | No llegó al mínimo | Contra el voraz base (mejor / igual / peor) | Razón máxima al óptimo | Pasó de H(d) | Tiempo medio (ms) |
| --- | :---: | :---: | ---: | ---: | ---: |
| Voraz base | 0 de 1 | — (es la referencia) | 1.000 | 0 | 0.045 |
| Esenciales | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.052 |
| Rareza | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.169 |
| Parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.259 |
| Esenciales + rareza | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.163 |
| Esenciales + parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.246 |
| Rareza + parejas | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 1.012 |
| Los tres (enfoque D) | 0 de 1 | 0 / 1 / 0 | 1.000 | 0 | 0.976 |

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
| 01_b_cero | 5 | 0 | presupuesto | [] | 0 | — | 0 | 0 | sí | 40 → 40 | 0.0 % | 0.027 |
| 03_nada_cabe | 5 | 20 | presupuesto | [] | 0 | 0 % | 0 | 0 | sí | 40 → 40 | 0.0 % | 0.023 |
| 07_empates | 6 | 5 | presupuesto | [1, 2] | 4 | 80 % | 6 | 6 | sí | 36 → 30 | 16.7 % | 0.029 |
| 11_limite_n12 | 12 | 85 | presupuesto | [2, 3, 7, 8, 9, 10, 12] | 85 | 100 % | 144 | 144 | sí | 305 → 161 | 47.2 % | 0.358 |
| 12_n13_sin_fuerza_bruta | 13 | 76 | presupuesto | [1, 3, 4, 6, 7, 10, 13] | 76 | 100 % | 135 | — | — | 268 → 133 | 50.4 % | 0.318 |
| 13_n20_b_moderado | 20 | 76 | presupuesto | [1, 2, 3, 4, 5, 7, 8, 9, 12, 13, 15, 19, 20] | 76 | 100 % | 322 | — | — | 693 → 371 | 46.5 % | 0.502 |
| 15_n50_b_un_tercio | 50 | 249 | presupuesto | [1, 2, 3, 5, 6, 8, 9, 10, 14, 17, 18, 19, 22, 23, 27, 31, 33, 35, 36, 37, 39, 40, 42, 46, 48, 49] | 249 | 100 % | 786 | — | — | 1700 → 914 | 46.2 % | 4.312 |
| 17_n200_b_enorme_base_no_cabe | 200 | 50000000 | valor | [2, 3, 4, 5, 6, 8, 10, 12, 13, 14, 15, 17, 18, 20, 22, 23, 24, 25, 27, 28, 30, 36, 38, 39, 40, 41, 44, 45, 46, 47, 49, 51, 52, 54, 56, 58, 60, 61, 62, 64, 66, 67, 68, 69, 70, 71, 72, 74, 75, 77, 79, 80, 85, 87, 89, 90, 91, 93, 96, 97, 98, 99, 101, 102, 105, 106, 108, 110, 111, 112, 113, 114, 115, 117, 118, 121, 122, 123, 128, 129, 131, 133, 134, 135, 137, 138, 139, 140, 141, 143, 145, 149, 150, 152, 156, 160, 161, 162, 166, 169, 170, 173, 174, 175, 176, 178, 180, 181, 182, 184, 186, 188, 189, 190, 191, 193, 195, 197, 199, 200] | 49850554 | 100 % | 282 | — | — | 870 → 588 | 32.4 % | 14.924 |
| 20_valor_gana_n8_costos_enormes | 8 | 2265815 | valor | [1, 4, 5, 7] | 2243555 | 99 % | 26 | 26 | sí | 80 → 54 | 32.5 % | 0.078 |
| 21_valor_gana_n12_presupuesto_en_millones | 12 | 21393847 | valor | [1, 2, 3, 4, 9] | 20995013 | 98 % | 22 | 22 | sí | 67 → 45 | 32.8 % | 0.108 |
| 24_valor_gana_n60_ahorro_unitario | 60 | 822648 | valor | [1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 17, 18, 20, 22, 24, 26, 27, 29, 31, 32, 33, 36, 38, 39, 40, 41, 42, 43, 44, 45, 48, 49, 50, 51, 53, 54, 55, 58, 60] | 799775 | 97 % | 41 | — | — | 198 → 157 | 20.7 % | 0.743 |
| 26_valor_gana_n150_base_no_cabe | 150 | 28419849 | valor | [2, 4, 5, 8, 9, 13, 14, 17, 18, 19, 24, 26, 30, 34, 38, 43, 45, 46, 47, 48, 49, 55, 57, 64, 67, 71, 72, 74, 76, 78, 79, 80, 81, 82, 83, 84, 86, 87, 89, 90, 92, 96, 98, 99, 100, 101, 103, 108, 109, 111, 113, 115, 116, 117, 118, 119, 121, 124, 126, 127, 129, 131, 133, 134, 135, 137, 138, 139, 142, 143, 144, 149] | 28301223 | 100 % | 225 | — | — | 763 → 538 | 29.5 % | 9.678 |
| 28_cruce_empate_b_igual_d | 20 | 347 | presupuesto | [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] | 327 | 94 % | 343 | — | — | 517 → 174 | 66.3 % | 2.303 |
| 29_presupuesto_gana_n10 | 10 | 41 | presupuesto | [1, 2, 3, 7, 8, 9] | 33 | 80 % | 157 | 157 | sí | 320 → 163 | 49.1 % | 0.143 |
| 31_presupuesto_gana_n40_b_un_cuarto | 40 | 120 | presupuesto | [1, 2, 3, 5, 6, 8, 9, 10, 15, 16, 18, 20, 21, 22, 28, 30, 31, 32, 37, 38, 40] | 119 | 99 % | 595 | — | — | 1320 → 725 | 45.1 % | 1.569 |
| 33_presupuesto_gana_n150 | 150 | 1048 | presupuesto | [1, 3, 4, 8, 11, 13, 16, 21, 22, 25, 28, 29, 30, 31, 33, 36, 38, 41, 42, 43, 49, 50, 51, 53, 55, 57, 60, 61, 63, 66, 73, 78, 83, 85, 88, 89, 93, 94, 97, 100, 107, 109, 111, 112, 113, 118, 120, 121, 123, 125, 126, 127, 128, 129, 130, 132, 133, 135, 136, 138, 139, 140, 141, 142, 143, 144, 147, 148, 149, 150] | 1047 | 100 % | 2970 | — | — | 5930 → 2960 | 50.1 % | 58.796 |
| 35_mezcla_d_cero_y_c_cero | 10 | 12 | presupuesto | [1, 4, 5, 7, 8] | 12 | 100 % | 25 | 25 | sí | 85 → 60 | 29.4 % | 0.061 |
| 40_valor_gana_base_si_cabe_n30 | 30 | 24606 | presupuesto | [3, 5, 6, 11, 13, 15, 16, 17, 23, 24, 28, 29] | 24367 | 99 % | 80 | — | — | 211 → 131 | 37.9 % | 247.736 |
| entrada_G3_mochila_20_nodos | 20 | 72 | presupuesto | [2, 3, 4, 6, 8, 12] | 72 | 100 % | 55 | — | — | 501 → 446 | 11.0 % | 0.454 |

## Parte 2 (mínimo número) vs Variante 1 (mínimo costo)

«Costo del J de la Parte 2» = lo que costaría auditar, con los costos a_j, las interacciones que elige el voraz de la Parte 2. «Ahorro» = cuánto más barato sale el voraz ponderado.

| Caso | n | r | d | H(d) | P2: \|J\| | P2: óptimo | P2: razón | V1: \|J\| | V1: costo | V1: óptimo | V1: razón | Costo del J de la P2 | Ahorro de la V1 | P2 (ms) | V1 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 20 | 12 | 4 | 2.083 | 4 | 4 | 1.000 | 4 | 27 | 26 | 1.038 | 29 | 2 (7 %) | 0.060 | 0.060 |


### Parte 1 — DP por presupuesto y por valor, caso por caso

Las dos tablas son exactas: cuando las dos caben deben dar el mismo ahorro. «Celdas» es el tamaño de cada tabla; «—» = no cabe (límite 10000000 celdas) y no se corrió. La solución del caso es la tabla por presupuesto si cabe; si no, la de valor.

| Caso | n | B | D | Celdas presupuesto | Celdas valor | Ahorro presupuesto | Ahorro valor | ¿Coinciden? | Tiempo presupuesto (ms) | Tiempo valor (ms) | Solución del caso |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: | ---: | --- |
| 01_b_cero | 5 | 0 | 20 | 6 | 126 | 0 | 0 | sí | 0.027 | 0.049 | por presupuesto |
| 03_nada_cabe | 5 | 20 | 20 | 126 | 126 | 0 | 0 | sí | 0.023 | 0.029 | por presupuesto |
| 07_empates | 6 | 5 | 18 | 42 | 133 | 6 | 6 | sí | 0.029 | 0.031 | por presupuesto |
| 11_limite_n12 | 12 | 85 | 176 | 1118 | 2301 | 144 | 144 | sí | 0.358 | 0.348 | por presupuesto |
| 12_n13_sin_fuerza_bruta | 13 | 76 | 167 | 1078 | 2352 | 135 | 135 | sí | 0.318 | 0.381 | por presupuesto |
| 13_n20_b_moderado | 20 | 76 | 411 | 1617 | 8652 | 322 | 322 | sí | 0.502 | 1.417 | por presupuesto |
| 15_n50_b_un_tercio | 50 | 249 | 1212 | 12750 | 61863 | 786 | 786 | sí | 4.312 | 11.192 | por presupuesto |
| 17_n200_b_enorme_base_no_cabe | 200 | 50000000 | 386 | 10050000201 | 77787 | — | 282 | — | — | 14.924 | por valor |
| 19_n400_ninguna_tabla_cabe | 400 | 100000000 | 79674 | 40100000401 | 31949675 | — | — | — | — | — | no cabe ninguna |
| 20_valor_gana_n8_costos_enormes | 8 | 2265815 | 35 | 20392344 | 324 | — | 26 | — | — | 0.078 | por valor |
| 21_valor_gana_n12_presupuesto_en_millones | 12 | 21393847 | 36 | 278120024 | 481 | — | 22 | — | — | 0.108 | por valor |
| 24_valor_gana_n60_ahorro_unitario | 60 | 822648 | 60 | 50181589 | 3721 | — | 41 | — | — | 0.743 | por valor |
| 26_valor_gana_n150_base_no_cabe | 150 | 28419849 | 357 | 4291397350 | 54058 | — | 225 | — | — | 9.678 | por valor |
| 28_cruce_empate_b_igual_d | 20 | 347 | 347 | 7308 | 7308 | 343 | 343 | sí | 2.303 | 1.234 | por presupuesto |
| 29_presupuesto_gana_n10 | 10 | 41 | 208 | 462 | 2299 | 157 | 157 | sí | 0.143 | 0.324 | por presupuesto |
| 31_presupuesto_gana_n40_b_un_cuarto | 40 | 120 | 930 | 4961 | 38171 | 595 | 595 | sí | 1.569 | 6.313 | por presupuesto |
| 33_presupuesto_gana_n150 | 150 | 1048 | 4423 | 158399 | 668024 | 2970 | 2970 | sí | 58.796 | 138.445 | por presupuesto |
| 35_mezcla_d_cero_y_c_cero | 10 | 12 | 35 | 143 | 396 | 25 | 25 | sí | 0.061 | 0.075 | por presupuesto |
| 40_valor_gana_base_si_cabe_n30 | 30 | 24606 | 133 | 762817 | 4154 | 80 | 80 | sí | 247.736 | 0.732 | por presupuesto |
| entrada_G3_mochila_20_nodos | 20 | 72 | 165 | 1533 | 3486 | 55 | 55 | sí | 0.454 | 0.535 | por presupuesto |

### Parte 2 — tamaño de J de cada enfoque, caso por caso

Cada celda es el número de interacciones que eligió el enfoque; menos es mejor. «Óptimo» es el mínimo real por fuerza bruta (solo con n ≤ 12). Las claves son los ingredientes: e = esenciales, r = rareza, p = parejas; «todo» = los tres.

| Caso | n | r | H(d) | Óptimo | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 20 | 12 | 2.083 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Parte 2 — tiempo de cada enfoque (ms), caso por caso

| Caso | Voraz base | Esenciales | Rareza | Parejas | Esenciales + rareza | Esenciales + parejas | Rareza + parejas | Los tres (enfoque D) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| entrada_G3_mochila_20_nodos | 0.045 | 0.052 | 0.169 | 0.259 | 0.163 | 0.246 | 1.012 | 0.976 |

