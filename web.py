import streamlit as st
import pandas as pd
import datetime
import smtplib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from PIL import Image 

def predicciónDem(fec, datos, oferta):
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop(["Demanda"], axis=1)
    test = p["Demanda"]
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=0.9, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    for elemento in pred:
        demanda.append(round(elemento,2))
    demanda.append(p["Demanda"][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.NaN)

    return pd.Series(data=demanda, index=fec, name="Pred. Demanda")

def predicciónVul(fec, datos, oferta):
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop(["Vuelos ofrecidos"], axis=1)
    test = p["Vuelos ofrecidos"]
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=0.9, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    for elemento in pred:
        demanda.append(round(elemento,2))
    demanda.append(p["Vuelos ofrecidos"][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.NaN)

    return pd.Series(data=demanda, index=fec, name="Pred. vuelos ofre.")

@st.cache
def variacion(provincia,delta, mercado, rang, x,i):
    datos,fec,oferta  = [np.NaN,np.NaN,np.NaN], [], [np.NaN,np.NaN,np.NaN]
    if mercado == "todos":
        a = "Ciudad de destino"
        mercado = provincia
    else:
        a = "País origen"
        
    for z in range(1,5):
        dia = datetime.datetime.now() + datetime.timedelta(days=z-i)
        fecha = f"{dia.month:02d}-{dia.day:02d}"
        fec.append(fecha)

    d2 = pd.read_csv(f'2021-04-18.csv', delimiter=';')
    d2 = d2.loc[d2["Ciudad de destino"] == provincia]
    if rang == "Mes": d2 = d2.loc[d2["Mes"]==x]
    for p in range(0, delta):
        dia = datetime.datetime.now() - datetime.timedelta(days=p+i)
        d = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
        d = d.loc[d["Ciudad de destino"] == provincia]
        if rang == "Mes": d = d.loc[d["Mes"]==x]
        df_verano = (d.groupby(a)["Precio"].mean()/d2.groupby(a)["Precio"].mean()-1)*100
        d = d.loc[d["Es directo"]==1]
        d2c = d2.loc[d2["Es directo"]==1]
        df_demanda = (d.groupby(a)["Es directo"].sum()/d2c.groupby(a)["Es directo"].sum()-1)*100
        s= round(df_verano[mercado],2)
        datos.append(s)
        fecha = f"{dia.month:02d}-{dia.day:02d}"
        fec.append(fecha)
        o= round(df_demanda[mercado],2)
        oferta.append(o)

    dat = pd.Series(data=datos, index=fec, name="Demanda")
    var = pd.Series(data=oferta, index=fec, name="Vuelos ofrecidos")
    pred1 = predicciónDem(fec, dat, var)
    pred2 = predicciónVul(fec, dat, var)
    p = pd.concat([dat, var, pred1, pred2], axis=1)

    return p

img = Image.open("logo.jpg")
st.set_page_config(layout="wide",page_title="SkyDemand",page_icon=img,initial_sidebar_state="expanded", ) #configuramos la página
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style,unsafe_allow_html=True)


try:
    dia = datetime.datetime.now() #dia de ayer
    df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    i=0
    delta = dia - datetime.datetime(2021,4,18)
    delta = delta.days +1
except:
    dia = datetime.datetime.now() - datetime.timedelta(days=1) #dia de ayer
    df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    i=1
    delta = dia - datetime.datetime(2021,4,18)
    delta = delta.days +1

"""
# SkyDemand
Comprueba como cambia los vuelos hacia tu ciudad y adelanta tu negocio al mercado.
"""
expander = st.beta_expander("¿Qué solucionamos?")
expander.markdown("""

COMPLETAR

#### ¿Cómo usarlo?

Simplemnte escoge la ciudad que quieras estudiar en el panel lateral, un rango de días 
para los gráficos de barra y un perido de tiempo (junio, julio, agosto o todo el verano).
Tambíen puedes ir modificando estos parámetros más adelante.

#### ¿Cómo funciona?

Comprobamos la fluctuación de los mercados a diario realizando más de 7500 búsquedas en 
en los vuelos que ofrecen las distintas aerolíneas hacia las dos principales vias de entrada para turistas internacionales de la Comunitat Valenciana, los aeropuertos 
de Alicante y Valencia. Con los datos representamos como fluctua la variación de los precios y cantidad de vuelos que ofrecen las aerolineas.
""")


st.markdown(f"ÚLTIMA ACTUALIZACIÓN 2021-{dia.month:02d}-{dia.day:02d}")
provincia = st.sidebar.selectbox("Seleccione una ciudad",("Valencia", "Alicante", "Tenerife"))
number = st.sidebar.slider("Elige el rango en días entre los datos", 1, 14)
dia2 = datetime.datetime.now() - datetime.timedelta(days=number+i)
df2 = pd.read_csv(f'2021-{dia2.month:02d}-{dia2.day:02d}.csv', delimiter=';')


df = df.loc[df["Ciudad de destino"] == provincia]
df2 = df2.loc[df2["Ciudad de destino"] == provincia]
df["Var"] = df["Precio"]
df2["Var"] = df2["Precio"]

rang = st.sidebar.radio("Escoge un rango", ["Todo el verano","Mes"])
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
else:
    x=0

st.sidebar.text("")
st.sidebar.text("")
expander = st.sidebar.beta_expander("Newsletter")
expander.markdown(""" 
Recibe un email cada vez que se produzca un 
cambio importante (de más del 5%) en los principales mercados 
emisores: Reino Unido, Alemania o Francia.
""")
email = st.sidebar.text_input(f'Suscríbete a nuestro newsletter sobre {provincia}', 'ejemplo@mail.com')
a = st.sidebar.button("Suscribir")
usuario = st.secrets["usuario"]
contra = st.secrets["contra"]

def enviar(email, provincia):
    conn = smtplib.SMTP("smtp.gmail.com", 587)
    conn.ehlo()
    conn.starttls()
    conn.login(usuario,contra)
    conn.sendmail(usuario,usuario,f"Subject:Suscripcion {provincia} {email}")
    conn.sendmail(usuario,email,f"Subject:Bienvenido \n\nLe damos la bienvenida al newsletter de tourisData sobre {provincia}. Cada vez que se produzca un cambio importante en la demanda le enviaremos un informe semanal sobre como ha evolucionado el mercado.\n\nUn saludo,\n\nel equipo de touristData.")
    conn.quit()

if a:
    email1 = email.split("@")
    email2 = email1[1]
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

st.subheader(f"Variación de la llegada de turistas para {provincia}.")
expander = st.beta_expander("Más información")
expander.markdown(f"""La siguiente gráfica muestra el porcentaje de variación de la demanda en función de la volatilidad de los precios y si 
la cantidad de vuelos que se ofrece hacia {provincia} cambia (el dato base corresponde al día 18 de abril). Tambíen se ofrece una pequeña predicción futura basada
en el comportamiento que ha tenido hasta el momento.
""")
st.text("")
p = variacion(provincia,delta, "todos", rang, x,i)
st.line_chart(p,use_container_width=True)


st.subheader("Variación llegada de turistas por país de origen.")
expander = st.beta_expander("Más información")
expander.markdown(f"Muestra el comportamiento del mercado para {provincia} por cada uno de los principales paises emisores de turistas. El porcentaje es como ha variado en {number} día/s.")
st.text("")
df_verano = (df.groupby("País origen")["Var"].mean()/df2.groupby("País origen")["Var"].mean()-1)*100
st.bar_chart(df_verano, use_container_width=True)


"""
## Estudio por país de orgen.
Selecciona un país de la lista y obten los datos filtrados con las llegadas para el origen escogido.
"""
mercado = st.selectbox("Elige un mercado",("Reino Unido","Alemania", "Francia"))
df = df.loc[df["País origen"]==mercado]
df2 = df2.loc[df2["País origen"]==mercado]

st.subheader(f"Variación llegada de turistas procedentes {mercado}.")
expander = st.beta_expander("Más información")
expander.markdown(f"""La siguiente gráfica muestra el porcentaje de variación de la demanda en función de la volatilidad de los precios y si 
la cantidad de vuelos que se ofrece desde {mercado} hacia {provincia} cambia (el dato base corresponde al día 18 de abril). Tambíen se ofrece una pequeña predicción futura basada
en el comportamiento que ha tenido hasta el momento.""")
st.text("")
p = variacion(provincia,delta, mercado, rang, x,i)
st.line_chart(p,use_container_width=True)


col1, col2 = st.beta_columns([5, 3])
j = (df.groupby("Ciudad origen")["Var"].mean()/df2.groupby("Ciudad origen")["Var"].mean()-1)*100
col1.subheader(f"Variación llegada de turistas por ciudad de {mercado}")
expander = col1.beta_expander("Más información")
expander.markdown("(Varia en función de los rango de dias y el mes escogido)")
col1.bar_chart(j, use_container_width=True)
col2.subheader("")
col2.text("")
col2.dataframe(j, 400, 700)

expander = st.beta_expander("Sobre nosotros")
expander.markdown("""
touristData es un proyecto desarrollado
por estudiantes del grado de
Ciencia de Datos por la Universitat Politècnica de València
con el objetivo de ayudar a los pequeños negocios
dependientes del turismo a predecir 
cuando reabrir sus negocios o a 
adaptar sus productos a la demanda.
""")
