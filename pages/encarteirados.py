import streamlit as st
import pandas as pd
import requests

# Definindo estilo CSS para as caixas
st.markdown("""
    <style>
    .box {
        background-color: #80CBC4;
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        color: white;
        width: 80%; /* Set a width for the boxes */
        max-width: 300px; /* Max width for better display */
    }
    .box-title {
        font-size: 18px;
        margin-bottom: 10px;
    }
    .box-value {
        font-size: 20px;
    }
    .box hr {
        margin: 10px 0;
        border: 1px solid white;
    }
    .container {
        display: flex;
        justify-content: center;
        gap: 20px; /* Space between boxes */
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def create_box(title, value):
    st.markdown(f"""
    <div class="box">
        <div class="box-title">{title}</div>
        <hr>
        <div class="box-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def get_sfmc_access_token(client_id, client_secret, auth_url):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(auth_url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

def get_data_extension_rows(base_url, access_token, de_key):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{base_url}/data/v1/customobjectdata/key/{de_key}/rowset', headers=headers)
    response.raise_for_status()
    return response.json()['items']

# Configurações da API da SFMC
client_id = 'SEU_CLIENT_ID'
client_secret = 'SEU_CLIENT_SECRET'
auth_url = 'URL_DE_AUTENTICACAO_SFMC'
base_url = 'URL_BASE_SFMC'
de_key = 'CHAVE_DA_DATA_EXTENSION'

try:
    # Obter token de acesso
    access_token = get_sfmc_access_token(client_id, client_secret, auth_url)
    
    # Buscar dados da Data Extension
    de_rows = get_data_extension_rows(base_url, access_token, de_key)
    
    # Converter dados para DataFrame
    df = pd.DataFrame(de_rows)

    # Título principal
    st.title("J7 Expansão de Rede")

    # Filtro de Ano/Mês
    year_months = ["All period"] + sorted(df['yearMonth'].unique().tolist())
    ano_mes = st.selectbox("Ano / Mês", year_months)

    # Filtrando os dados com base no filtro de Ano / Mês
    if ano_mes != "All period":
        df = df[df['yearMonth'] == ano_mes]

    # Obtendo valores dinamicamente do DataFrame
    emails_enviados_C1A = df['totalEmailsSent_C1a'].sum()
    emails_enviados_C2 = df['totalEmailsSent_C2'].sum()
    emails_enviados_C3 = df['totalEmailsSent_C3'].sum()

    taxa_abertura_C1A = (df['totalEmailsOpen_C1a'].sum() / emails_enviados_C1A) * 100 if emails_enviados_C1A else 0
    taxa_abertura_C2 = (df['totalEmailsOpen_C2'].sum() / emails_enviados_C2) * 100 if emails_enviados_C2 else 0
    taxa_abertura_C3 = (df['totalEmailsOpen_C3'].sum() / emails_enviados_C3) * 100 if emails_enviados_C3 else 0

    taxa_clique_C1A = (df['totalEmailsClick_c1a'].sum() / emails_enviados_C1A) * 100 if emails_enviados_C1A else 0
    taxa_clique_C2 = (df['totalEmailsClick_c2'].sum() / emails_enviados_C2) * 100 if emails_enviados_C2 else 0
    taxa_clique_C3 = (df['totalEmailsClick_c3'].sum() / emails_enviados_C3) * 100 if emails_enviados_C3 else 0

    outbound = df['totalOutbound'].sum()
    oportunidades_criadas = df['totalOpportunity'].sum()

    goals_totais = df['totalGoals'].sum()
    c2c = df['detailedGoalC2C'].sum()
    proposta = df['detailedGoalC2CProposta'].sum()
    taxa_conv_global = df['detailedGoalProposta'].mean()

    # Subtítulo
    st.markdown("### Qual é a performance dos emails?")

    # Layout das caixas
    with st.container():    
        rows = [
            [("Emails enviados C1A", emails_enviados_C1A), ("Emails enviados C2", emails_enviados_C2), ("Emails enviados C3", emails_enviados_C3)],
            [("Tx. Abertura C1A", f"{taxa_abertura_C1A:.2f}%"), ("Tx. Abertura C2", f"{taxa_abertura_C2:.2f}%"), ("Tx. Abertura C3", f"{taxa_abertura_C3:.2f}%")],
            [("Tx. Clique C1A", f"{taxa_clique_C1A:.2f}%"), ("Tx. Clique C2", f"{taxa_clique_C2:.2f}%"), ("Tx. Clique C3", f"{taxa_clique_C3:.2f}%")]
        ]

        for row in rows:
            cols = st.columns(3)
            for col, (title, value) in zip(cols, row):
                with col:
                    st.metric(label=title, value=value)

    # Adiciona uma linha horizontal para separar as seções
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.container():
        cols = st.columns(2)
        with cols[0]:
            create_box("Outbound", outbound)
        with cols[1]:
            create_box("Oportunidades criadas", oportunidades_criadas)

    # Adiciona uma linha horizontal para separar as seções
    st.markdown("<hr>", unsafe_allow_html=True)

    # Subtítulo
    st.markdown("### Como se comportam os goals?")

    # Layout das caixas
    with st.container():    
        rows = [
            [("Goals totais", goals_totais), ("C2C", c2c)],
            [("Proposta", proposta), ("Taxa de Conv. Global", f"{taxa_conv_global:.2f}%")]
        ]

        for row in rows:
            cols = st.columns(2)
            for col, (title, value) in zip(cols, row):
                with col:
                    st.metric(label=title, value=value)

except Exception as e:
    st.error(f"Erro ao carregar os dados: {str(e)}. Certifique-se de que a configuração da API está correta e que a Data Extension existe e está acessível.")