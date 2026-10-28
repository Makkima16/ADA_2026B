---
name: formalizar-problema
description: Guía para escribir la formalización de un problema del proyecto (Parte 1, Parte 2 o variante ponderada) con tamaño de entrada, entrada, salida, restricciones, objetivo y versión de decisión. Úsalo cuando se vaya a redactar o revisar una formalización para el informe.
---

# Formalizar un problema

Cada formalización del informe debe tener, en este orden, las seis partes siguientes. Usa la notación única del proyecto: n, B, r, t_i, c_i, d_i, S_j, a_j, A, J.

1. **Tamaño de la entrada.** Qué parámetros miden la instancia y una frase de por qué (Parte 1: n y B; Parte 2 y variante: n y r). Aclara que B ocupa log₂B bits.
2. **Entrada.** Qué datos recibe, con sus tipos.
3. **Salida.** Qué conjunto se devuelve (A en la Parte 1; J en la Parte 2 y la variante).
4. **Restricciones** (la guía nueva las pide explícitas, no basta con el objetivo):
   - Parte 1: Σ c_i de A ≤ B; 0 ≤ d_i ≤ t_i; todos los valores son enteros no negativos.
   - Parte 2: la unión de los S_j de J es U = {1, …, r}; factibilidad previa: la unión de todos los S_j es U (verificable en O(n·r)).
   - Variante: igual que la Parte 2 más a_j > 0.
5. **Objetivo.** Parte 1: minimizar Σ t_i − Σ d_i de A (equivale a maximizar el ahorro). Parte 2: minimizar |J|. Variante: minimizar Σ a_j de J.
6. **Versión de decisión.** Parte 1: dado L, ¿existe A con costo ≤ B y duración ≤ L? Parte 2: dado k, ¿existe J con |J| ≤ k que cubra todo? Variante: dado un costo máximo, ¿existe J que cubra todo con costo ≤ ese valor?

Revisa al final: ¿las restricciones están escritas como condiciones y no solo mencionadas en prosa? ¿La versión de decisión es la que usan las reducciones? ¿La notación coincide con el resto del informe?
