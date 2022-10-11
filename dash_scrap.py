import pandas as pd
import numpy as np
import calendar
import datetime
import time  # to simulate a real time data, time loop
import requests
from datetime import timedelta
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
from PIL import Image
image = Image.open('logo.png')

date = datetime.datetime.utcnow()
utc_time = str(calendar.timegm(date.utctimetuple()))
from_time = str(int(utc_time) - 29784000  )  # hoje menos 40 dias
moedas = [
"cosmos", 
"algorand", 
"the-sandbox", 
"compound-governance-token", 
"matic-network", 
"uniswap",
"bitcoin",
'ethereum'
]
categoria = [
"Infraestrutura", 
"Infraestrutura", 
"Metaverso", 
"DeFi", 
"DeFi", 
"DeFi",
"Infraestrutura",
"Pagamento",
]
st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

def is_what_percent_of(num_a, num_b):
    return ((num_a - num_b) / num_b) * 100
    

@st.experimental_memo
def get_coin_change():
    d = {}
    teste = []
    for c in moedas:
        res = requests.get(f"https://api.coingecko.com/api/v3/coins/{c}/market_chart/range?vs_currency=usd&from={from_time}&to={utc_time}")
        res2 = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={c}&vs_currencies=usd")
        if (res.status_code != 204 and res.headers["content-type"].strip().startswith("application/json") and res2.status_code !=204 and res2.headers["content-type"].strip().startswith("application/json")
        ):
            try:
                data2 = res2.json()
                data = res.json()
                data2[c] = pd.DataFrame(data2).reset_index()
                valores = data2[c][c]
                prices = data['prices']
                data[c] = pd.DataFrame(prices, columns=['Data','Preço'])
                data[c]['Data'] = data[c]['Data'].astype(str).str[:10]
                data[c]['Data'] = pd.to_datetime(data[c]['Data'], unit='s')
                ult = data[c].groupby(data[c]['Data'].dt.date,group_keys=True)['Preço'].apply(lambda x: x.tail(1)).reset_index()
                data[c]['Data_i'] = data[c]['Data'] 
                data[c]['Preço'] = data[c]['Preço']
                #data[c]['Categoria'] = np.array(categoria)
                data[c].set_index(keys='Data_i', inplace=True)
                data[c]['Moeda Nome'] = c
                data[c] = data[c].between_time('00:00', '00:30')
                data[c]['Preço'] = data[c].Preço.shift(-1)
                data[c]['Moeda'] = c
                data[c].at[data[c]['Data'].iloc[-1],'Preço']  = valores
                P_hoje = data[c].at[data[c]['Data'].iloc[-1],'Preço']
                P_sete = data[c].at[data[c]['Data'].iloc[-1] - timedelta(days=8),'Preço']
                P_30 = data[c].at[data[c]['Data'].iloc[-1] - timedelta(days=31),'Preço']
                data[c]['Semanal'] = is_what_percent_of(P_hoje,P_sete) / 100
                data[c]['Mensal'] = is_what_percent_of(P_hoje,P_30) / 100
                print(data[c])
                teste.append(data[c].iloc[[-1]])
            except ValueError:
                print('deu merda')
     
   
    log = pd.concat(teste)
    final = pd.DataFrame(log)
    final.set_index('Moeda', inplace=True)
    final['Categoria'] = np.array(categoria)
    print(final)
    return final

df = get_coin_change()

# dashboard title
col1, col2, col3 = st.columns([14, 5, 15])
with col2:
    st.image("logo.png", width=200)

st.title("Crypto Overview")


# top-level filters


# creating a single-element container
placeholder = st.empty()

# dataframe filter
destaque_pst_7d = f"{df.loc[df.Semanal.idxmax(), 'Moeda Nome']}"
destaque_ngt_7d = f"{df.loc[df.Semanal.idxmin(), 'Moeda Nome']}"
destaque_pst_30d = f"{df.loc[df.Mensal.idxmax(), 'Moeda Nome']}"
destaque_ngt_30d = f"{df.loc[df.Mensal.idxmin(), 'Moeda Nome']}"
# near real-time / live feed simulation
for seconds in range(200):
    maior_semana = ('{:,.2%}'.format(df["Semanal"].max()))
    menor_semana = ('{:,.2%}'.format(df["Semanal"].min()))
    maior_mes =    ('{:,.2%}'.format(df["Mensal"].max()))
    menor_mes =    ('{:,.2%}'.format(df["Mensal"].min()))
    with placeholder.container():
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        kpi1.metric(
            label=f"Destaque Positivo (7d): {destaque_pst_7d}",
            value=maior_semana
        )
    
        kpi2.metric(
            label=f"Destaque Negativo(7d): {destaque_ngt_7d}",
            value=menor_semana
        )
    
        kpi3.metric(
            label=f"Destaque Positivo(30d): {destaque_pst_30d}",
            value=maior_mes
        )

        kpi4.metric(
            label=f"Destaque Negativo(30d): {destaque_ngt_30d}",
            value=menor_mes
        )



escolha_cat,  = st.columns([1])

with escolha_cat:
    escolher_catego = st.selectbox(
        "Selecione o setor",
        ("Todos", "Pagamento", "DeFi", "Metaverso", "GameFi", "Memecoin", "Armazenamento", "Layer 2"),
    )
    if escolher_catego != "Todos":
        df = df[df.Categoria == escolher_catego]


    fig = px.bar(
    data_frame=df, y="Semanal", x="Moeda Nome",
    )
    fig.update_layout(yaxis_tickformat = '.2%', )
    fig.update_traces(marker_color='rgb(223, 208, 134)')
    st.plotly_chart(fig, use_container_width=True)


    fig2 = px.bar(
    data_frame=df, x="Moeda Nome", y="Mensal")
    fig2.update_layout(yaxis_tickformat = '.2%')
    fig.update_traces(marker_color='rgb(223, 208, 134)')
    fig2.update_traces(marker_color='rgb(223, 208, 134)')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("Cotação Cripto")
    st.dataframe(df)
    time.sleep(1)

