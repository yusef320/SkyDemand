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
from email.mime.text import MIMEText
import random


############################################
#####           FUNCIONES               ####
############################################

@st.cache_data
def predicción(fec, datos, oferta, dato):
    """
    Modelo predictivo.
    """
    p = pd.concat([datos, oferta], axis=1)
    p = p.dropna(axis=0, how="any")
    demanda = []
    train = p.drop([dato], axis=1)
    test = p[dato]
    
    s=0.85
    X_train, X_test, Y_train, Y_test = train_test_split(train, test, test_size=s, random_state=1)
    regr = LinearRegression()
    regr.fit(X_train, Y_train)
    pred = regr.predict(X_train)
    n = round(regr.score(X_train, Y_train),2)
    #Genera correctamente un modelo de regresión lineal pero esta mal utilizado por la función  
    i=0
    for elemento in pred:
        if i >= 4: break
        demanda.append(round(elemento,0))
        i+=1
    demanda.append(p[dato][0])
    dist = len(fec)-len(demanda)

    for i in range(dist):
        demanda.append(np.nan)

    if dato == "Nº de plazas":
        name = "Pred. nº de plazas"
    else:
        name = "Predicción precio"

    return pd.Series(data=demanda, index=fec, name=name),n

@st.cache_data
def variacion(provincia,delta, mercado, rang, x,i):
    """
    Devuelve un dataframe con la variación de las tarifas
    y el número de vuelos asi como la predicción para ambas.
    """
    datos, fec, oferta = [np.nan, np.nan, np.nan, np.nan], [], [np.nan, np.nan, np.nan, np.nan]
    if mercado == "todos":
        a = "Ciudad de destino"
        mercado = provincia
    else:
        a = "País origen"

    for z in range(1,5):
        dia = datetime.datetime(2021,6,29) + datetime.timedelta(days=z-i)
        fecha = datetime.date(2021, dia.month, dia.day)
        fec.append(fecha)

    for p in range(0, delta):
        dia = datetime.datetime(2021,6,29) - datetime.timedelta(days=p+i)
        d = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
        d = d.loc[d["Mes"]!=6]
        d = d.loc[d["Ciudad de destino"] == provincia]
        if rang == "Mes":
            d = d.loc[d["Mes"]==x]
        elif rang == "Día":
            d = d.loc[d["Mes"]==x[0]]
            d = d.loc[d["Dia"]==x[1]]
        df_demanda = d.groupby(a)["Es directo"].count()*189
        d = d.loc[d["Es directo"]==1]
        df_verano = d.groupby(a)["Precio"].mean()
        val_precio = df_verano.get(mercado, np.nan)
        if pd.notna(val_precio):
            val_precio = round(val_precio, 2)
        datos.append(val_precio)
        fecha = datetime.date(2021, dia.month, dia.day)
        fec.append(fecha)
        val_oferta = df_demanda.get(mercado, np.nan)
        if pd.notna(val_oferta):
            val_oferta = round(val_oferta, 2)
        oferta.append(val_oferta)

    dat = pd.Series(data=datos, index=fec, name="Precio medio")
    var = pd.Series(data=oferta, index=fec, name="Nº de plazas")
    pred1,n = predicción(fec, dat, var,"Precio medio")
    pred2,n1 = predicción(fec, dat, var, "Nº de plazas")
    p = pd.concat([dat, pred1], axis=1)
    v = pd.concat([var, pred2], axis=1)
    return [p,v,n,n1]

def enviar(email, provincia):
    """
    Suscribe a los emails en el newsletter
    """
    text_type = "plain"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(usuario,contra)
    texto = f"Le damos la bienvenida al newsletter de SkyDemand sobre {provincia}. Cada viernes recibirá un email con un resumen semanal de con datos relevantes como el precio, el bnúmero de plazas, y su fluctuación.\n\nUn saludo,\n\nel equipo de SkyDemand."
    msg = MIMEText(texto, text_type, 'utf-8')
    msg['Subject'] = "Bienvenido"
    msg['From'] = usuario
    msg['To'] = email
    server.sendmail(usuario,usuario,f"Subject:Suscripcion {provincia} {email}")
    server.send_message(msg)
    server.quit()
    
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
dia = datetime.datetime(2021,6,29) #Día de hoy
df = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
i=0


###########################################################
####                CUERPO DE LA PÁGINA                ####
###########################################################

