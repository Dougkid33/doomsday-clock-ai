import os
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from clock_component import get_clock_html
from infra.repository import SQLiteRepo
from application.use_cases import refresh_pipeline
from infra.official_clock import fetch_official_clock
from infra.official_timeline import fetch_timeline_from_wikipedia

DB_PATH = os.path.join("data", "doomsday.db")

st.set_page_config(page_title="Doomsday Clock AI", layout="wide")

# ---------------------------
# State / Controls
# ---------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

st.sidebar.title("Controles")
st.session_state.theme = st.sidebar.radio(
    "Tema",
    ["dark", "light"],
    index=0 if st.session_state.theme == "dark" else 1
)

repo = SQLiteRepo(DB_PATH)

# ---------------------------
# Data Refresh (cached)
# ---------------------------
@st.cache_data(ttl=1800)  # 30 min
def run_refresh():
    # Não passe objetos não-serializáveis pro cache.
    # Aqui funciona porque o refresh_pipeline usa o repo internamente.
    return refresh_pipeline(repo)

@st.cache_data(ttl=86400)  # 24h, oficial muda raramente
def get_official_clock():
    return fetch_official_clock()

@st.cache_data(ttl=86400)
def get_official_timeline():
    return fetch_timeline_from_wikipedia()

# Rodar refresh 1x por execução do app
info = run_refresh()

# Botão manual para forçar refresh
if st.sidebar.button("Atualizar agora (coletar + recalcular)"):
    run_refresh.clear()
    info = run_refresh()
    st.sidebar.success(
        f"Atualizado. Coletado: {info['items_collected']} | Scored: {info['items_scored']}"
    )

# ---------------------------
# Tabs
# ---------------------------
tab_overview, tab_feed, tab_method, tab_history = st.tabs([
    "Overview",
    "Feed",
    "Metodologia",
    "Histórico"
])

# ---------------------------
# Overview
# ---------------------------
with tab_overview:
    st.subheader("Visão Geral")

    c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="center")
    with c2:
        st.metric("Risco Global (0–1)", f"{info['global_risk']:.2f}")
    with c3:
        st.metric("Seu modelo — minutos", f"{info['minutes_to_midnight']:.2f}")

    # --- oficial com proteção ---
    st.markdown("### Comparação com o Doomsday Clock oficial")

    try:
        official = get_official_clock()

        left, right = st.columns([1, 1])
        with left:
            st.metric("Oficial (Bulletin) — segundos", f"{official.seconds_to_midnight}")
            if official.as_of:
                st.caption(f"Atualizado em: {official.as_of.isoformat()}")
            st.caption("Fonte oficial: Bulletin (link na aba Metodologia)")

        with right:
            model_seconds = int(info["minutes_to_midnight"] * 60)
            st.metric("Seu modelo — segundos", f"{model_seconds}")
            delta_sec = model_seconds - official.seconds_to_midnight
            st.metric("Delta (modelo - oficial) em segundos", f"{delta_sec:+d}")

    except Exception as e:
        st.warning("Não foi possível carregar o valor oficial agora (falha de rede ou parsing).")
        st.caption(str(e))

    st.divider()

    # --- relógio visual ---
    clock_html = get_clock_html(info["minutes_to_midnight"], theme=st.session_state.theme)
    components.html(clock_html, height=560)

    st.caption("⚠️ Índice experimental baseado em RSS + análise automática. Não é o Doomsday Clock oficial.")
