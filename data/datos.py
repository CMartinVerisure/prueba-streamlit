import pandas as pd
import streamlit as st


@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "data/eventos_alarma.csv",
        parse_dates=["fecha_hora"]
    )
    return df
    