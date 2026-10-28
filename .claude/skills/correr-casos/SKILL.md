---
name: correr-casos
description: Corre toda la solución base (y la variante ponderada) sobre los casos de la profesora en casos/ y genera las evidencias en resultados/ (resultado, tiempo y traza por caso). Úsalo cuando se pida generar o regenerar las evidencias de la entrega.
---

# Correr los casos y generar evidencias

1. Confirma que existe `casos/` y que tiene archivos. Si el formato de los casos todavía no está definido en `CLAUDE.md`, detente y pregunta; no lo inventes.
2. Confirma que el árbol de git está limpio o que los cambios pendientes son intencionales (`git status`). Las evidencias deben corresponder a una versión concreta del código.
3. Corre `python3 run_all.py --casos casos/ --salida resultados/`. Si `run_all.py` no existe, créalo siguiendo la convención de `CLAUDE.md`.
4. Verifica que **para cada caso** existan: resultado, tiempo (medido con `time.perf_counter`) y traza.
   - Parte 1: decisiones/estados de la DP, etapas aceleradas y costos.
   - Parte 2 y variante: elección de cada paso del voraz y cobertura final.
5. Guarda en `resultados/` el hash del commit con el que se generaron (`git rev-parse --short HEAD`).
6. Entrega una tabla resumen: caso, parte, resultado, tiempo en segundos, ruta de la traza.

Nunca edites la lógica de los algoritmos para que un caso funcione. Si un caso falla, reporta cuál y por qué.
