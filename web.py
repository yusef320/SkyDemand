# Autor: Yusef Ahsini Ouariaghli

import streamlit as st
import pandas as pd
import datetime
import smtplib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from PIL import Image
import plotly.express as px


############################################
#####           FUNCIONES               ####
############################################

@st.cache
def predicción(fec, datos, oferta, dato):
    """
    Modelo predictivo.
    """
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop([dato], axis=1)
    test = p[dato]
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=0.85, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    i=0
    for elemento in pred:
        if i >= 3: break
        demanda.append(round(elemento,0))
        i+=1
    demanda.append(p[dato][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.NaN)

    if dato == "Nº de plazas":
        name = "Pred. nº de plazas"
    else:
        name = "Predicción precio"

    return pd.Series(data=demanda, index=fec, name=name)

@st.cache
def variacion(provincia,delta, mercado, rang, x,i):
    """
    Devuelve un dataframe con la variación de las tarifas
    y el número de vuelos asi como la predicción para ambas.
    """
    datos,fec,oferta  = [np.NaN,np.NaN,np.NaN], [], [np.NaN,np.NaN,np.NaN]
    if mercado == "todos":
        a = "Ciudad de destino"
        mercado = provincia
    else:
        a = "País origen"

    for z in range(1,4):
        dia = datetime.datetime.now() + datetime.timedelta(days=z-i)
        fecha = f"{dia.month:02d}-{dia.day:02d}"
        fec.append(fecha)

    for p in range(0, delta):
        dia = datetime.datetime.now() - datetime.timedelta(days=p+i)
        d = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
        d = d.loc[d["Ciudad de destino"] == provincia]
        if rang == "Mes":
            d = d.loc[d["Mes"]==x]
        elif rang == "Día":
            d = d.loc[d["Mes"]==x[0]]
            d = d.loc[d["Dia"]==x[1]]
        df_demanda = d.groupby(a)["Es directo"].count()*189
        d = d.loc[d["Es directo"]==1]
        df_verano = d.groupby(a)["Precio"].mean()
        s= round(df_verano[mercado],2)
        datos.append(s)
        fecha = f"{dia.month:02d}-{dia.day:02d}"
        fec.append(fecha)
        o= round(df_demanda[mercado],2)
        oferta.append(o)

    dat = pd.Series(data=datos, index=fec, name="Precio medio")
    var = pd.Series(data=oferta, index=fec, name="Nº de plazas")
    pred1 = predicción(fec, dat, var,"Precio medio")
    pred2 = predicción(fec, dat, var, "Nº de plazas")
    p = pd.concat([dat, pred1], axis=1)
    v = pd.concat([var, pred2], axis=1)
    return [p,v]

def enviar(email, provincia):
    """
    Suscribe a los emails en el newsletter
    """
    conn = smtplib.SMTP("smtp.gmail.com", 587)
    conn.ehlo()
    conn.starttls()
    conn.login(usuario,contra)
    conn.sendmail(usuario,usuario,f"Subject:Suscripcion {provincia} {email}")
    conn.sendmail(usuario,email,f"Subject:Bienvenido \n\nLe damos la bienvenida al newsletter de SkyDemand sobre {provincia}. Cada vez que se produzca una fluctuacion importante en la demanda basada en el precio de los vuelos (de mas del 5%) le enviaremos un informe semanal sobre como ha evolucionado el mercado dia a dia.\n\nUn saludo,\n\nel equipo de SkyDemand.")

def color(provincia, num):
    """
    devuelve el color del semáforo
    """
    if provincia == "Tenerife":
        max, min = 190,120 #rango obtenido mediante busquedas en Google flights
    elif provincia == "Valencia":
        max, min = 140,90
    else:
        max, min = 150,100

    if num >= max:
        return "#33FF00"
    elif num>=min and num<max:
        return "#FFFB00"
    else:
        return "#F91212"
############################################################
####                CONFIGURAMOS LA PÁGINA              ####
############################################################


img = Image.open("logopag.png")
st.set_page_config(layout="wide",page_title="SkyDemand",page_icon=img,initial_sidebar_state="expanded", ) #configuramos la página
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style,unsafe_allow_html=True)

#Comprobamos si hay una ultima actualización para los datos
try:
    dia = datetime.datetime.now() #Día de hoy
    df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    i=0
except:
    dia = datetime.datetime.now() - datetime.timedelta(days=1) #dia de ayer
    df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    i=1

delta = dia - datetime.datetime(2021,4,18)
delta = delta.days +1

###########################################################
####                CUERPO DE LA PÁGINA                ####
###########################################################

# Barra lateral

