"""
Autor: Yusef Ahsini Ouariaghli
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

def semanaInfo(mercados, prov):
    """
    
    Crea un informe de la variación diaria durante la última semana.
    
    """
    text = ""
    texto = ""
    for mercado in mercados:
        text = ""
        for i in range(1,8):
            dia = datetime.datetime.now() - datetime.timedelta(days=i-1)
            dia2 = datetime.datetime.now() - datetime.timedelta(days=i)
            d = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
            d2 = pd.read_csv(f'2021-{dia2.month:02d}-{dia2.day:02d}.csv', delimiter=';')
            d = d.loc[d["Ciudad de destino"] == prov]
            d2 = d2.loc[d2["Ciudad de destino"] == prov]
            df_verano = (d.groupby("País origen")["Precio"].mean()/d2.groupby("País origen")["Precio"].mean()-1)*100
            s= round(df_verano[mercado],2)
            text += f"\t{dia.day:02d}/{dia.month:02d}  {s}% \n"
            dia = dia2
        texto += f"{mercado} (en la ultima semana):\n\n"
        texto += text+"\n\n"
    return texto

def emails():
    """
    
    Recolecta los emails suscritos al newsletter.
    
    """
    
    host = 'TU HOST'
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
    g = Github(login_or_token=('TOKEN DE GITHUB'))

    repo = g.get_user().get_repo('NOMBRE DEL REPOSITORIO')
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

    for i in range(1,32):
        if i == 31 and mes == 6: break
        vuelo= []
        url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/ES/EUR/es-ES/{orgien}-sky/{destino}-sky/{anio}-{mes:02d}-{i:02d}"
        headers = {
            'x-rapidapi-key': "KEY DE LA API SKYSCANNER",
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
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

starttime = time.time() #iniciamos el tiempo para nuestro bucle temporal
while True:
    today = date.today()
    print(today)
    lista = []
    orig = ["VLC", "TFS", "ALC"] #codigo IATA del aeropuerto de destino
    aeropuertos = ["FRA", "DUS", "BER", "MUC", "HAM","NRN","STR", "BRU", "CRL", "VIE", "CPH", "HEL","TLS","CDG","ORY","BVA",
                   "MRS","NCE","NTE","LYS","LUX","AMS","EIN","LHR","LTN", "LGW", "EDI","GLA","LPL","BHX","STN","MAN",
                   "NCL","BHD","BRS","PRG","ARN","ZRH","GVA"] #principales aeropuertos europeos
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

    #creamos un DataFrame con los datos de la lista

    df = pd.DataFrame(lista, columns=["Fecha", "Mes" ,"Fecha de busqueda", "Precio","Moneda","Es directo",
                                      "Aerolinea", "Origen", "Destino", "Ciudad origen", "País origen","Ciudad de destino"])
    def diaDelMes(fecha):
        fec = fecha.split("-")
        return fec[2]

    df["Dia"] = df["Fecha"].map(diaDelMes)
    df.to_csv (f"{today}.csv",sep=';', index=False, header=True)
    subirArchivo(f"{today}.csv") #subimos el archivo a nuestro repositorio de github 
    
    #Comparamos los datos para ver si se ha producido una variación importante
    
    dia = datetime.datetime.now() - datetime.timedelta(days=1)
    df2 = pd.read_csv(f'2021-{dia.month:02d}-{dia.day:02d}.csv', delimiter=';')
    var = {}
    print("Analizando variación")
    provincias=["Valencia", "Alicante", "Tenerife"]
    for prov in provincias:
        print(prov)
        listaDem = []
        d = df.loc[df["Ciudad de destino"] == prov]
        d2 = df2.loc[df2["Ciudad de destino"] == prov]
        for mercado in ["Reino Unido", "Alemania","Francia",]:
            df_verano = (d.groupby("País origen")["Precio"].mean()/d2.groupby("País origen")["Precio"].mean()-1)*100
            s = round(df_verano[mercado],2)
            print(mercado, s)
            if s > 5 or s < -5: #La variación tiene que ser superior al 5% para enviar un informe
                listaDem.append(mercado)
        var[prov] = listaDem # diccionario con todos los mercados en lo que hay variación

    #enviamos los emails en caso de que se produzca una variación    
    listaMails = emails()
    conn = smtplib.SMTP("HOST", 587)
    conn.ehlo()
    conn.starttls()
    conn.login("USUARIO","CONTRASEÑA")
    i=0
    print("Enviando emails")
    for prov in provincias:
        if var[prov] != []:
            info = semanaInfo(var[prov],prov)
            for email in listaMails[i]:
                conn.sendmail("USUARIO",email,f"Subject:Demanda turistica {prov}\n\nSaludos cordiales,\n\nSegun nuestro ultimo analisis, le informamos de la variacion en la demanda turistica producida en los siguientes mercados:\n\n{info}\n\nSaludos cordiales de parte del quipo de touristData.\n\nPara darse de baja enviar un email con el ausnto: CANCELAR.")
            i+=1
    conn.quit()
    print("Programa finalizado con exito")

    time.sleep(86400.0 - ((time.time() - starttime) % 86400.0)) #se repite en 24 horas.
