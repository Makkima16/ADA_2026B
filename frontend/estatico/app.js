"use strict";

/* Visor del voraz (Parte 2). Toda la lógica de decisión vive en el código del
   proyecto (src/auditoria), invocada desde el servidor local: aquí solo se arma el
   caso, se pide el análisis y se dibuja el resultado paso a paso. */

const $ = (sel) => document.querySelector(sel);
const todasLasFilas = () => [...document.querySelectorAll(".fila-manual")];

const LIMITE_CASILLAS = 40;   // con más riesgos que esto, la fila pasa a texto
const VELOCIDAD_MS = 1500;
const MAX_CHIPS = 40;         // tope de fichas dibujadas en una lista de riesgos

const estado = {
  metodo: "",      // combinación cuyo recorrido se muestra: "" es el voraz normal; si no, letras e, r, p
  res: null,     // último resultado devuelto por el servidor
  pos: 0,        // paso actual: 0 = antes de elegir, m = final
  temporizador: null,
  archivo: null, // { nombre, completo, texto } del archivo elegido en "Subir archivo"
};

/* ------------------------- utilidades ---------------------------------- */

/* Los nombres vienen del archivo y se insertan como HTML: se escapan siempre. */
function esc(texto) {
  return String(texto).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const coma = (x, dec) => Number(x).toFixed(dec).replace(".", ",");

/* Si el archivo trae ids (JSON) se muestran E01, R01...; si no, los números.
   `fuente` es el resultado del análisis (por defecto) o la vista previa del archivo. */
function nombreInteraccion(j, fuente) {
  const f = fuente || estado.res;
  const ids = f && f.ids_interaccion;
  return esc(ids ? ids[j - 1] : j);
}

function nombreRiesgo(c, fuente) {
  const f = fuente || estado.res;
  const ids = f && f.ids_categoria;
  return esc(ids ? ids[c - 1] : c);
}

function nombreCorto(c, fuente) {
  /* Nombre descriptivo del riesgo ("seguridad"), o "" si el archivo no lo trae. */
  const f = fuente || estado.res;
  const nombres = f && f.nombres_categoria;
  return nombres && nombres[c - 1] ? esc(nombres[c - 1]) : "";
}

function descripcionRiesgo(c, fuente) {
  /* "R04 (seguridad)" para los textos de ayuda al pasar el mouse. */
  const corto = nombreCorto(c, fuente);
  return nombreRiesgo(c, fuente) + (corto ? " (" + corto + ")" : "");
}

const ICONO_ALERTA =
  '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16v.5"/></svg>';
const ICONO_OK =
  '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>';
const FLECHA =
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9A8F74" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>';

/* ------------------------- armado del caso (formulario) ---------------- */

function riesgosDelFormulario() {
  return Math.max(1, Math.min(200, parseInt($("#manual-r").value, 10) || 1));
}

function interaccionesDelFormulario() {
  return Math.max(1, Math.min(200, parseInt($("#manual-n").value, 10) || 1));
}

function generarFilas() {
  const n = interaccionesDelFormulario();
  const r = riesgosDelFormulario();
  const contenedor = $("#filas-manuales");
  ocultarError();
  contenedor.innerHTML = "";
  for (let j = 1; j <= n; j++) contenedor.appendChild(crearFila(j, r));
  actualizarRevision();
  actualizarPrevisualizacion();
}

function crearFila(j, r) {
  const fila = document.createElement("div");
  fila.className = "fila-manual";
  fila.dataset.j = j;

  const encabezado = document.createElement("div");
  encabezado.className = "encabezado-fila";
  encabezado.innerHTML =
    "<span class='rotulo-fila'>Interacción " + j + "<small class='cuenta-fila'>0 riesgos</small></span>" +
    "<span class='miniacciones'>" +
    "<button type='button' class='btn mini' data-accion='todos'>todos</button>" +
    "<button type='button' class='btn mini' data-accion='ninguno'>ninguno</button>" +
    "</span>";
  fila.appendChild(encabezado);

  if (r <= LIMITE_CASILLAS) {
    const casillas = document.createElement("div");
    casillas.className = "riesgos-fila";
    casillas.setAttribute("role", "group");
    casillas.setAttribute("aria-label", "Riesgos que revisa la interacción " + j);
    for (let c = 1; c <= r; c++) {
      const etiqueta = document.createElement("label");
      etiqueta.innerHTML =
        '<input type="checkbox" class="marca" data-c="' + c + '" aria-label="la interacción ' + j +
        " revisa el riesgo " + c + '">' + c;
      casillas.appendChild(etiqueta);
    }
    fila.appendChild(casillas);
  } else {
    const entrada = document.createElement("input");
    entrada.type = "text";
    entrada.className = "categorias-manuales";
    entrada.spellcheck = false;
    entrada.placeholder = "números entre 1 y " + r + ", separados por espacios";
    fila.appendChild(entrada);
    const detalle = document.createElement("div");
    detalle.className = "error-fila oculto";
    fila.appendChild(detalle);
  }
  return fila;
}

function riesgosMarcados(fila) {
  const casillas = fila.querySelector(".riesgos-fila");
  if (casillas) {
    return [...casillas.querySelectorAll(".marca:checked")]
      .map((b) => parseInt(b.dataset.c, 10))
      .sort((a, b) => a - b);
  }
  const entrada = fila.querySelector(".categorias-manuales");
  return entrada
    ? entrada.value.split(/[,\s]+/).filter(Boolean).map(Number).filter((x) => Number.isInteger(x))
    : [];
}

function actualizarCuenta(fila) {
  const n = riesgosMarcados(fila).length;
  const marca = fila.querySelector(".cuenta-fila");
  if (marca) marca.textContent = n + (n === 1 ? " riesgo" : " riesgos");
}

function textoDelFormulario() {
  const lineas = [riesgosDelFormulario() + " " + interaccionesDelFormulario()];
  for (const fila of todasLasFilas()) lineas.push(riesgosMarcados(fila).join(" "));
  return lineas.join("\n") + "\n";
}

function actualizarPrevisualizacion() {
  $("#texto-previsualizacion").textContent = textoDelFormulario();
}

/* --------------------- validación en vivo del caso --------------------- */

/* Guía visual mientras se marca; el veredicto real lo da el análisis, que
   valida el caso con el lector del proyecto. */
function actualizarRevision() {
  const r = riesgosDelFormulario();
  const revisados = new Set();
  for (const fila of todasLasFilas()) {
    for (const c of riesgosMarcados(fila)) {
      if (c >= 1 && c <= r) revisados.add(c);
    }
  }
  const faltan = [];
  for (let c = 1; c <= r; c++) {
    if (!revisados.has(c)) faltan.push(c);
  }
  const panel = $("#estado-cobertura");
  if (!todasLasFilas().length) {
    panel.className = "estado-cobertura";
    panel.textContent = "";
    return;
  }
  if (!faltan.length) {
    panel.className = "estado-cobertura ok";
    panel.textContent = r === 1 ? "Vista previa: el riesgo ya tiene al menos una interacción que lo revisa." : "Vista previa: los " + r + " riesgos ya tienen al menos una interacción que los revisa.";
  } else {
    panel.className = "estado-cobertura aviso";
    panel.textContent =
      "Vista previa: nadie revisa todavía " +
      (faltan.length === r ? "ningún riesgo" : "el riesgo " + faltan.join(", el ")) +
      ". El análisis lo confirmará.";
  }
}

function validarTokensDeFila(fila) {
  /* Solo en el modo de texto (riesgos > LIMITE_CASILLAS): avisa en vivo
     números inexistentes, repetidos o que no son enteros. */
  const r = riesgosDelFormulario();
  const entrada = fila.querySelector(".categorias-manuales");
  const detalle = fila.querySelector(".error-fila");
  if (!entrada || !detalle) return true;
  const tokens = entrada.value.split(/[,\s]+/).filter(Boolean);
  const vistos = new Set();
  const problemas = [];
  for (const token of tokens) {
    if (!/^\d+$/.test(token)) problemas.push("'" + token + "' no es un número");
    else {
      const valor = parseInt(token, 10);
      if (valor < 1 || valor > r) problemas.push("el riesgo " + valor + " no existe (van de 1 a " + r + ")");
      else if (vistos.has(valor)) problemas.push("el riesgo " + valor + " está repetido");
      else vistos.add(valor);
    }
  }
  fila.classList.toggle("error", problemas.length > 0);
  detalle.classList.toggle("oculto", problemas.length === 0);
  detalle.textContent = problemas.length ? "Revisa: " + problemas.join("; ") + "." : "";
  return problemas.length === 0;
}

function validarFormulario() {
  const sinRiesgos = [];
  for (const fila of todasLasFilas()) {
    fila.classList.remove("error");
    const detalle = fila.querySelector(".error-fila");
    if (detalle) detalle.classList.add("oculto");
    if (!riesgosMarcados(fila).length) sinRiesgos.push(fila.dataset.j);
  }
  if (sinRiesgos.length) {
    mostrarError(
      "La interacción " + sinRiesgos.join(", la ") +
      " no tiene riesgos asignados: marca al menos uno (o reduce la cantidad de interacciones)."
    );
    return false;
  }
  let tokensOk = true;
  for (const fila of todasLasFilas()) {
    if (!validarTokensDeFila(fila)) tokensOk = false;
  }
  if (!tokensOk) {
    mostrarError("Hay números que no corresponden a riesgos existentes: revisa las filas marcadas en rojo.");
    return false;
  }
  return true;
}

/* ------------------------------ servidor ------------------------------- */

async function pedir(ruta, texto, nombre) {
  /* Devuelve { ok, datos }; si no hay servidor, ok es false y datos trae el mensaje. */
  try {
    const respuesta = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: texto, nombre: nombre }),
    });
    const datos = await respuesta.json();
    return { ok: respuesta.ok, datos: datos };
  } catch (e) {
    return { ok: false, datos: { error: "No se pudo contactar el servidor local. ¿Sigue corriendo?" } };
  }
}