# ---------------------------
# Feed (com filtros por fonte e categoria)
# ---------------------------
with tab_feed:
    st.subheader("Feed de Inteligência")

    rows = repo.fetch_latest(limit=250)
    df = pd.DataFrame(rows, columns=[
        "source", "category", "title", "url", "published_at", "risk", "label", "summary"
    ])

    # normaliza
    if df.empty:
        st.info("Sem dados ainda. Clique em 'Atualizar agora' no menu lateral.")
    else:
        df["risk"] = df["risk"].fillna(0.0)
        df["label"] = df["label"].fillna("N/A")
        df["category"] = df["category"].fillna("Geral")

        # filtros
        sources = ["Todas"] + sorted(df["source"].dropna().unique().tolist())
        categories = ["Todas"] + sorted(df["category"].dropna().unique().tolist())
        labels = ["Todos", "Baixo", "Médio", "Alto", "Crítico", "N/A"]

        f1, f2, f3 = st.columns(3)
        sel_source = f1.selectbox("Fonte", sources)
        sel_cat = f2.selectbox("Categoria", categories)
        sel_label = f3.selectbox("Nível", labels)

        dff = df.copy()
        if sel_source != "Todas":
            dff = dff[dff["source"] == sel_source]
        if sel_cat != "Todas":
            dff = dff[dff["category"] == sel_cat]
        if sel_label != "Todos":
            dff = dff[dff["label"] == sel_label]

        # ordena por risco (desc) e recência (desc)
        # published_at pode ser string ISO, então ordena como string funciona ok, mas vamos converter se possível
        try:
            dff["published_at_dt"] = pd.to_datetime(dff["published_at"], errors="coerce")
            dff = dff.sort_values(["risk", "published_at_dt"], ascending=[False, False])
        except Exception:
            dff = dff.sort_values(["risk", "published_at"], ascending=[False, False])

        # cards
        for _, r in dff.head(30).iterrows():
            st.markdown(
                f"""
                <div style="
                  padding:14px 16px;
                  border-radius:14px;
                  border:1px solid rgba(255,255,255,0.08);
                  background: rgba(0,0,0,0.18);
                  margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-weight:800;font-size:14px;">
                      {r['source']} • {r['category']}
                    </div>
                    <div style="font-weight:900;">
                      RISCO {int(float(r['risk']) * 100)}
                    </div>
                  </div>
                  <div style="margin-top:6px;font-size:16px;font-weight:800;">
                    {r['title']}
                  </div>
                  <div style="margin-top:6px;opacity:0.8;">
                    {str(r['summary'])[:240]}...
                  </div>
                  <div style="margin-top:8px;">
                    <a href="{r['url']}" target="_blank">Abrir fonte</a>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------------------------
# Metodologia
# ---------------------------
with tab_method:
    st.subheader("Metodologia")

    st.markdown("""
**Como o risco é calculado (0..1):**

- **Sentimento (VADER):** textos mais negativos aumentam risco  
- **Palavras-chave:** termos de risco existencial (guerra, nuclear, pandemia, IA, clima)  
- **Peso por fonte:** fontes reconhecidas têm peso maior  
- **Recência:** notícias recentes pesam mais  

O risco global é a **média** dos scores mais recentes.  
Depois convertemos risco → **minutos para midnight** (calibrado para não colapsar em 0.1).

> Este sistema é experimental e serve como demo de pipeline/arquitetura + visualização.
""")

# ---------------------------
# Histórico (Plotly)
# ---------------------------
with tab_history:
    st.subheader("Histórico")

    import plotly.express as px

    # --- 1) Histórico oficial (Bulletin/Wiki) ---
    st.markdown("### Doomsday Clock — Histórico oficial (segundos para meia-noite)")

    try:
        timeline = get_official_timeline()
        df_off = pd.DataFrame(
            [{"year": p.year, "seconds": p.seconds_to_midnight} for p in timeline]
        ).sort_values("year")

        fig_off = px.line(
            df_off,
            x="year",
            y="seconds",
            title="Histórico oficial — segundos para meia-noite",
        )
        st.plotly_chart(fig_off, width="stretch")

    except Exception as e:
        st.warning(
            "Não foi possível carregar o histórico oficial agora (falha de rede ou parsing). "
            "Tente novamente mais tarde."
        )
        st.caption(str(e))

    st.divider()

    # --- 2) Histórico do seu risco (SQLite) ---
    st.markdown("### Seu modelo — evolução do risco médio (0..1)")

    hist = repo.fetch_risk_history(limit=500)

    if not hist:
        st.info("Sem histórico ainda. Use 'Atualizar agora' algumas vezes para gerar dados.")
    else:
        dfh = pd.DataFrame(hist, columns=["timestamp", "risk"])
        dfh["timestamp"] = pd.to_datetime(dfh["timestamp"], errors="coerce")
        dfh = dfh.dropna(subset=["timestamp"]).sort_values("timestamp")

        fig_risk = px.line(
            dfh,
            x="timestamp",
            y="risk",
            title="Evolução do risco médio (seu modelo)",
        )
        st.plotly_chart(fig_risk, width="stretch")