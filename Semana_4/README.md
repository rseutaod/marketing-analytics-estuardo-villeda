# Venta cruzada y recomendación — la palanca del ARPU

Todos los notebooks y los datos viven en esta misma carpeta, igual que la semana anterior.
Los notebooks leen los datos con la ruta relativa `data/…`, así que hay que abrirlos desde esta carpeta (en Colab: subir la carpeta `data/` junto al notebook).

## Para los estudiantes
| Min | Notebook | Tema |
|---|---|---|
| 30–55 | `breakout_1.ipynb` | Apriori: soporte, confianza, lift y la trampa de la popularidad |
| 75–95 | `breakout_2.ipynb` | La matriz cliente × producto y la similitud coseno |
| 110–140 | `breakout_3.ipynb` | Filtrado colaborativo por ítem y por cliente |
| 150–170 | `breakout_4.ipynb` | Comparar los métodos y medir (holdout, hit rate, A/B) |
| extra | `breakout_5_clima_extra.ipynb` | Recomendar según el clima (estilo Deep Brew) — fuera de los 180 min |

- `data/`: datos sintéticos. Breakouts 1–4: `orders.csv`, `items.csv`, `customers.csv`. Extra del clima: `ordenes.csv`, `bebidas.csv`, `clima_diario.csv`, `clientes.csv`, `ab_test.csv`, `ab_asignacion.csv`.
- `simulador_manzanitas.html`: simulador con una frutería de juguete (ábrelo en el navegador).
- `requirements.txt`: `pip install -r requirements.txt` (en Colab solo hace falta `!pip install mlxtend`).

Cada notebook tiene dos o más celdas `# TODO` con un `...` real: no corren de punta a punta hasta completarlas.

## Para el instructor (no repartir)
- `resuelto_breakout_*_SOLUCION_instructor.ipynb`: resueltos y ejecutados, con las respuestas esperadas.
- `GUIA_instructor.md`: guion minuto a minuto, cifras verificadas y límites de los datos.
- `generate_data.py` (breakouts 1–4; necesita `../semana1/data/customers.csv`) y `generate_data_clima.py` (extra del clima): regeneran los datos con semilla fija.

Los datos son sintéticos con estructura plantada: enseñan el método, no predicen resultados de una cadena real.
