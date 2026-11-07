#!/usr/bin/env python3
"""Servidor local del visor: inicio, Parte 1 (aceleración, DP) y Parte 2 (auditoría, voraz).

Material de apoyo para la sustentación, en `frontend/` de la raíz (ver su
README.md). NO es parte de los entregables de la primera entrega.

Sirve una página de inicio y dos visores locales:
  /             inicio: elegir la parte que se quiere explicar
  /aceleracion  Parte 1: la tabla de la programación dinámica (Mochila 0/1)
  /auditoria    Parte 2: el algoritmo voraz de Set Cover
  /aleatorios   pruebas aleatorias: completo (genera casos en Casos/casos_temporales/ y los prueba con run_all.py), solo Parte 1 o solo Parte 2 (en memoria)

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
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from auditoria.lectura import ErrorDeLectura, leer_instancia  # noqa: E402
from auditoria.resolver import resolver_caso                   # noqa: E402
from auditoria.traza import formatear_resultado                # noqa: E402
from auditoria.lectura_ponderada import ErrorDeCostos, leer_opciones  # noqa: E402  (variante ponderada)
from auditoria.opciones import depurar, formatear_opciones      # noqa: E402
from auditoria.resolver_ponderada import resolver_caso_ponderado  # noqa: E402
from auditoria.traza_ponderada import formatear_resultado_ponderado  # noqa: E402
from fuerza_bruta_demo import analizar as analizar_fuerza_bruta  # noqa: E402  (mismo directorio)
from auditoria.enfoques.comparacion.experimento import comparar_caso  # noqa: E402  (enfoques aparte del voraz base)
from aceleracion.aceleracion import ErrorDeEntrada, MAX_CELDAS_TABLA  # noqa: E402  (Parte 1)
from aceleracion.lectura import ErrorDeLectura as ErrorDeLecturaAceleracion  # noqa: E402
from aceleracion.lectura import leer_instancia as leer_instancia_aceleracion  # noqa: E402
from aceleracion.resolver import resolver_caso as resolver_caso_aceleracion  # noqa: E402
from aceleracion.traza import formatear_caso as formatear_caso_aceleracion  # noqa: E402
from aceleracion.enfoques.dp_por_valor.resolver import resolver_caso_valor  # noqa: E402  (enfoque aparte de la DP base)
from aceleracion.enfoques.dp_por_valor.traza import formatear_caso_valor  # noqa: E402
from aceleracion.enfoques.seleccion import PRESUPUESTO, VALOR, elegir_enfoque, tamanos_de_tablas  # noqa: E402
from aceleracion.enfoques.dp_por_valor import pruebas_aleatorias as pruebas_pd  # noqa: E402  (pruebas aleatorias de la Parte 1)
from auditoria.enfoques.comparacion.ablacion import COMBINACIONES, ablacion_detalle  # noqa: E402  (pruebas aleatorias de la Parte 2)
from auditoria.enfoques.comparacion.experimento import FAMILIAS  # noqa: E402
from aceleracion.verificacion import N_MAX_FUERZA_BRUTA as N_MAX_FB_ACELERACION  # noqa: E402
from aceleracion.verificacion import fuerza_bruta as fuerza_bruta_aceleracion  # noqa: E402
from generacion_casos import carpetas as carpetas_temporales  # noqa: E402  (casos aleatorios y su prueba)
from generacion_casos import generador as generador_casos  # noqa: E402
from generacion_casos import probar as probar_casos  # noqa: E402

DIR_ESTATICO = Path(__file__).resolve().parent / "estatico"
MAX_CUERPO = 1_000_000  # 1 MB: sobra para cualquier caso razonable
MAX_CUERPO_SUBIDA = 50_000_000   # 50 MB: hasta 200 casos de la profesora subidos de una vez
MAX_INSTANCIAS_VORAZ = 5000   # por familia de densidad (3 familias x 5000 tardan unos 12 s)
EJEMPLOS_POR_COMBINACION = 3

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
    "explicacion.js": "application/javascript; charset=utf-8",
    "combinador.js": "application/javascript; charset=utf-8",
    "variante.js": "application/javascript; charset=utf-8",
    "aleatorios.html": "text/html; charset=utf-8",
    "aleatorios.js": "application/javascript; charset=utf-8",
}

# Generar y probar casos aleatorios usa las mismas dos carpetas de la raíz: de a un pedido por vez.
CANDADO_ALEATORIOS = threading.Lock()

# Páginas: ruta -> archivo estático.
PAGINAS = {
    "/": "inicio.html",
    "/aceleracion": "aceleracion.html",
    "/auditoria": "index.html",
    "/aleatorios": "aleatorios.html",
}


def abrir_navegador(url: str) -> None:
    """Abre la página sin que el navegador escriba en esta terminal.

    `webbrowser.open` deja que Chrome comparta la terminal y, si ya está abierto, imprime avisos como
    "Abriendo en una sesión existente del navegador" y errores internos de Chromium (zygote). En Linux se usa
    `xdg-open` con la salida silenciada; en otros sistemas, o si no existe, `webbrowser.open`.
    """
    abridor = shutil.which("xdg-open") if sys.platform.startswith("linux") else None
    if abridor:
        try:
            subprocess.Popen([abridor, url], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
            return
        except OSError:
            pass
    webbrowser.open(url)


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



def _version_a_json(inst, opciones) -> dict:
    """Una versión de la variante ponderada (solo completas o con parciales) lista para la página, paso a paso.

    No reimplementa nada: corre `resolver_caso_ponderado` y `depurar` del proyecto. Lo único que calcula aquí es, para
    cada paso, las candidatas (costo por categoría nueva de cada opción) para poder explicar por qué ganó la elegida.
    """
    rv = resolver_caso_ponderado(opciones.instancia, opciones.costos)
    op = opciones.instancia
    etq = op.etiqueta_interaccion
    salida = {"version": opciones.version, "n_opciones": len(opciones.costos), "factible": rv.factible,
              "sin_cubrir": sorted(rv.sin_cubrir), "opciones": [etq(k) for k in range(1, len(opciones.costos) + 1)],
              "costos": list(opciones.costos), "tipos": list(opciones.tipo), "cota": rv.cota}
    if not rv.factible:
        return salida
    dep = depurar(rv.J, opciones)
    faltan = set(range(1, inst.r + 1))
    pasos = []
    for p in rv.pasos:
        candidatas = []
        for k, s in enumerate(op.S, start=1):
            nuevas = set(s) & faltan
            if nuevas:
                candidatas.append({"opcion": etq(k), "costo": opciones.costos[k - 1], "nuevas": len(nuevas),
                                   "razon": opciones.costos[k - 1] / len(nuevas), "k": k})
        candidatas.sort(key=lambda c: (c["razon"], c["k"]))
        pasos.append({"opcion": etq(p.j), "k": p.j, "costo": p.costo, "nuevas": sorted(p.nuevas), "razon": p.costo_por_categoria,
                      "acumulado": p.acumulado, "faltan": sorted(p.faltan), "candidatas": candidatas[:5],
                      "n_candidatas": len(candidatas)})
        faltan = set(p.faltan)
    salida.update({
        "pasos": pasos, "J": [etq(k) for k in rv.J], "costo_voraz": dep.costo_voraz, "costo_real": dep.costo_real,
        "conservadas": [etq(k) for k in dep.conservadas], "descartadas": [etq(k) for k in dep.descartadas],
        "cobertura": [{"categoria": c, "opcion": etq(rv.cobertura[c])} for c in sorted(rv.cobertura)], "cubre": rv.cubre,
        "optimo_costo": rv.optimo_costo, "optimo_metodo": rv.optimo_metodo, "tiempo_s": rv.tiempo_s,
        "texto_evidencia": formatear_resultado_ponderado(rv) + formatear_opciones(rv, opciones, dep)})
    return salida


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


def _tamanos_aceleracion(inst) -> dict:
    """Celdas de cada tabla, cuál conviene y el tope de memoria (ninguna conviene si ninguna cabe)."""
    celdas = tamanos_de_tablas(inst)
    try:
        recomendado = elegir_enfoque(inst)
    except ErrorDeEntrada:
        recomendado = None
    return {"celdas_presupuesto": celdas[PRESUPUESTO], "celdas_valor": celdas[VALOR],
            "limite_celdas": MAX_CELDAS_TABLA, "recomendado": recomendado}


def _instancia_aceleracion_a_json(inst) -> dict:
    """Serializa solo la composición del caso de la Parte 1 (sin resolverlo)."""
    return {
        **_tamanos_aceleracion(inst),
        "nombre": inst.nombre,
        "n": len(inst.c),
        "B": inst.B,
        "ids": list(inst.ids_etapa) if inst.ids_etapa else None,
        "t": list(inst.t),
        "c": list(inst.c),
        "d": list(inst.d),
    }


def _decisiones_presupuesto(rc) -> list:
    """Reconstrucción de la DP base, leída de la tabla ya calculada: `b` es el presupuesto restante."""
    inst, DP = rc.instancia, rc.tabla
    aceleradas = set(rc.aceleradas)
    decisiones = []
    b = rc.B
    for i in range(rc.n, 0, -1):
        ci, di = inst.c[i - 1], inst.d[i - 1]
        acelerada = i in aceleradas
        decisiones.append({
            "i": i, "b": b, "valor": DP[i][b], "sin": DP[i - 1][b],
            "con": di + DP[i - 1][b - ci] if ci <= b else None,
            "acelerada": acelerada, "b_despues": b - ci if acelerada else b,
        })
        if acelerada:
            b -= ci
    return decisiones


def _decisiones_valor(rc) -> tuple:
    """Reconstrucción de la DP por valor: `b` es el ahorro que falta lograr. Devuelve (decisiones, tabla)
    con None donde la tabla tiene INF (= B + 1: no se puede o pasa del presupuesto)."""
    inst, C, B = rc.instancia, rc.tabla, rc.B
    fin = lambda x: None if x > B else x  # noqa: E731
    aceleradas = set(rc.aceleradas)
    decisiones = []
    v = rc.ahorro
    for i in range(rc.n, 0, -1):
        ci, di = inst.c[i - 1], inst.d[i - 1]
        acelerada = i in aceleradas
        con = fin(C[i - 1][v - di] + ci) if v >= di and C[i - 1][v - di] <= B else None
        decisiones.append({
            "i": i, "b": v, "valor": fin(C[i][v]), "sin": fin(C[i - 1][v]), "con": con,
            "acelerada": acelerada, "b_despues": v - di if acelerada else v,
        })
        if acelerada:
            v -= di
    return decisiones, [[fin(x) for x in fila] for fila in C]


def _resultado_aceleracion_a_json(rc, enfoque: str) -> dict:
    """Serializa un ResultadoCaso de la Parte 1 para dibujar la DP (por presupuesto o por valor) paso a paso."""
    inst = rc.instancia
    n, B = rc.n, rc.B
    celdas = (n + 1) * len(rc.tabla[0])
    if enfoque == VALOR:
        decisiones, tabla = _decisiones_valor(rc)
        evidencia = formatear_caso_valor(rc)
    else:
        decisiones, tabla = _decisiones_presupuesto(rc), rc.tabla
        evidencia = formatear_caso_aceleracion(rc)

    fb = None
    if n <= N_MAX_FB_ACELERACION:
        t0 = time.perf_counter()
        optimo = fuerza_bruta_aceleracion(inst.t, inst.c, inst.d, inst.B)["ahorro"]
        fb = {"ahorro": optimo, "subconjuntos": 2 ** n, "tiempo_s": time.perf_counter() - t0}

    return {
        **_instancia_aceleracion_a_json(inst),
        "enfoque": enfoque,
        "D": sum(inst.d),
        "aceleradas": list(rc.aceleradas),
        "costo": rc.costo,
        "ahorro": rc.ahorro,
        "duracion_original": rc.duracion_original,
        "duracion_final": rc.duracion_final,
        "tiempo_s": rc.tiempo_s,
        "valida": rc.valida,
        "celdas": celdas,
        "tabla": tabla if celdas <= MAX_CELDAS_VISIBLES else None,
        "decisiones": decisiones,
        "fuerza_bruta": fb,
        "evidencia": evidencia,
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
        elif ruta.startswith("/api/aleatorios/"):
            self._api_aleatorios_get(ruta)
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
        elif self.path == "/api/auditoria/variante":
            self._api_variante()
        elif self.path == "/api/aceleracion/resolver":
            self._api_aceleracion(resolver=True)
        elif self.path == "/api/aceleracion/previsualizar":
            self._api_aceleracion(resolver=False)
        elif self.path == "/api/aleatorios/solo-voraz":
            self._api_experimento_auditoria()
        elif self.path == "/api/aleatorios/solo-pd":
            self._api_experimento_aceleracion()
        elif self.path == "/api/aleatorios/generar":
            self._api_aleatorios_generar()
        elif self.path == "/api/aleatorios/subir":
            self._api_aleatorios_subir()
        elif self.path == "/api/aleatorios/probar":
            self._api_aleatorios_probar()
        else:
            self._json(404, {"error": "recurso desconocido"})

    # ---------- Casos aleatorios: generar en Casos/casos_temporales/ y probar en Resultados/resultados_temporales/ ----------

    def _estado_aleatorios(self) -> dict:
        casos, salida = carpetas_temporales.CASOS_TEMPORALES, carpetas_temporales.RESULTADOS_TEMPORALES
        return {"casos": carpetas_temporales.listar_casos(casos), "resumen": probar_casos.leer_resumen(salida),
                "comparacion": probar_casos.leer_comparacion(salida), "enfoques": probar_casos.leer_resumen_enfoques(salida),
                "limites": {"casos": generador_casos.MAX_CASOS, "voraz_por_densidad": MAX_INSTANCIAS_VORAZ,
                            "pd": pruebas_pd.MAX_INSTANCIAS}}

    def _api_aleatorios_get(self, ruta: str) -> None:
        consulta = parse_qs(urlparse(self.path).query)
        try:
            if ruta == "/api/aleatorios/estado":
                self._json(200, self._estado_aleatorios())
            elif ruta == "/api/aleatorios/caso":
                self._json(200, {"texto": carpetas_temporales.leer_texto_caso(consulta.get("nombre", [""])[0], carpetas_temporales.CASOS_TEMPORALES)})
            elif ruta == "/api/aleatorios/traza":
                self._json(200, {"texto": probar_casos.leer_traza(consulta.get("archivo", [""])[0], carpetas_temporales.RESULTADOS_TEMPORALES)})
            else:
                self._json(404, {"error": "recurso desconocido"})
        except FileNotFoundError:
            self._json(404, {"error": "ese archivo no está en las carpetas temporales (quizá se regeneraron)"})

    def _api_aleatorios_generar(self) -> None:
        """Vacía Casos/casos_temporales/ y escribe los casos nuevos (y vacía Resultados/resultados_temporales/: ya no corresponden)."""
        datos = self._leer_parametros()
        if datos is None:
            return
        try:
            lote = generador_casos.generar_lote(
                int(datos.get("cantidad", 20)), int(datos.get("semilla", 2026)),
                int(datos.get("n_min", 8)), int(datos.get("n_max", 16)),
                int(datos.get("r_min", 6)), int(datos.get("r_max", 15)),
                [str(d) for d in datos.get("densidades", list(generador_casos.DENSIDADES))])
        except generador_casos.ErrorDeParametros as e:
            self._json(400, {"error": str(e)})
            return
        except (TypeError, ValueError):
            self._json(400, {"error": "la cantidad, la semilla, n y r deben ser números enteros"})
            return
        with CANDADO_ALEATORIOS:
            carpetas_temporales.escribir_casos(lote, carpetas_temporales.CASOS_TEMPORALES)
            carpetas_temporales.vaciar(carpetas_temporales.RESULTADOS_TEMPORALES)
        self._json(200, self._estado_aleatorios())

    def _api_aleatorios_subir(self) -> None:
        """Reemplaza Casos/casos_temporales/ por los .json que sube la persona (por ejemplo, los de la profesora)."""
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            if largo > MAX_CUERPO_SUBIDA:
                self._json(413, {"error": "los archivos son demasiado grandes (máximo %d MB en total)" % (MAX_CUERPO_SUBIDA // 1_000_000)})
                return
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
            archivos = [(str(a["nombre"]), str(a["texto"])) for a in datos["archivos"]]
        except (KeyError, TypeError, ValueError, UnicodeDecodeError):
            self._json(400, {"error": "se esperaba {archivos: [{nombre, texto}, ...]}"})
            return
        with CANDADO_ALEATORIOS:
            try:
                carpetas_temporales.escribir_archivos(archivos, carpetas_temporales.CASOS_TEMPORALES)
            except carpetas_temporales.ErrorDeArchivos as e:
                self._json(400, {"error": str(e)})
                return
            carpetas_temporales.vaciar(carpetas_temporales.RESULTADOS_TEMPORALES)
        self._json(200, self._estado_aleatorios())

    def _api_aleatorios_probar(self) -> None:
        """Vacía Resultados/resultados_temporales/ y corre run_all.py sobre Casos/casos_temporales/."""
        with CANDADO_ALEATORIOS:
            try:
                proceso = probar_casos.probar(carpetas_temporales.CASOS_TEMPORALES, carpetas_temporales.RESULTADOS_TEMPORALES)
            except ValueError as e:
                self._json(400, {"error": str(e)})
                return
            except subprocess.TimeoutExpired:
                self._json(504, {"error": "la prueba tardó más de %d s y se cortó" % probar_casos.TIEMPO_MAXIMO_S})
                return
        if proceso.returncode not in (0, 1):      # 1 = algún caso dio ERROR; queda en su evidencia
            self._json(500, {"error": "run_all.py falló: %s" % (proceso.stderr.strip() or proceso.stdout.strip())})
            return
        self._json(200, self._estado_aleatorios())

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

    def _api_variante(self) -> None:
        """Variante ponderada de un caso: lee los costos con `leer_opciones` y devuelve las dos versiones paso a paso."""
        pedido = self._leer_pedido()
        if pedido is None:
            return
        texto, nombre, _ = pedido
        extension = ".json" if texto.lstrip().startswith("{") else ".txt"
        directorio = Path(tempfile.gettempdir()) / "frontend_variante_casos"
        directorio.mkdir(parents=True, exist_ok=True)
        camino = directorio / ("%s%s" % (_nombre_seguro(nombre), extension))
        try:
            camino.write_text(texto, encoding="utf-8")
            inst = leer_instancia(camino)
            opciones = leer_opciones(camino, inst)
        except (ErrorDeLectura, ErrorDeCostos) as e:
            self._json(400, {"error": str(e)})
            return
        except OSError as e:
            self._json(500, {"error": "no se pudo guardar el caso: %s" % e})
            return
        finally:
            camino.unlink(missing_ok=True)
        if opciones is None:
            self._json(200, {"sin_costos": True, "nombre": inst.nombre})
            return
        completas = _version_a_json(inst, opciones.solo_completas())
        parciales = _version_a_json(inst, opciones) if opciones.hay_parcial else None
        base = resolver_caso(inst)
        costo_p2 = sum(opciones.costos[j - 1] for j in base.J) if base.factible else None   # las completas tienen los índices 1..n
        self._json(200, {"nombre": inst.nombre, "n": len(inst.S), "r": inst.r, "sin_costos": False,
                         "ids_categoria": list(inst.ids_categoria) if inst.ids_categoria else None,
                         "nombres_categoria": list(inst.nombres_categoria) if inst.nombres_categoria else None,
                         "n_parciales": opciones.n_parciales, "completas": completas, "parciales": parciales,
                         "parte2": {"J": list(base.J), "tamano": len(base.J), "costo": costo_p2} if base.factible else None})

    def _api_previsualizar(self) -> None:
        """Solo lee el caso (sin resolverlo) para mostrar de qué se compone."""
        inst = self._cargar_instancia()
        if inst is not None:
            self._json(200, _instancia_a_json(inst))

    def _leer_parametros(self):
        """Cuerpo JSON con parámetros (para las pruebas aleatorias). Si falla ya respondió y devuelve None."""
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            if largo > MAX_CUERPO:
                self._json(413, {"error": "el pedido es demasiado grande"})
                return None
            datos = json.loads(self.rfile.read(largo).decode("utf-8"))
            if not isinstance(datos, dict):
                raise ValueError
            return datos
        except (ValueError, UnicodeDecodeError):
            self._json(400, {"error": "se esperaba un objeto JSON con los parámetros"})
            return None

    def _api_experimento_auditoria(self) -> None:
        """Solo Parte 2: pruebas aleatorias de las ocho combinaciones, en memoria (mismo código que `ablacion.py`)."""
        datos = self._leer_parametros()
        if datos is None:
            return
        try:
            cantidad, semilla = int(datos.get("instancias", 500)), int(datos.get("semilla", 2026))
            familias = [f for f in datos.get("familias", list(FAMILIAS)) if f in FAMILIAS]
        except (TypeError, ValueError):
            self._json(400, {"error": "la cantidad, la semilla y las familias deben ser números y nombres válidos"})
            return
        if not 1 <= cantidad <= MAX_INSTANCIAS_VORAZ:
            self._json(400, {"error": "la cantidad de instancias por familia debe estar entre 1 y %d" % MAX_INSTANCIAS_VORAZ})
            return
        if not familias:
            self._json(400, {"error": "elige al menos una densidad (ralo, medio o denso)"})
            return
        d = ablacion_detalle(cantidad, semilla, familias, EJEMPLOS_POR_COMBINACION)
        self._json(200, {
            "instancias": d["instancias"], "con_optimo": d["instancias"], "cantidad": cantidad, "semilla": semilla, "familias": familias,
            "combinaciones": [dict(d[nombre], nombre=nombre) for nombre, *_ in COMBINACIONES],
            "casos_por_familia": {f: cantidad for f in familias},
            "por_familia": d["por_familia"], "ejemplos": d.get("ejemplos", {}),
        })

    def _api_experimento_aceleracion(self) -> None:
        """Solo Parte 1: pruebas aleatorias de las dos tablas de la DP, en memoria (mismo código que `pruebas_aleatorias.py`)."""
        datos = self._leer_parametros()
        if datos is None:
            return
        try:
            r = pruebas_pd.experimento(
                int(datos.get("instancias", 200)), int(datos.get("semilla", 2026)),
                int(datos.get("n_min", 5)), int(datos.get("n_max", 30)),
                int(datos.get("costo_min", 1)), int(datos.get("costo_max", 30)),
                int(datos.get("ahorro_min", 1)), int(datos.get("ahorro_max", 30)),
                float(datos.get("presupuesto_pct", 50)))
        except (TypeError, ValueError) as e:      # incluye ErrorDeParametros
            self._json(400, {"error": str(e) if isinstance(e, pruebas_pd.ErrorDeParametros) else "los parámetros deben ser números"})
            return
        self._json(200, r)

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
            enfoque = pedido.get("enfoque", "auto")
            if not isinstance(texto, str) or not texto.strip():
                raise KeyError("texto")
        except (KeyError, ValueError, UnicodeDecodeError):
            self._json(400, {"error": "se esperaba JSON con el campo 'texto'"})
            return None
        return texto, nombre, enfoque

    def _api_aceleracion(self, resolver: bool) -> None:
        """Parte 1: lee el caso con la lectura del proyecto y, si se pide, lo resuelve con la DP."""
        pedido = self._leer_pedido()
        if pedido is None:
            return
        texto, nombre, enfoque = pedido
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
            if enfoque == "auto":
                enfoque = elegir_enfoque(inst)
            if enfoque not in (PRESUPUESTO, VALOR):
                self._json(400, {"error": "enfoque desconocido: %r" % (enfoque,)})
                return
            resolver = resolver_caso_valor if enfoque == VALOR else resolver_caso_aceleracion
            rc = resolver(inst)
        except ErrorDeEntrada as e:
            self._json(400, {"error": str(e)})
            return
        self._json(200, _resultado_aceleracion_a_json(rc, enfoque))

    def _cargar_instancia(self):
        """Parte 2: recibe {texto, nombre}, lo lee con `leer_instancia` y devuelve la Instancia.

        Si algo falla ya respondió el error al navegador y devuelve None.
        """
        pedido = self._leer_pedido()
        if pedido is None:
            return None
        texto, nombre, _ = pedido

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
        abrir_navegador(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
