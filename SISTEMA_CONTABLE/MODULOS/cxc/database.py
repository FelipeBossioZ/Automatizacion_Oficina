
import sqlite3

def inicializar_bd():
    """Crea y configura las tablas iniciales en la base de datos."""
    try:
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()

        # --- Tabla de Clientes ---
        # Almacena información persistente de cada cliente.
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

        # --- Tabla de Cuentas de Cobro ---
        # Almacena cada instancia de una cuenta de cobro generada.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CuentasCobro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            numero_cxc TEXT NOT NULL UNIQUE,
            valor REAL NOT NULL,
            fecha_emision DATE,
            estado TEXT DEFAULT 'Pendiente',  -- Pendiente, Pagada, Vencida
            ruta_pdf TEXT,
            FOREIGN KEY(cliente_id) REFERENCES Clientes(id)
        )
        ''')

        # --- Tabla de Egresos ---
        # Almacena todos los gastos fijos y variables.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha_vencimiento DATE,
            categoria TEXT,
            etiqueta TEXT, -- OFICINA o GTFF
            estado TEXT DEFAULT 'Pendiente' -- Pendiente, Pagado
        )
        ''')

        conn.commit()
        print("Base de datos inicializada correctamente.")

    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    inicializar_bd()
