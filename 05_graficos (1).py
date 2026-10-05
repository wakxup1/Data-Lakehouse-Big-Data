import os
import pandas as pd
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession

# 1. Leer las zonas Silver y Gold con Spark
spark = SparkSession.builder.appName("Graficos").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df_silver = spark.read.parquet("Data-Lakehouse-Big-Data/data/silver/ventas")
df_gold = spark.read.parquet("Data-Lakehouse-Big-Data/data/gold/ventas_por_ciudad")

# 2. Pasar los datos a pandas (son pocas filas) y cerrar Spark
silver = pd.DataFrame(df_silver.collect(), columns=df_silver.columns)
gold = pd.DataFrame(df_gold.collect(), columns=df_gold.columns)
spark.stop()

# 3. Preparar los datos, expresados en millones de pesos
ciudad = gold.sort_values("ingresos_totales", ascending=False)
ciudad_millones = ciudad["ingresos_totales"] / 1_000_000

producto = silver.groupby("producto")["total"].sum().sort_values()
producto_millones = producto / 1_000_000

# 4. Dibujar los dos gráficos lado a lado
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

barras = ax1.bar(ciudad["ciudad"], ciudad_millones, color="#1F6F78")
ax1.bar_label(barras, fmt="%.1f")  # escribe el valor sobre cada barra
ax1.set_title("Ingresos por ciudad")
ax1.set_ylabel("Millones de $")

barras = ax2.barh(producto_millones.index, producto_millones, color="#1F6F78")
ax2.bar_label(barras, fmt="%.1f")
ax2.set_title("Ingresos por producto")
ax2.set_xlabel("Millones de $")

plt.tight_layout()

# 5. Guardar la imagen y mostrarla
os.makedirs("Data-Lakehouse-Big-Data/graficos", exist_ok=True)
plt.savefig("Data-Lakehouse-Big-Data/graficos/ventas.png", dpi=150)
plt.show()
