import streamlit as st
import mysql.connector
import switcher as switcher
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
    despesas = run_query("SELECT DISTINCT nome_grupo_despesa FROM grupos_despesas")
    grupo_despesas = []

    for grupo in despesas:
        gp = str(grupo)
        grupo_despesas.append(gp[2:-3])

    despesa = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = grupo_despesas)

    st.sidebar.markdown('## Região')
    regioes_base = run_query("SELECT DISTINCT uf FROM localidade")
    regioes = []

    for regiao in regioes_base:
        uf = str(regiao)
        regioes.append(uf[2:-3])

    regiao = st.sidebar.selectbox('Selecione a região que deseja saber a porcentagem', options = regioes)

    #escreve aqui a porcentagem (filtra do sql) - pega as variáveis despesa e regiao e faz uma query e o resultado da query escreve no write
    # run_query("SELECT * from fato_despesas;")

    st.write('valor aqui', '%')

def questao2():
    #https://docs.streamlit.io/library/api-reference/charts/st.pydeck_chart
    st.subheader('**2 - Cidades que receberam mais investimentos de programas orçamentários**')

def plot_acoes(dataframe, categoria):
    #alterar esses dados
    dados_plot = dataframe.query('Categoria == @categoria')

    fig, ax = plt.subplots(figsize=(8, 6))
    ax = sns.barplot(x='Ação', y='Despesa', data=dados_plot)
    ax.set_title(f'Menores despesas em ações orçamentárias na região', fontsize=16)
    ax.set_xlabel('Ação', fontsize=12)
    ax.tick_params(rotation=20, axis='x')
    ax.set_ylabel('Despesa', fontsize=12)

    return fig

def questao3():
    # https://www.alura.com.br/artigos/streamlit-compartilhando-sua-aplicacao-de-dados-sem-dor-de-cabeca

    st.subheader('**3 - Ações orçamentárias que causaram menos despesa para cada região brasileira**')

    st.sidebar.markdown('## Ações orçamentárias')
    acoes = run_query("escrever query aqui pra pegar os nomes das ações orçamentárias da base de dados")
    acoes_orcamentarias = []

    for acao in acoes:
       acoes_orcamentarias.append(acao)

    acao = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = acoes_orcamentarias)

    st.sidebar.markdown('## Região')
    regioes_base = run_query("escrever query aqui pra pegar os nomes das regioes da base de dados")
    regioes = []

    for regiao in regioes_base:
       regioes.append(regiao)

    regiao = st.sidebar.selectbox('Selecione a região que deseja saber a porcentagem', options = regioes)

    #tem que alterar aqui os dados que sao passados para essa funcao - filtrar da base os menores valores das ações de cada regiao
    grafico = plot_acoes(dados, categoria_grafico)
    st.pyplot(grafico)

def questao4():
    st.subheader('**4 - Programas orçamentários que causaram menos despesas**')

def questao5():
    #https://docs.streamlit.io/library/api-reference/charts/st.map
    st.subheader('**5 - Estados que investem mais em segurança pública e em educação**')

def questao6():
    st.subheader('**6 - Gasto total semanal da primeira semana (do dia 1 ao dia 8) de janeiro por cada estado**')

def questao7():
    st.subheader('**7 - Gastos com a segurança do Recife em janeiro**')

def questao8():
    st.subheader('**8 - Porcentagem de gastos com dívidas externas e internas no mês de janeiro**')

def questao9():
    st.subheader('**9 - No mês de janeiro, qual foi o valor empenhado, liquidado e pago para aposentadoria no estado de Pernambuco e que não tenha sido de dívida**')

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
    "Gráfico 2": questao2,
    "Gráfico 3": questao3,
    "Gráfico 4": questao4,
    "Gráfico 5": questao5,
    "Gráfico 6": questao6,
    "Gráfico 7": questao7,
    "Gráfico 8": questao8,
    "Gráfico 9": questao9
    }

def switch(dayOfWeek):
    return switcher.get(dayOfWeek, default)()

switch(grafico)
