#!/usr/bin/env python3
"""Servidor local del visor: inicio, Parte 1 (aceleración, DP) y Parte 2 (auditoría, voraz).

Material de apoyo para la sustentación, en `frontend/` de la raíz (ver su
README.md). NO es parte de los entregables de la primera entrega.

Sirve una página de inicio y dos visores locales:
  /             inicio: elegir la parte que se quiere explicar
  /aceleracion  Parte 1: la tabla de la programación dinámica (Mochila 0/1)
  /auditoria    Parte 2: el algoritmo voraz de Set Cover

No duplica la lógica: llama a las mismas funciones del código base
(`leer_instancia` y `resolver_caso` de src/aceleracion/ y de src/auditoria/),
de modo que lo que muestra cada página es exactamente lo que produce el
proyecto, incluidos los errores de formato que detecta la lectura.

Solo librería estándar. Uso (desde la raíz del proyecto):

    python3 frontend/servidor.py [--puerto 8765] [--no-abrir]

Escucha únicamente en 127.0.0.1 y abre el navegador por defecto.
"""

import argparse
import json
import re
import sys
import tempfile
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from auditoria.lectura import ErrorDeLectura, leer_instancia  # noqa: E402
from auditoria.resolver import resolver_caso                   # noqa: E402
from auditoria.traza import formatear_resultado                # noqa: E402
from fuerza_bruta_demo import analizar as analizar_fuerza_bruta  # noqa: E402  (mismo directorio)
from auditoria.enfoques.comparacion.experimento import comparar_caso  # noqa: E402  (enfoques aparte del voraz base)
from aceleracion.aceleracion import ErrorDeEntrada  # noqa: E402  (Parte 1)
from aceleracion.lectura import ErrorDeLectura as ErrorDeLecturaAceleracion  # noqa: E402
from aceleracion.lectura import leer_instancia as leer_instancia_aceleracion  # noqa: E402
from aceleracion.resolver import resolver_caso as resolver_caso_aceleracion  # noqa: E402
from aceleracion.traza import formatear_caso as formatear_caso_aceleracion  # noqa: E402
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA as N_MAX_FB_ACELERACION  # noqa: E402
from aceleracion.verificacion import fuerza_bruta as fuerza_bruta_aceleracion  # noqa: E402

DIR_ESTATICO = Path(__file__).resolve().parent / "estatico"
MAX_CUERPO = 1_000_000  # 1 MB: sobra para cualquier caso razonable

# Tope de celdas de la tabla DP que se envían al navegador para dibujarla (con más, solo se envían las decisiones).
MAX_CELDAS_VISIBLES = 20_000

TIPOS_ESTATICOS = {
    "index.html": "text/html; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
    "estilos.css": "text/css; charset=utf-8",
    "inicio.html": "text/html; charset=utf-8",
    "inicio.css": "text/css; charset=utf-8",
    "aceleracion.html": "text/html; charset=utf-8",
    "aceleracion.js": "application/javascript; charset=utf-8",
    "aceleracion.css": "text/css; charset=utf-8",
}

