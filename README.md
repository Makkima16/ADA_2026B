# Proyecto ADA 2026-B — Ruta crítica y auditoría (Grupo 3)

Proyecto semestral de Análisis y Diseño de Algoritmos, Universidad de Caldas.

El proyecto estudia dos problemas de optimización NP-difíciles que aparecen en un mismo escenario: un flujo de trabajo que procesa cada solicitud a través de una cadena de etapas y que, además, debe decidir qué solicitudes auditar. Para cada problema se pide formalizarlo, demostrar su dificultad, resolverlo y justificar con rigor qué tan eficiente es la solución.

## Escenario

Un flujo de trabajo procesa cada solicitud a través de una cadena de $n$ etapas en serie. Cada etapa $i$ dura normalmente $t_i$ y puede acelerarse a un costo $c_i$, lo que reduce su duración en $d_i$. Se dispone de un presupuesto $B$ para acelerar. Por separado, cada solicitud puede requerir una revisión de cumplimiento normativo; auditarlas todas es demasiado costoso, así que solo se audita un subconjunto.

## Los dos problemas

### Parte 1 — Aceleración óptima de la cadena (Mochila 0/1)

- **Entrada:** $n$ etapas con $t_i$, $c_i$, $d_i$ (con $0 \le d_i \le t_i$) y un presupuesto entero $B$.
- **Objetivo:** elegir el conjunto $A$ de etapas a acelerar con $\sum_{i \in A} c_i \le B$ que maximice $\sum_{i \in A} d_i$. La duración final de la cadena es $\sum t_i - \sum_{i \in A} d_i$.
- **Algoritmo exacto:** programación dinámica con la recurrencia $DP[i][b] = \max(DP[i-1][b],\ DP[i-1][b-c_i] + d_i)$ si $c_i \le b$.
- **Eficiencia:** $T(n, B) = O(n \cdot B)$. Es **pseudo-polinomial**: $B$ ocupa $\log_2 B$ bits, por lo que el costo es exponencial en el tamaño real de la entrada. Esto no contradice la NP-dureza (es NP-difícil en sentido débil).
- **NP-dureza:** reducción **desde** Mochila 0/1 (peso $w_i = c_i$, valor $v_i = d_i = t_i$, capacidad $W = B$).

### Parte 2 — Cobertura mínima de auditoría (Set Cover)

- **Entrada:** $n$ interacciones candidatas y $r$ categorías de riesgo; cada interacción $j$ cubre un subconjunto $S_j$ de categorías.
- **Objetivo:** elegir el menor conjunto $J$ de interacciones a auditar tal que la unión de sus $S_j$ cubra las $r$ categorías.
- **Factibilidad:** antes de correr cualquier algoritmo se verifica en $O(n \cdot r)$ que la unión de todos los $S_j$ cubre las $r$ categorías.
- **Algoritmo aproximado (voraz):** en cada paso elige la interacción que cubre más categorías aún sin cubrir.
- **Garantía de aproximación:** el voraz usa a lo sumo $H(d) = 1 + \tfrac12 + \dots + \tfrac1d \le \ln r + 1$ veces el óptimo, con $d = \max_j |S_j|$ (Johnson, 1974; Chvátal, 1979).
- **Eficiencia del voraz:** $T(n, r) = O(n \cdot r \cdot \min(n, r))$, que es más ajustada que la cota $O(n \cdot r^2)$; ambas son correctas.
- **Algoritmo exacto (solo para verificar):** fuerza bruta, con $n$ pequeño (≈ 12 o menos).
- **NP-dureza:** reducción **desde** Cobertura de Vértices (aristas = categorías, vértices = interacciones, mismo $k$).

## Alcance de la primera entrega

| Entregable | Contenido |
| --- | --- |
| Informe | Formalización de ambas partes (tamaño de entrada, entrada, salida, objetivo y restricciones) y prueba formal de NP-dureza por reducción polinomial, en ambas direcciones (⇒ y ⇐) más el tiempo polinomial de la construcción. |
| Repositorio | Código del problema base, dependencias, este README e instrucciones de ejecución. |
| Manual técnico | Algoritmos, estructura del código, formatos de entrada y salida, pasos de ejecución y limitaciones. |
| Evidencias | Por cada caso proporcionado por la profesora: resultado, tiempo y traza. |

**Traza Parte 1:** decisiones y estados de la DP, etapas aceleradas y costos.
**Traza Parte 2:** elección del voraz en cada paso y cobertura final.

