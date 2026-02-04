import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Configuração visual profissional
st.set_page_config(page_title="Radar 3D - Bráulio", layout="wide")

# Barra Lateral com Metas
st.sidebar.title("📊 Gestão de Metas")
st.sidebar.metric("Meta Mensal", "R$ 6.000,00")
st.sidebar.write("Equipamento: Bambu Lab A1")

# TOKEN E BUSCA
# Já inserido para facilitar seu acesso imediato
APIFY_TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe"
termo_busca = st.text_input("🔍 O que minerar na Shopee hoje?", "decoração nerd 3d")

if st.button("Executar Escaneamento em Tempo Real"):
    with st.spinner('🤖 O robô está analisando a concorrência...'):
        client = ApifyClient(APIFY_TOKEN)
        run_input = {
            "keyword": termo_busca,
            "location": "Brazil",
            "maxItems": 40,
            "proxyConfiguration": { "useApifyProxy": True }
        }
        
        run = client.actor("fatihtahta/shopee-scraper").call(run_input=run_input)
        results = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
        df = pd.DataFrame(results)

        # Processamento e Opportunity Score
        df['price'] = df['price'] / 100000
        df['Score'] = (df['historical_sold'] / (df['stock'] + 1)) * (5.1 - df['rating_star'])
        
        # Gráfico de Oportunidades
        fig = px.bar(df.sort_values('Score', ascending=False).head(12), 
                     x='Score', y='name', orientation='h',
                     title="Produtos com Melhor Custo-Benefício de Entrada",
                     color='price', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.success(f"Busca finalizada! Foram encontrados {len(df)} produtos no nicho de {termo_busca}.")
        st.dataframe(df[['name', 'price', 'historical_sold', 'Score', 'item_url']])
