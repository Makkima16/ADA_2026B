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

## Visor (`frontend/`, se versiona)

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 frontend/servidor.py` | Raíz | Levanta el visor local en `http://127.0.0.1:8765`: **página de inicio** para elegir la Parte 1 (`/aceleracion`: tabla de la programación dinámica paso a paso, con caso por archivo `.json`, formulario o texto) o la Parte 2 (`/auditoria`, voraz): página para subir un caso (`.json` o `.txt`), crearlo en el formulario o pegarlo como texto y ver la decisión paso a paso con lenguaje no técnico. Incluye un botón de voraz normal y tres botones de ingredientes combinables (esenciales / rareza / parejas) que cambian todo el paso a paso, la comparación entre las ocho combinaciones, el porqué de cada elección y el cuadro de costo total. Opciones: `--puerto N`, `--no-abrir`. Detener con Ctrl+C. Solo librería estándar y un navegador. Herramienta de demostración: no es un entregable (ver `frontend/README.md`). |
| `python3 frontend/fuerza_bruta_demo.py CASO [CASO ...]` | Raíz | Demostración de la fuerza bruta sobre uno o varios casos (`.json` o `.txt`): prueba las combinaciones por tamaño, muestra cuántas revisó de 2^n, el mínimo real, el tiempo y lo compara con el voraz. Solo con n ≤ 12; con más interacciones o si el caso no es factible avisa y no ejecuta. |

## Pendiente

| Comando | Quién | Estado |
| --- | --- | --- |
| Correr todos los casos de `casos/` y generar las evidencias (resultado, tiempo y traza por caso) | Integrante 3 | Pendiente: lo completa el integrante 3 cuando lleguen los casos. |
| `pip install -r requirements.txt` | Integrante 3 | Pendiente: `requirements.txt` aún no existe (hoy solo se necesita `pytest`). |
