from pyspark.sql import SparkSession

# 1. Iniciar sesión de Spark
spark = SparkSession.builder.appName("LectorParquet").getOrCreate()

# 2. Leer y mostrar los datos de la Zona Silver (Datos limpios)
print("--- ZONA SILVER: Primeras 10 filas de ventas procesadas ---")
df_silver = spark.read.parquet("data/processed/ventas")
df_silver.show(10)

# 3. Leer y mostrar los datos de la Zona Gold (Modelo final)
print("--- ZONA GOLD: Ingresos totales por ciudad ---")
df_gold = spark.read.parquet("data/gold/ventas_por_ciudad")
df_gold.show()

spark.stop()