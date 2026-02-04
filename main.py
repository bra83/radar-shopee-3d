import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Identidade Visual Savepoint Quest
st.set_page_config(page_title="Radar 3D - Gestão", layout="wide")

st.sidebar.title("💰 Gestão Financeira")
meta_lucro = 6000.00
st.sidebar.metric("Meta de Lucro", f"R$ {meta_lucro:,.2f}")
st.sidebar.write("---")
st.sidebar.write("**Equipamento:**")
st.sidebar.write("- Bambu Lab A1 / Anycubic Mono X")

# TOKEN (Use o seu personal token aqui)
TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe"
# Este é o robô que aceita termos de busca (Keywords)
ACTOR_NAME = "shoppre/shopee-scraper"

st.title("🎯 Monitor de Oportunidades: Nerd Nostalgia")
st.markdown("Pesquise nichos para suas impressões 3D.")

col1, col2 = st.columns([3, 1])
with col1:
    termo = st.text_input("O que buscar na Shopee?", "estátua resina geek")
with col2:
    custo_producao = st.number_input("Custo de Produção (R$)", value=25.0)

if st.button("🔍 Iniciar Busca"):
    try:
        client = ApifyClient(TOKEN)
        with st.spinner('Minerando dados... Isso leva cerca de 40 segundos.'):
            # Input simplificado para evitar erros de validação
            run_input = {
                "keyword": termo,
                "location": "Brazil",
                "maxItems": 20
            }
            
            run = client.actor(ACTOR_NAME).call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not results:
                st.warning("Nenhum produto encontrado. Tente um termo mais comum.")
            else:
                df = pd.DataFrame(results)

                # Ajuste de Preço
                df['Preco_Real'] = df['price'] / 100000 if df['price'].max() > 1000 else df['price']
                
                # Cálculo de Oportunidade (Vendas / Estoque)
                df['Score'] = (df['historical_sold'] / (df['stock'] + 1)) * (5.1 - df['rating_star'].fillna(4.0))
                df['Lucro_Est'] = df['Preco_Real'] - custo_producao

                # Dashboard
                top = df.sort_values('Score', ascending=False).iloc[0]
                lucro_un = top['Lucro_Est']
                vendas_meta = meta_lucro / lucro_un if lucro_un > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Top Oportunidade", f"{top['name'][:20]}...")
                c2.metric("Lucro p/ Peça", f"R$ {lucro_un:.2f}")
                c3.metric("Vendas p/ Meta", f"{int(vendas_meta)} un")

                st.subheader("Gráfico de Viabilidade")
                fig = px.scatter(df, x="Preco_Real", y="historical_sold", size="Score", 
                                 color="rating_star", hover_name="name",
                                 template="plotly_dark", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df[['name', 'Preco_Real', 'historical_sold', 'Score']])

    except Exception as e:
        st.error(f"Erro: {e}")
        st.info("Se o erro persistir, pode ser que seus \$5.00 de créditos gratuitos do Apify tenham acabado.")

else:
    st.info("Aguardando termo de busca.")
