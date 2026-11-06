# Casos propios de la Parte 1 (programación dinámica)

Casos de prueba propios, **no** de la profesora. Mismo formato JSON que el ejemplo de la profesora
(`entrada_G3_mochila_20_nodos.json`, que también está en esta carpeta); la clave `descripcion` dice qué prueba cada
caso y el resultado calculado con el código del proyecto. Se generan con semilla fija:

```
python3 Casos/casos_propios/pd/generar_casos.py
```

| Caso | n | B | Qué prueba |
| --- | --- | --- | --- |
| `01_b_cero.json` | 5 | 0 | Presupuesto B = 0: no cabe ninguna etapa con costo positivo; el ahorro es 0. |
| `02_todo_cabe.json` | 5 | 100 | El presupuesto sobra (B >= suma de costos): se aceleran todas las etapas y no hay nada que elegir. |
| `03_nada_cabe.json` | 5 | 20 | Todas las etapas cuestan más que B: ninguna se puede acelerar. |
| `04_acelerar_gratis.json` | 5 | 5 | Etapas con costo 0 y ahorro positivo: siempre se aceleran; el presupuesto se reparte entre las demás. |
| `05_sin_ahorro.json` | 3 | 10 | Ninguna etapa ahorra nada (d_i = 0): no conviene acelerar y el ahorro es 0 aunque el presupuesto alcance. |
| `06_razon_falla.json` | 3 | 10 | Tomar siempre lo que más ahorra por unidad de costo NO es óptimo: toma E01 (ahorra 8) y ya no caben las otras dos, que juntas ahorran 12. |
| `07_empates.json` | 6 | 5 | Seis etapas idénticas: hay muchas soluciones óptimas con el mismo ahorro (se aceleran 2). |
| `08_d_igual_t.json` | 5 | 7 | Cada etapa que se acelera pasa a durar 0 (d_i = t_i, el máximo permitido). |
| `09_b_grande_d_chico.json` | 12 | 40000 | Costos grandes y ahorros chicos (D pequeña, B grande): la tabla por valor es mucho más chica que la de presupuesto. |
| `10_b_chico_d_grande.json` | 12 | 25 | Presupuesto chico y ahorros grandes (B pequeño, D grande): la tabla por presupuesto es la más chica. |
| `11_limite_n12.json` | 12 | 85 | Justo en el límite de la fuerza bruta (n = 12): se puede comparar con el óptimo exacto. |
| `12_n13_sin_fuerza_bruta.json` | 13 | 76 | n = 13: la fuerza bruta ya no se corre (solo con n <= 12). |
| `13_n20_b_moderado.json` | 20 | 76 | n = 20 con presupuesto de la mitad del costo total. |
| `14_n30.json` | 30 | 219 | n = 30 con presupuesto de la mitad del costo total. |
| `15_n50_b_un_tercio.json` | 50 | 249 | n = 50 con presupuesto de un tercio del costo total. |
| `16_n100.json` | 100 | 733 | n = 100 con presupuesto de la mitad del costo total. |
| `17_n200_b_enorme_base_no_cabe.json` | 200 | 50000000 | Costos enormes: la tabla por presupuesto NO cabe en memoria, la tabla por valor sí. Solo se resuelve con el enfoque por valor. |
| `18_n300_b2000_tabla_grande.json` | 300 | 2000 | Tabla de más de 600 mil celdas: el visor la omite y muestra solo las decisiones. |
| `19_n400_ninguna_tabla_cabe.json` | 400 | 100000000 | CASO DE ERROR ESPERADO: B y D enormes, ninguna de las dos tablas cabe en el tope de memoria y la solución lo avisa con un error. |
| `20_valor_gana_n8_costos_enormes.json` | 8 | 2265815 | Costos de cientos de miles y ahorros de 1 a 10: la tabla por valor es mucho más chica. Con n = 8 se puede comparar con la fuerza bruta. |
| `21_valor_gana_n12_presupuesto_en_millones.json` | 12 | 21393847 | Presupuesto de decenas de millones y ahorros de 1 a 5, con n = 12: gana la tabla por valor y se comprueba con la fuerza bruta. |
| `22_valor_gana_n25_costos_en_miles.json` | 25 | 57793 | Costos de 1.000 a 9.999 (por ejemplo, dinero) y ahorros de 1 a 9 (por ejemplo, días): gana la tabla por valor. |
| `23_valor_gana_n40_dinero_contra_dias.json` | 40 | 109491 | Costos de 1.200 a 9.800 y ahorros de 1 a 9, con n = 40: el caso típico de pagar mucho para ahorrar pocos días. |
| `24_valor_gana_n60_ahorro_unitario.json` | 60 | 822648 | Todas las etapas ahorran exactamente 1 (D = n): la tabla por valor tiene n + 1 columnas sin importar lo grande que sea B. |
| `25_valor_gana_n100.json` | 100 | 2905991 | n = 100, costos de 10.000 a 100.000 y ahorros de 1 a 5: la tabla por presupuesto tendría cientos de millones de celdas. |
| `26_valor_gana_n150_base_no_cabe.json` | 150 | 28419849 | n = 150 con costos de cientos de miles: la tabla por presupuesto NO cabe en memoria y la de valor sí. |
| `27_valor_gana_n300_ahorros_chicos.json` | 300 | 7611503 | n = 300 con costos de 1.000 a 100.000 y ahorros de 1 a 3: solo se resuelve cómodamente por valor. |
| `28_cruce_empate_b_igual_d.json` | 20 | 347 | El presupuesto B es exactamente la suma de los ahorros D: las dos tablas tienen el mismo tamaño y se elige la base (empate). |
| `29_presupuesto_gana_n10.json` | 10 | 41 | n = 10, ahorros mayores que los costos y B de la mitad del costo total: gana la tabla por presupuesto. Se compara con la fuerza bruta. |
| `30_presupuesto_gana_n15.json` | 15 | 89 | n = 15 con costos y ahorros de escala parecida (como el ejemplo de la profesora). |
| `31_presupuesto_gana_n40_b_un_cuarto.json` | 40 | 120 | n = 40 con un presupuesto de un cuarto del costo total. |
| `32_presupuesto_gana_n75.json` | 75 | 675 | n = 75 con presupuesto de la mitad del costo total. |
| `33_presupuesto_gana_n150.json` | 150 | 1048 | n = 150 con presupuesto de un tercio del costo total. |
| `34_presupuesto_gana_n250_b1500.json` | 250 | 1500 | n = 250 con B = 1.500 (la tabla tiene unas 376 mil celdas: el visor muestra solo las decisiones). |
| `35_mezcla_d_cero_y_c_cero.json` | 10 | 12 | Mezcla de etapas que no ahorran nada (d = 0), etapas gratis (c = 0) y etapas normales. |
| `36_b_casi_todo.json` | 12 | 93 | El presupuesto alcanza para casi todo (B = costo total − 1): hay que dejar fuera una sola etapa, la que menos ahorra por lo que cuesta. |
| `37_valor_gana_base_si_cabe_n10.json` | 10 | 6481 | n = 10: la tabla por presupuesto tiene unas 70 mil celdas y corre sin problema, pero la de valor tiene unas 300. Se compara con la fuerza bruta. |
| `38_valor_gana_base_si_cabe_n12.json` | 12 | 22405 | n = 12: la tabla por presupuesto (unas 300 mil celdas) cabe y corre; la de valor tiene unas 700. Se compara con la fuerza bruta. |
| `39_valor_gana_base_si_cabe_n20.json` | 20 | 18607 | n = 20: la base (unas 400 mil celdas) cabe y corre; la tabla por valor es unas 300 veces más chica. |
| `40_valor_gana_base_si_cabe_n30.json` | 30 | 24606 | n = 30: la base tiene unas 760 mil celdas y corre; la tabla por valor, unas 4 mil. |
| `41_valor_gana_base_si_cabe_n60.json` | 60 | 16585 | n = 60: la base tiene alrededor de un millón de celdas y corre; la tabla por valor, menos de 8 mil. |
| `42_valor_gana_base_si_cabe_n50_ahorro_unitario.json` | 50 | 41360 | n = 50 y todos los ahorros valen 1: la base tiene unos 2 millones de celdas y corre (tarda menos de 1 segundo); la tabla por valor tiene solo 51 columnas. |
| `43_valor_gana_base_si_cabe_n100_la_base_tarda.json` | 100 | 49627 | n = 100: la base tiene unos 5 millones de celdas (cabe en el tope, pero tarda casi 2 segundos y ocupa unos 190 MB); la de valor tarda milésimas de segundo. |
| `44_valor_gana_base_si_cabe_ventaja_chica.json` | 20 | 393 | Cerca del cruce: B es solo 1,5 veces la suma de los ahorros D. La tabla por valor gana, pero por poco, y las dos son chicas. |

Los casos con `valor_gana` en el nombre son aquellos donde la tabla por valor es la más chica (en `22`, `23`, `37`, `38`, `39`, `40`, `41`, `42`, `43`, `44` la tabla por presupuesto **también cabe y puede correr**, así que se pueden comparar las dos; en los demás solo cabe la de valor); los de `presupuesto_gana`, donde lo es la de presupuesto; el 28 es el empate (se elige la base).

El caso `19_n400_ninguna_tabla_cabe` **debe dar error** (ninguna tabla cabe); todos los demás se resuelven. Las pruebas están en `tests/test_casos_propios_pd.py`.
