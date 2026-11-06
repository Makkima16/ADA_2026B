# Evidencias de los casos propios

Salida de `run_all.py` sobre los casos propios de `Casos/casos_propios/`. Cada carpeta deja **20 casos**:

- `voraz/`: los 20 casos propios de la Parte 2.
- `pd/`: **20 de los 45** casos de la Parte 1 (los 44 propios más el ejemplo de la profesora), una selección representativa cuya lista
  está en `Casos/casos_propios/pd/resultados_propios.txt`: el ejemplo de la profesora, los bordes, el límite de la fuerza bruta,
  casos medianos, los que la tabla por presupuesto no resuelve (solo por valor y ninguna tabla), los que gana cada tabla y B = D.
  Los 45 casos de entrada se conservan; solo las evidencias están reducidas.

Cada carpeta tiene, por caso, la traza de cada parte que aplica (`*_parte1.txt`, `*_parte2.txt`, `*_variante1.txt` —solo completas, la
versión principal— y `*_variante1_parcial.txt` —la extensión con parciales, solo en los casos que las traen—) y de todos los enfoques
(`*_parte1_enfoques.txt`, `*_parte2_enfoques.txt`), más `resumen.csv` (una fila por caso y por enfoque), `comparacion.md` (empieza por el
resumen y deja las tablas por caso al final), `resumen_enfoques.json` (los resúmenes por parte que usa el visor) y `version.txt`
(commit, fecha y comando).

Se regeneran completas con:

```
python3 run_all.py --casos Casos/casos_propios/pd --lista Casos/casos_propios/pd/resultados_propios.txt --salida Resultados/resultados_propios/pd
python3 run_all.py --casos Casos/casos_propios/voraz --salida Resultados/resultados_propios/voraz
```

## Casos de una sola parte: «no aplica», no error

Los casos propios son de **una sola parte** a propósito, y `run_all.py` corre las tres partes sobre cada archivo. Cuando un caso no trae
los datos de una parte, esa parte figura como **«no aplica»** en `resumen.csv` (con la columna de la traza vacía: no se crea archivo) y se
analiza solo la que sí trae. Igual pasa con los archivos que se suban en el visor. Un archivo mal formado, o que no trae datos de ninguna
de las dos partes, sí da `ERROR`.

| Carpeta | Filas «no aplica» | Motivo |
| --- | --- | --- |
| `pd/` | `parte2` y `variante1` (19 casos cada una; el ejemplo de la profesora trae las dos partes) | El caso no trae `categorias_riesgo`: solo tiene datos de la Parte 1. |
| `voraz/` | `parte1` (20 casos) | El caso no trae el presupuesto B ni las duraciones: solo tiene datos de la Parte 2. |

La única fila con `ERROR` es la `parte1` de `pd/19_n400_ninguna_tabla_cabe`: error a propósito. La tabla por presupuesto (40 100 000 401
celdas) y la tabla por valor (31 949 675 celdas) superan el límite de 10 000 000 celdas, y el mensaje dice que la tabla es demasiado
grande y no cabe.

Los casos de `pd/` donde la tabla por presupuesto no cabe (17, 20, 21, 24 y 26) **no** dan error: se resuelven solo con la DP por valor,
y la fila `parte1` lo indica con «[solo por valor: la tabla por presupuesto no cabe]».

Las evidencias de la entrega son las de los casos de la profesora, no estas.
