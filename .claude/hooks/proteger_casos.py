#!/usr/bin/env python3
"""Hook PreToolUse: impide modificar la carpeta casos/ (casos de la profesora, solo lectura).

Claude Code le pasa por stdin un JSON con el nombre de la herramienta y sus argumentos.
Salir con código 2 BLOQUEA la acción y el mensaje de stderr se le muestra a Claude.
Salir con 0 deja pasar la acción.
"""
import json
import os
import re
import sys

MENSAJE = (
    "Bloqueado: casos/ es de solo lectura (casos de la profesora). "
    "Si el formato no encaja, adapta la lectura de entrada en src/, nunca los casos."
)


def main():
    try:
        datos = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # si no se puede leer la entrada, no bloqueamos nada

    herramienta = datos.get("tool_name", "")
    entrada = datos.get("tool_input") or {}
    raiz = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    carpeta_casos = os.path.join(raiz, "casos")

    if herramienta in ("Write", "Edit", "MultiEdit"):
        ruta = entrada.get("file_path", "")
        if ruta:
            absoluta = os.path.realpath(os.path.join(raiz, ruta))
            if absoluta == carpeta_casos or absoluta.startswith(carpeta_casos + os.sep):
                print(MENSAJE, file=sys.stderr)
                return 2

    elif herramienta == "Bash":
        # Heurística: bloquea borrar/mover/sobrescribir cosas dentro de casos/.
        # Leer (cat, ls, python3 run_all.py --casos casos/) sigue permitido.
        comando = entrada.get("command", "")
        if (
            re.search(r"\b(rm|mv|truncate|tee)\b[^|;&]*\bcasos/", comando)
            or re.search(r"\bsed\s+-i\b[^|;&]*\bcasos/", comando)
            or re.search(r">>?\s*(\./)?casos/", comando)
        ):
            print(MENSAJE, file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
