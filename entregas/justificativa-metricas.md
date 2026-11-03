# Justificativa das métricas — Dashboard 2

**Público-alvo:** Gerência de Logística / Operações da Olist.
**Por que esse público:** o principal achado da EDA é que o atraso na entrega é o fator que mais derruba a satisfação
(nota média de 4,29 no prazo contra 2,56 com atraso). Quem pode agir sobre isso é a gerência de logística.

As métricas são calculadas sobre os pedidos **entregues** (exceto a métrica 4, que usa todos os pedidos) e respondem
aos filtros de nota e região da barra lateral e ao clique nos estados do gráfico por UF. Quando há filtro, cada métrica
mostra a diferença em relação ao total.

## Métrica 1: Entregas no prazo (%)
- **Variável:** `atrasado` (1 = entregue depois da data prometida; 0 = no prazo)
- **O que mede:** a proporção de pedidos entregues até a data prometida ao cliente. Valor no período todo: 91,9 %.
- **Por que foi escolhida:** é o indicador mais direto de cumprimento da promessa de entrega e resume a variável em um só número.
- **Público-alvo:** Gerência de Logística / Operações.
- **Qual decisão pode ser apoiada por essa métrica?** Definir metas de nível de serviço e decidir onde reforçar a
  operação (quais estados e quais períodos ficam abaixo da meta).
- **O que comunica ao público-alvo:** "de cada 100 pedidos, quantos chegaram no dia prometido", sem precisar ler a
  distribuição dos dias de atraso.

## Métrica 2: Prazo médio de entrega (dias)
- **Variável:** `dias_entrega` (dias entre a compra e a entrega ao cliente)
- **O que mede:** a média de dias que o cliente espera pelo pedido. Valor no período todo: 12,5 dias.
- **Por que foi escolhida:** mostra a velocidade real da operação, independentemente do que foi prometido.
- **Público-alvo:** Gerência de Logística / Operações.
- **Qual decisão pode ser apoiada por essa métrica?** Priorizar estados ou regiões com prazos longos para
  negociar transportadoras, abrir centros de distribuição ou atrair vendedores locais.
- **O que comunica ao público-alvo:** quanto tempo, em média, o cliente espera; comparado ao total, mostra se um
  estado está mais rápido ou mais lento que a média da empresa.

## Métrica 3: Folga média do prazo (dias)
- **Variável:** `dias_prometidos` − `dias_entrega` (prazo prometido menos prazo real)
- **O que mede:** quantos dias, em média, a entrega chega antes da data prometida. Valor no período todo: 11,1 dias.
- **Por que foi escolhida:** a EDA mostrou que a Olist promete prazos folgados (cerca de 24 dias para entregar em 12).
  Onde a folga é pequena, o atraso aparece: a correlação entre folga e % de atraso por estado é de −0,73.
- **Público-alvo:** Gerência de Logística / Operações.
- **Qual decisão pode ser apoiada por essa métrica?** Ajustar a promessa de prazo por estado: encurtar onde há folga
  sobrando (melhora a conversão) e alongar onde ela é pequena (evita atrasos).
- **O que comunica ao público-alvo:** o tamanho da "margem de segurança" da promessa de entrega.

## Métrica 4: Frete / valor pago (%)
- **Variáveis:** `valor_frete` e `valor_pago` (soma do frete dividida pela soma do valor pago)
- **O que mede:** quanto do dinheiro pago pelo cliente vai para o frete. Valor no período todo: 14,1 %.
- **Por que foi escolhida:** o frete é o custo logístico que o cliente sente no bolso, e ele sobe muito fora do Sudeste
  (o Norte paga o dobro do Sudeste, em média).
- **Público-alvo:** Gerência de Logística / Operações.
- **Qual decisão pode ser apoiada por essa métrica?** Revisar contratos de frete e políticas de subsídio (frete grátis
  ou reduzido) nas regiões onde o frete pesa mais.
- **O que comunica ao público-alvo:** "de cada R$ 100 pagos, quantos reais são frete", sem precisar comparar médias de
  frete e de ticket separadamente.

## Métrica 5: Nota dos atrasados (★)
- **Variáveis:** `review_score` dos pedidos com `atrasado` = 1, comparada com a dos pedidos no prazo
- **O que mede:** a nota média (1 a 5) dada pelos clientes cujo pedido atrasou e a diferença para os pedidos no prazo.
  Valor no período todo: 2,56 ★, ou 1,73 ponto abaixo dos pedidos no prazo.
- **Por que foi escolhida:** traduz o atraso em impacto na satisfação, o principal achado da EDA.
- **Público-alvo:** Gerência de Logística / Operações.
- **Qual decisão pode ser apoiada por essa métrica?** Justificar investimento em logística e criar ações para pedidos
  que vão atrasar (aviso antecipado ao cliente, cupom de compensação).
- **O que comunica ao público-alvo:** quanto custa um atraso em satisfação, de forma direta: "atrasou, a nota cai quase 2 pontos".
