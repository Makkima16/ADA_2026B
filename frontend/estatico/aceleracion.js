"use strict";

/* Visor de la Parte 1 (programación dinámica, Mochila 0/1). Toda la lógica del problema vive en el
   código del proyecto (src/aceleracion), invocada desde el servidor local: aquí solo se arma el caso,
   se pide el análisis y se dibuja la tabla y la reconstrucción paso a paso. */

const $ = (sel) => document.querySelector(sel);
const todasLasFilas = () => [...document.querySelectorAll(".fila-etapa")];

const MAX_ETAPAS_HITOS = 60;   // con más pasos que esto no se dibujan los botones de cada paso

const estado = {
  res: null,          // último resultado devuelto por el servidor
  pos: 0,             // paso actual: 0 = inicio; luego una fila por etapa; luego una decisión por etapa
  celda: null,        // celda de la tabla tocada por la persona: { i, b }
  temporizador: null,
  archivo: null,      // { nombre, completo, texto } del archivo elegido en "Subir archivo"
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

async function analizar(texto, nombre) {
  ocultarError();
  const { ok, datos } = await pedir("/api/aceleracion/resolver", texto, nombre);
  if (!ok) {
    mostrarError(datos.error || "Error desconocido del servidor.");
    return;
  }
  detenerReproduccion();
  estado.res = datos;
  estado.pos = 0;
  estado.celda = null;
  dibujarSalida();
  $("#panel-resultado").scrollIntoView({ behavior: "smooth", block: "start" });
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
  const res = estado.res;
  $("#vacio").classList.add("oculto");
  $("#salida").classList.remove("oculto");
  dibujarResumen(res);
  dibujarCosto(res);
  dibujarFuerzaBruta(res);
  $("#texto-evidencia").textContent = res.evidencia;
  $("#slider-paso").max = totalPasos();
  fijarPosicion(0);
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
    '<div class="stat ancha"><span class="clave">Comprobación</span><span class="texto">' +
    (res.valida ? "Solución válida" : "La solución NO es válida") + '</span><span class="pie">' + pieComprobacion + "</span></div>";
}

function dibujarCosto(res) {
  const n = res.n, B = res.B;
  const calculos = n * (B + 1);
  const bytes = res.celdas * 38;
  const memoria = bytes >= 1e6 ? coma(bytes / 1e6, 1) + " MB" : num(Math.max(1, Math.round(bytes / 1e3))) + " KB";
  const bits = B === 0 ? 1 : Math.ceil(Math.log2(B + 1));
  const sumaC = res.aceleradas.reduce((a, i) => a + res.c[i - 1], 0);
  const sumaD = res.aceleradas.reduce((a, i) => a + res.d[i - 1], 0);
  const lista = (v) => (res.aceleradas.length
    ? res.aceleradas.slice(0, 6).map((i) => v[i - 1]).join(" + ") + (res.aceleradas.length > 6 ? " + …" : "") + " = "
    : "");
  $("#tarjeta-costo").innerHTML =
    "<h3>Costo total</h3>" +
    '<div class="cols-costo">' +
    '<div class="bloque-costo"><h4>Costo de la solución</h4>' +
    '<p class="ecuacion">Σ costos = ' + lista(res.c) + num(sumaC) + " ≤ B = " + num(B) + "</p>" +
    '<p class="ecuacion">Σ ahorros = ' + lista(res.d) + num(sumaD) + "</p>" +
    '<p class="ecuacion">Duración final = ' + num(res.duracion_original) + " − " + num(sumaD) + " = " + num(res.duracion_final) + "</p>" +
    "<p>Se acelera lo que más ahorra sin pasarse del presupuesto: ese es el trabajo del algoritmo.</p></div>" +
    '<div class="bloque-costo"><h4>Costo del algoritmo con los números del caso</h4>' +
    '<p class="ecuacion">celdas de la tabla = (n+1)·(B+1) = ' + num(n + 1) + " · " + num(B + 1) + " = " + num(res.celdas) + "</p>" +
    '<p class="ecuacion">cálculos de celda = n·(B+1) = ' + num(calculos) + "</p>" +
    "<p><b>Por qué:</b> los dos ciclos recorren siempre toda la tabla, sin importar los datos, y cada celda cuesta un número constante de operaciones. " +
    "Por eso T(n, B) = Θ(n·B) en tiempo y en memoria (≈ " + memoria + " aquí).</p>" +
    "<p><b>Pseudo-polinomial:</b> n·B es polinomial en el <i>valor</i> de B, pero B se escribe con solo " + bits +
    " bits. Con 10 bits más, la tabla sería unas 1.024 veces más grande.</p></div>" +
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
  const res = estado.res, total = totalPasos();
  $("#titulo-paso").textContent = f.fase === "inicio" ? "Inicio" : "Paso " + estado.pos + " de " + total;
  const elegida = (i) => '<span class="elegida">' + nombreEtapa(i) + "</span>";
  let frase = "", expl = "", rotulo, numero, relleno, porQue;

  if (f.fase === "inicio") {
    if (res.tabla) {
      frase = "Empezamos con la fila 0: con <strong>0 etapas</strong> no se puede acelerar nada, así que el ahorro es 0 con cualquier presupuesto.";
      expl = "<p>La tabla tiene una fila por etapa (de 0 a " + res.n + ") y una columna por presupuesto (de 0 a " + num(res.B) + "). " +
        "Cada celda guarda el <b>mayor ahorro posible</b> usando solo las primeras etapas y gastando a lo sumo ese presupuesto.</p>" +
        '<p class="formula">DP[i][b] = máx( DP[i−1][b] , d_i + DP[i−1][b−c_i] )</p>' +
        '<p class="pista">Primero se llena la tabla, fila por fila; después se recorre hacia atrás para saber qué etapas se aceleraron.</p>';
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
    const i = f.i, T = res.tabla, B = res.B;
    const c = res.c[i - 1], d = res.d[i - 1], t = res.t[i - 1];
    let noCabe = 0, igual = 0, mejora = 0;
    for (let b = 0; b <= B; b++) {
      if (c > b) noCabe++;
      else if (T[i][b] > T[i - 1][b]) mejora++;
      else igual++;
    }
    frase = "Llenamos la fila de " + elegida(i) + ": dura <strong>" + t + "</strong>, cuesta <strong>" + c +
      "</strong> acelerarla y ahorra <strong>" + d + "</strong>.";
    expl = '<p class="formula">DP[' + i + "][b] = máx( DP[" + (i - 1) + "][b] , " + d + " + DP[" + (i - 1) + "][b−" + c + "] )</p>" +
      "<p>En cada una de las " + num(B + 1) + " celdas se pregunta lo mismo: ¿conviene acelerar esta etapa?</p><ul>" +
      "<li><b>" + num(noCabe) + "</b> celdas: no cabe (cuesta " + c + " y hay menos) → se copia lo de arriba.</li>" +
      "<li><b>" + num(igual) + "</b> celdas: cabe, pero acelerarla no mejora el ahorro → igual que arriba.</li>" +
      "<li><b>" + num(mejora) + "</b> celdas: acelerarla ahorra más → celda verde.</li></ul>";
    rotulo = "Filas calculadas";
    numero = i + " <small>de " + res.n + "</small>";
    relleno = i / res.n;
    porQue = "Cada fila usa solo la fila anterior; por eso cada etapa se acelera a lo sumo una vez.";
  } else {
    const dec = f.dec;
    const c = res.c[dec.i - 1], d = res.d[dec.i - 1];
    if (dec.acelerada) {
      frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>se acelera</strong>.";
      expl = "<p>Con <b>" + num(dec.b) + "</b> de presupuesto restante, la tabla dice DP[" + dec.i + "][" + dec.b + "] = <b>" + dec.valor +
        "</b>. Sin acelerar esta etapa solo se lograría DP[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + dec.sin + "</b>.</p>" +
        "<p>Como <b>" + dec.valor + " ≠ " + dec.sin + "</b>, el máximo viene de acelerarla.</p>" +
        '<p class="razon">Se pagan ' + c + " (el presupuesto restante pasa de " + num(dec.b) + " a " + num(dec.b_despues) +
        ") y se ahorran " + d + ".</p>";
    } else {
      frase = "Hacia atrás, en " + elegida(dec.i) + ": <strong>no se acelera</strong>.";
      expl = "<p>Con <b>" + num(dec.b) + "</b> de presupuesto restante, la tabla dice DP[" + dec.i + "][" + dec.b + "] = <b>" + dec.valor +
        "</b>, y sin acelerar esta etapa también se logra DP[" + (dec.i - 1) + "][" + dec.b + "] = <b>" + dec.sin + "</b>.</p>" +
        '<p class="razon">Son iguales: acelerarla no aporta nada. No se gasta presupuesto (sigue en ' + num(dec.b) + ").</p>";
    }
    rotulo = "Presupuesto gastado";
    numero = num(res.B - dec.b_despues) + " <small>de " + num(res.B) + "</small>";
    relleno = res.B > 0 ? (res.B - dec.b_despues) / res.B : 0;
    porQue = "Se empieza con todo el presupuesto y se resta lo que cuesta cada etapa que se acelera.";
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
  const { i, b } = sel, T = res.tabla;
  const cab = "Celda <b>DP[" + i + "][" + b + "]</b>";
  if (i > filasCalculadas(f)) {
    return '<div class="detalle-celda">' + cab + ": la fila de " + nombreEtapa(i) + " todavía no se calcula.</div>";
  }
  if (i === 0) {
    return '<div class="detalle-celda">' + cab + ": con 0 etapas no se puede acelerar nada → ahorro <b>0</b>.</div>";
  }
  const c = res.c[i - 1], d = res.d[i - 1], v = T[i][b], sin = T[i - 1][b];
  const et = nombreEtapa(i);
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
  const T = res.tabla, B = res.B, n = res.n, W = B + 1;
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
    const c = res.c[sel.i - 1];
    if (c <= sel.b) origen.add((sel.i - 1) * W + (sel.b - c));
  }

  let html = '<div class="tabla-dp" style="grid-template-columns: 112px repeat(' + W + ', 46px)">' +
    '<div class="t-esquina">etapa ╲ b</div>';
  for (let b = 0; b <= B; b++) html += '<div class="t-cab">' + b + "</div>";
  for (let i = 0; i <= n; i++) {
    const actual = f.fase === "llenar" && i === f.i;
    html += '<div class="t-lab' + (actual ? " actual" : "") + '">i=' + i + "<small>" +
      (i === 0 ? "sin etapas" : nombreEtapa(i)) + "</small></div>";
    for (let b = 0; b <= B; b++) {
      const clave = i * W + b;
      let cls, txt;
      if (i > R) { cls = "c-pendiente"; txt = "·"; }
      else {
        txt = T[i][b];
        if (actual && T[i][b] > T[i - 1][b]) cls = "c-nuevo";
        else if (actual) cls = "c-igual";
        else cls = "c-cubierto";
      }
      if (camino.has(clave)) cls += " c-camino";
      if (clave === ahora) cls += " c-ahora";
      if (clave === destino) cls += " c-destino";
      if (origen.has(clave)) cls += " c-origen";
      if (sel && sel.i === i && sel.b === b) cls += " c-sel";
      html += '<div class="tcelda celda ' + cls + '" data-i="' + i + '" data-b="' + b + '" role="cell">' + txt + "</div>";
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
