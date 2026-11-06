"""Pruebas de los enfoques medidos en cada parte (`resolver_enfoques_p1` y `resolver_enfoques_p2`) y de run_all con ellos."""

import csv
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import run_all  # noqa: E402
from aceleracion.enfoques.resolver_enfoques import (  # noqa: E402
    agregar_p1, formatear_enfoques_p1, formatear_solucion_p1, resolver_enfoques_p1, resumen_md_p1, tabla_enfoques_p1)
from aceleracion.enfoques.seleccion import PRESUPUESTO, VALOR  # noqa: E402
from aceleracion.resolver import InstanciaAceleracion  # noqa: E402
from auditoria.enfoques.comparacion.resolver_enfoques import (  # noqa: E402
    agregar_p2, formatear_enfoques_p2, resolver_enfoques_p2, resumen_md_p2, tabla_enfoques_p2)
from auditoria.resolver import Instancia  # noqa: E402
from generacion_casos import generador  # noqa: E402


# ------------------------------------------------------------------ Parte 1

def _p1(t, c, d, B, nombre="caso"):
    return InstanciaAceleracion(nombre, list(t), list(c), list(d), B)


def test_p1_las_dos_tablas_caben_y_coinciden():
    comp = resolver_enfoques_p1(_p1([5, 4, 6], [2, 3, 4], [3, 4, 5], 5))
    assert comp.usada == PRESUPUESTO and comp.coinciden is True
    assert comp.presupuesto.resultado.ahorro == comp.valor.resultado.ahorro == 7
    assert comp.mas_rapida in (PRESUPUESTO, VALOR)
    assert "Las dos tablas dieron el mismo ahorro" in formatear_enfoques_p1(comp)


def test_p1_si_la_base_no_cabe_se_resuelve_solo_por_valor():
    comp = resolver_enfoques_p1(_p1([5, 4, 6], [2, 3, 4], [3, 4, 5], 10_000_000))      # (n+1)(B+1) = 4·10^7 > límite
    assert not comp.presupuesto.cabe and comp.presupuesto.resultado is None
    assert comp.valor.cabe and comp.usada == VALOR and comp.coinciden is None
    assert comp.resultado.ahorro == 12 and comp.resultado.aceleradas == [1, 2, 3]     # B enorme: todo cabe
    texto = formatear_solucion_p1(comp)
    assert "SOLO con la DP por valor" in texto and "DP por valor" in texto


def test_p1_si_ninguna_cabe_el_mensaje_es_que_es_demasiado_grande():
    grande = 2_000_000
    comp = resolver_enfoques_p1(_p1([grande] * 5, [1] * 5, [grande] * 5, 10_000_000))
    assert comp.usada is None and comp.resultado is None
    assert "demasiado grande y no cabe" in comp.mensaje_no_cabe()
    assert formatear_solucion_p1(comp).startswith("Caso: caso\nERROR en la Parte 1: la tabla es demasiado grande")
    assert "Ninguna tabla cabe" in formatear_enfoques_p1(comp)


def test_p1_liviano_quita_las_tablas_y_conserva_el_resultado():
    comp = resolver_enfoques_p1(_p1([5, 4, 6], [2, 3, 4], [3, 4, 5], 5)).liviano()
    assert comp.presupuesto.resultado.tabla == [] and comp.valor.resultado.tabla == []
    assert comp.presupuesto.resultado.ahorro == 7


def test_p1_el_resumen_cuenta_cada_situacion():
    comps = [resolver_enfoques_p1(_p1([5, 4, 6], [2, 3, 4], [3, 4, 5], 5, "a")),
             resolver_enfoques_p1(_p1([5, 4, 6], [2, 3, 4], [3, 4, 5], 10_000_000, "b")),
             resolver_enfoques_p1(_p1([2_000_000] * 5, [1] * 5, [2_000_000] * 5, 10_000_000, "c"))]
    agg = agregar_p1([c.liviano() for c in comps])
    assert agg["hechas"] == 3 and agg["ambas"] == {"corridas": 1, "coinciden": 1}
    assert agg["solo_valor"] == 1 and agg["ninguna_cabe"] == 1 and agg["no_corridas"] == {PRESUPUESTO: 2, VALOR: 1}
    assert agg["recomendado"] == {PRESUPUESTO: 1, VALOR: 1, "empate": 0, "ninguna": 1}
    assert agg["fuerza_bruta"] == {"comparadas": 2, "presupuesto_ok": 1, "valor_ok": 2}   # n <= 12: dos casos con óptimo
    assert [agg["regiones"][r]["casos"] for r in ("B menor que D", "B igual a D", "B mayor que D")] == [1, 1, 1]   # c: B = D = 10^7
    texto = resumen_md_p1(agg)
    assert "**3 casos.** Las dos tablas cupieron en 1 y dieron el mismo ahorro en 1" in texto
    assert "**Solo por valor:** 1 casos" in texto and "**Ninguna cabe:** 1" in texto
    assert resumen_md_p1(None) == "" and tabla_enfoques_p1([]) == "" and "| a |" in tabla_enfoques_p1(comps)


