# Visor del proyecto: aceleración (Parte 1) y voraz (Parte 2)

Herramienta de apoyo con una **página de inicio** y un visor por parte: **Parte 1 (aceleración de la cadena, programación dinámica)** y **Parte 2 (cobertura mínima de auditoría, voraz)**. Más abajo, la sección de la Parte 1; lo que sigue de esta introducción describe la Parte 2.

La Parte 2 permite Permite cargar un caso, ejecutar el
voraz de la entrega y los enfoques de `src/auditoria/enfoques/`, y ver paso a paso cómo decide cada uno y por qué.
Sirve para explicar y defender el algoritmo con lenguaje entendible para cualquier persona.

El visor **no es un entregable** ni reemplaza las evidencias: las evidencias de la entrega salen de
`resolver_caso` y de la traza de `src/auditoria/`. Está en el repositorio como herramienta de demostración.

## Cómo se ejecuta

Desde la raíz del proyecto (solo librería estándar de Python, sin instalar nada):

```
python3 frontend/servidor.py
```

Abre `http://127.0.0.1:8765` en el navegador, en la página de inicio, desde donde se entra a la aceleración (`/aceleracion`) o a la auditoría (`/auditoria`); arriba de cada visor hay un selector para cambiar de parte. Solo escucha en `127.0.0.1` (esta máquina). Opciones: `--puerto N`
para cambiar de puerto y `--no-abrir` para no abrir el navegador. El navegador se abre con su salida silenciada (en Linux, con `xdg-open`), para que no aparezcan en la terminal los avisos de Chrome como "Abriendo en una sesión existente del navegador" ni los errores internos de Chromium (`zygote ... Tubería rota`), que son inofensivos. Se detiene con `Ctrl+C`.

## Cómo se carga un caso

- **Subir archivo:** un `.json` (formato del ejemplo de la profesora) o un `.txt` (formato provisional). También se
  puede arrastrar el archivo. Antes de analizar muestra un resumen de lo que contiene.
- **Crear el caso:** se indica la cantidad de riesgos (r) y de interacciones (n) y, para cada interacción, se marcan
  con casillas los riesgos que revisa. Sirve para transcribir un caso venga como venga.
- **Desde texto:** pegar el caso. Si el texto empieza con `{` se lee como JSON; si no, como el formato `.txt`.

La lectura es la de `src/auditoria/lectura.py`: si un caso viene mal escrito, el mensaje de error es el del lector del
proyecto. Los riesgos se numeran del 1 al r.

## Qué muestra

1. **Resumen:** cuántas interacciones se auditan, en qué orden, la garantía teórica H(d) (solo donde está
   demostrada), el mínimo real, la comparación con él y el tiempo.
2. **Costo total** (cuadro aparte): el costo de la solución (|J| = 1 + 1 + … = N, con el porqué) y el costo del
   algoritmo con los números del caso (ecuación con n, r, k, e y Σ|S_j|, resultado en comparaciones de riesgos, el
   porqué y la cota teórica). Es una estimación por conteo de operaciones, no un tiempo medido.
3. **Comprobación por fuerza bruta** (solo n ≤ 12): el mínimo real, cuántas combinaciones revisó de 2^n, el tiempo y
   una tabla por tamaño de combinación. Con n > 12 explica por qué no se ejecuta.
4. **Comparación:** tabla con las ocho combinaciones de ingredientes (la elegida resaltada): tamaño, orden, mejor o
   peor frente al voraz normal, frente al mínimo real, tiempo y costo teórico. Con n > 12 no hay mínimo real y se
   muestra la cota inferior ⌈r / d⌉.
5. **Paso a paso** (con reproducir, adelantar, atrasar, slider y teclas ← →): la matriz interacción × riesgo pintada
   por paso, los hitos, los riesgos que faltan, la cobertura final y una vista técnica con la evidencia en texto.

### Selector de método

Sobre el paso a paso hay un botón azul, **Voraz normal**, y, separados, tres botones verdes de ingredientes:
**Esenciales**, **Rareza** y **Parejas**. Los ingredientes **se combinan**: al activar dos o tres se arma la combinación
(por ejemplo, rareza + parejas) y con los tres se obtiene "los tres juntos"; sin ninguno activo, o al pulsar "Voraz
normal", se vuelve al voraz normal. Al cambiar, todo (resumen, costo, comparación y paso a paso) pasa a mostrar cómo
resuelve el caso esa combinación.

