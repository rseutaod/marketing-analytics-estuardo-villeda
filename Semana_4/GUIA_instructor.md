# Guía del instructor — Venta cruzada y recomendación (3 horas)

La pregunta que hilvana la sesión: **¿cómo subimos lo que nos deja cada cliente (ARPU), y cómo sabemos si funciona?**
Formato: slides → breakout → slides → breakout, cuatro veces (igual que churn). Todos los grupos ven el mismo notebook.
Deck: "Venta cruzada y recomendación — la palanca del ARPU" (24 slides, con notas del orador en cada una).

## Minuto a minuto

| Min | Bloque | Qué hacer |
|---|---|---|
| 0–15 | Apertura | `cover`, `mapa-formula` (tres palancas), `arpu-lineal` (retención 8,2× → 15,8×; ARPU +10% → +10%), `gartner-personalizacion`, `agenda-hoy` |
| 15–30 | Apriori | `canasta-idea`, `apriori-tres-numeros` (Latte → Croissant: soporte 2,9%, confianza 32%, lift 6,0), `apriori-trampa` |
| 30–55 | **Breakout 1** | `br1-apriori`. Cada persona habla ~5 min; respuestas individuales al foro |
| 55–65 | Descanso | |
| 65–75 | Matriz | `matriz-idea` (2.000 × 29; 85,8% vacío), `matriz-coseno` |
| 75–95 | **Breakout 2** | `br2-matriz` |
| 95–110 | Filtrado colaborativo | `cf-dos-caminos`, `cf-item`, `cf-cliente`, `cf-costos` |
| 110–140 | **Breakout 3** | `br3-cf` |
| 140–150 | Medir | `medir-holdout`, `medir-metricas`, `medir-resultados`, `medir-causal` |
| 150–170 | **Breakout 4** | `br4-comparar` |
| 170–180 | Cierre | `cierre-creepy`, `cierre-puente` |

**Si vas corto de tiempo:** salta `cf-costos` (la escala se discute en el Breakout 3) y acorta el descanso a 5 min.
El simulador de manzanitas sirve para abrir cada bloque (2–3 min) o para quien llegue tarde.

## Cifras de los notebooks (todas verificadas ejecutando los notebooks resueltos)

**Datos:** 14.579 órdenes · 2.000 clientes · 29 productos · 2,01 productos por orden. Corte: 2026-06-01 (últimos 90 días = holdout).

**Breakout 1 — Apriori** (soporte mínimo 1%): 68 conjuntos frecuentes, 48 reglas A → B, 15 reglas con confianza ≥ 0,25 y lift ≥ 1,5.
- Latte → Croissant: soporte 0,029 · confianza 0,324 · lift 5,99 (el Croissant va en ~5,4% de las canastas).
- Mayores lifts: Granola ↔ Matcha Latte 7,9 · Americano ↔ Sándwich 6,9 · Latte ↔ Croissant 6,0 · Pastel de Queso ↔ Refresher 5,3 · Cappuccino ↔ Muffin 4,9 · Frappuccino ↔ Galleta 4,2 · Té Chai ↔ Banana Bread 4,0.
- Trampa: el Agua va en 45,9% de las canastas; X → Agua tiene confianza 46–48% y lift 1,02–1,05 (Muffin → Agua 47,8% / 1,04).
- Oportunidad con 10% de aceptación: la regla que más margen potencial deja es Galleta → Frappuccino (≈ $281), no la de mayor lift (Matcha → Granola ≈ $167).

**Breakout 2 — Matriz:** 2.000 × 29, densidad 14,2%; promedio 4,1 productos por cliente; 268 clientes (13,4%) con 0 productos antes del corte y 63 con 1.
- sim(cliente 14, 1015) = 0,833 · sim(14, 62) = 0,000 · sim(Latte, Croissant) = 0,505 · sim(Latte, Ensalada) = 0,060.
- El Agua tiene la mayor similitud promedio con los demás productos (≈ 0,36): se parece a todo.

**Breakout 3 — Filtrado colaborativo** (K = 30 vecinos): para el cliente 14, por ítem recomienda Té Verde (2,03), Croissant (1,69), Latte (1,56); por cliente, Té Verde (7,29), Croissant (2,17), Galleta (1,45).
- Misma recomendación #1: 68%; coinciden en ≥ 2 de 3: 82% (1.669 clientes con ≥ 2 productos).
- Matriz de productos 29 × 29 (841 celdas) vs. clientes 2.000 × 2.000 (4 millones).

**Breakout 4 — Comparar:** 986 de 2.000 clientes (49%) probaron algo nuevo en el holdout.

| Método | Hit rate@3 | Precisión@3 | Cobertura (de 28) |
|---|---|---|---|
| Popularidad | 34,7% | 0,138 | 13 |
| Apriori | 40,9% | 0,152 | 19 |
| Filtrado por ítem | 58,6% | 0,243 | 28 |
| Filtrado por cliente | 56,4% | 0,233 | 28 |

ARPU del holdout (90 días, precios del catálogo): $20,96 por cliente ($41.914 en total).

