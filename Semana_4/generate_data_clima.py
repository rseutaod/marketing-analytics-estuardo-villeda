"""Datos sintéticos para el módulo extra: recomendación de bebidas según el clima (estilo Deep Brew).

Genera en data/:
  bebidas.csv       catálogo (tipo frío/caliente, familia, precio, costo)
  clima_diario.csv  temperatura media y lluvia por ciudad y día (abril–octubre 2026)
  clientes.csv      3.000 clientes con su ciudad
  ordenes.csv       historial de órdenes abril–septiembre (con el clima de ese día)
  ab_test.csv       experimento de octubre: aperturas de la app con 3 grupos aleatorios
  ab_asignacion.csv grupo asignado a cada uno de los 3.000 clientes (incluye a quienes no abrieron la app)

IMPORTANTE: el efecto del clima y el efecto de las campañas están PLANTADOS por este generador.
Sirven para practicar el método; no prueban que el clima mueva las ventas de ninguna cadena real.
"""
import os
import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)

# nombre, frio(1)/caliente(0), familia, precio, costo, popularidad base
BEB = [
    ("Americano caliente", 0, "café", 3.2, 0.9, 1.0),
    ("Latte caliente", 0, "café", 4.2, 1.3, 1.3),
    ("Capuchino", 0, "café", 4.0, 1.2, 1.0),
    ("Chocolate caliente", 0, "dulce", 4.4, 1.4, 0.8),
    ("Chai latte caliente", 0, "té", 4.5, 1.4, 0.8),
    ("Té verde caliente", 0, "té", 3.0, 0.6, 0.6),
    ("Cold brew", 1, "café", 4.6, 1.2, 1.0),
    ("Latte helado", 1, "café", 4.7, 1.4, 1.1),
    ("Frappuccino de caramelo", 1, "dulce", 5.6, 1.7, 1.2),
    ("Frappuccino de fresa", 1, "dulce", 5.6, 1.8, 0.8),
    ("Té helado de durazno", 1, "té", 3.8, 0.7, 0.9),
    ("Refresher de mango", 1, "fruta", 4.8, 1.3, 0.9),
    ("Matcha helado", 1, "té", 5.2, 1.6, 0.6),
]
bebidas = pd.DataFrame(BEB, columns=["bebida", "es_fria", "familia", "precio", "costo", "pop"])
FAMS = ["café", "dulce", "té", "fruta"]
fam_idx = bebidas["familia"].map({f: i for i, f in enumerate(FAMS)}).values
es_fria = bebidas["es_fria"].values.astype(float)
logpop = np.log(bebidas["pop"].values)
es_cafe = (bebidas["familia"] == "café").values.astype(float)
es_te = (bebidas["familia"] == "té").values.astype(float)
es_dulce = (bebidas["familia"] == "dulce").values.astype(float)

CIUDADES = [  # nombre, temp base, prob. lluvia, peso
    ("Ciudad de Guatemala", 22.5, 0.45, 0.40),
    ("Antigua Guatemala", 20.0, 0.45, 0.20),
    ("Cobán", 19.0, 0.60, 0.15),
    ("Puerto San José", 30.5, 0.35, 0.25),
]
FRANJAS = ["mañana", "tarde", "noche"]
FR_OFF = {"mañana": -2.5, "tarde": 2.0, "noche": -2.0}

# ---------- clima diario ----------
fechas = pd.date_range("2026-04-01", "2026-10-31")
filas = []
for nombre, base, pllu, _ in CIUDADES:
    for i, f in enumerate(fechas):
        lluvia = int(rng.random() < pllu)
        t = base + 1.8 * np.sin(2 * np.pi * (i - 20) / 365 * 2) + rng.normal(0, 2.4) - 1.5 * lluvia
        filas.append((f, nombre, round(t, 1), lluvia))
clima = pd.DataFrame(filas, columns=["fecha", "ciudad", "temp_c", "lluvia"])
clima.to_csv(f"{OUT}/clima_diario.csv", index=False)
clima_idx = clima.set_index(["fecha", "ciudad"])

# ---------- clientes ----------
N = 3000
pesos = np.array([c[3] for c in CIUDADES])
ciudad_cli = rng.choice([c[0] for c in CIUDADES], size=N, p=pesos / pesos.sum())
aff = rng.dirichlet([1.5, 1.0, 0.8, 0.6], size=N)                 # gusto por familia
ruido_bebida = rng.normal(0, 0.5, size=(N, len(bebidas)))           # "lo de siempre" de cada cliente
sens = np.clip(rng.normal(1.0, 0.5, size=N), 0.0, 2.0)              # cuánto le afecta el clima
tasa = rng.gamma(1.2, 7.0, size=N)                                  # órdenes en ~6 meses
clientes = pd.DataFrame({"customer_id": np.arange(1, N + 1), "ciudad": ciudad_cli})
clientes.to_csv(f"{OUT}/clientes.csv", index=False)


