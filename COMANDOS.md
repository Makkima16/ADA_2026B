# Comandos del proyecto

> Documento vivo: se agrega una fila cada vez que el proyecto suma un comando nuevo.
> Última actualización: 2026-11-04 (el visor entra al repositorio; limpieza de archivos que ya no se usan).
> Salvo que se indique otra cosa, todos los comandos se ejecutan **desde la raíz del proyecto** (la carpeta que contiene `README.md`).

## Entorno virtual

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 -m venv .venv` | Raíz | Crea el entorno virtual (solo una vez). |
| `source .venv/bin/activate` | Raíz | Activa el entorno virtual en la terminal actual. |
| `deactivate` | Cualquiera, con el venv activo | Sale del entorno virtual. |
| `pip install pytest` | Raíz, con el venv activo | Instala pytest dentro del venv (pendiente: registrarlo en `requirements.txt`). |

## Pruebas

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 -m pytest tests/` | Raíz, con el venv activo | Corre las pruebas (voraz contra fuerza bruta y cota H(d), traza, factibilidad). Requiere pytest instalado. |

## Resolver un caso con el voraz de la entrega

No hay un comando de terminal propio para esto todavía (ver "Pendiente"). Se hace desde Python, en la raíz:

```
python3 -c "
import sys; sys.path.insert(0, 'src')
from auditoria.lectura import leer_instancia
from auditoria.resolver import resolver_caso
from auditoria.traza import formatear_resultado
print(formatear_resultado(resolver_caso(leer_instancia('ruta/al/caso.json'))))   # también acepta .txt
"
```

Imprime la traza de elecciones, la cobertura final, el tiempo y, si n ≤ 12, el óptimo por fuerza bruta. El visor (más abajo) hace lo mismo con una interfaz.

## Resolver un caso con la DP de la Parte 1

Tampoco hay comando de terminal todavía (lo hará el `run_all.py` del integrante 3). Desde Python, en la raíz:

```
python3 -c "
import sys; sys.path.insert(0, 'src')
from aceleracion.lectura import leer_instancia
from aceleracion.resolver import resolver_caso
from aceleracion.traza import formatear_caso
print(formatear_caso(resolver_caso(leer_instancia('ruta/al/caso.json'))))   # solo .json
"
```

Imprime las etapas aceleradas, costo, ahorro, duración final, tiempo de la DP, la comprobación de la solución, el óptimo por fuerza bruta si n ≤ 12, las decisiones etapa por etapa y la tabla DP (solo si B ≤ 100). Si la instancia no cumple las restricciones lanza `ErrorDeEntrada` (resolver) o `ErrorDeLectura` (lector) con un mensaje claro. Guía de cada archivo: `docs/Guía del código de la Parte 1.md`.

