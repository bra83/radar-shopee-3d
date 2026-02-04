import streamlit as st
import pandas as pd
import plotly.express as px
from apify_client import ApifyClient

# Configuração da página e identidade visual
st.set_page_config(page_title="Radar 3D - Savepoint Quest", layout="wide")

# Interface Lateral - Foco no Objetivo Financeiro
st.sidebar.title("📈 Gestão Savepoint Quest")
meta_lucro = 6000.00 
st.sidebar.metric("Meta Mensal", f"R$ {meta_lucro:,.2f}")
st.sidebar.write("---")
st.sidebar.write("**Equipamento Ativo:**")
st.sidebar.write("- Bambu Lab A1")
st.sidebar.write("- Anycubic Mono X")

# TOKEN DE ACESSO
TOKEN = "apify_api_bEuGre9AfeeLqfureqPIm1FXrpvqiC41lNhe"

st.title("🎯 Monitor de Oportunidades Shopee")
st.markdown("Foco em **Nerd Nostalgia** e itens de alto ticket.")

# Entrada de Dados
col1, col2 = st.columns([3, 1])
with col1:
    termo_pesquisa = st.text_input("Qual nicho pesquisar agora?", "action figure articulado")
with col2:
    custo_filamento_resina = st.number_input("Custo de produção (R$)", value=15.0)

if st.button("🚀 Iniciar Mineração em Tempo Real"):
    try:
        client = ApifyClient(TOKEN)
        
        with st.spinner('Acessando a Shopee... Isso pode levar até 60 segundos.'):
            # Configuração do input para o Actor fatihtahta/shopee-scraper
            run_input = {
                "keyword": termo_pesquisa,
                "location": "Brazil",
                "maxItems": 30,
                "proxyConfiguration": { "useApifyProxy": True }
            }
            
            # Execução do robô específico
            run = client.actor("fatihtahta/shopee-scraper").call(run_input=run_input)
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not results:
                st.error("O robô não encontrou resultados para este termo. Tente mudar a palavra-chave.")
            else:
                df = pd.DataFrame(results)

                # Tratamento de Preço (Conversão de centavos Shopee)
                if 'price' in df.columns:
                    df['price'] = df['price'] / 100000 
                
                # Cálculo do Score de Oportunidade
                # Fórmula: (Vendas Totais / Estoque) * Diferencial de Qualidade (5 - Nota)
                df['Score'] = (df['historical_sold'] / (df['stock'] + 1)) * (5.1 - df['rating_star'])
                df['Lucro_Estimado'] = df['price'] - custo_filamento_resina

                # --- DASHBOARD INTERATIVO ---
                st.subheader(f"Análise de Mercado: {termo_pesquisa}")
                
                # Gráfico de Dispersão
                fig = px.scatter(df, x="price", y="historical_sold", 
                                 size="Score", color="rating_star",
                                 hover_name="name", 
                                 title="Oportunidade por Produto (Bolas maiores = Menos concorrência/Mais busca)",
                                 color_continuous_scale="RdYlGn", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

                # Resumo Estratégico para Meta de R$ 6.000,00
                st.divider()
                top_oportunidade = df.sort_values('Score', ascending=False).iloc[0]
                lucro_un = top_oportunidade['Lucro_Estimado']
                vendas_para_meta = meta_lucro / lucro_un if lucro_un > 0 else 0
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Melhor Entrada", f"{top_oportunidade['name'][:25]}...")
                c2.metric("Margem Estimada", f"R$ {lucro_un:.2f}")
                c3.metric("Volume p/ Meta", f"{int(vendas_para_meta)} un/mês")

                st.write("---")
                st.write("**Tabela de Dados Extraídos:**")
                st.dataframe(df[['name', 'price', 'historical_sold', 'rating_star', 'Score']].sort_values('Score', ascending=False))

    except Exception as e:
        st.error(f"Erro na conexão com o Apify: {e}")
        st.info("Verifique se o seu Token é válido e se você tem saldo (Usage) na conta do Apify.")

else:
    st.info("Aguardando comando. Defina o nicho e clique em escanear.")
