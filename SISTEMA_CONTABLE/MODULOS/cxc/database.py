import sqlite3
from datetime import datetime

def inicializar_bd():
    """Crea y configura las tablas con mejoras para alertas y presupuestos."""
    try:
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()

        # --- Tabla de Clientes (sin cambios) ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            codigo_cliente TEXT UNIQUE,
            nit_cc TEXT,
            direccion TEXT,
            telefonos TEXT,
            ciudad TEXT,
            correo_electronico TEXT,
            grupo_familiar TEXT,
            es_titular BOOLEAN DEFAULT 0,
            observaciones TEXT
        )
        ''')

        # --- Tabla de Cuentas de Cobro (sin cambios) ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CuentasCobro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            numero_cxc TEXT NOT NULL UNIQUE,
            valor REAL NOT NULL,
            fecha_emision DATE,
            estado TEXT DEFAULT 'Pendiente',
            ruta_pdf TEXT,
            FOREIGN KEY(cliente_id) REFERENCES Clientes(id)
        )
        ''')

        # --- Tabla de Egresos MEJORADA ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha_vencimiento DATE,
            categoria TEXT,
            etiqueta TEXT,
            estado TEXT DEFAULT 'Pendiente',
            
            -- NUEVOS CAMPOS PARA ALERTAS INTELIGENTES
            tiene_descuento BOOLEAN DEFAULT 0,
            fecha_limite_descuento DATE,
            porcentaje_descuento REAL DEFAULT 0,
            monto_descuento REAL DEFAULT 0,
            
            -- TRACKING DE ALERTAS
            alertas_enviadas INTEGER DEFAULT 0,
            ultima_alerta TIMESTAMP,
            
            -- AUDITORÍA
            usuario_que_pago TEXT,
            fecha_pago TIMESTAMP,
            observaciones TEXT,
            
            -- RECURRENCIA
            es_recurrente BOOLEAN DEFAULT 0,
            frecuencia TEXT,  -- 'Mensual', 'Anual', 'Trimestral', etc.
            proximo_vencimiento DATE
        )
        ''')

        # --- NUEVA TABLA: Presupuestos Mensuales ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            etiqueta TEXT NOT NULL,
            monto_presupuestado REAL NOT NULL,
            monto_gastado REAL DEFAULT 0,
            estado TEXT DEFAULT 'Activo',  -- Activo, Excedido, Completado
            UNIQUE(mes, anio, categoria, etiqueta)
        )
        ''')

        # --- NUEVA TABLA: Historial de Alertas ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS HistorialAlertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            egreso_id INTEGER,
            tipo_alerta TEXT,  -- 'Vencimiento Cercano', 'Vencido', 'Descuento por Vencer'
            fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fue_atendida BOOLEAN DEFAULT 0,
            usuario_que_atendio TEXT,
            FOREIGN KEY(egreso_id) REFERENCES Egresos(id)
        )
        ''')

        # --- NUEVA TABLA: Tareas y Recordatorios ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            prioridad TEXT DEFAULT 'Media',  -- Alta, Media, Baja
            categoria TEXT,  -- 'Declaración', 'Cliente', 'Interno', 'Favor'
            cliente_relacionado TEXT,
            estado TEXT DEFAULT 'Pendiente',  -- Pendiente, En Proceso, Completada, Cancelada
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_completado TIMESTAMP,
            usuario_asignado TEXT,
            recordatorio_dias_antes INTEGER DEFAULT 2
        )
        ''')

        # --- NUEVA TABLA: Configuración del Sistema ---
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL,
            descripcion TEXT,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Insertar configuraciones por defecto
        cursor.execute('''
            INSERT OR IGNORE INTO Configuracion (clave, valor, descripcion)
            VALUES 
                ('dias_alerta_anticipada', '7', 'Días de anticipación para alertas de vencimiento'),
                ('dias_alerta_critica', '3', 'Días para alertas críticas'),
                ('alertas_activas', '1', 'Sistema de alertas activado'),
                ('email_notificaciones', '', 'Email para notificaciones'),
                ('flujo_minimo_caja', '2000000', 'Monto mínimo en caja para alertar')
        ''')

        conn.commit()
        print("✅ Base de datos inicializada con mejoras de alertas y presupuestos.")

    except sqlite3.Error as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    inicializar_bd()