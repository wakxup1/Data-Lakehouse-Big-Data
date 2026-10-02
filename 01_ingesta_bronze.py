import json
import os
import random
from datetime import datetime, timedelta

def generar_datos_bronze():
    os.makedirs("data_lake/bronze", exist_ok=True)
    
    productos = [
        "Laptop Gamer 16GB", "Monitor 144Hz", "Teclado Mecanico RGB", 
        "Mouse Optico Pro", "Audifonos Wireless ANC", "Silla Ergonomica"
    ]
    ciudades = ["Santiago", "Valdivia", "Concepcion", "Temuco", "La Serena", "Antofagasta"]
    
    registros = []
    fecha_base = datetime(2026, 9, 1, 8, 0, 0)

    for i in range(1, 1001):
        fecha = fecha_base + timedelta(minutes=random.randint(1, 43200))
        
        prob_monto = random.random()
        if prob_monto < 0.03:
            monto = None
        elif prob_monto < 0.06:
            monto = -15000
        else:
            monto = random.choice([25990, 49990, 119990, 249990, 599990, 899990])
        
        producto = random.choice(productos) if random.random() > 0.04 else None

        registros.append({
            "transaccion_id": f"TXN-{2000 + i}",
            "cliente_id": f"CLI-{random.randint(100, 300)}",
            "producto": producto,
            "monto": monto,
            "ciudad": random.choice(ciudades),
            "timestamp": fecha.isoformat()
        })

    registros.extend(registros[:35])

    ruta_salida = "data_lake/bronze/ventas_raw.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4)
        
    print(f"[OK BRONZE] Generados {len(registros)} registros en '{ruta_salida}'.")

if __name__ == "__main__":
    generar_datos_bronze()