# Páginas: ruta -> archivo estático.
PAGINAS = {
    "/": "inicio.html",
    "/aceleracion": "aceleracion.html",
    "/auditoria": "index.html",
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


def _instancia_aceleracion_a_json(inst) -> dict:
    """Serializa solo la composición del caso de la Parte 1 (sin resolverlo)."""
    return {
        "nombre": inst.nombre,
        "n": len(inst.c),
        "B": inst.B,
        "ids": list(inst.ids_etapa) if inst.ids_etapa else None,
        "t": list(inst.t),
        "c": list(inst.c),
        "d": list(inst.d),
    }


def _resultado_aceleracion_a_json(rc) -> dict:
    """Serializa un ResultadoCaso de la Parte 1 para dibujar la DP paso a paso."""
    inst = rc.instancia
    n, B, DP = rc.n, rc.B, rc.tabla
    celdas = (n + 1) * (B + 1)
    aceleradas = set(rc.aceleradas)

    # Decisiones de la reconstrucción (de la última etapa a la primera), leídas de la tabla ya calculada.
    decisiones = []
    b = B
    for i in range(n, 0, -1):
        ci, di = inst.c[i - 1], inst.d[i - 1]
        acelerada = i in aceleradas
        decisiones.append({
            "i": i, "b": b, "valor": DP[i][b], "sin": DP[i - 1][b],
            "con": di + DP[i - 1][b - ci] if ci <= b else None,
            "acelerada": acelerada, "b_despues": b - ci if acelerada else b,
        })
        if acelerada:
            b -= ci

    fb = None
    if n <= N_MAX_FB_ACELERACION:
        t0 = time.perf_counter()
        optimo = fuerza_bruta_aceleracion(inst.t, inst.c, inst.d, inst.B)["ahorro"]
        fb = {"ahorro": optimo, "subconjuntos": 2 ** n, "tiempo_s": time.perf_counter() - t0}

    return {
        **_instancia_aceleracion_a_json(inst),
        "aceleradas": list(rc.aceleradas),
        "costo": rc.costo,
        "ahorro": rc.ahorro,
        "duracion_original": rc.duracion_original,
        "duracion_final": rc.duracion_final,
        "tiempo_s": rc.tiempo_s,
        "valida": rc.valida,
        "celdas": celdas,
        "tabla": DP if celdas <= MAX_CELDAS_VISIBLES else None,
        "decisiones": decisiones,
        "fuerza_bruta": fb,
        "evidencia": formatear_caso_aceleracion(rc),
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
        ruta = self.path.split("?", 1)[0].rstrip("/") or "/"
        if ruta in PAGINAS:
            self._servir_estatico(PAGINAS[ruta])
        elif ruta.startswith("/index"):
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
        elif self.path == "/api/aceleracion/resolver":
            self._api_aceleracion(resolver=True)
        elif self.path == "/api/aceleracion/previsualizar":
            self._api_aceleracion(resolver=False)
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

    def _leer_pedido(self):
        """Lee el cuerpo {texto, nombre}. Si algo falla ya respondió el error y devuelve None."""
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
        return texto, nombre

    def _api_aceleracion(self, resolver: bool) -> None:
        """Parte 1: lee el caso con la lectura del proyecto y, si se pide, lo resuelve con la DP."""
        pedido = self._leer_pedido()
        if pedido is None:
            return
        texto, nombre = pedido
        # La lectura trabaja sobre archivos: se escribe uno temporario y se usa leer_instancia tal cual.
        directorio = Path(tempfile.gettempdir()) / "frontend_aceleracion_casos"
        directorio.mkdir(parents=True, exist_ok=True)
        camino = directorio / ("%s.json" % _nombre_seguro(nombre))
        try:
            camino.write_text(texto, encoding="utf-8")
            inst = leer_instancia_aceleracion(camino)
        except ErrorDeLecturaAceleracion as e:
            self._json(400, {"error": str(e)})
            return
        except OSError as e:
            self._json(500, {"error": "no se pudo guardar el caso: %s" % e})
            return
        finally:
            camino.unlink(missing_ok=True)
        if not resolver:
            self._json(200, _instancia_aceleracion_a_json(inst))
            return
        try:
            rc = resolver_caso_aceleracion(inst)
        except ErrorDeEntrada as e:
            self._json(400, {"error": str(e)})
            return
        self._json(200, _resultado_aceleracion_a_json(rc))

    def _cargar_instancia(self):
        """Parte 2: recibe {texto, nombre}, lo lee con `leer_instancia` y devuelve la Instancia.

        Si algo falla ya respondió el error al navegador y devuelve None.
        """
        pedido = self._leer_pedido()
        if pedido is None:
            return None
        texto, nombre = pedido

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
        description="Visor local: inicio, Parte 1 (programación dinámica) y Parte 2 (voraz), con ingreso de casos y traza paso a paso."
    )
    parser.add_argument("--puerto", type=int, default=8765, help="puerto local (por defecto 8765)")
    parser.add_argument("--no-abrir", action="store_true", help="no abrir el navegador")
    args = parser.parse_args(argv)

    servidor = ThreadingHTTPServer(("127.0.0.1", args.puerto), Visor)
    url = "http://127.0.0.1:%d" % args.puerto
    print("Visor del proyecto (inicio, Parte 1 y Parte 2) en %s  (Ctrl+C para detener)" % url)
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
