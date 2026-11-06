"use strict";

/* Visor de la Parte 1 (programación dinámica, Mochila 0/1). Toda la lógica del problema vive en el
   código del proyecto (src/aceleracion), invocada desde el servidor local: aquí solo se arma el caso,
   se pide el análisis y se dibuja la tabla y la reconstrucción paso a paso. */

const $ = (sel) => document.querySelector(sel);
const todasLasFilas = () => [...document.querySelectorAll(".fila-etapa")];

const MAX_ETAPAS_HITOS = 60;   // con más pasos que esto no se dibujan los botones de cada paso

const estado = {
  res: null,          // resultado que muestra la simulación paso a paso (la tabla y el recorrido)
  resTop: null,       // resultado que muestran las tarjetas de arriba (resumen, costo, fuerza bruta); es independiente de la simulación
  cache: {},          // resultados ya pedidos del caso actual, por enfoque
  pos: 0,             // paso actual: 0 = inicio; luego una fila por etapa; luego una decisión por etapa
  celda: null,        // celda de la tabla tocada por la persona: { i, b }
  temporizador: null,
  archivo: null,      // { nombre, completo, texto } del archivo elegido en "Subir archivo"
  ultimo: null,       // { texto, nombre } del último caso analizado (para cambiar de enfoque sin volver a cargarlo)
};

/* ------------------------- utilidades ---------------------------------- */

/* Los nombres vienen del archivo y se insertan como HTML: se escapan siempre. */
function esc(texto) {
  return String(texto).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const num = (x) => Number(x).toLocaleString("es-CO");
const coma = (x, dec) => Number(x).toFixed(dec).replace(".", ",");
const msTexto = (x) => coma(x * 1000, 3) + " ms";
const fmt = (x) => (x === Infinity ? "∞" : x);                       // valor de una celda; ∞ = no se puede
const inf = (x) => (x === null ? Infinity : x);                       // el servidor manda null donde hay ∞

/* Enfoque con el que se resolvió el caso: "presupuesto" (tabla base, columnas = presupuesto b) o
   "valor" (columnas = ahorro v; cada celda guarda el menor costo). */
const esValor = () => estado.res.enfoque === "valor";
const anchoTabla = (res) => (res.enfoque === "valor" ? res.D : res.B);

/* "E03" si el caso trae ids; si no, el número de la etapa. `fuente` es el resultado o la vista previa. */
function nombreEtapa(i, fuente) {
  const f = fuente || estado.res;
  return esc(f && f.ids ? f.ids[i - 1] : i);
}

const ICONO_ALERTA =
  '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16v.5"/></svg>';
const ICONO_OK =
  '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>';

/* ------------------------- armado del caso (formulario) ---------------- */

const EJEMPLO = [[10, 5, 6], [8, 4, 5], [7, 3, 4], [9, 6, 7], [6, 2, 3]];   // [t, c, d] de las primeras filas

const idManual = (i) => "E" + String(i).padStart(2, "0");
const entero = (s) => /^\d+$/.test(String(s).trim());

function datosFilas() {
  return todasLasFilas().map((f) => ({
    t: f.querySelector('[data-k="t"]').value,
    c: f.querySelector('[data-k="c"]').value,
    d: f.querySelector('[data-k="d"]').value,
  }));
}

function crearFila(i, v) {
  const fila = document.createElement("div");
  fila.className = "fila-manual fila-etapa";
  fila.dataset.i = i;
  fila.innerHTML =
    '<div class="encabezado-fila"><span class="rotulo-fila">' + idManual(i) + "</span></div>" +
    '<div class="campos-etapa">' +
    '<label>Dura (t)<input type="number" min="0" step="1" data-k="t" value="' + esc(v.t) + '"></label>' +
    '<label>Cuesta acelerarla (c)<input type="number" min="0" step="1" data-k="c" value="' + esc(v.c) + '"></label>' +
    '<label>Ahorra (d)<input type="number" min="0" step="1" data-k="d" value="' + esc(v.d) + '"></label>' +
    "</div>";
  return fila;
}

function generarFilas() {
  const n = Math.max(1, Math.min(200, parseInt($("#manual-n").value, 10) || 1));
  $("#manual-n").value = n;
  const previos = datosFilas();
  const contenedor = $("#filas-manuales");
  contenedor.innerHTML = "";
  for (let i = 1; i <= n; i++) {
    let v = previos[i - 1];
    if (!v) {
      const e = previos.length === 0 && EJEMPLO[i - 1];
      v = e ? { t: e[0], c: e[1], d: e[2] } : { t: "", c: "", d: "" };
    }
    contenedor.appendChild(crearFila(i, v));
  }
  actualizarRevision();
}

/* Revisa el formulario. Devuelve la lista de problemas (vacía si todo está bien) y marca las filas con error. */
function problemasDelFormulario() {
  const problemas = [];
  if (!entero($("#manual-B").value)) problemas.push("El presupuesto B debe ser un entero de 0 o más.");
  todasLasFilas().forEach((f) => {
    const t = f.querySelector('[data-k="t"]').value, c = f.querySelector('[data-k="c"]').value;
    const d = f.querySelector('[data-k="d"]').value;
    let msg = "";
    if (![t, c, d].every(entero)) msg = idManual(f.dataset.i) + ": completa la duración, el costo y el ahorro con enteros de 0 o más.";
    else if (parseInt(d, 10) > parseInt(t, 10)) msg = idManual(f.dataset.i) + ": el ahorro (" + d + ") no puede superar la duración (" + t + ").";
    f.classList.toggle("error", msg !== "");
    if (msg) problemas.push(msg);
  });
  return problemas;
}

function actualizarRevision() {
  const caja = $("#estado-revision");
  const problemas = problemasDelFormulario();
  if (problemas.length) {
    caja.className = "estado-cobertura aviso";
    caja.textContent = problemas[0] + (problemas.length > 1 ? " (y " + (problemas.length - 1) + " más)" : "");
  } else {
    const filas = datosFilas();
    const sc = filas.reduce((a, f) => a + parseInt(f.c, 10), 0);
    const sd = filas.reduce((a, f) => a + parseInt(f.d, 10), 0);
    caja.className = "estado-cobertura ok";
    caja.textContent = "Todo listo: " + filas.length + " etapas · costo de acelerarlas todas = " + sc +
      " · ahorro máximo posible = " + sd + " · presupuesto B = " + parseInt($("#manual-B").value, 10) + ".";
  }
  actualizarPrevisualizacion();
}

function textoDelFormulario() {
  const filas = datosFilas();
  const caso = {
    parametros: { presupuesto_aceleracion_B: parseInt($("#manual-B").value, 10) || 0, numero_etapas: filas.length },
    etapas: filas.map((f, k) => ({
      id: idManual(k + 1),
      duracion_normal: parseInt(f.t, 10) || 0,
      costo_aceleracion: parseInt(f.c, 10) || 0,
      reduccion_tiempo_si_acelera: parseInt(f.d, 10) || 0,
    })),
  };
  return JSON.stringify(caso, null, 2);
}

function actualizarPrevisualizacion() {
  $("#texto-previsualizacion").textContent = textoDelFormulario();
}

/* ------------------------- pedidos al servidor ------------------------- */

async function pedir(ruta, texto, nombre, enfoque) {
  /* Devuelve { ok, datos }; si no hay servidor, ok es false y datos trae el mensaje. */
  try {
    const respuesta = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: texto, nombre: nombre, enfoque: enfoque || "auto" }),
    });
    const datos = await respuesta.json();
    return { ok: respuesta.ok, datos: datos };
  } catch (e) {
    return { ok: false, datos: { error: "No se pudo contactar el servidor local. ¿Sigue corriendo?" } };
  }
}

