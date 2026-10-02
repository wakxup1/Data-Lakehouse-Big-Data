import os
import duckdb

def procesar_silver():
    os.makedirs("data_lake/silver", exist_ok=True)
    
    con = duckdb.connect()
    
    query = """
    COPY (
        WITH raw_stream AS (
            SELECT * FROM read_json_auto('data_lake/bronze/ventas_raw.json')
        ),
        datos_limpios AS (
            SELECT 
                transaccion_id,
                cliente_id,
                COALESCE(producto, 'Sin Clasificar') AS producto,
                CAST(monto AS DOUBLE) AS monto,
                ciudad,
                CAST(timestamp AS TIMESTAMP) AS fecha_transaccion,
                ROW_NUMBER() OVER(PARTITION BY transaccion_id ORDER BY timestamp DESC) as fila_num
            FROM raw_stream
            WHERE monto IS NOT NULL AND monto > 0
        )
        SELECT 
            transaccion_id,
            cliente_id,
            producto,
            monto,
            ciudad,
            fecha_transaccion
        FROM datos_limpios
        WHERE fila_num = 1
    ) TO 'data_lake/silver/ventas_limpias.parquet' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
    """
    
    con.execute(query)
    total_filas = con.execute("SELECT COUNT(*) FROM 'data_lake/silver/ventas_limpias.parquet'").fetchone()[0]
    print(f"[OK SILVER] Consolidada tabla curada con {total_filas} registros limpios.")

if __name__ == "__main__":
    procesar_silver()
