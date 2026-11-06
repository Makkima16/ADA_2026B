"use strict";

/* Casos aleatorios: genera en Casos/casos_temporales/ y prueba en Resultados/resultados_temporales/ (mismo código que
   `python3 probar_aleatorios.py`). La página solo muestra lo que devuelve el servidor. */

(function () {
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const PARTES = [["parte1", "Parte 1 · DP"], ["parte2", "Parte 2 · voraz"], ["variante1", "Variante 1 · ponderada"]];
  document.getElementById("direccion").textContent = location.host || "127.0.0.1";

  function error(texto) {
    $("#al-mensaje-error").textContent = texto || "";
    $("#al-error").classList.toggle("oculto", !texto);
  }

  async function pedir(url, cuerpo) {
    const opciones = cuerpo === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) };
    const respuesta = await fetch(url, opciones);
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error || "error del servidor");
    return datos;
  }

  function dibujarCasos(casos) {
    $("#al-resumen-casos").textContent = casos.length
      ? casos.length + " casos en Casos/casos_temporales/. Pulsa el nombre de uno para ver su contenido."
      : "Todavía no hay casos: genera primero.";
    $("#al-probar").disabled = !casos.length;
    $("#al-tabla-casos").innerHTML = casos.length
      ? "<thead><tr><th>Caso</th><th class=\"num\">n</th><th class=\"num\">r</th><th class=\"num\">B</th></tr></thead><tbody>" +
        casos.map((c) => '<tr><td><a href="#" class="al-ver-caso" data-nombre="' + esc(c.nombre) + '">' + esc(c.nombre) + '</a></td><td class="num">' + esc(c.n) +
          '</td><td class="num">' + esc(c.r) + '</td><td class="num">' + esc(c.B) + "</td></tr>").join("") + "</tbody>"
      : "";
    $("#al-vista-caso").classList.add("oculto");
  }

  function dibujarResultados(filas, comparacion) {
    $("#al-panel-resultados").classList.toggle("oculto", !filas.length);
    if (!filas.length) return;
    const porCaso = {};
    filas.forEach((f) => { (porCaso[f.caso] = porCaso[f.caso] || {})[f.parte] = f; });
    const celda = (f) => f
      ? esc(f.resultado) + (f.tiempo_s ? ' <small>(' + (Number(f.tiempo_s) * 1000).toFixed(3).replace(".", ",") + " ms)</small>" : "") +
        ' <a href="#" class="al-ver-traza" data-archivo="' + esc(f.traza) + '" data-titulo="' + esc(f.caso + " · " + f.parte) + '">traza</a>'
      : "—";
    $("#al-tabla-resultados").innerHTML = "<thead><tr><th>Caso</th>" + PARTES.map((p) => "<th>" + p[1] + "</th>").join("") + "</tr></thead><tbody>" +
      Object.keys(porCaso).sort().map((caso) => "<tr><td>" + esc(caso) + "</td>" + PARTES.map((p) => "<td>" + celda(porCaso[caso][p[0]]) + "</td>").join("") + "</tr>").join("") + "</tbody>";
    $("#al-comparacion").textContent = comparacion;
    $("#al-vista-traza").classList.add("oculto");
  }

  function dibujar(estado) {
    dibujarCasos(estado.casos);
    dibujarResultados(estado.resumen, estado.comparacion);
  }

  async function trabajar(boton, textoEspera, tarea) {
    const original = boton.textContent;
    boton.disabled = true;
    boton.textContent = textoEspera;
    error("");
    try { dibujar(await tarea()); } catch (e) { error(e.message); } finally { boton.textContent = original; boton.disabled = !$("#al-tabla-casos").innerHTML; }
  }

  $("#al-generar").addEventListener("click", () => {
    const densidades = Array.from(document.querySelectorAll('input[name="densidad"]:checked')).map((i) => i.value);
    const cuerpo = {
      cantidad: Number($("#al-cantidad").value), semilla: Number($("#al-semilla").value),
      n_min: Number($("#al-nmin").value), n_max: Number($("#al-nmax").value),
      r_min: Number($("#al-rmin").value), r_max: Number($("#al-rmax").value), densidades,
    };
    if (!densidades.length) { error("Elige al menos una densidad."); return; }
    trabajar($("#al-generar"), "Generando…", () => pedir("/api/aleatorios/generar", cuerpo)).then(() => { $("#al-generar").disabled = false; });
  });

  $("#al-probar").addEventListener("click", () => trabajar($("#al-probar"), "Probando…", () => pedir("/api/aleatorios/probar", {})));

  document.addEventListener("click", async (ev) => {
    const caso = ev.target.closest(".al-ver-caso"), traza = ev.target.closest(".al-ver-traza");
    if (!caso && !traza) return;
    ev.preventDefault();
    try {
      if (caso) {
        const r = await pedir("/api/aleatorios/caso?nombre=" + encodeURIComponent(caso.dataset.nombre));
        $("#al-titulo-caso").textContent = caso.dataset.nombre + ".json";
        $("#al-texto-caso").textContent = r.texto;
        $("#al-vista-caso").classList.remove("oculto");
      } else {
        const r = await pedir("/api/aleatorios/traza?archivo=" + encodeURIComponent(traza.dataset.archivo));
        $("#al-titulo-traza").textContent = "Traza · " + traza.dataset.titulo;
        $("#al-texto-traza").textContent = r.texto;
        $("#al-vista-traza").classList.remove("oculto");
      }
    } catch (e) { error(e.message); }
  });

  pedir("/api/aleatorios/estado").then(dibujar).catch((e) => error(e.message));   // retoma lo que haya en las carpetas
})();
