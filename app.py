import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Olist · Distribuição, Correlação e KPIs de Logística",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
# Variáveis quantitativas do estudo (as mesmas analisadas na seção 8 da EDA)
VARS_QUANT = {
    "valor_pago": "Valor pago (R$)",
    "valor_produtos": "Valor dos produtos (R$)",
    "valor_frete": "Frete (R$)",
    "n_itens": "Nº de itens",
    "parcelas": "Parcelas",
    "peso_total_g": "Peso total (g)",
    "dias_entrega": "Dias até a entrega",
    "dias_prometidos": "Prazo prometido (dias)",
    "dias_atraso": "Dias de atraso",
    "review_score": "Nota de avaliação",
}
PADRAO = ["valor_pago", "valor_frete", "peso_total_g", "dias_entrega", "dias_atraso", "review_score"]
REGIOES = ["Sudeste", "Sul", "Centro-Oeste", "Nordeste", "Norte"]

COR_PRINCIPAL = "#1f5fbf"
COR_NO_PRAZO = "#1baf7a"
COR_ATRASADO = "#e34948"
CORES_SITUACAO = alt.Scale(domain=["No prazo", "Atrasado"], range=[COR_NO_PRAZO, COR_ATRASADO])


def nome(col):
    return VARS_QUANT.get(col, col)


def fmt(v, casas=1, sufixo=""):
    """Número no padrão brasileiro (1.234,5)."""
    if pd.isna(v):
        return "–"
    numero = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return numero + sufixo


df = load_data()
df["situacao_entrega"] = df["atrasado"].map({0: "No prazo", 1: "Atrasado"})

st.title("Olist · E-commerce brasileiro (2017–2018)")
st.caption(
    "Fonte: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) "
    "· ~99 mil pedidos · EDA completa em `notebooks/eda.ipynb`"
)

# ---------------------------------------------------------------------------
# Sidebar: filtros (valem para as duas abas)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=list(VARS_QUANT),
        default=PADRAO,
        format_func=nome,
        help="Variáveis usadas no mapa de calor e nos histogramas do Dashboard 1.",
    )

    faixa_nota = st.slider(
        "Nota de avaliação (intervalo)",
        min_value=1,
        max_value=5,
        value=(1, 5),
        step=1,
        help="Exclui da análise os pedidos com nota fora do intervalo. Ex.: (1, 2) mostra só clientes insatisfeitos.",
    )

    corte_outlier = st.slider(
        "Remover outliers acima do percentil",
        min_value=90,
        max_value=100,
        value=99,
        step=1,
        help="Dashboard 1: para cada variável selecionada, descarta pedidos acima desse percentil. 100 = não remove nada.",
    )

    regioes = st.multiselect("Região do cliente", options=REGIOES, help="Vazio = todas as regiões.")

    colorir_situacao = st.toggle(
        "Distinguir no prazo × atrasado",
        value=False,
        help="Colore os histogramas pela situação da entrega (só pedidos entregues).",
    )

# ---------------------------------------------------------------------------
# Aplicação dos filtros
# ---------------------------------------------------------------------------
# Filtros comuns às duas abas: nota e região
df_base = df
if faixa_nota != (1, 5):
    df_base = df_base[df_base["review_score"].between(*faixa_nota)]
if regioes:
    df_base = df_base[df_base["regiao"].isin(regioes)]

# Dashboard 1 também corta os outliers das variáveis selecionadas
df_filtrado = df_base
if corte_outlier < 100:
    for var in variaveis:
        if var == "review_score":
            continue  # nota é discreta (1–5): o corte é feito pelo slider de nota
        limite = df_filtrado[var].quantile(corte_outlier / 100)
        df_filtrado = df_filtrado[df_filtrado[var].isna() | (df_filtrado[var] <= limite)]

st.sidebar.caption(f"**{fmt(len(df_filtrado), 0)}** de {fmt(len(df), 0)} pedidos no Dashboard 1")

aba_lab, aba_kpi = st.tabs([" Dashboard 1 · Laboratório", " Dashboard 2 · KPIs de Logística"])

# ---------------------------------------------------------------------------
# Dashboard 1: laboratório de distribuição e correlação
# ---------------------------------------------------------------------------


