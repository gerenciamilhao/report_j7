import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Página Inicial", page_icon="🏠")
st.title("Bem-vindo!")
st.markdown("### ao report da J7 Expansão de Rede")

# Adiciona uma linha horizontal para separar as seções
st.markdown("<hr>", unsafe_allow_html=True)

# Adiciona campo para subir um arquivo CSV
uploaded_file = st.file_uploader("Faça upload do seu arquivo .CSV abaixo", type=["csv"])
if uploaded_file is not None:
    # Lê o arquivo CSV
    df = pd.read_csv(uploaded_file)
    
    # Conecta ao banco de dados SQLite (cria o banco se ele não existir)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    # Cria a tabela no banco de dados (apaga e recria se já existir)
    c.execute('DROP TABLE IF EXISTS data')
    df.to_sql('data', conn, index=False)
    
    # Fecha a conexão com o banco de dados
    conn.close()
    
    st.write("Dados do arquivo CSV carregados no banco de dados SQLite:")
    st.write(df)
