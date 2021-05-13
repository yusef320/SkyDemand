"""
Autores: Yusef Ahsini Ouariaghli, Pablo Díaz Masa Valencia
"""


import pandas as pd
import time
import requests
import datetime
from datetime import date
from github import Github
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from calendar import monthrange

################################################
####               FUNCIONES                ####
################################################

def newsletter(mercados, prov, d, d2,):
    d = d.loc[d["Ciudad de destino"] == prov]
    d2 = d2.loc[d2["Ciudad de destino"] == prov]
    plaztotal = d.groupby("Ciudad de destino")["Es directo"].count()*189
    plazas = d.groupby("País origen")["Es directo"].count()*189
    varPlazas = df_verano = round((d.groupby("País origen")["Es directo"].mean()/d2.groupby("País origen")["Es directo"].mean()-1)*100 ,2)
    texto = f"El número de plazas estimadas para {prov} es de {plaztotal[prov]}"
    precioMediototal = d.groupby("Ciudad de destino")["Precio"].mean()
    precioMedio = d.groupby("País origen")["Precio"].mean()
    varPrecio = df_verano = round((d.groupby("País origen")["Precio"].mean()/d2.groupby("País origen")["Precio"].mean()-1)*100 ,2)

    texto += f" y precio medio se situó en {round(precioMediototal[prov],2)}€.\n\nPor paises emisores la variación ha sido la siguiente:\n\n"
    for mercado in mercados:
        texto += f"\t{mercado}:  El número de plazas es {plazas[mercado]}, una variación del {varPlazas[mercado]}%  , una . El precio medio se situo en un {round(precioMedio[mercado],2)}€, lo que significa una diferencia del {varPrecio[mercado]}% en comparación a la semana pasada.\n\n"

    text = f"Buenas,\n\nSegún nuestros análisis, le informamos que durante la última semana el comportamiento ha sido el siguiente:\n\n{texto}Entra en https://tinyurl.com/skydemand para infomación más detallada.\n\nPara darse de baja enviar un email con el asunto: CANCELAR."

    return text

def enviarEmails(mails,texto,prov):
    text_type = "plain"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login('EMAIL',"CONTRASEÑA")
    for mail in mails:
        msg = MIMEText(texto, text_type, 'utf-8')
        msg['Subject'] = f"Info turística {prov}"
        msg['From'] = 'EMAIL'
        msg['To'] = mail
        server.send_message(msg)
    server.quit()

def emails():
    host = 'imap.gmail.com'
    username = 'USUARIO'
    password = 'CONTRASEÑA'

    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select("inbox")
    _, search_data = mail.search(None, 'ALL')   # con ALL mira todos los correos, con UNSEEN sólo los correos sin abrir y con SEEN los abiertos
    newslt_VLC = []
    newslt_ALC = []
    newslt_TCI = []
    for num in search_data[0].split():
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        palabras_asunto = email_message['subject'].split()   # estructura: ['Suscripcion', 'VLC', 'user@example.com']
        # print(palabras_asunto)
        if palabras_asunto[0] == 'Suscripcion':
            if palabras_asunto[1] == 'Valencia':
                newslt_VLC.append(palabras_asunto[2])   # se añade el correo
            elif palabras_asunto[1] == 'Alicante' :
                newslt_ALC.append(palabras_asunto[2])
            elif palabras_asunto[1] == 'Tenerife':
                newslt_TCI.append(palabras_asunto[2])

    return [newslt_VLC, newslt_ALC, newslt_TCI]

def subirArchivo(nombreArchivo):
    g = Github(login_or_token=('TOKEN GITHUB'))

    repo = g.get_user().get_repo('rep')
    all_files = []
    contents = repo.get_contents('')
    while contents:
        file_content = contents.pop(0)
        if file_content.type == 'dir':
            contents.extend(repo.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

    file = open(nombreArchivo, encoding="utf8")
    content = file.read()
    git_file = nombreArchivo
    if git_file in all_files:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, nombreArchivo, content, contents.sha, branch='main')
        print(git_file + ' UPDATED')
    else:
        repo.create_file(git_file, nombreArchivo, content, branch='main')
        print(git_file + ' CREATED')

def ciudad(d):
    if d == "TFS":
        return "Tenerife"
    if d == "VLC":
        return "Valencia"
    else: 
        return "Alicante"


