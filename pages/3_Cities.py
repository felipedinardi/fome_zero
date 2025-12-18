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
    page_title='Cities View | Fome Zero',
    page_icon='🏙️',
    layout='wide'
)

# =====================================
# CARREGAMENTO DOS DADOS
# =====================================
# df = pd.read_csv('seu_arquivo.csv')

# =====================================
# SIDEBAR (MESMA ESTRUTURA DAS PÁGINAS ANTERIORES)
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
st.title('🏙️ Cities View')

# =====================================
# BLOCO 1 – TOP 10 CIDADES COM MAIS RESTAURANTES
# =====================================
df_rest_country = (
    filtered_df.groupby(['City', 'Country Name'])['Aggregate rating']
    .count()
    .reset_index()
    .sort_values(by='Aggregate rating', ascending=False)
    .head(10)
)

fig_c = px.bar(
    df_rest_country,
    x='City',
    y='Aggregate rating',
    color='Country Name',
    title='Top 10 cities with the highest number of restaurants in the dataset',
    color_discrete_sequence=px.colors.qualitative.Prism
)

fig_c.update_layout(height=500)

st.plotly_chart(fig_c, use_container_width=True)

st.markdown('---')

# =====================================
# BLOCO 2 – AVALIAÇÕES ALTAS E BAIXAS
# =====================================
col1, col2 = st.columns(2)

# -------- Gráfico 1: Média > 4

df_agg = (
    filtered_df.groupby(['City', 'Country Name', 'Restaurant Name'])['Aggregate rating']
    .mean()
    .reset_index()
)

df_agg_fil = (
    df_agg[df_agg['Aggregate rating'] > 4]
    .groupby(['City', 'Country Name'])['Aggregate rating']
    .count()
    .reset_index()
    .sort_values(by='Aggregate rating', ascending=False)
    .head(7)
)

fig_agg = px.bar(
    df_agg_fil,
    x='City',
    y='Aggregate rating',
    color='Country Name',
    title='Top 7 cities with restaurants having an average rating above 4',
    color_discrete_sequence=px.colors.qualitative.Prism,
    category_orders={'City': df_agg_fil['City'].tolist()}
)

fig_agg.update_layout(height=450)

with col1:
    st.plotly_chart(fig_agg, use_container_width=True)

# -------- Gráfico 2: Média < 2.5

df_agg2 = (
    filtered_df.groupby(['City', 'Country Name', 'Restaurant Name'])['Aggregate rating']
    .mean()
    .reset_index()
)

df_agg_fil2 = (
    df_agg2[df_agg2['Aggregate rating'] < 2.5]
    .groupby(['City', 'Country Name'])['Aggregate rating']
    .count()
    .reset_index()
    .sort_values(by='Aggregate rating', ascending=False)
    .head(7)
)

fig_agg2 = px.bar(
    df_agg_fil2,
    x='City',
    y='Aggregate rating',
    color='Country Name',
    title='Top 7 cities with restaurants having an average rating below 2.5',
    color_discrete_sequence=px.colors.qualitative.Prism
)

fig_agg2.update_layout(height=450)

with col2:
    st.plotly_chart(fig_agg2, use_container_width=True)

st.markdown('---')

# =====================================
# BLOCO 3 – TIPOS CULINÁRIOS DISTINTOS
# =====================================
df_agg_unique = (
    filtered_df.groupby(['City', 'Country Name'])['Cuisines Unique']
    .nunique()
    .reset_index()
    .sort_values(by='Cuisines Unique', ascending=False)
    .head(10)
)

fig_agg_unique = px.bar(
    df_agg_unique,
    x='City',
    y='Cuisines Unique',
    color='Country Name',
    title='Top 10 cities with the highest number of restaurants offering distinct cuisine types',
    color_discrete_sequence=px.colors.qualitative.Prism
)

fig_agg_unique.update_layout(height=500)

st.plotly_chart(fig_agg_unique, use_container_width=True)
