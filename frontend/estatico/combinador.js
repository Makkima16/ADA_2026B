"use strict";

/* Sección 2 del visor del voraz, pestaña "Armar una combinación": se encienden los ingredientes (esenciales, rareza,
   parejas) y se muestra el detalle de esa combinación: cómo decide, qué arregla, qué aporta cada ingrediente, qué se midió
   y qué cuesta. Las cifras salen de `ablacion_detalle(3000, 2026)` (src/auditoria/enfoques/comparacion/ablacion.py):
   9.000 instancias pequeñas (n <= 12), comparadas con el mínimo real. Si cambia el experimento, hay que actualizarlas. */

(function () {
  const TOTAL = 9000;
  const NOMBRES = {
    "": "Voraz normal", e: "Esenciales", r: "Rareza", p: "Parejas",
    er: "Esenciales + rareza", ep: "Esenciales + parejas", rp: "Rareza + parejas", erp: "Los tres juntos",
  };
  const ING = { e: "Esenciales", r: "Rareza", p: "Parejas" };
  /* fallas: casos en que no llegó al mínimo; mejora/igual/peor: frente al voraz normal; razon: peor caso (veces el mínimo). */
  const DATOS = {
    "": { fallas: 513, mejora: 0, igual: 0, peor: 0, razon: 2.0 },
    e: { fallas: 211, mejora: 313, igual: 8676, peor: 11, razon: 1.6667 },
    r: { fallas: 135, mejora: 404, igual: 8571, peor: 25, razon: 1.5 },
    p: { fallas: 138, mejora: 387, igual: 8603, peor: 10, razon: 1.5 },
    er: { fallas: 97, mejora: 441, igual: 8534, peor: 25, razon: 1.5 },
    ep: { fallas: 25, mejora: 493, igual: 8502, peor: 5, razon: 1.3333 },
    rp: { fallas: 13, mejora: 501, igual: 8498, peor: 1, razon: 1.3333 },
    erp: { fallas: 9, mejora: 506, igual: 8492, peor: 2, razon: 1.3333 },
  };
  const ARREGLA = {
    e: "<b>Esenciales</b> arregla el caso de las interacciones <em>obligatorias</em>: si un riesgo solo lo revisa una interacción, esa decisión no debe dejarse al orden. Las toma primero.",
    r: "<b>Rareza</b> arregla el caso de los riesgos <em>difíciles de cubrir</em>: los pesa más que a los comunes, para no dejarlos al final cuando ya cuestan una interacción entera.",
    p: "<b>Parejas</b> arregla el caso de las <em>trampas</em>: una interacción grande parece la mejor pero tapa que dos pequeñas, juntas, cubrían más. Mirando pares se ve lo que una sola no muestra.",
  };

  const num = (x) => Number(x).toLocaleString("es-CO");
  const dec = (x, d) => Number(x).toFixed(d).replace(".", ",");
  const veces = (x) => (x < 10 ? dec(x, 1) : String(Math.round(x)));
  const bandera = (clave, l) => clave.indexOf(l) !== -1;

  function lema(clave) {
    const e = bandera(clave, "e"), r = bandera(clave, "r"), p = bandera(clave, "p");
    let regla;
    if (p && r) regla = "mira parejas de interacciones y valora cada pareja por la rareza de lo que cubre";
    else if (p) regla = "mira parejas de interacciones antes de elegir";
    else if (r) regla = "elige la interacción de mayor puntaje de rareza";
    else regla = "elige la interacción que revisa más riesgos nuevos";
    if (e) return "Primero las obligatorias (esenciales); con lo que falte, " + regla + ".";
    return regla.charAt(0).toUpperCase() + regla.slice(1) + ".";
  }

  function pasos(clave) {
    const e = bandera(clave, "e"), r = bandera(clave, "r"), p = bandera(clave, "p");
    const lista = [];
    if (e) lista.push("Busca las <b>esenciales</b> (las interacciones que son las únicas que revisan algún riesgo) y las elige todas primero, sin discutir.");
    let regla;
    if (p && r) regla = "Evalúa <b>todas las parejas</b> de interacciones y valora cada pareja por la <b>rareza</b> de los riesgos nuevos que cubre (cada riesgo pendiente vale 1 dividido entre cuántas interacciones lo revisan). De la mejor pareja se compromete la interacción que más vale por sí sola.";
    else if (p) regla = "Evalúa <b>todas las parejas</b> de interacciones y busca la que revisa más riesgos nuevos <em>juntas</em>. De esa pareja se compromete la que más revisa por sí sola. Si una sola interacción cubre lo mismo que una pareja, se prefiere la sola.";
    else if (r) regla = "Da a cada riesgo pendiente el valor <b>1 ÷ (cuántas interacciones lo revisan)</b>, suma ese valor para cada interacción y elige la de <b>mayor puntaje</b> (ante empate, la que cubre más riesgos nuevos y luego la de número menor).";
    else regla = "Cuenta, para cada interacción, cuántos <b>riesgos nuevos</b> revisaría (los que aún no cubre ninguna de las ya elegidas) y elige la que más. Si dos empatan, gana la de número menor.";
    lista.push((e ? "Con los riesgos que faltan, en cada paso: " : "En cada paso: ") + regla.charAt(0).toLowerCase() + regla.slice(1));
    lista.push("Repite hasta que <b>todos los riesgos estén revisados</b>. Nunca se arrepiente de lo ya elegido.");
    return "<ol class=\"lista-explicacion\">" + lista.map((t) => "<li>" + t + "</li>").join("") + "</ol>";
  }

  function sinIngrediente(clave, l) {
    return ["e", "r", "p"].filter((x) => bandera(clave, x) && x !== l).join("");
  }

  function aporte(clave) {
    const ings = ["e", "r", "p"].filter((l) => bandera(clave, l));
    if (!ings.length) return "";
    const items = ings.map((l) => {
      const sin = sinIngrediente(clave, l);
      const a = DATOS[sin].fallas, b = DATOS[clave].fallas;
      const resultado = b < a ? "con él, <b>" + num(b) + "</b>" + (b > 0 ? " (" + veces(a / b) + " veces menos)" : "")
        : "con él, " + num(b) + ": no mejora aquí";
      return "<li><b>" + ING[l] + ":</b> sin él (quedaría <em>" + NOMBRES[sin].toLowerCase() + "</em>) falla en <b>" + num(a) + "</b> de las " + num(TOTAL) + "; " + resultado + ".</li>";
    });
    return "<h4>Qué aporta cada ingrediente en esta combinación</h4><ul class=\"lista-explicacion\">" + items.join("") + "</ul>";
  }

  function velocidad(clave) {
    const p = bandera(clave, "p");
    const orden = p ? "O(n²·r·min(n, r)): revisa todos los pares, un factor n más que el voraz normal"
      : "O(n·r·min(n, r)): el mismo orden de costo que el voraz normal";
    const medido = {
      "": "Es la referencia.", e: "Casi no suma tiempo (medido).", r: "Unas 4 veces más lento que el voraz normal (medido).",
      p: "De 6 a 46 veces más lento entre 20 y 160 interacciones (medido).", erp: "De 14 a 138 veces más lento entre 20 y 160 interacciones (medido).",
    }[clave];
    return orden + ". " + (medido || "Su tiempo no se midió por separado.");
  }

  function garantia(clave) {
    if (clave === "") return "<b>Garantía demostrada</b> (Johnson 1974; Chvátal 1979): nunca usa más de H(d) veces el mínimo, donde d es la mayor cantidad de riesgos que revisa una sola interacción.";
    if (clave === "e") return "<b>Garantía demostrada:</b> conserva la del voraz normal, |J| ≤ |E| + H(d)·(OPT − |E|) ≤ H(d)·OPT.";
    const por = [bandera(clave, "r") ? "rareza" : "", bandera(clave, "p") ? "parejas" : ""].filter(Boolean).join(" y ");
    return "<b>Garantía: ninguna.</b> No existe ninguna garantía matemática demostrada para esta combinación (lleva " + por +
      ", y para eso no hay prueba ni se encontró en la literatura). Solo se midió: en estas instancias nunca superó la cota del voraz normal, pero eso no es una prueba.";
  }

  function detalle(clave) {
    const d = DATOS[clave], nIng = clave.length;
    const etiqueta = nIng === 0 ? "El método base" : nIng === 1 ? "1 ingrediente" : nIng === 2 ? "2 ingredientes" : "Los 3 ingredientes";
    const frente = clave === "" ? "Es la referencia"
      : "Mejora en <b>" + num(d.mejora) + "</b> · igual en " + num(d.igual) + " · peor en <b>" + num(d.peor) + "</b>";
    const menos = clave === "" ? "" : " · " + veces(DATOS[""].fallas / d.fallas) + " veces menos fallas que el voraz normal";
    const arreglos = ["e", "r", "p"].filter((l) => bandera(clave, l)).map((l) => "<li>" + ARREGLA[l] + "</li>").join("");
    return "<span class=\"etiqueta-enfoque" + (nIng === 0 ? " base" : "") + "\">" + etiqueta + "</span>" +
      "<h3>" + NOMBRES[clave] + "</h3>" +
      "<p class=\"lema\">&laquo;" + lema(clave) + "&raquo;</p>" +
      "<h4>Cómo decide, paso a paso</h4>" + pasos(clave) +
      (arreglos ? "<h4>Qué arregla</h4><ul class=\"lista-explicacion\">" + arreglos + "</ul>" : "") +
      aporte(clave) +
      "<h4>Qué se midió</h4>" +
      "<div class=\"mini-stats\">" +
      "<div class=\"mini-stat\"><span class=\"clave\">No llegó al mínimo</span><b>" + num(d.fallas) + "</b><span>de " + num(TOTAL) + " instancias (" + dec(d.fallas / TOTAL * 100, 2) + " %)" + menos + "</span></div>" +
      "<div class=\"mini-stat\"><span class=\"clave\">Frente al voraz normal</span><b class=\"chico\">" + frente + "</b></div>" +
      "<div class=\"mini-stat\"><span class=\"clave\">Peor caso medido</span><b>" + dec(d.razon, 2) + " veces</b><span>el mínimo (lo máximo que se alejó)</span></div>" +
      "</div>" +
      "<p class=\"nota-cmp\">9.000 instancias pequeñas generadas al azar (hasta 12 interacciones), comparadas con el mínimo real por fuerza bruta. No se puede asegurar que sea igual en casos grandes.</p>" +
      "<h4>Qué cuesta</h4><p>" + velocidad(clave) + "</p>" +
      "<p class=\"cuando\">" + garantia(clave) + "</p>";
  }

  const caja = document.getElementById("detalle-armador");
  const botones = [...document.querySelectorAll("#ingredientes-armador .btn-ing")];
  if (!caja || !botones.length) return;
  const encendidos = { e: false, r: false, p: false };

  function dibujar() {
    const clave = ["e", "r", "p"].filter((l) => encendidos[l]).join("");
    botones.forEach((b) => {
      b.classList.toggle("activo", encendidos[b.dataset.ing]);
      b.setAttribute("aria-pressed", encendidos[b.dataset.ing] ? "true" : "false");
    });
    document.getElementById("nombre-armador").textContent = NOMBRES[clave];
    caja.innerHTML = detalle(clave);
  }

  botones.forEach((b) => b.addEventListener("click", () => {
    encendidos[b.dataset.ing] = !encendidos[b.dataset.ing];
    dibujar();
  }));
  dibujar();
})();
