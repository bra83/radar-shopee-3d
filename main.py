import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração de Identidade Visual - Savepoint Quest
st.set_page_config(page_title="Radar Savepoint - CSV Mode", layout="wide")

st.sidebar.title("💰 Gestão Savepoint Quest")
meta_lucro = 6000.00
st.sidebar.metric("Meta Mensal", f"R$ {meta_lucro:,.2f}")
st.sidebar.write("---")
st.sidebar.write("**Equipamento Ativo:**")
st.sidebar.write("- Bambu Lab A1 / Anycubic Mono X")

st.title("🎯 Analisador de Nichos (Modo Manual)")
st.markdown("Suba o arquivo extraído da Shopee para calcular a viabilidade do nicho.")

# Upload do Arquivo
uploaded_file = st.file_uploader("Escolha o arquivo CSV extraído", type="csv")
custo_producao = st.number_input("Custo de Produção Estimado (R$)", value=20.0)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # Identificação automática de colunas (para funcionar com qualquer extrator)
        price_col = [c for c in df.columns if 'price' in c.lower() or 'preço' in c.lower()][0]
        sold_col = [c for c in df.columns if 'sold' in c.lower() or 'vendidos' in c.lower()][0]
        name_col = [c for c in df.columns if 'name' in c.lower() or 'nome' in c.lower() or 'title' in c.lower()][0]
        rating_col = [c for c in df.columns if 'rating' in c.lower() or 'avaliação' in c.lower()][0]

        # Limpeza básica de dados
        df[price_col] = pd.to_numeric(df[price_col].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.'), errors='coerce')
        df[sold_col] = pd.to_numeric(df[sold_col].astype(str).str.extract('(\d+)')[0], errors='coerce').fillna(0)
        
        # Fórmula de Oportunidade Savepoint
        df['Score'] = (df[sold_col] / 10) * (5.1 - df[rating_col].fillna(4.0))
        df['Lucro_Est'] = df[price_col] - custo_producao

        # Dashboard Financeiro
        top = df.sort_values('Score', ascending=False).iloc[0]
        vendas_meta = meta_lucro / top['Lucro_Est'] if top['Lucro_Est'] > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Produto Recomendado", f"{top[name_col][:20]}...")
        c2.metric("Margem p/ Peça", f"R$ {top['Lucro_Est']:.2f}")
        c3.metric("Meta de Vendas", f"{int(vendas_meta)} un")

        st.subheader("Gráfico de Oceano Azul")
        fig = px.scatter(df, x=price_col, y=sold_col, size="Score", color=rating_col,
                         hover_name=name_col, template="plotly_dark", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

        st.write("**Tabela de Dados:**")
        st.dataframe(df[[name_col, price_col, sold_col, 'Score']])

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}. Certifique-se de que as colunas de Preço e Vendas estão visíveis.")
else:
    st.info("Aguardando upload do CSV. Use a extensão 'Instant Data Scraper' na página de busca da Shopee.")