# ------------------------------------------------------------------ Parte 2

CLASICO = Instancia("clasico", 6, [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}])      # el voraz usa 3 y el óptimo 2


def test_p2_corre_las_ocho_combinaciones_y_las_compara_con_el_optimo():
    comp = resolver_enfoques_p2(CLASICO)
    assert [m.identificador for m in comp.medidas] == ["voraz", "esenciales", "rareza", "parejas", "esenciales_rareza",
                                                         "esenciales_parejas", "rareza_parejas", "todo"]
    assert all(m.cubre for m in comp.medidas)
    assert len(comp.optimo) == 2 and len(comp.base.J) == 3 and comp.razon(comp.base) == 1.5
    assert len(next(m for m in comp.medidas if m.clave == "erp").J) == 2        # «todo junto» arregla este caso
    texto = formatear_enfoques_p2(comp)
    assert "Enfoque: Voraz base" in texto and "Enfoque: Los tres" in texto and "mejor" in texto


def test_p2_reutiliza_el_optimo_ya_calculado_y_lo_calcula_por_subconjuntos_con_n_grande():
    assert resolver_enfoques_p2(CLASICO, optimo=[2, 3]).optimo == [2, 3]
    n13 = Instancia("n13", 4, [{1, 2}, {3, 4}] + [{1}] * 11)                      # n = 13 > 12 pero r = 4 <= 16
    assert sorted(resolver_enfoques_p2(n13).optimo) == [1, 2]                      # el mínimo real llega por subconjuntos de categorías
    r17 = Instancia("r17", 17, [set(range(1, 10)), set(range(10, 18))] + [{1}] * 11)   # n = 13 y r = 17: ninguna verificación aplica
    assert resolver_enfoques_p2(r17).optimo is None


def test_p2_caso_no_factible_no_corre_ningun_enfoque():
    comp = resolver_enfoques_p2(Instancia("roto", 3, [{1}, {2}]))
    assert not comp.factible and comp.medidas == [] and 3 in comp.sin_cubrir
    assert "no es factible" in formatear_enfoques_p2(comp) and tabla_enfoques_p2([comp]) == ""


def test_p2_el_resumen_por_enfoque():
    c = resolver_enfoques_p2(CLASICO)
    agg = agregar_p2([c.liviano()])
    assert agg["instancias"] == 1 and agg["con_optimo"] == 1 and agg["fallan_cobertura"] == 0
    assert agg["Voraz base"]["no_optimo"] == 1 and agg["Voraz base"]["razon_max"] == 1.5
    assert agg["Los tres (enfoque D)"]["no_optimo"] == 0 and agg["Los tres (enfoque D)"]["mejora"] == 1
    assert agg["por_familia"][c.familia]["Voraz base"] == 1 and sum(agg["casos_por_familia"].values()) == 1
    assert agg["ejemplos"] == {} or all(len(v) <= 3 for v in agg["ejemplos"].values())
    texto = resumen_md_p2(agg)
    assert "| Voraz base | 1 de 1 | — (es la referencia) | 1.500 |" in texto
    assert "| Los tres (enfoque D) | 0 de 1 | 1 / 0 / 0 | 1.000 |" in texto
    assert "0 de 8 ejecuciones no cubrieron" in texto
    assert "caso por caso" in tabla_enfoques_p2([c.liviano()]) and resumen_md_p2(None) == ""


def test_p2_los_ejemplos_son_los_casos_donde_el_enfoque_empeoro():
    # Contraejemplo donde «rareza» usa más que el voraz base se busca con una instancia generada: si no hay, no hay ejemplos
    comps = [resolver_enfoques_p2(Instancia("c%d" % k, 6, s)).liviano() for k, s in enumerate(
        [[{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}], [{1, 2}, {3, 4}, {5, 6}]])]
    agg = agregar_p2(comps)
    for lista in agg["ejemplos"].values():
        for e in lista:
            assert e["archivo"].endswith("_parte2_enfoques.txt") and len(e["combinacion"]) > len(e["voraz"])


