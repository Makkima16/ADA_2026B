#!/usr/bin/env python3
"""Hook Stop: al terminar Claude, avisa si src/ cambió y resultados/ no se regeneró.

Compara la fecha de modificación más reciente de los .py de src/ con la del archivo más
reciente de resultados/. Solo AVISA (mensaje al usuario, código 0): no bloquea ni obliga
a Claude a seguir. Regla del proyecto: informe, repo, manual y evidencias deben ser de la misma versión.
"""
import json
import os
import sys


def ultima_modificacion(carpeta, solo_py=False):
    mas_reciente = None
    for base, _, archivos in os.walk(carpeta):
        if "__pycache__" in base:
            continue
        for nombre in archivos:
            if solo_py and not nombre.endswith(".py"):
                continue
            t = os.path.getmtime(os.path.join(base, nombre))
            if mas_reciente is None or t > mas_reciente:
                mas_reciente = t
    return mas_reciente


def main():
    try:
        json.load(sys.stdin)  # no usamos el contenido, pero lo consumimos
    except json.JSONDecodeError:
        pass

    raiz = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    src = os.path.join(raiz, "src")
    if not os.path.isdir(src):
        return 0
    t_src = ultima_modificacion(src, solo_py=True)
    if t_src is None:
        return 0  # todavía no hay código

    resultados = os.path.join(raiz, "resultados")
    t_res = ultima_modificacion(resultados) if os.path.isdir(resultados) else None

    if t_res is None:
        motivo = "resultados/ está vacío o no existe"
    elif t_src > t_res:
        motivo = "src/ cambió después de la última generación de resultados/"
    else:
        return 0

    aviso = (
        f"Aviso: {motivo}. Las evidencias podrían no corresponder a este código. "
        "Antes de entregar: python3 run_all.py --casos casos/ --salida resultados/"
    )
    print(json.dumps({"systemMessage": aviso}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
