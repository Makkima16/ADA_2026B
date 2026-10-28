---
name: manual-tecnico
description: Redacta o actualiza el manual técnico del proyecto leyendo el código real de src/. Úsalo cuando se pida crear, completar o sincronizar el manual técnico de la entrega.
---

# Manual técnico

El manual es un documento aparte del informe. Debe describir **lo que el código hace de verdad**, así que primero lee `src/`, `run_all.py` y `README.md`.

Secciones obligatorias (las pide la guía de la entrega):

1. **Algoritmo:** DP de la Parte 1 (recurrencia y reconstrucción), voraz de la Parte 2, voraz ponderado. Con su T(n) y su garantía citada (Johnson 1974; Chvátal 1979).
2. **Estructura del código:** árbol de carpetas y qué hace cada módulo y cada función pública (qué recibe, qué devuelve).
3. **Formatos de entrada y salida:** de los casos, del resultado y de la traza, con un ejemplo corto de cada uno.
4. **Pasos de ejecución:** comandos exactos, versión de Python y dependencias.
5. **Limitaciones:** pseudo-polinomialidad de la DP, voraz no siempre óptimo, fuerza bruta solo para n pequeño, y todo lo que no esté implementado todavía.

Reglas:

- No inventes formatos: si algo no existe en el código, escribe "pendiente" y dilo al final.
- Si el manual y el código se contradicen, el código manda; corrige el manual y avisa.
- Escribe en español sencillo; el equipo debe poder defender cada sección en la sustentación.
