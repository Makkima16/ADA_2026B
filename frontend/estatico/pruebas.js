"use strict";

/* Sección 4 del visor del voraz: crear pruebas aleatorias. Pide al servidor las ocho combinaciones
   (mismo código que `python3 src/auditoria/enfoques/comparacion/ablacion.py`) y dibuja la tabla. */

(function () {
  const $ = (sel) => document.querySelector(sel);
  const num = (x) => Number(x).toLocaleString("es-CO");
  const dec = (x, d) => Number(x).toFixed(d).replace(".", ",");
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const NOMBRE_FAMILIA = { ralo: "Ralo", medio: "Medio", denso: "Denso" };
  let ultimo = null;

  const ids = (J) => J.map((j) => "E" + String(j).padStart(2, "0")).join(", ");

  function casoComoJson(ej) {
    const n = ej.S.length, r = ej.r;
    return JSON.stringify({
      parametros: { numero_etapas: n, numero_categorias_riesgo: r },
      categorias_riesgo: Array.from({ length: r }, (_, i) => ({ id: "R" + String(i + 1).padStart(2, "0"), categoria: "Riesgo " + (i + 1) })),
      etapas: ej.S.map((s, k) => ({ id: "E" + String(k + 1).padStart(2, "0"), riesgos_cubiertos_auditoria_completa: s.map((c) => "R" + String(c).padStart(2, "0")) })),
    });
  }

  function dibujar(d) {
    ultimo = d;
    const combos = d.combinaciones;
    const mejorLlegan = Math.max(...combos.map((c) => d.instancias - c.no_optimo));
    $("#pv-resumen").innerHTML = "<b>" + num(d.instancias) + "</b> casos (" + d.familias.map((f) => NOMBRE_FAMILIA[f].toLowerCase()).join(", ") +
      " · " + num(d.cantidad) + " por densidad · semilla " + d.semilla + "). Cada método se comparó con el mínimo real.";

    let filas = "";
    combos.forEach((c) => {
      const base = c.nombre === "Voraz base";
      const llegan = d.instancias - c.no_optimo;
      filas += "<tr" + (llegan === mejorLlegan ? ' class="fila-elegida"' : "") + "><td><b>" + esc(c.nombre === "Voraz base" ? "Voraz normal" : c.nombre) + "</b></td>" +
        '<td class="num"><b>' + num(llegan) + "</b> <small>(" + dec(llegan / d.instancias * 100, 2) + " %)</small></td>" +
        '<td class="num">' + num(c.no_optimo) + "</td>" +
        '<td class="num">' + (base ? "—" : c.mejora ? '<span class="mejor">' + num(c.mejora) + "</span>" : "0") + "</td>" +
        '<td class="num">' + (base ? "—" : num(c.igual)) + "</td>" +
        '<td class="num">' + (base ? "—" : c.peor ? '<span class="peor">' + num(c.peor) + "</span>" : "0") + "</td>" +
        '<td class="num">' + dec(c.razon_max, 2) + "</td>" +
        '<td class="num">' + num(c.viola_cota) + "</td></tr>";
    });
    $("#pv-tabla").innerHTML = "<thead><tr><th>Método</th><th class=\"num\">Llega al mínimo</th><th class=\"num\">No llega</th><th class=\"num\">Mejor que el voraz normal</th>" +
      "<th class=\"num\">Igual</th><th class=\"num\">Peor</th><th class=\"num\">Razón máxima</th><th class=\"num\">Pasa H(d)</th></tr></thead><tbody>" + filas + "</tbody>";

    let cab = "<thead><tr><th>Método</th>" + d.familias.map((f) => '<th class="num">' + NOMBRE_FAMILIA[f] + "</th>").join("") + "</tr></thead><tbody>";
    combos.forEach((c) => {
      cab += "<tr><td>" + esc(c.nombre === "Voraz base" ? "Voraz normal" : c.nombre) + "</td>" +
        d.familias.map((f) => '<td class="num">' + num(d.por_familia[f][c.nombre]) + " <small>de " + num(d.cantidad) + "</small></td>").join("") + "</tr>";
    });
    $("#pv-tabla-familias").innerHTML = cab + "</tbody>";

    const nombresConEjemplos = Object.keys(d.ejemplos);
    $("#pv-ejemplos-nota").textContent = nombresConEjemplos.length
      ? "Se muestran los casos más chicos donde cada método usó más interacciones que el voraz normal. El botón carga el caso en el visor (sección 3) para ver el paso a paso."
      : "En estos casos ningún método empeoró al voraz normal.";
    $("#pv-ejemplos").innerHTML = nombresConEjemplos.map((nombre) => {
      const c = combos.find((x) => x.nombre === nombre);
      const items = d.ejemplos[nombre].map((ej, i) =>
        "<li><span>" + ej.r + " riesgos, " + ej.S.length + " interacciones (" + NOMBRE_FAMILIA[ej.familia].toLowerCase() + "). El voraz normal usó <b>" + ej.voraz.length + "</b> (" + ids(ej.voraz) +
        "); " + esc(nombre) + " usó <b>" + ej.combinacion.length + "</b> (" + ids(ej.combinacion) + "); el mínimo es <b>" + ej.optimo.length + "</b> (" + ids(ej.optimo) + ").</span> " +
        '<button class="btn mini pv-ver" type="button" data-nombre="' + esc(nombre) + '" data-i="' + i + '">Ver en el visor</button></li>').join("");
      return "<details class=\"plegable\"><summary><b>" + esc(nombre) + "</b>: empeoró en " + num(c.peor) + (c.peor === 1 ? " caso" : " casos") + "</summary><ul class=\"lista-ejemplos\">" + items + "</ul></details>";
    }).join("");
    $("#pv-resultado").classList.remove("oculto");
  }

  function error(mensaje) {
    $("#pv-mensaje-error").textContent = mensaje;
    $("#pv-error").classList.remove("oculto");
  }

  async function correr() {
    const boton = $("#pv-correr");
    const familias = [...document.querySelectorAll(".pv-familia")].filter((c) => c.checked).map((c) => c.value);
    $("#pv-error").classList.add("oculto");
    boton.disabled = true;
    boton.textContent = "Calculando…";
    try {
      const respuesta = await fetch("/api/auditoria/experimento", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instancias: parseInt($("#pv-instancias").value, 10), semilla: parseInt($("#pv-semilla").value, 10) || 0, familias: familias }),
      });
      const datos = await respuesta.json();
      if (!respuesta.ok) error(datos.error || "Error desconocido del servidor.");
      else dibujar(datos);
    } catch (e) {
      error("No se pudo contactar el servidor local. ¿Sigue corriendo?");
    } finally {
      boton.disabled = false;
      boton.textContent = "Correr la prueba";
    }
  }

  $("#pv-correr").addEventListener("click", correr);
  $("#pv-ejemplos").addEventListener("click", (e) => {
    const b = e.target.closest(".pv-ver");
    if (!b || !ultimo) return;
    const ej = ultimo.ejemplos[b.dataset.nombre][parseInt(b.dataset.i, 10)];
    analizar(casoComoJson(ej), "ejemplo_donde_empeora", false);     // `analizar` es del visor (app.js)
  });
})();
