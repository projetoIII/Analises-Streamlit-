import streamlit as st
import mysql.connector
import switcher as switcher
import pandas as pd
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

def estadosLista():
    estados_base = run_query("SELECT DISTINCT uf FROM localidade order by uf")
    estados = []

    for estado in estados_base:
        if estado[0] != "não informado":
            estados.append(estado[0])

    return estados

def grupoDespesaLista():
    despesas = run_query("SELECT DISTINCT nome_grupo_despesa, grupo_despesa_id FROM grupos_despesas")
    grupo_despesas = []
    grupo_despesas_id = []
    for grupo in despesas:
        grupo_despesas.append(grupo[0])
        grupo_despesas_id.append(grupo[1])

    return (grupo_despesas, grupo_despesas_id)


def anoLista():
    anoQuery = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []
    for ano in anoQuery:
        if (ano[0] != "0000") and (ano[0] not in anos):
            anos.append(ano[0])

    return anos

def mesLista():
    mesQuery = run_query("SELECT DISTINCT mes, tempo_id FROM tempo")
    meses = []
    meses_id = []
    for mes in mesQuery:
        if (mes[0] != "0000") and (mes[0] not in meses):
            meses.append(mes[0])
            meses_id.append(mes[1])
    return (meses, meses_id)

def programaGovernoLista():
    programas = run_query("SELECT DISTINCT nome_programa_governo, programa_governo_id FROM programas_governo")
    programas_base = []
    programas_id = []
    for programa in programas:
        programas_base.append(programa[0])
        programas_id.append(programa[1])
    return (programas_base, programas_id)

def programaOrcamentarioLista():
    programas = run_query("SELECT DISTINCT nome_programa_orcamentario, programa_orcamentario_id FROM programas_orcamentarios")
    programas_base = []
    programas_id = []

    for programa in programas:
        programas_base.append(programa[0])
        programas_id.append(programa[1])

    return (programas_base, programas_id)

def trimestreLista():
    trimestre_base = run_query("SELECT DISTINCT trimestre FROM tempo")
    trimestres = []

    for trimestre in trimestre_base:
        if (trimestre[0] != 0):
            trimestres.append(trimestre[0])
    return trimestres

def orgaosLista():
    orgaos = run_query("SELECT DISTINCT nome_orgao, orgao_id FROM orgaos")
    orgaos_base = []
    orgaos_id = []

    for orgao in orgaos:
        orgaos_base.append(orgao[0])
        orgaos_id.append(orgao[1])
    return (orgaos_base, orgaos_id)

def questao1():
    st.subheader('**1 - Porcentagem de gastos de cada grupo de despesa por estado em cada mês do ano**')

    st.sidebar.markdown('## Grupo de despesa')

    gruposDespesas = grupoDespesaLista()
    despesa = st.sidebar.selectbox('Selecione o grupo de gastos que deseja saber a porcentagem', options = gruposDespesas[0], key = 1)
    despesa_index = gruposDespesas[0].index(despesa)
    despesa_id = gruposDespesas[1][despesa_index]

    st.sidebar.markdown('## Estado')

    estado = st.sidebar.selectbox('Selecione o estado que deseja saber a porcentagem', options = estadosLista(), key = 2)

    st.sidebar.markdown('## Ano')

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anoLista(), key = 3)

    st.sidebar.markdown('## Mês')

    meses = mesLista()
    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses[0], key = 4)
    mes_index = meses[0].index(mes)
    mes_id = meses[1][mes_index]

    #retornar aqui tres valores, filtrados a cada mes
    query = "SELECT ((select sum(valor_pago) from fato_despesas fd " \
            "INNER JOIN localidade l ON l.local_id = fd.localidade_id " \
            "INNER JOIN tempo t ON t.tempo_id = fd.tempo_id "\
            "where fd.grupo_despesa_id = {0} and l.uf = '{2}' and t.tempo_id = {1})/(select sum(valor_pago) " \
            "from fato_despesas fd " \
            "INNER JOIN tempo t ON t.tempo_id = fd.tempo_id " \
            "INNER JOIN localidade l ON l.local_id = fd.localidade_id " \
            "where t.tempo_id = {1} and l.uf = '{2}')) * 100  as porcentagem " \
            "FROM fato_despesas f " \
            "INNER JOIN grupos_despesas gd ON gd.grupo_despesa_id = f.grupo_despesa_id " \
            "INNER JOIN tempo t ON t.tempo_id = f.tempo_id " \
            "INNER JOIN localidade l ON l.local_id = f.localidade_id " \
            "WHERE f.grupo_despesa_id = {0} and t.ano like '%{3}%' and t.tempo_id = {1} and l.uf = '{2}' " \
            "GROUP BY l.uf ORDER BY porcentagem desc;".format(despesa_id, mes_id, estado, ano)

    porcentagem = run_query(query)

    if(len(porcentagem) != 0):
        st.write(porcentagem[0][0], '%')
    else :
        st.write("Não existe valor relacionado")

