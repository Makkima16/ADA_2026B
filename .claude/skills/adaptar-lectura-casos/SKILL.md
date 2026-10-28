---
name: adaptar-lectura-casos
description: Guía para adaptar la lectura de los casos de la profesora cuando se conozca su formato, tocando únicamente el módulo de lectura y nunca la lógica de los algoritmos. Úsalo cuando lleguen los casos o cambie su formato.
---

# Adaptar la lectura de los casos

Regla del proyecto: si un caso no encaja, se adapta la lectura de entrada, **nunca** el algoritmo. Los archivos de `casos/` son de solo lectura.

1. **Mirar antes de escribir.** Lee los archivos de `casos/` y describe el formato real que encuentras (campos, separadores, qué trae cada parte, si hay costos a_j para la variante). Si el formato sigue sin ser claro, pregunta una vez en vez de asumir.
2. **Un solo módulo.** Toda la lectura vive en un único módulo de `src/ruta/` (por ejemplo `lectura.py`). Los algoritmos reciben estructuras ya leídas (listas de t_i, c_i, d_i y B; o r y la lista de S_j, con a_j si aplica) y no saben nada del archivo.
3. **Validar al leer.** Comprueba las restricciones de la formalización: enteros no negativos, 0 ≤ d_i ≤ t_i, B entero, índices de categorías dentro de 1..r, a_j > 0 en la variante. Si algo falla, el error indica caso, línea y qué restricción se rompió.
4. **Identificar por nombre.** Cada caso conserva el nombre del archivo para la salida y la traza.
5. **Probar.** Añade en `tests/` pruebas de lectura con un caso pequeño por parte, y corre `python3 -m pytest tests/`.
6. **Documentar.** Describe el formato de entrada en el manual técnico (sección de formatos) y en el README.
7. **Regenerar.** Si cambió `src/`, regenera todo `resultados/` con la skill `correr-casos`.

Si para que un caso funcione parece necesario cambiar un algoritmo, detente y avisa en vez de hacerlo.
