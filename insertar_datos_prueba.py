
import sqlite3
from datetime import date, timedelta

def insertar_gastos_prueba():
    """Inserta algunos gastos de ejemplo en la base de datos para probar el dashboard."""
    conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
    cursor = conn.cursor()

    hoy = date.today()
    gastos = [
        ('Pago Arriendo Oficina', 2500000, (hoy + timedelta(days=5)).strftime('%Y-%m-%d'), 'Arriendo', 'OFICINA', 'Pendiente'),
        ('Suscripción Software Contable', 150000, (hoy - timedelta(days=2)).strftime('%Y-%m-%d'), 'Suscripciones', 'OFICINA', 'Pendiente'),
        ('Nómina Empleado 1', 1800000, (hoy + timedelta(days=14)).strftime('%Y-%m-%d'), 'Nómina', 'OFICINA', 'Pendiente'),
        ('Servicios Públicos', 350000, (hoy + timedelta(days=25)).strftime('%Y-%m-%d'), 'Servicios', 'OFICINA', 'Pendiente'),
        ('Gasto Personal Dueño', 500000, (hoy + timedelta(days=10)).strftime('%Y-%m-%d'), 'Gastos Personales', 'GTFF', 'Pendiente')
    ]

    cursor.executemany('''
        INSERT INTO Egresos (descripcion, monto, fecha_vencimiento, categoria, etiqueta, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', gastos)

    conn.commit()
    conn.close()
    print(f"{len(gastos)} gastos de prueba insertados en la base de datos.")

if __name__ == '__main__':
    insertar_gastos_prueba()
