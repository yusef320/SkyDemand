import streamlit as st
import pandas as pd
import datetime
import smtplib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from PIL import Image


#####           FUNCIONES               ####

@st.cache
def predicciónDem(fec, datos, oferta):
    """
    Modelo predictivo para la fluctucación de las tarifas aéreas.
    """
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop(["% Fluctuación precios"], axis=1)
    test = p["% Fluctuación precios"]
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=0.85, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    i=0
    for elemento in pred:
        if i >= 2: break
        demanda.append(round(elemento,2))
        i+=1
    demanda.append(p["% Fluctuación precios"][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.NaN)

    return pd.Series(data=demanda, index=fec, name="% Pred. fluctuación")

@st.cache
def predicciónVul(fec, datos, oferta):
    """
    Modelo predictivo para la fluctucación del número de vuelos.
    """
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop(["% Vuelos ofrecidos"], axis=1)
    test = p["% Vuelos ofrecidos"]
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=0.85, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    i=0
    for elemento in pred:
        if i >= 2: break
        demanda.append(round(elemento,2))
        i+=1
    demanda.append(p["% Vuelos ofrecidos"][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.NaN)

    return pd.Series(data=demanda, index=fec, name="% Pred. de vuelos ofrecidos")

@st.cache
def variacion(provincia,delta, mercado, rang, x,i):
    """
    Devuelve un dataframe con la variación de las tarifas
    y el número de vuelos asi como la predicción para ambas.
    """
    datos,fec,oferta  = [np.NaN,np.NaN], [], [np.NaN,np.NaN]
    if mercado == "todos":
        a = "Ciudad de destino"
        mercado = provincia
    else:
        a = "País origen"

    for z in range(1,3):
        dia = datetime.datetime.now() + datetime.timedelta(days=z-i)
        fecha = f"{dia.month:02d}-{dia.day:02d}"
        fec.append(fecha)

    d2 = pd.read_csv(f'2021-04-18.csv', delimiter=';')
    d2 = d2.loc[d2["Ciudad de destino"] == provincia]
    if rang == "Mes":
        d2 = d2.loc[d2["Mes"]==x]
    elif rang == "Día":
        d2 = d2.loc[d2["Mes"]==x[0]]
        d2 = d2.loc[d2["Dia"]==x[1]]

    for p in range(0, delta):
        dia = datetime.datetime.now() - datetime.timedelta(days=p+i)
        d = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
        d = d.loc[d["Ciudad de destino"] == provincia]
        if rang == "Mes":
            d = d.loc[d["Mes"]==x]
        elif rang == "Día":
            d = d.loc[d["Mes"]==x[0]]
            d = d.loc[d["Dia"]==x[1]]
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

    dat = pd.Series(data=datos, index=fec, name="% Fluctuación precios")
    var = pd.Series(data=oferta, index=fec, name="% Vuelos ofrecidos")
    pred1 = predicciónDem(fec, dat, var)
    pred2 = predicciónVul(fec, dat, var)
    p = pd.concat([dat, var, pred1, pred2], axis=1)
    return p

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


####                CUERPO DE LA PÁGINA                ####

#La configuramos

img = Image.open("logo.jpg")
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
    delta = dia - datetime.datetime(2021,4,18)
    delta = delta.days +1
except:
    dia = datetime.datetime.now() - datetime.timedelta(days=1) #dia de ayer
    df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    i=1
    delta = dia - datetime.datetime(2021,4,18)
    delta = delta.days +1

###
image = Image.open('logo.png')
st.image(image, width=300)
"""
Comprueba como cambia los vuelos hacia tu ciudad y adelanta tu negocio al mercado.
"""
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


provincia = st.sidebar.selectbox("Seleccione una ciudad",("Valencia", "Alicante", "Tenerife"))
number = st.sidebar.slider("Elige el rango en días entre los datos", 1, 14)
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
st.sidebar.text("")
expander = st.sidebar.beta_expander("Newsletter")
expander.markdown(""" 
Recibe un email cada vez que se produzca un 
cambio importante (de más del 5%) en los paises de origen de los turistas:
Reino Unido, Alemania o Francia.
""")
email = st.sidebar.text_input(f'Suscríbete a nuestro newsletter sobre {provincia}', 'ejemplo@mail.com')
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

st.subheader(f"Fluctuación del mercado para {provincia}.")
f"""La gráfica muestra el porcentaje de la variación de demanda de vuelos a {provincia} en función de la volatilidad de los precios. 
También estudia si la cantidad de vuelos programados a {provincia} cambia. Ofrece, además, una pequeña predicción futura basada en el 
comportamiento que han tenido los datos hasta el momento.
"""
st.text("")
p = variacion(provincia,delta, "todos", rang, x,i)
st.line_chart(p,use_container_width=True)

if number > 1:
    days = "días"
else:
    days = "día"
        

st.subheader("Variación por país de origen.")
f"""La gráfica muestra la variación del precio medio de los vuelos a {provincia} dependiendo del país de origen de los turistas. 
El porcentaje se corresponde con la variación del precio en {number} {days}."""
st.text("")
df_verano = round((df.groupby("País origen")["% var. precio"].mean()/df2.groupby("País origen")["% var. precio"].mean()-1)*100 ,2)
selec = abs(df_verano) > 0.2
df_verano = df_verano[selec]
st.bar_chart(df_verano, use_container_width=True)



"""
## Estudio por país de orgen.
Selecciona un país de la lista y obten los datos filtrados con las llegadas para el origen escogido.
"""
mercado = st.selectbox("Elige un mercado",("Reino Unido","Alemania", "Francia","Países Bajos","Bélgica"))
df = df.loc[df["País origen"]==mercado]
df2 = df2.loc[df2["País origen"]==mercado]

try:
    st.subheader(f"Fluctución del mercado procedentes {mercado}.")
    expander = st.beta_expander("Más información")
    expander.markdown(f"""La gráfica muestra el porcentaje de la variación de demanda de vuelos con origen {mercado} en función de la volatilidad de los precios. 
    También estudia si la cantidad de vuelos programados desde {mercado} hacia {provincia} cambia. Ofrece, además, una pequeña predicción futura basada en el 
    comportamiento que han tenido los datos hasta el momento.
    """)
    st.text("")
    p = variacion(provincia,delta, mercado, rang, x,i)
    st.line_chart(p,use_container_width=True)

    col1, col2 = st.beta_columns([5, 3])
    j = round((df.groupby("Ciudad origen")["% var. precio"].mean()/df2.groupby("Ciudad origen")["% var. precio"].mean()-1)*100,2)
    selec = abs(j) > 0.2
    j = j[selec]
    col1.subheader(f"Variación por ciudad de {mercado}.")
    if j.empty == False:
        expander = col1.beta_expander("Más información")
        expander.markdown(f"""La gráfica muestra la variación del precio medio de los vuelos provenientes de {mercado} segregados por ciudad de origen de los turistas. 
        El porcentaje se corresponde con la variación del precio en {number} {days}.""")
        col1.bar_chart(j, use_container_width=True)
        col2.subheader("")
        col2.text("")
        col2.table(j)
    else:
        st.code("No se ha producido ninguna variación por ciudad para esta seleción.")
except:
    st.code("No existen datos para esta selección, modifiquela para solucionarlo.")


"""
## Sobre nosotros

SkyDemand es un proyecto desarrollado
por estudiantes del grado de
Ciencia de Datos por la Universitat Politècnica de València
con el objetivo de ayudar a los pequeños negocios
dependientes del turismo a predecir 
cuando reabrir sus negocios o a 
adaptar sus productos a la demanda.

"""
st.write("Todo nuestro código en [Github](https://github.com/yusef320/SkyDemand)")

image = Image.open('agradecimientos.png')
st.image(image)
