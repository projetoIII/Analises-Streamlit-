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

#DAQUI PRA BAIXO COMEÇO A FAZER OS GRÁFICOS DINAMICOS PARA CADA QUESTÃO

def estadosLista():
    estados_base = run_query("SELECT DISTINCT uf FROM localidade")
    estados = []

    for estado in estados_base:
        uf = str(estado)
        estados.append(uf[2:-3])

    return estados

def questao1():
    # https://www.alura.com.br/artigos/streamlit-compartilhando-sua-aplicacao-de-dados-sem-dor-de-cabeca

    st.subheader('**1 - Porcentagem de gastos de cada grupo de despesa por estado**')

    st.sidebar.markdown('## Grupo de despesa')
    despesas = run_query("SELECT DISTINCT nome_grupo_despesa FROM grupos_despesas")
    grupo_despesas = []

    for grupo in despesas:
        gp = str(grupo)
        grupo_despesas.append(gp[2:-3])

    despesa = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = grupo_despesas)

    st.sidebar.markdown('## Estado')
    estados = estadosLista()

    estado = st.sidebar.selectbox('Selecione o estado que deseja saber a porcentagem', options = estados)

    query = "SELECT grupo_despesa.nome_grupo_despesa, fato_despesas.grupo_despesa_id as grupo, " \
             "count(select count(fato_despesas.valor_pago) from fatos_despesas where fatos.grupo_despesa_id = grupo)* 100.0 / sum(fato_despesas.valor_pago) as pcrt " \
             "FROM fato_despesas INNER JOIN grupo_despesa ON grupo_despesa.id = fato_despesas.grupo_despesa_id " \
             "INNER JOIN localidade ON localidade.id = fato_despesas.localidade.id " \
             "WHERE localidade.uf =" + estado + "GROUP BY group_despesas;"

    #escreve aqui a porcentagem (filtra do sql) - pega as variáveis despesa e regiao e faz uma query e o resultado da query escreve no write
    porcentagem = run_query(query)

    st.write(porcentagem, '%')

def questao2():
    st.subheader('**2 - Estados investem mais em um órgão específico**')

    st.sidebar.markdown('## Órgão')
    orgaos = run_query("SELECT DISTINCT nome_orgao FROM orgaos")
    orgaos_base = []

    for orgao in orgaos:
        og = str(orgao)
        orgaos_base.append(og[2:-3])

    orgao = st.sidebar.selectbox('Selecione o órgão', options = orgaos_base)

    #fazer uma query que pegue aquele orgao e retorne os tres estados que mais investem nele
    estados = estadosLista() #trocar isso aqui pelo resultado da query

    st.title("Estados que mais investem")
    for i in range(1, 4):
        st.write(i, ' - ', estados[i-1])

def questao3():
    st.subheader('**3 - Gasto total semanal por semana e por estado**')

def questao4():
    st.subheader('**4 - Gasto com programas orçamentários por cidade**')

    estados = estadosLista()
    estado = st.sidebar.selectbox('Selecione o estado que seja consultar as cidades e suas despesas com programas orçamentários', options = estados)

    #query para pegar as cidades do estado
    cidades_base = run_query("SELECT DISTINCT municipio FROM localidade WHERE ------")
    cidades = []

    # query para pegar os gastos
    gastos_base = run_query("SELECT DISTINCT municipio FROM localidade WHERE ------")
    gastos = []

    for cidade in cidades_base:
        cd = str(cidade[2:-3])
        cidades.append(cd)

    st.write(pd.DataFrame({
        'Cidade': cidades,
        'Gastos': gastos,
    }))


def questao5():
    st.subheader('**5 - Porcentagem de gastos com um programa orçamentário específico**')

def questao6():
    st.subheader('**6 - Valor empenhado, liquidado e pago por ação num estado específico e que não tenha sido de dívida**')


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
    "Gráfico 6": questao6
    }

def switch(dayOfWeek):
    return switcher.get(dayOfWeek, default)()

switch(grafico)
