# Evidencias de la entrega (resultados/)

Salida de `python3 run_all.py --casos casos/ --salida resultados/`. Se regenera completa en cada corrida; `version.txt`
dice con qué commit se generó. Por cada caso, identificado por su nombre:

| Archivo | Contenido |
| --- | --- |
| `<caso>_parte1.txt` | Parte 1: etapas aceleradas, costo, ahorro, duración final, tiempo, decisiones de la DP y tabla (si B ≤ 100) |
| `<caso>_parte1_enfoques.txt` | Las dos tablas de la DP (por presupuesto y por valor): celdas, resultado y tiempo |
| `<caso>_parte2.txt` | Parte 2: traza del voraz paso a paso, cobertura final, óptimo y cota H(d) |
| `<caso>_parte2_enfoques.txt` | Las ocho combinaciones del voraz y su comparación con el voraz base y el óptimo |
| `<caso>_variante1.txt` | Variante 1 (solo completas): traza del voraz ponderado y costo |
| `<caso>_variante1_parcial.txt` | Variante 1 con parciales (extensión) |
| `resumen.csv`, `comparacion.md`, `resumen_enfoques.json` | Resumen por caso y por enfoque, tablas comparativas y los mismos datos en JSON |
| `version.txt` | Commit, fecha, versión de Python, comando y número de casos |

Los tiempos son de una sola ejecución y dependen de la máquina.
