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
    st.subheader('**1 - Porcentagem de gastos de cada grupo de despesa por estado**')

    st.sidebar.markdown('## Grupo de despesa')
    despesas = run_query("SELECT DISTINCT nome_grupo_despesa, grupo_despesa_id FROM grupos_despesas")
    grupo_despesas = []
    grupo_despesas_id = []

    for grupo in despesas:
        gp = str(grupo)
        if gp[2:-5] != "Indefinido":
            gp = str(grupo)
            grupo_despesas.append(gp[2:-5])
            grupo_despesas_id.append(gp[-3:-1])

    despesa = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = grupo_despesas)

    despesa_index = grupo_despesas.index(despesa)
    despesa_id = grupo_despesas_id[despesa_index]

    st.sidebar.markdown('## Estado')
    estados_base = run_query("SELECT DISTINCT uf, local_id FROM localidade")
    estados = []
    estados_id = []

    for estado in estados_base:
        uf = str(estado)
        if uf[2:-5] != "não informado":
            uf = str(estado)
            estados.append(uf[2:-5])
            estados_id.append(uf[-3:-1])

    estado = st.sidebar.selectbox('Selecione o estado que deseja saber a porcentagem', options = estados)

    estado_index = estados.index(estado)
    estado_id = estados_id[estado_index]

    query = query = "SELECT gd.nome_grupo_despesa,  " \
            "(sum(valor_pago) /  (select sum(valor_pago) " \
            "from fato_despesas fd " \
            "where fd.localidade_id = {0} "\
            "and f.grupo_despesa_id = {1})) * 100  as porcentagem "\
             "FROM fato_despesas f INNER JOIN grupos_despesas gd ON gd.grupo_despesa_id = f.grupo_despesa_id " \
             "WHERE  f.localidade_id = {2} " \
             "and  f.grupo_despesa_id = {3} "\
             "GROUP BY nome_grupo_despesa".format(estado_id, despesa_id, estado_id, despesa_id)

    porcentagem = run_query(query)

    st.write(porcentagem[0][1], '%')

def questao2():
    st.subheader('**2 - Estados investem mais em um órgão específico**')

    st.sidebar.markdown('## Órgão')
    orgaos = run_query("SELECT DISTINCT nome_orgao FROM orgaos")
    orgaos_base = []

    for orgao in orgaos:
        og = str(orgao)
        if og[2:-3] != "Indefinido" and og[2:-3] != "Sem informação":
            orgaos_base.append(og[2:-3])

    orgao = st.sidebar.selectbox('Selecione o órgão', options = orgaos_base)

    #fazer uma query que pegue aquele orgao e retorne os tres estados que mais investem nele
    estados_base = run_query("SELECT localidade.uf from fato_despesas INNER JOIN localidade "
                             "ON localidade.local_id = fato_despesas.localidade_id "
                             "where fato_despesas.orgao_superior_id "
                             "order by (select sum(valor_pago) from fato_despesas group by localidade_id limit 1)")
    estados = []

    for estado in estados_base:
        uf = str(estado)
        if uf[2:-3] != "não informado":
            estados.append(uf[2:-3])

    st.title("Estados que mais investem")
    for i in range(1, 4):
        st.write(i, ' - ', estados[i-1])

