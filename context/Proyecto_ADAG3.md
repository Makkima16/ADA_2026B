# Proyecto Semestral 2026-2
## Análisis y Diseño de Algoritmos

## 1. Presentación

Este documento formula un proyecto de optimización algorítmica, que no depende de ninguna tecnología propietaria, y puede formularse, resolverse y evaluarse íntegramente con las herramientas del curso.

Recuerden que no basta con programar algo que funcione. Cada equipo debe demostrar formalmente qué tan eficiente es su solución, tanto para el caso exacto como para cualquier aproximación o heurística que proponga.

## 2. Qué significa "eficiente"

Esto es lo que se exige demostrar — no es opcional ni queda a discreción del equipo:

- **Deben demostrar:** la definición precisa del tamaño de entrada $n$ del problema (qué está creciendo cuando el problema se vuelve más grande).
- **Deben demostrar:** la función de eficiencia $T(n)$ del algoritmo exacto, obtenida contando operaciones o resolviendo una recurrencia (no una estimación intuitiva: una deducción explícita, paso a paso, con su notación resultante).
- **Deben demostrar:** para cualquier algoritmo aproximado o heurístico: su propia función de eficiencia $T(n)$, y — cuando exista una garantía demostrable conocida (por ejemplo, una razón de aproximación) — su demostración o su aplicación correcta citando el resultado del que proviene.
- **Deben demostrar:** una validación experimental, esto implica medir el tiempo real de ejecución para valores crecientes de $n$, graficar los resultados, y contrastar el crecimiento observado contra el crecimiento que predice la función $T(n)$ deducida teóricamente, como lo hemos hecho en clase.

Un informe que solo reporte "......tardó X segundos" sin la formalidad requerida, no cumple el nivel del curso, sin importar qué tan bien funcione el código.

## 3. Estructura general

| Problema | Técnica central | Tipo de dificultad |
| --- | --- | --- |
| Ruta crítica con aceleración bajo presupuesto, y cobertura mínima de auditoría | Programación dinámica (mochila) + aproximación voraz logarítmica | NP-difícil (reducción desde Mochila 0/1 y desde Cobertura de Conjuntos) |

## 4. Proyecto Ruta — Ruta crítica con aceleración bajo presupuesto, y cobertura de auditoría

### 4.1 Escenario

Un flujo de trabajo procesa cada solicitud a través de una cadena de $n$ etapas dispuestas en serie. Cada etapa $i$ tiene una duración normal $t_i$, y puede acelerarse a un costo $c_i$, reduciendo su duración en $d_i$ unidades de tiempo. Hay un presupuesto total $B$ para acelerar etapas. Por separado, cada solicitud que atraviesa el flujo puede necesitar una revisión de cumplimiento normativo a fondo; revisar todas es demasiado costoso, así que solo se audita un subconjunto.

### 4.2 Parte 1 — Aceleración óptima de la cadena bajo presupuesto

**Tamaño de la entrada:** $n$, el número de etapas de la cadena, y $B$, el presupuesto disponible.

**Objetivo:** elegir qué subconjunto de etapas acelerar, sin exceder el presupuesto $B$, para minimizar la duración total de la cadena (la suma de las duraciones de todas las etapas, aceleradas o no, ya que al ser una cadena en serie todas están siempre en el camino crítico).

Se exige demostrar que este problema es exactamente el problema de la Mochila 0/1: maximizar la suma de reducciones de tiempo $d_i$ de las etapas elegidas para acelerar, sujeto a que la suma de sus costos $c_i$ no exceda $B$, es literalmente la Mochila 0/1 con "valor" $= d_i$ y "peso" $= c_i$. Como la Mochila 0/1 es NP-difícil (ya demostrado en el curso), y una cadena en serie es apenas un caso particular de un flujo general (que puede tener etapas en paralelo y rutas alternativas), el problema general de acelerar un flujo cualquiera bajo presupuesto es al menos igual de difícil — es decir, también NP-difícil.

**El algoritmo exacto (programación dinámica) y su función de eficiencia:** la Mochila 0/1 se resuelve de forma exacta con programación dinámica sobre una tabla indexada por etapa y presupuesto usado, con la recurrencia clásica

$$
DP[i][b] = \max\big(DP[i-1][b],\; DP[i-1][b-c_i] + d_i\big) \quad \text{si } c_i \le b.
$$

El tamaño de la tabla es $n$ filas por $B$ columnas, y cada celda se calcula en tiempo constante, así que $T(n, B) = O(n \cdot B)$ — pseudo-polinomial: eficiente cuando $B$ es un número pequeño, pero exponencial en el tamaño de la representación de $B$ si $B$ se mide en bits, lo cual se exige explicar y justificar en el informe.

### 4.3 Parte 2 — Cobertura mínima de auditoría

