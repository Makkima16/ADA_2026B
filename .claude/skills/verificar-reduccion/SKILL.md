---
name: verificar-reduccion
description: Guía para escribir y revisar las pruebas de NP-dureza del proyecto (Mochila 0/1 → aceleración, Cobertura de Vértices → auditoría). Úsalo cuando se vaya a redactar, corregir o ensayar una reducción para el informe o la sustentación.
---

# Escribir una reducción de NP-dureza

Estructura obligatoria, en este orden:

1. **Problema conocido (versión de decisión)** y **problema nuestro (versión de decisión)**.
2. **Construcción:** tabla que traduce cada elemento de la instancia conocida a la nuestra.
3. **Tiempo polinomial** de la construcción, con su O(·).
4. **Equivalencia:** demostrar ⇒ y ⇐ por separado.
5. **Conclusión:** como el problema conocido es NP-difícil, el nuestro también.

## Parte 1 — Mochila 0/1 ≤ₚ aceleración

| Mochila 0/1 | Cadena de etapas |
| --- | --- |
| objeto i con peso w_i | etapa i con costo c_i = w_i |
| valor v_i | reducción d_i = v_i |
| (no existe) | duración t_i = v_i (así d_i ≤ t_i) |
| capacidad W | presupuesto B = W |
| umbral V | límite de duración L = Σ v_i − V |

Clave: duración(A) = Σ t_i − Σ_{i∈A} d_i = Σ v_i − Σ_{i∈A} v_i. Por eso "duración ≤ L" equivale a "valor ≥ V".

## Parte 2 — Cobertura de Vértices ≤ₚ auditoría mínima

| Cobertura de Vértices | Auditoría |
| --- | --- |
| arista e ∈ E | categoría de riesgo (r = \|E\|) |
| vértice v ∈ V | interacción que cubre las aristas incidentes a v |
| entero k | el mismo k |

Construcción en O(|V| + |E|). La factibilidad se cumple sola: cada arista está cubierta por sus dos extremos.

## Errores que se castigan

- Hacer la reducción en el sentido contrario.
- Probar solo una dirección de la equivalencia.
- No justificar el tiempo polinomial.
- Decir que O(n·B) contradice la NP-dureza: es pseudo-polinomial (B ocupa log₂ B bits).

Para una revisión independiente, delega en el subagente `revisor-reducciones`.