def utilidad(i, temp, lluvia, franja):
    """Log-puntaje de cada bebida para el cliente i en ese contexto (modelo VERDADERO, oculto a los estudiantes)."""
    u = logpop + np.log(aff[i][fam_idx] * 4) + ruido_bebida[i]
    u = u + sens[i] * 0.30 * (temp - 22.0) * es_fria                  # calor -> frías
    u = u + lluvia * (0.45 * (1 - es_fria) - 0.20 * es_fria)          # lluvia -> calientes
    if franja == "mañana":
        u = u + 0.5 * es_cafe + 0.1 * es_te
    elif franja == "noche":
        u = u + 0.4 * es_dulce - 0.7 * es_cafe
    else:
        u = u + 0.2 * es_dulce
    return u


def elegir(i, temp, lluvia, franja):
    u = utilidad(i, temp, lluvia, franja)
    p = np.exp(u - u.max()); p /= p.sum()
    return rng.choice(len(bebidas), p=p)


# ---------- órdenes abril–septiembre ----------
dias_hist = pd.date_range("2026-04-01", "2026-09-30")
filas = []
oid = 1
for i in range(N):
    n = rng.poisson(tasa[i])
    for _ in range(n):
        f = dias_hist[rng.integers(len(dias_hist))]
        ciudad = ciudad_cli[i] if rng.random() < 0.9 else CIUDADES[rng.integers(4)][0]
        fr = rng.choice(FRANJAS, p=[0.45, 0.35, 0.20])
        t_dia, llu = clima_idx.loc[(f, ciudad)]
        temp = t_dia + FR_OFF[fr]
        b = elegir(i, temp, llu, fr)
        filas.append((oid, i + 1, f, ciudad, fr, round(temp, 1), int(llu), bebidas["bebida"][b]))
        oid += 1
ordenes = pd.DataFrame(filas, columns=["order_id", "customer_id", "fecha", "ciudad", "franja", "temp_c", "lluvia", "bebida"])
ordenes.to_csv(f"{OUT}/ordenes.csv", index=False)

# ---------- experimento A/B de octubre ----------
grupos = np.array(["control", "generica", "clima"] * (N // 3))
grupos = grupos[rng.permutation(N)]
p0 = rng.beta(3.4, 16, size=N)                                      # prob. base de comprar al abrir la app
dias_oct = pd.date_range("2026-10-01", "2026-10-31")
filas = []
for i in range(N):
    for _ in range(rng.poisson(5)):
        f = dias_oct[rng.integers(len(dias_oct))]
        ciudad = ciudad_cli[i]
        fr = rng.choice(FRANJAS, p=[0.45, 0.35, 0.20])
        t_dia, llu = clima_idx.loc[(f, ciudad)]
        temp = round(t_dia + FR_OFF[fr], 1)
        extremo = int(temp >= 28 or temp <= 17)
        g = grupos[i]
        efecto = 0.0
        if g == "generica":
            efecto = 0.015
        elif g == "clima":
            efecto = 0.085 if extremo else 0.02
        compra = int(rng.random() < min(p0[i] + efecto, 0.95))
        if compra:
            b = elegir(i, temp, llu, fr)
            beb, precio, costo = bebidas["bebida"][b], bebidas["precio"][b], bebidas["costo"][b]
        else:
            beb, precio, costo = "", 0.0, 0.0
        filas.append((i + 1, g, f, ciudad, fr, temp, int(llu), extremo, compra, beb, precio,
                      round(precio - costo, 2) if compra else 0.0, 0.0 if g == "control" else 0.02))
ab = pd.DataFrame(filas, columns=["customer_id", "grupo", "fecha", "ciudad", "franja", "temp_c", "lluvia", "dia_extremo",
                                  "compro", "bebida", "gasto", "margen", "costo_envio"])
ab.to_csv(f"{OUT}/ab_test.csv", index=False)

pd.DataFrame({"customer_id": np.arange(1, N + 1), "grupo": grupos}).to_csv(f"{OUT}/ab_asignacion.csv", index=False)
bebidas.drop(columns=["pop"]).to_csv(f"{OUT}/bebidas.csv", index=False)
print("órdenes:", len(ordenes), "| clientes:", N, "| exposiciones A/B:", len(ab))