function normalizar(datos) {
  /* El servidor manda null donde la tabla por valor tiene ∞. */
  if (datos.tabla) datos.tabla = datos.tabla.map((fila) => fila.map(inf));
  if (datos.enfoque === "valor") {
    datos.decisiones.forEach((d) => { d.valor = inf(d.valor); d.sin = inf(d.sin); d.con = inf(d.con); });
  }
  return datos;
}

async function analizar(texto, nombre) {
  /* Caso nuevo: se resuelve con el enfoque recomendado y se muestra igual arriba y en la simulación. */
  ocultarError();
  const { ok, datos } = await pedir("/api/aceleracion/resolver", texto, nombre, "auto");
  if (!ok) {
    mostrarError(datos.error || "Error desconocido del servidor.");
    return;
  }
  detenerReproduccion();
  normalizar(datos);
  estado.ultimo = { texto: texto, nombre: nombre };
  estado.cache = {};
  estado.cache[datos.enfoque] = datos;
  estado.res = datos;
  estado.resTop = datos;
  estado.pos = 0;
  estado.celda = null;
  dibujarSalida();
  $("#panel-resultado").scrollIntoView({ behavior: "smooth", block: "start" });
  reproducir();
}

async function obtener(enfoque) {
  /* Resultado del caso actual con ese enfoque (del caché, o pidiéndolo al servidor). null si falla. */
  if (estado.cache[enfoque]) return estado.cache[enfoque];
  const { ok, datos } = await pedir("/api/aceleracion/resolver", estado.ultimo.texto, estado.ultimo.nombre, enfoque);
  if (!ok) {
    mostrarError(datos.error || "Error desconocido del servidor.");
    return null;
  }
  estado.cache[enfoque] = normalizar(datos);
  return estado.cache[enfoque];
}

async function cambiarEnfoqueTop(enfoque) {
  /* Botones de arriba: cambian solo las tarjetas de resultado; la simulación no se toca. */
  const datos = await obtener(enfoque);
  if (!datos) return;
  ocultarError();
  estado.resTop = datos;
  dibujarTop();
}

async function cambiarEnfoqueSim(enfoque) {
  /* Botones de la simulación: cambian la tabla y el paso a paso; las tarjetas de arriba no se tocan. */
  const datos = await obtener(enfoque);
  if (!datos) return;
  ocultarError();
  detenerReproduccion();
  estado.res = datos;
  estado.pos = 0;
  estado.celda = null;
  dibujarSim();
  reproducir();
}

function mostrarError(mensaje) {
  $("#mensaje-error").textContent = mensaje;
  $("#banner-error").classList.remove("oculto");
}

function ocultarError() {
  $("#banner-error").classList.add("oculto");
}

/* ------------------- vista previa del archivo subido ------------------- */

async function previsualizar(texto, nombre) {
  /* Pide al servidor que lea el caso con el lector del proyecto (sin resolverlo). */
  $("#vista-previa").classList.add("oculto");
  $("#btn-analizar-archivo").disabled = true;
  const { ok, datos } = await pedir("/api/aceleracion/previsualizar", texto, nombre);
  if (!ok) {
    mostrarError(datos.error || "Error desconocido del servidor.");
    return;
  }
  dibujarVistaPrevia(datos);
  $("#btn-analizar-archivo").disabled = false;
}

function avisoTablas(f) {
  /* Cuántas celdas tendría cada tabla y cuál conviene (la de menos celdas, si cabe en memoria). */
  const texto = "Por presupuesto: <strong>" + num(f.celdas_presupuesto) + "</strong> celdas · por valor: <strong>" + num(f.celdas_valor) + "</strong> celdas. ";
  if (!f.recomendado) {
    return '<div class="aviso rojo" role="status">' + ICONO_ALERTA + "<span>" + texto + "<strong>Ninguna cabe en memoria</strong> (el límite es " +
      num(f.limite_celdas) + "): este caso es demasiado grande.</span></div>";
  }
  return '<div class="aviso ok">' + ICONO_OK + "<span>" + texto + "Conviene la tabla <strong>" +
    (f.recomendado === "valor" ? "por valor" : "por presupuesto") + "</strong> (la de menos celdas).</span></div>";
}