async function analizar(texto, nombre, desdeFormulario) {
  ocultarError();
  const { ok, datos } = await pedir("/api/resolver", texto, nombre);
  if (!ok) {
    mostrarErrorServidor(datos.error || "Error desconocido del servidor.", desdeFormulario);
    return;
  }
  estado.res = datos;
  estado.pos = 0;
  dibujarSalida();
  $("#panel-resultado").scrollIntoView({ behavior: "smooth", block: "start" });
  if (datos.factible) reproducir();
}

/* ------------------------- mensajes de error --------------------------- */

function mostrarError(mensaje, detalle) {
  $("#mensaje-error").textContent = mensaje;
  const caja = $("#detalle-error");
  if (detalle) {
    $("#detalle-error-texto").textContent = detalle;
    caja.classList.remove("oculto");
  } else {
    caja.classList.add("oculto");
  }
  $("#banner-error").classList.remove("oculto");
}

function mostrarErrorServidor(mensaje, desdeFormulario) {
  /* El lector del proyecto reporta problemas por número de línea del archivo
     interno; solo si el caso salió del formulario se señala la interacción
     correspondiente (con un archivo subido o pegado esas filas no aplican). */
  todasLasFilas().forEach((f) => f.classList.remove("error"));
  const coincidencia = desdeFormulario ? mensaje.match(/línea (\d+)/) : null;
  if (coincidencia) {
    const interaccion = parseInt(coincidencia[1], 10) - 1;
    const fila = interaccion >= 1 ? document.querySelector('.fila-manual[data-j="' + interaccion + '"]') : null;
    if (fila) {
      fila.classList.add("error");
      fila.scrollIntoView({ block: "center", behavior: "smooth" });
      mostrarError("Revisa la interacción " + interaccion + ": hay algo mal escrito en sus riesgos.",
        "Detalle del lector de archivos: " + mensaje);
      return;
    }
  }
  mostrarError(mensaje);
}

function ocultarError() {
  $("#banner-error").classList.add("oculto");
}

/* ------------------- vista previa del archivo subido ------------------- */

async function previsualizar(texto, nombre) {
  /* Pide al servidor que lea el caso con el lector del proyecto (sin resolverlo). */
  $("#vista-previa").classList.add("oculto");
  $("#btn-analizar-archivo").disabled = true;
  const { ok, datos } = await pedir("/api/previsualizar", texto, nombre);
  if (!ok) {
    mostrarErrorServidor(datos.error || "Error desconocido del servidor.", false);
    return;
  }
  dibujarVistaPrevia(datos);
  $("#btn-analizar-archivo").disabled = false;
}

function dibujarVistaPrevia(info) {
  /* Muestra cuántas interacciones y riesgos trae el caso y cómo se componen. */
  const r = info.r;
  const cubiertoPor = Array.from({ length: r + 1 }, () => []);
  info.S.forEach((fila, k) => fila.forEach((c) => cubiertoPor[c].push(k + 1)));
  const sinCubrir = [];
  for (let c = 1; c <= r; c++) if (!cubiertoPor[c].length) sinCubrir.push(c);
  const vacias = info.S.reduce((a, fila, k) => (fila.length ? a : a.concat(k + 1)), []);
  const relaciones = info.S.reduce((a, f) => a + f.length, 0);

  $("#vp-nombre").textContent = estado.archivo ? estado.archivo.completo : info.nombre;
  $("#vp-cifras").innerHTML =
    '<div class="cifra"><b>' + info.n + "</b><span>interacciones</span></div>" +
    '<div class="cifra"><b>' + info.r + "</b><span>tipos de riesgo</span></div>" +
    '<div class="cifra"><b>' + relaciones + "</b><span>relaciones</span></div>";

  let avisos = "";
  if (vacias.length) {
    avisos += '<div class="aviso ambar" role="status">' + ICONO_ALERTA + "<span><strong>" +
      vacias.map((j) => nombreInteraccion(j, info)).join(", ") +
      (vacias.length === 1 ? " no revisa ningún riesgo." : " no revisan ningún riesgo.") +
      "</strong> No pasa nada: simplemente no se elegirá.</span></div>";
  }
  if (sinCubrir.length) {
    avisos += '<div class="aviso rojo" role="status">' + ICONO_ALERTA + "<span><strong>Ninguna interacción revisa: " +
      sinCubrir.map((c) => nombreRiesgo(c, info)).join(", ") +
      ".</strong> El caso no tendrá solución.</span></div>";
  } else {
    avisos += '<div class="aviso ok">' + ICONO_OK +
      "<span>Todos los riesgos tienen al menos una interacción que los revisa.</span></div>";
  }
  $("#vp-avisos").innerHTML = avisos;

  $("#vp-interacciones").innerHTML = info.S.map((fila, k) =>
    "<li><span class='li-id'>" + nombreInteraccion(k + 1, info) + "</span>" +
    "<span class='li-texto" + (fila.length ? "" : " vacio-ambar") + "'>" +
    (fila.length ? fila.map((c) => nombreRiesgo(c, info)).join(" ") : "ninguno") + "</span></li>"
  ).join("");

  $("#vp-riesgos").innerHTML = cubiertoPor.slice(1).map((lista, i) => {
    const c = i + 1;
    const corto = nombreCorto(c, info);
    const imp = info.importancia ? " · importancia " + esc(info.importancia[i]) : "";
    return "<li class='col'><span class='li-id riesgo'>" + nombreRiesgo(c, info) +
      (corto || imp ? " <span class='li-nombre'>" + corto + imp + "</span>" : "") + "</span>" +
      "<span class='li-texto" + (lista.length ? "" : " vacio-ambar") + "'>" +
      (lista.length ? lista.map((j) => nombreInteraccion(j, info)).join(" ") : "nadie") + "</span></li>";
  }).join("");

  $("#vista-previa").classList.remove("oculto");
}

