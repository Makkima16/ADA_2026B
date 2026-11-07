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

Cada visor (Parte 1 y Parte 2) tiene tres secciones: **1. Cargar el caso**, **2. Cómo funciona cada enfoque** y
**3. Resultado y decisión, paso a paso**. Las pruebas aleatorias (antes la sección 4 de cada visor) están ahora todas en `/aleatorios`. La sección 2 es una explicación para quien no conoce los algoritmos: en la Parte 1
cuenta el problema, por qué no se prueba todo, qué es la programación dinámica, qué hace cada tabla (por presupuesto y por valor,
con un ejemplo pequeño que se puede desplegar) y una comparación; en la Parte 2 cuenta el problema, qué es un método voraz y qué
hace cada uno (voraz normal, esenciales, rareza, parejas), cómo se combinan y cuáles tienen garantía demostrada. Una barra de botones elige qué enfoque se explica y solo se muestra
ese (Parte 1: por presupuesto, por valor, compararlos; Parte 2: voraz normal, esenciales, rareza, parejas y las combinaciones); la lógica es `estatico/explicacion.js`, común a las dos páginas, y se maneja también con las flechas del teclado.
La pestaña "Armar una combinación" de la Parte 2 deja encender los ingredientes (esenciales, rareza, parejas) y muestra el detalle de esa combinación: la idea, cómo decide paso a paso, qué arregla, qué aporta cada ingrediente (cuántas fallas habría sin él), cuántas veces falla en 9000 instancias, cómo se compara con el voraz normal (mejora / igual / peor), el peor caso medido, el costo y la garantía (solo el voraz normal y las esenciales la tienen demostrada). La lógica es `estatico/combinador.js` y las cifras salen de `ablacion_detalle(3000, 2026)` (`src/auditoria/enfoques/comparacion/ablacion.py`); una prueba en `tests/test_enfoques.py` comprueba que las cifras escritas en el visor sean las del código.
El panel "Las combinaciones" de la Parte 2 explica qué arregla cada ingrediente, por qué juntos funcionan mejor, cuántas veces falla cada
combinación (9000 instancias con n ≤ 12, con barras), cuándo brilla cada una, el costo en tiempo y las limitaciones (sin garantía demostrada,
instancias pequeñas y ingredientes elegidos mirando los mismos resultados). Las cifras salen de `comparacion/experimento.py` con semilla 2026 y están escritas a mano en `index.html`: si cambia el experimento hay que actualizarlas.
Los textos son fijos (están en `index.html` y `aceleracion.html`); si cambian los enfoques hay que actualizarlos a mano.

## Pruebas aleatorias (`/aleatorios`)

Reúne lo que antes eran la sección 4 de `/auditoria` y la de `/aceleracion` y lo que hacía `probar_aleatorios.py` en el visor.
Elegís **qué probar** (tres modos) y los resultados salen **separados por parte**, cada uno con su resumen, sus tarjetas y su tabla agrupada.

| Modo | Motor | Tope de casos | ¿Escribe archivos? | Qué se ve |
| --- | --- | --- | --- | --- |
| **Las dos partes y la variante** | `run_all.py` sobre `Casos/casos_temporales/` | 500 | Sí: resultado, tiempo y traza por caso en `Resultados/resultados_temporales/` | Resumen de la Parte 1, de la Parte 2 y de la variante (dos versiones) y un selector para ver un caso en detalle |
| **Solo Parte 1 (DP)** | `pruebas_aleatorias.py`, en memoria | 500 (corte a los 25 s) | No | DP por presupuesto contra DP por valor, según B < D, B = D o B > D |
| **Solo Parte 2 (voraz)** | `ablacion.py`, en memoria | 5.000 por densidad (15.000 en total; 9.000 con 3.000 por densidad) | No | Los ocho enfoques contra el mínimo real y contra el voraz normal, por densidad, y los casos donde un enfoque empeoró |

**Por qué hay modos.** Cada caso del modo completo deja unos 13 archivos de evidencia (500 casos son unos 6.500); con 9.000 casos serían unos 117.000
archivos por corrida. Por eso, cuando se prueba una sola parte, los casos se generan y se miden en memoria, sin escribir archivos, y solo se ven los
resultados agregados. Es el mismo experimento de siempre (los comandos `ablacion.py` y `pruebas_aleatorias.py` siguen existiendo).

**Qué muestra cada bloque de resultados** (el mismo formato en los tres modos):
- **Parte 1:** tarjetas (las dos tablas dieron lo mismo, contra la fuerza bruta, tabla más chica, solo por valor, no se corrieron) y la tabla por relación entre B y D.
- **Parte 2:** tarjetas (casos, el voraz normal llegó al mínimo, el que más veces llega) y la tabla con una fila por enfoque: llega al mínimo, no llega, mejor / igual / peor que el voraz normal, razón máxima, pasa H(d) y, en el modo completo, el tiempo medio; la fila con más aciertos va resaltada. Debajo, el desglose por densidad y los casos más chicos donde un enfoque empeoró.
- **Variante 1** (solo modo completo), en dos bloques: **solo completas** (la versión principal: casos, si llegó al mínimo real, cómo se compara con el J de la Parte 2) y **con parciales** (la extensión: cuántos casos con parciales y con depuración, y cómo se compara contra la versión solo completas del mismo caso).
- **Un caso en detalle** (solo modo completo): un selector (con anterior y siguiente) para elegir uno de los casos; muestra su ficha (resultado de la Parte 1, de la Parte 2 y de la variante en sus dos versiones, y los ocho enfoques) y dos botones, **Ver paso a paso en Aceleración** y **Ver paso a paso en Auditoría**, que abren esa página ya con el caso cargado (`/aceleracion?caso=NOMBRE` y `/auditoria?caso=NOMBRE`: la página pide el caso a `GET /api/aleatorios/caso` y lo analiza como si lo hubieras subido). Un botón queda desactivado si el caso no trae datos de esa parte. Un tercer botón, **Ver la variante ponderada paso a paso**, abre `/auditoria?caso=NOMBRE&modo=variante`. Solo aparece cuando se corren las dos partes con `run_all.py`; las tablas por caso quedan en `comparacion.md` y en las trazas.

