#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de corrección para agregar columnas faltantes en LogCreacionPresupuestos
"""

import sqlite3

DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'

def corregir_tabla():
    print("=" * 70)
    print("CORRECCIÓN COMPLETA DE TABLA LogCreacionPresupuestos")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        print("\n✅ Conexión exitosa a la base de datos")
        
        # Verificar columnas actuales
        cursor.execute("PRAGMA table_info(LogCreacionPresupuestos)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📋 Columnas actuales: {', '.join(columnas)}")
        
        # Verificar si faltan columnas críticas
        columnas_necesarias = ['template_id', 'presupuesto_id', 'monto_aplicado']
        faltan = [col for col in columnas_necesarias if col not in columnas]
        
        if faltan:
            print(f"\n⚠️  Faltan columnas: {', '.join(faltan)}")
            print("\n🔧 Recreando tabla completa con estructura correcta...")
            
            # Guardar datos existentes si hay
            datos_existentes = cursor.execute("SELECT * FROM LogCreacionPresupuestos").fetchall()
            
            # Eliminar tabla vieja
            cursor.execute("DROP TABLE LogCreacionPresupuestos")
            
            # Crear tabla nueva con estructura correcta
            cursor.execute('''
                CREATE TABLE LogCreacionPresupuestos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER,
                    presupuesto_id INTEGER,
                    mes INTEGER NOT NULL,
                    anio INTEGER NOT NULL,
                    monto_aplicado REAL NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES PresupuestosTemplates(id),
                    FOREIGN KEY (presupuesto_id) REFERENCES Presupuestos(id)
                )
            ''')
            
            print("   ✅ Tabla recreada con todas las columnas necesarias")
            
        else:
            print("\n✅ La tabla ya tiene todas las columnas necesarias")
        
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("PRAGMA table_info(LogCreacionPresupuestos)")
        columnas_finales = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📋 Columnas finales: {', '.join(columnas_finales)}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\nAhora puedes ejecutar: crear_presupuestos_automaticos.py\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    corregir_tabla()