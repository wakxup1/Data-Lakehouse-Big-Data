from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# 1. Iniciar sesión de Spark
spark = SparkSession.builder.appName("LectorParquet").getOrCreate()

# 2. Leer y mostrar los datos de la Zona Silver (Datos limpios)
print("--- ZONA SILVER: Primeras 10 filas de ventas procesadas ---")
df_silver = spark.read.parquet("Data-Lakehouse-Big-Data/data/processed/ventas")
df_silver.show(10)

# 3. Leer y mostrar los datos de la Zona Gold (Modelo final)
print("--- ZONA GOLD: Ingresos totales por ciudad ---")
df_gold = spark.read.parquet("Data-Lakehouse-Big-Data/data/gold/ventas_por_ciudad")
df_gold.show()

# 4. Mostrar Consulta Basica del TOP 10 Ventas mas grandes
print("--- TOP 10 VENTAS MÁS GRANDES ---")
df_top = (
    df_silver.select("id_ventas", "fecha", "ciudad", "producto", "cantidad", "total")
    .orderBy(F.desc("total"))
    .limit(10)
)
df_top.show()

spark.stop()