# ------------------------------------------------------------------ run_all con todo

def _caso(nombre, **cambios):
    caso = generador.generar_caso(nombre, 6, 5, 7, 0.4)
    caso["parametros"].update(cambios.pop("parametros", {}))
    for i, e in enumerate(caso["etapas"]):
        for k, v in cambios.items():
            e[k] = v[i] if isinstance(v, list) else v
    return caso


def test_run_all_mide_los_enfoques_y_resuelve_por_valor_lo_que_la_base_no_cabe(tmp_path):
    casos = tmp_path / "casos"
    casos.mkdir()
    normal = _caso("a_normal")
    enorme = _caso("b_base_no_cabe", parametros={"presupuesto_aceleracion_B": 20_000_000})
    imposible = _caso("c_ninguna_cabe", parametros={"presupuesto_aceleracion_B": 20_000_000},
                      duracion_normal=2_000_000, reduccion_tiempo_si_acelera=2_000_000)
    for c in (normal, enorme, imposible):
        (casos / (c["nombre"] + ".json")).write_text(json.dumps(c), encoding="utf-8")
    salida = tmp_path / "resultados"
    codigo = run_all.main(["--casos", str(casos), "--salida", str(salida), "--sin-tabla"])

    filas = {(f["caso"], f["parte"]): f for f in csv.DictReader(open(salida / "resumen.csv", encoding="utf-8"))}
    assert filas[("a_normal", "parte1")]["resultado"].startswith("A=")
    assert "[solo por valor" in filas[("b_base_no_cabe", "parte1")]["resultado"]     # base no cabe: solo por valor
    assert filas[("b_base_no_cabe", "parte1_presupuesto")]["resultado"].startswith("no cabe")
    assert filas[("b_base_no_cabe", "parte1_valor")]["resultado"].startswith("ahorro=")
    assert filas[("c_ninguna_cabe", "parte1")]["resultado"].startswith("ERROR: la tabla es demasiado grande y no cabe")
    assert codigo == 1                                                               # el que no cabe en ninguna cuenta como error
    for caso in ("a_normal", "b_base_no_cabe", "c_ninguna_cabe"):
        for sufijo in ("_parte1_enfoques.txt", "_parte2_enfoques.txt"):
            assert (salida / (caso + sufijo)).exists(), caso + sufijo
        assert ("c_ninguna_cabe" == caso) or (caso, "parte2_todo") in filas
        assert (caso, "parte2_voraz") in filas
    assert "AVISO: la tabla por presupuesto no cabe" in (salida / "b_base_no_cabe_parte1.txt").read_text(encoding="utf-8")
    md = (salida / "comparacion.md").read_text(encoding="utf-8")
    assert md.index("## Resumen") < md.index("## Detalle por caso")                     # el resumen va arriba
    assert "### Parte 1 — las dos tablas de la DP" in md and "### Parte 2 — los ocho enfoques del voraz" in md
    assert "| b_base_no_cabe |" in md and "por valor" in md and "no cabe ninguna" in md
    resumen = json.loads((salida / "resumen_enfoques.json").read_text(encoding="utf-8"))
    assert resumen["casos"] == 3 and resumen["parte1"]["solo_valor"] == 1 and resumen["parte1"]["ninguna_cabe"] == 1
    assert resumen["parte2"]["instancias"] == 3 and resumen["variante"]["casos"] == 3     # los tres traen la Parte 2


def test_run_all_regenera_los_archivos_de_enfoques(tmp_path):
    casos = tmp_path / "casos"
    casos.mkdir()
    (casos / "a.json").write_text(json.dumps(_caso("a")), encoding="utf-8")
    salida = tmp_path / "res"
    salida.mkdir()
    (salida / "viejo_parte2_enfoques.txt").write_text("viejo", encoding="utf-8")
    run_all.main(["--casos", str(casos), "--salida", str(salida), "--sin-tabla"])
    assert not (salida / "viejo_parte2_enfoques.txt").exists() and (salida / "a_parte2_enfoques.txt").exists()


# ------------------------------------------------------------------ casos de una sola parte: «no aplica», no error

