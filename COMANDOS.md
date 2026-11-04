# Comandos del proyecto

> Documento vivo: se agrega una fila cada vez que el proyecto suma un comando nuevo.
> Última actualización: 2026-11-03 (se retiró el comando del enfoque exploratorio; el visor local se marca como no versionado).
> Salvo que se indique otra cosa, todos los comandos se ejecutan **desde la raíz del proyecto** (`/home/makkima16/Universidad/Algoritmos/Proyecto`).

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

## Visor local (no se versiona)

| Comando | Ruta desde donde se ejecuta | Para qué sirve |
| --- | --- | --- |
| `python3 frontend/servidor.py` | Raíz | Levanta el visor local del voraz (Parte 2) en `http://127.0.0.1:8765`: página para crear un caso (formulario o texto) y ver la decisión paso a paso con lenguaje no técnico. Opciones: `--puerto N`, `--no-abrir`. Detener con Ctrl+C. No es parte de la entrega ni del repositorio: la carpeta `frontend/` solo existe en la máquina de su autor. |
