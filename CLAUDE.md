# Proyecto ADA 2026-B — Grupo 3 (Ruta crítica y auditoría)

Proyecto semestral de Análisis y Diseño de Algoritmos, Universidad de Caldas.
Equipo de 3 personas. Idioma de trabajo: **español** (código en inglés o español, pero comentarios, informe y manual en español).

El enunciado completo está en @context/Proyecto_ADAG3.md. Léelo antes de tocar algoritmos o escribir pruebas formales.

## Qué es el proyecto

Dos problemas independientes, ambos NP-difíciles:

1. **Parte 1 — Aceleración de la cadena (Mochila 0/1).** n etapas en serie con duración t_i, costo de acelerar c_i y reducción d_i (0 ≤ d_i ≤ t_i). Presupuesto entero B. Maximizar Σ d_i de las etapas aceleradas con Σ c_i ≤ B. Duración final = Σ t_i − Σ d_i.
   - Exacto: programación dinámica, T(n, B) = O(n·B), **pseudo-polinomial**.
   - Reducción de NP-dureza: **desde Mochila 0/1** (c_i = w_i, d_i = v_i, t_i = v_i, B = W, L = Σv_i − V).
2. **Parte 2 — Cobertura mínima de auditoría (Set Cover).** n interacciones, r categorías de riesgo; cada interacción cubre un subconjunto. Minimizar cuántas se auditan para cubrir las r categorías.
   - Aproximado: voraz (elige la que cubre más categorías aún no cubiertas), garantía H(d) = 1 + 1/2 + … + 1/d ≤ ln r + 1 (Johnson 1974; Chvátal 1979).
   - Eficiencia del voraz: T(n, r) = O(n·r·min(n, r)). Es más ajustada que O(n·r²) y ambas son correctas; usar la ajustada y mencionar la otra.
   - Exacto (solo para verificar, n pequeño): fuerza bruta.
   - Reducción de NP-dureza: **desde Cobertura de Vértices** (aristas = categorías, vértices = interacciones, mismo k).
   - Verificar factibilidad (la unión cubre las r categorías) en O(n·r) **antes** de correr cualquier algoritmo.

## Alcance de la PRIMERA ENTREGA (lo que se construye ahora)

Entregables: informe, repositorio, manual técnico y evidencias. Todo debe corresponder a **la misma versión**.

- **Informe (un solo documento):** formalización de las dos partes (tamaño de la entrada, entrada, salida, objetivo **y restricciones**) y prueba formal de NP-dureza por reducción polinomial de ambas.
- **Repositorio:** código del problema **base** (sin variantes, salvo la ponderada), dependencias, README e instrucciones de ejecución.
- **Manual técnico:** algoritmo, estructura del código, formatos de entrada/salida, pasos de ejecución y limitaciones.
- **Casos de la profesora:** ejecutar la solución base con ellos y entregar, **por caso**: resultado, tiempo y traza.
  - Traza Parte 1: decisiones/estados de la DP, etapas aceleradas, costos.
  - Traza Parte 2: elección en cada paso del voraz y cobertura final.
- **Por ser grupo de 3:** además implementar la **variante 1 — auditoría ponderada por costo** (cubrir todas las categorías con costo total mínimo; el voraz elige la interacción de menor costo por categoría nueva cubierta; la cota H(d) se conserva, Chvátal 1979). Incluir resultados, tiempos, traza de elecciones y análisis de complejidad.

**Fuera de alcance por ahora:** variante de presupuesto conjunto, variante de etapas en paralelo (DAG), validación experimental con gráficas de crecimiento. Son de entregas posteriores; no las implementes sin que se pida.

**Pendiente:** el formato de los casos de la profesora aún no se conoce. No lo inventes: si hace falta decidir cómo se leen, pregunta o deja la lectura aislada en un solo módulo.

## Estructura del repositorio (convención)

```
CLAUDE.md
README.md
requirements.txt
run_all.py            # corre todos los casos y genera evidencias
context/                 # enunciado, guía de entrega, manual técnico, informe
src/ruta/             # algoritmos (aceleracion, auditoria, ponderada) + lectura de casos + traza
casos/                # casos de la profesora (SOLO LECTURA)
resultados/           # salida, tiempo y traza por caso (se regenera completo)
tests/                # pruebas (DP vs fuerza bruta, voraz vs óptimo y cota H(d))
```

## Reglas de código

- Python 3.8+. Preferir solo librería estándar; si se agrega una dependencia, registrarla en `requirements.txt`.
- **Reproducible:** semillas fijas en todo generador aleatorio. Mismo código + mismos casos = mismos resultados.
- **No editar la lógica de los algoritmos para adaptarlos a un caso.** Si un caso no encaja, se adapta la lectura de entrada, nunca el algoritmo.
- Medir tiempos con `time.perf_counter()`. Cada caso se identifica por nombre en la salida.
- Fuerza bruta solo para verificar, con n ≤ ~12.
- Separar siempre algoritmo, lectura de entrada y escritura de traza, para poder reutilizarlos en las variantes.
- Notación única en todo el proyecto: n, B, r, t_i, c_i, d_i, S_j, a_j (costo de auditar j), A (etapas aceleradas), J (interacciones auditadas).

## Comandos

```
python3 run_all.py --casos casos/ --salida resultados/    # todas las evidencias
python3 -m pytest tests/                                   # pruebas
```

Si un comando no existe todavía, créalo siguiendo esta convención en vez de inventar otra.

## Cosas que el profesor revisa (no fallar)

- La reducción va **desde** el problema conocido **hacia** el nuestro, nunca al revés, y se prueban las dos direcciones (⇒ y ⇐) además del tiempo polinomial de la construcción.
- O(n·B) es pseudo-polinomial: B ocupa log₂B bits, así que es exponencial en el tamaño real de la entrada. No contradice la NP-dureza (es NP-difícil en sentido débil).
- Las cotas se **citan bien** (autor y año) y se **verifican** contra el óptimo por fuerza bruta en instancias pequeñas.
- No basta con "tardó X segundos": toda afirmación de eficiencia lleva su deducción de T(n).
- La sustentación vale 45 %: cada integrante debe poder explicar **ambas** reducciones sin notas.

## Cómo quiero que trabajes

- Antes de cambios grandes, propón un plan corto y espera confirmación.
- Un cambio, una prueba: después de tocar un algoritmo, corre las pruebas.
- Si el enunciado y la guía de entrega se contradicen, avisa en vez de elegir en silencio. La guía de la primera entrega manda para esta entrega.
- No modifiques `casos/`. No borres `resultados/` sin regenerarlos completos.
- Explica las decisiones en español sencillo; el equipo tiene que poder defenderlas en la sustentación.