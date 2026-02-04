import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Configuração de Layout
st.set_page_config(page_title="Radar 3D - Savepoint Quest", layout="wide")

# Estilização e Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/625/625315.png", width=100)
st.sidebar.title("🚀 Painel de Metas")
meta_objetivo = 6000.00 # Sua meta de lucro
st.sidebar.metric("Meta Mensal", f"R$ {meta_objetivo:,.2f}")
st.sidebar.write("---")

# TOKEN DE ACESSO (Mantenha este código seguro)
TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe" 

st.title("🎯 Radar de Oportunidades: Nerd Nostalgia")
st.markdown(f"Analisando nichos para sua **Bambu Lab A1** e **Anycubic Mono X**.")

# Interface de Busca
col_a, col_b = st.columns([3, 1])
with col_a:
    termo = st.text_input("O que você quer vender hoje?", "action figure articulado 3d")
with col_b:
    custo_estimado = st.number_input("Custo médio de produção (R$)", value=15.0)

if st.button("🔥 Escanear Mercado Agora"):
    try:
        client = ApifyClient(TOKEN)
        
        with st.spinner('Minerando dados da Shopee... Isso leva cerca de 1 minuto.'):
            # Usando um Actor mais acessível para evitar erros de permissão
            run_input = {
                "keyword": termo,
                "location": "Brazil",
                "maxItems": 30,
                "proxyConfiguration": { "useApifyProxy": True }
            }
            
            run = client.actor("shoppre/shopee-scraper").call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not results:
                st.warning("Nenhum dado retornado. Tente um termo mais simples.")
            else:
                df = pd.DataFrame(results)

                # TRATAMENTO DE DADOS
                # Ajuste de preço (Shopee envia em formato inteiro longo)
                df['price'] = df['price'] / 100000 
                
                # CÁLCULO DE OPORTUNIDADE (Fórmula exclusiva)
                # Valoriza: Mais vendas, preço sustentável e concorrência com nota baixa
                df['Score'] = (df['historical_sold'] / (df['stock'] + 1)) * (5.1 - df['rating_star'])
                df['Lucro_Est'] = df['price'] - custo_estimado

                # --- VISUALIZAÇÃO ---
                st.subheader(f"Principais Oportunidades em '{termo}'")
                
                fig = px.scatter(df, x="price", y="historical_sold", 
                                 size="Score", color="rating_star",
                                 hover_name="name", title="Vendas x Preço (Tamanho da bola = Oportunidade)",
                                 labels={'price': 'Preço de Venda', 'historical_sold': 'Total Vendido'},
                                 color_continuous_scale="RdYlGn", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

                # MÉTRICAS DE META FINANCEIRA
                st.divider()
                top_item = df.sort_values('Score', ascending=False).iloc[0]
                lucro_un = top_item['Lucro_Est']
                vendas_nec = meta_objetivo / lucro_un if lucro_un > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Produto Sugerido", f"{top_item['name'][:20]}...")
                c2.metric("Lucro p/ Peça", f"R$ {lucro_un:.2f}")
                c3.metric("Vendas p/ bater Meta", f"{int(vendas_nec)} unidades")

                st.write("---")
                st.dataframe(df[['name', 'price', 'historical_sold', 'rating_star', 'Score']].sort_values('Score', ascending=False))

    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        st.info("Dica: Verifique se sua conta no Apify atingiu o limite de $5.00 gratuitos.")

else:
    st.info("Digite um termo acima e clique no botão para começar.")