function dibujarVistaPrevia(info) {
  const n = info.n, B = info.B;
  const sumaT = info.t.reduce((a, x) => a + x, 0);
  const sumaC = info.c.reduce((a, x) => a + x, 0);
  const listar = (idx) => idx.map((i) => nombreEtapa(i, info)).join(", ");
  const todas = Array.from({ length: n }, (_, k) => k + 1);
  const nuncaCaben = todas.filter((i) => info.c[i - 1] > B);
  const sinAhorro = todas.filter((i) => info.d[i - 1] === 0);

  $("#vp-nombre").textContent = estado.archivo ? estado.archivo.completo : info.nombre;
  $("#vp-cifras").innerHTML =
    '<div class="cifra"><b>' + n + "</b><span>etapas</span></div>" +
    '<div class="cifra"><b>' + num(B) + "</b><span>presupuesto B</span></div>" +
    '<div class="cifra"><b>' + num(sumaT) + "</b><span>duración total</span></div>";

  let avisos = "";
  if (sumaC <= B) {
    avisos += '<div class="aviso ambar" role="status">' + ICONO_ALERTA + "<span><strong>El presupuesto alcanza para acelerarlo todo</strong> (costo total " +
      num(sumaC) + " ≤ B = " + num(B) + "). No hay nada que elegir.</span></div>";
  } else {
    avisos += '<div class="aviso ok">' + ICONO_OK + "<span>Acelerarlo todo costaría <strong>" + num(sumaC) +
      "</strong> y solo hay B = <strong>" + num(B) + "</strong>: hay que elegir qué etapas acelerar.</span></div>";
  }
  if (nuncaCaben.length) {
    avisos += '<div class="aviso ambar" role="status">' + ICONO_ALERTA + "<span><strong>" + listar(nuncaCaben) +
      (nuncaCaben.length === 1 ? " cuesta" : " cuestan") + " más que B:</strong> nunca se podrá acelerar.</span></div>";
  }
  if (sinAhorro.length) {
    avisos += '<div class="aviso ambar" role="status">' + ICONO_ALERTA + "<span><strong>" + listar(sinAhorro) +
      (sinAhorro.length === 1 ? " no ahorra" : " no ahorran") + " nada</strong> al acelerarse: no conviene.</span></div>";
  }
  avisos += avisoTablas(info);
  $("#vp-avisos").innerHTML = avisos;

  $("#vp-etapas").innerHTML = todas.map((i) =>
    "<li><span class='li-id'>" + nombreEtapa(i, info) + "</span><span class='li-texto'>dura " + info.t[i - 1] +
    " · cuesta " + info.c[i - 1] + " · ahorra " + info.d[i - 1] + "</span></li>").join("");

  const razon = (i) => (info.c[i - 1] === 0 ? (info.d[i - 1] > 0 ? Infinity : 0) : info.d[i - 1] / info.c[i - 1]);
  const orden = todas.slice().sort((a, b) => razon(b) - razon(a) || a - b);
  $("#vp-rendimiento").innerHTML = orden.map((i) => {
    const r = razon(i);
    const texto = r === Infinity ? "gratis y ahorra" : coma(r, 2) + " por unidad";
    return "<li><span class='li-id'>" + nombreEtapa(i, info) + "</span><span class='li-texto'>" + texto + "</span></li>";
  }).join("");

  $("#vista-previa").classList.remove("oculto");
}

/* ------------------------------ salida --------------------------------- */

function dibujarSalida() {
  $("#vacio").classList.add("oculto");
  $("#salida").classList.remove("oculto");
  dibujarTop();
  dibujarSim();
}

function dibujarTop() {
  /* Tarjetas de resultado (arriba): usan estado.resTop. */
  const res = estado.resTop;
  dibujarResumen(res);
  dibujarCosto(res);
  dibujarFuerzaBruta(res);
  marcarEnfoques("#enfoques-res", res);
  $("#nombre-enfoque-res").textContent = res.enfoque === "valor" ? "Por valor" : "Por presupuesto";
}

function dibujarSim() {
  /* Simulación paso a paso (abajo): usa estado.res. */
  const res = estado.res;
  dibujarSelectorEnfoque(res);
  $("#texto-evidencia").textContent = res.evidencia;
  $("#slider-paso").max = totalPasos();
  fijarPosicion(0);
}

function marcarEnfoques(selector, res) {
  /* Marca el botón del enfoque mostrado y deshabilita el que no cabe en memoria. */
  document.querySelectorAll(selector + " .btn-ing").forEach((b) => {
    const enf = b.dataset.enf;
    const activo = enf === res.enfoque;
    const celdas = enf === "valor" ? res.celdas_valor : res.celdas_presupuesto;
    b.classList.toggle("activo", activo);
    b.setAttribute("aria-pressed", activo ? "true" : "false");
    b.disabled = celdas > res.limite_celdas;
    b.title = b.disabled ? "Esta tabla no cabe en memoria (" + num(celdas) + " celdas)" : "";
  });
}

function dibujarSelectorEnfoque(res) {
  marcarEnfoques("#enfoques", res);
  $("#tamanos-tablas").textContent = "por presupuesto " + num(res.celdas_presupuesto) + " · por valor " + num(res.celdas_valor) +
    (res.recomendado ? " · conviene " + (res.recomendado === "valor" ? "por valor" : "por presupuesto") : "");
  const columnas = res.enfoque === "valor"
    ? "Filas: etapas · Columnas: ahorro que se quiere lograr · Cada celda: el menor costo para lograrlo (∞ si no se puede o pasa de B)"
    : "Filas: etapas · Columnas: presupuesto disponible · Cada celda: el mayor ahorro posible";
  $("#nota-tabla").textContent = columnas;
  $("#nota-enfoque").innerHTML = res.enfoque === "valor"
    ? "<b>Por valor.</b> La tabla se indexa por el <i>ahorro</i> v: cada celda guarda el <b>menor costo</b> para lograr exactamente ese ahorro. " +
      "Al final se toma el mayor ahorro cuyo costo cabe en B. Cuesta Θ(n·D), con D = Σ ahorros: no depende de B, así que sirve cuando B es muy grande."
    : "<b>Por presupuesto.</b> La tabla se indexa por el <i>presupuesto</i> b: cada celda guarda el <b>mayor ahorro</b> posible gastando a lo sumo b. " +
      "Cuesta Θ(n·B): sirve cuando B es moderado.";
}

function memoriaTabla(celdas) {
  /* Estimación: ~38 bytes por celda (medido en el peor caso de la DP). */
  const bytes = celdas * 38;
  return bytes >= 1e6 ? coma(bytes / 1e6, 1) + " MB" : num(Math.max(1, Math.round(bytes / 1e3))) + " KB";
}