def histograma(dados, var, nbins, por_situacao):
    """Histograma em Altair a partir de contagens pré-calculadas (leve mesmo com ~95 mil pedidos)."""
    serie = dados[var].dropna()
    if por_situacao:
        dados = dados.dropna(subset=[var, "situacao_entrega"])
        serie = dados[var]
    if var == "review_score":  # variável discreta: uma barra por nota
        bordas = np.arange(0.5, 6.5, 1.0)
    else:
        bordas = np.histogram_bin_edges(serie, bins=nbins)
    partes = []
    grupos = dados.groupby("situacao_entrega")[var] if por_situacao else [("Todos", serie)]
    for grupo, valores in grupos:
        contagem, _ = np.histogram(valores.dropna(), bins=bordas)
        partes.append(pd.DataFrame({"inicio": bordas[:-1], "fim": bordas[1:], "pedidos": contagem, "grupo": grupo}))
    tabela = pd.concat(partes, ignore_index=True)

    barras = alt.Chart(tabela).mark_bar(binSpacing=1).encode(
        x=alt.X("inicio:Q", bin="binned", title=nome(var)),
        x2="fim:Q",
        y=alt.Y("pedidos:Q", title="Pedidos", stack=True),
        tooltip=[
            alt.Tooltip("inicio:Q", title="de", format=",.1f"),
            alt.Tooltip("fim:Q", title="até", format=",.1f"),
            alt.Tooltip("pedidos:Q", title="pedidos", format=","),
        ],
    )
    if por_situacao:
        barras = barras.encode(
            color=alt.Color("grupo:N", title=None, scale=CORES_SITUACAO, legend=alt.Legend(orient="top")),
            tooltip=[
                alt.Tooltip("grupo:N", title="situação"),
                alt.Tooltip("inicio:Q", title="de", format=",.1f"),
                alt.Tooltip("fim:Q", title="até", format=",.1f"),
                alt.Tooltip("pedidos:Q", title="pedidos", format=","),
            ],
        )
    else:
        barras = barras.mark_bar(binSpacing=1, color=COR_PRINCIPAL)

    media = alt.Chart(pd.DataFrame({"x": [serie.mean()], "rotulo": [f"média {fmt(serie.mean())}"]})).mark_rule(
        strokeDash=[5, 4], color="#333333"
    ).encode(x="x:Q", tooltip=alt.Tooltip("rotulo:N", title="média"))

    return (barras + media).properties(title=nome(var), height=230)


