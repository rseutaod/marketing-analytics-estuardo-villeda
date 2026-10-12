"""
Laboratorio Final — Starbucks Rewards (Grupo 8)
App para explorar el T-learner: curva Qini y tabla de políticas.

Correr con:  streamlit run streamlit_starter.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

st.set_page_config(
    page_title="Laboratorio Final — Starbucks Rewards", page_icon="☕", layout="wide"
)

GREEN = "#00704A"
ORANGE = "#C4512F"
GRAY = "#9A988E"
FEATURES = ["recency_days", "frequency", "monetary", "email_open_rate", "tenure_days"]

MODELOS = {
    "Regresión logística (notebook)": lambda: LogisticRegression(max_iter=1000),
    "Árbol (max_depth=4, min_samples_leaf=100)": lambda: DecisionTreeClassifier(
        max_depth=4, min_samples_leaf=100, random_state=42
    ),
    "Random Forest (depth=5, leaf=50)": lambda: RandomForestClassifier(
        n_estimators=200, max_depth=5, min_samples_leaf=50, random_state=42, n_jobs=-1
    ),
    "Gradient Boosting (depth=2, lr=0.05)": lambda: GradientBoostingClassifier(
        n_estimators=150, max_depth=2, learning_rate=0.05, random_state=42
    ),
}


@st.cache_data
def load_data():
    return pd.read_csv("data/uplift_campaign.csv")


@st.cache_data
def entrenar_t_learner(
    df: pd.DataFrame, nombre_modelo: str, test_size: float, seed: int
):
    train, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df["treatment_group"]
    )
    fabrica = MODELOS[nombre_modelo]

    train_t = train[train["treatment_group"] == "treatment"]
    train_c = train[train["treatment_group"] == "control"]
    modelo_tratado = fabrica().fit(train_t[FEATURES], train_t["responded_60d"])
    modelo_control = fabrica().fit(train_c[FEATURES], train_c["responded_60d"])

    test = test.copy()
    X_test = test[FEATURES]
    test["p_tratado"] = modelo_tratado.predict_proba(X_test)[:, 1]
    test["p_control"] = modelo_control.predict_proba(X_test)[:, 1]
    test["uplift_estimado"] = test["p_tratado"] - test["p_control"]
    return train, test


def valor_de_la_politica(test_df, seleccionados):
    sel = test_df.loc[seleccionados]
    valor_tratado = sel.loc[
        sel["treatment_group"] == "treatment", "utilidad_neta_60d"
    ].mean()
    valor_control = sel.loc[sel["treatment_group"] == "control", "margin_60d"].mean()
    return valor_tratado - valor_control, len(sel)


def curva_qini(test_df, score_col, steps=40):
    orden = test_df.sort_values(score_col, ascending=False).reset_index(drop=True)
    es_tratado = (orden["treatment_group"] == "treatment").values
    respondio = orden["responded_60d"].values
    acum_t = np.cumsum(np.where(es_tratado, respondio, 0))
    acum_c = np.cumsum(np.where(~es_tratado, respondio, 0))
    n_t = np.cumsum(es_tratado)
    n_c = np.cumsum(~es_tratado)
    n = len(orden)
    xs, ys = [0.0], [0.0]
    # se parte de n/steps (no de 1 cliente) para evitar un pico artificial en x=0
    for i in np.linspace(n / steps, n, steps).astype(int):
        nt, nc = n_t[i - 1], n_c[i - 1]
        tasa_t = acum_t[i - 1] / nt if nt > 0 else 0
        tasa_c = acum_c[i - 1] / nc if nc > 0 else 0
        xs.append(i / n)
        ys.append((tasa_t - tasa_c) * n)
    return np.array(xs), np.array(ys)


def coeficiente_qini(xs, ys, n):
    area_modelo = np.trapezoid(ys, xs)
    area_azar = np.trapezoid(np.linspace(0, ys[-1], len(xs)), xs)
    return (area_modelo - area_azar) / n


@st.cache_data
def tabla_de_politicas(_test: pd.DataFrame, clave: str, paso: int):
    orden = _test.sort_values("uplift_estimado", ascending=False)
    filas = []
    for pct in range(paso, 101, paso):
        idx = orden.head(int(len(_test) * pct / 100)).index
        v, n = valor_de_la_politica(_test, idx)
        filas.append(
            {
                "% contactado": pct,
                "Clientes contactados": n,
                "Valor por cliente ($)": round(v, 2),
                "Valor total ($)": round(v * n, 0),
            }
        )
    return pd.DataFrame(filas)


# --- Título ---
st.title("☕ Starbucks Rewards — ¿a qué % de la base mandamos el cupón?")
st.caption(
    "Esta app ayuda a decidir **a cuántos clientes enviar el cupón de $5** para maximizar la utilidad neta: "
    "ordena a los clientes por cuánto *cambia* el cupón su compra (uplift) y muestra dónde deja de convenir contactar."
)

df = load_data()

with st.sidebar:
    st.header("Parámetros")
    nombre_modelo = st.selectbox("Modelo dentro del T-learner", list(MODELOS), index=0)
    pct_contactar = st.slider(
        "% de la base a contactar", min_value=5, max_value=100, value=20, step=5
    )
    st.markdown("---")
    st.caption(
        "Base: 40,000 clientes, mitad con cupón y mitad control, medidos a 60 días. "
        "Evaluación sobre el 30% de clientes que el modelo nunca vio."
    )

train, test = entrenar_t_learner(df, nombre_modelo, test_size=0.30, seed=42)
n_test = len(test)

# --- Qini ---
xs, ys = curva_qini(test, "uplift_estimado")
qini = coeficiente_qini(xs, ys, n_test)

tabla = tabla_de_politicas(test, nombre_modelo, 5)
mejor = tabla.loc[tabla["Valor total ($)"].idxmax()]

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Curva Qini del T-learner")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        xs * 100, ys, color=GREEN, linewidth=3, label=f"T-learner (Qini = {qini:+.3f})"
    )
    ax.plot([0, 100], [0, ys[-1]], color=GRAY, linestyle="--", label="Al azar")
    ax.axvline(
        pct_contactar,
        color=ORANGE,
        linewidth=2,
        linestyle=":",
        label=f"Elegido: {pct_contactar}%",
    )
    ax.set_xlabel("% de la base contactada (ordenada por uplift estimado)")
    ax.set_ylabel("Respuestas incrementales acumuladas")
    ax.legend(loc="upper right")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    st.caption(
        "Mientras más alta quede la curva sobre la diagonal, mejor ordena el modelo: los primeros clientes de la lista son los que más compran *gracias* al cupón."
    )

with col2:
    st.subheader(f"Política: contactar al {pct_contactar}%")
    orden = test.sort_values("uplift_estimado", ascending=False)
    idx = orden.head(int(n_test * pct_contactar / 100)).index
    v, n = valor_de_la_politica(test, idx)
    m1, m2 = st.columns(2)
    m1.metric("Valor por cliente", f"${v:+.2f}")
    m2.metric("Valor total (muestra de prueba)", f"${v * n:+,.0f}")
    escala = len(df) / n_test
    st.metric(
        "Valor total proyectado a toda la base (40,000)", f"${v * n * escala:+,.0f}"
    )
    if v * n < 0:
        st.error(
            "Con este % se **destruye** valor: el cupón cuesta más de lo que genera."
        )
    elif pct_contactar >= mejor["% contactado"] + 15:
        st.warning(
            "Estás por encima del % que maximiza el valor total: los últimos clientes ya restan."
        )
    else:
        st.success("Este % deja valor neto positivo.")
    st.info(
        f"**% que maximiza el valor total con este modelo:** {int(mejor['% contactado'])}% "
        f"(${mejor['Valor total ($)']:+,.0f} en la muestra de prueba)."
    )

st.subheader("Tabla de políticas (Paso 3)")
tabla_mostrar = tabla.copy()
tabla_mostrar["Elegido"] = np.where(
    tabla_mostrar["% contactado"] == pct_contactar, "◀", ""
)
st.dataframe(
    tabla_mostrar.style.format(
        {
            "Valor por cliente ($)": "{:+.2f}",
            "Valor total ($)": "{:+,.0f}",
            "Clientes contactados": "{:,}",
        }
    ).apply(
        lambda r: [
            "background-color: #d7ede4" if r["% contactado"] == pct_contactar else ""
            for _ in r
        ],
        axis=1,
    ),
    hide_index=True,
)
st.caption(
    "**Por qué el % óptimo por cliente y el % óptimo total no coinciden:** el valor por cliente es un promedio y se maximiza con "
    "los clientes más prometedores; el total sigue creciendo mientras el *último* cliente contactado aporte valor positivo. "
    "Los valores salen del experimento (tratados vs. control) y tienen ruido de muestreo: diferencias pequeñas entre % cercanos no son concluyentes."
)