function dibujarResumen(res) {
  const k = res.aceleradas.length;
  const ids = res.aceleradas.slice(0, 8).map((i) => nombreEtapa(i)).join(", ") + (k > 8 ? " …" : "");
  const fb = res.fuerza_bruta;
  const pieComprobacion = fb
    ? (fb.ahorro === res.ahorro ? "coincide con la fuerza bruta" : "NO coincide con la fuerza bruta (ahorro " + fb.ahorro + ")")
    : "la fuerza bruta solo se corre con n ≤ 12";
  $("#resumen").innerHTML =
    '<div class="stat destacada"><span class="clave">Etapas aceleradas</span><span class="grande">' + k +
    " <small>de " + res.n + '</small></span><span class="pie">' + (k ? ids : "ninguna") + "</span></div>" +
    '<div class="stat"><span class="clave">Presupuesto usado</span><span class="grande">' + num(res.costo) +
    " <small>de " + num(res.B) + '</small></span><span class="pie">sobran ' + num(res.B - res.costo) + "</span></div>" +
    '<div class="stat destacada"><span class="clave">Tiempo que se ahorra</span><span class="grande">' + num(res.ahorro) +
    '</span><span class="pie">es el máximo posible con ese presupuesto</span></div>' +
    '<div class="stat"><span class="clave">Duración final de la cadena</span><span class="grande">' + num(res.duracion_final) +
    '</span><span class="pie">antes: ' + num(res.duracion_original) + "</span></div>" +
    '<div class="stat"><span class="clave">Lo que tardó la DP</span><span class="medio">' + msTexto(res.tiempo_s) +
    '</span><span class="pie">solo el algoritmo</span></div>' +
    '<div class="stat"><span class="clave">Celdas de la tabla</span><span class="grande">' + num(res.celdas) +
    '</span><span class="pie">' + num(res.n + 1) + " filas × " + num(anchoTabla(res) + 1) + " columnas (" +
    (res.enfoque === "valor" ? "por valor" : "por presupuesto") + ") · ≈ " + memoriaTabla(res.celdas) +
    " en memoria · la otra tabla: " + num(res.enfoque === "valor" ? res.celdas_presupuesto : res.celdas_valor) + "</span></div>" +
    '<div class="stat ancha"><span class="clave">Comprobación</span><span class="texto">' +
    (res.valida ? "Solución válida" : "La solución NO es válida") + '</span><span class="pie">' + pieComprobacion + "</span></div>";
}

function dibujarCosto(res) {
  const n = res.n, B = res.B, D = res.D;
  const valor = res.enfoque === "valor";
  const ancho = valor ? D : B;
  const calculos = n * (ancho + 1);
  const memoria = memoriaTabla(res.celdas);
  const bits = ancho === 0 ? 1 : Math.ceil(Math.log2(ancho + 1));
  const sumaC = res.aceleradas.reduce((a, i) => a + res.c[i - 1], 0);
  const sumaD = res.aceleradas.reduce((a, i) => a + res.d[i - 1], 0);
  const lista = (v) => (res.aceleradas.length
    ? res.aceleradas.slice(0, 6).map((i) => v[i - 1]).join(" + ") + (res.aceleradas.length > 6 ? " + …" : "") + " = "
    : "");
  const letra = valor ? "D" : "B";
  const quien = valor ? "ahorro máximo posible D = Σ d_i = " + num(D) : "presupuesto B = " + num(B);
  $("#tarjeta-costo").innerHTML =
    "<h3>Costo total</h3>" +
    '<div class="cols-costo">' +
    '<div class="bloque-costo"><h4>Costo de la solución</h4>' +
    '<p class="ecuacion">Σ costos = ' + lista(res.c) + num(sumaC) + " ≤ B = " + num(B) + "</p>" +
    '<p class="ecuacion">Σ ahorros = ' + lista(res.d) + num(sumaD) + "</p>" +
    '<p class="ecuacion">Duración final = ' + num(res.duracion_original) + " − " + num(sumaD) + " = " + num(res.duracion_final) + "</p>" +
    "<p>Se acelera lo que más ahorra sin pasarse del presupuesto: ese es el trabajo del algoritmo.</p></div>" +
    '<div class="bloque-costo"><h4>Costo del algoritmo (' + (valor ? "por valor" : "por presupuesto") + ") con los números del caso</h4>" +
    '<p class="ecuacion">celdas de la tabla = (n+1)·(' + letra + "+1) = " + num(n + 1) + " · " + num(ancho + 1) + " = " + num(res.celdas) + "</p>" +
    '<p class="ecuacion">cálculos de celda = n·(' + letra + "+1) = " + num(calculos) + "</p>" +
    "<p><b>Por qué:</b> los dos ciclos recorren siempre toda la tabla, sin importar los datos, y cada celda cuesta un número constante de operaciones. " +
    "Por eso T = Θ(n·" + letra + ") en tiempo y en memoria (≈ " + memoria + " aquí).</p>" +
    "<p><b>Pseudo-polinomial:</b> n·" + letra + " es polinomial en el <i>valor</i> de " + letra + ", pero " + letra + " se escribe con solo " + bits +
    " bits. Con 10 bits más, la tabla sería unas 1.024 veces más grande.</p>" +
    "<p><b>Contra la otra tabla:</b> por presupuesto tendría " + num(res.celdas_presupuesto) + " celdas y por valor " + num(res.celdas_valor) +
    ". Entre las dos se paga Θ(n·mín(B, D)) (" + quien + ").</p></div>" +
    "</div>";
}

function dibujarFuerzaBruta(res) {
  const fb = res.fuerza_bruta;
  const caja = $("#tarjeta-fb");
  if (!fb) {
    const total = Math.pow(2, res.n);
    caja.innerHTML = "<h3>Comprobación por fuerza bruta</h3>" +
      '<p class="nota">No se ejecuta: con ' + res.n + " etapas habría que probar 2<sup>" + res.n + "</sup> = " +
      (total < 1e15 ? num(total) : "una cantidad enorme de") + " subconjuntos. Solo se corre con n ≤ 12.</p>";
    return;
  }
  const igual = fb.ahorro === res.ahorro;
  caja.innerHTML =
    "<h3>Comprobación por fuerza bruta</h3>" +
    '<p class="nota">Prueba todos los subconjuntos de etapas que se podrían acelerar y se queda con el que más ahorra sin pasarse de B. ' +
    "Es lenta, pero encuentra el máximo real: sirve para comprobar a la programación dinámica.</p>" +
    '<div class="resumen-fb">' +
    "<span>Probó <b>" + num(fb.subconjuntos) + "</b> subconjuntos (2<sup>" + res.n + "</sup>)</span>" +
    "<span>Mejor ahorro: <b>" + num(fb.ahorro) + "</b></span>" +
    "<span>Tardó <b>" + msTexto(fb.tiempo_s) + "</b> (la DP: " + msTexto(res.tiempo_s) + ")</span>" +
    "<span>" + (igual ? "La DP acertó: ahorra lo mismo (" + num(res.ahorro) + ")" : "La DP ahorra " + num(res.ahorro) + " y el máximo real es " + num(fb.ahorro)) + "</span></div>";
}