with aba_lab:
    st.subheader("Laboratório de distribuição e correlação")
    st.caption(
        f"{fmt(len(df_filtrado), 0)} de {fmt(len(df), 0)} pedidos dentro dos filtros · "
        f"nota entre {faixa_nota[0]} e {faixa_nota[1]} · "
        + (f"outliers acima do p{corte_outlier} removidos" if corte_outlier < 100 else "sem corte de outliers")
    )

    if df_filtrado.empty:
        st.warning("Nenhum pedido com esses filtros. Amplie o intervalo de nota ou as regiões.")
    elif not variaveis:
        st.info("Selecione pelo menos uma variável na barra lateral.")
    else:
        col_correlacao, col_distribuicao = st.columns([1, 1.4], gap="large")

        with col_correlacao:
            st.markdown("#### Correlação")
            if len(variaveis) < 2:
                st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
            else:
                metodo = st.radio(
                    "Método",
                    ["pearson", "spearman"],
                    horizontal=True,
                    format_func=lambda m: {"pearson": "Pearson (linear)", "spearman": "Spearman (ordem)"}[m],
                    help="Spearman é mais robusto a outliers e a relações não lineares.",
                )
                rotulos = [nome(v) for v in variaveis]
                corr = (
                    df_filtrado[variaveis]
                    .corr(method=metodo)
                    .rename(index=nome, columns=nome)
                    .rename_axis(index="var_y", columns="var_x")
                    .stack()
                    .rename("correlacao")
                    .reset_index()
                )
                # Só o triângulo inferior, sem a diagonal: a matriz é simétrica e a diagonal é sempre 1
                ordem = {r: i for i, r in enumerate(rotulos)}
                corr = corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]

                base = alt.Chart(corr).encode(
                    x=alt.X("var_x:N", title=None, sort=rotulos[:-1], axis=alt.Axis(labelAngle=-35, labelLimit=140)),
                    y=alt.Y("var_y:N", title=None, sort=rotulos[1:], axis=alt.Axis(labelLimit=160)),
                )
                mapa = base.mark_rect().encode(
                    color=alt.Color(
                        "correlacao:Q",
                        title="r",
                        scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
                    ),
                    tooltip=[
                        alt.Tooltip("var_x:N", title="variável"),
                        alt.Tooltip("var_y:N", title="× variável"),
                        alt.Tooltip("correlacao:Q", title="correlação", format=".2f"),
                    ],
                )
                valores = base.mark_text(fontSize=13).encode(
                    text=alt.Text("correlacao:Q", format=".2f"),
                    color=alt.condition("abs(datum.correlacao) > 0.5", alt.value("white"), alt.value("black")),
                )
                st.altair_chart(
                    (mapa + valores).properties(height=420),
                    width="stretch",
                    alt="Mapa de calor da correlação entre as variáveis quantitativas selecionadas",
                )

                pares = corr.assign(par=corr["var_y"] + " × " + corr["var_x"], abs_r=corr["correlacao"].abs())
                pares = pares.sort_values("abs_r", ascending=False).head(5)
                st.markdown("**Pares mais correlacionados**")
                st.dataframe(
                    pares[["par", "correlacao"]].rename(columns={"par": "Par", "correlacao": "r"}).round(2),
                    hide_index=True,
                    width="stretch",
                )

        with col_distribuicao:
            st.markdown("#### Distribuição")
            nbins = st.slider("Nº de barras dos histogramas", 10, 60, 30, step=5)
            for inicio in range(0, len(variaveis), 2):
                colunas = st.columns(2)
                for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                    with coluna:
                        st.altair_chart(
                            histograma(df_filtrado, var, nbins, colorir_situacao),
                            width="stretch",
                            alt=f"Histograma de {nome(var)}",
                        )

        with st.expander("Estatísticas descritivas das variáveis selecionadas"):
            desc = df_filtrado[variaveis].describe().T
            desc.index = [nome(v) for v in desc.index]
            st.dataframe(desc.round(2), width="stretch")

        st.info(
            "**Como ler:** a nota de avaliação tem correlação **negativa** com dias de entrega e dias de atraso: "
            "quanto mais demora, menor a nota. Valor e frete quase não se relacionam com a nota. "
            "Experimente o slider de nota em (1, 2) e ligue *Distinguir no prazo × atrasado*."
        )

# ---------------------------------------------------------------------------
# Dashboard 2: KPIs para a Gerência de Logística
# ---------------------------------------------------------------------------
FAIXAS_DIAS = [0, 5, 10, 15, 20, 30, 45, 1000]
ROTULOS_DIAS = ["0–5", "6–10", "11–15", "16–20", "21–30", "31–45", "45+"]


def kpis_logistica(dados):
    """Métricas do Dashboard 2, calculadas sobre os pedidos entregues."""
    ent = dados[dados["dias_entrega"].notna()]
    return {
        "pct_no_prazo": (1 - ent["atrasado"].mean()) * 100,
        "prazo_medio": ent["dias_entrega"].mean(),
        "folga_media": (ent["dias_prometidos"] - ent["dias_entrega"]).mean(),
        "frete_sobre_valor": dados["valor_frete"].sum() / dados["valor_pago"].sum() * 100,
        "nota_atrasados": ent.loc[ent["atrasado"] == 1, "review_score"].mean(),
        "nota_no_prazo": ent.loc[ent["atrasado"] == 0, "review_score"].mean(),
    }


def ufs_clicadas():
    """Estados clicados no gráfico por UF (seleção do Altair guardada pelo Streamlit no session_state)."""
    estado = st.session_state.get("grafico_uf")
    if not estado:
        return []
    itens = estado.get("selection", {}).get("uf_clicada", [])
    return sorted({item["uf"] for item in itens if "uf" in item})


