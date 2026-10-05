"""
05_graficos.py  -  Capa de visualizacion del Data Lakehouse
 
Lee las zonas Silver y Gold con PySpark y genera 2 graficos con matplotlib:
  - Ingresos por ciudad    (Gold:   data/gold/ventas_por_ciudad)
  - Ingresos por producto  (Silver: data/silver/ventas)
 
Salida (carpeta "graficos" junto a "data"):
  - dashboard_ventas.png   -> los 2 graficos en una sola lamina
  - un PNG por grafico     -> para usar por separado en informes
 
Uso:
  python 05_graficos.py                  (guarda los PNG y abre la ventana)
  python 05_graficos.py --sin-ventana    (solo guarda los PNG)
 
Antes hay que haber ejecutado 01, 02 y 03 (que existan las zonas Silver y Gold).
"""
import argparse
import os
import sys
from pathlib import Path
import matplotlib
import pandas as pd
 
# El backend se elige ANTES de importar pyplot: con --sin-ventana no se intenta abrir
# ninguna ventana (util si no hay pantalla o tkinter no esta instalado).
if "--sin-ventana" in sys.argv:
    matplotlib.use("Agg")
 
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
 
# Los montos llevan "$": sin esto matplotlib toma dos "$" en un mismo texto como una
# formula matematica y deforma la linea.
if "text.parse_math" in plt.rcParams:
    plt.rcParams["text.parse_math"] = False
 
# ----------------------------------------------------------------------------
# Estilo y formatos
# ----------------------------------------------------------------------------
C_PRIMARIO = "#1F6F78"   # verde azulado
C_NEUTRO = "#9AA5B1"     # gris
C_TEXTO = "#2B2F36"
C_SUAVE = "#5B6470"
C_GRILLA = "#E3E7EB"
 
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
 
# Formato chileno: punto para miles y coma para decimales
_INTERCAMBIO = str.maketrans(",.", ".,")
 
 
def pesos(x):
    """155760000 -> '$155.760.000'"""
    return "$" + f"{x:,.0f}".translate(_INTERCAMBIO)
 
 
def millones(x):
    """73135000 -> '$73,1 M'"""
    return "$" + f"{x / 1e6:,.1f}".translate(_INTERCAMBIO) + " M"
 
 
def fecha_es(f):
    return f"{f.day} {MESES[f.month - 1].lower()} {f.year}"
 
 
def estilo(ax, grilla="y"):
    """Aspecto limpio: sin bordes superior/derecho y con grilla suave."""
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#C9CFD6")
    ax.tick_params(colors=C_TEXTO, length=0)
    if grilla:
        ax.grid(axis=grilla, color=C_GRILLA, linewidth=0.8)
        ax.set_axisbelow(True)
 
 
def titulo(ax, texto, zona):
    ax.set_title(f"{texto}  |  {zona}", loc="left", fontsize=12.5, fontweight="bold",
                 color=C_TEXTO, pad=12)
 
 
def eje_millones(ax, eje="y"):
    formato = FuncFormatter(lambda v, _: f"{v / 1e6:.0f}")
    (ax.yaxis if eje == "y" else ax.xaxis).set_major_formatter(formato)
 
 
# ----------------------------------------------------------------------------
# Carga de datos
# ----------------------------------------------------------------------------
def localizar_data_dir():
    """Busca la carpeta data/ probando las ubicaciones habituales del proyecto."""
    aqui = Path(__file__).resolve().parent
    candidatos = [
        Path.cwd() / "Data-Lakehouse-Big-Data" / "data",   # mismo criterio que los scripts 01-04
        aqui / "data",
        Path.cwd() / "data",
        aqui.parent / "Data-Lakehouse-Big-Data" / "data",
    ]
    for c in candidatos:
        if (c / "silver" / "ventas").exists() and (c / "gold" / "ventas_por_ciudad").exists():
            return c
    probadas = "\n  ".join(str(c) for c in candidatos)
    sys.exit("No encontre las zonas Silver y Gold. Ejecuta primero 01, 02 y 03.\nRutas probadas:\n  "
             + probadas)
 
 
def ruta_spark(p):
    """Ruta relativa al directorio actual, como en los scripts 02-04.
    Evita problemas con espacios o backslashes de Windows al pasarla a Spark."""
    try:
        return Path(os.path.relpath(p)).as_posix()
    except ValueError:            # Windows: la ruta esta en otro disco
        return Path(p).as_posix()
 
 
def spark_a_pandas(sdf):
    """DataFrame de Spark -> pandas usando collect().
    Se evita toPandas() para no depender de pyarrow ni de la compatibilidad
    entre versiones de pyspark y pandas. Los datos son pocos, asi que es seguro."""
    filas = [fila.asDict() for fila in sdf.collect()]
    return pd.DataFrame(filas, columns=sdf.columns)
 
 
