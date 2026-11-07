"use strict";

/* Variante ponderada en /auditoria: cada interacción tiene un costo y el voraz elige, en cada paso, la opción que sale más
   barata por riesgo nuevo. La página no calcula nada: pide al servidor (POST /api/auditoria/variante) lo que dan las funciones
   del proyecto (`leer_opciones`, `resolver_caso_ponderado`, `depurar`) y lo muestra paso a paso.
   Funciona con app.js: este usa `estado.caso` (el último caso analizado) y llama a `window.alAnalizar()` al terminar. */

(function () {
  const $ = (sel) => document.querySelector(sel);
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const num = (x) => Number(x).toLocaleString("es-CO", { maximumFractionDigits: 2 });
  const dec = (x, d) => Number(x).toFixed(d).replace(".", ",");
  const plural = (n, uno, varios) => num(n) + " " + (n === 1 ? uno : varios);

  const S = { vista: "voraz", datos: null, version: "completas", pos: 0, temporizador: null, pedido: 0 };
  const params = new URLSearchParams(location.search);
  let vistaInicial = params.get("modo") === "variante" ? "variante" : null;       // desde /aleatorios: «ver la variante paso a paso»

  const cat = (c) => esc(S.datos && S.datos.ids_categoria ? S.datos.ids_categoria[c - 1] : c);
  const v = () => (S.datos ? (S.version === "parciales" && S.datos.parciales ? S.datos.parciales : S.datos.completas) : null);

  // ------------------------------------------------------------------ vista: voraz normal o variante
  function activarVista(nombre) {
    S.vista = nombre;
    document.querySelectorAll("#vista-selector .btn-voraz").forEach((b) => b.classList.toggle("activo", b.dataset.vista === nombre));
    $("#panel-resultado").classList.toggle("oculto", nombre !== "voraz");
    $("#panel-variante").classList.toggle("oculto", nombre !== "variante");
    if (nombre !== "variante") detener();
    if (nombre === "variante") { cargar(); $("#panel-variante").scrollIntoView({ behavior: "smooth", block: "start" }); }
  }
  window.vistaVariante = () => S.vista === "variante";
  document.querySelectorAll("#vista-selector .btn-voraz").forEach((b) => b.addEventListener("click", () => activarVista(b.dataset.vista)));

  // ------------------------------------------------------------------ carga desde el servidor
  window.alAnalizar = function () {
    S.datos = null;
    detener();
    if (vistaInicial) { const quiere = vistaInicial; vistaInicial = null; activarVista(quiere); return; }
    if (S.vista === "variante") cargar();
  };

  async function cargar() {
    if (typeof estado === "undefined" || !estado.caso) { mostrarVacio(); return; }
    if (S.datos && S.datos.nombre !== undefined && S.datos.__texto === estado.caso.texto) { dibujar(); return; }
    const mio = ++S.pedido;
    let ok, datos;
    try {
      const r = await fetch("/api/auditoria/variante", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ texto: estado.caso.texto, nombre: estado.caso.nombre }) });
      ok = r.ok; datos = await r.json();
    } catch (e) { ok = false; datos = { error: "No se pudo contactar el servidor local. ¿Sigue corriendo?" }; }
    if (mio !== S.pedido) return;                                                   // llegó tarde: ya se pidió otro caso
    if (!ok) { mostrarVacio(datos.error || "Error desconocido del servidor."); return; }
    datos.__texto = estado.caso.texto;
    S.datos = datos;
    S.version = "completas";
    S.pos = 0;
    dibujar();
  }

  function mostrarVacio(mensaje) {
    ["#var-sin-costos", "#var-no-factible", "#var-salida"].forEach((id) => $(id).classList.add("oculto"));
    $("#var-vacio").classList.remove("oculto");
    $("#var-vacio").querySelector(".vacio-texto").innerHTML = mensaje ? esc(mensaje) : "Carga un caso arriba y pulsa <strong>Analizar</strong>. Aquí verás la variante con costos, paso a paso.";
  }

  // ------------------------------------------------------------------ dibujo
  function dibujar() {
    const d = S.datos;
    $("#var-vacio").classList.add("oculto");
    $("#var-sin-costos").classList.toggle("oculto", !d.sin_costos);
    if (d.sin_costos) { ["#var-no-factible", "#var-salida"].forEach((id) => $(id).classList.add("oculto")); return; }
    const x = v();
    $("#var-no-factible").classList.toggle("oculto", x.factible);
    $("#var-salida").classList.toggle("oculto", !x.factible);
    if (!x.factible) {
      $("#var-texto-no-factible").innerHTML = "<p>Ninguna interacción revisa estos riesgos, así que es imposible cubrirlos todos: " + x.sin_cubrir.map((c) => '<span class="chip rojo">' + cat(c) + "</span>").join(" ") + "</p>";
      return;
    }
    // interruptor de versión
    document.querySelectorAll("#var-versiones [data-version]").forEach((b) => b.classList.toggle("activo", b.dataset.version === S.version));
    $("#btn-parciales").disabled = !d.parciales;
    $("#var-nota-version").innerHTML = S.version === "parciales"
      ? "<b>Con parciales (extensión):</b> cada variación de auditoría es una opción con su costo (" + plural(x.n_opciones, "opción", "opciones") + "). El voraz es el mismo; solo tiene más opciones para elegir."
      : "<b>Solo completas (versión principal):</b> un costo por interacción, la definición de la variante." +
        (d.parciales ? "" : " Este caso no trae variaciones parciales, así que no hay otra versión.");
    tarjetas(x);
    $("#var-slider").max = x.pasos.length;
    $("#var-evidencia").textContent = x.texto_evidencia;
    fijar(Math.min(S.pos, x.pasos.length));
  }

  function tarjetas(x) {
    const d = S.datos;
    const stat = (clave, grande, pie, destacada) => '<div class="stat' + (destacada ? " destacada" : "") + '"><span class="clave">' + clave + '</span><span class="grande">' + grande + '</span><span class="pie">' + pie + "</span></div>";
    const statTexto = (clave, texto, pie) => '<div class="stat"><span class="clave">' + clave + '</span><span class="texto">' + texto + '</span><span class="pie">' + pie + "</span></div>";
    const razon = x.optimo_costo ? x.costo_real / x.optimo_costo : null;
    let t = stat("Costo total a pagar", num(x.costo_real), "auditando " + x.conservadas.map(esc).join(", "), true);
    t += x.optimo_costo !== null && x.optimo_costo !== undefined
      ? statTexto("Mínimo real", num(x.optimo_costo), "por " + esc(x.optimo_metodo) + " · el voraz pagó " + dec(razon, 2) + " veces el mínimo")
      : statTexto("Mínimo real", "no calculado", "hay más de 12 opciones y más de 16 riesgos");
    t += statTexto("Garantía teórica", "H(d) ≈ " + dec(x.cota, 2), "nunca paga más de " + dec(x.cota, 2) + " veces el mínimo (Chvátal, 1979)");
    if (d.parte2) {
      t += statTexto("Contra el voraz normal (Parte 2)", num(d.parte2.costo) + " <small>" + (d.parte2.costo > x.costo_real ? "→ " + num(x.costo_real) : "") + "</small>",
        "el conjunto del voraz normal (" + d.parte2.tamano + " interacciones) costaría " + num(d.parte2.costo) + " con estos costos");
    }
    if (S.version === "parciales" && d.completas.factible) {
      const dif = d.completas.costo_real - x.costo_real;
      t += stat("Contra solo completas", dif > 0 ? "−" + num(dif) : (dif < 0 ? "+" + num(-dif) : "igual"), "solo completas paga " + num(d.completas.costo_real) + (x.descartadas.length ? " · se depuró " + x.descartadas.map(esc).join(", ") + " (parcial y completa de la misma interacción)" : ""));
    }
    $("#var-tarjetas").innerHTML = t;
  }

  function fijar(pos) {
    const x = v();
    S.pos = Math.max(0, Math.min(pos, x.pasos.length));
    $("#var-slider").value = S.pos;
    $("#var-contador").textContent = S.pos === 0 ? "Antes de empezar" : "Paso " + S.pos + " de " + x.pasos.length;
    $("#var-ant").disabled = S.pos === 0;
    $("#var-sig").disabled = S.pos === x.pasos.length;

    // chips de riesgos: cubiertos hasta el paso anterior, nuevos en este paso, pendientes
    const r = S.datos.r, cubiertos = new Set(), nuevos = new Set((S.pos > 0 ? x.pasos[S.pos - 1].nuevas : []));
    for (let i = 0; i < S.pos - 1; i++) x.pasos[i].nuevas.forEach((c) => cubiertos.add(c));
    let chips = "";
    for (let c = 1; c <= r; c++) {
      chips += '<span class="celda ' + (nuevos.has(c) ? "c-nuevo" : cubiertos.has(c) ? "c-cubierto" : "c-pendiente") + '" title="' + cat(c) + '">' + cat(c) + "</span>";
    }
    $("#var-categorias").innerHTML = chips;

    // explicación del paso actual
    if (S.pos === 0) {
      $("#var-paso").innerHTML = '<div class="paso-var"><h4>Antes de empezar</h4><p>Hay ' + plural(r, "riesgo", "riesgos") + " por cubrir y " + plural(x.n_opciones, "opción", "opciones") +
        " para auditar, cada una con su costo. Pulsa <b>›</b> o <b>Reproducir</b> para ver qué elige el voraz en cada paso.</p></div>";
    } else {
      const p = x.pasos[S.pos - 1];
      const mejores = p.candidatas.map((c, i) => "<tr" + (i === 0 ? ' class="fila-elegida"' : "") + "><td>" + esc(c.opcion) + '</td><td class="num">' + num(c.costo) + '</td><td class="num">' + c.nuevas + '</td><td class="num"><b>' + dec(c.razon, 2) + "</b></td></tr>").join("");
      $("#var-paso").innerHTML = '<div class="paso-var"><h4>Paso ' + S.pos + ": elige " + esc(p.opcion) + "</h4>" +
        "<p>Cuesta <b>" + num(p.costo) + "</b> y cubre <b>" + plural(p.nuevas.length, "riesgo nuevo", "riesgos nuevos") + " (" + p.nuevas.map(cat).join(", ") + ")</b>: <b>" + dec(p.razon, 2) + "</b> por riesgo nuevo, la más barata de las " + p.n_candidatas + " opciones que todavía aportan." +
        " Llevas gastado <b>" + num(p.acumulado) + "</b>" + (p.faltan.length ? " y faltan " + plural(p.faltan.length, "riesgo", "riesgos") + "." : " y ya no falta ningún riesgo.") + "</p>" +
        '<div style="overflow-x:auto"><table class="tabla-cmp tabla-pruebas"><thead><tr><th>Mejores opciones en este paso</th><th class="num">Costo</th><th class="num">Riesgos nuevos</th><th class="num">Costo por riesgo nuevo</th></tr></thead><tbody>' + mejores + "</tbody></table></div></div>";
    }
    $("#var-lista").innerHTML = S.pos ? '<ul class="lista-pasos-var">' + x.pasos.slice(0, S.pos).map((p, i) =>
      '<li class="' + (i === S.pos - 1 ? "actual" : "") + '">Paso ' + (i + 1) + ": " + esc(p.opcion) + " · costo " + num(p.costo) + " · " + dec(p.razon, 2) + " por riesgo nuevo · acumulado " + num(p.acumulado) + "</li>").join("") + "</ul>" : "";

    // cobertura final al terminar
    const fin = S.pos === x.pasos.length;
    $("#var-cobertura-final").classList.toggle("oculto", !fin);
    if (fin) {
      $("#var-tabla-cobertura").innerHTML = x.cobertura.map((f) => '<span class="par-cobertura"><span class="r">' + cat(f.categoria) + '</span><span class="f">→</span><span class="e">' + esc(f.opcion) + "</span></span>").join("");
    }
  }

  // ------------------------------------------------------------------ controles
  function detener() { if (S.temporizador) { clearInterval(S.temporizador); S.temporizador = null; } $("#var-play").textContent = "Reproducir"; }
  function reproducir() {
    detener();
    const x = v();
    if (S.pos >= x.pasos.length) fijar(0);
    $("#var-play").textContent = "Pausar";
    S.temporizador = setInterval(() => { if (S.pos >= v().pasos.length) { detener(); return; } fijar(S.pos + 1); }, 1500);
  }
  $("#var-play").addEventListener("click", () => { if (S.temporizador) detener(); else if (v() && v().factible) reproducir(); });
  $("#var-ant").addEventListener("click", () => { detener(); fijar(S.pos - 1); });
  $("#var-sig").addEventListener("click", () => { detener(); fijar(S.pos + 1); });
  $("#var-slider").addEventListener("input", (e) => { detener(); fijar(parseInt(e.target.value, 10)); });
  document.querySelectorAll("#var-versiones [data-version]").forEach((b) => b.addEventListener("click", () => {
    if (!S.datos || (b.dataset.version === "parciales" && !S.datos.parciales)) return;
    detener(); S.version = b.dataset.version; S.pos = 0; dibujar();
  }));
  document.addEventListener("keydown", (e) => {
    if (S.vista !== "variante" || !v() || !v().factible || ["TEXTAREA", "INPUT", "SELECT"].includes(e.target.tagName)) return;
    if (e.key === "ArrowLeft") { detener(); fijar(S.pos - 1); }
    if (e.key === "ArrowRight") { detener(); fijar(S.pos + 1); }
  });
})();