/* ------------------------------ pasos ---------------------------------- */

/* Con tabla dibujable hay un paso por fila y luego uno por decisión; sin tabla, solo las decisiones. */
const pasosLlenar = () => (estado.res.tabla ? estado.res.n : 0);
const totalPasos = () => pasosLlenar() + estado.res.n;

function faseDe(p) {
  const L = pasosLlenar();
  if (p === 0) return { fase: "inicio" };
  if (p <= L) return { fase: "llenar", i: p };
  const m = p - L;
  return { fase: "decidir", m: m, dec: estado.res.decisiones[m - 1] };
}

/* Filas de la tabla ya calculadas en el paso p. */
function filasCalculadas(f) {
  if (f.fase === "inicio") return 0;
  if (f.fase === "llenar") return f.i;
  return estado.res.n;
}

function fijarPosicion(pos, centrar) {
  const res = estado.res;
  if (!res) return;
  estado.pos = Math.max(0, Math.min(pos, totalPasos()));
  $("#slider-paso").value = estado.pos;
  const f = faseDe(estado.pos);
  dibujarPaso(f);
  dibujarHitos();
  dibujarTabla(f, centrar !== false);
  dibujarCadena(f);
  const final = estado.pos === totalPasos();
  $("#solucion-final").classList.toggle("oculto", !final);
  if (final) {
    dibujarSolucion();
    detenerReproduccion();
  }
}

function dibujarPaso(f) {
  const res = estado.res, total = totalPasos(), valor = esValor();
  $("#titulo-paso").textContent = f.fase === "inicio" ? "Inicio" : "Paso " + estado.pos + " de " + total;
  const elegida = (i) => '<span class="elegida">' + nombreEtapa(i) + "</span>";
  const FORMULA_P = "DP[i][b] = máx( DP[i−1][b] , d_i + DP[i−1][b−c_i] )";
  const FORMULA_V = "C[i][v] = mín( C[i−1][v] , c_i + C[i−1][v−d_i] )";
  let frase = "", expl = "", rotulo, numero, relleno, porQue;

  if (f.fase === "inicio") {
    if (res.tabla && !valor) {
      frase = "Empezamos con la fila 0: con <strong>0 etapas</strong> no se puede acelerar nada, así que el ahorro es 0 con cualquier presupuesto.";
      expl = "<p>La tabla tiene una fila por etapa (de 0 a " + res.n + ") y una columna por presupuesto (de 0 a " + num(res.B) + "). " +
        "Cada celda guarda el <b>mayor ahorro posible</b> usando solo las primeras etapas y gastando a lo sumo ese presupuesto.</p>" +
        '<p class="formula">' + FORMULA_P + "</p>" +
        '<p class="pista">Primero se llena la tabla, fila por fila; después se recorre hacia atrás para saber qué etapas se aceleraron.</p>';
    } else if (res.tabla) {
      frase = "Empezamos con la fila 0: con <strong>0 etapas</strong> solo se logra el ahorro 0, y cuesta 0. Cualquier otro ahorro es imposible (∞).";
      expl = "<p>La tabla tiene una fila por etapa (de 0 a " + res.n + ") y una columna por ahorro (de 0 a " + num(res.D) + "). " +
        "Cada celda guarda el <b>menor costo</b> para lograr exactamente ese ahorro con las primeras etapas; ∞ si no se puede o si pasa de B = " + num(res.B) + ".</p>" +
        '<p class="formula">' + FORMULA_V + "</p>" +
        '<p class="pista">Primero se llena la tabla; después se toma el mayor ahorro cuyo costo cabe en B y se recorre hacia atrás.</p>';
    } else {
      frase = "La tabla es demasiado grande para dibujarla, pero el algoritmo sí la calculó. Aquí se ve la <strong>reconstrucción</strong>.";
      expl = "<p>La tabla tiene " + num(res.celdas) + " celdas. Para no saturar la página solo se muestran las decisiones, " +
        "de la última etapa a la primera.</p>";
    }
    rotulo = res.tabla ? "Filas calculadas" : "Etapas decididas";
    numero = "0 <small>de " + res.n + "</small>";
    relleno = 0;
    porQue = res.tabla ? "Cada fila se calcula usando solo la fila anterior." : "Se empieza por la última etapa.";
  } else if (f.fase === "llenar") {
    const i = f.i, T = res.tabla, W = anchoTabla(res);
    const c = res.c[i - 1], d = res.d[i - 1], t = res.t[i - 1];
    let aparte = 0, igual = 0, mejora = 0;
    for (let b = 0; b <= W; b++) {
      if (valor) {
        if (b < d) aparte++;
        else if (T[i][b] < T[i - 1][b]) mejora++;
        else igual++;
      } else if (c > b) aparte++;
      else if (T[i][b] > T[i - 1][b]) mejora++;
      else igual++;
    }
    frase = "Llenamos la fila de " + elegida(i) + ": dura <strong>" + t + "</strong>, cuesta <strong>" + c +
      "</strong> acelerarla y ahorra <strong>" + d + "</strong>.";
    if (valor) {
      expl = '<p class="formula">C[' + i + "][v] = mín( C[" + (i - 1) + "][v] , " + c + " + C[" + (i - 1) + "][v−" + d + "] )</p>" +
        "<p>En cada una de las " + num(W + 1) + " celdas se pregunta: ¿cuál es el menor costo para lograr <i>exactamente</i> este ahorro?</p><ul>" +
        "<li><b>" + num(aparte) + "</b> celdas: este ahorro es menor que lo que ahorra la etapa (" + d + ") → no se puede usar; se copia lo de arriba.</li>" +
        "<li><b>" + num(igual) + "</b> celdas: se puede usar, pero no sale más barato (o pasa de B) → igual que arriba.</li>" +
        "<li><b>" + num(mejora) + "</b> celdas: acelerarla logra ese ahorro más barato, o lo hace posible → celda verde.</li></ul>";
    } else {
      expl = '<p class="formula">DP[' + i + "][b] = máx( DP[" + (i - 1) + "][b] , " + d + " + DP[" + (i - 1) + "][b−" + c + "] )</p>" +
        "<p>En cada una de las " + num(W + 1) + " celdas se pregunta lo mismo: ¿conviene acelerar esta etapa?</p><ul>" +
        "<li><b>" + num(aparte) + "</b> celdas: no cabe (cuesta " + c + " y hay menos) → se copia lo de arriba.</li>" +
        "<li><b>" + num(igual) + "</b> celdas: cabe, pero acelerarla no mejora el ahorro → igual que arriba.</li>" +
        "<li><b>" + num(mejora) + "</b> celdas: acelerarla ahorra más → celda verde.</li></ul>";
    }
    rotulo = "Filas calculadas";
    numero = i + " <small>de " + res.n + "</small>";
    relleno = i / res.n;
    porQue = "Cada fila usa solo la fila anterior; por eso cada etapa se acelera a lo sumo una vez.";
  } else {
    const dec = f.dec;
    const c = res.c[dec.i - 1], d = res.d[dec.i - 1];
    if (valor) {
      const arranque = f.m === 1
        ? "<p>Se parte del <b>mayor ahorro que cabe en B = " + num(res.B) + "</b>: " + num(res.ahorro) + " (lograrlo cuesta " + num(res.costo) + ").</p>"
        : "";
      if (dec.acelerada) {
        frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>se acelera</strong>.";
        expl = arranque + "<p>Con <b>" + num(dec.b) + "</b> de ahorro por lograr, la tabla dice que cuesta C[" + dec.i + "][" + dec.b + "] = <b>" + fmt(dec.valor) +
          "</b>. Sin esta etapa costaría C[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + fmt(dec.sin) + "</b>.</p>" +
          "<p>Como <b>" + fmt(dec.valor) + " ≠ " + fmt(dec.sin) + "</b>, el mínimo viene de acelerarla.</p>" +
          '<p class="razon">Se ahorran ' + d + " (faltan por lograr " + num(dec.b_despues) + ") y se pagan " + c + ".</p>";
      } else {
        frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>no se acelera</strong>.";
        expl = arranque + "<p>Con <b>" + num(dec.b) + "</b> de ahorro por lograr, la tabla dice que cuesta C[" + dec.i + "][" + dec.b + "] = <b>" + fmt(dec.valor) +
          "</b>, y sin esta etapa también cuesta C[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + fmt(dec.sin) + "</b>.</p>" +
          '<p class="razon">Son iguales: acelerarla no abarata nada. No se acelera y el ahorro por lograr sigue en ' + num(dec.b) + ".</p>";
      }
      rotulo = "Ahorro asegurado";
      numero = num(res.ahorro - dec.b_despues) + " <small>de " + num(res.ahorro) + "</small>";
      relleno = res.ahorro > 0 ? (res.ahorro - dec.b_despues) / res.ahorro : 1;
      porQue = "Se parte del ahorro final y se resta lo que ahorra cada etapa elegida, hasta llegar a 0.";
    } else if (dec.acelerada) {
      frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>se acelera</strong>.";
      expl = "<p>Con <b>" + num(dec.b) + "</b> de presupuesto restante, la tabla dice DP[" + dec.i + "][" + dec.b + "] = <b>" + dec.valor +
        "</b>. Sin acelerar esta etapa solo se lograría DP[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + dec.sin + "</b>.</p>" +
        "<p>Como <b>" + dec.valor + " ≠ " + dec.sin + "</b>, el máximo viene de acelerarla.</p>" +
        '<p class="razon">Se pagan ' + c + " (el presupuesto restante pasa de " + num(dec.b) + " a " + num(dec.b_despues) +
        ") y se ahorran " + d + ".</p>";
      rotulo = "Presupuesto gastado";
      numero = num(res.B - dec.b_despues) + " <small>de " + num(res.B) + "</small>";
      relleno = res.B > 0 ? (res.B - dec.b_despues) / res.B : 0;
      porQue = "Se empieza con todo el presupuesto y se resta lo que cuesta cada etapa que se acelera.";
    } else {
      frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>no se acelera</strong>.";
      expl = "<p>Con <b>" + num(dec.b) + "</b> de presupuesto restante, la tabla dice DP[" + dec.i + "][" + dec.b + "] = <b>" + dec.valor +
        "</b>, y sin acelerar esta etapa también se logra DP[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + dec.sin + "</b>.</p>" +
        '<p class="razon">Son iguales: acelerarla no aporta nada. No se gasta presupuesto (sigue en ' + num(dec.b) + ").</p>";
      rotulo = "Presupuesto gastado";
      numero = num(res.B - dec.b_despues) + " <small>de " + num(res.B) + "</small>";
      relleno = res.B > 0 ? (res.B - dec.b_despues) / res.B : 0;
      porQue = "Se empieza con todo el presupuesto y se resta lo que cuesta cada etapa que se acelera.";
    }
  }

  $("#frase-paso").innerHTML = frase;
  $("#explicacion-paso").innerHTML = expl + detalleCelda(f);
  $("#progreso-rotulo").textContent = rotulo;
  $("#progreso-num").innerHTML = numero;
  $("#barra-relleno").style.width = Math.round(relleno * 100) + "%";
  $("#por-que").textContent = porQue;
}

