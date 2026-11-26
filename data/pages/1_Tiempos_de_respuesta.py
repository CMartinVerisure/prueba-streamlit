import streamlit as st
from datos import cargar_datos

st.set_page_config(page_title="Tiempos de respuesta", layout="wide")

st.title("Tiempos de respuesta")
st.caption("Análisis de los tiempos de respuesta de los eventos de alarma")

df = cargar_datos()
filtrado = df.copy()

provincias = st.session_state.get("filtro_provincias", [])
tipos = st.session_state.get("filtro_tipos", [])
rango = st.session_state.get("filtro_periodo", [])

if provincias:
    filtrado = filtrado[filtrado["provincia"].isin(provincias)]

if tipos:
    filtrado = filtrado[filtrado["tipo_evento"].isin(tipos)]

if len(rango) == 2:
    filtrado = filtrado[
        (filtrado["fecha_hora"].dt.date >= rango[0]) &
        (filtrado["fecha_hora"].dt.date <= rango[1])
    ]

st.caption(f"Eventos analizados: {len(filtrado):,}".replace(",", "."))

if provincias:
    st.caption(f"Provincia seleccionada: {', '.join(provincias)}")

if tipos:
    st.caption(f"Tipo de evento seleccionado: {', '.join(tipos)}")
 
st.subheader("Selecciona el percentil")

percentil = st.select_slider(
    "Percentil",
    options=[50, 75, 90, 95],
    value=90
)

st.write(f"Percentil seleccionado: P{percentil}")

st.subheader("Tiempo de respuesta por tipo de evento")

tabla_percentiles = (
    filtrado.groupby("tipo_evento")["tiempo_resp_s"]
    .quantile(percentil / 100)
    .reset_index()
)

tabla_percentiles.columns = [
    "Tipo de evento",
    f"P{percentil} (segundos)"
]

tabla_percentiles = tabla_percentiles.sort_values(
    f"P{percentil} (segundos)",
    ascending=False
)

st.dataframe(
    tabla_percentiles,
    width="stretch",
    hide_index=True
)

peor_tipo = tabla_percentiles.iloc[0]["Tipo de evento"]
peor_tiempo = tabla_percentiles.iloc[0][f"P{percentil} (segundos)"]

st.info(
    f"Para el percentil P{percentil}, el tipo de evento con mayor "
    f"tiempo de respuesta es **{peor_tipo}**, con **{peor_tiempo:.1f} segundos**."
)
st.subheader("Tiempo de respuesta por hora del día")

df_horas = filtrado.copy()

df_horas["hora"] = df_horas["fecha_hora"].dt.hour

respuesta_hora = (
    df_horas.groupby("hora")["tiempo_resp_s"]
    .quantile(percentil / 100)
)

st.bar_chart(respuesta_hora)
