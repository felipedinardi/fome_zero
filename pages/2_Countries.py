import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium
from IPython.display import display

#------------------------------------------------------------------------------------------------------------
# Base carregada

df = pd.read_csv('dataset/zomato.csv')

#------------------------------------------------------------------------------------------------------------
# Funções

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def filter_max(Cuisine):
    df_filter = df[df['Cuisines Unique'] == Cuisine].groupby('Restaurant Name')['Aggregate rating'].mean().reset_index().sort_values(by='Aggregate rating', ascending=False)
    
    df_filter_max = df_filter['Aggregate rating'].max()
    
    df_max_restaurant = df_filter[['Restaurant Name']][df_filter['Aggregate rating'] == df_filter_max].head(1)
    
    return df_max_restaurant

def filter_min(Cuisine):
    df_filter = df[df['Cuisines Unique'] == Cuisine].groupby('Restaurant Name')['Aggregate rating'].mean().reset_index().sort_values(by='Aggregate rating', ascending=False)
    
    df_filter_min = df_filter['Aggregate rating'].min()
    
    df_min_restaurant = df_filter[['Restaurant Name']][df_filter['Aggregate rating'] == df_filter_min].head(1)
    
    return df_min_restaurant

#------------------------------------------------------------------------------------------------------------
# Bloco limpeza e tratamento de dados

# Início da limpeza, retirando possíveis espaços a mais nos campos object

cols = df.select_dtypes(include=['object']).columns

df[cols] = df[cols].select_dtypes(include=['object']).apply(lambda x: x.str.strip())

# Redefinindo a base com a exclusão dos dados NaN na coluna Cuisine. Métodos de imputação foram testados porém não foram efetivos

df = df[df['Cuisines'].notna()]

# Eliminar linhas duplicadas

df = df.drop_duplicates()

df['Country Name'] = df['Country Code'].apply(lambda x: country_name(x))
df['Price Type'] = df['Price range'].apply(lambda x: create_price_type(x))
df['Color Name'] = df['Rating color'].apply(lambda x: color_name(x))
df['Cuisines Unique'] = df.loc[:, "Cuisines"].apply(lambda x: x.split(",")[0])


# Correção nome dos países que estavam incorretos

df['Country Name'] = df['Country Name'].str.replace('Singapure','Singapore')
df['Country Name'] = df['Country Name'].str.replace('New Zeland','New Zealand')


# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(
    page_title='Countries View | Fome Zero',
    page_icon='🌍',
    layout='wide'
)

# =====================================
# CARREGAMENTO DOS DADOS
# =====================================
# df = pd.read_csv('seu_arquivo.csv')

# =====================================
# SIDEBAR (MESMA ESTRUTURA DA PÁGINA ANTERIOR)
# =====================================
with st.sidebar:
    st.image('logo.png', use_container_width=True)
    st.markdown('---')

    countries = sorted(df['Country Name'].unique())
    selected_countries = st.multiselect(
        'Countries:',
        options=countries,
        default=countries
    )

# Aplica filtro
filtered_df = df[df['Country Name'].isin(selected_countries)]

# =====================================
# TÍTULO
# =====================================
st.title('🌍 Countries View')

# =====================================
# GRÁFICO 1 – RESTAURANTES POR PAÍS
# =====================================
df_register_country = (
    filtered_df.groupby('Country Name')['Restaurant ID']
    .nunique()
    .reset_index()
    .sort_values(by='Restaurant ID', ascending=False)
)

fig1 = px.bar(
    df_register_country,
    x='Country Name',
    y='Restaurant ID',
    title='Number of Registered Restaurants by Country'
)

fig1.update_traces(marker_color='#4C78A8')
fig1.update_layout(
    xaxis_title='Country',
    yaxis_title='Restaurants',
    xaxis_tickangle=-45,
    margin=dict(l=110, r=40, t=60, b=120),
    height=500
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================
# GRÁFICO 2 – CIDADES POR PAÍS
# =====================================
df_register_city = (
    filtered_df.groupby('Country Name')['City']
    .nunique()
    .reset_index()
    .sort_values(by='City', ascending=False)
)

fig2 = px.bar(
    df_register_city,
    x='Country Name',
    y='City',
    title='Number of Registered Cities by Country'
)

fig2.update_traces(marker_color='#4C78A8')
fig2.update_layout(
    xaxis_title='Country',
    yaxis_title='Number of Cities',
    xaxis_tickangle=-45,
    margin=dict(l=110, r=40, t=60, b=120),
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================
# GRÁFICO 3 – MÉDIA DE AVALIAÇÕES
# =====================================
mean_country = (
    filtered_df.groupby('Country Name')['Votes']
    .mean()
    .reset_index(name='Mean Votes')
    .sort_values(by='Mean Votes', ascending=False)
)

fig3 = px.bar(
    mean_country,
    x='Country Name',
    y='Mean Votes',
    title='Rating Average by Country'
)

fig3.update_traces(marker_color='#4C78A8')
fig3.update_layout(
    xaxis_title='Country',
    yaxis_title='Rating Average',
    xaxis_tickangle=-45,
    margin=dict(l=110, r=40, t=60, b=120),
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================
# VISUALIZAÇÃO – PREÇO MÉDIO PARA DUAS PESSOAS
# =====================================
st.markdown('## Average Price for Two People by Country')

plate_avg = (
    filtered_df.groupby('Country Name')['Average Cost for two']
    .mean()
    .round(2)
    .reset_index()
)

# -------- Linha 1 (países com escala semelhante)
plate_avg_others = plate_avg[(plate_avg['Country Name'] != 'Indonesia') &
                             (plate_avg['Country Name'] != 'Australia') &
                             (plate_avg['Country Name'] != 'Sri Lanka') &
                             (plate_avg['Country Name'] != 'Philippines') &
                             (plate_avg['Country Name'] != 'India')]

fig4 = px.bar(
    plate_avg_others,
    x='Country Name',
    y='Average Cost for two',
    title='Average Price (Comparable Scale)'
)

fig4.update_traces(marker_color='#4C78A8')
fig4.update_layout(height=500)

st.plotly_chart(fig4, use_container_width=True)

# -------- Linha 2 (dois gráficos lado a lado)
col1, col2 = st.columns(2)

plate_avg_auind = plate_avg[(plate_avg['Country Name'] == 'Indonesia') |
                            (plate_avg['Country Name'] == 'Australia')]

fig5 = px.bar(
    plate_avg_auind,
    x='Country Name',
    y='Average Cost for two',
    title='Austrália, Indonésia'
)
fig5.update_traces(marker_color='#4C78A8')

with col1:
    st.plotly_chart(fig5, use_container_width=True)

plate_avg_pis = plate_avg[(plate_avg['Country Name'] == 'Philippines') |
                           (plate_avg['Country Name'] == 'India') |
                           (plate_avg['Country Name'] == 'Sri Lanka')]

fig6 = px.bar(
    plate_avg_pis,
    x='Country Name',
    y='Average Cost for two',
    title='Filipinas, Índia, Sri Lanka'
)
fig6.update_traces(marker_color='#4C78A8')

with col2:
    st.plotly_chart(fig6, use_container_width=True)

# Observação
st.markdown(
    '> **Note:** Multiple charts were created for this view because the values are expressed in each country’s local currency. Displaying all of them in a single chart would result in significant scale distortion.'
)

