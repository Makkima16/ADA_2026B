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
