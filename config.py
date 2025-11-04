#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Archivo de Configuración del Sistema
Centraliza todas las configuraciones importantes
"""

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================

# PIN para operaciones críticas (eliminar presupuestos con datos)
PIN_SISTEMA = "0000"  # ⚠️ CAMBIAR después de la presentación

# Configuración de sesiones (para cuando se implemente login)
SESSION_TIMEOUT = 3600  # Segundos (1 hora)

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================

DATABASE_PATH = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'
BACKUP_FOLDER = 'SISTEMA_CONTABLE/DATOS/BACKUPS'

# Configuración de backups automáticos
BACKUPS_MANTENER = 30  # Número de backups a mantener
BACKUP_HORA = "06:00"  # Hora del backup automático

# ==========================================
# CONFIGURACIÓN DE PRESUPUESTOS
# ==========================================

# Meses con presupuestos especiales
MESES_ESPECIALES = {
    2: "Cesantías",
    6: "Prima",
    12: "Liquidaciones"
}

# Etiquetas disponibles
ETIQUETAS = ["OFICINA", "GTFF"]

# ==========================================
# CONFIGURACIÓN DE ALERTAS
# ==========================================

# Días de anticipación para alertas
DIAS_ALERTA_ANTICIPADA = 7
DIAS_ALERTA_CRITICA = 3

# Configuración para detección de tendencias
MESES_PARA_TENDENCIA = 3  # Cuántos meses consecutivos para alertar
PORCENTAJE_EXCESO_ALERTA = 10  # % de exceso para generar alerta

# ==========================================
# CONFIGURACIÓN DE SERVIDOR
# ==========================================

# Puerto del servidor Flask
SERVER_PORT = 8000
SERVER_HOST = '0.0.0.0'  # Para permitir conexiones externas

# Modo debug (cambiar a False en producción)
DEBUG_MODE = False

# ==========================================
# CONFIGURACIÓN DE REPORTES
# ==========================================

# Formato de moneda
MONEDA = "COP"
SEPARADOR_MILES = ","
SEPARADOR_DECIMALES = "."

# Configuración de Excel
EXCEL_EMPRESA = "Tu Empresa"
EXCEL_LOGO = None  # Ruta al logo (opcional)

# ==========================================
# CATEGORÍAS POR DEFECTO
# ==========================================

CATEGORIAS_DEFAULT = [
    'Nómina',
    'Arriendo',
    'Servicios',
    'Internet',
    'Suscripciones',
    'Mantenimiento',
    'Cafetería',
    'Impuestos',
    'Otros'
]

# ==========================================
# INFORMACIÓN DE LA EMPRESA
# ==========================================

EMPRESA_NOMBRE = "Tu Empresa"
EMPRESA_NIT = "123456789-0"
EMPRESA_DIRECCION = "Calle 123 #45-67, Medellín"
EMPRESA_TELEFONO = "+57 (4) 123-4567"
EMPRESA_EMAIL = "contacto@tuempresa.com"

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def obtener_pin():
    """Retorna el PIN configurado"""
    return PIN_SISTEMA

def validar_pin(pin_ingresado):
    """Valida si el PIN ingresado es correcto"""
    return pin_ingresado == PIN_SISTEMA

def cambiar_pin(pin_nuevo):
    """
    Cambia el PIN del sistema
    NOTA: Esto solo cambia en memoria, no modifica el archivo
    Para cambio permanente, editar este archivo directamente
    """
    global PIN_SISTEMA
    PIN_SISTEMA = pin_nuevo
    return True

def obtener_configuracion():
    """Retorna un diccionario con toda la configuración"""
    return {
        'pin': PIN_SISTEMA,
        'database': DATABASE_PATH,
        'backup_folder': BACKUP_FOLDER,
        'port': SERVER_PORT,
        'debug': DEBUG_MODE,
        'empresa': {
            'nombre': EMPRESA_NOMBRE,
            'nit': EMPRESA_NIT,
            'direccion': EMPRESA_DIRECCION,
            'telefono': EMPRESA_TELEFONO,
            'email': EMPRESA_EMAIL
        }
    }

# ==========================================
# PARA USO FUTURO: CONFIGURACIÓN DINÁMICA
# ==========================================

def cargar_configuracion_desde_archivo():
    """
    Para implementación futura:
    Cargar configuración desde archivo JSON/INI
    """
    pass

def guardar_configuracion_a_archivo():
    """
    Para implementación futura:
    Guardar configuración en archivo JSON/INI
    """
    pass