provincia = st.sidebar.selectbox("Seleccione una ciudad",("Valencia", "Alicante", "Tenerife"))
number = st.sidebar.slider("Elige el rango en días entre los datos", 7, 21)
dia2 = datetime.datetime.now() - datetime.timedelta(days=number+i)
df2 = pd.read_csv(f'2021-{dia2.month:02d}-{dia2.day:02d}.csv', delimiter=';')
df = df.loc[df["Ciudad de destino"] == provincia]
df2 = df2.loc[df2["Ciudad de destino"] == provincia]
df["% var. precio"] = df["Precio"]
df2["% var. precio"] = df2["Precio"]
rang = st.sidebar.radio("Escoge un rango", ["Todo el verano","Mes","Día"])
if rang == "Mes":
    mes = st.sidebar.radio("Escoge un mes", ["Junio","Julio","Agosto"])
    if mes == "Junio":
        x = 6
        df = df.loc[df["Mes"]==6]
        df2 = df2.loc[df2["Mes"]==6]
    elif mes == "Julio":
        x = 7
        df = df.loc[df["Mes"]==7]
        df2 = df2.loc[df2["Mes"]==7]
    elif mes == "Agosto":
        x = 8
        df = df.loc[df["Mes"]==8]
        df2 = df2.loc[df2["Mes"]==8]
elif rang == "Día":
    date = st.sidebar.date_input("Selecciona una fecha",min_value=datetime.datetime(2021,6,1),
                                 max_value=datetime.datetime(2021,8,31), value=datetime.datetime(2021,6,1))
    x = [date.month, date.day]
    df = df.loc[df["Mes"]==x[0]]
    df2 = df2.loc[df2["Mes"]==x[0]]
    df = df.loc[df["Dia"]==x[1]]
    df2 = df2.loc[df2["Dia"]==x[1]]
else:
    x=0

st.sidebar.text("")
st.sidebar.markdown(f""" 
#### Newsletter
""")
email = st.sidebar.text_input(f"Recibe un email una vez a la semana con información relevante para {provincia}.",'ejemplo@mail.com')
a = st.sidebar.button("Suscribir")
usuario = st.secrets["usuario"]
contra = st.secrets["contra"]

if a:
    email1 = email.split("@")
    if email == "ejemplo@mail.com":
        st.sidebar.text("Introduce un email")
        a = False
    elif len(email1) == 2:
        email2 = email1[1].split(".")
        if len(email2) >= 2:
            enviar(email, provincia)
            st.sidebar.text("¡Suscripción creada con éxito!")
        else:
            a = False
            st.sidebar.text("Email incorrecto, intentelo de nuevo.")
    else:
        a = False
        st.sidebar.text("Email incorrecto, intentelo de nuevo.")

#Parte central

image = Image.open('logo.png')
st.image(image, width=300)
f"""
Comprueba como cambia los vuelos hacia tu ciudad y adelanta tu negocio al mercado. 
"""
st.text(f"Última actualización: 2021-{dia.month:02d}-{dia.day:02d}")
expander = st.beta_expander("Información sobre la web.")
expander.markdown("""
#### ¿Qué ofrecemos?
Nuestra web proporciona información amplia, fiable y actualizada aceeca de la afluencia de turistas internacionales a determinados aeropuertos españoles. De esta manera, ayudamos a pequeños y medianos negocios dependientes del turismo estival a tomar decisiones relevantes en función de estos análisis.
#### ¿Cómo se usa?
Ajustando los parámetros disponibles (ciudad y rango de tiempo en días, meses o todo el verano) recogidos en la pestaña desplegable lateral. Estos valores se pueden modificar en cualquier momento y el análisis correspondiente se muestra al instante.
#### ¿Cómo funciona?
Efectuando 7500 búsquedas diarias, usando la API de SkyScanner, recogemos la oferta de vuelos de distintas aerolíneas hacia los dos principales aeropuertos de la Comunidad Valenciana, Alicante y Valencia. También incluimos Tenerife puesto que en esa zona hay empresas interesadas.
Con los datos recogidos, efectuamos análisis y predicciones en tiempo real, ofreciendo así una idea exacta de la fluctuación de precio y cantidad de los vuelos.
""")

p = variacion(provincia,delta, "todos", rang, x,i)

st.code("🢀 Modifica los valores en el panel lateral para cambiar el rango de los datos.")

st.subheader(f"Número de plazas estimadas para {provincia}.*")
st.markdown(f"Número de plazas programadas por las aerolineas hacia {provincia}.")
st.line_chart(p[1],use_container_width=True)
st.markdown("**189 pasajeros por vuelo (capacidad media de un Boeing 737 o un a320).* ")

