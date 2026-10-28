---
name: congelar-version
description: Protocolo para congelar la versión de la entrega: pruebas, evidencias regeneradas, prueba cruzada del README y coherencia entre informe, repositorio, manual y evidencias. Úsalo cuando el código esté listo y se vaya a entregar.
---

# Congelar la versión

Regla de la guía: informe, repositorio, manual y evidencias deben corresponder a **la misma versión**. Sigue estos pasos en orden y detente si alguno falla.

1. **Pruebas.** Corre `python3 -m pytest tests/`. Todo debe pasar (DP contra fuerza bruta, voraz contra óptimo y cota H(d)).
2. **Estado del código.** Confirma que no hay cambios sin guardar que no sean intencionales. Si el proyecto es un repositorio git, usa `git status`; si no, avisa que no hay forma de fijar una versión y sugiere inicializarlo.
3. **Evidencias.** Usa la skill `correr-casos` para regenerar **todo** `resultados/` con `python3 run_all.py --casos casos/ --salida resultados/`. Nunca regeneres solo una parte.
4. **Verificación.** Pide al subagente `verificador` que confirme que cada caso tiene resultado, tiempo y traza.
5. **Coherencia.** Pide al subagente `auditor-consistencia` que revise informe, manual, README y código, y al `revisor-reducciones` que revise las dos pruebas de NP-dureza.
6. **Prueba cruzada.** Un integrante distinto al autor sigue **solo el README** en una carpeta limpia. Si algo no funciona sin preguntar, el README está incompleto: corrígelo y vuelve al paso 3.
7. **Registro.** Anota en `resultados/` la fecha y el identificador de la versión (hash de git si existe).
8. **Congelar.** Desde aquí no se cambia más la lógica. Si algo se corrige, se repite desde el paso 1.

Entrega un resumen con cada paso en ✔ o ✘.
