import sqlite3
from datetime import datetime

def migrar_sistema_templates():
    """
    Crea las tablas necesarias para el sistema de templates y categorías dinámicas.
    """
    try:
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()
        
        print("=" * 60)
        print("MIGRACIÓN: Sistema de Templates de Presupuestos")
        print("=" * 60)
        
        # ============================================
        # TABLA 1: Templates de Presupuestos
        # ============================================
        print("\n1. Creando tabla PresupuestosTemplates...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS PresupuestosTemplates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            etiqueta TEXT NOT NULL,
            monto_base REAL NOT NULL,
            monto_febrero REAL,
            monto_junio REAL,
            monto_diciembre REAL,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observaciones TEXT,
            UNIQUE(categoria, etiqueta)
        )
        ''')
        print("   ✅ Tabla PresupuestosTemplates creada")
        
        # ============================================
        # TABLA 2: Categorías Dinámicas
        # ============================================
        print("\n2. Creando tabla Categorias...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            color TEXT DEFAULT '#667eea',
            activa BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            orden INTEGER DEFAULT 0
        )
        ''')
        print("   ✅ Tabla Categorias creada")
        
        # Insertar categorías por defecto
        categorias_default = [
            ('Nómina', 'Salarios y prestaciones sociales', '#4299e1', 1),
            ('Arriendo', 'Alquiler de oficina o local', '#48bb78', 2),
            ('Servicios', 'Agua, luz, gas', '#ed8936', 3),
            ('Internet', 'Conexión a internet y telefonía', '#9f7aea', 4),
            ('Suscripciones', 'Software, plataformas, servicios', '#38b2ac', 5),
            ('Mantenimiento', 'Reparaciones y mantenimiento', '#d69e2e', 6),
            ('Cafetería', 'Alimentos y bebidas', '#f56565', 7),
            ('Impuestos', 'Impuestos y contribuciones', '#e53e3e', 8),
            ('Otros', 'Gastos varios', '#718096', 99)
        ]
        
        for nombre, desc, color, orden in categorias_default:
            cursor.execute('''
                INSERT OR IGNORE INTO Categorias (nombre, descripcion, color, orden)
                VALUES (?, ?, ?, ?)
            ''', (nombre, desc, color, orden))
        
        print("   ✅ Categorías por defecto insertadas")
        
        # ============================================
        # TABLA 3: Registro de Cambios en Templates
        # ============================================
        print("\n3. Creando tabla HistorialTemplates...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS HistorialTemplates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            accion TEXT,
            usuario TEXT,
            valores_anteriores TEXT,
            valores_nuevos TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(template_id) REFERENCES PresupuestosTemplates(id)
        )
        ''')
        print("   ✅ Tabla HistorialTemplates creada")
        
        # ============================================
        # TABLA 4: Agregar campo a Presupuestos
        # ============================================
        print("\n4. Verificando campos en tabla Presupuestos...")
        
        # Verificar si ya existe el campo template_id
        cursor.execute("PRAGMA table_info(Presupuestos)")
        columnas_presupuestos = [col[1] for col in cursor.fetchall()]
        
        if 'template_id' not in columnas_presupuestos:
            cursor.execute('''
                ALTER TABLE Presupuestos 
                ADD COLUMN template_id INTEGER
            ''')
            print("   ✅ Campo 'template_id' agregado a Presupuestos")
        else:
            print("   ⏭️  Campo 'template_id' ya existe")
        
        if 'creado_automaticamente' not in columnas_presupuestos:
            cursor.execute('''
                ALTER TABLE Presupuestos 
                ADD COLUMN creado_automaticamente BOOLEAN DEFAULT 0
            ''')
            print("   ✅ Campo 'creado_automaticamente' agregado")
        else:
            print("   ⏭️  Campo 'creado_automaticamente' ya existe")
        
        # ============================================
        # TABLA 5: Log de Creación Automática
        # ============================================
        print("\n5. Creando tabla LogCreacionPresupuestos...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS LogCreacionPresupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            cantidad_creados INTEGER DEFAULT 0,
            fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detalles TEXT
        )
        ''')
        print("   ✅ Tabla LogCreacionPresupuestos creada")
        
        # ============================================
        # TABLA 6: Alertas de Tendencias
        # ============================================
        print("\n6. Creando tabla AlertasTendencias...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS AlertasTendencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            etiqueta TEXT NOT NULL,
            tipo_alerta TEXT NOT NULL,
            severidad TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            meses_consecutivos INTEGER DEFAULT 1,
            porcentaje_promedio REAL,
            fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_resolucion TIMESTAMP,
            activa BOOLEAN DEFAULT 1
        )
        ''')
        print("   ✅ Tabla AlertasTendencias creada")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nResumen de tablas creadas:")
        print("  1. PresupuestosTemplates")
        print("  2. Categorias (con 9 categorías por defecto)")
        print("  3. HistorialTemplates")
        print("  4. LogCreacionPresupuestos")
        print("  5. AlertasTendencias")
        print("  6. Presupuestos (campos adicionales)")
        print("\n🎉 El sistema está listo para usar templates!")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrar_sistema_templates()