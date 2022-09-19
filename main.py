import streamlit as st
import mysql.connector
import switcher as switcher

st.title('Análise dos dados')

@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

#run_query("SELECT * from fato_despesas;")

#DAQUI PRA BAIXO COMEÇO A FAZER OS GRÁFICOS DINAMICOS PARA CADA QUESTÃO

def questao1():
    # https://www.alura.com.br/artigos/streamlit-compartilhando-sua-aplicacao-de-dados-sem-dor-de-cabeca

    st.subheader('**1 - Porcentagem de gastos de cada grupo de despesa por região no mês de janeiro**')

    st.sidebar.markdown('## Grupo de despesa')
    despesas = run_query("escrever query aqui pra pegar os nomes dos grupos de despesas da base de dados")
    grupo_despesas = []

    for grupo in despesas:
       grupo_despesas.append(grupo)

    despesa = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = grupo_despesas)

    st.sidebar.markdown('## Região')
    regioes_base = run_query("escrever query aqui pra pegar os nomes das regioes da base de dados")
    regioes = []

    for regiao in regioes_base:
       regioes.append(regiao)

    regiao = st.sidebar.selectbox('Selecione a região que deseja saber a porcentagem', options = regioes)

    #escreve aqui a porcentagem (filtra do sql) - pega as variáveis despesa e regiao e faz uma query e o resultado da query escreve no write
    # run_query("SELECT * from fato_despesas;")

    st.write('valor aqui', '%')

def default():
    return "Incorreto"
#----------------------------------------------------------------------------

questoes = []

for i in range(1, 16):
    questoes.append("Gráfico {}".format(i))

st.sidebar.markdown('# Gráfico')
grafico = st.sidebar.selectbox('Selecione o gráfico que deseja exibir', options = questoes)

#ir criando uma função pra cada questão
switcher = {
    "Gráfico 1": questao1,
    "Gráfico 2": questao1,
    "Gráfico 3": questao1,
    "Gráfico 4": questao1,
    "Gráfico 5": questao1,
    "Gráfico 6": questao1,
    "Gráfico 7": questao1,
    "Gráfico 8": questao1,
    "Gráfico 9": questao1,
    "Gráfico 10": questao1,
    "Gráfico 11": questao1,
    "Gráfico 12": questao1,
    "Gráfico 13": questao1,
    "Gráfico 14": questao1,
    "Gráfico 15": questao1
    }

def switch(dayOfWeek):
    return switcher.get(dayOfWeek, default)()

switch(grafico)
