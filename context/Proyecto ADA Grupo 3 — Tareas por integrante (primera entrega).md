# Proyecto ADA Grupo 3 — Tareas por integrante (primera entrega)

Oct 22, 2026 · @Gyro

## Qué cambió con la guía nueva

La guía nueva mantiene lo de antes (formalización, NP-dureza con Mochila 0/1 y Cobertura de Vértices, código base) y agrega cinco cosas. La más pesada: como somos 3, también hay que implementar la variante de auditoría ponderada por costo.

| Qué | Antes | Ahora |
| --- | --- | --- |
| Formalización | Entrada, salida, tamaño, objetivo | Lo mismo **más restricciones** escritas explícitamente |
| Reducciones | Mochila 0/1 y Cobertura de Vértices | Igual, sin cambios |
| Código | Resolver el problema base con instancias propias | Correrlo con **los casos de la profesora** y reportar resultado, tiempo y traza **por caso** |
| Traza | No se pedía | Estados y decisiones de la DP, etapas aceleradas, costos y cobertura de auditoría |
| Repositorio | Solo código | Código, dependencias, README e instrucciones de ejecución |
| Manual técnico | No se pedía | Documento aparte: algoritmo, estructura del código, formatos de entrada/salida, pasos de ejecución y limitaciones |
| Variante 1 (por ser 3) | Iba para después | **Ahora:** auditoría ponderada por costo, con resultados, tiempos, traza de elecciones y análisis de complejidad |
| Aceptación | — | Los resultados deben salir del código sin editar la lógica, e informe, repo, manual y evidencias deben ser de la misma versión |

**Pregunta abierta:** todavía no conocemos el formato de los casos de la profesora. Hay que pedirlo o esperar a recibirlos antes de cerrar cómo el programa lee la entrada.

## Qué se entrega y cómo está repartido

Se entregan cuatro cosas: el informe, el repositorio, el manual técnico y las evidencias de correr el código con los casos de la profesora. Cada integrante es dueño de una parte del código y escribe esa parte en el informe y en el manual.

| Integrante | Se encarga de | Aporta al informe | Aporta al manual técnico |
| --- | --- | --- | --- |
| 1 | Parte 1: acelerar la cadena (Mochila 0/1, programación dinámica) | Formalización y reducción de la Parte 1 | Sección del algoritmo de la DP |
| 2 | Parte 2: auditoría mínima (Set Cover, voraz) | Formalización y reducción de la Parte 2 | Sección del algoritmo voraz |
| 3 | Variante 1: auditoría ponderada por costo, y armar repositorio y manual | Formalización, complejidad y resultados de la variante | Estructura general, formatos, ejecución y limitaciones |

Todos corren su parte con los casos de la profesora y entregan, por cada caso, el resultado, el tiempo y la traza.

## Integrante 1 — Parte 1: acelerar la cadena

Tu trabajo es dejar lista toda la Parte 1: formalizarla, demostrar que es NP-difícil desde la Mochila 0/1, programar la programación dinámica y correrla con los casos de la profesora mostrando la traza.

**De qué se trata, en simple:** hay n etapas en fila. Cada etapa dura t\_i, y si pagas c\_i se vuelve d\_i unidades más rápida. Con un presupuesto B hay que escoger qué etapas acelerar para que la cadena termine lo antes posible. Es como llenar una mochila: el costo es el "peso" y el tiempo ahorrado es el "valor".

### Tarea 1: Formalizar

1. Tamaño de la entrada: n (etapas) y B (presupuesto), con una frase de por qué.
2. Entrada: para cada etapa, t\_i, c\_i y d\_i; y el presupuesto B.
3. Salida: el conjunto A de etapas aceleradas.
4. **Restricciones** (ahora se piden explícitas): la suma de los c\_i de A es a lo sumo B; 0 ≤ d\_i ≤ t\_i; todos los valores son enteros no negativos.
5. Objetivo: minimizar la duración total = (suma de los t\_i) − (suma de los d\_i de A), que equivale a maximizar el ahorro.
6. Versión de decisión: dado L, ¿existe A con costo ≤ B y duración ≤ L?

### Tarea 2: Reducción desde Mochila 0/1

1. Escribe la Mochila 0/1 en versión de decisión (pesos w\_i, valores v\_i, capacidad W, umbral V).
2. Arma la traducción en una tabla: c\_i = w\_i, d\_i = v\_i, t\_i = v\_i, B = W, L = (suma de los v\_i) − V.
3. Muestra que la traducción toma tiempo polinomial, O(n).
4. Demuestra la ida (⇒) y la vuelta (⇐).
5. Conclusión: nuestro problema es NP-difícil. Cuidado con la **dirección**: va desde la Mochila hacia nuestro problema.

### Tarea 3: Programar la DP con traza

