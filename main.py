import streamlit as st
import mysql.connector
import switcher as switcher
import pandas as pd

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

    query = "SELECT gd.nome_grupo_despesa,  " \
            "(sum(valor_pago) /  (select sum(valor_pago) " \
            "from fato_despesas fd " \
            "where fd.localidade_id = 2 " \
            "and f.grupo_despesa_id = 3)) * 100  as porcentagem " \
            "FROM fato_despesas f INNER JOIN grupos_despesas gd ON gd.grupo_despesa_id = f.grupo_despesa_id " \
            "WHERE  f.localidade_id = 2 " \
            "and  f.grupo_despesa_id = 3 " \
            "GROUP BY nome_grupo_despesa;"

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
    estados = run_query("SELECT DISTINCT uf FROM localidade")

    st.title("Estados que mais investem")
    for i in range(1, 4):
        st.write(i, ' - ', estados[i-1])

def questao3():
    st.subheader('**3 - Gasto total semanal por semana e por estado**')

    st.sidebar.markdown('## Estado')
    estados = estadosLista()
    estado = st.sidebar.selectbox('Selecione o estado que deseja consultar os gastos semanais', options=estados)

    gastos_base = run_query("SELECT DISTINCT uf FROM localidade") #fazer a query pra retornar os valores por semana
    gastos = []

    for gasto in gastos_base:
        gastos.append(gasto)

    chart_data = pd.DataFrame(gastos, columns=['semanas'])
    st.line_chart(data=chart_data, x="Semana", y="Gastos")


def questao4():
    st.subheader('**4 - Gasto com programas orçamentários por cidade**')

    st.sidebar.markdown('## Estado')
    estados = estadosLista()
    estado = st.sidebar.selectbox('Selecione o estado que seja consultar as cidades e suas despesas com programas orçamentários', options = estados)

    #query para pegar as cidades do estado
    cidades_base = run_query("SELECT DISTINCT uf FROM localidade")
    cidades = []

    # query para pegar os gastos
    gastos_base = run_query("SELECT DISTINCT uf FROM localidade")
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

    st.sidebar.markdown('## Programa orçamentário')
    programas_orcamentarios = run_query("SELECT DISTINCT uf FROM localidade") #ajeitar essa query
    programas = []

    for programa in programas_orcamentarios:
        pg = str(programa)
        programas.append(pg[2:-3])

    programa = st.sidebar.selectbox('Selecione o programa orçamentário que deseja saber a porcentagem',
                                   options=programas)

    gasto_total = run_query("SELECT DISTINCT uf FROM localidade") # query que retorno o total de gasto de todos os programas orcamentarios
    gasto_programa = run_query("SELECT DISTINCT uf FROM localidade") #query que retorne o valor total do programa orcamentario especifico

    porcentagem = "fazer aqui uma conta pra descobrir sua porcentagem"

    st.write(porcentagem, '%')

def questao6():
    st.subheader('**6 - Valor empenhado, liquidado e pago por ação num estado específico e que não tenha sido de dívida**')

    st.sidebar.markdown('## Estados')
    estados = estadosLista()
    estado = st.sidebar.selectbox(
        'Selecione o estado que seja consultar uma ação', options=estados)

    st.sidebar.markdown('## Ação orçamentária')
    acoes_base = run_query("SELECT DISTINCT uf FROM localidade") #corrigir query
    acoes = []

    for acao in acoes_base:
        ac = str(acao)
        acoes.append(ac[2:-3])

    acao = st.sidebar.selectbox('Selecione ação orçamentária que deseja saber os valores',
                                   options=acoes)

    valores_base = run_query("SELECT DISTINCT uf FROM localidade") #query que retorne o valor empenhado, liquidado e pago
    valores = []

    for valor in valores_base:
        valores.append(valor)

    st.title("Valor empenhado, liquidado e pago pela ação ", acao, " no estado ", estado)
    st.write("Valor empenhado: ", valores[0])
    st.write("Valor liquidado: ", valores[1])
    st.write("Valor pago: ", valores[2])


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
