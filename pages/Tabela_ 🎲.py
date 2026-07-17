import streamlit as st
from streamlit_gsheets import GSheetsConnection

# conexão planilha
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet="Página1", ttl=0)

st.title('Segue a base de dados atual 💸')

st.divider()

st.write(df)