def cargar_con_spark(data_dir):
    """Lee Silver y Gold (Parquet) con PySpark, igual que 03_Consumo.py y 04_lector.py."""
    from pyspark.sql import SparkSession   # import aqui: asi el resto del modulo no lo exige
 
    spark = (SparkSession.builder.appName("GraficosLakehouse")
             .config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        silver = spark_a_pandas(spark.read.parquet(ruta_spark(data_dir / "silver" / "ventas")))
        gold = spark_a_pandas(spark.read.parquet(ruta_spark(data_dir / "gold" / "ventas_por_ciudad")))
    finally:
        spark.stop()
    return silver, gold
 
 
def preparar_datos(silver, gold):
    silver = silver.copy()
    silver["fecha"] = pd.to_datetime(silver["fecha"])
    d = {"silver": silver, "gold": gold, "avisos": []}
 
    if abs(gold["ingresos_totales"].sum() - silver["total"].sum()) > 1:
        d["avisos"].append("Gold no coincide con Silver. Vuelve a ejecutar 03_Consumo.py.")
    return d
 
 
# ----------------------------------------------------------------------------
# Graficos (cada uno dibuja sobre un "ax" recibido, asi sirve para el panel y por separado)
# ----------------------------------------------------------------------------
def graf_ciudad(ax, d):
    g = d["gold"].sort_values("ingresos_totales", ascending=False)
    total = g["ingresos_totales"].sum()
    barras = ax.bar(g["ciudad"].tolist(), g["ingresos_totales"].tolist(), color=C_PRIMARIO, width=0.6)
    for b, v in zip(barras, g["ingresos_totales"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{millones(v)}\n{v / total:.0%}",
                ha="center", va="bottom", fontsize=9.5, color=C_TEXTO)
    ax.set_ylim(0, g["ingresos_totales"].max() * 1.2)
    ax.set_ylabel("Millones de $", color=C_SUAVE)
    eje_millones(ax, "y")
    titulo(ax, "Ingresos por ciudad", "Gold")
    estilo(ax, "y")
 
 
def graf_producto(ax, d):
    p = d["silver"].groupby("producto")["total"].sum().sort_values()   # mayor arriba al graficar
    ax.barh(p.index.tolist(), p.values, color=C_PRIMARIO, height=0.62)
    for y, v in enumerate(p.values):
        ax.text(v, y, " " + millones(v), va="center", ha="left", fontsize=9.5, color=C_TEXTO)
    ax.set_xlim(0, p.max() * 1.22)
    ax.set_xlabel("Millones de $", color=C_SUAVE)
    eje_millones(ax, "x")
    titulo(ax, "Ingresos por producto", "Silver")
    estilo(ax, "x")
 
 
GRAFICOS = [
    ("01_ingresos_por_ciudad", graf_ciudad),
    ("02_ingresos_por_producto", graf_producto),
]
 
 
# ----------------------------------------------------------------------------
# Composicion y salida
# ----------------------------------------------------------------------------
def panel(d):
    """Una sola lamina con los 2 graficos y un encabezado con las cifras clave."""
    fig, ejes = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax, (_, dibujar) in zip(ejes.flat, GRAFICOS):
        dibujar(ax, d)
 
    s = d["silver"]
    kpis = (f"{len(s)} ventas limpias    |    {pesos(s['total'].sum())} en ingresos    |    "
            f"ticket promedio {pesos(s['total'].mean())}    |    "
            f"{fecha_es(s['fecha'].min())} a {fecha_es(s['fecha'].max())}")
    fig.text(0.015, 0.93, "Data Lakehouse  -  Panel de ventas", fontsize=22, fontweight="bold", color=C_TEXTO)
    fig.text(0.015, 0.875, kpis, fontsize=12, color=C_SUAVE)
    fig.text(0.015, 0.012, "Fuente: zonas Silver y Gold del lakehouse (carpeta data/)",
             fontsize=9, color=C_NEUTRO)
    fig.tight_layout(rect=(0, 0.04, 1, 0.84))
    return fig
 
 
def guardar_todo(d, carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    fig = panel(d)
    ruta_panel = carpeta / "dashboard_ventas.png"
    fig.savefig(ruta_panel, dpi=150, facecolor="white")
    rutas = [ruta_panel]
 
    for nombre, dibujar in GRAFICOS:           # un PNG por grafico
        f, ax = plt.subplots(figsize=(8, 5.2))
        dibujar(ax, d)
        f.tight_layout()
        ruta = carpeta / f"{nombre}.png"
        f.savefig(ruta, dpi=150, facecolor="white")
        plt.close(f)                           # solo el panel queda abierto para plt.show()
        rutas.append(ruta)
    return fig, rutas
 
 
def main():
    ap = argparse.ArgumentParser(description="Graficos del Data Lakehouse (Silver y Gold).")
    ap.add_argument("--sin-ventana", action="store_true", help="solo guardar los PNG, sin abrir ventana")
    args = ap.parse_args()
 
    data_dir = localizar_data_dir()
    print("Leyendo el lakehouse en:", data_dir)
 
    silver, gold = cargar_con_spark(data_dir)
    d = preparar_datos(silver, gold)
 
    for aviso in d["avisos"]:
        print("AVISO:", aviso)
 
    _, rutas = guardar_todo(d, data_dir.parent / "graficos")
    print(f"Listo: {len(rutas)} imagenes guardadas en {rutas[0].parent}")
    for r in rutas:
        print("  -", r.name)
 
    if not args.sin_ventana:
        plt.show()
 
 
if __name__ == "__main__":
    main()