/* ------------------------------ salida --------------------------------- */

function dibujarSalida() {
  const res = estado.res;
  $("#vacio").classList.add("oculto");
  if (!res.factible) {
    $("#salida").classList.add("oculto");
    $("#no-factible").classList.remove("oculto");
    $("#texto-no-factible").innerHTML =
      "<p>Ninguna interacción revisa estos riesgos, así que es imposible cubrirlos todos:</p>" +
      '<div class="chips" style="margin: 12px 0">' +
      res.sin_cubrir.map((c) => '<span class="chip rojo">' + nombreRiesgo(c) + "</span>").join("") +
      "</div><p class='nota' style='font-size:17px'>Agrega una interacción que los revise, o quítalos del caso, y vuelve a analizar.</p>";
    detenerReproduccion();
    return;
  }
  $("#no-factible").classList.add("oculto");
  $("#salida").classList.remove("oculto");
  estado.metodo = "";
  marcarMetodoActivo();
  dibujarResumen(res);
  dibujarCosto(res);
  dibujarFuerzaBruta(res);
  dibujarComparacion(res);
  $("#slider-paso").max = totalPasos();
  $("#texto-evidencia").textContent = res.texto_evidencia;
  fijarPosicion(0);
}

function dibujarResumen(res) {
  const m = datosMetodo(res);
  const J = m.J;
  const tieneOptimo = res.optimo !== null;
  const d = res.S.reduce((a, f) => Math.max(a, f.length), 0);
  const razon = tieneOptimo ? J.length / Math.max(res.optimo.length, 1) : null;
  const cubierto = new Set();
  J.forEach((j) => res.S[j - 1].forEach((c) => cubierto.add(c)));
  const cubre = cubierto.size === res.r;
  const ficha = (j) => '<span class="ficha-orden">' + nombreInteraccion(j) + "</span>";
  const orden = J.map(ficha).join(FLECHA);
  const conGarantia = estado.metodo === "" || estado.metodo === "e";

  const tarjetas = [
    '<div class="stat destacada"><span class="clave">' + nombreCombinacion(estado.metodo) + ' · hay que auditar</span>' +
      '<span class="grande">' + J.length + " <small>de " + res.n + (res.n === 1 ? " interacción" : " interacciones") + "</small></span>" +
      '<span class="pie">' + (cubre ? (res.r === 1 ? "y así se revisa el único riesgo ✓" : "y así se revisan los " + res.r + " riesgos ✓") : "pero NO quedan todos los riesgos revisados") +
      "</span></div>",
    '<div class="stat ancha"><span class="clave">En este orden</span><div class="orden">' + orden + "</div></div>",
    '<div class="stat"><span class="clave">Garantía teórica</span>' +
      (conGarantia
        ? '<span class="medio">H(' + d + ") ≈ " + coma(res.cota, 2) + "</span>" +
          '<span class="pie">nunca usa más de ' + coma(res.cota, 2) + " veces lo mínimo</span>"
        : '<span class="texto">Sin garantía demostrada</span><span class="pie">solo medida en los experimentos</span>') + "</div>",
    '<div class="stat"><span class="clave">Mínimo real</span>' +
      (tieneOptimo
        ? '<span class="texto">' + res.optimo.length + (res.optimo.length === 1 ? " interacción" : " interacciones") + "</span>" +
          '<span class="pie">' + res.optimo.map((j) => nombreInteraccion(j)).join(", ") + "</span>"
        : '<span class="texto">No se calcula</span><span class="pie">solo con 12 interacciones o menos</span>') +
      "</div>",
    '<div class="stat"><span class="clave">Comparado con el mínimo</span>' +
      (tieneOptimo
        ? '<span class="texto">' + (razon === 1 ? "igual al mínimo" : coma(razon, 2) + " veces el mínimo") + "</span>" +
          '<span class="pie">' + J.length + " frente a " + res.optimo.length + "</span>"
        : '<span class="texto" style="color: var(--texto-3)">—</span><span class="pie">requiere el mínimo real</span>') +
      "</div>",
    '<div class="stat"><span class="clave">Tiempo</span><span class="medio">' +
      coma(m.tiempo_s * 1000, 3) + " ms</span></div>",
  ];
  $("#resumen").innerHTML = tarjetas.join("");
}

function dibujarFuerzaBruta(res) {
  /* Comprobación por fuerza bruta: solo con 12 interacciones o menos. */
  const fb = res.fuerza_bruta;
  const caja = $("#tarjeta-fb");
  if (!fb || !fb.aplica) {
    caja.innerHTML = "<h3>Comprobación por fuerza bruta</h3>" +
      '<p class="nota">No se ejecuta: ' + ((fb && fb.motivo) || "no hay datos") + ".</p>";
    return;
  }
  const filas = fb.tamanos.map((t) =>
    "<tr" + (t.encontrado ? ' class="hallado"' : "") + "><td>" + t.k + "</td><td>" + t.subconjuntos + "</td><td>" +
    t.probados + "</td><td>" + (t.encontrado ? "sí, es el mínimo" : "ninguno cubre todo") + "</td></tr>").join("");
  const igual = res.J.length === fb.optimo.length;
  caja.innerHTML =
    "<h3>Comprobación por fuerza bruta</h3>" +
    '<p class="nota">Prueba todas las combinaciones de interacciones, de a una, de a dos, de a tres… hasta que una cubre todos los riesgos. ' +
    "Es lenta, pero encuentra el mínimo real: sirve para comprobar al método rápido.</p>" +
    '<div class="resumen-fb"><span><b>' + fb.optimo.length + "</b> interacciones: " +
    fb.optimo.map((j) => nombreInteraccion(j)).join(", ") + "</span>" +
    "<span>Revisó <b>" + fb.revisados + "</b> de <b>" + fb.total + "</b> combinaciones posibles (2<sup>" + res.n + "</sup>)</span>" +
    "<span>Tardó <b>" + coma(fb.tiempo_s * 1000, 3) + " ms</b></span>" +
    "<span>" + (igual ? "El método rápido acertó: también usa " + res.J.length
                      : "El método rápido usa " + res.J.length + " y el mínimo es " + fb.optimo.length) + "</span></div>" +
    '<table class="tabla-fb"><thead><tr><th>Tamaño de la combinación</th><th>Combinaciones posibles</th><th>Probadas</th><th>¿Alguna cubre todo?</th></tr></thead><tbody>' +
    filas + "</tbody></table>";
}

/* ------------- voraz normal y combinaciones de ingredientes ------------- */

/* Tres ingredientes que se le suman al voraz normal: e = esenciales, r = rareza, p = parejas.
   La clave de una combinación son sus letras en ese orden ("" es el voraz normal). */
