import duckdb
import matplotlib.pyplot as plt

def generar_reportes_y_graficos():
    con = duckdb.connect()
    
    print("\n=== KPI CIUDADES (CAPA GOLD) ===")
    df_ciudades = con.execute("SELECT * FROM 'data_lake/gold/kpi_ciudades.parquet'").fetchdf()
    print(df_ciudades.to_string(index=False))
    
    print("\n=== KPI PRODUCTOS (CAPA GOLD) ===")
    df_productos = con.execute("SELECT * FROM 'data_lake/gold/kpi_productos.parquet'").fetchdf()
    print(df_productos.to_string(index=False))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    colores = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
    ax1.bar(df_ciudades['ciudad'], df_ciudades['facturacion_total'] / 1e6, color=colores[:len(df_ciudades)])
    ax1.set_title("Facturacion por Ciudad (Millones CLP)")
    ax1.set_ylabel("Millones de Pesos")
    ax1.tick_params(axis='x', rotation=30)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    ax2.pie(
        df_productos['ingresos_totales'], 
        labels=df_productos['producto'], 
        autopct='%1.1f%%', 
        startangle=140
    )
    ax2.set_title("Participacion de Ventas por Producto")
    
    plt.tight_layout()
    plt.savefig("metricas_lakehouse.png", dpi=300)
    print("\n[OK BI] Reporte visual guardado como 'metricas_lakehouse.png'.")

if __name__ == "__main__":
    generar_reportes_y_graficos()
