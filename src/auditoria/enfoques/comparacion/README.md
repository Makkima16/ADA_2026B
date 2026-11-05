# Comparación de enfoques

`experimento.py` compara, sobre las mismas instancias y con semilla fija, el voraz base, el enfoque A
(esenciales), el enfoque B (parejas), el enfoque C (rareza) y el enfoque D (todo junto) contra el óptimo exacto por fuerza bruta (solo con n ≤ 12).

Secciones de la salida:
1. Instancias aleatorias de tres densidades (ralo p = 0.10, medio p = 0.25, denso p = 0.45): cuántas
   veces cada enfoque mejora, empata o empeora al voraz base, cuántas veces no es óptimo, razón al óptimo
   y si se pasa de la cota H(d).
2. Familia de cebos (óptimo = 2) donde el voraz base se equivoca y las esenciales no ayudan.
3. La instancia más chica hallada donde cada enfoque empeora al voraz base.
4. Instancias grandes (n de 20 a 30): sin mínimo real, solo mejora, igual y peor frente al voraz base, y tiempos.
5. Tiempos con instancias de tamaño creciente (n = r de 20 a 160).
6. Contribución de cada ingrediente (`ablacion.py`): las 8 combinaciones de esenciales, rareza y parejas, con cuántos casos no óptimos deja cada una.

```
python3 src/auditoria/enfoques/comparacion/experimento.py --instancias 3000 --semilla 2026
```

La función `comparar_caso` también la usa el visor local (`frontend/`). Tarda unos 20 s con 3000 instancias por familia.