const COMBINACIONES = [
  { clave: "", nombre: "Voraz normal" },
  { clave: "e", nombre: "Esenciales" },
  { clave: "r", nombre: "Rareza" },
  { clave: "p", nombre: "Parejas" },
  { clave: "er", nombre: "Esenciales + rareza" },
  { clave: "ep", nombre: "Esenciales + parejas" },
  { clave: "rp", nombre: "Rareza + parejas" },
  { clave: "erp", nombre: "Los tres juntos" },
];
const msTexto = (x) => coma(x * 1000, 3) + " ms";

function nombreCombinacion(clave) {
  const c = COMBINACIONES.find((x) => x.clave === clave);
  return c ? c.nombre : clave;
}

function banderas(clave) {
  return { e: clave.includes("e"), r: clave.includes("r"), p: clave.includes("p") };
}

function claveDe(ing) {
  return (ing.e ? "e" : "") + (ing.r ? "r" : "") + (ing.p ? "p" : "");
}

function costoTeorico(clave) {
  return banderas(clave).p ? "O(n²·r·min(n, r))" : "O(n·r·min(n, r))";
}

function datosMetodo(res) {
  /* Resultado de la combinación elegida: J, pasos, esenciales, tiempo. */
  return res.comparacion.metodos[estado.metodo];
}

function totalPasos() {
  return datosMetodo(estado.res).pasos.length;
}

function coberturaDe(m) {
  /* Para cada riesgo, la interacción que lo revisó por primera vez en el recorrido del método. */
  const filas = [];
  m.pasos.forEach((p) => p.nuevas.forEach((c) => filas.push({ categoria: c, interaccion: p.j })));
  return filas.sort((a, b) => a.categoria - b.categoria);
}

function veredicto(tam, base) {
  if (tam < base) return '<span class="mejor">mejor (' + (base - tam) + " menos)</span>";
  if (tam > base) return '<span class="peor">peor (' + (tam - base) + " más)</span>";
  return '<span class="igual">igual</span>';
}

function dibujarComparacion(res) {
  const caja = $("#tarjeta-comparacion");
  const cmp = res.comparacion;
  if (!cmp) { caja.innerHTML = ""; return; }
  const m = cmp.metodos;
  const base = m[""].J.length;
  const opt = cmp.optimo ? cmp.optimo.length : null;
  const orden = (J) => J.map((j) => nombreInteraccion(j)).join(" → ");

  let filas = "";
  for (const { clave, nombre } of COMBINACIONES) {
    const x = m[clave];
    const tam = x.J.length;
    filas += '<tr' + (clave === estado.metodo ? ' class="fila-elegida"' : "") + "><td>" + nombre + '</td><td class="num"><b>' + tam + "</b></td><td>" + orden(x.J) + "</td><td>" +
      (clave === "" ? "—" : veredicto(tam, base)) + "</td><td>" +
      (opt === null ? "—" : tam === opt ? "es el mínimo" : coma(tam / opt, 2) + " veces el mínimo") +
      '</td><td class="num">' + msTexto(x.tiempo_s) + "</td><td>" + costoTeorico(clave) + "</td></tr>";
  }
  if (opt !== null) {
    filas += '<tr class="optimo"><td>Mínimo real (fuerza bruta)</td><td class="num">' + opt + "</td><td>" + orden(cmp.optimo) +
      '</td><td>—</td><td>—</td><td class="num">' + msTexto(cmp.tiempo_optimo_s) + "</td><td>O(2^n·n·r)</td></tr>";
  } else {
    filas += '<tr class="optimo"><td colspan="7">Mínimo real: no se calcula con más de 12 interacciones (la fuerza bruta es exponencial en n). ' +
      "Lo único que se sabe del mínimo es que no baja de " + cmp.cota_inferior + " (cota inferior ⌈r / d⌉).</td></tr>";
  }

  /* qué interacciones son esenciales y por qué */
  const cuenta = {};
  res.S.forEach((fila) => fila.forEach((c) => { cuenta[c] = (cuenta[c] || 0) + 1; }));
  const esenciales = m.e.esenciales || [];
  const textoEsenciales = esenciales.length
    ? "Esenciales: " + esenciales.map((j) => {
        const unicos = res.S[j - 1].filter((c) => cuenta[c] === 1);
        return nombreInteraccion(j) + " (la única que revisa " + unicos.map((c) => nombreRiesgo(c)).join(", ") + ")";
      }).join("; ") + "."
    : "No hay esenciales: ningún riesgo lo revisa una sola interacción, así que sumar ese ingrediente no cambia nada.";

  caja.innerHTML =
    "<h3>Comparación: voraz normal frente a cada combinación</h3>" +
    '<p class="nota">Las ocho combinaciones corren sobre el mismo caso. No reemplazan al voraz normal, que es la solución de la entrega. ' +
    "Arriba, con los botones de ingredientes, puedes ver paso a paso cómo resuelve el caso cada una.</p>" +
    '<div style="overflow-x:auto"><table class="tabla-cmp"><thead><tr><th>Método</th><th class="num">Interacciones</th><th>En este orden</th>' +
    "<th>Frente al voraz normal</th><th>Frente al mínimo</th><th class=\"num\">Tiempo</th><th>Costo teórico</th></tr></thead><tbody>" + filas + "</tbody></table></div>" +
    '<p class="nota-cmp">' + textoEsenciales + "</p>";
}

/* -------------- explicación de cada paso según los ingredientes -------------- */

function candidatasTexto(res, p) {
  /* Cuántos riesgos nuevos (o qué puntaje, con rareza) tenía cada interacción en este paso (las mejores primero). */
  const valores = p.puntajes || p.candidatos;
  const fmt = (x) => (p.puntajes ? coma(x, 2) : x);
  const cand = valores.map((cant, i) => ({ j: i + 1, cant: cant }));
  cand.sort((a, b) => b.cant - a.cant || a.j - b.j);
  const mostradas = cand.slice(0, 10).map((x) =>
    '<span class="cand' + (x.j === p.j ? " elegida" : "") + '">' + nombreInteraccion(x.j) + " · " + fmt(x.cant) + "</span>").join("");
  const resto = cand.length > 10 ? '<span class="nota"> … y ' + (cand.length - 10) + " más</span>" : "";
  return '<div class="cands">' + mostradas + resto + "</div>";
}

function mejorDelVoraz(p) {
  /* La interacción que el voraz normal elegiría en este mismo estado (más nuevas; empate: menor índice). */
  let mj = 1, mc = -1;
  p.candidatos.forEach((c, i) => { if (c > mc) { mc = c; mj = i + 1; } });
  return { j: mj, cant: mc };
}

const nuevosTxt = (c) => c + (c === 1 ? " riesgo nuevo" : " riesgos nuevos");