## Lo que conviene decir antes de que lo noten
- **Los datos son sintéticos con estructura plantada** (6 gustos de cliente y 6 asociaciones bebida → comida), así que los métodos funcionan mejor que en datos reales. Las cifras enseñan el método, no predicen resultados de una cadena.
- **El Agua está plantada como trampa** (45% de las canastas). No es un hallazgo del mundo real.
- **El hit rate no es efecto causal.** En el holdout nadie recibió recomendaciones; el 49% que probó algo nuevo lo hizo solo. Para medir el ARPU incremental se necesita un grupo de control (es el puente a uplift).
- **Hit rate de la popularidad: 35%.** Es la línea base; el filtrado por ítem le gana por ~69% relativo.
- Un intento de mostrar "fuga" (calcular las similitudes con todos los datos, holdout incluido) cambió el hit rate casi nada en esta base (≈ 0,5 puntos), por eso no lo incluí como actividad.

## Gartner: qué se verificó y qué no
Verificado en los comunicados de prensa de Gartner:
- 53% de los clientes vive experiencias negativas con marketing personalizado; 3,2 veces más arrepentimiento y 44% menos probabilidad de recompra (1.464 personas, 3 de junio de 2025).
- 38% dejaría de hacer negocios si la personalización parece "creepy" (más de 2.500 clientes, 11 de marzo de 2019).
- 80% de los marketers abandonaría la personalización para 2025 por falta de ROI o por problemas de datos (predicción del 2 de diciembre de 2019; no se verificó si se cumplió).

**No encontré** una cifra de Gartner sobre cuánto sube el ARPU por venta cruzada: el único documento sobre venta cruzada que abrí (abril de 2025) está tras muro de pago y su resumen no trae números. No uses cifras de aumento de ARPU de blogs de proveedores como si fueran de Gartner.

## Videos (candidatos sin verificar)
No pude abrir las páginas de YouTube (el servidor rechazó las consultas), así que solo sé los títulos de la búsqueda. Míralos antes de ponerlos:
- Apriori: https://www.youtube.com/watch?v=nK701M6lxSM · https://www.youtube.com/watch?v=oNTs4gWW2DE
- Filtrado colaborativo: https://www.youtube.com/watch?v=rizwooaTNEA · https://www.youtube.com/watch?v=fXNjkuKm2r8 · https://www.youtube.com/watch?v=nbua719p1m4

## Simulador de manzanitas
Cuatro pestañas (canastas y Apriori; matriz y similitud; recomendar por ítem y por cliente; medir con holdout) con una frutería de juguete (10 productos, 15 clientes, 24 canastas). Ojo con la pestaña "Medir": el holdout oculta una compra por cliente de una lista fija escrita en los datos de juguete, y esa lista se escogió después de probar otra donde los métodos quedaban casi iguales. Con 14 clientes, un cliente de diferencia mueve cada barra 7 puntos: es ilustrativo, no una prueba de que un método sea mejor.


## Módulo extra: recomendación por clima (`breakout_5_clima_extra.ipynb`, fuera de los 180 minutos)
Úsalo como demo de 10–15 minutos al final del Breakout 4, como tarea o en la sesión siguiente. Cifras verificadas ejecutando el notebook resuelto:
- Bebidas frías según temperatura: ≈ 14% con frío (<18°), 40% templado, 79% con calor (>25°). Sin lluvia ≈ 51% y con lluvia ≈ 34%.
- Holdout de septiembre (3.961 órdenes), hit rate@3: Popularidad 43,3%, Lo de siempre 51,5%, Popularidad por clima 49,3%, **Cliente × clima 55,6%**. Con calor la popularidad global acierta solo 14,6%; Cliente × clima 55,8%. Con frío: 59,2 / 55,5 / 60,3 / 63,7.
- Mensaje: el clima solo no le gana al historial, el historial solo no ve el clima; juntos suben ≈ 4 puntos sobre "lo de siempre". Es una mejora modesta en promedio.
- A/B de octubre (1.000 clientes por grupo): ARPU del mes control US$ 3,72, genérica 4,37, clima 5,02. ΔARPU genérica +0,65 (IC 95% +0,25 a +1,05); clima +1,30 (+0,88 a +1,71). Margen neto adicional (descontando US$ 0,02 por notificación): genérica +0,36 (+0,08 a +0,64); clima +0,81 (+0,52 a +1,10).
- Conversión por apertura de app: día normal 17,2 / 19,3 / 20,3%; día extremo (≥28° o ≤17°) 16,2 / 19,1 / 27,9% (control / genérica / clima).

**Lo que hay que decir con claridad:**
- Los datos son sintéticos y **el efecto del clima y el de las campañas los plantó el generador** (+0,085 en conversión por apertura en días extremos con la campaña de clima, +0,02 en días normales, +0,015 con la genérica). Un ARPU +35% es un efecto de juguete: en la vida real esperen mucho menos.
- No tengo verificado qué señales usa Deep Brew en la realidad; el notebook dice "según se ha publicado, usa señales como el clima y la hora". Confírmalo con el caso o con fuentes de Starbucks antes de afirmarlo en clase.
- La tabla de conversión por día extremo es por apertura de app (descriptiva); la comparación formal del ARPU es por cliente. Los 3.000 clientes se aleatorizaron, no los días.
- Cerca del 8% de las órdenes del holdout son de clientes con ≤ 2 órdenes previas; ahí el clima suple la falta de historial (cold start).