with aba_kpi:
    st.subheader("KPIs de Logística · público-alvo: Gerência de Logística / Operações")
    st.caption(
        "Pergunta da gerência: **estamos entregando no prazo, onde falhamos e quanto isso custa em satisfação?** "
        "Valem os filtros de nota e região da barra lateral (o corte de outliers é só do Dashboard 1, "
        "para não esconder os piores atrasos)."
    )

    # ignora estados clicados que saíram do filtro da sidebar (ex.: trocou a região depois de clicar)
    ufs_sel = [uf for uf in ufs_clicadas() if uf in set(df_base["uf"])]
    df_sel = df_base[df_base["uf"].isin(ufs_sel)] if ufs_sel else df_base
    if ufs_sel:
        st.info(f"Filtrando pelos estados clicados no gráfico: **{', '.join(ufs_sel)}**. "
                "Clique numa área vazia do gráfico por estado para limpar.")

    if df_sel["dias_entrega"].notna().sum() == 0:
        st.warning("Nenhum pedido entregue com esses filtros. Amplie o intervalo de nota ou as regiões.")
    else:
        k, geral = kpis_logistica(df_sel), kpis_logistica(df)
        filtrado = len(df_sel) < len(df)

        def delta(chave, casas=1, sufixo=""):
            return f"{fmt(k[chave] - geral[chave], casas, sufixo)} vs. total" if filtrado else None

        # --- Métricas (5)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Entregas no prazo", fmt(k["pct_no_prazo"], 1, " %"), delta("pct_no_prazo", 1, " p.p."),
                  help="% dos pedidos entregues até a data prometida.")
        m2.metric("Prazo médio de entrega", fmt(k["prazo_medio"], 1, " dias"), delta("prazo_medio", 1, " d"),
                  delta_color="inverse", help="Dias entre a compra e a entrega ao cliente.")
        m3.metric("Folga média do prazo", fmt(k["folga_media"], 1, " dias"), delta("folga_media", 1, " d"),
                  help="Prazo prometido − prazo real. Quanto maior, mais 'colchão' a Olist dá na promessa.")
        m4.metric("Frete / valor pago", fmt(k["frete_sobre_valor"], 1, " %"), delta("frete_sobre_valor", 1, " p.p."),
                  delta_color="inverse", help="Quanto do dinheiro pago pelo cliente vai para o frete.")
        m5.metric("Nota dos atrasados", fmt(k["nota_atrasados"], 2, " ★"),
                  f"{fmt(k['nota_atrasados'] - k['nota_no_prazo'], 2)} vs. no prazo",
                  help="Nota média dos pedidos atrasados, comparada com a dos entregues no prazo.")

        ent = df_sel[df_sel["dias_entrega"].notna()]

        # --- Visual 1: % de atraso por mês
        mensal = (ent.groupby("ano_mes")
                     .agg(pct_atraso=("atrasado", "mean"), pedidos=("atrasado", "size"))
                     .assign(pct_atraso=lambda x: x["pct_atraso"] * 100)
                     .reset_index())
        media_periodo = 100 - k["pct_no_prazo"]
        linha = alt.Chart(mensal).mark_line(point=True, color=COR_ATRASADO, strokeWidth=2.5).encode(
            x=alt.X("ano_mes:O", title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("pct_atraso:Q", title="% de entregas atrasadas"),
            tooltip=[alt.Tooltip("ano_mes:O", title="mês"),
                     alt.Tooltip("pct_atraso:Q", title="% atrasadas", format=".1f"),
                     alt.Tooltip("pedidos:Q", title="pedidos entregues", format=",")],
        )
        media = alt.Chart(pd.DataFrame({"y": [media_periodo]})).mark_rule(strokeDash=[6, 4], color="#555555").encode(
            y="y:Q", tooltip=alt.Tooltip("y:Q", title="média do período (%)", format=".1f"))
        st.altair_chart(
            (linha + media).properties(title="Quando falhamos: % de entregas atrasadas por mês", height=320),
            width="stretch", alt="Linha com o percentual de entregas atrasadas por mês",
        )
        st.caption("Picos de atraso na Black Friday (nov/2017) e em fev–mar/2018: a operação não acompanha os picos de demanda. "
                   "A linha tracejada é a média do período.")

        col_uf, col_nota = st.columns(2, gap="large")

        # --- Visual 2: desempenho por UF (clique filtra as métricas e os outros gráficos)
        with col_uf:
            metrica_uf = st.selectbox("Métrica por estado", ["% de atraso", "Prazo médio (dias)", "Frete médio (R$)"])
            col = {"% de atraso": "pct_atraso", "Prazo médio (dias)": "prazo", "Frete médio (R$)": "frete"}[metrica_uf]
            por_uf = (df_base.groupby("uf")
                             .agg(pct_atraso=("atrasado", "mean"), prazo=("dias_entrega", "mean"),
                                  frete=("valor_frete", "mean"), pedidos=("uf", "size"))
                             .assign(pct_atraso=lambda x: x["pct_atraso"] * 100)
                             .dropna(subset=[col])
                             .reset_index())
            clique = alt.selection_point(name="uf_clicada", fields=["uf"])
            barras_uf = alt.Chart(por_uf).mark_bar(color=COR_PRINCIPAL).encode(
                x=alt.X(f"{col}:Q", title=metrica_uf),
                y=alt.Y("uf:N", title=None, sort="-x"),
                opacity=alt.condition(clique, alt.value(1), alt.value(0.3)),
                tooltip=[alt.Tooltip("uf:N", title="UF"),
                         alt.Tooltip(f"{col}:Q", title=metrica_uf, format=",.1f"),
                         alt.Tooltip("pedidos:Q", title="pedidos", format=",")],
            ).add_params(clique).properties(
                title="Onde falhamos: por estado (clique para filtrar)", height=max(380, 17 * len(por_uf)))
            st.altair_chart(barras_uf, key="grafico_uf", on_select="rerun", width="stretch",
                            alt="Barras por estado; clicar num estado filtra as métricas e os outros gráficos")

        # --- Visual 3: nota média × dias até a entrega
        with col_nota:
            e = ent[ent["review_score"].notna()]
            faixa = pd.cut(e["dias_entrega"], FAIXAS_DIAS, labels=ROTULOS_DIAS, include_lowest=True)
            npp = (e.groupby(faixa, observed=False)
                    .agg(nota=("review_score", "mean"), pedidos=("review_score", "size"))
                    .rename_axis("faixa").reset_index()
                    .astype({"faixa": str})
                    .dropna(subset=["nota"]))
            base_npp = alt.Chart(npp).encode(
                x=alt.X("faixa:O", title="dias até a entrega", sort=ROTULOS_DIAS, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("nota:Q", title="nota média", scale=alt.Scale(domain=[1, 5])),
                tooltip=[alt.Tooltip("faixa:O", title="dias"), alt.Tooltip("nota:Q", title="nota média", format=".2f"),
                         alt.Tooltip("pedidos:Q", title="pedidos", format=",")],
            )
            curva = base_npp.mark_line(point=True, color=COR_PRINCIPAL, strokeWidth=2.5)
            rotulos = base_npp.mark_text(dy=-12, fontSize=12).encode(text=alt.Text("nota:Q", format=".1f"))
            st.markdown("&nbsp;")  # alinha com o selectbox da coluna ao lado
            st.altair_chart((curva + rotulos).properties(title="Quanto custa: nota média × dias até a entrega", height=380),
                            width="stretch", alt="Linha da nota média por faixa de dias até a entrega")

            mesmo = (ent.dropna(subset=["uf_vendedor_principal"])
                        .assign(origem=lambda x: x["mesmo_estado"].map({True: "Mesmo estado", False: "Outro estado"}))
                        .groupby("origem").agg(atraso=("atrasado", "mean"), prazo=("dias_entrega", "mean")))
            if len(mesmo) == 2:
                st.caption(
                    f"Vendedor no **mesmo estado** do cliente: prazo médio {fmt(mesmo.loc['Mesmo estado', 'prazo'])} dias "
                    f"e {fmt(mesmo.loc['Mesmo estado', 'atraso'] * 100)} % de atraso, contra "
                    f"{fmt(mesmo.loc['Outro estado', 'prazo'])} dias e {fmt(mesmo.loc['Outro estado', 'atraso'] * 100)} % "
                    "quando o vendedor é de outro estado."
                )

        with st.expander("💡 Recomendações para a gerência"):
            st.markdown(
                "- **Reforçar a operação antes dos picos** (Black Friday, Natal, início do ano): é quando o atraso dispara.\n"
                "- **Atrair vendedores fora de SP** (principalmente N/NE): vendedor no mesmo estado entrega em metade do tempo.\n"
                "- **Monitorar pedidos acima de ~20 dias:** a partir daí a nota cai rápido; vale avisar o cliente antes.\n"
                "- **Revisar a promessa de prazo por estado:** onde a folga do prazo é pequena, o atraso aparece."
            )