function razonEleccion(res, clave, k) {
  /* La razón específica de por qué se eligió esta interacción y no otra. */
  const b = banderas(clave);
  const m = res.comparacion.metodos[clave];
  const p = m.pasos[k - 1];
  const esenciales = m.esenciales || [];
  const esEsencial = b.e && k <= esenciales.length;
  const nombre = nombreInteraccion(p.j);
  const cant = p.candidatos[p.j - 1];
  const otros = p.candidatos.map((c, i) => ({ j: i + 1, c: c })).filter((x) => x.j !== p.j).sort((a, b2) => b2.c - a.c || a.j - b2.j);
  let txt;
  if (esEsencial) {
    const unicas = (m.unicas[String(p.j)] || []).map((c) => nombreRiesgo(c)).join(", ");
    txt = nombre + " es la única interacción que revisa " + unicas + ": si no se audita, ese riesgo quedaría sin revisar. Por eso se elige sin compararla con las demás.";
  } else if (b.p) {
    const par = p.par;
    const pt = p.puntajes;
    const v = mejorDelVoraz(p);
    if (b.r) {
      if (par[0] === par[1]) {
        txt = "ninguna pareja de interacciones vale más que ella sola: su puntaje de rareza es " + coma(pt[p.j - 1], 2) + " (" + nuevosTxt(cant) + ", y los que pocas interacciones revisan pesan más).";
      } else {
        const otro = par[0] === p.j ? par[1] : par[0];
        txt = "forma parte de la mejor pareja, (" + nombreInteraccion(par[0]) + ", " + nombreInteraccion(par[1]) + "), que juntas valen " + coma(p.puntaje_par, 2) +
          " de puntaje de rareza (" + nuevosTxt(p.cobertura_par) + ") y ninguna otra pareja vale más (en un empate gana la primera en orden). Dentro de la pareja se elige " + nombre +
          " porque vale " + coma(pt[p.j - 1], 2) + " por sí sola" + (pt[p.j - 1] > pt[otro - 1] ? ", frente a " + coma(pt[otro - 1], 2) + " de la interacción " + nombreInteraccion(otro) : " (empata con " + nombreInteraccion(otro) + ", gana la que revisa más o, si no, el menor número)") + ".";
      }
      if (v.j !== p.j) txt += " El voraz normal habría elegido " + nombreInteraccion(v.j) + " (" + v.cant + (v.cant === 1 ? " nuevo" : " nuevos") + ") porque mira una sola interacción a la vez y cuenta todos los riesgos igual.";
    } else {
      if (par[0] === par[1]) {
        const mej = otros.length ? otros[0] : null;
        txt = "revisa " + nuevosTxt(cant) + (mej ? " (la siguiente, " + nombreInteraccion(mej.j) + ", " + mej.c + ")" : "") + " y ninguna pareja de interacciones revisa más que ella sola.";
      } else {
        const otro = par[0] === p.j ? par[1] : par[0];
        const cOtro = p.candidatos[otro - 1];
        txt = "forma parte de la mejor pareja, (" + nombreInteraccion(par[0]) + ", " + nombreInteraccion(par[1]) + "), que juntas revisan " + nuevosTxt(p.cobertura_par) +
          " y ninguna otra pareja revisa más (en un empate gana la primera en orden). Dentro de la pareja se elige " + nombre +
          " porque revisa " + cant + " por sí sola" + (cant > cOtro ? ", frente a " + cOtro + " de la interacción " + nombreInteraccion(otro) : " (empata con " + nombreInteraccion(otro) + ", gana el menor número)") + ".";
      }
      if (v.j !== p.j) txt += " El voraz normal habría elegido " + nombreInteraccion(v.j) + " (" + v.cant + (v.cant === 1 ? " nuevo" : " nuevos") + ") porque mira una sola interacción a la vez.";
    }
  } else if (b.r) {
    const pt = p.puntajes;
    const ord = pt.map((x, i) => ({ j: i + 1, x: x })).filter((o) => o.j !== p.j).sort((a, b2) => b2.x - a.x || a.j - b2.j);
    const mio = pt[p.j - 1];
    if (!ord.length) txt = "es la única interacción del caso.";
    else if (ord[0].x < mio) txt = "su puntaje es " + coma(mio, 2) + " (cada riesgo pendiente vale 1 dividido entre cuántas interacciones lo revisan) y la mejor de las otras, " +
      nombreInteraccion(ord[0].j) + ", solo " + coma(ord[0].x, 2) + ". Los riesgos que pocas interacciones revisan pesan más.";
    else {
      const emp = ord.filter((o) => o.x === mio).map((o) => nombreInteraccion(o.j));
      txt = "empata en puntaje (" + coma(mio, 2) + ") con " + emp.join(", ") + "; desempata la que revisa más riesgos nuevos (" + cant + ") y, si siguen iguales, el menor número.";
    }
  } else if (!otros.length) {
    txt = "es la única interacción del caso.";
  } else if (otros[0].c === 0) {
    txt = "revisa " + nuevosTxt(cant) + " y las demás interacciones ya no revisan ningún riesgo pendiente (o ya fueron elegidas).";
  } else if (otros[0].c < cant) {
    txt = "revisa " + nuevosTxt(cant) + " y la mejor de las otras, " + nombreInteraccion(otros[0].j) + ", solo " + otros[0].c + ". Ninguna otra pasa de " + otros[0].c + ".";
  } else {
    const emp = otros.filter((x) => x.c === cant).map((x) => nombreInteraccion(x.j));
    txt = "empata en " + nuevosTxt(cant) + " con " + emp.join(", ") + "; se elige " + nombre + " por tener el menor número (desempate fijo).";
  }
  return '<p class="razon"><b>¿Por qué ' + nombre + " y no otra?</b> " + txt + "</p>";
}

function explicacionPaso(res, clave, k) {
  const b = banderas(clave);
  const m = res.comparacion.metodos[clave];
  const p = m.pasos[k - 1];
  const esenciales = m.esenciales || [];
  const nombre = nombreInteraccion(p.j);
  if (b.e && k <= esenciales.length) {
    const unicas = (m.unicas[String(p.j)] || []).map((c) => nombreRiesgo(c)).join(", ");
    return "<p><b>" + nombre + "</b> es <b>esencial</b>: es la única interacción que revisa " + unicas +
      ". Todo mínimo tiene que incluirla, así que se elige primero, sin comparar con las demás.</p>";
  }
  if (b.p && b.r)
    return "<p>Se valoró cada interacción sola y cada pareja por la <b>rareza</b> de lo que cubre: cada riesgo pendiente vale 1 dividido entre cuántas interacciones lo revisan. " +
      "Estos son los puntajes de cada interacción por sí sola en este paso:</p>" + candidatasTexto(res, p);
  if (b.p)
    return "<p>Se evaluaron todas las parejas. La mejor revisa " + nuevosTxt(p.cobertura_par) + " juntas. Así revisaba cada interacción por sí sola en este paso:</p>" + candidatasTexto(res, p);
  if (b.r)
    return "<p>Se puntúa cada interacción sumando, por cada riesgo que aún falta, 1 dividido entre cuántas interacciones lo revisan. Estos son los mejores puntajes de este paso:</p>" + candidatasTexto(res, p);
  const max = Math.max.apply(null, p.candidatos);
  const empatadas = p.candidatos.map((c, i) => (c === max ? i + 1 : 0)).filter((x) => x);
  return "<p>Se cuentan los riesgos nuevos que revisaría cada interacción. La que más revisa es <b>" + nombre + "</b> (" + max + ")." +
    (empatadas.length > 1 ? " Hay empate entre " + empatadas.map((j) => nombreInteraccion(j)).join(", ") + ": gana la de menor índice." : "") +
    "</p>" + candidatasTexto(res, p);
}

