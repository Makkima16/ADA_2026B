#!/usr/bin/env python3
"""Hook PostToolUse: después de que Claude edite un .py en src/ o tests/, corre las pruebas.

Si fallan, sale con código 2: el resultado le llega a Claude para que lo corrija solo.
Si no hay carpeta tests/ o no está pytest instalado, no hace nada (no estorba al empezar).
"""
import json
import os
import subprocess
import sys

LIMITE_SEGUNDOS = 120
LINEAS_A_MOSTRAR = 40


def main():
    try:
        datos = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    ruta = (datos.get("tool_input") or {}).get("file_path", "")
    if not ruta.endswith(".py"):
        return 0

    raiz = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    absoluta = os.path.realpath(os.path.join(raiz, ruta))
    en_codigo = any(
        absoluta.startswith(os.path.join(raiz, carpeta) + os.sep)
        for carpeta in ("src", "tests")
    )
    if not en_codigo or not os.path.isdir(os.path.join(raiz, "tests")):
        return 0

    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-x", "-q", "tests/"],
            cwd=raiz, capture_output=True, text=True, timeout=LIMITE_SEGUNDOS,
        )
    except subprocess.TimeoutExpired:
        print(f"Las pruebas pasaron de {LIMITE_SEGUNDOS} s; no se esperó el resultado.", file=sys.stderr)
        return 1  # error NO bloqueante

    salida = (r.stdout or "") + (r.stderr or "")
    if "No module named pytest" in salida:
        print("pytest no está instalado; se omiten las pruebas automáticas.", file=sys.stderr)
        return 1
    if r.returncode in (0, 5):  # 0 = todo bien, 5 = no hay pruebas todavía
        return 0

    cola = "\n".join(salida.strip().splitlines()[-LINEAS_A_MOSTRAR:])
    print("Las pruebas fallan después de este cambio. Corrígelo antes de seguir:\n" + cola, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
