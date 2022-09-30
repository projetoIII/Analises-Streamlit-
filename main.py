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
    st.subheader('**1 - Porcentagem de gastos de cada grupo de despesa por estado em cada mês do ano**')

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

    despesa = st.sidebar.selectbox('Selecione o grupo de gastros que deseja saber a porcentagem', options = grupo_despesas, key = 1)
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

    estado = st.sidebar.selectbox('Selecione o estado que deseja saber a porcentagem', options = estados, key = 2)
    estado_index = estados.index(estado)
    estado_id = estados_id[estado_index]

    st.sidebar.markdown('## Ano')
    ano_base = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []

    for ano in ano_base:
        tp = str(ano)
        if (tp[2:-5] != "0000") and (tp[2:-5] not in anos):
            tp = str(ano)
            anos.append(tp[2:-5])

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anos, key = 3)

    st.sidebar.markdown('## Mês')
    meses_base = run_query("SELECT DISTINCT mes, tempo_id FROM tempo")
    meses = []
    meses_id = []

    for mes in meses_base:
        ms = str(mes)
        if ms[2:-5] != "Não especificada":
            ms = str(mes)
            meses.append(ms[2:-5])
            meses_id.append(ms[-3:-1])

    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses, key = 4)
    mes_index = meses.index(mes)
    mes_id = meses_id[mes_index]

    #retornar aqui tres valores, filtrados a cada mes
    query = "SELECT l.uf,  " \
            "(sum(valor_pago) /  (select sum(valor_pago) " \
            "from fato_despesas fd " \
            "where fd.localidade_id = {0} "\
            "and f.grupo_despesa_id = {1})) * 100  as porcentagem "\
             "FROM fato_despesas f INNER JOIN grupos_despesas gd " \
            "INNER JOIN tempo t ON t.tempo_id = f.tempo_id INNER JOIN localidade l " \
            "ON l.local_id = f.localidade_id " \
            "WHERE   f.grupo_despesa_id = {1} " \
            "and t.ano like '%2022%' and t.mes_numero = {2} " \
            "GROUP BY nome_grupo_despesa,localidade_id " \
            "ORDER BY porcentagem desc".format(estado_id, despesa_id, mes_id)

    porcentagem = run_query(query)

    if(len(porcentagem) != 0):
        st.write(porcentagem[0][1], '%')
    else :
        st.write("Não existe valor relacionado")

def questao2():
    st.subheader('**2 - Estados que mais investem em cada um dos órgãos e seus valores e em cada mês**')

    st.sidebar.markdown('## Órgão')
    orgaos = run_query("SELECT DISTINCT nome_orgao, orgao_id FROM orgaos")
    orgaos_base = []
    orgaos_id = []

    for orgao in orgaos:
        og = str(orgao)
        if og[2:-5] != "Indefinido" and og[2:-5] != "Sem informação":
            orgaos_base.append(og[2:-5])
            orgaos_id.append(og[-3:-1])

    orgao = st.sidebar.selectbox('Selecione o órgão', options=orgaos_base, key=1)

    orgao_index = orgaos_base.index(orgao)
    orgao_id = orgaos_id[orgao_index]

    st.sidebar.markdown('## Ano')
    ano_base = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []

    for ano in ano_base:
        tp = str(ano)
        if (tp[2:-5] != "0000") and (tp[2:-5] not in anos):
            tp = str(ano)
            anos.append(tp[2:-5])

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anos, key=2)

    st.sidebar.markdown('## Mês')
    meses_base = run_query("SELECT DISTINCT mes, tempo_id FROM tempo")
    meses = []
    meses_id = []

    for mes in meses_base:
        ms = str(mes)
        if ms[2:-5] != "Não especificada":
            ms = str(mes)
            meses.append(ms[2:-5])
            meses_id.append(ms[-3:-1])

    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses, key=3)
    mes_index = meses.index(mes)
    mes_id = meses_id[mes_index]

    estados_base = run_query("SELECT l.uf, sum(valor_pago) as valor_pago_total "
                             "from fato_despesas f INNER JOIN localidade l ON l.local_id = f.localidade_id "
                             "where f.orgao_superior_id = {0} and l.local_id != 0 group by l.uf "
                             "order by valor_pago_total desc".format(orgao_id, mes_id))

    estados = []
    valores = []

    for estado in estados_base:
        uf = str(estado)
        estados.append(uf[2:4])
        valores.append(uf[16:-3])

    st.title("Estados que mais investem")
    count = 0
    for i in range(0, len(estados)):
        if(valores[i] != '0.00'):
            count+=1
            st.write(i+1, ' - ', estados[i], ': R$', valores[i])

    if(count == 0):
        st.write("Não houveram investimentos para o órgão selecionado no período.")

def questao3():
    st.subheader('**3 - Soma de gastos pagos, liquidados e empenhados por programa do governo e por estado a em determinado mês**')

    st.sidebar.markdown('## Programa de governo')
    programas = run_query("SELECT DISTINCT nome_programa_governo, programa_governo_id FROM programas_governo")
    programas_base = []
    programas_id = []

    for programa in programas:
        og = str(programa)
        if og[2:-5] != "NAO ATRIBUIDO" and og[2:-5] != "Indefinido" and og[2:-5] != "Sem informação":
            programas_base.append(og[2:-5])
            programas_id.append(og[-3:-1])

    programa = st.sidebar.selectbox('Selecione o programa de governo', options=programas_base, key=1)

    programa_index = programas_base.index(programa)
    programa_id = programas_id[programa_index]

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

    estado = st.sidebar.selectbox('Selecione o estado que deseja consultar os gastos semanais', options=estados, key=2)

    estado_index = estados.index(estado)
    estado_id = estados_id[estado_index]

    st.sidebar.markdown('## Ano')
    ano_base = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []

    for ano in ano_base:
        tp = str(ano)
        if (tp[2:-5] != "0000") and (tp[2:-5] not in anos):
            tp = str(ano)
            anos.append(tp[2:-5])

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anos, key=3)

    st.sidebar.markdown('## Mês')
    meses_base = run_query("SELECT DISTINCT mes, tempo_id FROM tempo")
    meses = []
    meses_id = []

    for mes in meses_base:
        ms = str(mes)
        if ms[2:-5] != "Não especificada":
            ms = str(mes)
            meses.append(ms[2:-5])
            meses_id.append(ms[-3:-1])

    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses, key=4)
    mes_index = meses.index(mes)
    mes_id = meses_id[mes_index]

    #alterar query
    #gastos_base = run_query()

    #alterar ainda o modo de exibicao
    #st.write('R$',str(gastos_base[0][0]))


def questao4():
    st.subheader('**4 - Gasto com programas orçamentários por estado**')

    query = run_query("select l.uf, sum(valor_pago) as valor_pago_total FROM fato_despesas f "
                 "INNER JOIN localidade l on l.local_id = f.localidade_id "
                 "WHERE f.programa_orcamentario_id != -1 and l.local_id != 0 GROUP BY l.uf;")
    estados = []
    valores = []

    for valor in query:
        vl = str(valor)
        estados.append(str(vl[2:4]))
        valores.append(str(valor[1]))
    chart_data = pd.DataFrame(valores, estados)
    st.line_chart(data=chart_data)

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
