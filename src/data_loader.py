import pandas as pd
import streamlit as st


@st.cache_data(show_spinner="Carregando dados...")
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado na última célula de notebooks/eda.ipynb)."""
    return pd.read_csv(path, parse_dates=["data_compra"])