/* Cómo se calculó la celda que tocó la persona. */
function detalleCelda(f) {
  const res = estado.res, sel = estado.celda;
  if (!res.tabla) return "";
  if (!sel) return f.fase === "decidir" ? "" : '<p class="pista">Toca cualquier celda de la tabla para ver cómo se calculó.</p>';
  const { i, b } = sel, T = res.tabla, valor = esValor();
  const pref = valor ? "C" : "DP";
  const cab = "Celda <b>" + pref + "[" + i + "][" + b + "]</b>";
  if (i > filasCalculadas(f)) {
    return '<div class="detalle-celda">' + cab + ": la fila de " + nombreEtapa(i) + " todavía no se calcula.</div>";
  }
  if (i === 0) {
    return '<div class="detalle-celda">' + cab + (valor
      ? (b === 0 ? ": con 0 etapas se logra el ahorro 0 con costo <b>0</b>." : ": con 0 etapas no se puede lograr un ahorro de " + b + " → <b>∞</b>.")
      : ": con 0 etapas no se puede acelerar nada → ahorro <b>0</b>.") + "</div>";
  }
  const c = res.c[i - 1], d = res.d[i - 1], v = T[i][b], sin = T[i - 1][b];
  const et = nombreEtapa(i);
  if (valor) {
    if (b < d) {
      return '<div class="detalle-celda">' + cab + ": " + et + " ahorra " + d + " y aquí se pide exactamente " + b +
        " → no se puede usar. Se copia " + pref + "[" + (i - 1) + "][" + b + "] = <b>" + fmt(v) + "</b>.</div>";
    }
    const resto = T[i - 1][b - d], con = resto + c;
    const conTxt = resto === Infinity ? "∞ (no se puede lograr " + (b - d) + " antes)" : (con > res.B ? con + " → pasa de B, cuenta como ∞" : con);
    const gana = v < sin ? "gana acelerarla" : "gana no acelerarla (o empatan)";
    return '<div class="detalle-celda">' + cab + " (etapa " + et + ", ahorro " + b + ")" +
      "<br>Sin acelerar: " + pref + "[" + (i - 1) + "][" + b + "] = <b>" + fmt(sin) + "</b>" +
      "<br>Acelerando (ahorra " + d + ", falta " + (b - d) + "): " + c + " + " + pref + "[" + (i - 1) + "][" + (b - d) + "] = <b>" + conTxt + "</b>" +
      "<br>El menor es <b>" + fmt(v) + "</b> (" + gana + ").</div>";
  }
  if (c > b) {
    return '<div class="detalle-celda">' + cab + ": acelerar " + et + " cuesta " + c + " y solo hay " + b +
      " → no cabe. Se copia DP[" + (i - 1) + "][" + b + "] = <b>" + v + "</b>.</div>";
  }
  const resto = T[i - 1][b - c], con = d + resto;
  const gana = con > sin ? "gana acelerarla" : (con === sin ? "empatan: se deja sin acelerar" : "gana no acelerarla");
  return '<div class="detalle-celda">' + cab + " (etapa " + et + ", presupuesto " + b + ")" +
    "<br>Sin acelerar: DP[" + (i - 1) + "][" + b + "] = <b>" + sin + "</b>" +
    "<br>Acelerando (cuesta " + c + ", queda " + (b - c) + "): " + d + " + DP[" + (i - 1) + "][" + (b - c) + "] = " + d + " + " + resto + " = <b>" + con + "</b>" +
    "<br>El mayor es <b>" + v + "</b> (" + gana + ").</div>";
}

