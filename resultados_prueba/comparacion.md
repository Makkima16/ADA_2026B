# Comparación de resultados

Versión del código: 97a6e43 (con cambios sin commit) · Generado: 2026-11-05 15:31:26 · Casos: 22

La fuerza bruta (óptimo real) solo se calcula con n ≤ 12; con n mayor aparece «—».

## Parte 1 — Aceleración de la cadena (DP exacta)

La DP es exacta: su ahorro debe coincidir siempre con el de la fuerza bruta (que solo se calcula con n ≤ 12). «Reducción» = cuánto bajó la duración de la cadena; «Presupuesto usado» = costo de las etapas aceleradas sobre B.

| Caso | n | B | Etapas aceleradas | Costo usado | Presupuesto usado | Ahorro DP | Ahorro fuerza bruta | ¿Coinciden? | Duración inicial → final | Reducción | Tiempo DP (ms) |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | :---: | --- | ---: | ---: |
| prueba_n10_r06_ralo | 10 | 24 | [2, 3, 4, 7] | 24 | 100 % | 27 | 27 | sí | 82 → 55 | 32.9 % | 0.058 |
| prueba_n10_r15_denso | 10 | 22 | [2, 5, 7, 8] | 20 | 91 % | 18 | 18 | sí | 68 → 50 | 26.5 % | 0.169 |
| prueba_n11_r07_ralo | 11 | 30 | [1, 2, 5, 8, 10] | 27 | 90 % | 20 | 20 | sí | 62 → 42 | 32.3 % | 0.071 |
| prueba_n11_r14_denso | 11 | 19 | [1, 2, 3, 5, 9, 11] | 19 | 100 % | 35 | 35 | sí | 81 → 46 | 43.2 % | 0.048 |
| prueba_n12_r08_ralo | 12 | 30 | [3, 7, 8, 9, 12] | 27 | 90 % | 35 | 35 | sí | 94 → 59 | 37.2 % | 0.079 |
| prueba_n12_r13_denso | 12 | 29 | [1, 5, 6, 8, 10, 11] | 27 | 93 % | 30 | 30 | sí | 90 → 60 | 33.3 % | 0.096 |
| prueba_n13_r09_ralo | 13 | 21 | [2, 3, 10, 12, 13] | 21 | 100 % | 44 | — | — | 105 → 61 | 41.9 % | 0.067 |
| prueba_n13_r12_denso | 13 | 25 | [1, 3, 4, 5, 6, 11, 13] | 25 | 100 % | 37 | — | — | 95 → 58 | 38.9 % | 0.074 |
| prueba_n14_r10_ralo | 14 | 22 | [2, 5, 7, 11, 12, 14] | 21 | 95 % | 33 | — | — | 86 → 53 | 38.4 % | 0.069 |
| prueba_n14_r11_denso | 14 | 24 | [1, 2, 8, 9, 10, 12] | 21 | 88 % | 22 | — | — | 88 → 66 | 25.0 % | 0.074 |
| prueba_n15_r10_denso | 15 | 26 | [2, 5, 10, 12, 13] | 26 | 100 % | 27 | — | — | 86 → 59 | 31.4 % | 0.149 |
| prueba_n15_r11_ralo | 15 | 26 | [1, 2, 4, 8, 10, 11, 15] | 26 | 100 % | 37 | — | — | 105 → 68 | 35.2 % | 0.129 |
| prueba_n16_r09_denso | 16 | 32 | [3, 4, 8, 10, 11, 13, 15, 16] | 32 | 100 % | 45 | — | — | 140 → 95 | 32.1 % | 0.120 |
| prueba_n16_r12_ralo | 16 | 31 | [3, 4, 5, 6, 7, 8, 10, 15, 16] | 31 | 100 % | 38 | — | — | 93 → 55 | 40.9 % | 0.105 |
| prueba_n17_r08_denso | 17 | 22 | [2, 3, 6, 7, 12, 13, 17] | 22 | 100 % | 40 | — | — | 110 → 70 | 36.4 % | 0.151 |
| prueba_n17_r13_ralo | 17 | 31 | [1, 2, 3, 5, 9, 10, 11, 15, 17] | 31 | 100 % | 33 | — | — | 119 → 86 | 27.7 % | 0.117 |
| prueba_n18_r07_denso | 18 | 36 | [1, 2, 4, 6, 7, 9, 10, 16, 18] | 36 | 100 % | 58 | — | — | 161 → 103 | 36.0 % | 0.135 |
| prueba_n18_r14_ralo | 18 | 32 | [1, 2, 7, 13, 16, 18] | 32 | 100 % | 37 | — | — | 127 → 90 | 29.1 % | 0.209 |
| prueba_n19_r06_denso | 19 | 47 | [1, 2, 4, 5, 8, 9, 11, 12, 13, 15, 16] | 47 | 100 % | 61 | — | — | 135 → 74 | 45.2 % | 0.188 |
| prueba_n19_r15_ralo | 19 | 38 | [4, 5, 7, 11, 12, 14, 17, 18, 19] | 38 | 100 % | 64 | — | — | 141 → 77 | 45.4 % | 0.190 |
| prueba_n20_r06_ralo | 20 | 45 | [1, 2, 3, 5, 11, 12, 14, 17] | 40 | 89 % | 48 | — | — | 138 → 90 | 34.8 % | 0.259 |
| prueba_n20_r15_denso | 20 | 40 | [1, 3, 4, 7, 8, 9, 12, 14, 16, 17, 19] | 40 | 100 % | 60 | — | — | 122 → 62 | 49.2 % | 0.292 |

## Parte 2 (mínimo número) vs Variante 1 (mínimo costo)