1. Tabla DP de (n+1) × (B+1), donde DP\[i\]\[b\] es el mayor ahorro con las primeras i etapas gastando máximo b.
2. Llena la tabla con la recurrencia: no acelerar (DP\[i−1\]\[b\]) o acelerar si cabe (DP\[i−1\]\[b−c\_i\] + d\_i).
3. Reconstrucción hacia atrás para saber qué etapas se aceleraron.
4. **Traza** (nuevo): que el programa pueda imprimir o guardar, por cada etapa, la decisión tomada en la reconstrucción ("etapa 3: acelerada, costo 5, ahorro 4, presupuesto restante 2") y, en casos pequeños, la tabla DP completa.
5. **Salida por caso** (nuevo): etapas aceleradas, costo usado, ahorro, duración final y tiempo de ejecución medido.
6. Una fuerza bruta para comprobar la DP en casos pequeños.

### Tarea 4: Correr los casos de la profesora

1. Haz que el programa lea los casos desde archivo, en el formato que entregue la profesora, sin tocar la lógica del algoritmo.
2. Corre todos los casos y guarda la salida, el tiempo y la traza de cada uno, identificados por nombre de caso.
3. Entrégale esos resultados al integrante 3 para las evidencias.

### Tarea 5: Tu sección del manual técnico

1. Explica el algoritmo de la DP en palabras y con la recurrencia.
2. Describe tus funciones: qué recibe y qué devuelve cada una.
3. Escribe sus limitaciones: la tabla ocupa memoria proporcional a n·B, así que con B muy grande se vuelve lenta (es pseudo-polinomial).

## Integrante 2 — Parte 2: auditoría mínima

Tu trabajo es dejar lista toda la Parte 2 base: formalizarla, demostrar que es NP-difícil desde Cobertura de Vértices, programar el voraz y correrlo con los casos de la profesora mostrando la traza de cobertura.

**De qué se trata, en simple:** hay r categorías de riesgo y n interacciones. Cada interacción, si se audita, revisa algunas categorías. Hay que escoger la menor cantidad de interacciones que juntas revisen todas las categorías (Set Cover).

### Tarea 1: Formalizar

1. Tamaño de la entrada: n (interacciones) y r (categorías), con una frase de por qué.
2. Entrada: U = {1, …, r} y, para cada interacción j, el subconjunto S\_j que cubre.
3. Salida: el conjunto J de interacciones a auditar.
4. **Restricciones** (explícitas): la unión de los S\_j de J debe ser U; y como condición previa, la unión de todos los S\_j debe ser U (factibilidad, revisada en O(n·r)).
5. Objetivo: minimizar cuántas interacciones tiene J.
6. Versión de decisión: dado k, ¿existe J con a lo sumo k interacciones que cubra todo?

### Tarea 2: Reducción desde Cobertura de Vértices

1. Escribe Cobertura de Vértices en versión de decisión (grafo G = (V, E) y k).
2. Traducción en una tabla: cada arista es una categoría, cada vértice es una interacción que cubre sus aristas, k queda igual.
3. Muestra que es polinomial: O(|V| + |E|).
4. Demuestra la ida (⇒) y la vuelta (⇐).
5. Conclusión citando a Karp (1972).

### Tarea 3: Programar el voraz con traza

1. Verificación de factibilidad en O(n·r); si alguna categoría no la cubre nadie, el programa lo dice y se detiene.
2. Voraz: mientras falten categorías, escoge la interacción que cubre más categorías que todavía faltan.
3. **Traza** (nuevo): por cada paso, qué interacción se eligió, qué categorías nuevas cubrió y cuáles faltan todavía. Al final, la cobertura completa: qué interacción cubre cada categoría.
4. **Salida por caso** (nuevo): interacciones auditadas, cuántas son, comprobación de que cubren todo y tiempo de ejecución.
5. Fuerza bruta para el óptimo en casos pequeños y comparación contra la cota H(d) (Johnson, 1974; Chvátal, 1979).

### Tarea 4: Correr los casos de la profesora

1. Lectura de los casos desde archivo, en su formato, sin tocar la lógica del algoritmo.
2. Guardar salida, tiempo y traza de cada caso, identificados por nombre.
3. Entregarle los resultados al integrante 3.

### Tarea 5: Tu sección del manual técnico

1. Explica el voraz en palabras.
2. Describe tus funciones: qué reciben y qué devuelven.
3. Limitaciones: el voraz no siempre da el óptimo (solo garantiza H(d) veces) y la fuerza bruta solo sirve para casos pequeños.

**Coordínate con el integrante 3:** la variante ponderada es casi el mismo voraz con otra regla de elección. Usen el mismo formato de entrada y de traza para no hacer dos veces el trabajo.

## Integrante 3 — Variante ponderada, repositorio y manual

Tu trabajo tiene dos partes: implementar la variante 1 (auditoría ponderada por costo), que es el requisito extra por ser un grupo de 3, y armar el repositorio y el manual técnico donde cae el trabajo de los tres.

**De qué se trata la variante, en simple:** es la misma auditoría de la Parte 2, pero ahora auditar cada interacción j cuesta a\_j (por ejemplo, según su longitud). Ya no importa cuántas se auditan, sino cuánto cuesta en total cubrir todas las categorías.