def test_los_archivos_de_una_sola_parte_no_dan_error_en_la_parte_que_no_traen(tmp_path):
    from aceleracion.lectura import trae_datos as trae1
    from auditoria.lectura import trae_datos as trae2
    casos = tmp_path / "casos"
    casos.mkdir()
    completo = _caso("a_completo")
    solo_pd = {"parametros": {"presupuesto_aceleracion_B": 5}, "etapas": [
        {"id": "E01", "duracion_normal": 5, "costo_aceleracion": 2, "reduccion_tiempo_si_acelera": 3},
        {"id": "E02", "duracion_normal": 4, "costo_aceleracion": 3, "reduccion_tiempo_si_acelera": 4}], "nombre": "b_solo_pd"}
    solo_voraz = {"categorias_riesgo": [{"id": "R01", "categoria": "x"}, {"id": "R02", "categoria": "y"}], "etapas": [
        {"id": "E01", "riesgos_cubiertos_auditoria_completa": ["R01"]}, {"id": "E02", "riesgos_cubiertos_auditoria_completa": ["R02"]}]}
    vacio = {"nombre": "d_nada", "otra_cosa": 1}
    for nombre, c in (("a_completo", completo), ("b_solo_pd", solo_pd), ("c_solo_voraz", solo_voraz), ("d_nada", vacio)):
        (casos / (nombre + ".json")).write_text(json.dumps(c), encoding="utf-8")
    assert (trae1(casos / "b_solo_pd.json"), trae2(casos / "b_solo_pd.json")) == (True, False)
    assert (trae1(casos / "c_solo_voraz.json"), trae2(casos / "c_solo_voraz.json")) == (False, True)

    salida = tmp_path / "res"
    codigo = run_all.main(["--casos", str(casos), "--salida", str(salida), "--sin-tabla"])
    filas = {(f["caso"], f["parte"]): f["resultado"] for f in csv.DictReader(open(salida / "resumen.csv", encoding="utf-8"))}
    assert filas[("b_solo_pd", "parte1")].startswith("A=")
    assert filas[("b_solo_pd", "parte2")].startswith("no aplica") and filas[("b_solo_pd", "variante1")].startswith("no aplica")
    assert filas[("c_solo_voraz", "parte1")].startswith("no aplica") and filas[("c_solo_voraz", "parte2")].startswith("J=")
    assert ("b_solo_pd", "parte2_voraz") not in filas and ("c_solo_voraz", "parte1_valor") not in filas   # sin enfoques de lo que no aplica
    assert filas[("d_nada", "parte1")].startswith("ERROR: el archivo no trae datos de ninguna")      # ese sí es un error
    assert codigo == 1                                                                                  # solo por d_nada
    md = (salida / "comparacion.md").read_text(encoding="utf-8")
    assert "No aplica la Parte 1 en 1 casos" in md and "c_solo_voraz" in md and "No aplica la Parte 2 en 1 casos" in md
    assert not any(v.startswith("ERROR") for (c, _), v in filas.items() if c in ("b_solo_pd", "c_solo_voraz"))
    # lo que no aplica deja su fila en el resumen, pero sin archivo de traza
    trazas = {(f["caso"], f["parte"]): f["traza"] for f in csv.DictReader(open(salida / "resumen.csv", encoding="utf-8"))}
    assert trazas[("b_solo_pd", "parte2")] == "" and trazas[("c_solo_voraz", "parte1")] == "" and trazas[("b_solo_pd", "variante1")] == ""
    assert not (salida / "b_solo_pd_parte2.txt").exists() and not (salida / "c_solo_voraz_parte1.txt").exists()
    assert (salida / "b_solo_pd_parte1.txt").exists() and (salida / "c_solo_voraz_parte2.txt").exists()


def test_la_opcion_lista_corre_solo_los_casos_pedidos(tmp_path):
    casos = tmp_path / "casos"
    casos.mkdir()
    for nombre in ("a", "b", "c"):
        (casos / (nombre + ".json")).write_text(json.dumps(_caso(nombre)), encoding="utf-8")
    lista = tmp_path / "lista.txt"
    lista.write_text("# comentario\nc   # el último\na\n\n", encoding="utf-8")
    salida = tmp_path / "res"
    assert run_all.main(["--casos", str(casos), "--salida", str(salida), "--lista", str(lista), "--sin-tabla"]) == 0
    assert {f["caso"] for f in csv.DictReader(open(salida / "resumen.csv", encoding="utf-8"))} == {"a", "c"}
    assert not (salida / "b_parte1.txt").exists()
    lista.write_text("a\nno_existe\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="no_existe"):
        run_all.main(["--casos", str(casos), "--salida", str(salida), "--lista", str(lista)])
    lista.write_text("# nada\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="vacía"):
        run_all.main(["--casos", str(casos), "--salida", str(salida), "--lista", str(lista)])