«Costo del J de la Parte 2» = lo que costaría auditar, con los costos a_j, las interacciones que elige el voraz de la Parte 2. «Ahorro» = cuánto más barato sale el voraz ponderado.

| Caso | n | r | d | H(d) | P2: \|J\| | P2: óptimo | P2: razón | V1: \|J\| | V1: costo | V1: óptimo | V1: razón | Costo del J de la P2 | Ahorro de la V1 | P2 (ms) | V1 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| prueba_n10_r06_ralo | 10 | 6 | 3 | 1.833 | 4 | 4 | 1.000 | 4 | 12 | 12 | 1.000 | 12 | 0 (0 %) | 0.019 | 0.025 |
| prueba_n10_r15_denso | 10 | 15 | 11 | 3.020 | 2 | 2 | 1.000 | 3 | 29 | 29 | 1.000 | 33 | 4 (12 %) | 0.046 | 0.028 |
| prueba_n11_r07_ralo | 11 | 7 | 4 | 2.083 | 3 | 3 | 1.000 | 5 | 17 | 15 | 1.133 | 21 | 4 (19 %) | 0.013 | 0.026 |
| prueba_n11_r14_denso | 11 | 14 | 7 | 2.593 | 4 | 4 | 1.000 | 5 | 38 | 37 | 1.027 | 52 | 14 (27 %) | 0.034 | 0.049 |
| prueba_n12_r08_ralo | 12 | 8 | 5 | 2.283 | 3 | 3 | 1.000 | 6 | 21 | 19 | 1.105 | 24 | 3 (12 %) | 0.018 | 0.047 |
| prueba_n12_r13_denso | 12 | 13 | 10 | 2.929 | 3 | 3 | 1.000 | 4 | 31 | 30 | 1.033 | 52 | 21 (40 %) | 0.024 | 0.030 |
| prueba_n13_r09_ralo | 13 | 9 | 5 | 2.283 | 3 | — | — | 5 | 21 | — | — | 22 | 1 (5 %) | 0.022 | 0.029 |
| prueba_n13_r12_denso | 13 | 12 | 9 | 2.829 | 2 | — | — | 5 | 27 | — | — | 63 | 36 (57 %) | 0.016 | 0.037 |
| prueba_n14_r10_ralo | 14 | 10 | 5 | 2.283 | 4 | — | — | 6 | 26 | — | — | 59 | 33 (56 %) | 0.033 | 0.038 |
| prueba_n14_r11_denso | 14 | 11 | 8 | 2.718 | 3 | — | — | 4 | 37 | — | — | 52 | 15 (29 %) | 0.021 | 0.032 |
| prueba_n15_r10_denso | 15 | 10 | 7 | 2.593 | 3 | — | — | 4 | 23 | — | — | 43 | 20 (47 %) | 0.022 | 0.030 |
| prueba_n15_r11_ralo | 15 | 11 | 5 | 2.283 | 4 | — | — | 6 | 30 | — | — | 28 | -2 (-7 %) | 0.024 | 0.043 |
| prueba_n16_r09_denso | 16 | 9 | 5 | 2.283 | 3 | — | — | 4 | 16 | — | — | 18 | 2 (11 %) | 0.029 | 0.049 |
| prueba_n16_r12_ralo | 16 | 12 | 6 | 2.450 | 4 | — | — | 5 | 19 | — | — | 40 | 21 (52 %) | 0.024 | 0.040 |
| prueba_n17_r08_denso | 17 | 8 | 6 | 2.450 | 3 | — | — | 4 | 17 | — | — | 17 | 0 (0 %) | 0.030 | 0.083 |
| prueba_n17_r13_ralo | 17 | 13 | 6 | 2.450 | 4 | — | — | 7 | 50 | — | — | 47 | -3 (-6 %) | 0.024 | 0.049 |
| prueba_n18_r07_denso | 18 | 7 | 4 | 2.083 | 3 | — | — | 5 | 13 | — | — | 27 | 14 (52 %) | 0.026 | 0.054 |
| prueba_n18_r14_ralo | 18 | 14 | 6 | 2.450 | 5 | — | — | 8 | 79 | — | — | 69 | -10 (-14 %) | 0.035 | 0.052 |
| prueba_n19_r06_denso | 19 | 6 | 5 | 2.283 | 2 | — | — | 3 | 9 | — | — | 10 | 1 (10 %) | 0.016 | 0.028 |
| prueba_n19_r15_ralo | 19 | 15 | 9 | 2.829 | 3 | — | — | 5 | 39 | — | — | 68 | 29 (43 %) | 0.022 | 0.039 |
| prueba_n20_r06_ralo | 20 | 6 | 3 | 1.833 | 3 | — | — | 5 | 11 | — | — | 19 | 8 (42 %) | 0.037 | 0.036 |
| prueba_n20_r15_denso | 20 | 15 | 10 | 2.929 | 2 | — | — | 3 | 24 | — | — | 57 | 33 (58 %) | 0.040 | 0.039 |

## Resumen

- **Parte 1:** la DP coincidió con la fuerza bruta en 6 de 6 casos con n ≤ 12 (debe ser siempre: es exacta). La duración de la cadena bajó en promedio 36.0 % (entre 25.0 % y 49.2 %), usando en promedio el 97 % del presupuesto B.
- **Parte 2:** el voraz fue óptimo en 6 de 6 casos con fuerza bruta; razón máxima 1.000; casos que superan H(d): 0.
- **Variante 1:** el voraz ponderado fue óptimo en 2 de 6 casos con fuerza bruta; razón máxima 1.133; casos que superan H(d): 0.
- **Parte 2 vs Variante 1:** la variante salió más barata que el J de la Parte 2 en 17 de 22 casos (ahorro medio 25 %), igual en 2 y más cara en 3.