### Tarea 1: Formalizar la variante

1. Tamaño de la entrada: n y r, igual que la Parte 2.
2. Entrada: lo mismo de la Parte 2 más un costo a\_j > 0 por cada interacción.
3. Salida: el conjunto J de interacciones a auditar.
4. Restricciones: la unión de los S\_j de J es U; la instancia debe ser factible.
5. Objetivo: minimizar el costo total, la suma de los a\_j de J.
6. NP-dureza: explica que si todos los costos valen 1 queda exactamente la Parte 2, así que la variante es al menos igual de difícil (generaliza un problema NP-difícil).

### Tarea 2: Programar el voraz ponderado con traza

1. Regla de elección: en cada paso, escoger la interacción con **menor costo por categoría nueva**, es decir, menor a\_j dividido entre el número de categorías que cubre y que todavía faltan. Ignorar las que no cubren nada nuevo.
2. **Traza de elecciones:** por cada paso, la interacción elegida, su costo, cuántas categorías nuevas cubrió, el costo por categoría y el costo acumulado.
3. **Salida por caso:** interacciones auditadas, costo total, comprobación de cobertura y tiempo de ejecución.
4. Fuerza bruta que encuentre el costo mínimo real en casos pequeños, para comparar.

### Tarea 3: Complejidad y garantía

1. Deduce la función de eficiencia del voraz ponderado: hay a lo sumo min(n, r) pasos y cada paso revisa n interacciones con costo O(r), así que T(n, r) = O(n·r·min(n, r)).
2. Deduce la de la fuerza bruta: O(2^n · n · r), exponencial.
3. Cita la garantía: el voraz ponderado cuesta a lo sumo H(d) veces el óptimo, con H(d) = 1 + 1/2 + … + 1/d (Chvátal, 1979).
4. Compruébalo en casos pequeños: costo del voraz dividido entre costo óptimo nunca mayor que H(d).

### Tarea 4: Correr los casos de la profesora

1. Corre la variante con los casos de la profesora (si los casos traen costos de auditoría) y guarda salida, tiempo y traza de cada uno.
2. Recoge también los resultados de los integrantes 1 y 2 y arma con todo una carpeta de evidencias, un archivo por caso.

### Tarea 5: Repositorio

1. Crea el repositorio con carpetas claras: código de cada parte, casos de entrada, resultados.
2. Archivo de dependencias (por ejemplo requirements.txt, aunque solo diga la versión de Python).
3. README con las instrucciones exactas para correr cada parte y reproducir los resultados.
4. Un comando o script único que corra todos los casos y genere todas las evidencias, sin editar la lógica de los algoritmos.

### Tarea 6: Manual técnico

1. Junta las secciones de algoritmo de los integrantes 1 y 2 y escribe la de la variante.
2. Escribe tú las partes generales: estructura del código, formato de entrada, formato de salida y de la traza, pasos de ejecución y limitaciones.

## Trabajo de los tres

El informe es un solo documento y lo arman entre los tres; la regla más importante de la guía es que informe, repositorio, manual y evidencias correspondan a la misma versión del código.

1. **Formato de entrada común:** apenas lleguen los casos de la profesora, acuerden juntos cómo los lee cada programa. Hasta entonces, cada uno puede probar con instancias propias.
2. **Informe:** cada uno escribe su formalización y su reducción (o, en el caso del integrante 3, la de la variante); después se unifica la notación (n, B, r, t\_i, c\_i, d\_i, S\_j, a\_j) y se agregan portada, introducción y referencias.
3. **Congelar la versión:** cuando el código esté listo, se corren todos los casos una sola vez, se guardan las evidencias y no se cambia más la lógica. Si algo se corrige, se vuelven a generar todas las evidencias.
4. **Prueba cruzada:** cada uno corre el código de otro siguiendo solo el README. Si no le funciona sin preguntar, el README está incompleto.
5. **Sustentación (45 % de la nota):** los tres deben poder explicar las dos reducciones sin notas, no solo la propia.

## Orden de trabajo

Los tres trabajan en paralelo desde el inicio; lo único que bloquea es el formato de los casos de la profesora, así que conviene pedirlo ya.

1. **Primero:** cada uno formaliza su parte (con restricciones). El integrante 3 crea el repositorio y la estructura del informe y del manual. Alguien pide o confirma el formato de los casos.
2. **Segundo:** los integrantes 1 y 2 hacen su reducción y se la explican uno al otro. El integrante 3 escribe el argumento de NP-dureza y la complejidad de la variante.
3. **Tercero:** cada uno programa su algoritmo con traza y salida por caso, probando con instancias propias.
4. **Cuarto:** se adapta la lectura al formato de la profesora, se corren todos los casos y se guardan las evidencias.
5. **Quinto:** se completan informe y manual, se hace la prueba cruzada del README, se congela la versión y se entrega.