function introMetodo(res, clave) {
  const b = banderas(clave);
  const e = res.comparacion.metodos[clave].esenciales || [];
  let regla;
  if (b.p && b.r) regla = "mira <b>parejas</b> de interacciones y valora cada pareja por la <b>rareza</b> de lo que cubre (cada riesgo vale 1 dividido entre cuántas interacciones lo revisan)";
  else if (b.p) regla = "mira qué <b>pareja</b> de interacciones revisa más riesgos nuevos juntas y de esa pareja elige la que más revisa sola";
  else if (b.r) regla = "elige la interacción de mayor <b>puntaje de rareza</b> (cada riesgo pendiente vale 1 dividido entre cuántas interacciones lo revisan, así que los raros pesan más)";
  else regla = "elige la interacción que revisa <b>más riesgos que todavía no están revisados</b>";
  let t = "<p><b>" + nombreCombinacion(clave) + ".</b> " + (b.e ? "Primero las <b>esenciales</b> y, con lo que falte, en cada paso " : "En cada paso ") + regla + ".</p>";
  if (b.e) t += "<p>" + (e.length ? "Esenciales encontradas: <b>" + e.map((j) => nombreInteraccion(j)).join(", ") + "</b> (cada una es la única que revisa algún riesgo). Se eligen primero."
    : "No hay interacciones esenciales: ningún riesgo lo revisa una sola interacción, así que arranca directo con la regla de los pasos siguientes.") + "</p>";
  if (!b.e && !b.r && !b.p) t += "<p>Nunca se arrepiente de lo ya elegido.</p>";
  return t;
}

function cambiarMetodo(clave) {
  detenerReproduccion();
  estado.metodo = clave;
  marcarMetodoActivo();
  if (!estado.res || !estado.res.factible) return;
  dibujarResumen(estado.res);
  dibujarCosto(estado.res);
  dibujarComparacion(estado.res);
  $("#slider-paso").max = totalPasos();
  fijarPosicion(0);
}

function alternarIngrediente(letra) {
  /* Enciende o apaga un ingrediente y arma la combinación. Sin ninguno encendido vuelve al voraz normal. */
  const ing = banderas(estado.metodo);
  ing[letra] = !ing[letra];
  cambiarMetodo(claveDe(ing));
}

function marcarMetodoActivo() {
  const ing = banderas(estado.metodo);
  $("#btn-voraz").classList.toggle("activo", estado.metodo === "");
  $("#btn-voraz").setAttribute("aria-pressed", estado.metodo === "" ? "true" : "false");
  document.querySelectorAll("#ingredientes .btn-ing").forEach((b) => {
    const activo = ing[b.dataset.ing];
    b.classList.toggle("activo", activo);
    b.setAttribute("aria-pressed", activo ? "true" : "false");
  });
  $("#nombre-combinacion").textContent = nombreCombinacion(estado.metodo);
}

$("#btn-voraz").addEventListener("click", () => cambiarMetodo(""));
document.querySelectorAll("#ingredientes .btn-ing").forEach((b) => b.addEventListener("click", () => alternarIngrediente(b.dataset.ing)));

/* ------------------------------ costo total ------------------------------ */

function dibujarCosto(res) {
  /* Cuadro aparte: costo de la solución (|J|) y costo del algoritmo con los números de este caso. */
  const caja = $("#tarjeta-costo");
  if (!res.comparacion) { caja.innerHTML = ""; return; }
  const clave = estado.metodo;
  const b = banderas(clave);
  const m = datosMetodo(res);
  const n = res.n, r = res.r, k = m.J.length;
  const e = b.e ? (m.esenciales || []).length : 0;
  const sumaS = res.S.reduce((a, f) => a + f.length, 0);
  const pares = n * (n - 1) / 2;
  const miles = (x) => String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  /* --- costo de la solución --- */
  const unos = k <= 10 ? Array(k).fill("1").join(" + ") : "1 + 1 + … + 1 (" + k + " veces)";
  const interTxt = k === 1 ? " interacción" : " interacciones";
  let compara;
  if (res.optimo) compara = k === res.optimo.length ? "El mínimo real es " + res.optimo.length + ": este método lo alcanza."
    : "El mínimo real es " + res.optimo.length + ": este método usa " + (k - res.optimo.length) + " de más.";
  else compara = "No hay mínimo real calculado (n > 12); lo único seguro es que hacen falta al menos " + res.comparacion.cota_inferior + " (cota inferior ⌈r / d⌉).";

  /* --- costo del algoritmo: cada intersección o unión de conjuntos de a lo sumo r riesgos cuesta r comparaciones --- */
  const conteo = (b.e || b.r) ? sumaS : 0;
  const porPaso = b.p ? n + pares : n;           // con parejas: n intersecciones + n(n−1)/2 uniones; si no, n
  const pasosRestantes = k - e;
  const total = n * r + conteo + e * r + pasosRestantes * porPaso * r;
  const kTxt = b.e ? "(k − e)" : "k";
  const formula = ["n·r"].concat(conteo ? ["Σ|S_j|"] : [], b.e ? ["e·r"] : [],
    [kTxt + "·" + (b.p ? "(n + n(n−1)/2)" : "n") + "·r"]).join(" + ");
  const numeros = [n + "·" + r].concat(conteo ? [String(sumaS)] : [], b.e ? [e + "·" + r] : [],
    [pasosRestantes + "·" + (b.p ? "(" + n + " + " + miles(pares) + ")" : n) + "·" + r]).join(" + ");
  const cota = (b.p ? n * n : n) * r * Math.min(n, r);
  const razones = ["Factibilidad: n·r (n uniones de r comparaciones)."];
  if (conteo) razones.push("Contar cuántas interacciones revisan cada riesgo, que sirve para " +
    (b.e && b.r ? "las esenciales y la rareza" : b.e ? "hallar las esenciales" : "la rareza") + ": Σ|S_j| = " + sumaS + ".");
  if (b.e) razones.push(e === 0 ? "No hay esenciales, así que ese ingrediente no suma costo aquí."
    : "Elegir " + (e === 1 ? "la única esencial (e = 1)" : "las e = " + e + " esenciales") + ": r comparaciones cada una.");
  const operacion = (b.p ? "se valoran las n interacciones solas y las n(n−1)/2 parejas" + (b.r ? " por rareza" : "") : "se revisan las n interacciones" + (b.r ? " puntuándolas por rareza" : "")) +
    ", y cada operación cuesta r comparaciones" + (b.p ? ": por eso es un factor n más que el voraz normal." : ".");
  if (pasosRestantes === 0) razones.push("No quedan pasos después de las esenciales: ya cubren todo.");
  else razones.push((pasosRestantes === 1 ? "En el único paso" : "En cada uno de los " + pasosRestantes + " pasos") + (b.e ? " restante" + (pasosRestantes === 1 ? "" : "s") : "") + " " + operacion);
  const cotaTxt = "La cota teórica " + costoTeorico(clave) + " vale " + (b.p ? n + "²·" : n + "·") + r + "·" + Math.min(n, r) + " = " + miles(cota) +
    ": se llegaría a ella si hubiera min(n, r) pasos.";

  caja.innerHTML =
    "<h3>Costo total · " + nombreCombinacion(clave) + "</h3>" +
    '<div class="cols-costo">' +
      '<div class="bloque-costo"><h4>Costo de la solución</h4>' +
        '<p class="ecuacion">|J| = ' + (k === 1 ? "<b>1</b> interacción" : unos + " = <b>" + k + "</b> interacciones") + "</p>" +
        "<p>¿Por qué? El objetivo del problema es minimizar cuántas interacciones se auditan, y en la versión base cada una cuenta 1 " +
        "(los costos distintos por interacción, a_j, son de la variante ponderada). " + compara + "</p></div>" +
      '<div class="bloque-costo"><h4>Costo del algoritmo en este caso</h4>' +
        '<p class="ecuacion">T = ' + formula + "</p>" +
        '<p class="ecuacion">' + numeros + " = " + miles(total) + " <small>comparaciones de riesgos</small></p>" +
        "<p>¿Por qué? " + razones.join(" ") + "</p>" +
        '<p class="nota-cmp">' + cotaTxt + " Es una estimación por conteo de operaciones (n = " + n + ", r = " + r + ", k = " + k + "), no un tiempo medido.</p></div>" +
    "</div>";
}

