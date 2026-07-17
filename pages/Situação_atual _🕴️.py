import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# conexão planilha
hoje = datetime.now()
ano = str(hoje.year)[2:]
mes = str(hoje.month)

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet=f"{mes}/{ano}", ttl=0)

# Plotando no Streamlit
col1, col2, col3 = st.columns([0.33, 0.33, 0.34])

receita_total = df[df['origem'] == 'Receita']['valor'].sum()
col1.metric('Receitas 💸', f'R$ {receita_total:.2f}')

despesa_total = df[df['origem'] == 'Despesa']['valor'].sum()
col2.metric('Despesas totais❗', f'R$ {despesa_total:.2f}')

saldo = receita_total - despesa_total
col3.metric('Disponível para Investimento 🌱', f'R$ {saldo:.2f}')


st.divider()

col21, col22 = st.columns([0.5, 0.5])

despesas_pagas = df[(df['origem'] == 'Despesa') & (df['situacao'] == 'Pago')]['valor'].sum()
#colorir em verde
col21.metric('Despesas Pagas: ', f"R$ {despesas_pagas:.2f}")

despesas_pendentes = df[(df['origem'] == 'Despesa') & (df['situacao'] == 'Pendente')]['valor'].sum()
#colorir em vermelho
col21.metric('Despesas Pendentes: ', f"R$ {despesas_pendentes:.2f}")


st.divider()


col31, col32, col33 = st.columns([0.34, 0.33, 0.34])

# Gráfico Pizza 
metrica_31 = st.sidebar.selectbox('Análise Geral:', ['Receita', 'Despesa'])

if metrica_31 == 'Receita':
    col31.subheader('Distruibuição Despesas')
else:
    col31.subheader('Distruibuição Receitas')

fig_pizza = px.pie(df, names=metrica_31, values='total')
col31.plotly_chart(fig_pizza, use_container_width=True)

# Gráfico Distruibuição dos gastos
col32.subheader('Para onde o dinheiro está indo')

df_despesas = df[df['origem'] == 'Despesa']
despesas_agrupadas = df_despesas.groupby('classificacao')['valor'].sum().reset_index()

## criando as listas para o gráfico
nomes = ['Receita Total'] + despesas_agrupadas['classificacao'].tolist() + ['Saldo Disponível']
valores = [receita_total] + [-valor for valor in despesas_agrupadas['valor']] + [0]
medidas = ['relative'] + ['relative'] * len(despesas_agrupadas) + ['total']

fig_cascata = go.Figure(go.Waterfall(
    name="Fluxo",
    orientation="v",
    measure=medidas,
    x=nomes,
    textposition="outside",
    text=[f"R$ {v:,.2f}" for v in valores], # Mostra o valor em cima da barra
    y=valores,
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#ff6666"}}, # Cor das despesas (vermelho)
    increasing={"marker": {"color": "#66cc66"}}, # Cor das receitas (verde)
    totals={"marker": {"color": "#66b3ff"}}      # Cor do saldo final (azul)
))

fig_cascata.update_layout(
    title="Composição do Saldo Mensal",
    showlegend=False,
    plot_bgcolor='rgba(0,0,0,0)' # Fundo transparente
)

col32.plotly_chart(fig_cascata, use_container_width=True)

# Gráfico Distruibuído por responsável

col33.subheader("Despesas por Responsável")

responsavel_agrupado = df_despesas.groupby('responsavel')['valor'].sum().reset_index()
responsavel_agrupado = responsavel_agrupado.sort_values(by='valor', ascending=True)

fig_responsavel = px.bar(
    responsavel_agrupado, 
    x='valor', 
    y='responsavel', 
    orientation='h',
    text='valor', # Mostra o valor na barra
    color_discrete_sequence=["#09B1C7"] # Cor das barras
)

fig_responsavel.update_layout(
    title="Concentração de Gastos",
    xaxis_title="Valor (R$)",
    yaxis_title="Responsável",
    plot_bgcolor='rgba(0,0,0,0)'
)

fig_responsavel.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')

col33.plotly_chart(fig_responsavel, use_container_width=True)


st.divider()

# DF de depesas Pendentes

st.subheader('Despesas Pendentes 🚨')

df_pendente = df[df['situacao'] == 'Pendente']
df_pendente_editado = st.data_editor(
    df_pendente,
    column_config={
        "situacao": st.column_config.SelectboxColumn(
            "Situação",
            help="Altere para 'Pago' quando quitar a despesa",
            options=["Pendente", "Pago"],
            required=True
        )
    },
    disabled=["data", "valor", "metodo", "classificacao", "responsavel", "observacao"], 
    hide_index=True
)

if st.button('Salvar Atualizações de Pendências'):

    df_historico = conn.read(worksheet="Histórico", ttl=0)
    
    for index, row in df_pendente_editado.iterrows():
        if row['situacao'] == 'Pago':
            # Atualiza a situação no DataFrame principal (df)
            df.at[index, 'situacao'] = 'Pago'

            filtro_historico = (
                (df_historico['valor'] == row['valor']) & 
                (df_historico['data'] == row['data']) & 
                (df_historico['responsavel'] == row['responsavel']) &
                (df_historico['situacao'] == 'Pendente')
            )
            
            # Aplica a alteração para 'Pago' nas linhas que baterem com o filtro
            df_historico.loc[filtro_historico, 'situacao'] = 'Pago'

    conn.update(worksheet=f"{mes}/{ano}", data=df)
    conn.updade(worksheet=f"Histórico", data=df_historico)

    st.success('Pendências atualizadas com sucesso no banco de dados!')
    st.rerun()