### Por qué esta interacción y no otra

En cada paso hay un recuadro con la razón concreta de la elección:

- **Voraz normal:** cuántos riesgos nuevos revisa frente a la mejor de las otras, o el empate y el desempate.
- **Esenciales:** el riesgo que solo esa interacción revisa.
- **Parejas:** la pareja ganadora, cuánto cubre junta y por qué se compromete una de las dos; avisa si el voraz normal
  habría decidido distinto.
- **Rareza:** el puntaje de cada interacción (o de cada pareja); cada riesgo pendiente vale 1 dividido entre cuántas
  interacciones lo revisan.

## Secciones de cada visor

Cada visor (Parte 1 y Parte 2) tiene cuatro secciones: **1. Cargar el caso**, **2. Cómo funciona cada enfoque**,
**3. Resultado y decisión, paso a paso** y **4. Crear tus propias pruebas**. La sección 2 es una explicación para quien no conoce los algoritmos: en la Parte 1
cuenta el problema, por qué no se prueba todo, qué es la programación dinámica, qué hace cada tabla (por presupuesto y por valor,
con un ejemplo pequeño que se puede desplegar) y una comparación; en la Parte 2 cuenta el problema, qué es un método voraz y qué
hace cada uno (voraz normal, esenciales, rareza, parejas), cómo se combinan y cuáles tienen garantía demostrada. Una barra de botones elige qué enfoque se explica y solo se muestra
ese (Parte 1: por presupuesto, por valor, compararlos; Parte 2: voraz normal, esenciales, rareza, parejas y las combinaciones); la lógica es `estatico/explicacion.js`, común a las dos páginas, y se maneja también con las flechas del teclado.
La pestaña "Armar una combinación" de la Parte 2 deja encender los ingredientes (esenciales, rareza, parejas) y muestra el detalle de esa combinación: la idea, cómo decide paso a paso, qué arregla, qué aporta cada ingrediente (cuántas fallas habría sin él), cuántas veces falla en 9000 instancias, cómo se compara con el voraz normal (mejora / igual / peor), el peor caso medido, el costo y la garantía (solo el voraz normal y las esenciales la tienen demostrada). La lógica es `estatico/combinador.js` y las cifras salen de `ablacion_detalle(3000, 2026)` (`src/auditoria/enfoques/comparacion/ablacion.py`); una prueba en `tests/test_enfoques.py` comprueba que las cifras escritas en el visor sean las del código.
El panel "Las combinaciones" de la Parte 2 explica qué arregla cada ingrediente, por qué juntos funcionan mejor, cuántas veces falla cada
combinación (9000 instancias con n ≤ 12, con barras), cuándo brilla cada una, el costo en tiempo y las limitaciones (sin garantía demostrada,
instancias pequeñas y ingredientes elegidos mirando los mismos resultados). Las cifras salen de `comparacion/experimento.py` con semilla 2026 y están escritas a mano en `index.html`: si cambia el experimento hay que actualizarlas.
Los textos son fijos (están en `index.html` y `aceleracion.html`); si cambian los enfoques hay que actualizarlos a mano.

### Sección 4: crear tus propias pruebas

- **Voraz (`estatico/pruebas.js`, ruta `POST /api/auditoria/experimento`):** se elige la cantidad de casos por densidad (hasta 5.000), la semilla y qué densidades
  usar (ralo, medio, denso). Se generan casos al azar (n ≤ 12, r ≤ 14, para tener el mínimo real por fuerza bruta) y se corren las ocho combinaciones. La tabla muestra por
  método cuántas veces llegó al mínimo, cuántas no, cuántas fue mejor / igual / peor que el voraz normal, la razón máxima respecto del mínimo y cuántas veces pasó de H(d); la
  fila con más aciertos va resaltada. Debajo, el desglose por densidad y, por método, los casos más chicos donde empeoró al voraz normal, con un botón que carga ese caso en el
  visor (sección 3). Mismo código que `python3 src/auditoria/enfoques/comparacion/ablacion.py`.
