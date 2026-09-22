import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np

# titulo de la pagina web
st.title("Configuracion inicial")
st.write("Primera prueba de uso de streamlit y ambiente de MA2026")

# El slider de stream lit permite ingresar por un slider el parametro de inversion
gasto = st.slider("Seleccine nivel de gasto en publicicdad", 10, 200, 50)

# variables del modelo.
variable_x = np.array([[10], [20], [30], [40], [50]])
variable_y = np.array([15, 25, 35, 45, 55])
modelo_lr = LinearRegression()

modelo_lr.fit(variable_x, variable_y)

if st.button("Predecir"):
    resultado = modelo_lr.predict([[gasto]])

st.success(
    f"Las ventas proyectadas para una inversion de ${gasto} son: ${resultado[0]}"
)