st.subheader(f"Número de plazas estimadas para {provincia} por país.*")
st.markdown(f"Número de plazas programadas por las aerolineas hacia {provincia} por país de origen.")
d = df.loc[df["Es directo"]==1]   
df_total = d.groupby("País origen")["Es directo"].sum()
df_verano = df.groupby(f"País origen")["Es directo"].count() * 189
selec = abs(df_verano) > 1
df_verano = df_verano[selec]
df_verano = df_verano[df_total.index]
df_verano = df_verano.rename("Nº de plazas")
st.bar_chart(df_verano, width=600, height=380)
st.markdown("**189 pasajeros por vuelo (capacidad media de un Boeing 737 o un a320).* ")


st.subheader(f"País de origen de las plazas.")
st.markdown(f"Diagrama de tartas con los paises de origen y el nº de plazas que representan.")
df = df.loc[df["Es directo"]==1]   
df2 = df2.loc[df2["Es directo"]==1] 
num = df.groupby("Ciudad de destino")["Es directo"].sum()
df_total = round((df.groupby("País origen")["Es directo"].sum()/num[provincia])*100,2)
df_total = df_total.rename("% de las plazas")
df_total = pd.DataFrame(df_total)
fig = px.pie(df_total, values="% de las plazas", names=df_total.index)
st.plotly_chart(fig,use_container_width=True)
  
st.subheader(f"Variación de nº de plazas por país de origen en los últimos {number} días.")
st.markdown(f"Aumento o disminución de plazas programadas por las aerolineas hacia {provincia} por país de origen.")
df_verano = (df.groupby("País origen")["Es directo"].sum() * 189)-(df2.groupby("País origen")["Es directo"].sum()*189)
selec = abs(df_verano) > 0.01
df_verano = df_verano[selec]
df_verano = df_verano.rename("""Nº de plazas""")
st.bar_chart(df_verano, use_container_width=True)


st.subheader(f"Precio medio en euros de las tarifas hacia {provincia}.")
st.markdown(f"Precio medio en euros de los vuelos hacia {provincia} para el el rango escogido.")
col1, col2 = st.beta_columns([1, 7])
col1.color_picker("""Semáforo de demanda*""",color(provincia, p[0]["Precio medio"][3]))
col1.color_picker("""Predicción del semáforo*""",color(provincia, p[0]["Predicción precio"][2]))
col2.line_chart(p[0],use_container_width=True)
st.markdown("""🔴 *(demanda baja)*; 🟡 *(demanda media)*; 🟢 *(demanda alta)*""")
st.markdown("**En función del precio medio de las tarifas indica el estado de la demanda.*")


st.subheader(f"Variación de tarifas por país de origen en los últimos {number} días.")
df_verano = round((df.groupby("País origen")["Precio"].mean()/df2.groupby("País origen")["Precio"].mean()-1)*100 ,2)
df_verano = df_verano.rename("% var precio")
selec = abs(df_verano) > 0.01
df_verano = df_verano[selec]
st.bar_chart(df_verano, use_container_width=True)


st.code("🢀 Modifica los valores en el panel lateral para cambiar el rango de los datos.")

"""
## Estudio por país de orgen.
Selecciona un país de la lista y obten los datos filtrados con las llegadas para el origen escogido.
"""
#("Reino Unido","Alemania", "Francia","Países Bajos","Bélgica")
mercado = st.selectbox("Elige un mercado",df_total.index)

try:
    p2 = variacion(provincia,delta, mercado, rang, x,i)
    st.subheader(f"Número de plazas estimadas para {provincia} provenientes de {mercado}.*")
    st.line_chart(p2[1],use_container_width=True)

    st.subheader(f"Precio medio para {provincia} con origen {mercado}.*")
    col1, col2 = st.beta_columns([1, 7])
    col1.color_picker("""Semáforo de demanda *""",color(provincia, p2[0]["Precio medio"][3]))
    col1.color_picker("""Predicción del semáforo *""",color(provincia, p2[0]["Predicción precio"][2])) #semaforo basado valores obtenidos de Google Flights
    col2.line_chart(p2[0],use_container_width=True)
    st.markdown("""🔴 *(demanda baja)*; 🟡 *(demanda media)*; 🟢 *(demanda alta)*""")
    st.markdown("**En función del precio medio de las tarifas indica el estado de la demanda.*")
except:
    st.code("No hay datos para esta selección, modifíquela.")
        

st.text("")
"""
## Sobre nosotros
SkyDemand es un proyecto desarrollado íntegramente por 
estudiantes del Grado de Ciencia de Datos de la Universidad Politécnica de Valencia.
Nuestro objetivo es proveer a pequeños y medianos negocios de una herramienta útil para 
analizar y predecir la afluencia de turistas, permitiéndoles 
así tomar decisiones relevantes como las fechas de apertura,los precios de sus productos, la
duración de los contratos o donde enfocar su publicidad.
"""
st.write("Todo nuestro código en [Github](https://github.com/yusef320/SkyDemand).")

image = Image.open('agradecimientos.png')
st.image(image)