- **PD (`estatico/pruebas_pd.js`, ruta `POST /api/aceleracion/experimento`):** se eligen los casos (hasta 500), la semilla, los rangos de etapas, costos y ahorros y B como % del
  costo total, con tres ejemplos de parámetros (costos y ahorros parecidos, costos grandes con ahorros chicos, cerca del cruce). Como las dos tablas son exactas, la prueba comprueba
  que dan el mismo ahorro y, con n ≤ 12, que aciertan a la fuerza bruta; lo que mide es cuántas celdas y cuánto tiempo gasta cada una según B < D, B = D o B > D. Una tabla de más
  de 1.500.000 celdas no se corre y el cálculo se corta a los 25 s. Mismo código que `python3 src/aceleracion/enfoques/dp_por_valor/pruebas_aleatorias.py`.
- Las rutas validan los parámetros (cantidades, rangos y al menos una densidad) y responden 400 con el motivo.

## Parte 1: aceleración de la cadena (`/aceleracion`)

Mismo esquema y misma paleta que el visor de la Parte 2: primero se carga el caso y luego se ve el resultado paso a paso.

- **Cargar el caso:** subir o arrastrar un `.json` (formato de la profesora, lo lee `src/aceleracion/lectura.py`), crear el
  caso a mano (cantidad de etapas, presupuesto B y, por etapa, duración t, costo c y ahorro d, con validación de
  d ≤ t) o pegar el JSON. La vista previa avisa si el presupuesto alcanza para acelerarlo todo, si alguna etapa cuesta
  más que B o no ahorra nada, y ordena las etapas por ahorro por unidad de costo.
- **Resultado:** etapas aceleradas, presupuesto usado, ahorro, duración final, tiempo de la DP, **celdas de la tabla** (con filas × columnas, memoria estimada y las celdas de la otra tabla) y validación; el cuadro de
  costo total con los números del caso (celdas de la tabla, por qué es Θ(n·B), memoria y por qué es pseudo-polinomial);
  y la comprobación por fuerza bruta (n ≤ 12) o el motivo por el que no se corre.
- **Paso a paso:** primero se llena la tabla fila por fila (una celda verde es donde conviene acelerar) y luego se recorre
  hacia atrás: cada paso muestra la decisión de una etapa, el presupuesto restante y marca el camino de la solución.
  Se puede tocar cualquier celda ya calculada para ver cómo salió (qué vale no acelerar, qué vale acelerar y cuál gana)
  y de qué celdas viene. Debajo de la tabla, la cadena de etapas se va coloreando con cada decisión.
- **Dos selectores independientes:** hay botones de enfoque **arriba** de la sección 2 (junto al resumen) y otros en la
  **simulación**. Los de arriba cambian solo las tarjetas de resultado (resumen, costo total y, en el voraz, la tabla de
  comparación); los de la simulación cambian solo la tabla y el paso a paso. Así se puede ver el resultado de un enfoque
  mientras la simulación sigue en otro. Lo mismo vale en el visor del voraz (voraz normal e ingredientes).
- **Dos enfoques, a elegir:** arriba de la tabla, un selector con **Por presupuesto** (la DP base) y **Por valor**
  (`src/aceleracion/enfoques/dp_por_valor/`). Muestra cuántas celdas tendría cada tabla y cuál conviene (la de menos
  celdas); la que no cabe en memoria queda deshabilitada. Al cargar un caso se muestra el recomendado en ambos lados y se puede cambiar en
  cualquier momento: el otro enfoque se pide al servidor una sola vez y queda en memoria. En la tabla por valor las columnas son el
  ahorro que se quiere lograr, cada celda es el menor costo (∞ si no se puede o pasa de B) y la reconstrucción parte del
  mayor ahorro que cabe en B.
- **Tabla grande:** se dibuja (con desplazamiento) hasta 20 000 celdas, es decir (n+1)·(B+1) ≤ 20 000. Con más, solo se
  muestran las decisiones de la reconstrucción y se avisa. Con B tan grande que la tabla no cabe en memoria, el error es
  el del propio algoritmo (`MAX_CELDAS_TABLA`).