def vuelosEnMes(anio, mes, orgien, destino, lista):
    """
    Devuelve una lista anidada con los vuelos que encuentra SkyScanner con el origen, mes y año introducido 
    con el siguiente [Fecha, Precio, Si es directo el vuelo (True or False), Aerolinea, Origen, Destino, Ciudad, Pais]
    
    Para la variable origen y destino introduce el código IATA en mayusculas de los perspectivos aeropuertos.
    
    No introducir una fecha pasada.
    
    La API tiene un limite de 50 búsquedas por minuto, cuando se supera devuelve:
    
    {'message': 'You have exceeded the rate limit per minute for your plan, BASIC, by the API provider'}
    
    Lista es una lista donde se añadiran los datos
    
    """
    j=0
    if destino == "ALC":
        j=1
    elif destino == "VLC" and orgien == "ZRH":
        j=1
    elif destino == "TFS" and orgien == "ZRH":
        j=1
    elif destino == "TFS" and orgien == "VIE":
        j=1
    elif destino == "TFS" and orgien == "TLS":
        j=1

    dia = datetime.datetime.now()
    m = dia.month
    d = dia.day
    var =1
    rang = monthrange(2021, mes)[1]
    if m > mes:
        return lista
    elif m == mes:
        rang = monthrange(2021, mes)[1]
        var = (date(2021, mes, rang) - date(2021, mes, d)).days

    for i in range(var,rang+1):
        vuelo= []
        url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/ES/EUR/es-ES/{orgien}-sky/{destino}-sky/{anio}-{mes:02d}-{i:02d}"
        headers = {
            'x-rapidapi-key': "API KEY",
            'x-rapidapi-host': "API HOST"
            }
        response = requests.request("GET", url, headers=headers)
        d = response.json()

        try:
            if len(d["Quotes"]) != 0:
                for p in range(0,len(d["Quotes"])):
                    #creamos una lista a la que vamos agregando los datos de las distintas busquedas
                    vuelo.append(f"2021-{mes:02d}-{i:02d}")
                    vuelo.append(mes)
                    vuelo.append(str(datetime.date.today()))
                    vuelo.append(d["Quotes"][p]["MinPrice"])
                    vuelo.append("€")
                    vuelo.append(d["Quotes"][p]["Direct"])
                    if len(d["Quotes"]) != len(d["Carriers"]): #Previene errores, aveces hay dos vuelos y una aerolínea
                        vuelo.append(d["Carriers"][0]["Name"])
                    else: 
                        vuelo.append(d["Carriers"][p]["Name"])
                    vuelo.append(orgien)
                    vuelo.append(destino)
                    vuelo.append(d["Places"][j]["CityName"])
                    vuelo.append(d["Places"][j]["CountryName"])
                    vuelo.append(ciudad(destino))
                    lista.append(vuelo)
                    vuelo= []
        except:
            print(d) #si por algún error el programa imprime en consola el motivo
            break
    return lista

################################################
####               PROGRAMA                 ####
################################################

starttime = time.time() #iniciamos el tiempo para nuestro bucle temporal
while True:
    today = date.today()
    print(today)
    lista = []
    orig = ["VLC", "TFS", "ALC"] #codigo IATA del aeropuerto de destino
    aeropuertos = ["FRA", "DUS", "BER", "MUC","HHN","LEJ","HAM","NRN","STR", "BRU", "CRL", "VIE", "CPH", "HEL","TLS","CDG","ORY","BVA",
                   "MRS","NCE","NTE","LYS","LUX","AMS","EIN","LHR","LTN", "LGW", "EDI","GLA","LPL","BHX","STN","MAN",
                   "NCL","BHD","BRS","PRG","ARN","ZRH","GVA","DUB","ORK","SNN","FCO","MXP","VCE"] #principales aeropuertos europeos
    for destino in orig: #recolcetamos los datos para cada provincia
        print(f"Recolectando datos de {destino}")
        for aeropueto in aeropuertos: #estudiamos todos los aeropuertos de la lista
            print(aeropueto)
            i = 6
            while True:
                vuelosEnMes(2021,i,aeropueto,destino, lista)
                i +=1
                time.sleep(60.0 - ((time.time() - starttime) % 60.0))
                if i >= 9: break

    print("Recolección de datos terminada")

    ####                Creamos un DataFrame con los datos de la lista                  ####

    df = pd.DataFrame(lista, columns=["Fecha", "Mes" ,"Fecha de busqueda", "Precio","Moneda","Es directo",
                                      "Aerolinea", "Origen", "Destino", "Ciudad origen", "País origen","Ciudad de destino"])
    def diaDelMes(fecha):
        fec = fecha.split("-")
        return fec[2]

    df["Dia"] = df["Fecha"].map(diaDelMes)
    df.to_csv (f"{today}.csv",sep=';', index=False, header=True)
    subirArchivo(f"{today}.csv")
    dia = datetime.datetime.now() - datetime.timedelta(days=7)
    if dia.today().weekday() == 5:
        try:
            df2 = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
            provincias=["Valencia", "Alicante", "Tenerife"]
            mercados=["Reino Unido", "Alemania", "Francia", "Bélgica","Países Bajos"]

            ####                Iniciando mail              #####

            i=0
            print("Enviando emails")
            mails = emails()
            for prov in provincias:
                info = newsletter(mercados,prov,df,df2)
                enviarEmails(mails[i],info,prov)
                i+=1
            print("Programa finalizado con exito")
        except:
            enviarEmails(["EMAIL DE EMERGENCIA"],"SE HA PRODUCIDO UN ERROR","ERROR")
            print("Error con los emails")

    time.sleep(86400.0 - ((time.time() - starttime) % 86400.0))
