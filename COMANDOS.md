# Comandos del proyecto

> Documento vivo: se agrega una fila cada vez que el proyecto suma un comando nuevo.
> Última actualización: 2026-10-27 (experimento del enfoque de esenciales).
> Salvo que se indique otra cosa, todos los comandos se ejecutan **desde la raíz del proyecto** (`/home/makkima16/Universidad/Algoritmos/Proyecto`).

## Entorno virtual

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 -m venv .venv` | Raíz | Crea el entorno virtual (solo una vez; ya está creado). |
| `source .venv/bin/activate` | Raíz | Activa el entorno virtual en la terminal actual. |
| `deactivate` | Cualquiera, con el venv activo | Sale del entorno virtual. |
| `pip install pytest` | Raíz, con el venv activo | Instala pytest dentro del venv (pendiente: registrarlo en `requirements.txt`). |

## Pruebas

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 -m pytest tests/` | Raíz, con el venv activo | Corre las pruebas (voraz contra fuerza bruta y cota H(d), traza, factibilidad). Requiere pytest instalado. |

## Enfoques exploratorios

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 src/enfoques/esenciales/experimento.py` | Raíz | Compara el enfoque de interacciones esenciales contra el voraz estándar y el óptimo (3000 instancias, semilla 2026). No es parte de la entrega. |

## Evidencias

| Comando | Ruta desde donde se ejecuta | Para qué sirve | Estado |
| --- | --- | --- | --- |
| `python3 run_all.py --casos casos/ --salida resultados/` | Raíz | Corre todos los casos y genera resultado, tiempo y traza por caso. | Pendiente: `run_all.py` aún no existe (depende del formato de los casos de la profesora). |
