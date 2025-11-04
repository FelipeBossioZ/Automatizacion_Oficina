#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Automatización de Presupuestos
Crea presupuestos automáticamente el día 1 de cada mes basándose en templates activos
"""

import sqlite3
from datetime import datetime
import os

# Configuración
DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'

def obtener_monto_segun_mes(template, mes):
    """
    Retorna el monto correspondiente según el mes.
    Si el mes tiene monto especial, lo usa. Si no, usa el monto base.
    """
    if mes == 2 and template['monto_febrero']:  # Febrero
        return template['monto_febrero']
    elif mes == 6 and template['monto_junio']:  # Junio
        return template['monto_junio']
    elif mes == 12 and template['monto_diciembre']:  # Diciembre
        return template['monto_diciembre']
    else:
        return template['monto_base']

def actualizar_monto_gastado(conn, presupuesto_id, mes, anio, categoria, etiqueta):
    """
    Calcula y actualiza el monto ya gastado para un presupuesto
    """
    resultado = conn.execute('''
        SELECT COALESCE(SUM(monto), 0) as total
        FROM Egresos
        WHERE categoria = ? 
        AND etiqueta = ? 
        AND estado = 'Pagado'
        AND strftime('%m', fecha_vencimiento) = ?
        AND strftime('%Y', fecha_vencimiento) = ?
    ''', (categoria, etiqueta, f"{mes:02d}", str(anio))).fetchone()
    
    monto_gastado = resultado['total']
    conn.execute('UPDATE Presupuestos SET monto_gastado = ? WHERE id = ?', 
                (monto_gastado, presupuesto_id))
    
    return monto_gastado

def crear_presupuestos_del_mes():
    """
    Función principal que crea presupuestos automáticamente
    """
    print("=" * 70)
    print("CREACIÓN AUTOMÁTICA DE PRESUPUESTOS")
    print("=" * 70)
    
    # Obtener fecha actual
    ahora = datetime.now()
    mes_actual = ahora.month
    anio_actual = ahora.year
    
    print(f"\n📅 Fecha: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📊 Creando presupuestos para: {mes_actual}/{anio_actual}")
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return
    
    # Obtener templates activos
    try:
        templates = conn.execute('''
            SELECT * FROM PresupuestosTemplates 
            WHERE activo = 1
            ORDER BY categoria
        ''').fetchall()
        
        if not templates:
            print("\n⚠️  No hay templates activos configurados")
            print("   Configura templates en el módulo de Presupuestos")
            conn.close()
            return
        
        print(f"\n✅ Encontrados {len(templates)} templates activos\n")
    except Exception as e:
        print(f"❌ Error al obtener templates: {e}")
        conn.close()
        return
    
    # Procesar cada template
    presupuestos_creados = 0
    presupuestos_existentes = 0
    errores = 0
    
    for template in templates:
        categoria = template['categoria']
        etiqueta = template['etiqueta']
        
        print(f"\n🔄 Procesando: {categoria} - {etiqueta}")
        
        # Verificar si ya existe presupuesto para este mes
        existe = conn.execute('''
            SELECT id FROM Presupuestos 
            WHERE categoria = ? AND etiqueta = ? 
            AND mes = ? AND anio = ?
        ''', (categoria, etiqueta, mes_actual, anio_actual)).fetchone()
        
        if existe:
            print(f"   ⏭️  Ya existe presupuesto para este mes (ID: {existe['id']})")
            presupuestos_existentes += 1
            continue
        
        # Determinar el monto según el mes
        monto = obtener_monto_segun_mes(template, mes_actual)
        
        # Determinar si es mes especial
        mes_especial = ""
        if mes_actual == 2 and template['monto_febrero'] and template['monto_febrero'] != template['monto_base']:
            mes_especial = " (Cesantías)"
        elif mes_actual == 6 and template['monto_junio'] and template['monto_junio'] != template['monto_base']:
            mes_especial = " (Prima)"
        elif mes_actual == 12 and template['monto_diciembre'] and template['monto_diciembre'] != template['monto_base']:
            mes_especial = " (Liquidaciones)"
        
        try:
            # Crear el presupuesto
            cursor = conn.execute('''
                INSERT INTO Presupuestos 
                (mes, anio, categoria, etiqueta, monto_presupuestado, monto_gastado, 
                 template_id, creado_automaticamente)
                VALUES (?, ?, ?, ?, ?, 0, ?, 1)
            ''', (mes_actual, anio_actual, categoria, etiqueta, monto, template['id']))
            
            presupuesto_id = cursor.lastrowid
            
            # Actualizar monto gastado (por si hay gastos pagados del mes)
            monto_gastado = actualizar_monto_gastado(conn, presupuesto_id, mes_actual, 
                                                     anio_actual, categoria, etiqueta)
            
            # Registrar en el log
            conn.execute('''
                INSERT INTO LogCreacionPresupuestos 
                (template_id, presupuesto_id, mes, anio, monto_aplicado)
                VALUES (?, ?, ?, ?, ?)
            ''', (template['id'], presupuesto_id, mes_actual, anio_actual, monto))
            
            conn.commit()
            
            print(f"   ✅ Creado: ${monto:,.0f}{mes_especial}")
            if monto_gastado > 0:
                print(f"      💰 Ya gastado: ${monto_gastado:,.0f}")
            
            presupuestos_creados += 1
            
        except Exception as e:
            print(f"   ❌ Error al crear presupuesto: {e}")
            errores += 1
            conn.rollback()
    
    # Cerrar conexión
    conn.close()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE EJECUCIÓN")
    print("=" * 70)
    print(f"✅ Presupuestos creados:    {presupuestos_creados}")
    print(f"⏭️  Ya existían:             {presupuestos_existentes}")
    print(f"❌ Errores:                 {errores}")
    print(f"📊 Total templates activos: {len(templates)}")
    print("=" * 70)
    
    if presupuestos_creados > 0:
        print(f"\n🎉 ¡Éxito! Se crearon {presupuestos_creados} presupuestos para {mes_actual}/{anio_actual}")
    elif presupuestos_existentes > 0:
        print(f"\n✅ Los presupuestos para {mes_actual}/{anio_actual} ya estaban creados")
    else:
        print(f"\n⚠️  No se realizaron cambios")
    
    print(f"\n📅 Finalizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

if __name__ == "__main__":
    crear_presupuestos_del_mes()