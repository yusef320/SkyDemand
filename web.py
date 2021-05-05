import streamlit as st
import pandas as pd
import datetime
import smtplib

@st.cache
def variacion(provincia,delta, mercado, rang, x):
    if mercado == "todos":
        a = "Ciudad de destino"
        mercado = provincia
    else:
        a = "País origen"

    datos,fec,oferta  = [], [], []
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

    return fec, datos, oferta

st.set_page_config(layout="wide",page_title="touristData",initial_sidebar_state="expanded", ) #configuramos la página
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
# touristData
Estudia la demanda de turística de tu ciudad y adelanta tu negocio al mercado.
"""
st.text(f"ÚLTIMA ACTUALIZACIÓN 2021-{dia.month:02d}-{dia.day:02d}")
expander = st.beta_expander("Sobre nosotros")
expander.markdown("""
touristData es un proyecto desarrollado
por estudiantes del grado de
Ciencia de Datos por la Universitat Politècnica de València
para ayudar a los pequeños negocios
dependientes del turismo a predecir 
cuando reabrir sus negocios o a 
adaptar sus productos a la demanda.
Para usarlo, escoge tu ciudad y el periodo de tiempo que quieres analizar.
""")
"""
"""

provincia = st.sidebar.selectbox("Seleccione una ciudad",("Valencia", "Alicante", "Tenerife"))
number = st.sidebar.slider("Elige el rango en días entre los datos", 1, 10)
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
Mantente al día de la demanda de tu ciudad 
y recibe un email cada vez que se produzca un 
cambio importante en los principales mercados 
emisores: Reino Unido, Alemania o Francia.
""")
email = st.sidebar.text_input(f'Suscríbete a nuestro newsletter sobre {provincia}', 'ejemplo@mail.com')
a = st.sidebar.button("Suscribir")
usuario = 1
contra = 2

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

fec, datos, oferta = variacion(provincia,delta, "todos", rang, x)
st.subheader(f"Variación de la demanda para {provincia}.")
expander = st.beta_expander("Más información")
expander.markdown("Muestra el comportamiento del mercado en función de las reservas realizadas y los algoritmos de las aerolíneas, y también el número de vuelos ofrecidos.")
st.text("")
dat = pd.Series(data=datos, index=fec, name="Demanda")
var = pd.Series(data=oferta, index=fec, name="Vuelos ofrecidos")
p = pd.concat([dat, var], axis=1)
st.line_chart(p,use_container_width=True)



st.subheader("Variacion de demanda por mercado emisor.")
expander = st.beta_expander("Más información")
expander.markdown(f"Muestra el comportamiento del mercado para {provincia} por cada uno de los principales paises emisores de turistas.")
st.text("")
df_verano = (df.groupby("País origen")["Var"].mean()/df2.groupby("País origen")["Var"].mean()-1)*100
st.bar_chart(df_verano, use_container_width=True)


"""
## Estudio por mercado
Escoge el mercado que más te interesa o todos y estudia como fluctua la demanda.
"""
mercado = st.selectbox("Elige un mercado",("Reino Unido","Alemania", "Francia"))
df = df.loc[df["País origen"]==mercado]
df2 = df2.loc[df2["País origen"]==mercado]

fec, datos, oferta = variacion(provincia,delta, mercado, rang, x)
st.subheader(f"Variación de la demanda de {mercado}.")
expander = st.beta_expander("¿Qué significa?")
st.text("")
expander.markdown(f"Muestra el comportamiento del mercado para los vuelos procedentes de {mercado}.")
dat = pd.Series(data=datos, index=fec, name="Demanda")
var = pd.Series(data=oferta, index=fec, name="Vuelos ofrecidos")
p = pd.concat([dat, var], axis=1)
st.line_chart(p,use_container_width=True)


col1, col2 = st.beta_columns([5, 3])
j = (df.groupby("Ciudad origen")["Var"].mean()/df2.groupby("Ciudad origen")["Var"].mean()-1)*100
col1.subheader("Demanda por ciudad")
col1.markdown("Muestra la variación de demanda por ciudad.")
col1.bar_chart(j, use_container_width=True)
col2.subheader("")
col2.text("")
col2.write(j)
