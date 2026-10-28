#!/usr/bin/env python3
"""Hook PreToolUse (Bash): bloquea `git push --force` y sus variantes.

Bloquea: --force, -f (también combinado, p. ej. -fu), --force-with-lease, --force-if-includes
y refspecs que empiezan con "+" (git push origin +main), que también fuerzan.
Un push normal pasa. Salir con código 2 bloquea y el mensaje de stderr le llega a Claude.
"""
import json
import re
import shlex
import sys

MENSAJE = (
    "Bloqueado: git push con fuerza (--force / -f / --force-with-lease / +rama). "
    "Las reglas del proyecto exigen que el usuario lo pida explícitamente; ejecútalo él mismo si lo necesita."
)


def es_push_forzado(segmento):
    try:
        tokens = shlex.split(segmento)
    except ValueError:
        tokens = segmento.split()
    # Ubica "git ... push" (git puede llevar opciones antes, como -C dir)
    if "git" not in tokens:
        return False
    desde_git = tokens[tokens.index("git") + 1:]
    if "push" not in desde_git:
        return False
    argumentos = desde_git[desde_git.index("push") + 1:]
    for arg in argumentos:
        if arg in ("--force", "--force-with-lease", "--force-if-includes") or arg.startswith(
            ("--force=", "--force-with-lease=", "--force-if-includes=")
        ):
            return True
        if re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", arg):  # -f, -fu, -uf ...
            return True
        if arg.startswith("+") and len(arg) > 1:  # refspec con + fuerza la actualización
            return True
    return False


def main():
    try:
        datos = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if datos.get("tool_name") != "Bash":
        return 0
    comando = (datos.get("tool_input") or {}).get("command", "")

    # Revisa cada comando encadenado por ; && || | o salto de línea
    for segmento in re.split(r"&&|\|\||[;|\n]", comando):
        if es_push_forzado(segmento):
            print(MENSAJE, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