**Tamaño de la entrada:** $n$, el número de interacciones candidatas a auditar, y $r$, el número de categorías de riesgo distintas que existen (tipos de sesgo, fuga de datos personales, fallas de formato, entre otras).

**Entrada:** para cada interacción, el subconjunto de categorías de riesgo que cubriría si se audita.

**Objetivo:** elegir el menor número posible de interacciones a auditar de modo que, entre todas las elegidas, se cubra cada una de las $r$ categorías de riesgo al menos una vez.

Este es el problema clásico de Cobertura de Conjuntos (*Set Cover*), ya NP-completo. Se exige presentar la reducción formal desde 3-Cobertura de Conjuntos o la reducción estándar del curso, y aplicar el algoritmo voraz que en cada paso elige la interacción que cubre más categorías todavía no cubiertas, citando y verificando empíricamente su cota clásica de aproximación: el resultado del algoritmo voraz nunca usa más de $H_r = 1 + \frac{1}{2} + \frac{1}{3} + \cdots + \frac{1}{r}$ (aproximadamente $\ln(r) + 1$) veces el número mínimo real de interacciones necesarias (Johnson, 1974; Chvátal, 1979).

**Función de eficiencia del algoritmo voraz:** en el peor caso hay que repetir hasta $r$ veces la elección (una por cada categoría que falta cubrir), y cada elección revisa las $n$ interacciones restantes comparando cuántas categorías nuevas cubre cada una, un costo de $O(n \cdot r)$ por elección, dando $T(n, r) = O(n \cdot r^2)$ en el peor caso.

### 4.4 Variantes (todas obligatorias)

- Categorías de riesgo con distinta importancia (cobertura ponderada), que cambia ligeramente la cota $H_r$ y exige adaptarla.
- Combinar las dos partes: decidir simultáneamente cómo acelerar el flujo y qué auditar, bajo un presupuesto conjunto.
- Etapas en paralelo dentro del flujo (un grafo acíclico dirigido general en lugar de una cadena): la ruta crítica ya no es la suma de todas las etapas, y se exige primero un algoritmo de ruta más larga en un grafo acíclico dirigido (programación dinámica sobre el orden topológico, $T(n, m) = O(n + m)$ con $m$ aristas) antes de decidir qué acelerar.

## 5. Entregables

- **Informe técnico**, con una sección de análisis de complejidad: definición de $n$, deducción de $T(n)$ para el algoritmo exacto, prueba de NP-dureza por reducción, algoritmo aproximado con su cota (demostrada o correctamente citada y aplicada), y validación experimental que compare el crecimiento medido contra el crecimiento teórico (más adelante se darán los detalles de este informe).
- **Implementación:** código reproducible con generación de instancias sintéticas de tamaño creciente (al menos 5 tamaños distintos de $n$, en un rango suficiente para observar el crecimiento asintótico), medición de tiempos, y gráfica de tiempo contra $n$.
- **Sustentación grupal** de 15 a 20 minutos, donde el equipo debe poder explicar y defender, sin ayuda de notas, la reducción de NP-dureza de su problema y la deducción de la función de eficiencia de su algoritmo exacto.
- **Sustentación individual** donde cada estudiante debe desarrollar lo que se le indique.

## 6. Cronograma (11 semanas)

| Semanas | Hito |
| --- | --- |
| 1 – 2 | Formación de equipos y elección de la variante; entrega escrita de la formalización del problema ($n$, entrada, salida, objetivo) — sin código todavía |
| 3 – 4 | Prueba formal de NP-dureza por reducción (entrega parcial, revisada por el docente antes de continuar) |
| 5 – 6 | Algoritmo exacto (fuerza bruta o programación dinámica) + deducción formal de su $T(n)$ |
| 7 – 8 | Algoritmo aproximado o heurístico + su propia función de eficiencia + cota de aproximación cuando exista |
| 9 – 10 | Experimentación: generación de instancias, medición de tiempos, comparación contra la función teórica |
| 11 | Entrega final y sustentaciones |

## 7. Criterios de evaluación

| Componente | Peso |
| --- | --- |
| Formalización del problema ($n$, entrada, salida, objetivo) | 10 % |
| Prueba de NP-dureza por reducción, correcta y completa | 10 % |
| Deducción formal de función de eficiencia del algoritmo exacto | 10 % |
| Algoritmo aproximado/heurístico: diseño, función de eficiencia y cota de aproximación | 15 % |
| Validación experimental (medición y comparación contra la teoría) | 10 % |
| Sustentación | 45 % |

## 8. Notas finales

El proyecto no requiere datos reales de ningún proyecto externo: todas las instancias son sintéticas, generadas por los propios estudiantes según los parámetros descritos en cada sección. El criterio de éxito de este proyecto no es "que el código corra", sino que cada equipo pueda, al final del semestre, sostener con rigor por qué su solución es eficiente — y qué tan eficiente es, exactamente, en el lenguaje formal del curso.