def questao2():
    st.subheader('**2 - Estados que mais investem em cada um dos órgãos e seus valores e em cada mês**')

    st.sidebar.markdown('## Órgão')
    orgaos = orgaosLista()
    orgao = st.sidebar.selectbox('Selecione o órgão', options=orgaos[0], key=1)

    orgao_index = orgaos[0].index(orgao)
    orgao_id = orgaos[1][orgao_index]

    st.sidebar.markdown('## Ano')

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anoLista(), key=2)

    st.sidebar.markdown('## Mês')

    meses = mesLista()
    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses[0], key=3)

    estados_base = run_query("SELECT l.uf, sum(valor_pago) as valor_pago_total "
                             "from fato_despesas f "
                             "INNER JOIN localidade l "
                             "ON l.local_id = f.localidade_id "
                             "INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                             "where f.orgao_superior_id = {0} and l.local_id != 0 "
                             "and t.mes = '{1}' "
                             "and t.ano like '%2022%' group by l.uf order by valor_pago_total desc ".format(orgao_id, mes))

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
    st.subheader('**3 -Quanto foi os valores pagos, liquidados e empenhados por programa do governo e por estado a em determinado mês?**')

    st.sidebar.markdown('## Estado')

    estado = st.sidebar.selectbox('Selecione o Estado:', options=estadosLista(), key=1)

    st.sidebar.markdown('## Programa Governo')
    
    programas = programaGovernoLista()
    programa = st.sidebar.selectbox('Selecione o Programa:', options=programas[0], key=2)
    programa_index = programas[0].index(programa)
    programa_id = programas[1][programa_index]

    st.sidebar.markdown('## Ano')

    ano = st.sidebar.selectbox('Selecione o ano:', options=anoLista(), key=3)

    st.sidebar.markdown('## Mês')

    meses = mesLista()
    mes = st.sidebar.selectbox('Selecione o mês:', options=meses[0], key=4)


    resultado = run_query("select sum(valor_empenhado), sum(valor_liquidado), sum(valor_pago) "
                            "FROM fato_despesas f "
                            "INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                            "INNER JOIN localidade l ON l.local_id = f.localidade_id "
                            "WHERE f.programa_governo_id = {3} "
                            "and t.ano like '%{0}%' "
                            "and t.mes = '{1}' "
                            "and l.uf = '{2}'".format(ano, mes, estado, programa_id))
    #alterar ainda o modo de exibicao
    for i in resultado:
        st.write(i)
    #st.write('R$',str(gastos_base[0][0]))

def questao4():
    st.subheader('**4 - Unidades orçamentárias que mais receberam de despesas de valor pago e quanto foi deixado de pagar do resto de valores a pagar inscritos por mês e por ano  e quanto receberam**')

    st.sidebar.markdown('## Ano')
    ano_base = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []

    for ano in ano_base:
        tp = str(ano)
        if (tp[2:-5] != "0000") and (tp[2:-5] not in anos):
            tp = str(ano)
            anos.append(tp[2:-5])

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anos, key=1)

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

    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses, key=2)
    mes_index = meses.index(mes)
    mes_id = meses_id[mes_index]

    query = run_query("select  u.nome_unidade_orcamentaria, sum(valor_pago) as valor_pago, "
                      "sum(valor_resto_pagar_inscrito) as valor_resto "
                      "FROM fato_despesas f "
                      "INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                      "INNER JOIN localidade l ON l.local_id = f.localidade_id "
                      "INNER JOIN unidades_orcamentarias u ON u.unidade_orcamentaria_id = f.unidade_orcamentaria_id "
                      "and t.ano like '%2022%' and f.tempo_id = {0} "
                      "GROUP BY f.unidade_orcamentaria_id "
                      "ORDER BY valor_pago desc".format(mes_id))

    for i in query:
        st.write(i)

def questao5():
    st.subheader('**5 - Relação entre o mês, ano e valor pago por despesa por programa orçamentário**')

    st.sidebar.markdown('## Ano')
    ano_base = run_query("SELECT DISTINCT ano, tempo_id FROM tempo")
    anos = []

    for ano in ano_base:
        tp = str(ano)
        if (tp[2:-5] != "0000") and (tp[2:-5] not in anos):
            tp = str(ano)
            anos.append(tp[2:-5])

    ano = st.sidebar.selectbox('Selecione o ano que deseja saber a porcentagem', options=anos, key=1)

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

    mes = st.sidebar.selectbox('Selecione o mês que deseja saber a porcentagem', options=meses, key=2)
    mes_index = meses.index(mes)
    mes_id = meses_id[mes_index]

    gastos = run_query("select  p.nome_programa_orcamentario, sum(valor_pago) as valor_pago "
                       "FROM fato_despesas f "
                       "INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                       "INNER JOIN programas_orcamentarios p ON p.programa_orcamentario_id = f.programa_orcamentario_id "
                       "WHERE t.ano like '%2022%' and f.tempo_id = {0} "
                       "GROUP BY f.programa_orcamentario_id "
                       "order by valor_pago desc".format(mes_id))

    for i in gastos:
        st.write(i)