**Modo completo, en detalle**
- **Generar** (`POST /api/aleatorios/generar`): cantidad (hasta 500), semilla, rango de n (hasta 100), de r (hasta 60) y densidades. Escribe `.json` con el formato de la profesora (con `variaciones_auditoria` parcial y completa) en `Casos/casos_temporales/`, que se vacía y reescribe en cada generación (también se vacía `Resultados/resultados_temporales/`).
- **Subir casos propios** (`POST /api/aleatorios/subir`, o arrastrando): hasta 200 `.json` y 50 MB en total; reemplazan `Casos/casos_temporales/`. **Cada archivo debería traer las dos partes**, como el ejemplo de la profesora. Si un archivo trae solo la Parte 1 o solo la Parte 2, se analiza únicamente la parte que aplica y la otra figura como «no aplica» (no es un error). Antes de borrar nada se comprueba que cada archivo sea un objeto JSON válido; los nombres se sanean y los repetidos se numeran.
- **Probar** (`POST /api/aleatorios/probar`): llama a `run_all.py` (sin reimplementar nada), que además de `resumen.csv` y `comparacion.md` escribe `resumen_enfoques.json`, de donde salen los resúmenes por parte. `comparacion.md` empieza por el resumen y deja las tablas por caso al final.
- **Solo una parte:** `POST /api/aleatorios/solo-pd` y `POST /api/aleatorios/solo-voraz`. Validan los parámetros y responden 400 con el motivo.
- Las dos carpetas están en `.gitignore`. Solo se borran archivos sueltos `.json`, `.txt`, `.csv` o `.md` dentro de carpetas que se llamen exactamente así, nunca de forma recursiva. Las rutas de caso y de traza solo aceptan nombres que existan en esas carpetas.
- Lo mismo se hace desde la terminal con `python3 probar_aleatorios.py` y `python3 run_all.py` (ver `COMANDOS.md`). La lógica vive en `src/generacion_casos/` y en los módulos `resolver_enfoques.py` de cada parte.

## Variante ponderada en `/auditoria`

Sobre la sección de resultados hay un selector **«Qué quieres ver»**: **Voraz normal y enfoques** (lo de siempre) o **Variante ponderada (con costos)**. En modo variante se ve el paso a paso del voraz ponderado, que antes solo existía en las trazas de texto y en las tarjetas de `/aleatorios`:

- **Versión:** un interruptor **Solo completas** (la versión principal: un costo a_j por interacción) y **Con parciales** (la extensión: cada variación de auditoría es una opción con su costo). Se desactiva si el caso no trae parciales.
- **Tarjetas:** costo total a pagar, mínimo real (y con qué método se obtuvo), garantía H(d), cuánto costaría el conjunto del voraz normal (Parte 2) con estos costos y, en la versión con parciales, la diferencia contra solo completas y lo que se depuró.
- **Paso a paso** (anterior, siguiente, reproducir y deslizador): los riesgos aparecen como cubiertos, nuevos en este paso o pendientes; cada paso explica qué opción se eligió, cuánto cuesta, cuántos riesgos nuevos cubre y el costo por riesgo nuevo, con la tabla de las mejores opciones de ese paso para ver por qué ganó. Al terminar, qué opción cubre cada riesgo.
- **No calcula nada:** el servidor (`POST /api/auditoria/variante`) lee los costos con `leer_opciones` y corre `resolver_caso_ponderado` y `depurar`, y devuelve las dos versiones. Si el caso no trae costos, la página lo dice; si el archivo tiene costos mal escritos, muestra el error del lector.
- **Desde `/aleatorios`:** `/auditoria?caso=NOMBRE&modo=variante` carga el caso y abre directamente esta vista. Los archivos son `estatico/variante.js` y el panel `#panel-variante` de `index.html`.

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
                            API de la Parte 1: /api/aceleracion/resolver y /api/aceleracion/previsualizar,
                            API de casos aleatorios: /api/aleatorios/{estado,caso,traza,generar,subir,probar,solo-pd,solo-voraz})
    fuerza_bruta_demo.py    demostración de la fuerza bruta (Parte 2): módulo del servidor y comando de terminal
    estatico/
        inicio.html, inicio.css            página de inicio (elegir la parte)
        aceleracion.html, .js, .css        visor de la Parte 1 (tabla de la DP)
        aleatorios.html, .js               pruebas aleatorias: tres modos, resultados por parte (se sirve en /aleatorios)
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
