import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='')

st.set_page_config( page_title = 'Home', layout='wide')

#image_path = '/Users/felip/Desktop/Comunidade DS/FTC/final_project/'
image = Image.open('logo.png')

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('''---''')

st.write('# Fome Zero Dashboard')

st.markdown(
    '''
Fome Zero Dashboard was built to monitor the company’s growth metrics.  

### How to use this Dashboard?
- **Overview**
    - Strategic KPIs and a map view showing the global distribution of restaurants.
- **Countries View**
    - Indicators related to restaurants by country.
- **Cities View**
    - Indicators related to restaurants by city.
- **Cuisines View**
    - Indicators related to different types of cuisine.

All information can be filtered by country.
''')

