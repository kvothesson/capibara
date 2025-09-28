"""Test del SDK de Capibara directamente."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from capibara import Capibara

def test_sdk():
    print("🦫 Probando Capibara SDK directamente")
    print("=" * 50)
    
    # Inicializar Capibara
    cb = Capibara()
    
    # Test 1: Script simple
    print("\n1. Generando script para calcular el área de un círculo...")
    result = cb.run(
        "Create a script that calculates the area of a circle",
        context={"radius": 5}
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print("✓ Script generado y ejecutado exitosamente")
        print(f"  Raw output: {result.raw}")
    else:
        print(f"✗ Error: {result.output.get('message', 'Error desconocido')}")
    
    # Test 2: Script con lógica más compleja
    print("\n2. Generando script para procesar datos...")
    result = cb.run(
        "Create a script that processes a CSV-like data and returns summary statistics",
        context={
            "data": [
                {"name": "Alice", "age": 25, "score": 85},
                {"name": "Bob", "age": 30, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78}
            ]
        }
    )
    
    print(f"Status: {result.status}")
    if result.status == "ok":
        print("✓ Script generado y ejecutado exitosamente")
        print(f"  Raw output: {result.raw}")
    else:
        print(f"✗ Error: {result.output.get('message', 'Error desconocido')}")
    
    # Test 3: Listar scripts cacheados
    print("\n3. Scripts cacheados:")
    scripts = cb.list_scripts()
    print(f"Total: {len(scripts)} scripts")
    for i, script in enumerate(scripts[-3:], 1):  # Mostrar los últimos 3
        print(f"  {i}. {script['fingerprint'][:12]}... - {len(script['deps'])} dependencias")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas!")

if __name__ == "__main__":
    test_sdk()
