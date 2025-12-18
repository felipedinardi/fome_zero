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
    page_title=' Overview | Fome Zero!',
    page_icon='🍽️',
    layout='wide'
)

# =====================================
# CARREGAMENTO DOS DADOS
# 👉 ajuste o caminho conforme seu projeto
# =====================================
# df = pd.read_csv('seu_arquivo.csv')

# =====================================
# SIDEBAR
# =====================================
with st.sidebar:
    st.image('logo.png', use_container_width=True)
    st.markdown('---')

    # Filtro por país (default: todos)
    countries = sorted(df['Country Name'].unique())
    selected_countries = st.multiselect(
        'Countries:',
        options=countries,
        default=countries
    )

# Aplica filtro
filtered_df = df[df['Country Name'].isin(selected_countries)]

# =====================================
# TÍTULOS
# =====================================
st.title('Fome Zero!')
st.markdown('### The best place to find your next favorite restaurant !')

st.markdown('We have the following key figures on our platform:')

# =====================================
# KPIs
# =====================================
restaurantes_unicos = filtered_df['Restaurant Name'].nunique()
paises_unicos = filtered_df['Country Name'].nunique()
cidades_unicas = filtered_df['City'].nunique()
total_aval = filtered_df['Votes'].sum()
tipo_culinaria = filtered_df['Cuisines Unique'].nunique()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric('Registered Restaurants', restaurantes_unicos)
col2.metric('Registered Countries', paises_unicos)
col3.metric('Registered Cities', cidades_unicas)
col4.metric('Total Platform Reviews', f"{total_aval:,}")
col5.metric('Cuisines', tipo_culinaria)

st.markdown('---')

# =====================================
# MAPA
# =====================================
# Garante cor HEX válida
filtered_df['rating_color_hex'] = '#' + filtered_df['Rating color'].astype(str)

# Centro do mapa
map_center = [
    filtered_df['Latitude'].mean(),
    filtered_df['Longitude'].mean()
]

# Criação do mapa
m = folium.Map(
    location=map_center,
    zoom_start=3,
    tiles='OpenStreetMap'
)

# Pontos no mapa
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=4,
        color=row['rating_color_hex'],
        fill=True,
        fill_color=row['rating_color_hex'],
        fill_opacity=0.9,
        popup=folium.Popup(
            f"""
            <b>{row['Restaurant Name']}</b><br>
            País: {row.get('Country Name', 'N/A')}<br>
            Cidade: {row.get('City', 'N/A')}<br>
            Nota média: {row.get('Aggregate rating', 'N/A')}
            """,
            max_width=300
        )
    ).add_to(m)

# Exibição do mapa no Streamlit
st_folium(m, width=1200, height=600)


