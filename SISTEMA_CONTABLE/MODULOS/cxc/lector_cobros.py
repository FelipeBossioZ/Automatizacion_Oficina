
import pandas as pd
import sqlite3

def leer_y_poblar_clientes(ruta_excel):
    """
    Lee el archivo Excel de cobros, extrae la información de clientes
    y la inserta en la base de datos.
    """
    try:
        # Omitimos las primeras filas que no contienen datos de clientes
        df = pd.read_excel(ruta_excel, header=None, skiprows=6)
        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()

        grupo_familiar_actual = None
        es_titular = False

        # Iteramos sobre cada fila para interpretar la estructura
        for i, row in df.iterrows():
            # Asumimos que un nombre de grupo familiar está en la primera columna y en mayúsculas
            if pd.notna(row[1]) and row[1].isupper() and "FAMILIA" in row[1]:
                grupo_familiar_actual = row[1]
                es_titular = True # El primer miembro después del título de familia es el titular
                continue

            # Identificar una fila de cliente real
            nombre = str(row[1])
            if pd.notna(nombre) and "APELLIDOS Y NOMBRES" not in nombre.upper() and pd.to_numeric(row[7], errors='coerce') > 0:
                nit_cc = row[2]
                telefonos = row[3]
                direccion = row[4]
                ciudad = row[5]
                correo = row[6]

                # Insertar o actualizar cliente
                cursor.execute("SELECT id FROM Clientes WHERE nombre_completo = ?", (nombre,))
                cliente_existente = cursor.fetchone()

                if cliente_existente is None:
                    cursor.execute('''
                        INSERT INTO Clientes (nombre_completo, nit_cc, telefonos, direccion, ciudad, correo_electronico, grupo_familiar, es_titular)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (nombre, nit_cc, telefonos, direccion, ciudad, correo, grupo_familiar_actual, es_titular))
                else:
                    cursor.execute('''
                        UPDATE Clientes SET nit_cc = ?, telefonos = ?, direccion = ?, ciudad = ?, correo_electronico = ?, grupo_familiar = ?, es_titular = ?
                        WHERE id = ?
                    ''', (nit_cc, telefonos, direccion, ciudad, correo, grupo_familiar_actual, es_titular, cliente_existente[0]))

                es_titular = False # Solo el primero es titular

            # Si la fila está vacía, reseteamos el grupo familiar
            if row.isnull().all():
                grupo_familiar_actual = None

        conn.commit()
        print("Clientes cargados/actualizados en la base de datos.")

    except Exception as e:
        print(f"Error al leer el Excel y poblar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Necesitamos descargar el archivo primero
    # Este script se ejecutará desde el orquestador principal
    pass