/* ------------------------- decisión paso a paso ------------------------ */

function conjuntosDelPaso(res, k) {
  /* Riesgos ya revisados antes del paso k, y los que se revisan en él. */
  const todos = [];
  for (let c = 1; c <= res.r; c++) todos.push(c);
  const pasos = datosMetodo(res).pasos;
  const faltanDe = (i) => (i <= 0 ? todos : pasos[i - 1].faltan);
  const antes = new Set(todos.filter((c) => !faltanDe(k - 1).includes(c)));
  const nuevos = new Set(k >= 1 ? pasos[k - 1].nuevas : []);
  const despues = new Set([...antes, ...nuevos]);
  return { antes, nuevos, despues };
}

function fijarPosicion(pos) {
  const res = estado.res;
  if (!res || !res.factible) return;
  const m = totalPasos();
  estado.pos = Math.max(0, Math.min(pos, m));
  $("#slider-paso").value = estado.pos;
  const conj = conjuntosDelPaso(res, estado.pos);
  dibujarPaso(res, estado.pos, conj);
  dibujarHitos(res, estado.pos);
  dibujarMatriz(res, estado.pos, conj);
  const final = estado.pos === m;
  $("#cobertura-final").classList.toggle("oculto", !final);
  if (final) dibujarCobertura(res);
  if (final) detenerReproduccion();
}

function chipsDeFaltan(valores) {
  const mostrados = valores.slice(0, MAX_CHIPS);
  let html = mostrados
    .map((c) => '<span class="chip falta" title="' + descripcionRiesgo(c) + '">' + nombreRiesgo(c) + "</span>")
    .join("");
  if (valores.length > mostrados.length) html += '<span class="nota">… y ' + (valores.length - mostrados.length) + " más</span>";
  return html;
}

function dibujarPaso(res, k, conj) {
  const m = totalPasos();
  const pasos = datosMetodo(res).pasos;
  const faltan = [];
  for (let c = 1; c <= res.r; c++) if (!conj.despues.has(c)) faltan.push(c);

  $("#titulo-paso").textContent = k === 0 ? "Antes de empezar" : "Paso " + k + " de " + m;

  let frase, porQue, explicacion;
  if (k === 0) {
    frase = "Hay " + res.r + (res.r === 1 ? " riesgo por revisar" : " riesgos por revisar") + " y todavía no se auditó nada.";
    porQue = "Pulsa Reproducir o avanza con las flechas para ver cada decisión.";
    explicacion = introMetodo(res, estado.metodo);
  } else {
    const paso = pasos[k - 1];
    const nn = paso.nuevas.length;
    frase = "Se audita <span class='elegida'>" + nombreInteraccion(paso.j) + "</span>, que revisa " +
      "<span class='nuevos'>" + nn + (nn === 1 ? " riesgo nuevo" : " riesgos nuevos") + "</span>.";
    porQue = "";
    explicacion = razonEleccion(res, estado.metodo, k) + explicacionPaso(res, estado.metodo, k);
  }
  $("#explicacion-paso").innerHTML = explicacion;
  $("#frase-paso").innerHTML = frase;

  const filaNuevos = $("#fila-nuevos");
  const hayNuevos = k > 0 && conj.nuevos.size > 0;
  filaNuevos.classList.toggle("oculto", !hayNuevos);
  $("#chips-nuevos").innerHTML = [...conj.nuevos].sort((a, b) => a - b).map((c) => {
    const corto = nombreCorto(c);
    return '<span class="chip nuevo">+ ' + nombreRiesgo(c) + (corto ? "<small>" + corto + "</small>" : "") + "</span>";
  }).join("");

  $("#chips-faltan").innerHTML = faltan.length
    ? chipsDeFaltan(faltan)
    : '<span class="ok-texto">ninguno: todos los riesgos quedan revisados ✓</span>';

  $("#progreso-num").innerHTML = conj.despues.size + " <small>de " + res.r + "</small>";
  const barra = $("#barra-riesgos");
  barra.style.gridTemplateColumns = "repeat(" + res.r + ", minmax(0, 1fr))";
  let celdas = "";
  for (let c = 1; c <= res.r; c++) {
    celdas += '<span class="celda ' + (conj.nuevos.has(c) ? "c-nuevo" : conj.despues.has(c) ? "c-cubierto" : "c-pendiente") + '"></span>';
  }
  barra.innerHTML = celdas;
  $("#por-que").textContent = porQue;
}

function dibujarHitos(res, k) {
  const pasos = datosMetodo(res).pasos;
  const m = pasos.length;
  let html = "";
  for (let i = 0; i <= m; i++) {
    const clase = i === k ? "ahora" : i < k ? "hecho" : "";
    const aria = i === 0 ? "Ir al inicio" : "Ir al paso " + i + ", " + nombreInteraccion(pasos[i - 1].j);
    html += '<button type="button" class="btn hito ' + clase + '" data-paso="' + i + '" aria-label="' + aria + '">' +
      "<small>" + (i === 0 ? "Inicio" : "Paso " + i) + "</small>" +
      "<b>" + (i === 0 ? "0 / " + res.r : nombreInteraccion(pasos[i - 1].j)) + "</b></button>";
  }
  $("#hitos").innerHTML = html;
}

/* ------------------------------ matriz --------------------------------- */

function dibujarMatriz(res, k, conj) {
  const n = res.n;
  const r = res.r;
  const dm = datosMetodo(res);
  const paso = k >= 1 ? dm.pasos[k - 1] : null;
  const elegidasHasta = dm.J.slice(0, k);
  const cs = r <= 12 ? 40 : r <= 20 ? 34 : 28;
  const ancho = res.ids_categoria ? Math.max(cs, 38) : cs;
  const columnas = "138px repeat(" + r + ", " + ancho + "px)";

  let html = '<div class="matriz">';
  html += '<div class="m-fila m-cab" role="row" style="grid-template-columns: ' + columnas + '">' +
    '<span class="m-esquina" role="columnheader">interacción</span>';
  for (let c = 1; c <= r; c++) {
    const clase = conj.nuevos.has(c) ? "nuevo" : conj.despues.has(c) ? "cubierto" : "pendiente";
    html += '<span class="m-col ' + clase + '" role="columnheader" title="riesgo ' + descripcionRiesgo(c) + '">' +
      nombreRiesgo(c) + "</span>";
  }
  html += "</div>";

  for (let j = 1; j <= n; j++) {
    const marcada = elegidasHasta.includes(j);
    const actual = paso && paso.j === j;
    html += '<div class="m-fila' + (actual ? " fila-actual" : "") + '" role="row" style="grid-template-columns: ' + columnas + '">' +
      '<span class="m-id" role="rowheader" title="interacción ' + nombreInteraccion(j) + (marcada ? " (se audita)" : "") + '">' +
      '<span class="marca-ok">' + (marcada ? "✓" : "") + "</span>" + nombreInteraccion(j) +
      (actual ? '<span class="etiqueta">paso ' + k + "</span>" : "") + "</span>";
    const fila = res.S[j - 1];
    for (let c = 1; c <= r; c++) {
      const base = "la interacción " + nombreInteraccion(j) + " ";
      if (!fila.includes(c)) {
        html += '<span class="celda c-vacio" role="cell" style="height:' + cs + 'px" aria-label="' + base +
          "no revisa " + descripcionRiesgo(c) + '"></span>';
      } else if (actual && conj.nuevos.has(c)) {
        html += '<span class="celda c-nuevo" role="cell" style="height:' + cs + 'px" aria-label="' +
          descripcionRiesgo(c) + ' se revisa en este paso">+</span>';
      } else if (conj.despues.has(c)) {
        html += '<span class="celda c-cubierto" role="cell" style="height:' + cs + 'px" aria-label="' +
          descripcionRiesgo(c) + ' ya revisado"></span>';
      } else {
        html += '<span class="celda c-pendiente" role="cell" style="height:' + cs + 'px" aria-label="' +
          descripcionRiesgo(c) + ' pendiente">·</span>';
      }
    }
    html += "</div>";
  }
  html += "</div>";
  $("#zona-matriz").innerHTML = html;
}

