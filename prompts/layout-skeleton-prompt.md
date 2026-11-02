# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

Sou aluno da disciplina Análise e Visualização de Dados (CESAR School, 2026.2). Fiz uma EDA do dataset
**Brazilian E-Commerce Public Dataset by Olist** (Kaggle), com ~99 mil pedidos de jan/2017 a ago/2018, e preciso de
um app Streamlit com **duas abas**:

- **Dashboard 1:** laboratório de análise de distribuição e correlação das variáveis quantitativas.
- **Dashboard 2:** KPIs para um público-alvo — escolhi a **Gerência de Logística/Operações** da Olist, porque o principal
  achado da EDA é que o atraso na entrega é o que mais derruba a nota do cliente.

## Entrada

Rascunhos feitos no Excalidraw: `entregas/rascunho-dashboard1.png` e `entregas/rascunho-dashboard2.png`
(arquivos editáveis `.excalidraw` na mesma pasta).

Dataset: `data/clean/dataset.csv` (1 linha por pedido). Colunas:
`status, data_compra, ano_mes, dia_semana, hora, uf, regiao, n_itens, valor_produtos, valor_frete, valor_pago, parcelas,
tipo_pagamento, n_vendedores, peso_total_g, categoria_principal, uf_vendedor_principal, mesmo_estado, dias_entrega,
dias_prometidos, dias_atraso, atrasado, review_score, cliente_recorrente`.

Layout:
- Sidebar: seletor de variáveis quantitativas (multiselect), slider de intervalo da **nota de avaliação** (1–5) para
  excluir notas da análise e outros filtros (região, corte de outliers).
- Abas no topo: Dashboard 1 e Dashboard 2.
- Dashboard 1: mapa de calor de correlação à esquerda; à direita, 1 histograma por variável selecionada.
- Dashboard 2: 5 métricas no topo; abaixo, gráfico de atraso por mês (largura total) e, lado a lado,
  gráfico por estado e gráfico de nota × prazo de entrega.

Perguntas: quais variáveis se relacionam com a nota? Como elas se distribuem? Onde e quando a entrega falha, e quanto
isso custa em satisfação?

## Restrições

- Streamlit + **Altair** (`st.altair_chart`); editar só `app.py` (e `src/data_loader.py` para o cache).
- Carregar dados **somente** via `src/data_loader.py` (lê `data/clean/dataset.csv` por caminho relativo) com `@st.cache_data`.
- As duas visões em `st.tabs`; os filtros da sidebar valem para as duas abas.
- Dashboard 2 com seleção no gráfico (clique) atualizando as métricas, como no `ALTAIR-CROSSFILTER.md`.
- Não exibir identificadores nem dados sensíveis; não usar `secrets`.

## Formato de saída

Código completo do `app.py`, organizado em seções comentadas (sidebar, filtros, Dashboard 1, Dashboard 2), com uma breve
explicação de cada seção.
