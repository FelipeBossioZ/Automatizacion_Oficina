#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de PRUEBA para verificar la creación automática de presupuestos
Ejecutar ANTES de automatizar para verificar que funciona correctamente
"""

import sqlite3
from datetime import datetime

DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'

def probar_creacion():
    """
    Prueba la creación de presupuestos sin crear nada realmente
    Solo muestra qué se crearía
    """
    print("=" * 70)
    print("SIMULACIÓN DE CREACIÓN AUTOMÁTICA DE PRESUPUESTOS")
    print("(Este script NO crea nada, solo muestra qué pasaría)")
    print("=" * 70)
    
    # Obtener fecha actual
    ahora = datetime.now()
    mes_actual = ahora.month
    anio_actual = ahora.year
    
    print(f"\n📅 Fecha actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📊 Mes a procesar: {mes_actual}/{anio_actual}\n")
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        print("✅ Conexión a base de datos exitosa\n")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return
    
    # Obtener templates activos
    templates = conn.execute('''
        SELECT * FROM PresupuestosTemplates 
        WHERE activo = 1
        ORDER BY categoria
    ''').fetchall()
    
    if not templates:
        print("⚠️  No hay templates activos")
        print("   Crea templates en el módulo de Presupuestos primero\n")
        conn.close()
        return
    
    print(f"📋 TEMPLATES ACTIVOS ENCONTRADOS: {len(templates)}\n")
    print("-" * 70)
    
    for i, template in enumerate(templates, 1):
        categoria = template['categoria']
        etiqueta = template['etiqueta']
        monto_base = template['monto_base']
        
        print(f"\n{i}. {categoria} - {etiqueta}")
        print(f"   Monto Base: ${monto_base:,.0f}")
        
        # Mostrar montos especiales si existen
        if template['monto_febrero']:
            print(f"   Febrero:    ${template['monto_febrero']:,.0f} (Cesantías)")
        if template['monto_junio']:
            print(f"   Junio:      ${template['monto_junio']:,.0f} (Prima)")
        if template['monto_diciembre']:
            print(f"   Diciembre:  ${template['monto_diciembre']:,.0f} (Liquidaciones)")
        
        # Determinar qué monto se usaría este mes
        if mes_actual == 2 and template['monto_febrero']:
            monto_aplicar = template['monto_febrero']
            tipo = "Cesantías"
        elif mes_actual == 6 and template['monto_junio']:
            monto_aplicar = template['monto_junio']
            tipo = "Prima"
        elif mes_actual == 12 and template['monto_diciembre']:
            monto_aplicar = template['monto_diciembre']
            tipo = "Liquidaciones"
        else:
            monto_aplicar = monto_base
            tipo = "Base"
        
        # Verificar si ya existe
        existe = conn.execute('''
            SELECT id FROM Presupuestos 
            WHERE categoria = ? AND etiqueta = ? 
            AND mes = ? AND anio = ?
        ''', (categoria, etiqueta, mes_actual, anio_actual)).fetchone()
        
        print(f"\n   🎯 Monto para {mes_actual}/{anio_actual}: ${monto_aplicar:,.0f} ({tipo})")
        
        if existe:
            print(f"   ⚠️  YA EXISTE presupuesto para este mes (ID: {existe['id']})")
        else:
            print(f"   ✅ SE CREARÍA un presupuesto nuevo")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("FIN DE LA SIMULACIÓN")
    print("=" * 70)
    print("\n💡 Si todo se ve bien, ejecuta: crear_presupuestos_automaticos.py")
    print("   para crear los presupuestos reales\n")

if __name__ == "__main__":
    probar_creacion()