"use strict";

/* Sección "Cómo funciona cada enfoque" (Parte 1 y Parte 2): una barra de botones elige qué enfoque se
   explica y solo se muestra ese. Cada botón lleva data-vista y cada bloque data-vista-panel con el mismo valor. */

document.querySelectorAll("[data-selector-explicacion]").forEach((barra) => {
  const seccion = barra.closest(".panel-explicacion");
  const botones = [...barra.querySelectorAll(".tab")];

  function mostrar(vista) {
    botones.forEach((b) => {
      const activo = b.dataset.vista === vista;
      b.classList.toggle("activa", activo);
      b.setAttribute("aria-selected", activo ? "true" : "false");
      b.tabIndex = activo ? 0 : -1;
    });
    seccion.querySelectorAll("[data-vista-panel]").forEach((p) => {
      p.classList.toggle("oculto", p.dataset.vistaPanel !== vista);
    });
  }

  botones.forEach((b, i) => {
    b.addEventListener("click", () => mostrar(b.dataset.vista));
    b.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.stopPropagation();   // las flechas también avanzan la simulación; aquí solo cambian de botón
      const j = (i + (e.key === "ArrowRight" ? 1 : botones.length - 1)) % botones.length;
      botones[j].focus();
      mostrar(botones[j].dataset.vista);
    });
  });

  mostrar(botones[0].dataset.vista);
});
