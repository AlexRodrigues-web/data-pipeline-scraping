"""
Streamlit dashboard - Books Analytics
Inclui logging em arquivo logs/streamlit.log e no console.
"""

import os
import logging
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# ---------- LOGGING ----------
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "streamlit.log")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("streamlit_app")
logger.setLevel(logging.INFO)
logger.propagate = False  # evita logs duplicados no console do Streamlit

if not logger.handlers:
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    ch = logging.StreamHandler()
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)

# ---------- CONFIG ----------
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)

st.set_page_config(page_title="Books Analytics", layout="wide")
st.title("📚 Books Analytics — Demo")

# ---------- DB HELPERS ----------
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

@st.cache_data(show_spinner=False, ttl=60)
def load_data(limit=5000):
    logger.info("Carregando dados do DB...")
    try:
        engine = get_engine()
        # Use placeholder do psycopg2 (pyformat), não ':nome'
        query = """
            select title, price_gbp, rating, load_date
            from analytics.dim_books
            order by load_date desc, title asc
            limit %(lim)s
        """
        df = pd.read_sql(query, engine, params={"lim": int(limit)})

        # tipos numéricos para filtros/gráficos
        df["price_gbp"] = pd.to_numeric(df["price_gbp"], errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
        logger.info("Linhas carregadas: %d", len(df))
        return df
    except Exception:
        logger.exception("Falha ao carregar dados do banco.")
        raise

# ---------- UI ----------
try:
    df = load_data()

    if df.empty:
        st.warning("Sem dados na tabela `analytics.dim_books` ainda. Rode o DAG no Airflow e depois `dbt run`.")
        st.stop()

    # Ratings realmente presentes
    ratings_present = sorted(int(x) for x in df["rating"].dropna().unique().tolist())
    if not ratings_present:
        st.warning("Os registros atuais não possuem 'rating' (1–5). Ajuste a extração/transformação.")
        st.dataframe(df, use_container_width=True)
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        rating_sel = st.multiselect(
            "Filtrar por rating",
            options=[1, 2, 3, 4, 5],
            default=ratings_present,
        )

    # Slider seguro mesmo se todos os preços forem NaN; se não houver preços válidos,
    # NÃO aplicamos filtro de preço (mantém registros só pelo rating)
    valid_prices = df["price_gbp"].dropna()
    with col2:
        if valid_prices.empty:
            st.warning("Não há preços válidos na base ainda (todos NULL). O filtro de preço foi desativado.")
            price_range = None  # sinaliza "sem filtro de preço"
        else:
            price_min = float(valid_prices.min())
            price_max = float(valid_prices.max())
            if price_min == price_max:  # dá um respiro ao slider
                price_min = 0.0
            price_range = st.slider(
                "Faixa de preço (GBP)",
                min_value=float(price_min),
                max_value=float(price_max),
                value=(float(price_min), float(price_max)),
            )

    # Aplicar filtros
    mask = df["rating"].isin(rating_sel)
    if price_range is not None:
        mask = mask & df["price_gbp"].between(price_range[0], price_range[1], inclusive="both")

    filtered = df[mask].copy()

    st.subheader("Tabela")
    if filtered.empty:
        st.info("Sem dados para esses filtros. Ajuste rating e/ou faixa de preço.")
        st.dataframe(df, use_container_width=True)  # Mostra o bruto para orientar
        st.stop()
    else:
        st.dataframe(filtered, use_container_width=True)

    st.subheader("Preço médio por rating")
    mean_df = (
        filtered.dropna(subset=["price_gbp", "rating"])
                .groupby("rating", dropna=False)["price_gbp"]
                .mean()
                .reset_index()
                .sort_values("rating")
    )
    if not mean_df.empty:
        st.bar_chart(mean_df, x="rating", y="price_gbp")
    else:
        st.info("Não há valores de preço para calcular o gráfico.")

    st.caption("Dica: atualize o DAG diariamente para novos dados. Logs em `streamlit/logs/streamlit.log`.")
except Exception as e:
    st.error("Falha ao carregar/exibir dados. Verifique os logs.")
    st.exception(e)
