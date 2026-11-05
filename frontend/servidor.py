#!/usr/bin/env python3
"""Servidor local del visor del voraz (Parte 2, auditoría).

Material de apoyo para la sustentación, en `frontend/` de la raíz (ver su
README.md). NO es parte de los entregables de la primera entrega.

Sirve una página local para crear casos de la Parte 2 —con un formulario o
como texto en el formato provisional de src/ruta/lectura.py— y ver, paso a
paso, cómo opera el algoritmo voraz. No duplica la lógica: llama a las mismas
funciones del código base (`leer_instancia` y `resolver_caso`), de modo que
lo que muestra la página es exactamente lo que produce el proyecto, incluidos
los errores de formato que detecta la lectura.

Solo librería estándar. Uso (desde la raíz del proyecto):

    python3 frontend/servidor.py [--puerto 8765] [--no-abrir]

Escucha únicamente en 127.0.0.1 y abre el navegador por defecto.
"""

import argparse
import json
import re
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from ruta.lectura import ErrorDeLectura, leer_instancia  # noqa: E402
from ruta.resolver import resolver_caso                   # noqa: E402
from ruta.traza import formatear_resultado                # noqa: E402
from fuerza_bruta_demo import analizar as analizar_fuerza_bruta  # noqa: E402  (mismo directorio)
from enfoques.comparacion.experimento import comparar_caso  # noqa: E402  (enfoques aparte del voraz base)

DIR_ESTATICO = Path(__file__).resolve().parent / "estatico"
MAX_CUERPO = 1_000_000  # 1 MB: sobra para cualquier caso razonable

TIPOS_ESTATICOS = {
    "index.html": "text/html; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
    "estilos.css": "text/css; charset=utf-8",
}


def _nombre_seguro(nombre: str) -> str:
    """Nombre de caso saneado (solo letras, dígitos, '-' y '_')."""
    limpio = re.sub(r"[^A-Za-z0-9_-]", "_", (nombre or "").strip())[:60]
    return limpio or "caso"


def _resultado_a_json(res, inst) -> dict:
    """Serializa un ResultadoCaso (más la instancia) para la página."""
    return {
        "nombre": res.nombre,
        "n": res.n,
        "r": res.r,
        "factible": res.factible,
        "sin_cubrir": sorted(res.sin_cubrir),
        "J": list(res.J),
        "pasos": [
            {"j": p.j, "nuevas": sorted(p.nuevas), "faltan": sorted(p.faltan)}
            for p in res.pasos
        ],
        "cobertura": [
            {"categoria": c, "interaccion": res.cobertura[c]}
            for c in sorted(res.cobertura)
        ],
        "cubre": res.cubre,
        "tiempo_s": res.tiempo_s,
        "cota": res.cota,
        "optimo": list(res.optimo) if res.optimo is not None else None,
        "fuerza_bruta": analizar_fuerza_bruta(inst),
        "comparacion": _comparacion_a_json(inst) if res.factible else None,
        "S": [sorted(s) for s in inst.S],
        # Nombres opcionales (solo si el archivo es JSON); la página usa los números si son None.
        "ids_interaccion": list(inst.ids_interaccion) if inst.ids_interaccion else None,
        "ids_categoria": list(inst.ids_categoria) if inst.ids_categoria else None,
        "nombres_categoria": list(inst.nombres_categoria) if inst.nombres_categoria else None,
        "texto_evidencia": formatear_resultado(res),
    }


def _comparacion_a_json(inst) -> dict:
    """Voraz normal y enfoques (esenciales, parejas, ambas, rareza) sobre el mismo caso, el óptimo exacto y,
    para mostrar el recorrido, el detalle de cada paso (candidatas y pareja ganadora)."""
    cmp = comparar_caso(inst.r, inst.S)
    S = inst.S
    cuenta = {}
    for s in S:
        for c in s:
            cuenta[c] = cuenta.get(c, 0) + 1
    metodos = {}
    for nombre, m in cmp["metodos"].items():
        faltan_antes = set(range(1, inst.r + 1))
        pasos = []
        for p in m["pasos"]:
            paso = {"j": p.j, "nuevas": sorted(p.nuevas), "faltan": sorted(p.faltan),
                    # categorías nuevas que habría cubierto cada interacción (1..n) antes de este paso
                    "candidatos": [len(set(s) & faltan_antes) for s in S]}
            if hasattr(p, "puntajes"):                 # pasos de rareza: puntaje de cada interacción
                paso["puntajes"] = list(p.puntajes)
            if hasattr(p, "puntaje_par"):              # pasos del combinado: puntaje de rareza del par
                paso["puntaje_par"] = p.puntaje_par
            if hasattr(p, "par"):                      # pasos de parejas: qué par ganó y cuánto cubre junto
                paso["par"] = list(p.par)
                paso["cobertura_par"] = p.cobertura_par
            pasos.append(paso)
            faltan_antes = set(p.faltan)
        esenciales = m["esenciales"]
        metodos[nombre] = {
            "J": list(m["J"]),
            "pasos": pasos,
            "esenciales": esenciales,
            # por cada esencial, las categorías que SOLO ella cubre (la razón de ser esencial)
            "unicas": ({str(j): [c for c in sorted(S[j - 1]) if cuenta[c] == 1] for j in esenciales}
                       if esenciales is not None else None),
            "tiempo_s": m["tiempo_s"],
        }
    return {"metodos": metodos,
            "optimo": cmp["optimo"],
            "tiempo_optimo_s": cmp["tiempo_optimo_s"],
            "cota_inferior": cmp["cota_inferior"]}


