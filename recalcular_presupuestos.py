import sqlite3

def recalcular_todos_presupuestos():
    """
    Recalcula el monto gastado de TODOS los presupuestos existentes
    basándose en los gastos PAGADOS.
    """
    try:
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()
        
        print("Recalculando todos los presupuestos...")
        
        # Obtener todos los presupuestos
        presupuestos = cursor.execute('''
            SELECT id, mes, anio, categoria, etiqueta, monto_presupuestado 
            FROM Presupuestos
        ''').fetchall()
        
        if not presupuestos:
            print("❌ No hay presupuestos creados aún.")
            return
        
        print(f"\nEncontrados {len(presupuestos)} presupuestos para actualizar:\n")
        
        for presupuesto in presupuestos:
            p_id, mes, anio, categoria, etiqueta, presupuestado = presupuesto
            
            # Calcular el total gastado (solo PAGADOS) para esa categoría
            resultado = cursor.execute('''
                SELECT COALESCE(SUM(monto), 0) as total
                FROM Egresos
                WHERE categoria = ? 
                AND etiqueta = ? 
                AND estado = 'Pagado'
                AND strftime('%m', fecha_vencimiento) = ?
                AND strftime('%Y', fecha_vencimiento) = ?
            ''', (categoria, etiqueta, f"{mes:02d}", str(anio))).fetchone()
            
            monto_gastado = resultado[0]
            
            # Actualizar el presupuesto
            cursor.execute('''
                UPDATE Presupuestos 
                SET monto_gastado = ?
                WHERE id = ?
            ''', (monto_gastado, p_id))
            
            porcentaje = (monto_gastado / presupuestado * 100) if presupuestado > 0 else 0
            estado = "🚨 EXCEDIDO" if porcentaje > 100 else ("⚠️ CERCA" if porcentaje > 80 else "✅ OK")
            
            print(f"{estado} | {mes:02d}/{anio} | {categoria} - {etiqueta}")
            print(f"   Presupuestado: ${presupuestado:,.0f}")
            print(f"   Gastado: ${monto_gastado:,.0f} ({porcentaje:.1f}%)")
            print()
        
        conn.commit()
        print(f"✅ {len(presupuestos)} presupuestos actualizados correctamente!")
        print("\nAhora recarga la página de Presupuestos para ver los cambios.")
        
    except Exception as e:
        print(f"❌ Error al recalcular presupuestos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    recalcular_todos_presupuestos()