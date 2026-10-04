print("HOLA MUNDO!")
from pyspark.sql import SparkSession
import os 
from pyspark.sql.functions import col,trim,initcap, to_date 

#SparkSession inicia punto de entrada en PySpark
#trim = eliminar espacios vacios en un string
#col = referirse a una columna por su nombre
#initcap = Capitaliza los strings
#to_date = convierte el string de una fecha a una fecha real

spark = SparkSession.builder.appName("Limpieza").getOrCreate()
#getOrCreate = crea o reutliza la sesion.

df = spark.read.csv("Data-Lakehouse-Big-Data/data/raw/ventas.csv", header = True, inferSchema = True)
#Esto leera el archivo ventas.CSV en raw conviertiendolo en un DataFrame de spark
# header = True Indicar que los nombres de las columnas y no los datos
# inferSchema = True Interpreta el texto segun lo que sea similar a python "1" = 1 int
print("Filas del archivo Bronze:",df.count())

df_limpio = (
    
    df.dropDuplicates(["id_ventas"]) #Al ser id solo debe haber una
    .dropna(subset=["cantidad", "ciudad"] ) #dropna Elimina valores nulos en las columnas especificadas

    # withColumn Añade o modifica una columna existente dependiendo de los parametros dados
    .withColumn("ciudad", initcap(trim(col("ciudad")))) 
    .withColumn("fecha", to_date(col("fecha"), "dd-MM-yyyy"))
    .withColumn("total", col("cantidad") * col("precio_unitario")) 

    #Creamos la columna Total y lo multiplicamos
    # por su precio unitario y la cantidad registrada
)

df_limpio.write.mode("overwrite").parquet("Data-Lakehouse-Big-Data/data/processed/ventas")
# .write: escribir el data frame en disco
# mode("overwrite"): si existe la carpeta la reemplaza
# .parquet("ruta"): guarda el archivo en formato parquet

spark.stop()


