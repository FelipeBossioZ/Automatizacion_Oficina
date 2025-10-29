
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return conn

@app.route('/')
def index():
    # Por ahora redirigimos a la página de gastos. En el futuro, será el dashboard de alertas.
    return redirect(url_for('gestion_gastos'))

@app.route('/gastos')
def gestion_gastos():
    conn = get_db()
    gastos = conn.execute('SELECT * FROM Egresos ORDER BY fecha_vencimiento ASC').fetchall()
    conn.close()
    return render_template('gastos.html', gastos=gastos)

@app.route('/gasto', methods=['POST'])
def anadir_gasto():
    descripcion = request.form['descripcion']
    monto = request.form['monto']
    fecha_vencimiento = request.form['fecha_vencimiento']
    categoria = request.form['categoria']
    etiqueta = request.form['etiqueta']

    conn = get_db()
    conn.execute('''
        INSERT INTO Egresos (descripcion, monto, fecha_vencimiento, categoria, etiqueta)
        VALUES (?, ?, ?, ?, ?)
    ''', (descripcion, monto, fecha_vencimiento, categoria, etiqueta))
    conn.commit()
    conn.close()
    return redirect(url_for('gestion_gastos'))

@app.route('/gasto/pagar/<int:gasto_id>', methods=['POST'])
def pagar_gasto(gasto_id):
    conn = get_db()
    conn.execute("UPDATE Egresos SET estado = 'Pagado' WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gestion_gastos'))

if __name__ == '__main__':
    # El host '0.0.0.0' es crucial para que sea accesible desde otros PCs en la red local
    app.run(host='0.0.0.0', port=8000, debug=True)
