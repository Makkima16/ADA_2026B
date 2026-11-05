"""Prueba de punta a punta de run_all.py en una carpeta temporal.  [Integrante 3]"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import run_all  # noqa: E402


def _preparar(tmp_path):
    casos = tmp_path / "casos"
    casos.mkdir()
    datos = {
        "parametros": {"numero_etapas": 3, "numero_categorias_riesgo": 6, "presupuesto_aceleracion_B": 5},
        "categorias_riesgo": [{"id": "R%02d" % c, "categoria": "c%d" % c} for c in range(1, 7)],
        "etapas": [
            {"id": "E01", "duracion_normal": 6, "costo_aceleracion": 2, "reduccion_tiempo_si_acelera": 3,
             "riesgos_cubiertos_auditoria_completa": ["R01", "R02", "R03"], "costo_auditoria": 6},
            {"id": "E02", "duracion_normal": 5, "costo_aceleracion": 3, "reduccion_tiempo_si_acelera": 4,
             "riesgos_cubiertos_auditoria_completa": ["R04", "R05", "R06"], "costo_auditoria": 6},
            {"id": "E03", "duracion_normal": 5, "costo_aceleracion": 4, "reduccion_tiempo_si_acelera": 5,
             "riesgos_cubiertos_auditoria_completa": ["R01", "R02", "R04", "R05"], "costo_auditoria": 4},
        ],
    }
    (casos / "a_json.json").write_text(json.dumps(datos), encoding="utf-8")
    (casos / "b_sin_costos.txt").write_text("6 3\n1 2 4 5\n1 2 3\n4 5 6\n", encoding="utf-8")
    (casos / "c_roto.txt").write_text("3 2\n1 9\n1 2 3\n", encoding="utf-8")
    return casos, tmp_path / "resultados"


def test_run_all_genera_todo(tmp_path):
    casos, salida = _preparar(tmp_path)
    antes = sorted(p.name for p in casos.iterdir())
    codigo = run_all.main(["--casos", str(casos), "--salida", str(salida)])

    assert sorted(p.name for p in casos.iterdir()) == antes            # casos/ no se toca
    for nombre in ("a_json_parte1.txt", "a_json_parte2.txt", "a_json_variante1.txt",
                   "b_sin_costos_parte2.txt", "b_sin_costos_variante1.txt", "resumen.csv", "version.txt"):
        assert (salida / nombre).exists(), nombre
    assert not (salida / "b_sin_costos_parte1.txt").exists()             # un .txt no tiene Parte 1

    filas = {(f["caso"], f["parte"]): f for f in csv.DictReader(open(salida / "resumen.csv", encoding="utf-8"))}
    assert filas[("a_json", "parte1")]["resultado"].startswith("A=[1, 2]")
    assert filas[("a_json", "variante1")]["resultado"].startswith("J=[3, 1, 2] costo=16")
    assert filas[("a_json", "variante1")]["tiempo_s"] != ""
    assert "no se ejecuta" in filas[("b_sin_costos", "variante1")]["resultado"]
    assert filas[("c_roto", "parte2")]["resultado"].startswith("ERROR")    # el error no detiene a los demás
    assert codigo == 1                                                    # hubo un caso con error
    assert "Paso 1: interacción 3 (E03)" in (salida / "a_json_variante1.txt").read_text(encoding="utf-8")


def test_run_all_regenera_y_no_borra_ajenos(tmp_path):
    casos, salida = _preparar(tmp_path)
    salida.mkdir()
    (salida / "viejo_parte2.txt").write_text("evidencia vieja", encoding="utf-8")
    (salida / "notas.md").write_text("no es de run_all", encoding="utf-8")
    run_all.main(["--casos", str(casos), "--salida", str(salida)])
    assert not (salida / "viejo_parte2.txt").exists()                    # lo generado antes se regenera
    assert (salida / "notas.md").exists()                                # lo ajeno no se borra
