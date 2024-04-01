# Abrir ambiente virutal (venv) -> source venv/bin/activate
# Executar o código e visualizaar -> streamlit run app.py 
import pandas as pd
import streamlit as st
import requests
import plotly.express as px

st.set_page_config(layout='wide') #setar o layout da pagina para melhorar a visualização


#Parametros do page config:
#page_title -> Define o título da página que será mostrado na aba do navegador.

#page_icon -> Define um ícone para a página que será mostrado na aba do navegador.
#             Pode ser uma imagem, uma url contendo uma imagem ou um emoji.

#layout -> Modifica o formato de visualização do aplicativo.
#          O padrão é 'centered', que posiciona os elementos centralizados em uma coluna de tamanho fixo,
#          mas pode ser trocado para 'wide', que utiliza todo o espaço da tela.

#initial_sidebar_state -> estado inicial da barra lateral. 
#                         O valor padrão é 'auto', que oculta a barra lateral em dispositivos móveis.
#                         Pode ser alterado para 'expanded' para sempre iniciar com a barra lateral à mostra ou
#                         'collapsed' para sempre iniciar com a barra lateral oculta.

#menu_items -> Configura, a partir de um dicionário de chave-valor, o menu que aparece no topo superior direito do aplicativo.
#              Podem ser alteradas 3 opções do menu:
#              -Get help: Altera a página de ajuda do app (URL)
#              -'Report bug': altera a página de reportar um bug no app (URL)
#              -'About': altera um texto de indormação sobre a página (String em markdown)

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) #Label, Valor Min, Valor Max

query_string = {
    'regiao':regiao.lower(),
    'ano':ano
}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados.Vendedor.unique())
if filtro_vendedores:
    dados = dados[dados.Vendedor.isin(filtro_vendedores)]




## Tabelas
## Tabelas de Receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoras = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Tabelas de quantidade de vendas
qtd_vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
qtd_vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(qtd_vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

qtd_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()

qtd_vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

## Tabelas vendedores

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

fig_mapa_receita = px.scatter_geo(receita_estados, 
                                  lat = 'lat',
                                  lon='lon',
                                  scope = 'south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data= {'lat': False, 'lon': False},
                                  title='Receita por Estado'
                                  )
fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal'
                             )
fig_receita_mensal.update_layout(yaxis_title = 'Receita')


fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y= 'Preço',
                             text_auto=True,
                             title='Top Estados (Receita)'
                             )
fig_receita_estados.update_layout(yaxis_title = 'Receita')


fig_receita_categoria = px.bar(receita_categoras,
                               text_auto=True,
                               title='Receita por Categoria') 
fig_receita_categoria.update_layout(yaxis_title = 'Receita')


fig_mapa_qtd_vendas_estados = px.scatter_geo(qtd_vendas_estados,
                                        lat = 'lat',
                                        lon='lon',
                                        scope = 'south america',
                                        size='Preço',
                                        template='seaborn',
                                        hover_name='Local da compra',
                                        hover_data= {'lat': False, 'lon': False},
                                        title='Quantidade de venda por Estado'
                                        )

fig_qtd_vendas_mensal = px.line(qtd_vendas_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,qtd_vendas_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Qantidade de Vendas Mensal'
                             )

fig_qtd_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_qtd_vendas_estados = px.bar(qtd_vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)
fig_qtd_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_qtd_vendas_categorias = px.bar(qtd_vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_qtd_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

## Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])
with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True) #Respeitar os limites de tamanho da coluna
        st.plotly_chart(fig_receita_estados, use_container_width=True) #Respeitar os limites de tamanho da coluna
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categoria, use_container_width=True) #Respeitar os limites de tamanho da coluna

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd_vendas_estados, use_container_width=True) #Respeitar os limites de tamanho da coluna
        st.plotly_chart(fig_qtd_vendas_estados, use_container_width=True)
        
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_vendas_mensal, use_container_width=True) #Respeitar os limites de tamanho da coluna
        st.plotly_chart(fig_qtd_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title= f'Top {qtd_vendedores} vendedores (Receita)'
                                        )
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)

    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title= f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)'
                                        )
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)       

