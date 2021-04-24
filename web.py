import streamlit as st
import pandas as pd
import datetime

dia = datetime.datetime.now() - datetime.timedelta(days=1)

st.set_page_config(layout="wide",page_title="touristData",initial_sidebar_state="expanded")

"""
# touristData

Estudia la demanda de turistica de tu ciudad y adelanta tu negocio al mercado.
"""
st.text(f"ULTIMA ACTUALIZACION 2021-{dia.month:02d}-{dia.day:02d}")  
expander = st.beta_expander("Sobre nosotros")


expander.markdown("""

touristData es un proyecto desarrollado
por estudiantes del grado de
Ciencia de Datos por la Universitat Politècnica de València
para ayudar a los pequeños negocios
dependientes del turismo a predecir 
cuando reabrir sus negocios o a 
adaptar sus productos a la demanda.

Para usarlo, esocge tu ciudad y el periodo de tiempo que quieres analizar.

""")
"""

"""

provincia = st.sidebar.selectbox("Seleccione una ciudad",("Valencia", "Alicante", "Tenerife"))
number = st.sidebar.slider("Elige el rango en días entre los datos", 1, 7)
dia2 = datetime.datetime.now() - datetime.timedelta(days=number+1)

df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
df2 = pd.read_csv(f'2021-{dia2.month:02d}-{dia2.day:02d}.csv', delimiter=';')
    
      
df = df.loc[df["Ciudad de destino"] == provincia]
df2 = df2.loc[df2["Ciudad de destino"] == provincia]
df["Var"] = df["Precio"]
df2["Var"] = df2["Precio"]

rang = st.sidebar.radio("Escoge un rango", ["Todo el verano","Mes"])
if rang == "Mes":
    mes = st.sidebar.radio("Escoge un mes", ["Junio","Julio","Agosto"])
    if mes == "Junio":
        df = df.loc[df["Mes"]==6]
        df2 = df2.loc[df2["Mes"]==6]
    elif mes == "Julio":
        df = df.loc[df["Mes"]==7]
        df2 = df2.loc[df2["Mes"]==7]
    elif mes == "Agosto":
        df = df.loc[df["Mes"]==8]
        df2 = df2.loc[df2["Mes"]==8]


st.subheader("Variacion de demanda turística.")
st.text(f"Muestra el comportamiento del mercado para {provincia} por mercado emisor.")

df_verano = (df.groupby("País origen")["Var"].mean()/df2.groupby("País origen")["Var"].mean()-1)*100
st.bar_chart(df_verano)

d = df.loc[df["Es directo"]==1]
d2 = df2.loc[df2["Es directo"]==1]
df_vuelos = (df.groupby("País origen")["Es directo"].sum()/df2.groupby("País origen")["Es directo"].sum()-1)*100
st.subheader("Vuelos directos por día")
st.text("Aumento de los vuelos directos por mercado emisor")
st.bar_chart(df_vuelos)

"""
## Estudio por mercado

Escoge el mercado que más te interesa o todos y estudia como fluctua la demanda


"""

mercado = st.selectbox("Elige un mercado",("Todos","Reino Unido","Alemania", "Francia"))
if mercado != "Todos":
    df = df.loc[df["País origen"]==mercado]
    df2 = df2.loc[df2["País origen"]==mercado]



col1, col2 = st.beta_columns([5, 3])
j = (df.groupby("Ciudad origen")["Var"].mean()/df2.groupby("Ciudad origen")["Var"].mean()-1)*100
col1.subheader("Demanda por ciudad")
col1.bar_chart(j)
col2.subheader("")
col2.write(j)

