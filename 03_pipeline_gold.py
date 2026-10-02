import os
import duckdb

def procesar_gold():
    os.makedirs("data_lake/gold", exist_ok=True)
    con = duckdb.connect()
    
    query_ciudades = """
    COPY (
        SELECT 
            ciudad,
            COUNT(transaccion_id) AS total_ventas,
            ROUND(SUM(monto), 2) AS facturacion_total,
            ROUND(AVG(monto), 2) AS ticket_promedio
        FROM 'data_lake/silver/ventas_limpias.parquet'
        GROUP BY ciudad
        ORDER BY facturacion_total DESC
    ) TO 'data_lake/gold/kpi_ciudades.parquet' (FORMAT PARQUET);
    """
    
    query_productos = """
    COPY (
        SELECT 
            producto,
            COUNT(transaccion_id) AS unidades_vendidas,
            ROUND(SUM(monto), 2) AS ingresos_totales,
            ROUND(AVG(monto), 2) AS precio_promedio
        FROM 'data_lake/silver/ventas_limpias.parquet'
        GROUP BY producto
        ORDER BY ingresos_totales DESC
    ) TO 'data_lake/gold/kpi_productos.parquet' (FORMAT PARQUET);
    """
    
    con.execute(query_ciudades)
    con.execute(query_productos)
    print("[OK GOLD] Tablas analíticas kpi_ciudades y kpi_productos generadas.")

if __name__ == "__main__":
    procesar_gold()