import pandas as pd #Libreria Panda
import random
import os 
from datetime import datetime,timedelta

os.makedirs("Data-Lakehouse-Big-Data/data/bronze", exist_ok=True) 
#Crea la carpeta Raw en caso de que no exista,
#si existe no da error al tener el "exist_ok=True"

productos = ["Laptop", "Mouse", "Teclado","Monitor","Audifonos"]
ciudades = ["Santiago", "Valparaíso", "Concepción", "santiago ", None]

filas = []
for i in range(1,501):
    filas.append({
        "id_ventas": i,
        "fecha":(datetime(2026,1,1) + timedelta(days=random.randint(0,200))).strftime("%d-%m-%Y"),
        "producto": random.choice(productos),
        "ciudad": random.choice(ciudades),
        "cantidad": random.choice([1, 2, 3, 4, None]),
        "precio_unitario": random.choice([15000, 25000, 40000, 250000, 600000]),
    })

#Genera de manera aleatoria los valores a ingresar dentro de las filas utilizando el random para poder
#tener datos efectivamente aleatorios

df = pd.DataFrame(filas) #Convierte lista de dicc en tabla

df = pd.concat([df, df.head(10)]) 
#Pega las primeras 10 filas al final para generar duplicados simulando df = DataFrame
# errores posibles

df.to_csv("Data-Lakehouse-Big-Data/data/bronze/ventas.csv", index=False) #Index = False evita añadir columna extra con los numero de fila

print("Datos en bruto guardados:", len(df), "filas")