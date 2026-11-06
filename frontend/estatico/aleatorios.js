"use strict";

/* Pruebas aleatorias. Tres modos:
   - completo: genera casos en Casos/casos_temporales/ (o se suben los propios), los prueba con run_all.py y muestra los
     resúmenes por parte que arma run_all.py (resumen_enfoques.json) y, plegado, el detalle caso por caso;
   - solo PD y solo voraz: los experimentos en memoria de siempre (pruebas_aleatorias.py y ablacion.py), sin escribir archivos.
   Los resultados de los tres modos se dibujan con las mismas funciones porque tienen la misma forma. */

(function () {
  const $ = (sel) => document.querySelector(sel);
  const num = (x) => Number(x).toLocaleString("es-CO");
  const dec = (x, d) => Number(x).toFixed(d).replace(".", ",");
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const ms = (s) => (s * 1000 < 10 ? dec(s * 1000, 3) : dec(s * 1000, 1)) + " ms";
  const plural = (n, uno, varios) => num(n) + " " + (n === 1 ? uno : varios);

  const NOMBRES = ["Voraz base", "Esenciales", "Rareza", "Parejas", "Esenciales + rareza", "Esenciales + parejas", "Rareza + parejas", "Los tres (enfoque D)"];
  const mostrar = (n) => (n === "Voraz base" ? "Voraz normal" : n);
  const FAMILIAS = { ralo: "Ralo", medio: "Medio", denso: "Denso" };
  const REGIONES = [["B menor que D", "B menor que D <small>(conviene presupuesto)</small>"],
    ["B igual a D", "B igual a D <small>(empate)</small>"], ["B mayor que D", "B mayor que D <small>(conviene valor)</small>"]];
  const ENFOQUES_P2 = [["parte2_voraz", "Voraz base"], ["parte2_esenciales", "Esenciales"], ["parte2_rareza", "Rareza"], ["parte2_parejas", "Parejas"],
    ["parte2_esenciales_rareza", "Esenciales + rareza"], ["parte2_esenciales_parejas", "Esenciales + parejas"], ["parte2_rareza_parejas", "Rareza + parejas"], ["parte2_todo", "Todo junto"]];
  const PRESETS_PD = {
    parecidos: { nmin: 5, nmax: 30, cmin: 1, cmax: 30, dmin: 1, dmax: 30, pct: 50 },
    costosgrandes: { nmin: 5, nmax: 30, cmin: 1000, cmax: 9999, dmin: 1, dmax: 9, pct: 50 },
    cruce: { nmin: 5, nmax: 30, cmin: 1, cmax: 30, dmin: 1, dmax: 30, pct: 100 },
  };
  const EXPLICACION = {
    completo: "<p><strong>Cómo funciona.</strong> Los casos se escriben como archivos <span class=\"mono\">.json</span> (el formato de la profesora) en <span class=\"mono\">Casos/casos_temporales/</span> y se prueban con <span class=\"mono\">run_all.py</span>, " +
      "que deja por cada caso su resultado, su tiempo y su traza en <span class=\"mono\">Resultados/resultados_temporales/</span>. Como cada caso deja unos 13 archivos, el máximo es de <b>500 casos</b> por corrida: " +
      "con miles de casos serían decenas de miles de archivos. Las dos carpetas se vacían y se reescriben en cada corrida, así que no se acumula nada.</p>",
    pd: "<p><strong>Por qué en memoria.</strong> Aquí los casos se generan y se miden <b>sin escribir archivos</b> (es el experimento <span class=\"mono\">pruebas_aleatorias.py</span>). Al no guardar la evidencia de cada caso se pueden correr muchos más, " +
      "y se ven los resultados agregados: cuándo conviene cada tabla de la DP, según la relación entre el presupuesto B y la suma de los ahorros D. No queda traza por caso. Máximo: <b>500 casos</b>, con corte a los 25 segundos.</p>",
    voraz: "<p><strong>Por qué en memoria.</strong> Aquí los casos se generan y se miden <b>sin escribir archivos</b> (es el experimento <span class=\"mono\">ablacion.py</span>). Por eso se pueden correr hasta <b>5.000 casos por densidad</b> " +
      "(15.000 en total; con 3.000 por densidad son 9.000). Se ven los resultados agregados y los casos más chicos donde un enfoque empeoró; no queda traza por caso. Con los dos modos juntos, en cambio, cada caso es un archivo.</p>",
  };
  let modo = "completo";
  document.getElementById("direccion").textContent = location.host || "127.0.0.1";

  // ------------------------------------------------------------------ utilidades
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

  async function con(boton, textoEspera, tarea) {
    const original = boton.textContent;
    boton.disabled = true;
    boton.textContent = textoEspera;
    error("");
    try { await tarea(); } catch (e) { error(e.message); } finally { boton.textContent = original; boton.disabled = false; actualizarBotones(); }
  }

  const stat = (clave, grande, pie, destacada) => '<div class="stat' + (destacada ? " destacada" : "") + '"><span class="clave">' + clave + '</span><span class="grande">' + grande + '</span><span class="pie">' + pie + "</span></div>";
  const statTexto = (clave, texto, pie) => '<div class="stat"><span class="clave">' + clave + '</span><span class="texto">' + texto + '</span><span class="pie">' + pie + "</span></div>";

  // ------------------------------------------------------------------ Parte 1
  function dibujarP1(r, etiquetaCasos) {
    const caja = $("#res-p1");
    if (!r || !r.hechas) { caja.classList.add("oculto"); return; }
    caja.classList.remove("oculto");
    const a = r.ambas, f = r.fuerza_bruta, rec = r.recomendado;
    const coinciden = a.corridas ? (a.coinciden === a.corridas ? "ok" : "mal") : "";
    const extra = r.solo_valor !== undefined
      ? statTexto("Se resolvieron solo por valor", num(r.solo_valor) + " de " + num(r.hechas), "la tabla por presupuesto no cabía en memoria (" + num(r.ninguna_cabe) + " no cupieron en ninguna)") : "";
    $("#p1-stats").innerHTML =
      stat("Las dos tablas dieron lo mismo", num(a.coinciden) + " <small>de " + num(a.corridas) + "</small>",
        coinciden === "ok" ? "siempre el mismo ahorro, como se espera de dos métodos exactos" : coinciden === "mal" ? "¡hay una diferencia! algo falla" : "no se corrieron las dos", true) +
      stat("Contra la fuerza bruta (12 etapas o menos)", num(f.comparadas) + " <small>casos</small>", "por presupuesto acertó " + num(f.presupuesto_ok) + " · por valor acertó " + num(f.valor_ok)) +
      statTexto("Tabla más chica", "presupuesto " + num(rec.presupuesto) + " · valor " + num(rec.valor), "empates " + num(rec.empate) + " · ninguna cabe " + num(rec.ninguna)) +
      extra +
      statTexto("No se corrieron (más de " + num(r.limite_celdas) + " celdas)", "presupuesto " + num(r.no_corridas.presupuesto) + " · valor " + num(r.no_corridas.valor), "veces en que esa tabla era demasiado grande");

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
    $("#p1-tabla").innerHTML = "<thead><tr><th>Relación</th><th class=\"num\">Casos</th><th class=\"num\">Con las dos tablas</th><th class=\"num\">Celdas (presupuesto)</th><th class=\"num\">Celdas (valor)</th>" +
      "<th class=\"num\">Tiempo (presupuesto)</th><th class=\"num\">Tiempo (valor)</th><th>La de menos celdas fue más rápida</th></tr></thead><tbody>" + filas + "</tbody>";
    $("#p1-lecturas").innerHTML = lecturas.map((t) => "<li>" + t + "</li>").join("");
  }

  // ------------------------------------------------------------------ Parte 2
  const combosDe = (d) => (d.combinaciones || NOMBRES.map((n) => Object.assign({ nombre: n }, d[n])));

  function dibujarP2(d) {
    const caja = $("#res-p2");
    if (!d || !d.instancias) { caja.classList.add("oculto"); return; }
    caja.classList.remove("oculto");
    const combos = combosDe(d);
    const base = d.con_optimo !== undefined ? d.con_optimo : d.instancias;          // casos con mínimo real (n <= 12)
    const llegan = (c) => base - c.no_optimo;
    const mejorLlegan = Math.max(...combos.map(llegan));
    const mejores = combos.filter((c) => llegan(c) === mejorLlegan).map((c) => mostrar(c.nombre));
    const normal = combos.find((c) => c.nombre === "Voraz base");
    const hayTiempo = combos.every((c) => c.tiempo_medio_s !== undefined);

    $("#p2-stats").innerHTML =
      stat("Casos factibles", num(d.instancias), base ? num(base) + " con mínimo real (fuerza bruta o subconjuntos de categorías)" : "sin mínimo real calculable: solo se compara contra el voraz normal", true) +
      (base ? stat("El voraz normal llegó al mínimo", num(llegan(normal)) + " <small>de " + num(base) + "</small>", dec(llegan(normal) / base * 100, 1) + " % de los casos") +
        statTexto("El que más veces llega al mínimo", mejores.length > 2 ? "varios (" + mejores.length + ")" : mejores.join(" y "), num(mejorLlegan) + " de " + num(base) + " casos") : "") +
      (d.fallan_cobertura !== undefined ? stat("Cobertura incompleta", num(d.fallan_cobertura), "ejecuciones que no cubrieron todas las categorías (debe ser 0)") : "");

    let filas = "";
    combos.forEach((c) => {
      const esBase = c.nombre === "Voraz base";
      filas += "<tr" + (base && llegan(c) === mejorLlegan ? ' class="fila-elegida"' : "") + "><td><b>" + esc(mostrar(c.nombre)) + "</b></td>" +
        '<td class="num">' + (base ? "<b>" + num(llegan(c)) + "</b> <small>(" + dec(llegan(c) / base * 100, 2) + " %)</small>" : "—") + "</td>" +
        '<td class="num">' + (base ? num(c.no_optimo) : "—") + "</td>" +
        '<td class="num">' + (esBase ? "—" : c.mejora ? '<span class="mejor">' + num(c.mejora) + "</span>" : "0") + "</td>" +
        '<td class="num">' + (esBase ? "—" : num(c.igual)) + "</td>" +
        '<td class="num">' + (esBase ? "—" : c.peor ? '<span class="peor">' + num(c.peor) + "</span>" : "0") + "</td>" +
        '<td class="num">' + (base ? dec(c.razon_max, 2) : "—") + "</td>" +
        '<td class="num">' + (base ? num(c.viola_cota) : "—") + "</td>" +
        (hayTiempo ? '<td class="num">' + ms(c.tiempo_medio_s) + "</td>" : "") + "</tr>";
    });
    $("#p2-tabla").innerHTML = "<thead><tr><th>Método</th><th class=\"num\">Llega al mínimo</th><th class=\"num\">No llega</th><th class=\"num\">Mejor que el voraz normal</th>" +
      "<th class=\"num\">Igual</th><th class=\"num\">Peor</th><th class=\"num\">Razón máxima</th><th class=\"num\">Pasa H(d)</th>" + (hayTiempo ? "<th class=\"num\">Tiempo medio</th>" : "") + "</tr></thead><tbody>" + filas + "</tbody>";

    const fams = Object.keys(d.por_familia).filter((f) => FAMILIAS[f]);
    let cab = "<thead><tr><th>Método</th>" + fams.map((f) => '<th class="num">' + FAMILIAS[f] + (d.casos_por_familia ? " <small>(" + num(d.casos_por_familia[f] || 0) + " casos)</small>" : "") + "</th>").join("") + "</tr></thead><tbody>";
    combos.forEach((c) => {
      cab += "<tr><td>" + esc(mostrar(c.nombre)) + "</td>" + fams.map((f) => '<td class="num">' + num(d.por_familia[f][c.nombre]) + "</td>").join("") + "</tr>";
    });
    $("#p2-familias").innerHTML = cab + "</tbody>";

    const conEjemplos = Object.keys(d.ejemplos || {});
    $("#p2-ejemplos-nota").textContent = conEjemplos.length
      ? "Los casos más chicos donde cada enfoque usó más interacciones que el voraz normal."
      : "En estos casos ningún enfoque empeoró al voraz normal.";
    const ids = (J) => J.map((j) => "E" + String(j).padStart(2, "0")).join(", ");
    $("#p2-ejemplos").innerHTML = conEjemplos.map((nombre) => {
      const c = combos.find((x) => x.nombre === nombre);
      const items = d.ejemplos[nombre].map((ej) => "<li><span>" + (ej.caso ? "<b>" + esc(ej.caso) + "</b>: " : "") + ej.r + " riesgos" + (ej.n ? ", " + ej.n + " interacciones" : ej.S ? ", " + ej.S.length + " interacciones" : "") +
        " (" + (FAMILIAS[ej.familia] || ej.familia).toLowerCase() + "). El voraz normal usó <b>" + ej.voraz.length + "</b> (" + ids(ej.voraz) + "); " + esc(mostrar(nombre)) + " usó <b>" + ej.combinacion.length + "</b> (" + ids(ej.combinacion) + ")" +
        (ej.optimo ? "; el mínimo es <b>" + ej.optimo.length + "</b> (" + ids(ej.optimo) + ")" : "") + ".</span>" +
        (ej.archivo ? ' <a href="#" class="al-ver-traza" data-archivo="' + esc(ej.archivo) + '" data-titulo="' + esc(ej.caso + " · enfoques de la Parte 2") + '">ver traza</a>' : "") + "</li>").join("");
      return '<details class="plegable"><summary><b>' + esc(mostrar(nombre)) + "</b>: empeoró en " + plural(c.peor, "caso", "casos") + '</summary><ul class="lista-ejemplos">' + items + "</ul></details>";
    }).join("");
  }

  // ------------------------------------------------------------------ variante
  function dibujarVariante(v, idCaja, idStats, contra) {
    const caja = $(idCaja);
    if (!v || !v.casos) { caja.classList.add("oculto"); return; }
    caja.classList.remove("oculto");
    $(idStats).innerHTML =
      stat("Casos", num(v.casos), v.con_parcial ? num(v.con_parcial) + " con opciones parciales; en " + num(v.con_depuracion) + " el voraz eligió la parcial y la completa de una misma interacción y se depuró" : "una sola opción por interacción", true) +
      (v.con_optimo ? stat("Llegó al mínimo real", num(v.optimo_ok) + " <small>de " + num(v.con_optimo) + "</small>", "razón máxima " + dec(v.razon_max, 2) + " · pasó de H(d): " + num(v.viola_cota))
        : statTexto("Mínimo real", "no calculado", "hay más de 12 opciones y r > 16")) +
      stat("Más barata que " + contra, num(v.mas_barata) + " <small>de " + num(v.casos) + "</small>", "ahorro medio " + dec(v.ahorro_medio_pct, 0) + " % · igual en " + num(v.igual) + " · más cara en " + num(v.mas_cara));
  }

  // ------------------------------------------------------------------ selector de caso (solo modo completo)
  let porCaso = {}, metaCaso = {}, nombresCaso = [];
  const aplica = (filas, k) => { const f = filas[k]; return f && f.resultado.indexOf("no aplica") !== 0 && f.resultado.indexOf("ERROR") !== 0 ? f : null; };
  const primero = (re, texto) => { const m = re.exec(texto || ""); return m ? m[1] : null; };
  const enlaceTraza = (f, texto) => (f ? '<a href="#" class="al-ver-traza" data-archivo="' + esc(f.traza) + '" data-titulo="' + esc(f.caso + " · " + texto) + '">' + texto + "</a>" : "");

  function fichaDe(nombre) {
    const filas = porCaso[nombre] || {}, c = metaCaso[nombre] || {};
    const p1 = aplica(filas, "parte1"), p2 = aplica(filas, "parte2"), v1 = aplica(filas, "variante1"), vp = aplica(filas, "variante1_parcial");
    const sinDatos = (k) => (filas[k] && filas[k].resultado.indexOf("no aplica") === 0 ? "el caso no trae datos de esta parte" : "sin resultado");

    // Parte 1
    let t1;
    if (p1) {
      const base = primero(/\[(solo por valor)/, p1.resultado);
      const pres = filas.parte1_presupuesto, val = filas.parte1_valor;
      t1 = stat("Parte 1 · aceleración", "ahorro " + primero(/ahorro=(\d+)/, p1.resultado),
        "duración " + primero(/duración (\d+)/, p1.resultado) + " → " + primero(/-> (\d+)/, p1.resultado) + " · costo " + primero(/costo=(\d+)/, p1.resultado) + " de B = " + esc(c.B) +
        (pres && val ? "<br>tablas: presupuesto " + num(primero(/celdas=(\d+)/, pres.resultado) || 0) + " · valor " + num(primero(/celdas=(\d+)/, val.resultado) || 0) + " celdas" : "") + (base ? "<br><b>solo por valor</b>: la de presupuesto no cabe" : ""), true);
    } else t1 = statTexto("Parte 1 · aceleración", '<span class="no-aplica">No aplica</span>', sinDatos("parte1"));

    // Parte 2
    let t2;
    if (p2) {
      const k = primero(/\((\d+) interacciones\)/, p2.resultado), opt = primero(/óptimo (\d+)/, p2.resultado), razon = primero(/razón ([0-9.]+)/, p2.resultado);
      t2 = stat("Parte 2 · voraz", k + " <small>interacciones</small>", opt ? "mínimo real " + opt + " · razón " + dec(Number(razon), 2) : "mínimo real no calculable (n > 12 y r > 16)", true);
    } else t2 = statTexto("Parte 2 · voraz", '<span class="no-aplica">No aplica</span>', sinDatos("parte2"));

    // Variante
    let t3;
    if (v1) {
      const opt = primero(/óptimo ([0-9.]+)/, v1.resultado);
      t3 = stat("Variante 1 · ponderada", "costo " + primero(/costo=([0-9.]+)/, v1.resultado),
        "solo completas" + (opt ? " · mínimo real " + opt : "") + (vp ? "<br>con parciales: costo <b>" + primero(/costo=([0-9.]+)/, vp.resultado) + "</b>" + (primero(/óptimo ([0-9.]+)/, vp.resultado) ? " · mínimo real " + primero(/óptimo ([0-9.]+)/, vp.resultado) : "") : ""), true);
    } else t3 = statTexto("Variante 1 · ponderada", '<span class="no-aplica">No aplica</span>', sinDatos("variante1"));

    // Ocho enfoques de la Parte 2
    let tabla = "";
    const enf = ENFOQUES_P2.map(([k, nombre]) => [nombre, filas[k]]).filter(([, f]) => f && /interacciones/.test(f.resultado));
    if (enf.length) {
      const tam = enf.map(([, f]) => Number(primero(/\((\d+) interacciones\)/, f.resultado)));
      const menor = Math.min(...tam);
      tabla = '<h4 class="subtitulo-pruebas">Los ocho enfoques del voraz en este caso</h4><div style="overflow-x:auto"><table class="tabla-cmp tabla-pruebas"><thead><tr><th>Enfoque</th><th class="num">Interacciones</th><th class="num">Razón al mínimo</th><th class="num">Tiempo</th></tr></thead><tbody>' +
        enf.map(([nombreEnf, f], i) => { const r = primero(/razón ([0-9.]+)/, f.resultado);
          return "<tr" + (tam[i] === menor ? ' class="fila-elegida"' : "") + "><td>" + esc(nombreEnf === "Voraz base" ? "Voraz normal" : nombreEnf) + '</td><td class="num"><b>' + tam[i] + '</b></td><td class="num">' + (r ? dec(Number(r), 2) : "—") + '</td><td class="num">' + ms(Number(f.tiempo_s)) + "</td></tr>"; }).join("") + "</tbody></table></div>";
    }

    const hrefP1 = "/aceleracion?caso=" + encodeURIComponent(nombre), hrefP2 = "/auditoria?caso=" + encodeURIComponent(nombre);
    return '<div class="ficha-cab"><h4>' + esc(nombre) + '</h4><div class="chips"><span class="chip">' + esc(c.n) + ' etapas</span><span class="chip">' + esc(c.r) + ' categorías</span><span class="chip">B = ' + esc(c.B) + "</span></div></div>" +
      '<div class="resumen">' + t1 + t2 + t3 + "</div>" + tabla +
      '<div class="ficha-acciones"><a class="btn primario" href="' + hrefP1 + '"' + (p1 ? "" : ' aria-disabled="true"') + ">Ver paso a paso en Aceleración (Parte 1) →</a>" +
      '<a class="btn primario" href="' + hrefP2 + '"' + (p2 ? "" : ' aria-disabled="true"') + ">Ver paso a paso en Auditoría (Parte 2) →</a>" +
      '<a class="btn primario" href="' + hrefP2 + '&modo=variante"' + (v1 ? "" : ' aria-disabled="true"') + ">Ver la variante ponderada paso a paso →</a></div>" +
      '<div class="ficha-enlaces"><a href="#" class="al-ver-caso" data-nombre="' + esc(nombre) + '">Ver el caso (.json)</a>' +
      [enlaceTraza(p1, "traza Parte 1"), enlaceTraza(filas.parte1_presupuesto, "las dos tablas de la DP"), enlaceTraza(p2, "traza Parte 2"), enlaceTraza(filas.parte2_voraz, "los ocho enfoques"), enlaceTraza(v1, "traza variante"), enlaceTraza(vp, "traza variante con parciales")].filter(Boolean).join(" ") + "</div>";
  }

  function mostrarFicha() {
    const nombre = $("#sel-caso").value;
    $("#ficha-caso").innerHTML = nombre ? fichaDe(nombre) : "";
    $("#ficha-caso").querySelectorAll('.btn[aria-disabled="true"]').forEach((b) => b.classList.add("desactivado"));
    const i = nombresCaso.indexOf(nombre);
    $("#caso-contador").textContent = nombresCaso.length ? (i + 1) + " de " + nombresCaso.length : "";
    $("#caso-ant").disabled = i <= 0;
    $("#caso-sig").disabled = i < 0 || i >= nombresCaso.length - 1;
    $("#al-vista-caso").classList.add("oculto");
    $("#al-vista-traza").classList.add("oculto");
  }

  function dibujarSelector(estado) {
    const filas = estado.resumen || [];
    $("#res-selector").classList.toggle("oculto", !((estado.casos || []).length && filas.length));
    $("#res-comparacion").classList.toggle("oculto", !filas.length);
    $("#al-comparacion").textContent = estado.comparacion || "";
    if (!filas.length) return;
    porCaso = {}; metaCaso = {};
    filas.forEach((f) => { (porCaso[f.caso] = porCaso[f.caso] || {})[f.parte] = f; });
    (estado.casos || []).forEach((c) => { metaCaso[c.nombre] = c; });
    nombresCaso = Object.keys(porCaso).sort();
    const antes = $("#sel-caso").value;
    $("#sel-caso").innerHTML = nombresCaso.map((n) => '<option value="' + esc(n) + '">' + esc(n) + "</option>").join("");
    if (nombresCaso.indexOf(antes) >= 0) $("#sel-caso").value = antes;
    mostrarFicha();
  }

  // ------------------------------------------------------------------ pantalla
  function mostrarResultados(subtitulo, resumen) {
    $("#panel-resultados").classList.remove("oculto");
    $("#res-subtitulo").textContent = subtitulo;
    $("#res-resumen").innerHTML = resumen;
  }

  function dibujarCompleto(estado) {
    const e = estado.enfoques || {};
    const hayResultados = (estado.resumen || []).length > 0;
    hayCasos = (estado.casos || []).length > 0;
    $("#panel-resultados").classList.toggle("oculto", !hayCasos);
    if (!hayCasos) return;
    if (!hayResultados) {
      mostrarResultados("Casos listos para probar", "<b>" + plural(estado.casos.length, "caso generado", "casos generados") + "</b> en <span class=\"mono\">Casos/casos_temporales/</span>. Pulsa «Probar los casos» para correrlos.");
      ["#res-p1", "#res-p2", "#res-var", "#res-varp"].forEach((id) => $(id).classList.add("oculto"));
    } else {
      const errores = estado.resumen.filter((f) => f.resultado.indexOf("ERROR") === 0).length;
      const sin1 = (e.sin_parte1 || []).length, sin2 = (e.sin_parte2 || []).length;
      mostrarResultados("Las dos partes y la variante, con todos los enfoques",
        "<b>" + plural(e.casos || estado.casos.length, "caso", "casos") + "</b> probados con <span class=\"mono\">run_all.py</span>" +
        (sin1 || sin2 ? " · " + (sin1 ? plural(sin1, "caso sin Parte 1", "casos sin Parte 1") : "") + (sin1 && sin2 ? " y " : "") + (sin2 ? plural(sin2, "caso sin Parte 2", "casos sin Parte 2") : "") + " (no aplica, no es un error)" : "") +
        (errores ? " · <b>" + plural(errores, "fila con ERROR", "filas con ERROR") + "</b> (ver el caso en detalle)" : "") + ".");
      dibujarP1(e.parte1);
      dibujarP2(e.parte2);
      dibujarVariante(e.variante, "#res-var", "#var-stats", "el J de la Parte 2");
      dibujarVariante(e.variante_parcial, "#res-varp", "#varp-stats", "la versión solo completas");
    }
    dibujarSelector(estado);
  }

  let hayCasos = false;
  function actualizarBotones() {
    $("#al-probar").disabled = !hayCasos;
  }

  // ------------------------------------------------------------------ eventos: modos
  function cambiarModo(nuevo) {
    modo = nuevo;
    $("#form-completo").classList.toggle("oculto", modo !== "completo");
    $("#form-pd").classList.toggle("oculto", modo !== "pd");
    $("#form-voraz").classList.toggle("oculto", modo !== "voraz");
    $("#explica-modo").innerHTML = EXPLICACION[modo];
    error("");
    $("#panel-resultados").classList.add("oculto");
    if (modo === "completo") pedir("/api/aleatorios/estado").then(dibujarCompleto).catch((e) => error(e.message));
  }
  document.querySelectorAll('input[name="modo"]').forEach((r) => r.addEventListener("change", () => cambiarModo(r.value)));

  // ------------------------------------------------------------------ eventos: modo completo
  $("#al-generar").addEventListener("click", () => {
    const densidades = Array.from(document.querySelectorAll('input[name="densidad"]:checked')).map((i) => i.value);
    if (!densidades.length) { error("Elige al menos una densidad."); return; }
    const cuerpo = {
      cantidad: Number($("#al-cantidad").value), semilla: Number($("#al-semilla").value),
      n_min: Number($("#al-nmin").value), n_max: Number($("#al-nmax").value),
      r_min: Number($("#al-rmin").value), r_max: Number($("#al-rmax").value), densidades,
    };
    con($("#al-generar"), "Generando…", async () => dibujarCompleto(await pedir("/api/aleatorios/generar", cuerpo)));
  });

  $("#al-subir").addEventListener("click", () => {
    const lista = Array.from($("#al-archivos").files || []);
    if (!lista.length) { error("Elige al menos un archivo .json."); return; }
    con($("#al-subir"), "Subiendo…", async () => {
      const archivos = [];
      for (const f of lista) archivos.push({ nombre: f.name, texto: await f.text() });
      dibujarCompleto(await pedir("/api/aleatorios/subir", { archivos }));
    });
  });

  const zona = $("#zona-subida");
  ["dragenter", "dragover"].forEach((ev) => zona.addEventListener(ev, (e) => { e.preventDefault(); zona.classList.add("arrastrando"); }));
  ["dragleave", "drop"].forEach((ev) => zona.addEventListener(ev, (e) => { e.preventDefault(); zona.classList.remove("arrastrando"); }));
  zona.addEventListener("drop", (e) => {
    const json = Array.from(e.dataTransfer.files).filter((f) => /\.json$/i.test(f.name));
    if (!json.length) { error("Arrastra archivos con extensión .json."); return; }
    const dt = new DataTransfer();
    json.forEach((f) => dt.items.add(f));
    $("#al-archivos").files = dt.files;
    $("#al-subir").click();
  });

  $("#al-probar").addEventListener("click", () => con($("#al-probar"), "Probando…", async () => dibujarCompleto(await pedir("/api/aleatorios/probar", {}))));

  document.addEventListener("click", async (ev) => {
    const caso = ev.target.closest(".al-ver-caso"), tr = ev.target.closest(".al-ver-traza");
    if (!caso && !tr) return;
    ev.preventDefault();
    try {
      if (caso) {
        const r = await pedir("/api/aleatorios/caso?nombre=" + encodeURIComponent(caso.dataset.nombre));
        $("#al-titulo-caso").textContent = caso.dataset.nombre + ".json";
        $("#al-texto-caso").textContent = r.texto;
        $("#al-vista-caso").classList.remove("oculto");
      } else {
        const r = await pedir("/api/aleatorios/traza?archivo=" + encodeURIComponent(tr.dataset.archivo));
        $("#al-titulo-traza").textContent = "Traza · " + tr.dataset.titulo;
        $("#al-texto-traza").textContent = r.texto;
        $("#al-vista-traza").classList.remove("oculto");
        $("#al-vista-traza").scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } catch (e) { error(e.message); }
  });

  // ------------------------------------------------------------------ eventos: solo PD
  function aplicarPreset(nombre) {
    const v = PRESETS_PD[nombre];
    [["nmin", "pd-nmin"], ["nmax", "pd-nmax"], ["cmin", "pd-cmin"], ["cmax", "pd-cmax"], ["dmin", "pd-dmin"], ["dmax", "pd-dmax"], ["pct", "pd-pct"]].forEach(([k, id]) => { $("#" + id).value = v[k]; });
  }
  document.querySelectorAll(".pd-preset").forEach((b) => b.addEventListener("click", () => aplicarPreset(b.dataset.preset)));

  $("#pd-correr").addEventListener("click", () => con($("#pd-correr"), "Calculando…", async () => {
    const cuerpo = { instancias: parseInt($("#pd-instancias").value, 10), semilla: parseInt($("#pd-semilla").value, 10) || 0,
      n_min: parseInt($("#pd-nmin").value, 10), n_max: parseInt($("#pd-nmax").value, 10), costo_min: parseInt($("#pd-cmin").value, 10), costo_max: parseInt($("#pd-cmax").value, 10),
      ahorro_min: parseInt($("#pd-dmin").value, 10), ahorro_max: parseInt($("#pd-dmax").value, 10), presupuesto_pct: parseFloat($("#pd-pct").value) };
    const r = await pedir("/api/aleatorios/solo-pd", cuerpo);
    const p = r.parametros;
    mostrarResultados("Solo la Parte 1, en memoria (sin archivos)",
      "<b>" + num(r.hechas) + "</b> casos al azar (semilla " + p.semilla + "): " + p.n[0] + " a " + p.n[1] + " etapas, costos de " + num(p.costo[0]) + " a " + num(p.costo[1]) +
      ", ahorros de " + num(p.ahorro[0]) + " a " + num(p.ahorro[1]) + " y B = " + dec(p.presupuesto_pct, 0) + " % del costo total." +
      (r.detenido_por_tiempo ? " <b>Se cortó por tiempo</b> antes de llegar a los " + num(p.instancias) + " pedidos." : ""));
    $("#res-p2").classList.add("oculto"); ["#res-var", "#res-varp", "#res-selector", "#res-comparacion"].forEach((id) => $(id).classList.add("oculto"));
    dibujarP1(r);
  }));

  // ------------------------------------------------------------------ eventos: solo voraz
  $("#pv-correr").addEventListener("click", () => con($("#pv-correr"), "Calculando…", async () => {
    const familias = Array.from(document.querySelectorAll(".pv-familia")).filter((c) => c.checked).map((c) => c.value);
    const d = await pedir("/api/aleatorios/solo-voraz", { instancias: parseInt($("#pv-instancias").value, 10), semilla: parseInt($("#pv-semilla").value, 10) || 0, familias });
    mostrarResultados("Solo la Parte 2, en memoria (sin archivos)",
      "<b>" + num(d.instancias) + "</b> casos (" + d.familias.map((f) => FAMILIAS[f].toLowerCase()).join(", ") + " · " + num(d.cantidad) + " por densidad · semilla " + d.semilla + "). Cada enfoque se comparó con el mínimo real.");
    $("#res-p1").classList.add("oculto"); ["#res-var", "#res-varp", "#res-selector", "#res-comparacion"].forEach((id) => $(id).classList.add("oculto"));
    dibujarP2(d);
  }));

  // ------------------------------------------------------------------ arranque: retoma lo que haya en las carpetas
  cambiarModo("completo");
  pedir("/api/aleatorios/estado").then((estado) => {
    const l = estado.limites || {};
    if (l.casos) $("#lim-completo").textContent = num(l.casos);
    if (l.pd) $("#lim-pd").textContent = num(l.pd);
    if (l.voraz_por_densidad) $("#lim-voraz").textContent = num(l.voraz_por_densidad);
    actualizarBotones();
  }).catch(() => {});
})();
