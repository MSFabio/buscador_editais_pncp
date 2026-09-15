import streamlit as st
import pandas as pd

# Configuração inicial da página
st.set_page_config(page_title="Dashboard de Localização", page_icon="🗺️", layout="wide")

st.title("🗺️ Dashboard de Acessos e Geolocalização")
st.markdown("Visualização interativa das origens de acesso baseada nos endereços IP da planilha.")

@st.cache_data
def load_data():
    file_path = r"C:\Users\11429149760\Downloads\Relatório_IPs_Localizados.xlsx"
    df = pd.read_excel(file_path)
    
    # Prepara as colunas geográficas
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['lat'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['lon'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
    # Converte coluna DATA se existir, para possibilitar filtros de período
    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
        
    return df

with st.spinner("Carregando 110 mil registros..."):
    df_raw = load_data()

if not df_raw.empty:
    # ====== BARRA LATERAL (FILTROS) ======
    st.sidebar.header("🔍 Filtros")
    st.sidebar.markdown("Use as opções abaixo para segmentar os dados.")
    
    df = df_raw.copy()
    
    # 1. Filtro de Data (Período)
    if 'DATA' in df.columns and not df['DATA'].isna().all():
        min_date = df['DATA'].min()
        max_date = df['DATA'].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            date_range = st.sidebar.date_input(
                "Período de Acesso",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )
            # Aplica o filtro se as duas datas forem selecionadas
            if len(date_range) == 2:
                df = df[(df['DATA'].dt.date >= date_range[0]) & (df['DATA'].dt.date <= date_range[1])]

    # 2. Função auxiliar para filtros Multi-seleção
    def apply_multiselect(column_name, label):
        global df
        if column_name in df.columns:
            # Lista os valores únicos existentes após os filtros anteriores
            options = sorted(df[column_name].dropna().unique().tolist())
            if options:
                selected = st.sidebar.multiselect(label, options)
                if selected:
                    df = df[df[column_name].isin(selected)]

    # Aplicando filtros geográficos e de sistema em cascata
    apply_multiselect('País', 'País')
    apply_multiselect('Estado/Região', 'Estado/Região')
    apply_multiselect('Cidade', 'Cidade')
    apply_multiselect('Provedor (ISP)', 'Provedor de Internet (ISP)')
    apply_multiselect('MOTIVO_CONSULTA', 'Motivo da Consulta')

    # 3. Filtros de Busca por Texto
    st.sidebar.markdown("---")
    st.sidebar.subheader("Busca Específica")
    
    if 'NOME' in df.columns:
        busca_nome = st.sidebar.text_input("Nome do Usuário")
        if busca_nome:
            df = df[df['NOME'].astype(str).str.contains(busca_nome, case=False, na=False)]
            
    if 'IP' in df.columns:
        busca_ip = st.sidebar.text_input("Endereço IP")
        if busca_ip:
            df = df[df['IP'].astype(str).str.contains(busca_ip, case=False, na=False)]

    # Resumo na barra lateral
    st.sidebar.markdown("---")
    st.sidebar.success(f"**Registros exibidos:** {len(df):,} / {len(df_raw):,}".replace(",", "."))

    # ====== ÁREA PRINCIPAL ======
    if df.empty:
        st.warning("Nenhum registro encontrado com os filtros selecionados. Tente limpar os filtros na barra lateral.")
    else:
        # Métricas
        st.subheader("📊 Visão Geral")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Consultas", f"{len(df):,}".replace(",", "."))
        col2.metric("IPs Únicos", df['IP'].nunique() if 'IP' in df.columns else 0)
        col3.metric("Cidades Diferentes", df['Cidade'].nunique() if 'Cidade' in df.columns else 0)
        col4.metric("Estados Atingidos", df['Estado/Região'].nunique() if 'Estado/Região' in df.columns else 0)

        st.markdown("---")
        
        # Mapa
        st.subheader("📍 Mapa de Densidade de Acessos")
        map_data = df.dropna(subset=['lat', 'lon'])
        if not map_data.empty:
            st.map(map_data, use_container_width=True)
        else:
            st.info("Nenhum dado com latitude e longitude válidas para exibir no mapa com os filtros atuais.")

        st.markdown("---")
        
        # Gráficos
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("🏆 Cidades com mais acessos")
            if 'Cidade' in df.columns:
                st.bar_chart(df['Cidade'].value_counts().head(10), color="#FF4B4B")
                
        with col_right:
            st.subheader("🌐 ISP (provedores) com mais acessos")
            if 'Provedor (ISP)' in df.columns:
                st.bar_chart(df['Provedor (ISP)'].value_counts().head(10), color="#0068C9")
            
        st.markdown("---")
        
        # Tabela
        st.subheader("📄 Visualização dos Dados Filtrados")
        # Mostrar o dataframe inteiro agora que já pode ser filtrado
        st.dataframe(df, use_container_width=True)

else:
    st.error("Nenhum dado pôde ser carregado.")
