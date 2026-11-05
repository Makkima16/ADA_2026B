"""Pruebas del módulo de lectura de casos (formato propio provisional)."""

import pytest

from ruta.lectura import ErrorDeLectura, leer_casos, leer_instancia


def _escribir(tmp_path, nombre, contenido):
    archivo = tmp_path / nombre
    archivo.write_text(contenido, encoding="utf-8")
    return archivo


def test_lee_un_caso(tmp_path):
    archivo = _escribir(tmp_path, "03_clasico.txt", "6 3\n1 2 4 5\n1 2 3\n4 5 6\n")
    inst = leer_instancia(archivo)
    assert inst.nombre == "03_clasico"
    assert inst.r == 6
    assert inst.S == [{1, 2, 4, 5}, {1, 2, 3}, {4, 5, 6}]


def test_ignora_comentarios_y_lineas_vacias(tmp_path):
    archivo = _escribir(tmp_path, "caso.txt", "# comentario\n\n3 2\n1 2   # otra nota\n\n3\n")
    inst = leer_instancia(archivo)
    assert inst.nombre == "caso"
    assert inst.r == 3 and len(inst.S) == 2
    assert inst.S == [{1, 2}, {3}]


def test_leer_casos_los_ordena_por_nombre(tmp_path):
    _escribir(tmp_path, "b.txt", "2 1\n1 2\n")
    _escribir(tmp_path, "a.txt", "1 1\n1\n")
    instancias = leer_casos(tmp_path)
    assert [i.nombre for i in instancias] == ["a", "b"]


@pytest.mark.parametrize(
    "contenido, mensaje",
    [
        ("", "no tiene datos"),
        ("3\n1 2\n", "se esperaba 'r n'"),
        ("3 2\n1 2\n", "se esperaban 2 interacciones"),
        ("3 1\n1 4\n", "fuera de 1..3"),
        ("3 1\n1 1\n", "repetidas"),
        ("3 1\n1 a\n", "deben ser enteros"),
    ],
)
def test_errores_de_formato_indican_el_problema(tmp_path, contenido, mensaje):
    archivo = _escribir(tmp_path, "roto.txt", contenido)
    with pytest.raises(ErrorDeLectura) as exc:
        leer_instancia(archivo)
    assert mensaje in str(exc.value)


# ---------------------------- formato JSON ----------------------------

import json  # noqa: E402


def _json_base():
    """Caso mínimo en el formato de la profesora (3 etapas, 4 categorías)."""
    return {
        "parametros": {"numero_etapas": 3, "numero_categorias_riesgo": 4},
        "categorias_riesgo": [
            {"id": "R01", "categoria": "sesgo", "importancia": 4},
            {"id": "R02", "categoria": "privacidad", "importancia": 5},
            {"id": "R03", "categoria": "formato", "importancia": 2},
            {"id": "R04", "categoria": "seguridad", "importancia": 5},
        ],
        "etapas": [
            {"id": "E01", "riesgos_cubiertos_auditoria_completa": ["R01", "R02"]},
            {"id": "E02", "riesgos_cubiertos_auditoria_completa": ["R02", "R03"]},
            {"id": "E03", "riesgos_cubiertos_auditoria_completa": ["R04"]},
        ],
    }


def _escribir_json(tmp_path, datos, nombre="caso.json"):
    return _escribir(tmp_path, nombre, json.dumps(datos))


def test_lee_un_caso_json(tmp_path):
    inst = leer_instancia(_escribir_json(tmp_path, _json_base(), "mi_caso.json"))
    assert inst.nombre == "mi_caso"
    assert inst.r == 4
    assert inst.S == [{1, 2}, {2, 3}, {4}]
    assert inst.ids_interaccion == ("E01", "E02", "E03")
    assert inst.ids_categoria == ("R01", "R02", "R03", "R04")
    assert inst.nombres_categoria[3] == "seguridad"
    assert inst.importancia == (4, 5, 2, 5)


def test_txt_sigue_sin_etiquetas(tmp_path):
    inst = leer_instancia(_escribir(tmp_path, "t.txt", "2 1\n1 2\n"))
    assert inst.ids_interaccion is None and inst.ids_categoria is None
    assert inst.etiqueta_interaccion(1) == "1" and inst.etiqueta_categoria(2) == "2"


def test_json_y_txt_equivalentes_dan_la_misma_solucion(tmp_path):
    from ruta.resolver import resolver_caso
    a = leer_instancia(_escribir_json(tmp_path, _json_base()))
    b = leer_instancia(_escribir(tmp_path, "t.txt", "4 3\n1 2\n2 3\n4\n"))
    assert resolver_caso(a).J == resolver_caso(b).J == [1, 2, 3]


def test_leer_casos_mezcla_txt_y_json(tmp_path):
    _escribir_json(tmp_path, _json_base(), "b.json")
    _escribir(tmp_path, "a.txt", "1 1\n1\n")
    assert [i.nombre for i in leer_casos(tmp_path)] == ["a", "b"]


def _con(cambio):
    datos = _json_base()
    cambio(datos)
    return datos


@pytest.mark.parametrize(
    "datos, mensaje",
    [
        (_con(lambda d: d["etapas"][0].update(riesgos_cubiertos_auditoria_completa=["R01", "R99"])),
         "categorías no definidas"),
        (_con(lambda d: d["etapas"][0].update(riesgos_cubiertos_auditoria_completa=["R01", "R01"])),
         "repetidas"),
        (_con(lambda d: d["etapas"][0].pop("riesgos_cubiertos_auditoria_completa")),
         "falta 'riesgos_cubiertos_auditoria_completa'"),
        (_con(lambda d: d["etapas"][1].update(id="E01")), "ids de etapa repetidos"),
        (_con(lambda d: d["categorias_riesgo"][1].update(id="R01")), "ids de categoría repetidos"),
        (_con(lambda d: d.pop("etapas")), "falta 'etapas'"),
        (_con(lambda d: d.pop("categorias_riesgo")), "falta 'categorias_riesgo'"),
        (_con(lambda d: d["parametros"].update(numero_etapas=5)), "'numero_etapas' dice 5 pero hay 3"),
    ],
)
def test_json_con_errores_indica_el_problema(tmp_path, datos, mensaje):
    with pytest.raises(ErrorDeLectura) as exc:
        leer_instancia(_escribir_json(tmp_path, datos))
    assert mensaje in str(exc.value)


def test_json_mal_escrito_y_no_objeto(tmp_path):
    with pytest.raises(ErrorDeLectura) as exc:
        leer_instancia(_escribir(tmp_path, "roto.json", "{ no es json"))
    assert "JSON inválido" in str(exc.value)
    with pytest.raises(ErrorDeLectura) as exc:
        leer_instancia(_escribir(tmp_path, "lista.json", "[1, 2]"))
    assert "debe ser un objeto" in str(exc.value)


def test_importancia_incompleta_se_descarta(tmp_path):
    datos = _json_base()
    del datos["categorias_riesgo"][0]["importancia"]
    assert leer_instancia(_escribir_json(tmp_path, datos)).importancia is None
