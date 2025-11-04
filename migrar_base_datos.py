import sqlite3

def migrar_base_datos():
    """
    Agrega las nuevas columnas a la tabla Egresos existente
    y crea las tablas nuevas si no existen.
    """
    try:
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()
        
        print("Iniciando migración de base de datos...")
        
        # Lista de columnas nuevas que necesita la tabla Egresos
        nuevas_columnas = [
            ("tiene_descuento", "BOOLEAN DEFAULT 0"),
            ("fecha_limite_descuento", "DATE"),
            ("porcentaje_descuento", "REAL DEFAULT 0"),
            ("monto_descuento", "REAL DEFAULT 0"),
            ("alertas_enviadas", "INTEGER DEFAULT 0"),
            ("ultima_alerta", "TIMESTAMP"),
            ("usuario_que_pago", "TEXT"),
            ("fecha_pago", "TIMESTAMP"),
            ("observaciones", "TEXT"),
            ("es_recurrente", "BOOLEAN DEFAULT 0"),
            ("frecuencia", "TEXT"),
            ("proximo_vencimiento", "DATE")
        ]
        
        # Verificar qué columnas ya existen
        cursor.execute("PRAGMA table_info(Egresos)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        
        print(f"Columnas existentes en Egresos: {columnas_existentes}")
        
        # Agregar solo las columnas que no existen
        for nombre_columna, tipo_dato in nuevas_columnas:
            if nombre_columna not in columnas_existentes:
                try:
                    sql = f"ALTER TABLE Egresos ADD COLUMN {nombre_columna} {tipo_dato}"
                    cursor.execute(sql)
                    print(f"  ✅ Columna '{nombre_columna}' agregada")
                except sqlite3.OperationalError as e:
                    print(f"  ⚠️  No se pudo agregar '{nombre_columna}': {e}")
            else:
                print(f"  ⏭️  Columna '{nombre_columna}' ya existe")
        
        # Crear tablas nuevas si no existen
        print("\nCreando tablas nuevas...")
        
        # Tabla de Presupuestos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            etiqueta TEXT NOT NULL,
            monto_presupuestado REAL NOT NULL,
            monto_gastado REAL DEFAULT 0,
            estado TEXT DEFAULT 'Activo',
            UNIQUE(mes, anio, categoria, etiqueta)
        )
        ''')
        print("  ✅ Tabla Presupuestos verificada")
        
        # Tabla de Tareas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            prioridad TEXT DEFAULT 'Media',
            categoria TEXT,
            cliente_relacionado TEXT,
            estado TEXT DEFAULT 'Pendiente',
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_completado TIMESTAMP,
            usuario_asignado TEXT,
            recordatorio_dias_antes INTEGER DEFAULT 2
        )
        ''')
        print("  ✅ Tabla Tareas verificada")
        
        # Tabla de Configuración
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL,
            descripcion TEXT,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("  ✅ Tabla Configuracion verificada")
        
        # Insertar configuraciones por defecto
        configuraciones_default = [
            ('dias_alerta_anticipada', '7', 'Días de anticipación para alertas de vencimiento'),
            ('dias_alerta_critica', '3', 'Días para alertas críticas'),
            ('alertas_activas', '1', 'Sistema de alertas activado'),
            ('email_notificaciones', '', 'Email para notificaciones'),
            ('flujo_minimo_caja', '2000000', 'Monto mínimo en caja para alertar')
        ]
        
        for clave, valor, descripcion in configuraciones_default:
            cursor.execute('''
                INSERT OR IGNORE INTO Configuracion (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', (clave, valor, descripcion))
        
        print("  ✅ Configuraciones por defecto insertadas")
        
        # Tabla de Historial de Alertas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS HistorialAlertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            egreso_id INTEGER,
            tipo_alerta TEXT,
            fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fue_atendida BOOLEAN DEFAULT 0,
            usuario_que_atendio TEXT,
            FOREIGN KEY(egreso_id) REFERENCES Egresos(id)
        )
        ''')
        print("  ✅ Tabla HistorialAlertas verificada")
        
        conn.commit()
        print("\n🎉 ¡Migración completada exitosamente!")
        print("\nAhora puedes ejecutar: python SISTEMA_CONTABLE/MODULOS/panel_control/app.py")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrar_base_datos()