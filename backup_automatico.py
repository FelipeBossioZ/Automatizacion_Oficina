#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Backup Automático
Crea copias de seguridad de la base de datos con fecha
"""

import shutil
import os
from datetime import datetime

# Configuración
DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'
BACKUP_FOLDER = 'SISTEMA_CONTABLE/DATOS/BACKUPS'

def crear_backup():
    """
    Crea una copia de seguridad de la base de datos
    """
    print("=" * 70)
    print("BACKUP AUTOMÁTICO DE BASE DE DATOS")
    print("=" * 70)
    
    # Crear carpeta de backups si no existe
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
        print(f"\n✅ Carpeta de backups creada: {BACKUP_FOLDER}")
    
    # Verificar que existe la base de datos
    if not os.path.exists(DATABASE):
        print(f"\n❌ Error: No se encontró la base de datos en {DATABASE}")
        return
    
    # Generar nombre del backup con fecha y hora
    ahora = datetime.now()
    nombre_backup = f"backup_{ahora.strftime('%Y%m%d_%H%M%S')}.db"
    ruta_backup = os.path.join(BACKUP_FOLDER, nombre_backup)
    
    try:
        # Copiar archivo
        print(f"\n🔄 Creando backup...")
        print(f"   Origen: {DATABASE}")
        print(f"   Destino: {ruta_backup}")
        
        shutil.copy2(DATABASE, ruta_backup)
        
        # Obtener tamaño del archivo
        tamano = os.path.getsize(ruta_backup) / 1024  # KB
        
        print(f"\n✅ Backup creado exitosamente")
        print(f"   Archivo: {nombre_backup}")
        print(f"   Tamaño: {tamano:.2f} KB")
        print(f"   Fecha: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Listar backups existentes
        listar_backups()
        
        # Limpiar backups antiguos (mantener solo últimos 30)
        limpiar_backups_antiguos()
        
    except Exception as e:
        print(f"\n❌ Error al crear backup: {e}")

def listar_backups():
    """
    Lista todos los backups existentes
    """
    print("\n" + "-" * 70)
    print("BACKUPS EXISTENTES:")
    print("-" * 70)
    
    if not os.path.exists(BACKUP_FOLDER):
        print("No hay backups previos")
        return
    
    backups = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.db')]
    backups.sort(reverse=True)  # Más recientes primero
    
    if not backups:
        print("No hay backups previos")
        return
    
    print(f"\nTotal de backups: {len(backups)}\n")
    
    for i, backup in enumerate(backups[:10], 1):  # Mostrar solo últimos 10
        ruta = os.path.join(BACKUP_FOLDER, backup)
        tamano = os.path.getsize(ruta) / 1024
        fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta))
        
        print(f"{i}. {backup}")
        print(f"   Tamaño: {tamano:.2f} KB")
        print(f"   Fecha: {fecha_mod.strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    if len(backups) > 10:
        print(f"... y {len(backups) - 10} backups más antiguos")

def limpiar_backups_antiguos(mantener=30):
    """
    Elimina backups antiguos, manteniendo solo los más recientes
    """
    if not os.path.exists(BACKUP_FOLDER):
        return
    
    backups = [f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.db')]
    
    if len(backups) <= mantener:
        return
    
    # Ordenar por fecha de modificación
    backups_con_fecha = []
    for backup in backups:
        ruta = os.path.join(BACKUP_FOLDER, backup)
        fecha = os.path.getmtime(ruta)
        backups_con_fecha.append((backup, fecha))
    
    backups_con_fecha.sort(key=lambda x: x[1], reverse=True)
    
    # Eliminar los más antiguos
    for backup, _ in backups_con_fecha[mantener:]:
        ruta = os.path.join(BACKUP_FOLDER, backup)
        try:
            os.remove(ruta)
            print(f"   🗑️  Backup antiguo eliminado: {backup}")
        except Exception as e:
            print(f"   ⚠️  No se pudo eliminar {backup}: {e}")

def restaurar_backup(nombre_backup):
    """
    Restaura un backup específico
    CUIDADO: Sobrescribe la base de datos actual
    """
    print("=" * 70)
    print("RESTAURAR BACKUP")
    print("=" * 70)
    
    ruta_backup = os.path.join(BACKUP_FOLDER, nombre_backup)
    
    if not os.path.exists(ruta_backup):
        print(f"\n❌ Error: No se encontró el backup {nombre_backup}")
        return
    
    # Crear backup de seguridad antes de restaurar
    print("\n⚠️  Creando backup de seguridad antes de restaurar...")
    crear_backup()
    
    try:
        print(f"\n🔄 Restaurando backup: {nombre_backup}")
        shutil.copy2(ruta_backup, DATABASE)
        print(f"✅ Base de datos restaurada exitosamente")
    except Exception as e:
        print(f"❌ Error al restaurar: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restaurar":
        if len(sys.argv) < 3:
            print("Uso: python backup_automatico.py restaurar <nombre_backup>")
        else:
            restaurar_backup(sys.argv[2])
    else:
        crear_backup()
    
    print("\n" + "=" * 70)
    print("Finalizado: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print("=" * 70 + "\n")