def questao6():
    st.subheader('**6 - Quais os órgãos com maior valor empenhado por estado, e quanto foi empenhado por mês?**')

    st.sidebar.markdown('## Mês')

    meses = mesLista()
    mes = st.sidebar.selectbox('Selecione o mês:', options=meses[0], key=1)

    mes_index = meses[0].index(mes)
    mes_id = meses[1][mes_index]

    st.sidebar.markdown('## Estado')

    estado = st.sidebar.selectbox('Selecione o estado:', options=estadosLista(), key=2)
    resultado = run_query("select FORMAT(sum(valor_empenhado), 2, 'de_DE') as valor_total_empenhado, nome_orgao "
                        "FROM fato_despesas f INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                        "INNER JOIN localidade l ON l.local_id = f.localidade_id "
                        "INNER JOIN orgaos o ON o.orgao_id = f.orgao_superior_id "
                        "WHERE t.tempo_id = {0} and uf = '{1}' and valor_empenhado > 0 GROUP BY o.nome_orgao "
                        "order by valor_total_empenhado desc ".format(mes_id, estado))

    valores = []
    orgaos = []
    for valor in resultado:
        st.write("Órgão: {1}, Valor: R$ {0}".format(valor[0], valor[1]))
        valores.append(valor[1])
        orgaos.append(valor[0])

    fig = plt.figure(figsize = (10, 5))
    plt.bar(orgaos, valores)
    plt.xlabel("Valor")
    plt.ylabel("Órgãos")
    plt.title("Órgão x Valor")
    st.pyplot(fig)

def questao7():
    st.subheader('**7 - Quanto foi a diferença do valor que foi reservado e do que foi realmente pago para cada um dos programas orçamentários por estado e trimestre? E qual porcentagem das despesas tiveram valores empenhados e pagos diferentes?**')

    st.sidebar.markdown('## Estado')
    estado = st.sidebar.selectbox('Selecione o estado que deseja consultar os gastos semanais', options=estadosLista(), key=1)

    st.sidebar.markdown('## Ano')

    ano = st.sidebar.selectbox('Selecione o ano:', options=anoLista(), key=2)

    st.sidebar.markdown('## Programa Orçamentário')

    programas = programaOrcamentarioLista()
    programa = st.sidebar.selectbox('Selecione o programa orçamentário', options=programas[0], key=3)

    programa_index = programas[0].index(programa)
    programa_id = programas[1][programa_index]


    st.sidebar.markdown('## Trimestre')

    trimestre = st.sidebar.selectbox('Selecione o Trimestre:', options=trimestreLista(), key=4)


    # adicionar query aqui
    query = run_query("select (sum(valor_empenhado) - sum(valor_pago)) as diferenca_valor_empenhado_pago, "
                       "((select count(*) as qtd_despesas_negativas from fato_despesas "
                       "INNER JOIN localidade l ON l.local_id = localidade_id "
                       "where valor_empenhado <> valor_pago and l.uf = '{0}' and programa_orcamentario_id = {3}) "
                       " / (select count(*) as qtd_despesas from fato_despesas "
                       " INNER JOIN localidade l ON l.local_id = localidade_id "
                       " where l.uf = '{0}' and programa_orcamentario_id = {3})) * 100 as porcentagem "
                       "FROM fato_despesas f "
                       "INNER JOIN tempo t ON t.tempo_id = f.tempo_id "
                       "INNER JOIN localidade l ON l.local_id = f.localidade_id "
                       "WHERE t.ano like '%{1}%' "  
                       "and l.uf = '{0}' "
                       "and t.trimestre = {2} "
                       "and programa_orcamentario_id = {3};".format(estado, ano, trimestre, programa_id))

    if (query[0][0] is not None):
        st.write("**Diferença de: R$ {0}**".format(query[0][0]))

        if (query[0][0] >= 0):
            st.write("Isso significa que a soma dos valores pago foram menores ou iguais a dos empenhados")
        else: 
            st.write("Isso significa que a soma dos valores pagos foram maiores do que a dos empenhados")

        fig = plt.figure(figsize=(10, 4))
        diferencaPorcentagem = 100-query[0][1]
        plt.pie([query[0][1], diferencaPorcentagem], labels =  ["Valores Pagos Diferentes dos Empenhados","Valores Pagos de Acordo"], autopct='%.1f%%')

        st.pyplot(fig)
    else:
        st.write("Não existe valor relacionado")
    
    

def default():
    return "Incorreto"
#----------------------------------------------------------------------------

questoes = []

for i in range(1, 8):
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
    "Gráfico 7": questao7
    }

def switch(dayOfWeek):
    return switcher.get(dayOfWeek, default)()

switch(grafico)