function dibujarHitos() {
  const total = totalPasos(), res = estado.res;
  if (total > MAX_ETAPAS_HITOS) {
    $("#hitos").innerHTML = "";
    return;
  }
  let html = "";
  for (let k = 0; k <= total; k++) {
    const f = faseDe(k);
    const clase = k === estado.pos ? "ahora" : k < estado.pos ? "hecho" : "";
    const nombre = f.fase === "inicio" ? "0" : nombreEtapa(f.fase === "llenar" ? f.i : f.dec.i);
    const rotulo = f.fase === "inicio" ? "Inicio" : f.fase === "llenar" ? "Llenar" : "Decidir";
    html += '<button type="button" class="btn hito ' + clase + '" data-paso="' + k + '" aria-label="Ir al paso ' + k + '">' +
      "<small>" + rotulo + "</small><b>" + nombre + "</b></button>";
  }
  $("#hitos").innerHTML = html;
}

/* ------------------------------ la tabla ------------------------------- */

function dibujarTabla(f, centrar) {
  const res = estado.res, zona = $("#zona-tabla");
  if (!res.tabla) {
    zona.innerHTML = '<div class="sin-tabla">La tabla tiene ' + num(res.celdas) + " celdas (" + num(res.n + 1) + " filas × " +
      num(res.B + 1) + " columnas): demasiado grande para dibujarla. El algoritmo sí la calculó; mira a la izquierda las decisiones.</div>";
    return;
  }
  const T = res.tabla, valor = esValor(), B = anchoTabla(res), n = res.n, W = B + 1;
  const R = filasCalculadas(f);
  const sel = estado.celda;

  /* Camino de la solución y celda actual de la reconstrucción. */
  const camino = new Set();
  let ahora = -1, destino = -1;
  if (f.fase === "decidir") {
    for (let k = 0; k < f.m; k++) camino.add(res.decisiones[k].i * W + res.decisiones[k].b);
    ahora = f.dec.i * W + f.dec.b;
    destino = (f.dec.i - 1) * W + f.dec.b_despues;
    if (f.m === n) camino.add(destino);
  }
  /* Celdas de las que sale la celda tocada. */
  const origen = new Set();
  if (sel && sel.i >= 1 && sel.i <= R) {
    origen.add((sel.i - 1) * W + sel.b);
    const paso = valor ? res.d[sel.i - 1] : res.c[sel.i - 1];   // cuánto se retrocede en la fila de arriba
    if (paso <= sel.b) origen.add((sel.i - 1) * W + (sel.b - paso));
  }

  let html = '<div class="tabla-dp" style="grid-template-columns: 112px repeat(' + W + ', 46px)">' +
    '<div class="t-esquina">etapa ╲ ' + (valor ? "v" : "b") + "</div>";
  for (let b = 0; b <= B; b++) html += '<div class="t-cab">' + b + "</div>";
  for (let i = 0; i <= n; i++) {
    const actual = f.fase === "llenar" && i === f.i;
    html += '<div class="t-lab' + (actual ? " actual" : "") + '">i=' + i + "<small>" +
      (i === 0 ? "sin etapas" : nombreEtapa(i)) + "</small></div>";
    for (let b = 0; b <= B; b++) {
      const clave = i * W + b;
      let cls, txt, cls0 = "";
      if (i > R) { cls = "c-pendiente"; txt = "·"; }
      else {
        txt = fmt(T[i][b]);
        if (T[i][b] === Infinity) cls0 = " inf";
        const mejora = actual && (valor ? T[i][b] < T[i - 1][b] : T[i][b] > T[i - 1][b]);
        if (mejora) cls = "c-nuevo";
        else if (actual) cls = "c-igual";
        else cls = "c-cubierto";
      }
      if (camino.has(clave)) cls += " c-camino";
      if (clave === ahora) cls += " c-ahora";
      if (clave === destino) cls += " c-destino";
      if (origen.has(clave)) cls += " c-origen";
      if (sel && sel.i === i && sel.b === b) cls += " c-sel";
      html += '<div class="tcelda celda ' + cls + cls0 + '" data-i="' + i + '" data-b="' + b + '" role="cell">' + txt + "</div>";
    }
  }
  zona.innerHTML = html + "</div>";

  if (centrar) {
    const objetivo = f.fase === "llenar" ? zona.querySelector(".t-lab.actual") : zona.querySelector(".c-ahora");
    if (objetivo) {
      const z = zona.getBoundingClientRect(), o = objetivo.getBoundingClientRect();
      zona.scrollTop += o.top - z.top - zona.clientHeight / 2;
      if (f.fase === "decidir") zona.scrollLeft += o.left - z.left - zona.clientWidth / 2;
    }
  }
}