## Enfoques sobre el voraz (`src/auditoria/enfoques/`, se versiona)

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 src/auditoria/enfoques/comparacion/experimento.py [--instancias N] [--semilla S]` | Raíz | Compara el voraz base con los enfoques de esenciales, parejas, rareza y todo junto contra el óptimo exacto por fuerza bruta (n ≤ 12): instancias aleatorias de tres densidades (por defecto 3000 cada una, semilla 2026), familia de cebos, la instancia más chica donde cada enfoque empeora, instancias grandes (n de 20 a 30, sin mínimo real), tiempos con n = r de 20 a 160 y la contribución de cada ingrediente. Tarda unos 20 s. Las pruebas de los enfoques están en `tests/test_enfoques.py` (las corre el `pytest` de arriba). |

| `python3 src/aceleracion/enfoques/dp_por_valor/experimento.py [--semilla S]` | Raíz | Compara la DP base (Θ(n·B)) con la DP por valor (Θ(n·D), D = Σ d_i) en familias de instancias con B grande y D chica, al revés y parecidas: tamaño de cada tabla, tiempo, si dan el mismo ahorro y cuál elige la selección automática; con B y D enormes ninguna cabe. Semilla por defecto 2026; tarda unos 5 s. Las pruebas están en `tests/test_enfoque_dp_por_valor.py`. |

| `python3 src/auditoria/enfoques/comparacion/ablacion.py [--instancias N] [--semilla S]` | Raíz | Imprime la tabla de las ocho combinaciones de ingredientes (voraz base, esenciales, rareza, parejas y sus combinaciones) sobre N instancias aleatorias por familia de densidad (ralo, medio, denso; n ≤ 12 para tener el mínimo real por fuerza bruta): cuántas veces no llega al mínimo, cuántas mejora, empata o empeora al voraz base, la razón máxima respecto del mínimo y cuántas veces se pasa de la cota H(d). Por defecto 3000 por familia y semilla 2026 (las 9000 instancias de las que salen las cifras del visor); tarda unos 7 s. Es la misma prueba de la sección 4 del visor del voraz. Con 300 por familia tarda menos de 1 s. |
| `python3 src/aceleracion/enfoques/dp_por_valor/pruebas_aleatorias.py [--instancias N] [--semilla S] [--n-min A --n-max B] [--costo-min A --costo-max B] [--ahorro-min A --ahorro-max B] [--presupuesto-pct P]` | Raíz | Pruebas aleatorias de la Parte 1 (las mismas de la sección 4 del visor): genera hasta 500 instancias con semilla fija y rangos a elección, corre las dos tablas de la DP (por presupuesto y por valor) y comprueba que dan el mismo ahorro (y, con n ≤ 12, que aciertan a la fuerza bruta). Agrupa los casos según B menor, igual o mayor que D = Σ d_i y muestra, por grupo, las celdas y el tiempo medio de cada tabla y en cuántos casos la de menos celdas fue también la más rápida. Una tabla de más de 1.500.000 celdas no se corre (se cuenta) y todo se corta a los 25 s. Por defecto 200 casos, n de 5 a 30, costos y ahorros de 1 a 30, B = 50 % del costo total (gana presupuesto); con `--costo-min 1000 --costo-max 9999 --ahorro-max 9` gana valor. Las pruebas están en `tests/test_pruebas_aleatorias.py`. |
| `python3 casos_propios/pd/generar_casos.py [--salida CARPETA]` | Raíz | Genera los 44 casos propios de la Parte 1 (JSON con el formato del ejemplo de la profesora: bordes, la razón ahorro/costo que falla, empates, 16 casos donde gana la tabla por valor —costos grandes y ahorros chicos—, de ellos 8 donde la de presupuesto también cabe y puede correr (comparables), 6 donde gana la de presupuesto, un empate B = D, mezclas, n de 8 a 400 y un caso que debe dar error por memoria) y un `README.md` con la tabla de casos. Cada archivo trae su descripción y el resultado calculado con el código del proyecto. Semilla fija: reproduce los mismos archivos. Por defecto escribe en `casos_propios/pd/`. Las pruebas están en `tests/test_casos_propios_pd.py`. |

| `python3 casos_propios/voraz/convertir_a_json.py` | Raíz | Convierte los 20 casos propios de la Parte 2 de `.txt` (carpeta `casos_propios/voraz/txt_originales/`) a `.json` con el formato del ejemplo de la profesora (`categorias_riesgo` R01..Rr y `etapas` E01..En con `riesgos_cubiertos_auditoria_completa`; los comentarios del `.txt` pasan a la clave `descripcion`). La instancia leída es idéntica a la original (lo comprueba `tests/test_casos_propios_voraz.py`). Los `.txt` se conservan en `txt_originales/`. |

## Visor (`frontend/`, se versiona)

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 frontend/servidor.py` | Raíz | Levanta el visor local en `http://127.0.0.1:8765`: **página de inicio** para elegir la Parte 1 (`/aceleracion`: tabla de la programación dinámica paso a paso, con caso por archivo `.json`, formulario o texto, y selector entre la tabla por presupuesto y la tabla por valor) o la Parte 2 (`/auditoria`, voraz): página para subir un caso (`.json` o `.txt`), crearlo en el formulario o pegarlo como texto y ver la decisión paso a paso con lenguaje no técnico. Incluye un botón de voraz normal y tres botones de ingredientes combinables (esenciales / rareza / parejas) que cambian todo el paso a paso, la comparación entre las ocho combinaciones, el porqué de cada elección y el cuadro de costo total. Opciones: `--puerto N`, `--no-abrir`. Detener con Ctrl+C. Solo librería estándar y un navegador. Herramienta de demostración: no es un entregable (ver `frontend/README.md`). |
| `python3 frontend/fuerza_bruta_demo.py CASO [CASO ...]` | Raíz | Demostración de la fuerza bruta sobre uno o varios casos (`.json` o `.txt`): prueba las combinaciones por tamaño, muestra cuántas revisó de 2^n, el mínimo real, el tiempo y lo compara con el voraz. Solo con n ≤ 12; con más interacciones o si el caso no es factible avisa y no ejecuta. |

## Pendiente

| Comando | Quién | Estado |
| --- | --- | --- |
| Correr todos los casos de `casos/` y generar las evidencias (resultado, tiempo y traza por caso) | Integrante 3 | Pendiente: lo completa el integrante 3 cuando lleguen los casos. |
| `pip install -r requirements.txt` | Integrante 3 | Pendiente: `requirements.txt` aún no existe (hoy solo se necesita `pytest`). |