- Rutas: `POST /api/aceleracion/previsualizar` (solo lee) y `POST /api/aceleracion/resolver` (lee y resuelve; acepta
  `enfoque`: `auto`, `presupuesto` o `valor`; `auto` es el de la tabla más chica). Las decisiones de la reconstrucción se leen de la tabla ya calculada; no se reimplementa la DP.

## Decisiones

- **No duplica la lógica de los algoritmos.** El navegador le habla al servidor local (`servidor.py`, `http.server`),
  que importa `leer_instancia` y `resolver_caso` de `src/auditoria/` (y los equivalentes de `src/aceleracion/` para la Parte 1) y las combinaciones de `src/auditoria/enfoques/`
  (`comparar_caso`, vía `voraz_ablacion_traza`). Lo que se ve es lo que calculan esos módulos.
- **Los textos de las explicaciones son plantillas.** Están escritas en `estatico/app.js` (funciones
  `razonEleccion`, `explicacionPaso`, `introMetodo` y `dibujarCosto`) y se rellenan con los datos reales de la traza.
  No hay IA ni texto libre. Se verificó que lo que afirman es cierto en 42 293 pasos y que no fallan con casos de
  borde (n = 1, r = 1, interacciones vacías, n = 30). Algunas frases son fijas (por ejemplo, la regla de desempate
  se recuerda siempre, haya o no empate) y el visor no recalcula "ninguna otra pareja revisa más": se apoya en el
  algoritmo.
- **Lenguaje no técnico en pantalla** (riesgos, interacciones) y notación formal en el costo y la vista técnica.
- **Formato de la profesora:** si cambia, se adapta únicamente `src/auditoria/lectura.py` y el visor sigue funcionando.
- **Sin dependencias nuevas:** nada que registrar en `requirements.txt`. Requiere un navegador.

## Archivos

```
frontend/
    servidor.py             servidor local (páginas, API de la Parte 2: /api/resolver y /api/previsualizar,
                            API de la Parte 1: /api/aceleracion/resolver y /api/aceleracion/previsualizar)
    fuerza_bruta_demo.py    demostración de la fuerza bruta (Parte 2): módulo del servidor y comando de terminal
    estatico/
        inicio.html, inicio.css            página de inicio (elegir la parte)
        aceleracion.html, .js, .css        visor de la Parte 1 (tabla de la DP)
        index.html, app.js                 visor de la Parte 2 (voraz; se sirve en /auditoria)
        explicacion.js                     botones de la sección 2 (muestran un enfoque a la vez), común a las dos páginas
        combinador.js                      armador de combinaciones de la sección 2 del visor del voraz
        estilos.css                        diseño común (tema claro "Arena y oliva")
```

## Demostración de la fuerza bruta por terminal

```
python3 frontend/fuerza_bruta_demo.py ruta/al/caso.txt
```

Acepta uno o varios archivos `.json` o `.txt`. Para cada caso con n ≤ 12 muestra, por tamaño de combinación, cuántas se
probaron, el mínimo real, cuántas combinaciones revisó de 2^n, el tiempo y la comparación con el voraz. Con n > 12 o un
caso no factible avisa y no ejecuta. No reimplementa el algoritmo: llama a `fuerza_bruta` de `src/auditoria/auditoria.py` y
solo cuenta lo que revisó.

## Limitaciones

- Las plantillas cubren las ocho combinaciones de los tres ingredientes. Un ingrediente nuevo exige escribir sus
  plantillas.
- Las explicaciones dicen por qué se eligió una interacción según la regla del método; no dicen si fue la mejor
  decisión global (para eso están el mínimo real y la comparación).
- Las listas de candidatas muestran las 10 mejores y un "… y N más".
- Cubre la Parte 1 (DP base) y la Parte 2 (voraz base y enfoques). La variante ponderada no está incluida.
- Las páginas y las rutas de la Parte 1 se prueban en `tests/test_frontend_aceleracion.py` (levanta el servidor en un
  puerto libre y compara contra la DP y la fuerza bruta). El dibujo en el navegador no tiene pruebas automáticas; el visor
  de la Parte 2 se probó con un barrido de casos aleatorios en el navegador. La lógica de los algoritmos está cubierta por `tests/`.
