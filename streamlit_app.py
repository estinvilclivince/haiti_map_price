import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import pydeck as pdk
import shapefile as shp
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from pprint import pprint
import json
import altair as alt



st.set_page_config(page_title='HAITI -  Product Price',
                   layout='wide', page_icon=':cereal:')

st.title("A Spacial-temporal view on  price in Haiti  ")
st.markdown(" **tel:** 509 36055983 **| email:** vitalralph@hotmail.com")
st.markdown(" **source:** https://fews.net ")

text1 = """
       # Context
        Haiti has experienced significant fluctuations in food prices,
        largely due to economic instability and natural disasters. 
        Over the years, the country has faced challenges like inflation,
        which has driven up the cost of staple foods such as rice, beans, 
        and cooking oil. Import dependency also makes Haiti vulnerable to global price changes.
        Additionally, political unrest and supply chain disruptions have further exacerbated price hikes,
        making food less accessible for many Haitians. Those graphes present a spacio-tempral view regarding
        the evoluation of different products price  in haiti.
        """

st.markdown(text1)


# t1.image('haiti-flag-square.jpg', width=120)





@st.cache_data
def get_original():
    depart_path  = Path(__file__).parent/'data/FEWS_NET_Staple_Food_Price_Data.csv'
    depart_df = pd.read_csv(depart_path)
    return depart_df

population_df = get_original()

dates = sorted(list(population_df['period_date'].unique()))
max_date = max(dates)
min_date = min(dates)

disable = False
with st.sidebar:
    st.write('Parameters: ')

    d_market = st.selectbox(
        "Choose a market",
        list(population_df['market'].unique()),
    )
      
    d_product =  st.selectbox(
      "Choose a product",
       list(population_df['product'].unique()),
    )
    
    # d_source =  st.selectbox(
    #   "Choose a product type",
    #    list(population_df['product_source'].unique()),
    # )

    date_selected = st.selectbox(
     "Select a range of color wavelength",
     dates
    )

population_df = get_original()
# selected column 
col_select  = ['market', 'admin_1', 'product','latitude', 'longitude', 'period_date','product_source', 'unit','currency', 'unit_type', 'value']
population_df = population_df[col_select] # selection columns
population_df['price'] = population_df['value']
#selected market
filter_market = population_df[population_df['market'] == d_market]

#select product
filter_product = population_df[(population_df['product']==d_product)]


#selected market and product
filter_market_product = population_df[(population_df['market'] == d_market) &
                                      (population_df['product'] == d_product)]


#selected market and product
filter_market_date = population_df[(population_df['market'] == d_market) &
                                      (population_df['period_date'] == date_selected)]


#selected date_product                                      
filter_date_product = population_df[(population_df['period_date'] == date_selected) &
                                      (population_df['product'] == d_product)]


with st.container():
    st.header('{0} Products Price for {1}'.format(d_market,date_selected))
    filter_market_date  = filter_market_date[['product', 'unit', 'value']]
    bars = alt.Chart(filter_market_date).mark_bar(color="steelblue").encode(
    x="product:O",
    y="value:Q",
    )
    st.altair_chart(bars, use_container_width=True)

    #st.dataframe(filter_market_date.style.highlight_max(axis=0))


print(filter_date_product)
with st.container():
    st.header(' {} Prices accross markets  ({})'.format(d_product, date_selected))
    m = folium.Map(location=[18.53, -72.33], zoom_start=7.45,width=1000,height=600, )
    group_1 = folium.FeatureGroup("HAiti  Population").add_to(m)
    for ele in filter_date_product.to_dict(orient='records'):
        folium.Marker(
        location=[ele['latitude'], ele['longitude']],
        popup=""" <b>Market:</b>{} <br> <b>Price: {}{} <br> 
            """.format(ele['market'], ele['value'], ele['currency']),  ).add_to(group_1)
#folium.GeoJson(road_json, name="Haitian roads").add_to(m)
#folium.GeoJson(airp_json, name="Haitian airports").add_to(m)
    folium.LayerControl().add_to(m)
    st_folium(m, width=1000, height=500)
    with st.expander("Why are the markets missing ?"):
        st.write(f"Price about {d_product} are available  from {min(filter_product['period_date'].unique())}")

markets = population_df['market'].unique()

if not len(markets):
    st.warning("Select at least one indicator")



with st.container():
    st.header(' {} Prices accross time  {}'.format(d_product, date_selected))
    selected_markets = st.multiselect(
    'Which markets would you like to view?',
    markets,
    ['Cap Haitien', 'Port-au-Prince, Croix-de-Bossales','Jacmel'])
    filter_product  = filter_product[filter_product['market'].isin(selected_markets)]
    c = alt.Chart(filter_product, title=' Markets Price over  time ').mark_line(
    point=alt.OverlayMarkDef(filled=False, fill="white")
    ).encode(
    x='period_date:T',
    y=alt.Y('price:Q'),
    color='admin_1:N'
    )
    st.altair_chart(c, use_container_width=True)