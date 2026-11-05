# Enfoque B — parejas (voraz con vista al futuro de profundidad 2)

En cada paso se evalúa qué **par** de interacciones cubre más categorías nuevas juntas y se compromete la
que más cubre por sí sola; luego se vuelve a evaluar. Ante igual cobertura se prefieren menos
interacciones (una sola antes que un par); después, el menor índice.

- Código: `vision_futuro.py` (`paso_futuro`, `voraz_futuro`).
- Costo: O(n²·r) por paso y a lo sumo min(n, r) pasos: T(n, r) = O(n²·r·min(n, r)), un factor n más que
  el voraz base.
- Garantía: la prueba H(d) del voraz base **no aplica** (la interacción comprometida no es necesariamente la
  de mayor cobertura). Solo hay evidencia empírica (`comparacion/`).
- Límite: un lookahead de profundidad fija puede engañarse con cadenas de cebos más largas; no se afirma que
  sea óptimo, solo que en las familias medidas queda más cerca del óptimo que el voraz base.
