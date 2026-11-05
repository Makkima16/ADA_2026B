# Primera entrega — ADAG 2026-B

**Guía de requisitos | Grupos 1, 2 y 3**

> Conversión a Markdown de `Guia_Primera_Entrega_ADAG_2026B_Resumen (8).docx`. Si hay diferencias, manda el .docx.

**Objetivo.** Presentar la formalización, la justificación de complejidad y una solución base ejecutable, con evidencia verificable según el grupo.

## 1. Entregables obligatorios para todos

- **Informe (un solo documento):** formalización de las dos partes del problema (entradas, salidas, tamaño, objetivo y restricciones) y prueba formal de NP-dureza por reducción polinomial.
- **Repositorio:** código de la solución base, dependencias, README e instrucciones de ejecución.
- **Manual técnico:** algoritmo, estructura del código, formatos de entrada/salida, pasos de ejecución y limitaciones.

**Reducciones:** G1: 3-SAT; G2: Cobertura Máxima (selección de participantes); G3: Mochila 0/1 (aceleración) y Cobertura de Vértices (auditoría).

## 2. Requisitos específicos por grupo

- **G1 · Oráculo.** En el repositorio: `entrega.json` (grupo, semana, índices de rol, estrategia, formato, estilo, cierre y temperatura); **notebook de evaluación** que cargue el JSON y funcione con los datos privados de la profesora sin cambios; **notebook de búsqueda** con método, configuraciones y precisiones, trazas de fallos y validación con `oraculo.validar`.
- **G2 · Red.** Ejecutar la solución base con los casos de la profesora. Entregar resultados, tiempo por caso y traza: selección de nodos, ganancias marginales, reparto del presupuesto y verificación de restricciones.
- **G3 · Ruta.** Ejecutar la solución base con los casos de la profesora. Entregar resultados, tiempo por caso y traza: estados/decisiones de programación dinámica, etapas aceleradas, costos y cobertura de auditoría.
- **G3 · 3 integrantes.** Además de lo exigido a G3: implementar la variante 1 de auditoría ponderada por costo (minimizar el costo de cubrir todos los riesgos). Incluir resultados, tiempos, traza de elecciones y análisis de complejidad.

## 3. Condiciones de aceptación

- **Reproducibilidad:** los resultados deben poder obtenerse desde el código entregado, sin editar la lógica del algoritmo.
- **Pruebas:** G2 y G3 deben usar los casos recibidos de la profesora y reportar salida, tiempo y traza identificada por caso.
- **Consistencia:** informe, repositorio, manual y evidencias deben corresponder a la misma versión.
