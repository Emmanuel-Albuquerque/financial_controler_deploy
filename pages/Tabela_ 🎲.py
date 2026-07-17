import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# conexão planilha

hoje = datetime.now()
ano = str(hoje.year)[2:]
mes = str(hoje.month)

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet=f"{mes}/{ano}", ttl=0)

st.title('Segue a base de dados atual 💸')

st.divider()

st.write(df)