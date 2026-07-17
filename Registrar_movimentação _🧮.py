import pandas as pd
from datetime import date, datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def manipulador_valor(valor):
    valor = str(valor)

    if valor.split('.')[1] == '0':
        valor = f"{valor.split('.')[0]}.00"

    # xxx.xx -> xxx,xx
    if len(valor.split('.')[0]) == 3:
        valor = valor.replace('.', ',') 

    # xxxx.xx -> x.xxx,xx
    elif len(valor.split('.')[0]) == 4:
        valor = f"{valor.split('.')[0][:-3]}.{valor.split('.')[0][-3:]},{valor.split('.')[1]}"
    
    # xxxxx.xx -> xx.xxx,xx
    elif len(valor.split('.')[0]) > 4:
        valor = f"{valor.split('.')[0][:-3]}.{valor.split('.')[0][-3:]},{valor.split('.')[1]}"

    return valor

hoje = datetime.now()
ano = str(hoje.year)[2:]
mes = str(hoje.month)

# Conexão oficial
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title='Controle Financeiro', page_icon='📝', layout='wide')
st.title('Bem vindo Emmanuel! 🚀')

st.divider()

origem = st.selectbox('Qual das opções a seguir deseja registrar?', 
                    (
                        'Receita', 
                        'Despesa'
                        ))

# atribuindo valores para evitar erro
metodo_pagamento = None
classificacao = None
responsavel = None
situacao = None
observacao = None


if origem == 'Receita':
    valor = st.number_input('Qual o valor? (ex: 199.99)')

    classificacao = st.selectbox('Origem:', 
                                 (
                                     'Salário',
                                     'Trabalhos',
                                     'Investimentos'
                                 ))

else:

    valor = st.number_input('Qual o valor? (ex: 199.99)')

    metodo_pagamento = st.selectbox('Qual foi o método de pagamento? ', 
                                    (
                                        'Pix', 
                                        'Crédito', 
                                        'Débito', 
                                        'Dinheiro', 
                                        'Outro'
                                    ))

    classificacao = st.selectbox('Qual a classificação do gasto?', 
                                (
                                    'Investimento', 
                                    'Lazer', 
                                    'Alimentação', 
                                    'Mercado', 
                                    'Saúde', 
                                    'Estudos', 
                                    'Hobbies',
                                    'Transporte',
                                    'Presentes', 
                                    'Outros' 
                                ))

    responsavel = st.selectbox('Responsável:', 
                               (
                                   'Emmanuel',
                                   'Pai',
                                   'Mãe',
                                   'Madu',
                                   'Indira'
                               ))
    
    situacao = st.selectbox('Situação:', 
                            (
                                'Pago',
                                'Pendente'
                            ))
    
    observacao = st.text_input('Descreva:').lower()
    if observacao == '':
        observacao = 'não informado'

if st.button('Registrar ação'):

    nova_linha = pd.DataFrame([{
        'data': str(date.today()),
        'origem': origem,
        'valor': valor,
        'metodo': metodo_pagamento,
        'classificacao': classificacao,
        'responsavel': responsavel,
        'situacao': situacao, 
        'observacao': observacao,
    }])

    # Lê a planilha Histórico
    df_historico = conn.read(worksheet="Histórico", ttl=0)

    # Lê a planilha do mês correspondente
    df = conn.read(worksheet= f"{mes}/{ano}", ttl=0)
    
    # # Junta com a nova linha
    df = pd.concat([df, nova_linha], ignore_index=True)
    df_historico = pd.concat([df_historico, nova_linha], ignore_index=True)

    # Atualiza tudo novamente
    conn.update(worksheet=f"{mes}/{ano}", data=df)
    conn.update(worksheet=f"Histórico", data=df_historico)

    st.success(f'Movimentação registrada com sucesso!')