Por ser un grupo de tres integrantes se implementa además la **variante de auditoría ponderada por costo**: cubrir todas las categorías con costo total mínimo, donde el voraz elige la interacción de menor costo $a_j$ por categoría nueva cubierta. La cota $H(d)$ se conserva (Chvátal, 1979).

**Entregas posteriores (fuera de esta versión):** presupuesto conjunto de ambas partes, etapas en paralelo (grafo acíclico dirigido, ruta más larga en $O(n + m)$) y validación experimental con gráficas de crecimiento.

## Estructura del repositorio

```
README.md
COMANDOS.md             # comandos del proyecto y desde dónde se ejecutan
context/                # guía de entrega, enunciado y reparto de tareas
docs/                   # documentación: informe (formalización y reducción), manual técnico de la Parte 2 y estudio de enfoques sobre el voraz
src/aceleracion/        # Parte 1: DP, fuerza bruta de verificación, lectura de casos (.json) y traza
src/auditoria/          # Parte 2: voraz, fuerza bruta, lectura de casos, resolución y escritura de traza
src/auditoria/enfoques/           # enfoques aparte del voraz base (esenciales, parejas, rareza, todo junto) y su experimento de comparación
frontend/               # visor local para ver paso a paso cómo resuelve cada método un caso (herramienta de apoyo)
tests/                  # pruebas
```

Los algoritmos, la lectura de la entrada y la escritura de la traza están separados para poder reutilizarlos en las variantes. Los enfoques de `src/auditoria/enfoques/` **no reemplazan** al voraz base de `src/auditoria/`.

## Estado actual

- Implementado (Parte 2): voraz base, verificación de factibilidad, fuerza bruta, cota $H(d)$, resolución de un caso y escritura de traza, con la lectura de casos aislada en `src/auditoria/lectura.py` (formatos `.json` del ejemplo de la profesora y `.txt` provisional); con sus pruebas.
- Implementado (estudio adicional de la Parte 2): cuatro enfoques sobre el voraz (esenciales, parejas, rareza y todo junto), su comparación contra el óptimo y el visor `frontend/`.
- Documentación en `docs/`: informe de la Parte 2 (formalización y reducción), manual técnico de la Parte 2 y estudio de los enfoques.
- Pendiente: adaptar la lectura al formato final de los casos de la profesora (aún no llegaron; se guardarán en `casos/`), el comando que corre todos los casos y genera las evidencias, `requirements.txt`, la Parte 1 y la variante ponderada, y unir los documentos de `docs/` en el informe y el manual únicos del grupo.

## Ejecución

Requiere Python 3.8 o superior. El código usa solo la librería estándar; las pruebas requieren `pytest`.

```
python3 -m pytest tests/                                                  # pruebas
python3 frontend/servidor.py                                              # visor local (abre el navegador)
python3 src/auditoria/enfoques/comparacion/experimento.py --instancias 3000         # experimento de comparación de enfoques (unos 20 s)
```

Todos los comandos y desde dónde se ejecutan están en `COMANDOS.md`. Los tiempos se miden con `time.perf_counter()` y todo generador aleatorio usa semilla fija, de modo que el mismo código con los mismos casos produce los mismos resultados.

## Notación

$n$ (etapas o interacciones), $B$ (presupuesto), $r$ (categorías de riesgo), $t_i$ (duración), $c_i$ (costo de acelerar), $d_i$ (reducción), $S_j$ (categorías cubiertas por $j$), $a_j$ (costo de auditar $j$), $A$ (etapas aceleradas), $J$ (interacciones auditadas).

## Criterios de evaluación del curso

| Componente | Peso |
| --- | --- |
| Formalización del problema | 10 % |
| Prueba de NP-dureza por reducción | 10 % |
| Deducción formal de la eficiencia del algoritmo exacto | 10 % |
| Algoritmo aproximado: diseño, eficiencia y cota | 15 % |
| Validación experimental | 10 % |
| Sustentación | 45 % |

## Referencias

- Karp, R. M. (1972). Reducibility among combinatorial problems. En R. E. Miller y J. W. Thatcher (Eds.), *Complexity of Computer Computations* (pp. 85–103). Plenum Press.
- Johnson, D. S. (1974). Approximation algorithms for combinatorial problems. *Journal of Computer and System Sciences*, 9(3), 256–278.
- Chvátal, V. (1979). A greedy heuristic for the set-covering problem. *Mathematics of Operations Research*, 4(3), 233–235.
