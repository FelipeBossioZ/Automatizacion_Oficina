
import pandas as pd
import sqlite3
from datetime import datetime

def migrar_egresos_historicos(ruta_excel):
    """
    Lee el historial de egresos del archivo Excel principal y lo inserta
    en la tabla Egresos de la base de datos.
    """
    try:
        print("Iniciando migración de egresos históricos...")
        # 1. Leer la hoja de códigos para traducir
        df_codigos = pd.read_excel(ruta_excel, sheet_name='Códigos')
        mapa_codigos = pd.Series(df_codigos.iloc[:, 1].values, index=df_codigos.iloc[:, 0]).to_dict()

        # 2. Leer la hoja de egresos, omitiendo encabezados
        df_egresos = pd.read_excel(ruta_excel, sheet_name='EGRESOS DE CAJA', skiprows=7)

        conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
        cursor = conn.cursor()

        gastos_a_insertar = []
        for i, row in df_egresos.iterrows():
            # Validar que la fila parece un registro de gasto válido
            if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]) or pd.isna(row.iloc[6]):
                continue

            fecha = row.iloc[0]
            # Convertir fecha si es necesario (a veces pandas lee fechas como timestamps)
            if isinstance(fecha, datetime):
                fecha = fecha.date()

            codigo_egreso = int(row.iloc[1])
            descripcion = row.iloc[3]
            etiqueta = row.iloc[5]
            monto = pd.to_numeric(row.iloc[6], errors='coerce')

            # Traducir código a categoría
            categoria = mapa_codigos.get(codigo_egreso, 'Categoría Desconocida')

            # Asumimos que todos los gastos históricos ya están 'Pagados'
            estado = 'Pagado'

            if pd.notna(monto):
                gastos_a_insertar.append((
                    str(descripcion),
                    monto,
                    str(fecha), # Fecha de vencimiento es la misma fecha del gasto para datos históricos
                    str(categoria),
                    str(etiqueta),
                    estado
                ))

        # 3. Insertar todos los gastos en la base de datos
        cursor.executemany('''
            INSERT INTO Egresos (descripcion, monto, fecha_vencimiento, categoria, etiqueta, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', gastos_a_insertar)

        conn.commit()
        print(f"¡Migración completada! Se han insertado {len(gastos_a_insertar)} registros de egresos.")

    except Exception as e:
        print(f"Error durante la migración: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrar_egresos_historicos('MANEJO_OFICINA.xlsx')
