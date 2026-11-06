# Proyecto ADA 2026-B — Grupo 3 (Ruta crítica y auditoría)

Proyecto semestral de Análisis y Diseño de Algoritmos, Universidad de Caldas.
Equipo de 3 personas. Idioma de trabajo: **español** (código en inglés o español, pero comentarios, informe y manual en español).

## Fuentes y orden de prioridad (en `context/`)

Si dos fuentes se contradicen, manda la de mayor prioridad:

1. `Guia_Primera_Entrega_ADAG_2026B_Resumen.md` (también existe el .docx): la guía de la primera entrega.
2. `Proyecto-2026B.md`.
3. `Proyecto ADA Grupo 3 — Tareas por integrante (primera entrega).md`: reparto de tareas.
4. `Proyecto_ADAG3.md`: enunciado completo. Léelo antes de tocar algoritmos o escribir pruebas formales (@context/Proyecto_ADAG3.md).

La documentación del proyecto (informe y, luego, manual técnico) vive en `docs/`.

## Qué es el proyecto

Dos problemas independientes, ambos NP-difíciles:

1. **Parte 1 — Aceleración de la cadena (Mochila 0/1).** n etapas en serie con duración t_i, costo de acelerar c_i y reducción d_i (0 ≤ d_i ≤ t_i). Presupuesto entero B. Maximizar Σ d_i de las etapas aceleradas con Σ c_i ≤ B. Duración final = Σ t_i − Σ d_i.
   - Exacto: programación dinámica, T(n, B) = O(n·B), **pseudo-polinomial**.
   - Reducción de NP-dureza: **desde Mochila 0/1** (c_i = w_i, d_i = v_i, t_i = v_i, B = W, L = Σv_i − V).
2. **Parte 2 — Cobertura mínima de auditoría (Set Cover).** n interacciones, r categorías de riesgo; cada interacción cubre un subconjunto. Minimizar cuántas se auditan para cubrir las r categorías.
   - Aproximado: voraz (elige la que cubre más categorías aún no cubiertas), garantía H(d) = 1 + 1/2 + … + 1/d ≤ ln r + 1 (Johnson 1974; Chvátal 1979).
   - Eficiencia del voraz: T(n, r) = O(n·r·min(n, r)). Es más ajustada que O(n·r²) y ambas son correctas; usar la ajustada y mencionar la otra.
   - Exacto (solo para verificar): fuerza bruta con n ≤ 12 y, para n mayor, el mínimo por subconjuntos de categorías con r ≤ 16 (`src/auditoria/verificacion_exacta.py`; coincide con la fuerza bruta donde las dos valen).
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

**Formato de los casos:** llegó un ejemplo (`entrada_G3_mochila_20_nodos.json`) y se lee tal cual para las dos partes y la variante. Si los casos finales cambian, se adapta solo la lectura. Se ignoran, por ser de entregas posteriores, `flujo`, `presupuesto_conjunto_aceleracion_y_auditoria` y la `importancia` de las categorías (esta última se lee y se guarda, sin usar).
**Variante 1, parcial y completa:** la profesora no ha confirmado cuál usar y ningún documento define «parcial», así que se miden **las dos versiones**: «solo completas» (un costo a_j por interacción, la definición de la variante y la versión principal, fila `variante1`) y «con parciales» (cada variación es una opción con su costo; extensión, fila `variante1_parcial`). La extensión se compara contra la versión principal del mismo caso.

## Estructura del repositorio (convención)

```
CLAUDE.md
README.md
requirements.txt
run_all.py            # corre todos los casos y genera evidencias (lo crea el integrante 3; aún no está en el repo)
context/                 # enunciado, guía de entrega, manual técnico, informe
src/aceleracion/      # Parte 1 completa: algoritmo (DP), resolver de un caso, fuerza bruta de verificación, lectura de casos y traza
src/aceleracion/enfoques/ # enfoques aparte de la DP base (Parte 1): DP por valor y elección automática; no reemplazan a src/aceleracion/aceleracion.py
src/auditoria/        # Parte 2 completa: voraz, fuerza bruta, lectura de casos, resolución, traza y variante ponderada; verificacion_exacta.py (mínimo real por subconjuntos de categorías) y experimento_ponderada.py (verificación experimental de la variante)
src/auditoria/enfoques/  # enfoques aparte del voraz base (Parte 2) y su experimento; no reemplazan a src/auditoria/auditoria.py
src/generacion_casos/ # generador de casos aleatorios (formato JSON de la profesora), vaciado seguro de las carpetas temporales y prueba vía run_all.py
frontend/             # visor local de apoyo (inicio, Parte 1, Parte 2 y pruebas aleatorias); solo importa de src/aceleracion/, src/auditoria/ y src/generacion_casos/
casos/                # casos de la profesora (SOLO LECTURA)
resultados/           # salida, tiempo y traza por caso (se regenera completo)
Casos/                # casos propios y temporales (carpeta del grupo, no confundir con casos/ de la profesora)
  casos_propios/      #   casos propios fijos: pd/ (Parte 1) y voraz/ (Parte 2); se versionan
  casos_temporales/   #   casos aleatorios del visor o de probar_aleatorios.py (se vacía y reescribe en cada generación; en .gitignore)
Resultados/           # evidencias del grupo (no confundir con resultados/ de la entrega oficial)
  resultados_propios/ #   evidencias de los casos propios; se versionan
  resultados_temporales/ # evidencias de los casos temporales (se vacía y reescribe en cada prueba; en .gitignore)
probar_aleatorios.py  # genera casos aleatorios y los prueba desde la terminal (llama a run_all.py, no lo reemplaza)
tests/                # pruebas (DP vs fuerza bruta, voraz vs óptimo y cota H(d))
```