function dibujarCobertura(res) {
  $("#tabla-cobertura").innerHTML = coberturaDe(datosMetodo(res))
    .map((fila) =>
      '<span class="par-cobertura" title="' + descripcionRiesgo(fila.categoria) + '"><span class="r">' +
      nombreRiesgo(fila.categoria) + '</span><span class="f">→</span><span class="e">' +
      nombreInteraccion(fila.interaccion) + "</span></span>")
    .join("");
}

/* ------------------------------ controles ------------------------------ */

function reproducir() {
  detenerReproduccion();
  $("#btn-auto").textContent = "Pausar";
  estado.temporizador = setInterval(() => {
    if (!estado.res || estado.pos >= totalPasos()) {
      detenerReproduccion();
      return;
    }
    fijarPosicion(estado.pos + 1);
  }, VELOCIDAD_MS);
}

function detenerReproduccion() {
  if (estado.temporizador !== null) {
    clearInterval(estado.temporizador);
    estado.temporizador = null;
  }
  $("#btn-auto").textContent = "Reproducir";
}

/* ------------------------------ pestañas ------------------------------- */

function activarTab(nombre) {
  document.querySelectorAll("#tabs .tab").forEach((t) => {
    const activa = t.dataset.tab === nombre;
    t.classList.toggle("activa", activa);
    t.setAttribute("aria-selected", activa ? "true" : "false");
  });
  $("#tab-archivo").classList.toggle("oculto", nombre !== "archivo");
  $("#tab-manual").classList.toggle("oculto", nombre !== "manual");
  $("#tab-pegar").classList.toggle("oculto", nombre !== "pegar");
}

/* ------------------------------ subir archivo -------------------------- */

function elegirArchivo(archivo) {
  /* Lee el archivo en el navegador; el análisis lo hace el servidor con el lector del proyecto. */
  ocultarError();
  if (!archivo) return;
  if (!/\.(json|txt)$/i.test(archivo.name)) {
    mostrarError("El archivo debe ser .json o .txt.");
    return;
  }
  const lector = new FileReader();
  lector.onload = () => {
    estado.archivo = {
      nombre: archivo.name.replace(/\.[^.]+$/, ""),
      completo: archivo.name,
      texto: String(lector.result),
    };
    $("#texto-archivo").textContent = archivo.name + " (" + Math.max(1, Math.round(archivo.size / 1024)) + " KB)";
    $("#zona-archivo").classList.add("con-archivo");
    previsualizar(estado.archivo.texto, estado.archivo.nombre);
  };
  lector.onerror = () => mostrarError("No se pudo leer el archivo.");
  lector.readAsText(archivo, "utf-8");
}

/* ------------------------------ eventos -------------------------------- */

$("#direccion").textContent = location.host || "127.0.0.1";

document.querySelectorAll("#tabs .tab").forEach((t) => {
  t.addEventListener("click", () => activarTab(t.dataset.tab));
});

$("#entrada-archivo").addEventListener("change", (e) => elegirArchivo(e.target.files[0]));

const zonaArchivo = $("#zona-archivo");
["dragenter", "dragover"].forEach((ev) =>
  zonaArchivo.addEventListener(ev, (e) => { e.preventDefault(); zonaArchivo.classList.add("arrastrando"); }));
["dragleave", "drop"].forEach((ev) =>
  zonaArchivo.addEventListener(ev, (e) => { e.preventDefault(); zonaArchivo.classList.remove("arrastrando"); }));
zonaArchivo.addEventListener("drop", (e) => elegirArchivo(e.dataTransfer.files[0]));

$("#btn-analizar-archivo").addEventListener("click", () => {
  if (!estado.archivo) return;
  analizar(estado.archivo.texto, estado.archivo.nombre, false);
});

$("#manual-r").addEventListener("change", generarFilas);
$("#manual-n").addEventListener("change", generarFilas);
$("#btn-generar-filas").addEventListener("click", generarFilas);

$("#filas-manuales").addEventListener("change", (e) => {
  if (!e.target.classList.contains("marca")) return;
  actualizarCuenta(e.target.closest(".fila-manual"));
  actualizarRevision();
  actualizarPrevisualizacion();
});

$("#filas-manuales").addEventListener("click", (e) => {
  const accion = e.target.closest(".mini");
  if (!accion) return;
  const fila = accion.closest(".fila-manual");
  const activar = accion.dataset.accion === "todos";
  fila.querySelectorAll(".marca").forEach((c) => { c.checked = activar; });
  actualizarCuenta(fila);
  actualizarRevision();
  actualizarPrevisualizacion();
});

$("#filas-manuales").addEventListener("input", (e) => {
  if (e.target.classList.contains("categorias-manuales")) {
    const fila = e.target.closest(".fila-manual");
    validarTokensDeFila(fila);
    actualizarCuenta(fila);
    actualizarRevision();
    actualizarPrevisualizacion();
  }
});

$("#btn-analizar").addEventListener("click", () => {
  if (!validarFormulario()) return;
  analizar(textoDelFormulario(), "caso_creado", true);
});

$("#btn-resolver-texto").addEventListener("click", () => {
  const texto = $("#entrada-texto").value;
  if (!texto.trim()) {
    mostrarError("Pega primero el contenido del caso.");
    return;
  }
  analizar(texto, "caso_de_texto", false);
});

$("#btn-inicio").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(0); });
$("#btn-anterior").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(estado.pos - 1); });
$("#btn-siguiente").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(estado.pos + 1); });
$("#btn-final").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(totalPasos()); });
$("#btn-auto").addEventListener("click", () => {
  if (!estado.res || !estado.res.factible) return;
  if (estado.temporizador !== null) detenerReproduccion();
  else {
    if (estado.pos >= totalPasos()) fijarPosicion(0);
    reproducir();
  }
});
$("#hitos").addEventListener("click", (e) => {
  const boton = e.target.closest(".hito");
  if (!boton) return;
  detenerReproduccion();
  fijarPosicion(parseInt(boton.dataset.paso, 10));
});
$("#slider-paso").addEventListener("input", (e) => {
  detenerReproduccion();
  fijarPosicion(parseInt(e.target.value, 10));
});

document.addEventListener("keydown", (e) => {
  if (!estado.res || !estado.res.factible) return;
  if (["TEXTAREA", "INPUT", "SELECT"].includes(e.target.tagName)) return;
  if (e.key === "ArrowLeft") { detenerReproduccion(); fijarPosicion(estado.pos - 1); }
  if (e.key === "ArrowRight") { detenerReproduccion(); fijarPosicion(estado.pos + 1); }
});

generarFilas();