def _instancia_a_json(inst) -> dict:
    """Serializa solo la composición del caso (sin resolverlo)."""
    return {
        "nombre": inst.nombre,
        "n": len(inst.S),
        "r": inst.r,
        "S": [sorted(s) for s in inst.S],
        "ids_interaccion": list(inst.ids_interaccion) if inst.ids_interaccion else None,
        "ids_categoria": list(inst.ids_categoria) if inst.ids_categoria else None,
        "nombres_categoria": list(inst.nombres_categoria) if inst.nombres_categoria else None,
        "importancia": list(inst.importancia) if inst.importancia else None,
    }


class Visor(BaseHTTPRequestHandler):
    """Página estática + un endpoint JSON; todo en 127.0.0.1."""

    def _responder(self, codigo: int, contenido: bytes, tipo: str) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenido)

    def _json(self, codigo: int, dato) -> None:
        cuerpo = json.dumps(dato, ensure_ascii=False).encode("utf-8")
        self._responder(codigo, cuerpo, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 (nombre que impone http.server)
        if self.path == "/" or self.path.startswith("/index"):
            self._servir_estatico("index.html")
        elif self.path.startswith("/estatico/"):
            nombre = self.path[len("/estatico/"):]
            if nombre in TIPOS_ESTATICOS:
                self._servir_estatico(nombre)
            else:
                self._json(404, {"error": "recurso desconocido"})
        else:
            self._json(404, {"error": "recurso desconocido"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/resolver":
            self._api_resolver()
        elif self.path == "/api/previsualizar":
            self._api_previsualizar()
        else:
            self._json(404, {"error": "recurso desconocido"})

    def _servir_estatico(self, nombre: str) -> None:
        try:
            contenido = (DIR_ESTATICO / nombre).read_bytes()
        except OSError:
            self._json(404, {"error": "falta %s" % nombre})
            return
        self._responder(200, contenido, TIPOS_ESTATICOS[nombre])

    def _api_resolver(self) -> None:
        """Lee el texto del caso con la MISMA lectura del proyecto y resuelve."""
        inst = self._cargar_instancia()
        if inst is None:
            return
        res = resolver_caso(inst)
        self._json(200, _resultado_a_json(res, inst))

    def _api_previsualizar(self) -> None:
        """Solo lee el caso (sin resolverlo) para mostrar de qué se compone."""
        inst = self._cargar_instancia()
        if inst is not None:
            self._json(200, _instancia_a_json(inst))

    def _cargar_instancia(self):
        """Recibe {texto, nombre}, lo lee con `leer_instancia` y devuelve la Instancia.

        Si algo falla ya respondió el error al navegador y devuelve None.
        """
        try:
            largo = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "cabecera Content-Length inválida"})
            return None
        if largo > MAX_CUERPO:
            self._json(413, {"error": "el caso enviado es demasiado grande"})
            return None
        try:
            pedido = json.loads(self.rfile.read(largo).decode("utf-8"))
            texto = pedido["texto"]
            nombre = pedido.get("nombre", "caso")
            if not isinstance(texto, str) or not texto.strip():
                raise KeyError("texto")
        except (KeyError, ValueError, UnicodeDecodeError):
            self._json(400, {"error": "se esperaba JSON con el campo 'texto'"})
            return None

        # La lectura del proyecto trabaja sobre archivos: se escribe uno
        # temporario con el texto recibido y se usa leer_instancia tal cual.
        # La extensión decide el lector: si el texto empieza con '{' es JSON.
        extension = ".json" if texto.lstrip().startswith("{") else ".txt"
        directorio = Path(tempfile.gettempdir()) / "frontend_voraz_casos"
        directorio.mkdir(parents=True, exist_ok=True)
        camino = directorio / ("%s%s" % (_nombre_seguro(nombre), extension))
        try:
            camino.write_text(texto, encoding="utf-8")
            inst = leer_instancia(camino)
        except ErrorDeLectura as e:
            self._json(400, {"error": str(e)})
            return None
        except OSError as e:
            self._json(500, {"error": "no se pudo guardar el caso: %s" % e})
            return None
        finally:
            camino.unlink(missing_ok=True)
        return inst

    def log_message(self, formato, *args) -> None:
        """Consola limpia: solo errores de transporte, no cada request."""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Visor local del voraz (Parte 2): ingreso de casos y traza paso a paso."
    )
    parser.add_argument("--puerto", type=int, default=8765, help="puerto local (por defecto 8765)")
    parser.add_argument("--no-abrir", action="store_true", help="no abrir el navegador")
    args = parser.parse_args(argv)

    servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Visor)
    url = "http://127.0.0.1:%d" % args.puerto
    print("Visor del voraz (Parte 2) en %s  (Ctrl+C para detener)" % url)
    if not args.no_abrir:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
