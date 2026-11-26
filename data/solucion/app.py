"""Panel de eventos de alarma · solución del laboratorio.

Ejecutar desde la carpeta raíz:  streamlit run solucion/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RUTA = Path(__file__).resolve().parent.parent / "data" / "eventos_alarma.csv"

st.set_page_config(page_title="Eventos de alarma", layout="wide")


@st.cache_data(ttl=600)
def cargar_eventos(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta, parse_dates=["fecha_hora"])
    df["mes"] = df["fecha_hora"].dt.strftime("%Y-%m")
    df["fecha"] = df["fecha_hora"].dt.date
    return df


def filtrar(df, provincias, tipos, desde, hasta):
    m = (df["fecha"] >= desde) & (df["fecha"] <= hasta)
    if provincias:
        m &= df["provincia"].isin(provincias)
    if tipos:
        m &= df["tipo_evento"].isin(tipos)
    return df[m]


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


df = cargar_eventos(str(RUTA))

st.title("Eventos de alarma")
st.caption("Datos sintéticos para formación")

with st.sidebar:
    st.header("Filtros")
    provincias = st.multiselect("Provincia", sorted(df["provincia"].unique()))
    tipos = st.multiselect("Tipo de evento", sorted(df["tipo_evento"].unique()))
    rango = st.date_input("Periodo", value=(df["fecha"].min(), df["fecha"].max()),
                          min_value=df["fecha"].min(), max_value=df["fecha"].max())

if not isinstance(rango, tuple) or len(rango) != 2:
    st.info("Selecciona fecha de inicio y de fin.")
    st.stop()

f = filtrar(df, provincias, tipos, rango[0], rango[1])
if f.empty:
    st.warning("No hay eventos con esos filtros.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Eventos", fmt(len(f)))
c2.metric("Falsas alarmas", f"{100 * f['falsa_alarma'].mean():.1f} %")
c3.metric("Tiempo medio de respuesta", f"{f['tiempo_resp_s'].mean():.0f} s")

t1, t2, t3 = st.tabs(["Por provincia", "Evolución mensual", "Detalle"])
with t1:
    por_prov = (f.groupby("provincia")
                  .agg(eventos=("id_evento", "count"), pct_falsas=("falsa_alarma", "mean"))
                  .reset_index().sort_values("eventos", ascending=False))
    por_prov["pct_falsas"] = (100 * por_prov["pct_falsas"]).round(1)
    st.plotly_chart(px.bar(por_prov, x="provincia", y="eventos", hover_data=["pct_falsas"]),
                    width="stretch")
with t2:
    mensual = f.groupby(["mes", "tipo_evento"]).size().reset_index(name="eventos")
    st.plotly_chart(px.line(mensual, x="mes", y="eventos", color="tipo_evento", markers=True),
                    width="stretch")
with t3:
    st.dataframe(f.drop(columns=["fecha"]).head(500), width="stretch")

st.download_button("Descargar datos filtrados (CSV)",
                   f.drop(columns=["fecha"]).to_csv(index=False).encode("utf-8"),
                   file_name="eventos_filtrados.csv", mime="text/csv")