# Barra lateral
with st.sidebar:
    st.text("")
    st.text("")
    provincia = st.selectbox("Seleccione una ciudad", ("Valencia", "Alicante", "Tenerife", "Mallorca"))
    number = st.slider("Elija el rango en días entre los datos", 7, 21)
    dia2 = datetime.datetime(2021, 6, 29) - datetime.timedelta(days=number + i)
    df2 = pd.read_csv(f'2021-{dia2.month:02d}-{dia2.day:02d}.csv', delimiter=';')
    df = df.loc[df["Ciudad de destino"] == provincia]
    df2 = df2.loc[df2["Ciudad de destino"] == provincia]
    df["% var. precio"] = df["Precio"]
    df2["% var. precio"] = df2["Precio"]

    rang = st.radio("Escoja un rango", ["Todo el verano", "Mes", "Día"])
    if rang == "Mes":
        mes = st.radio("Escoja un mes", ["Julio", "Agosto"])
        rango = f"el mes de {mes}"
        if mes == "Junio":
            x = 6
            df = df.loc[df["Mes"] == 6]
            df2 = df2.loc[df2["Mes"] == 6]
        elif mes == "Julio":
            x = 7
            df = df.loc[df["Mes"] == 7]
            df2 = df2.loc[df2["Mes"] == 7]
        elif mes == "Agosto":
            x = 8
            df = df.loc[df["Mes"] == 8]
            df2 = df2.loc[df2["Mes"] == 8]
    elif rang == "Día":
        date = st.date_input(
            "Seleccione una fecha",
            min_value=datetime.datetime(2021, 7, 1),
            max_value=datetime.datetime(2021, 8, 31),
            value=datetime.datetime(2021, 7, 1),
        )
        x = [date.month, date.day]
        rango = f"el {x[1]}/{x[0]}/2021"
        df = df.loc[df["Mes"] == x[0]]
        df2 = df2.loc[df2["Mes"] == x[0]]
        df = df.loc[df["Dia"] == x[1]]
        df2 = df2.loc[df2["Dia"] == x[1]]
    else:
        df = df.loc[df["Mes"] != 6]
        df2 = df2.loc[df2["Mes"] != 6]
        x = 0
        rango = "todo el verano (julio y agosto)"

    if provincia == "Mallorca":
        delta = dia - datetime.datetime(2021, 5, 15)
        delta = delta.days + 1
    else:
        delta = dia - datetime.datetime(2021, 4, 18)
        delta = delta.days + 1

    st.text("")
    st.markdown("#### Newsletter")
    email = st.text_input(
        f"Reciba un email una vez a la semana con información relevante para {provincia}.",
        "ejemplo@mail.com",
    )
    suscribirme = st.button("Suscribirme")
    usuario = st.secrets["usuario"]
    contra = st.secrets["contra"]

    if suscribirme:
        email1 = email.split("@")
        if email == "ejemplo@mail.com":
            st.error("Escriba su email")
        elif len(email1) == 2:
            email2 = email1[1].split(".")
            if len(email2) >= 2:
                enviar(email, provincia)
                st.success("¡Ya se ha suscrito!")
            else:
                st.error("Email incorrecto, inténtelo de nuevo.")
        else:
            st.error("Email incorrecto, inténtelo de nuevo.")

#Parte central

