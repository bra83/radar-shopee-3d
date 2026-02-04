import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Configuração Profissional
st.set_page_config(page_title="Radar Savepoint Quest", layout="wide")

# Sidebar - Foco Financeiro
st.sidebar.title("📊 Gestão Savepoint")
meta_lucro = 6000.00 # Sua meta mensal
st.sidebar.metric("Meta de Lucro", f"R$ {meta_lucro:,.2f}")
st.sidebar.write("---")
st.sidebar.write("**Maquinário:**")
st.sidebar.write("- Bambu Lab A1") #
st.sidebar.write("- Anycubic Mono X") #

# TOKEN (Atualize se você resetou no Apify)
TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe"

st.title("🎯 Radar de Oportunidades Shopee (Versão Gratuita)")
st.markdown("Minerando nichos de **Deco Nerd** com baixo custo de API.") #

col1, col2 = st.columns([3, 1])
with col1:
    termo = st.text_input("O que pesquisar?", "action figure 3d")
with col2:
    custo_producao = st.number_input("Custo de Produção (R$)", value=15.0)

if st.button("🚀 Escanear Agora"):
    try:
        client = ApifyClient(TOKEN)
        
        with st.spinner('🤖 Robô gratuito em ação... Aguarde uns instantes.'):
            # Usando o Actor shoppre/shopee-scraper (mais chances de ser free)
            run_input = {
                "keyword": termo,
                "location": "Brazil",
                "maxItems": 20 # Limite baixo para não gastar seus créditos free
            }
            
            # Chamada do ator alternativo
            run = client.actor("shoppre/shopee-scraper").call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not results:
                st.warning("Nenhum dado encontrado. Verifique se o termo está correto.")
            else:
                df = pd.DataFrame(results)

                # Tratamento de Preço
                df['price'] = df['price'] / 100000 
                
                # Cálculo de Oportunidade
                df['Score'] = (df['historical_sold'] / (df['stock'] + 1)) * (5.1 - df['rating_star'])
                df['Lucro_Estimado'] = df['price'] - custo_producao

                # Visualização
                fig = px.bar(df.sort_values('Score', ascending=False).head(10), 
                             x='Score', y='name', orientation='h',
                             title="Top Oportunidades (Volume x Baixa Concorrência)",
                             color='price', template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

                # Análise da Meta de R$ 6.000,00
                st.divider()
                top = df.sort_values('Score', ascending=False).iloc[0]
                lucro_un = top['Lucro_Estimado']
                unidades = meta_lucro / lucro_un if lucro_un > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Produto Recomendado", f"{top['name'][:20]}...")
                c2.metric("Margem por Peça", f"R$ {lucro_un:.2f}")
                c3.metric("Meta de Vendas", f"{int(unidades)} un")

                st.dataframe(df[['name', 'price', 'historical_sold', 'Score']].sort_values('Score', ascending=False))

    except Exception as e:
        st.error(f"Erro: {e}")
        st.info("Se o erro persistir, verifique se você ainda tem os $5.00 de créditos gratuitos no menu 'Billing' do Apify.")

else:
    st.info("Aguardando comando para análise.")
