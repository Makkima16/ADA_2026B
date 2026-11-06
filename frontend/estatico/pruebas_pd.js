"use strict";

/* Sección 4 del visor de la PD: crear pruebas aleatorias. Pide al servidor el experimento
   (mismo código que `python3 src/aceleracion/enfoques/dp_por_valor/pruebas_aleatorias.py`). */

(function () {
  const $ = (sel) => document.querySelector(sel);
  const num = (x) => Number(x).toLocaleString("es-CO");
  const dec = (x, d) => Number(x).toFixed(d).replace(".", ",");
  const PRESETS = {
    parecidos: { nmin: 5, nmax: 30, cmin: 1, cmax: 30, dmin: 1, dmax: 30, pct: 50 },
    costosgrandes: { nmin: 5, nmax: 30, cmin: 1000, cmax: 9999, dmin: 1, dmax: 9, pct: 50 },
    cruce: { nmin: 5, nmax: 30, cmin: 1, cmax: 30, dmin: 1, dmax: 30, pct: 100 },
  };
  const REGIONES = [
    ["B menor que D", "B menor que D <small>(conviene presupuesto)</small>"],
    ["B igual a D", "B igual a D <small>(empate)</small>"],
    ["B mayor que D", "B mayor que D <small>(conviene valor)</small>"],
  ];
  const ms = (s) => (s * 1000 < 10 ? dec(s * 1000, 3) : dec(s * 1000, 1)) + " ms";

  function aplicar(nombre) {
    const v = PRESETS[nombre];
    [["nmin", "pd-nmin"], ["nmax", "pd-nmax"], ["cmin", "pd-cmin"], ["cmax", "pd-cmax"], ["dmin", "pd-dmin"], ["dmax", "pd-dmax"], ["pct", "pd-pct"]]
      .forEach(([k, id]) => { $("#" + id).value = v[k]; });
  }

  function dibujar(r) {
    const p = r.parametros, rec = r.recomendado, a = r.ambas, f = r.fuerza_bruta;
    $("#pd-resumen").innerHTML = "<b>" + num(r.hechas) + "</b> casos al azar (semilla " + p.semilla + "): " + p.n[0] + " a " + p.n[1] + " etapas, costos de " + num(p.costo[0]) + " a " + num(p.costo[1]) +
      ", ahorros de " + num(p.ahorro[0]) + " a " + num(p.ahorro[1]) + " y B = " + dec(p.presupuesto_pct, 0) + " % del costo total." +
      (r.detenido_por_tiempo ? " <b>Se cortó por tiempo</b> antes de llegar a los " + num(p.instancias) + " pedidos." : "");

    const coinciden = a.corridas ? (a.coinciden === a.corridas ? "ok" : "mal") : "";
    $("#pd-stats").innerHTML =
      '<div class="stat destacada"><span class="clave">Las dos tablas dieron lo mismo</span><span class="grande">' + num(a.coinciden) + " <small>de " + num(a.corridas) + '</small></span>' +
      '<span class="pie">' + (coinciden === "ok" ? "siempre el mismo ahorro, como se espera de dos métodos exactos" : coinciden === "mal" ? "¡hay una diferencia! algo falla" : "no se corrieron las dos") + "</span></div>" +
      '<div class="stat"><span class="clave">Contra la fuerza bruta (12 etapas o menos)</span><span class="grande">' + num(f.comparadas) + ' <small>casos</small></span>' +
      '<span class="pie">por presupuesto acertó ' + num(f.presupuesto_ok) + " · por valor acertó " + num(f.valor_ok) + "</span></div>" +
      '<div class="stat"><span class="clave">Tabla más chica</span><span class="texto">presupuesto ' + num(rec.presupuesto) + " · valor " + num(rec.valor) + "</span>" +
      '<span class="pie">empates ' + num(rec.empate) + " · ninguna cabe " + num(rec.ninguna) + "</span></div>" +
      '<div class="stat"><span class="clave">No se corrieron (más de ' + num(r.limite_celdas) + ' celdas)</span><span class="texto">presupuesto ' + num(r.no_corridas.presupuesto) + " · valor " + num(r.no_corridas.valor) + "</span>" +
      '<span class="pie">veces en que esa tabla era demasiado grande para la prueba</span></div>';

    let filas = "";
    const lecturas = [];
    REGIONES.forEach(([clave, etiqueta]) => {
      const g = r.regiones[clave], k = g.corridas || 1;
      const regla = g.regla_valida ? num(g.regla_mas_rapida) + " de " + num(g.regla_valida) : "—";
      filas += "<tr><td>" + etiqueta + '</td><td class="num">' + num(g.casos) + '</td><td class="num">' + num(g.corridas) + "</td>" +
        '<td class="num">' + (g.corridas ? num(Math.round(g.celdas_presupuesto / k)) : "—") + '</td><td class="num">' + (g.corridas ? num(Math.round(g.celdas_valor / k)) : "—") + "</td>" +
        '<td class="num">' + (g.corridas ? ms(g.tiempo_presupuesto / k) : "—") + '</td><td class="num">' + (g.corridas ? ms(g.tiempo_valor / k) : "—") + "</td><td>" + regla + "</td></tr>";
      if (g.corridas && g.celdas_presupuesto !== g.celdas_valor) {
        const menos = g.celdas_presupuesto < g.celdas_valor ? ["presupuesto", g.celdas_valor / g.celdas_presupuesto] : ["valor", g.celdas_presupuesto / g.celdas_valor];
        const tmenos = g.tiempo_presupuesto < g.tiempo_valor ? ["presupuesto", g.tiempo_valor / g.tiempo_presupuesto] : ["valor", g.tiempo_presupuesto / g.tiempo_valor];
        lecturas.push("<b>" + clave + ":</b> la tabla por " + menos[0] + " tuvo en promedio <b>" + dec(menos[1], menos[1] < 10 ? 1 : 0) + " veces menos celdas</b> y la de " + tmenos[0] +
          " fue en promedio " + dec(tmenos[1], tmenos[1] < 10 ? 1 : 0) + " veces más rápida.");
      }
    });
    $("#pd-tabla").innerHTML = "<thead><tr><th>Relación</th><th class=\"num\">Casos</th><th class=\"num\">Con las dos tablas</th><th class=\"num\">Celdas (presupuesto)</th><th class=\"num\">Celdas (valor)</th>" +
      "<th class=\"num\">Tiempo (presupuesto)</th><th class=\"num\">Tiempo (valor)</th><th>La de menos celdas fue más rápida</th></tr></thead><tbody>" + filas + "</tbody>";
    $("#pd-lecturas").innerHTML = lecturas.map((t) => "<li>" + t + "</li>").join("");
    $("#pd-resultado").classList.remove("oculto");
  }

  function error(mensaje) {
    $("#pd-mensaje-error").textContent = mensaje;
    $("#pd-error").classList.remove("oculto");
  }

  async function correr() {
    const boton = $("#pd-correr");
    const entero = (id) => parseInt($("#" + id).value, 10);
    $("#pd-error").classList.add("oculto");
    boton.disabled = true;
    boton.textContent = "Calculando…";
    try {
      const respuesta = await fetch("/api/aceleracion/experimento", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instancias: entero("pd-instancias"), semilla: entero("pd-semilla") || 0, n_min: entero("pd-nmin"), n_max: entero("pd-nmax"),
          costo_min: entero("pd-cmin"), costo_max: entero("pd-cmax"), ahorro_min: entero("pd-dmin"), ahorro_max: entero("pd-dmax"),
          presupuesto_pct: parseFloat($("#pd-pct").value),
        }),
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

  $("#pd-correr").addEventListener("click", correr);
  document.querySelectorAll(".pd-preset").forEach((b) => b.addEventListener("click", () => aplicar(b.dataset.preset)));
})();