image = Image.open('logo.png')
st.image(image, width=300)
st.write("Descubre cómo cambia la oferta de vuelos hacia tu ciudad y adelanta tu negocio al mercado.")
st.text(f"Última actualización: 2021-{dia.month:02d}-{dia.day:02d}")
if provincia in ["Alicante","Tenerife","Valencia","Mallorca"]:
    expander = st.expander("Información sobre la web", True)
    expander.markdown("""
    #### Nuestra misión
    SkyDemand proporciona información fiable y actualizada acerca de la afluencia prevista de turistas extranjeros a determinados aeropuertos españoles.


    Nuestra misión es ayudar a pequeños y medianos negocios dependientes del turismo internacional a tomar decisiones relevantes sobre la planificación y promoción de la
    temporada en función de estos datos. Entre estas decisiones incluimos **fijar fechas de apertura, diseñar campañas de promoción, establecer tarifas o
    estimar la duración de los contratos de la plantilla y de los suministros**.


    #### ¿En qué se basa?
    La oferta de vuelos por las aerolíneas cambia diariamente ajustándose a la demanda existente. 
    Usando la API de SkyScanner efectuamos **8000 búsquedas diarias**, recogiendo así la oferta de vuelos desde
    los principales países de origen (**Reino Unido, Alemania, Francia, Bélgica, Países Bajos, República Checa, Suecia, Finlandia, Italia, Dinamarca, Suiza y Luxemburgo**) 
    hacia los dos principales aeropuertos de la Comunitat Valenciana (**Alicante** y **Valencia**).
    También incluimos **Tenerife** y, próximamente, **Mallorca**, puesto que son zonas donde hemos detectado un gran número de empresas potencialmente interesadas.


    Con los datos recogidos, mostramos **análisis y predicciones en tiempo real**, ofreciendo así una idea exacta de la fluctuación de **precio y cantidad de los vuelos**. 
    Además, para facilitar que puedas ocuparte de tu negocio, te puedes suscribir a nuestra **newsletter** para recibir alertas de los cambios más significativos 
    en la demanda.


    #### ¿Cómo se usa?
    En la barra lateral debes ajustar los parámetros disponibles *ciudad* y *rango temporal* (días, meses o todo el verano). Estos valores se pueden modificar en cualquier momento y el análisis correspondiente se muestra al instante.
    
    #### ¿Para que me sirve?
    Una de las potenciales forma de usar SkyDemand es para **adaptar los productos que ofrece** tu empresa al mercado. 
    Puediendo **cambiar tus precios** en función del precio medio de los vuelos, **contratando más personal** si el número de plazas ofrecidas 
    aumenta considerablemte o **plantear tu presencia online y campañas publicitarias** a los países con plazas programadas. 
    """)
    
    expander.video("https://youtu.be/c4j9xQrSOG8")
    expander.text("")
    expander.markdown("**Recuerda modifica los valores en el panel lateral para cambiar el rango de los datos.**")
    
 
    p = variacion(provincia, delta, "todos", rang, x, i)
    d = df.loc[df["Es directo"] == 1]
    df_total = d.groupby("País origen")["Es directo"].sum()
    df_verano = df.groupby("País origen")["Es directo"].count() * 189
    selec = abs(df_verano) > 1
    df_verano = df_verano[selec]
    df_verano = df_verano[df_total.index]
    df_verano = df_verano.rename("Nº de plazas")
    tabs = st.tabs(["Análisis general", "Por país de origen"])

    with tabs[0]:
        st.subheader(f"Número de plazas programadas por las aerolíneas para {provincia} para {rango}.")
        st.markdown(
            f"""Muestra la estimación diaria del **número de plazas** programadas en vuelos con destino {provincia} para el período elegido.
        Dicha estimación se obtiene considerando que, en promedio, cada vuelo tiene una capacidad de 189 personas*."""
        )
        st.line_chart(p[1], use_container_width=True)
        st.markdown("**capacidad media de un Boeing 737 o Airbus A320.* ")

        st.subheader(f"Número de plazas programadas para {provincia} por país de origen.")
        st.markdown(
            f"""Muestra la estimación diaria del **número de plazas** en vuelos programados con destino {provincia} segmentada por los distintos países de origen de las rutas para {rango}."""
        )
        st.bar_chart(df_verano, width=600, height=380)

        st.subheader("Porcentaje que representa cada país del total de operaciones.")
        st.markdown(
            f"Gráfico circular con los **países de origen** y el **porcentaje** del total de operaciones que representa para {rango}."
        )
        df_share = round((df_verano / df_verano.sum()) * 100, 2)
        df_share = df_share.rename("% de las plazas")
        df_share = pd.DataFrame(df_share)
        fig = px.pie(df_share, values="% de las plazas", names=df_share.index)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Variación de número de plazas por país de origen en los últimos {number} días.")
        st.markdown(
            f"Muestra como varía el **número de plazas** en vuelos programados con destino {provincia} por país de origen en los últimos {number} días para {rango}."
        )
        df_var = (df.groupby("País origen")["Es directo"].sum() * 189) - (
            df2.groupby("País origen")["Es directo"].sum() * 189
        )
        selec = abs(df_var) > 0.01
        df_var = df_var[selec]
        df_var = df_var.rename("Nº de plazas")
        st.bar_chart(df_var, use_container_width=True)

        st.subheader(f"Precio medio en euros de las tarifas hacia {provincia} para {rango}.")
        st.markdown(
            f"Muestra el comportamiento del **precio medio** de todos los vuelos hacia {provincia} en el rango escogido. En función de dicho precio se genera una estimación de la demanda, basándonos en años anteriores, que se muestra en forma de **semáforo**."
        )
        col1, col2 = st.columns([1, 7])
        col1.color_picker("Semáforo de demanda*", color(provincia, p[0]["Precio medio"][3]))
        col1.color_picker("Predicción del semáforo*", color(provincia, p[0]["Predicción precio"][2]))
        col2.line_chart(p[0], use_container_width=True)
        st.markdown("🔴 *demanda baja*; 🟡 *demanda media*; 🟢 *demanda alta*")
        st.markdown("**Indica el estado de la demanda en función del precio medio de las tarifas.*")

        st.subheader(f"Variación de tarifas por país de origen en los últimos {number} días.")
        st.markdown(
            f"Muestra el comportamiento del **precio medio** de los vuelos hacia {provincia} **por país** en los últimos {number} días para {rango}."
        )
        df_price = round(
            (df.groupby("País origen")["Precio"].mean() / df2.groupby("País origen")["Precio"].mean() - 1) * 100,
            2,
        )
        df_price = df_price.rename("% var precio")
        selec = abs(df_price) > 0.01
        df_price = df_price[selec]
        st.bar_chart(df_price, use_container_width=True)

    with tabs[1]:
        st.markdown(
            """
        ## Estudio por país de origen.
        Selecciona un país de la lista y obtén los datos filtrados con las llegadas desde el país escogido.
        """
        )
        mercado = st.selectbox("Elige un mercado", df_total.index)
        try:
            p2 = variacion(provincia, delta, mercado, rang, x, i)
            st.subheader(
                f"Número de plazas en vuelos programados por las aerolíneas hacia {provincia} con origen {mercado} para {rango}."
            )
            st.markdown(
                f"""Muestra la estimación diaria del **número de plazas** en vuelos programados con destino {provincia} provenientes de {mercado} para el período elegido.
        Dicha estimación se obtiene considerando que, en promedio, cada vuelo tiene una capacidad de 189 personas*."""
            )
            st.line_chart(p2[1], use_container_width=True)
            st.markdown("**capacidad media de un Boeing 737 o Airbus A320.* ")

            st.subheader(
                f"Precio medio en euros de los precios de los vuelos hacia {provincia} con origen {mercado} para {rango}."
            )
            st.markdown(
                f"Muestra el comportamiento del **precio medio** para todos los vuelos en el rango escogido hacia {provincia} que provienen de {mercado}. En función de dicho precio se genera una estimación de la demanda, basándonos en años anteriores, que se muestra en **forma de semáforo**."
            )

            col1, col2 = st.columns([1, 7])
            col1.color_picker("Semáforo de demanda *", color(provincia, p2[0]["Precio medio"][3]))
            col1.color_picker("Predicción del semáforo *", color(provincia, p2[0]["Predicción precio"][2]))
            col2.line_chart(p2[0], use_container_width=True)
            st.markdown("🔴 *demanda baja*; 🟡 *demanda media*; 🟢 *demanda alta*")
            st.markdown("**Indica el estado de la demanda en función del precio medio de las tarifas.*")

        except:
            st.code("No hay disponibles análisis para esta selección. Por favor, modifíquela.")

  

else:
    st.text("")
    st.code("Próximamente estarán disponibles los análisis para esta selección.")


st.text("")
"""
## Sobre nosotros
SkyDemand es un proyecto desarrollado íntegramente por estudiantes de la Universidad Politécnica de Valencia, del grado de Ciencia de Datos y que se encuadra en el marco de la asignatura Proyecto I.
Nuestro objetivo es proveer a pequeños y medianos negocios de una herramienta útil para analizar y predecir la afluencia de turistas, permitiéndoles así tomar decisiones relevantes como las fechas de apertura, los precios, la duración de los contratos o la correcta colocación de publicidad.
"""
st.write("Síguenos en Twitter [@skydemand](https://twitter.com/skydemand).\nTodo nuestro código en [Github](https://github.com/yusef320/SkyDemand) ;)")


image = Image.open('agradecimientos.png')
st.image(image)