## Reglas de código

- Python 3.8+. Preferir solo librería estándar; si se agrega una dependencia, registrarla en `requirements.txt`.
- **Reproducible:** semillas fijas en todo generador aleatorio. Mismo código + mismos casos = mismos resultados.
- **No editar la lógica de los algoritmos para adaptarlos a un caso.** Si un caso no encaja, se adapta la lectura de entrada, nunca el algoritmo.
- Medir tiempos con `time.perf_counter()`. Cada caso se identifica por nombre en la salida.
- Fuerza bruta solo para verificar, con n ≤ ~12. Con n mayor y r ≤ 16, el mínimo real se obtiene por subconjuntos de categorías (`verificacion_exacta.py`), también solo para verificar: no es un algoritmo de la entrega ni un enfoque del voraz.
- Separar siempre algoritmo, lectura de entrada y escritura de traza, para poder reutilizarlos en las variantes.
- **Costo de los algoritmos** (`src/aceleracion/aceleracion.py` para la DP y `src/auditoria/auditoria.py` para el voraz): sin comentarios de costo línea por línea. Al final de cada uno de esos archivos va un bloque corto con el costo de cada función (T(n, B) o T(n, r)) y **por qué** sale ese costo. Los demás archivos (lectura, traza, verificación) no llevan análisis de costo; `resolver.py` solo una nota breve. Son comentarios: no cambian la lógica.
- Notación única en todo el proyecto: n, B, r, t_i, c_i, d_i, S_j, a_j (costo de auditar j), A (etapas aceleradas), J (interacciones auditadas).

## Comandos

```
python3 run_all.py --casos casos/ --salida resultados/    # todas las evidencias
python3 -m pytest tests/                                   # pruebas
python3 probar_aleatorios.py                               # genera casos aleatorios y los prueba (carpetas temporales)
```

Si un comando no existe todavía, créalo siguiendo esta convención en vez de inventar otra. **Excepción: `run_all.py`.** Lo creó el integrante 3; los demás integrantes no deben crear su propia versión. Debe cumplir esto:
- Usa solo las funciones públicas de cada parte: `src/aceleracion/` (`leer_instancia`, `resolver_caso`, `formatear_caso` y, para los enfoques, `enfoques/resolver_enfoques`: `resolver_enfoques_p1`, `formatear_solucion_p1`, `formatear_enfoques_p1`, `tabla_enfoques_p1`) y `src/auditoria/` (`leer_instancia`, `resolver_caso`, `formatear_resultado`; los enfoques del voraz con `enfoques/comparacion/resolver_enfoques`; la variante con `leer_opciones`, `resolver_caso_ponderado`, `depurar` y `formatear_opciones`). No reimplementa algoritmos ni lectura.
- Recibe `--casos` (directorio de entrada, solo lectura) y `--salida` (directorio donde regenera **todo** `resultados/`). Opcionales: `--lista` (solo los casos nombrados en un archivo), `--partes parte1 parte2 variante` (qué revisar; por defecto las tres) y `--sin-enfoques` (solo las soluciones base).
- Por caso escribe resultado, tiempo y traza, identificados por nombre de caso. Parte 1 y Parte 2 (y la variante ponderada) deben quedar en la misma versión.
- **Mide todos los enfoques, no solo la base.** Parte 1: la DP por presupuesto (base) y la DP por valor, cada una si cabe en memoria; si la base no cabe, el caso se resuelve solo por valor y la evidencia lo dice; si ninguna cabe, el mensaje es que la tabla es demasiado grande. Parte 2: las ocho combinaciones del voraz (base, esenciales, rareza, parejas y sus combinaciones; «todo junto» es la última). Los resultados quedan en `resumen.csv`, en los archivos `*_enfoques.txt` y en las tablas de `comparacion.md`, y se ven también en el visor (`/aleatorios`).
- **Casos de una sola parte:** si un caso no trae los datos de una parte (solo PD o solo voraz), esa parte figura como «no aplica» y no cuenta como error; un archivo mal formado o sin datos de ninguna parte sí da `ERROR`. Además de `resumen.csv` y `comparacion.md` (que empieza por el resumen) escribe `resumen_enfoques.json`, que usa el visor.
- `run_all.py` ya está en el repositorio. La lectura de la variante ponderada soporta el formato de la profesora (`variaciones_auditoria` con `completa` y `parcial`) y, como respaldo, `costo_auditoria` por etapa o `# costos:` en `.txt`.

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