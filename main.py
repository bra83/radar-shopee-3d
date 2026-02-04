import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Configuração de Identidade Visual
st.set_page_config(page_title="Radar Savepoint Quest", layout="wide")

# Sidebar - Painel Financeiro focado na meta de R$ 6k
st.sidebar.title("💰 Gestão Savepoint")
meta_lucro = 6000.00
st.sidebar.metric("Meta de Lucro", f"R$ {meta_lucro:,.2f}")
st.sidebar.write("---")
st.sidebar.write("**Maquinário Disponível:**")
st.sidebar.write("- Bambu Lab A1")
st.sidebar.write("- Anycubic Mono X")

# CONFIGURAÇÕES DE API
TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe"
# O ator que você encontrou:
ACTOR_NAME = "ywlfff2014/shopee-product-scraper"

st.title("🎯 Monitor de Mercado: Nerd Nostalgia")
st.markdown("Identificando nichos de alta demanda e baixa concorrência.")

col1, col2 = st.columns([3, 1])
with col1:
    termo = st.text_input("O que vamos minerar na Shopee hoje?", "suporte headset gamer 3d")
with col2:
    custo_producao = st.number_input("Custo Médio de Produção (R$)", value=18.0)

if st.button("🔥 Iniciar Escaneamento"):
    try:
        client = ApifyClient(TOKEN)
        with st.spinner(f'🤖 Rodando o robô {ACTOR_NAME}...'):
            # Configuração padrão para este scraper
            run_input = {
                "keyword": termo,
                "maxItems": 25, 
                "location": "Brazil"
            }
            
            run = client.actor(ACTOR_NAME).call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not results:
                st.warning("Nenhum dado retornado. Verifique se o termo é muito específico ou se o robô precisa de uma URL.")
            else:
                df = pd.DataFrame(results)

                # Tratamento Inteligente de Colunas (Scrapers variam nomes de campos)
                # Tentamos encontrar colunas de preço e vendas mesmo que mudem o nome
                price_col = [c for c in df.columns if 'price' in c.lower()][0] if any('price' in c.lower() for c in df.columns) else None
                sold_col = [c for c in df.columns if 'sold' in c.lower()][0] if any('sold' in c.lower() for c in df.columns) else None
                rating_col = [c for c in df.columns if 'rating' in c.lower()][0] if any('rating' in c.lower() for c in df.columns) else None

                if price_col and sold_col:
                    # Ajuste de escala de preço comum em APIs de Shopee
                    if df[price_col].max() > 10000:
                        df['Preço_Real'] = df[price_col] / 100000
                    else:
                        df['Preço_Real'] = df[price_col]
                    
                    # Cálculo do Opportunity Score (OS)
                    # USAMOS LATEX: $$OS = \left( \frac{\text{Vendas}}{\text{Estoque} + 1} \right) \times (5.1 - \text{Nota})$$
                    df['Score'] = (df[sold_col] / 10) * (5.1 - df[rating_col].fillna(4.0))
                    df['Lucro_Estimado'] = df['Preço_Real'] - custo_producao

                    # DASHBOARD FINANCEIRO
                    top_item = df.sort_values('Score', ascending=False).iloc[0]
                    lucro_un = top_item['Lucro_Estimado']
                    vendas_necessarias = meta_lucro / lucro_un if lucro_un > 0 else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Oportunidade de Ouro", f"{top_item['name'][:20]}...")
                    c2.metric("Margem p/ Peça", f"R$ {lucro_un:.2f}")
                    c3.metric("Vendas p/ Meta", f"{int(vendas_necessarias)} un")

                    st.subheader("Visualização de Nicho")
                    fig = px.scatter(df, x="Preço_Real", y=sold_col, size="Score", 
                                     color=rating_col, hover_name="name",
                                     template="plotly_dark", color_continuous_scale="RdYlGn",
                                     labels={'Preço_Real': 'Preço (R$)', sold_col: 'Qtd Vendida'})
                    st.plotly_chart(fig, use_container_width=True)

                    st.write("**Dados Detalhados:**")
                    st.dataframe(df[['name', 'Preço_Real', sold_col, 'Score']])
                else:
                    st.error("O robô retornou dados, mas os nomes das colunas (preço/vendas) são diferentes do esperado.")
                    st.write("Colunas encontradas:", df.columns.tolist())

    except Exception as e:
        st.error(f"Erro na execução: {e}")
        st.info("Verifique se o seu Token do Apify ainda possui créditos gratuitos ($5.00/mês).")

else:
    st.info("Aguardando comando para minerar o mercado.")
