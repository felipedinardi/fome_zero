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

##Função filtro KPI
def filter_kpi(Cuisine):
    df_filter = df[df['Cuisines Unique'] == Cuisine].groupby('Restaurant Name')['Aggregate rating'].mean().reset_index().sort_values(by='Aggregate rating', ascending=False)
        
    df_filter['Aggregate rating'].max()
    return df_filter[['Restaurant Name', 'Aggregate rating']][df_filter['Aggregate rating'] == df_filter_max].head(1).T

    
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
    page_title='Cuisines View | Fome Zero',
    page_icon='🍝',
    layout='wide'
)

# =====================================
# CARREGAMENTO DOS DADOS
# =====================================
# df = pd.read_csv('seu_arquivo.csv')

# =====================================
# SIDEBAR (PADRÃO DAS PÁGINAS ANTERIORES)
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
# FUNÇÃO KPI – MELHOR RESTAURANTE POR TIPO
# =====================================
def filter_kpi(cuisine):
    aux = filtered_df[filtered_df['Cuisines Unique'] == cuisine]

    aux = aux.sort_values(
        by=['Aggregate rating', 'Votes'],
        ascending=False
    )

    if aux.empty:
        return {'Restaurant': 'N/A', 'Rating': 'N/A'}

    top = aux.iloc[0]

    return {
        'Restaurant': top['Restaurant Name'],
        'Rating': top['Aggregate rating']
    }

# =====================================
# TÍTULO
# =====================================
st.title('🍽️ Cuisines View')

# =====================================
# BLOCO 1 – KPIs PRINCIPAIS TIPOS
# =====================================
st.markdown('## Best Restaurants among the Main Cuisine Types')

kpi_italian = filter_kpi('Italian')
kpi_american = filter_kpi('American')
kpi_japanese = filter_kpi('Japanese')
kpi_indian = filter_kpi('Indian')
kpi_chinese = filter_kpi('Chinese')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric('Italian', kpi_italian['Restaurant'], kpi_italian['Rating'])

with col2:
    st.metric('American', kpi_american['Restaurant'], kpi_american['Rating'])

with col3:
    st.metric('Japanese', kpi_japanese['Restaurant'], kpi_japanese['Rating'])

with col4:
    st.metric('Indian', kpi_indian['Restaurant'], kpi_indian['Rating'])

with col5:
    st.metric('Chinese', kpi_chinese['Restaurant'], kpi_chinese['Rating'])

st.markdown('---')

# =====================================
# BLOCO 2 – TOP 10 RESTAURANTES
# =====================================
st.markdown('## Top 10 Restaurants')

df_top10 = (
    filtered_df[['Restaurant ID', 'Restaurant Name', 'Country Name', 'City',
                 'Cuisines Unique', 'Average Cost for two',
                 'Aggregate rating', 'Votes']]
    .sort_values(by=['Aggregate rating', 'Votes'], ascending=False)
    .head(10)
)

st.dataframe(df_top10, use_container_width=True)

st.markdown(
    '> **Note: The ranking criteria prioritize the highest average rating, followed by the highest number of votes.'
)

st.markdown('---')

# =====================================
# BLOCO 3 – MELHORES E PIORES TIPOS
# =====================================
col1, col2 = st.columns(2)

# -------- Melhores tipos
best_cuisines = (
    filtered_df.groupby('Cuisines Unique')['Aggregate rating']
    .mean()
    .reset_index()
    .sort_values(by='Aggregate rating', ascending=False)
    .head(10)
)

fig_best = px.bar(
    best_cuisines,
    x='Cuisines Unique',
    y='Aggregate rating',
    title='Top 10 Best Cuisine Types',
    color_discrete_sequence=px.colors.qualitative.Prism
)

with col1:
    st.plotly_chart(fig_best, use_container_width=True)

# -------- Piores tipos
bottom_cuisine = (
    filtered_df[filtered_df['Cuisines Unique'] != 'Drinks Only']
    .groupby('Cuisines Unique')['Aggregate rating']
    .mean()
    .reset_index()
    .sort_values(by='Aggregate rating', ascending=True)
    .head(10)
)

fig_bottom = px.bar(
    bottom_cuisine,
    x='Cuisines Unique',
    y='Aggregate rating',
    title='Top 10 Most Unpopular Cuisines',
    color_discrete_sequence=px.colors.qualitative.Prism
)

with col2:
    st.plotly_chart(fig_bottom, use_container_width=True)