def questao3():
    st.subheader('**3 - Gasto total semanal por semana e por estado**')

    st.sidebar.markdown('## Estado')
    estados_base = run_query("SELECT DISTINCT uf, local_id FROM localidade")
    estados = []
    estados_id = []

    for estado in estados_base:
        uf = str(estado)
        if uf[2:-5] != "não informado":
            uf = str(estado)
            estados.append(uf[2:-5])
            estados_id.append(uf[-3:-1])

    estado = st.sidebar.selectbox('Selecione o estado que deseja consultar os gastos semanais', options=estados)

    estado_index = estados.index(estado)
    estado_id = estados_id[estado_index]

    st.sidebar.markdown('## Tempo')
    tempo_base = run_query("SELECT DISTINCT data_lancamento, tempo_id FROM tempo")
    data_lancamento = []
    tempo_id = []

    for tempo in tempo_base:
        tp = str(tempo)
        data_lancamento.append(tp[2:-5])
        tempo_id.append(tp[-3:-1])

    tempo = st.sidebar.selectbox('Selecione a data de lançamento que deseja consultar', options=data_lancamento)

    data_index = data_lancamento.index(tempo)
    data_id = tempo_id[data_index]

    gastos_base = run_query("select t.data_lancamento, (sum(valor_pago) /  (select sum(valor_pago) from fato_despesas fd "
                            "where fd.localidade_id = {0})) * 100  as porcentagem "
                            "FROM fato_despesas f INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                            "WHERE f.localidade_id = {1} and f.tempo_id = {2} GROUP BY data_lancamento".format(estado_id, estado_id, data_id))
    gastos = []

    for gasto in gastos_base:
        gastos.append(gasto)

    chart_data = pd.DataFrame(gastos, columns=['semanas'])
    st.line_chart(data=chart_data, x="Semana", y="Gastos")


def questao4():
    st.subheader('**4 - Gasto com programas orçamentários por cidade**')

    st.sidebar.markdown('## Estado')
    estados_base = run_query("SELECT DISTINCT uf, local_id FROM localidade")
    estados = []
    estados_id = []

    for estado in estados_base:
        uf = str(estado)
        if uf[2:-5] != "não informado":
            uf = str(estado)
            estados.append(uf[2:-5])
            estados_id.append(uf[-3:-1])

    estado = st.sidebar.selectbox('Selecione o estado que seja consultar as cidades e suas despesas com programas orçamentários', options = estados)

    estado_index = estados.index(estado)
    estado_id = estados_id[estado_index]

    query = run_query("select po.nome_programa_orcamentario, (sum(valor_pago) /  (select sum(valor_pago) "
                      "from fato_despesas fd where fd.localidade_id = {0})) * 100  as porcentagem "
                      "FROM fato_despesas f INNER JOIN programas_orcamentarios po "
                      "ON po.programa_orcamentario_id = f.programa_orcamentario_id WHERE f.localidade_id = {1} and "
                      "f.programa_orcamentario_id = {3}} GROUP BY nome_programa_orcamentario",format(estado_id, estado_id))

    for i in query:
        st.write(i)

    # #query para pegar as cidades do estado
    # cidades_base = run_query("SELECT DISTINCT uf FROM localidade")
    # cidades = []
    #
    # # query para pegar os gastos
    # gastos_base = run_query("SELECT DISTINCT uf FROM localidade")
    # gastos = []
    #
    # for cidade in cidades_base:
    #     cd = str(cidade[2:-3])
    #     cidades.append(cd)
    #
    # st.write(pd.DataFrame({
    #     'Cidade': cidades,
    #     'Gastos': gastos,
    # }))

def questao5():
    st.subheader('**5 - Porcentagem de gastos com um programa orçamentário específico**')

    st.sidebar.markdown('## Programa orçamentário')
    programas_orcamentarios = run_query("SELECT DISTINCT nome_programa_orcamentario, programa_orcamentario_id "
                                        "FROM programas_orcamentarios")
    programas = []
    programas_id = []

    for programa in programas_orcamentarios:
        pg = str(programa)
        if pg[2:-5] != "Indefinido":
            programas.append(pg[2:-6])
            programas_id.append(pg[-3:-1])

    programa = st.sidebar.selectbox('Selecione o programa orçamentário que deseja saber a porcentagem',
                                   options=programas)

    programa_index = programas.index(programa)
    programa_id = programas_id[programa_index]

    gastos = run_query("select po.nome_programa_orcamentario, (sum(valor_pago) /  (select sum(valor_pago) "
                        "from fato_despesas fd)) * 100  as porcentagem "
                        "FROM fato_despesas f INNER JOIN programas_orcamentarios po "
                        "ON po.programa_orcamentario_id = f.programa_orcamentario_id WHERE f.programa_orcamentario_id = {0} "
                        "GROUP BY nome_programa_orcamentario;".format(programa_id))

    st.write(gastos[0][1], '%')


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

for i in range(1, 7):
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
