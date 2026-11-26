"""Panel de eventos de alarma · punto de partida del laboratorio.

Datos SINTÉTICOS generados con generar_datos.py.
Ejecutar:  streamlit run app.py
"""
import streamlit as st
from datos import cargar_datos

st.set_page_config(page_title="Eventos de alarma", layout="wide")
st.title("Eventos de alarma")
st.caption("Datos sintéticos para formación")

# PASO 7 del laboratorio: mueve esta carga a una función con @st.cache_data
df = cargar_datos()

with st.sidebar:
    st.header("Filtros")

    provincias = st.multiselect(
        "Provincia",
        sorted(df["provincia"].unique()),
        default=st.session_state.get("filtro_provincias", [])
    )

    st.session_state["filtro_provincias"] = provincias

    tipos = st.multiselect(
    "Tipo de evento",
    sorted(df["tipo_evento"].unique()),
    default=st.session_state.get("filtro_tipos", [])
    )

    st.session_state["filtro_tipos"] = tipos

    rango = st.date_input(
    "Periodo",
    value=(
        df["fecha_hora"].min().date(),
        df["fecha_hora"].max().date()
    ),
    min_value=df["fecha_hora"].min().date(),
    max_value=df["fecha_hora"].max().date()
    )

    st.session_state["filtro_periodo"] = rango

filtrado = df.copy()
if provincias:
    filtrado = filtrado[filtrado["provincia"].isin(provincias)]
if tipos:
    filtrado = filtrado[filtrado["tipo_evento"].isin(tipos)]

if len(rango) == 2:
    filtrado = filtrado[
        (filtrado["fecha_hora"].dt.date >= rango[0]) &
        (filtrado["fecha_hora"].dt.date <= rango[1])
    ]
# PASO 4: sustituye esta métrica por una fila de tres con st.columns(3)
c1, c2, c3 = st.columns(3)

c1.metric(
    "Eventos",
    f"{len(filtrado):,}".replace(",", ".")
)

c2.metric(
    "Falsas alarmas",
    f"{100 * filtrado['falsa_alarma'].mean():.1f} %"
)

c3.metric(
    "Tiempo medio de respuesta",
    f"{filtrado['tiempo_resp_s'].mean():.0f} s"
)

# PASO 5: crea pestañas con st.tabs y añade la evolución mensual por tipo
t1, t2, t3 = st.tabs(
    ["Por provincia", "Evolución mensual", "Detalle"]
)

with t1:
    st.bar_chart(filtrado["provincia"].value_counts())

with t2:
    evolucion = (
        filtrado
        .set_index("fecha_hora")
        .groupby("tipo_evento")
        .resample("ME")
        .size()
        .unstack(0)
    )

    st.line_chart(evolucion)

with t3:
    st.dataframe(
        filtrado.head(200),
        width="stretch"
    )
# PASO 6: añade un st.download_button para descargar `filtrado` en CSV
csv = filtrado.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados en CSV",
    data=csv,
    file_name="eventos_alarma_filtrados.csv",
    mime="text/csv"
)