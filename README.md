# SkyDemand

SkyDemand es un proyecto desarrollado por un equipo de alumnos del Grado de Ciencia de datos por la Universidad Politécnica de 
Valencia y la Escuela Técnica Superior de Ingeniería Informatica dentro del Datathon organizado por la Cátedra de Transparencia y gestión de datos.

Entra en https://tinyurl.com/skydemand para acceder a la web.

### Miembros del equipo
  
  - Yusef Ahsini Ouariaghli - <ahsini30@gmaill.com>
  - Pablo Díaz Masa Valencia
  - Miguel Peris Aragón
  - Pablo Vellosillo Montalt
  - Joan Miravet Tenés
  
### Estructura del proyecto

La página web se ha creado usando Python con la libreria Streamlit, que a su vez ofrece el hosting para la misma. Tambien hacemos uso de las librerias 
Pandas (para el manejo de los datos), Pygithub (para automatizar la subida de los archivos), Sklearn (para los modelos predictivos), Numpy y Requests (para el 
uso de la API de SkyScanner). Para enviar los correos usamos las librerias de smtplib, imaplib y email.

#### Descripción de los archivos
  - web.py: página principal escrita en Pyhton 
  - recolcetor.py: programa encargado de la recolección de datos, enviar emails al newsletter, generar los CSV y subirlos a github. Funciona las 24 horas en una instancia de AWS.
  - fecha.csv: son los arichivos de datos recolectados en esa fecha.
  - carpeta .streamlit: configuración del tema de la página web.
  - .png: fotos que utiliza la web.


![image](https://user-images.githubusercontent.com/82632877/117624261-064e0b00-b175-11eb-8fb4-abcf893b331b.png)


### Licencia 

Reconocimiento-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)
