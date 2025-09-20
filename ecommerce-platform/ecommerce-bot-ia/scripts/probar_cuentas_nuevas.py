import requests
import time

def probar_cuentas_nuevas():
    print("PROBANDO CUENTAS ESPECIALIZADAS")
    print("=" * 50)
    
    # Configuracion de las cuentas a probar
    cuentas = [
        {
            "telefono": "+5678901234",
            "nombre": "Mundo Canino",
            "producto_test": "royal canin"
        },
        {
            "telefono": "+3456789012", 
            "nombre": "Green House",
            "producto_test": "og kush"
        }
    ]
    
    for cuenta in cuentas:
        print(f"\n=== PROBANDO {cuenta['nombre']} ({cuenta['telefono']}) ===")
        
        # 1. Conexion inicial
        print("1. Conectando al bot...")
        response = requests.post('http://localhost:8001/webhook', json={
            'telefono': cuenta['telefono'],
            'mensaje': 'Hola, buenos dias'
        })
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get('respuesta', '')
            if cuenta['nombre'] in respuesta:
                print(f"   OK - Conectado con {cuenta['nombre']}")
            else:
                print(f"   INFO - Respuesta: {respuesta[:100]}...")
        else:
            print(f"   ERROR - Status: {response.status_code}")
            continue
        
        time.sleep(2)
        
        # 2. Ver catalogo
        print("2. Consultando catalogo...")
        response = requests.post('http://localhost:8001/webhook', json={
            'telefono': cuenta['telefono'],
            'mensaje': 'que productos tienes disponibles?'
        })
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get('respuesta', '')
            # Contar productos (basado en simbolos de precio)
            num_productos = respuesta.count('$')
            print(f"   OK - Catalogo mostrado con ~{num_productos} productos")
            
            # Mostrar primera parte del catalogo
            if num_productos > 0:
                lines = respuesta.split('\n')[:5]  # Primeras 5 lineas
                for line in lines:
                    if line.strip():
                        print(f"      {line.strip()[:60]}...")
        else:
            print(f"   ERROR - Status: {response.status_code}")
            continue
        
        time.sleep(2)
        
        # 3. Buscar producto especifico
        print(f"3. Buscando '{cuenta['producto_test']}'...")
        response = requests.post('http://localhost:8001/webhook', json={
            'telefono': cuenta['telefono'],
            'mensaje': f'quiero comprar {cuenta["producto_test"]}'
        })
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get('respuesta', '')
            
            if 'cuanta' in respuesta.lower() or 'cantidad' in respuesta.lower():
                print("   OK - Producto encontrado, bot pidiendo cantidad")
                
                # 4. Especificar cantidad
                time.sleep(2)
                print("4. Especificando cantidad...")
                response = requests.post('http://localhost:8001/webhook', json={
                    'telefono': cuenta['telefono'],
                    'mensaje': '1'
                })
                
                if response.status_code == 200:
                    result = response.json()
                    respuesta = result.get('respuesta', '')
                    
                    if 'confirma' in respuesta.lower():
                        print("   OK - Bot pidiendo confirmacion de compra")
                        
                        # Mostrar detalles de la compra
                        if '$' in respuesta:
                            # Extraer precio
                            import re
                            precios = re.findall(r'\$[\d,]+', respuesta)
                            if precios:
                                print(f"   Precio detectado: {precios[-1]}")
                    else:
                        print(f"   INFO - Respuesta: {respuesta[:100]}...")
            elif 'no encontre' in respuesta.lower() or 'no encontr' in respuesta.lower():
                print("   INFO - Producto no encontrado")
            else:
                print(f"   INFO - Respuesta: {respuesta[:100]}...")
        else:
            print(f"   ERROR - Status: {response.status_code}")
    
    print(f"\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    print("MUNDO CANINO (+5678901234):")
    print("  - 7 productos para mascotas")
    print("  - Categorias: Alimento, Juguetes, Accesorios, Higiene, Camas")
    print("  - Rango: $5,990 - $89,990")
    print("")
    print("GREEN HOUSE (+3456789012):")
    print("  - 8 productos canabicos")
    print("  - Categorias: Flores, Concentrados, Comestibles, Accesorios, CBD, Semillas")
    print("  - Rango: $12,990 - $189,990")
    print("")
    print("CREDENCIALES PARA ACCESO AL BACKOFFICE:")
    print("Mundo Canino: admin@mundocanino.com / canino123")
    print("Green House: admin@greenhouse.com / green123")

if __name__ == "__main__":
    probar_cuentas_nuevas()