/* ------------------------- la cadena de etapas ------------------------- */

function dibujarCadena(f) {
  const res = estado.res;
  const decididas = new Map();
  if (f.fase === "decidir") for (let k = 0; k < f.m; k++) decididas.set(res.decisiones[k].i, res.decisiones[k].acelerada);
  const ahora = f.fase === "decidir" ? f.dec.i : -1;
  let html = "";
  for (let i = 1; i <= res.n; i++) {
    const t = res.t[i - 1], c = res.c[i - 1], d = res.d[i - 1];
    let cls = "pend", extra = "";
    if (decididas.has(i)) {
      cls = decididas.get(i) ? "acel" : "noacel";
      if (decididas.get(i)) extra = '<span class="linea">pasa a durar <b>' + (t - d) + "</b></span>";
    }
    html += '<div class="eta ' + cls + (i === ahora ? " ahora" : "") + '"><b>' + nombreEtapa(i) + "</b>" +
      '<span class="linea">dura ' + t + "</span>" +
      '<span class="linea">cuesta ' + c + " · ahorra " + d + "</span>" + extra + "</div>";
  }
  $("#cadena").innerHTML = html;
}

function dibujarSolucion() {
  const res = estado.res;
  $("#tabla-solucion").innerHTML = res.aceleradas.map((i) =>
    '<div class="par-cobertura"><span class="e">' + nombreEtapa(i) + '</span><span class="m">cuesta ' + res.c[i - 1] +
    " · ahorra " + res.d[i - 1] + "</span></div>").join("");
  $("#nota-solucion").textContent = res.aceleradas.length
    ? "Se gastan " + num(res.costo) + " de " + num(res.B) + " y se ahorran " + num(res.ahorro) + ": la cadena pasa de durar " +
      num(res.duracion_original) + " a durar " + num(res.duracion_final) + "."
    : "Ninguna etapa se acelera: con este presupuesto no hay ninguna que cuadre, y la cadena sigue durando " + num(res.duracion_original) + ".";
}

/* ------------------------------ controles ------------------------------ */

function reproducir() {
  detenerReproduccion();
  $("#btn-auto").textContent = "Pausar";
  const ms = estado.res && totalPasos() > 24 ? 600 : 1500;
  estado.temporizador = setInterval(() => {
    if (!estado.res || estado.pos >= totalPasos()) {
      detenerReproduccion();
      return;
    }
    fijarPosicion(estado.pos + 1);
  }, ms);
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
  if (!/\.json$/i.test(archivo.name)) {
    mostrarError("El archivo debe ser .json.");
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
  analizar(estado.archivo.texto, estado.archivo.nombre);
});

/* Dos selectores independientes: el de arriba cambia las tarjetas de resultado; el de la simulación, la tabla y el paso a paso. */
function elegirEnfoque(selector, actual, cambiar) {
  $(selector).addEventListener("click", (e) => {
    const boton = e.target.closest(".btn-ing");
    if (!boton || boton.disabled || !estado.res || !estado.ultimo || boton.dataset.enf === actual()) return;
    cambiar(boton.dataset.enf);
  });
}
elegirEnfoque("#enfoques-res", () => estado.resTop.enfoque, cambiarEnfoqueTop);
elegirEnfoque("#enfoques", () => estado.res.enfoque, cambiarEnfoqueSim);

$("#manual-n").addEventListener("change", generarFilas);
$("#manual-B").addEventListener("input", actualizarRevision);
$("#btn-generar-filas").addEventListener("click", generarFilas);
$("#filas-manuales").addEventListener("input", actualizarRevision);

$("#btn-analizar").addEventListener("click", () => {
  const problemas = problemasDelFormulario();
  if (problemas.length) {
    mostrarError(problemas.join(" "));
    return;
  }
  analizar(textoDelFormulario(), "caso_creado");
});

$("#btn-resolver-texto").addEventListener("click", () => {
  const texto = $("#entrada-texto").value;
  if (!texto.trim()) {
    mostrarError("Pega primero el contenido del caso.");
    return;
  }
  analizar(texto, "caso_de_texto");
});

$("#btn-inicio").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(0); });
$("#btn-anterior").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(estado.pos - 1); });
$("#btn-siguiente").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(estado.pos + 1); });
$("#btn-final").addEventListener("click", () => { detenerReproduccion(); fijarPosicion(totalPasos()); });
$("#btn-auto").addEventListener("click", () => {
  if (!estado.res) return;
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

/* Tocar una celda de la tabla explica cómo se calculó (y marca de dónde sale). */
$("#zona-tabla").addEventListener("click", (e) => {
  const celda = e.target.closest(".tcelda");
  if (!celda || celda.classList.contains("c-pendiente") || !estado.res) return;
  detenerReproduccion();
  const i = parseInt(celda.dataset.i, 10), b = parseInt(celda.dataset.b, 10);
  estado.celda = estado.celda && estado.celda.i === i && estado.celda.b === b ? null : { i: i, b: b };
  fijarPosicion(estado.pos, false);
});

document.addEventListener("keydown", (e) => {
  if (!estado.res) return;
  if (["TEXTAREA", "INPUT", "SELECT"].includes(e.target.tagName)) return;
  if (e.key === "ArrowLeft") { detenerReproduccion(); fijarPosicion(estado.pos - 1); }
  if (e.key === "ArrowRight") { detenerReproduccion(); fijarPosicion(estado.pos + 1); }
});

generarFilas();

/* Si se llega desde «Pruebas aleatorias» (/aleatorios), la dirección trae ?caso=NOMBRE: se pide ese caso al servidor
   y se resuelve con la misma función `analizar` que usa el resto de la página. */
(function cargarCasoDeLasPruebasAleatorias() {
  const nombre = new URLSearchParams(location.search).get("caso");
  if (!nombre) return;
  fetch("/api/aleatorios/caso?nombre=" + encodeURIComponent(nombre))
    .then((r) => r.json().then((d) => ({ ok: r.ok, d: d })))
    .then(({ ok, d }) => {
      if (!ok) { mostrarError(d.error || "No se encontró el caso " + nombre + " en las carpetas temporales."); return; }
      analizar(d.texto, nombre);
    })
    .catch(() => mostrarError("No se pudo contactar el servidor local. ¿Sigue corriendo?"));
})();
