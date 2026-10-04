from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, desc

# 1. Iniciar sesión de Spark
spark = SparkSession.builder.appName("ConsumoGold").getOrCreate()

# 2. Leer los datos limpios desde la zona Silver (Parquet)
df_silver = spark.read.parquet("Data-Lakehouse-Big-Data/data/processed/ventas")

print("Esquema de los datos limpios:")
df_silver.printSchema()

# 3. Modelar los datos para la zona Gold: Ventas totales por ciudad
df_gold = (
    df_silver.groupBy("ciudad")
    .agg(sum("total").alias("ingresos_totales"))
    .orderBy(desc("ingresos_totales"))
)

print("Resultados de la Zona Gold (Ingresos por Ciudad):")
df_gold.show()

# 4. Guardar los datos modelados en la zona Gold
df_gold.write.mode("overwrite").parquet("Data-Lakehouse-Big-Data/data/gold/ventas_por_ciudad")
print("¡Laboratorio completado! Datos modelados guardados en data/gold/ventas_por_ciudad")

spark.stop()