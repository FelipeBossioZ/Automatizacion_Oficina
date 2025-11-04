from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
import sqlite3
from datetime import datetime, timedelta, date
import json
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, PieChart, Reference


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala'
DATABASE = 'SISTEMA_CONTABLE/DATOS/contabilidad.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def actualizar_presupuestos_mes(mes, anio):
    """Actualiza los montos gastados de todos los presupuestos del mes especificado."""
    conn = get_db()
    presupuestos = conn.execute('''
        SELECT id, categoria, etiqueta FROM Presupuestos 
        WHERE mes = ? AND anio = ?
    ''', (mes, anio)).fetchall()
    
    for presupuesto in presupuestos:
        resultado = conn.execute('''
            SELECT COALESCE(SUM(monto), 0) as total
            FROM Egresos
            WHERE categoria = ? 
            AND etiqueta = ? 
            AND estado = 'Pagado'
            AND strftime('%m', fecha_vencimiento) = ?
            AND strftime('%Y', fecha_vencimiento) = ?
        ''', (presupuesto['categoria'], presupuesto['etiqueta'], 
              f"{mes:02d}", str(anio))).fetchone()
        
        monto_gastado = resultado['total']
        conn.execute('UPDATE Presupuestos SET monto_gastado = ? WHERE id = ?', 
                    (monto_gastado, presupuesto['id']))
    
    conn.commit()
    conn.close()

def detectar_alertas_tendencias():
    """Detecta tendencias de exceso en presupuestos (3 meses consecutivos >10%)"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    try:
        # Obtener todas las categorías únicas de presupuestos
        categorias = conn.execute('''
            SELECT DISTINCT categoria, etiqueta 
            FROM Presupuestos
            WHERE monto_presupuestado > 0
        ''').fetchall()
        
        mes_actual = datetime.now()
        
        for cat in categorias:
            # Obtener últimos 3 meses de esta categoría
            meses_analizar = []
            for i in range(3):
                fecha = mes_actual - timedelta(days=30*i)
                mes = fecha.month
                anio = fecha.year
                
                presupuesto = conn.execute('''
                    SELECT * FROM Presupuestos 
                    WHERE categoria = ? AND etiqueta = ? 
                    AND mes = ? AND anio = ?
                ''', (cat['categoria'], cat['etiqueta'], mes, anio)).fetchone()
                
                if presupuesto and presupuesto['monto_presupuestado'] > 0:
                    porcentaje = (presupuesto['monto_gastado'] / presupuesto['monto_presupuestado']) * 100
                    meses_analizar.append({
                        'mes': mes,
                        'anio': anio,
                        'porcentaje': porcentaje,
                        'exceso': porcentaje - 100 if porcentaje > 100 else 0,
                        'presupuestado': presupuesto['monto_presupuestado'],
                        'gastado': presupuesto['monto_gastado']
                    })
            
            # Verificar si hay 3 meses consecutivos con exceso >10%
            if len(meses_analizar) == 3:
                todos_exceden = all(m['porcentaje'] > 110 for m in meses_analizar)
                
                if todos_exceden:
                    promedio_presupuestado = sum(m['presupuestado'] for m in meses_analizar) / 3
                    promedio_gastado = sum(m['gastado'] for m in meses_analizar) / 3
                    porcentaje_exceso = ((promedio_gastado - promedio_presupuestado) / promedio_presupuestado) * 100
                    
                    # Verificar si ya existe esta alerta
                    existe = conn.execute('''
                        SELECT id FROM AlertasTendencias 
                        WHERE categoria = ? AND etiqueta = ? AND activa = 1
                    ''', (cat['categoria'], cat['etiqueta'])).fetchone()
                    
                    if not existe:
                        conn.execute('''
                            INSERT INTO AlertasTendencias 
                            (categoria, etiqueta, tipo_tendencia, meses_consecutivos, 
                             porcentaje_exceso, promedio_presupuestado, promedio_gastado)
                            VALUES (?, ?, 'EXCESO', 3, ?, ?, ?)
                        ''', (cat['categoria'], cat['etiqueta'], porcentaje_exceso, 
                              promedio_presupuestado, promedio_gastado))
                        conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Error en detectar_alertas_tendencias: {e}")
        conn.close()

# ===============================================
# DASHBOARD PRINCIPAL
# ===============================================

@app.route('/')
def dashboard():
    conn = get_db()
    today = date.today()
    
    config = dict(conn.execute('SELECT clave, valor FROM Configuracion').fetchall())
    dias_anticipada = int(config.get('dias_alerta_anticipada', 7))
    dias_critica = int(config.get('dias_alerta_critica', 3))
    
    alertas = {
        'vencidos': [], 'hoy': [], 'criticos': [], 
        'importantes': [], 'normales': [], 'descuentos_por_vencer': []
    }
    
    query = """
        SELECT id, descripcion, monto, fecha_vencimiento, categoria, etiqueta,
               tiene_descuento, fecha_limite_descuento, porcentaje_descuento, monto_descuento
        FROM Egresos
        WHERE estado = 'Pendiente' 
        AND date(fecha_vencimiento) <= date('now', '+30 days')
        ORDER BY fecha_vencimiento ASC
    """
    gastos_pendientes = conn.execute(query).fetchall()
    
    for gasto in gastos_pendientes:
        fecha_venc = datetime.strptime(gasto['fecha_vencimiento'], '%Y-%m-%d').date()
        dias_restantes = (fecha_venc - today).days
        
        descuento_perdido = 0
        if gasto['tiene_descuento'] and gasto['fecha_limite_descuento']:
            fecha_desc = datetime.strptime(gasto['fecha_limite_descuento'], '%Y-%m-%d').date()
            dias_descuento = (fecha_desc - today).days
            if dias_descuento < 0:
                descuento_perdido = gasto['monto_descuento']
        
        alerta_obj = {
            'id': gasto['id'], 'descripcion': gasto['descripcion'],
            'monto': gasto['monto'], 'categoria': gasto['categoria'],
            'etiqueta': gasto['etiqueta'], 'fecha_vencimiento': fecha_venc.strftime('%Y-%m-%d'),
            'dias_restantes': dias_restantes, 'descuento_perdido': descuento_perdido,
            'tiene_descuento': gasto['tiene_descuento'],
            'fecha_limite_descuento': gasto['fecha_limite_descuento']
        }
        
        if dias_restantes < 0:
            alertas['vencidos'].append(alerta_obj)
        elif dias_restantes == 0:
            alertas['hoy'].append(alerta_obj)
        elif dias_restantes <= dias_critica:
            alertas['criticos'].append(alerta_obj)
        elif dias_restantes <= dias_anticipada:
            alertas['importantes'].append(alerta_obj)
        else:
            alertas['normales'].append(alerta_obj)
        
        if gasto['tiene_descuento'] and gasto['fecha_limite_descuento']:
            fecha_desc = datetime.strptime(gasto['fecha_limite_descuento'], '%Y-%m-%d').date()
            dias_desc = (fecha_desc - today).days
            if 0 <= dias_desc <= 3:
                alertas['descuentos_por_vencer'].append({
                    **alerta_obj,
                    'dias_restantes_descuento': dias_desc,
                    'monto_ahorro': gasto['monto_descuento']
                })
    
    mes_actual = today.month
    anio_actual = today.year
    
    stats_query = """
        SELECT etiqueta, COUNT(*) as cantidad, SUM(monto) as total,
               SUM(CASE WHEN estado = 'Pagado' THEN monto ELSE 0 END) as pagado,
               SUM(CASE WHEN estado = 'Pendiente' THEN monto ELSE 0 END) as pendiente
        FROM Egresos
        WHERE strftime('%m', fecha_vencimiento) = ? AND strftime('%Y', fecha_vencimiento) = ?
        GROUP BY etiqueta
    """
    stats = conn.execute(stats_query, (f"{mes_actual:02d}", str(anio_actual))).fetchall()
    total_pendiente_mes = sum([s['pendiente'] for s in stats])
    
    presupuestos_excedidos = conn.execute('''
        SELECT categoria, etiqueta, monto_presupuestado, monto_gastado
        FROM Presupuestos
        WHERE mes = ? AND anio = ? AND monto_gastado > monto_presupuestado
    ''', (mes_actual, anio_actual)).fetchall()
    
    tareas_urgentes = conn.execute('''
        SELECT descripcion, fecha_vencimiento, prioridad, categoria, cliente_relacionado
        FROM Tareas
        WHERE estado = 'Pendiente' 
        AND date(fecha_vencimiento) <= date('now', '+7 days')
        ORDER BY 
            CASE prioridad 
                WHEN 'Alta' THEN 1 
                WHEN 'Media' THEN 2 
                WHEN 'Baja' THEN 3 
            END,
            fecha_vencimiento ASC
        LIMIT 10
    ''').fetchall()
    
    # Alertas de tendencias activas
    alertas_tendencias = conn.execute('''
        SELECT * FROM AlertasTendencias
        WHERE activa = 1
        ORDER BY severidad DESC, fecha_deteccion DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         alertas=alertas, stats=stats,
                         total_pendiente_mes=total_pendiente_mes,
                         presupuestos_excedidos=presupuestos_excedidos,
                         tareas_urgentes=tareas_urgentes,
                         alertas_tendencias=alertas_tendencias,
                         fecha_actual=today.strftime('%d de %B de %Y'))

# ===============================================
# GESTIÓN DE GASTOS
# ===============================================

@app.route('/gastos')
def gestion_gastos():
    conn = get_db()
    filtro_etiqueta = request.args.get('etiqueta', 'TODOS')
    filtro_estado = request.args.get('estado', 'TODOS')
    filtro_mes = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    
    query = 'SELECT * FROM Egresos WHERE 1=1'
    params = []
    
    if filtro_etiqueta != 'TODOS':
        query += ' AND etiqueta = ?'
        params.append(filtro_etiqueta)
    
    if filtro_estado != 'TODOS':
        query += ' AND estado = ?'
        params.append(filtro_estado)
    
    if filtro_mes != 'TODOS':
        query += " AND strftime('%Y-%m', fecha_vencimiento) = ?"
        params.append(filtro_mes)
    
    query += ' ORDER BY fecha_vencimiento DESC'
    gastos = conn.execute(query, params).fetchall()
    
    total_general = sum([g['monto'] for g in gastos])
    total_pendiente = sum([g['monto'] for g in gastos if g['estado'] == 'Pendiente'])
    total_pagado = sum([g['monto'] for g in gastos if g['estado'] == 'Pagado'])
    
    # Obtener categorías activas para el formulario
    categorias = conn.execute('SELECT nombre FROM Categorias WHERE activa = 1 ORDER BY orden').fetchall()
    
    conn.close()
    
    return render_template('gastos.html', gastos=gastos,
                         total_general=total_general,
                         total_pendiente=total_pendiente,
                         total_pagado=total_pagado,
                         filtro_etiqueta=filtro_etiqueta,
                         filtro_estado=filtro_estado,
                         filtro_mes=filtro_mes,
                         categorias=categorias)

@app.route('/gasto', methods=['POST'])
def anadir_gasto():
    descripcion = request.form['descripcion']
    monto = float(request.form['monto'])
    fecha_vencimiento = request.form['fecha_vencimiento']
    categoria = request.form['categoria']
    etiqueta = request.form['etiqueta']
    
    tiene_descuento = 1 if request.form.get('tiene_descuento') else 0
    fecha_limite_descuento = request.form.get('fecha_limite_descuento') or None
    porcentaje_str = request.form.get('porcentaje_descuento', '0').strip()
    porcentaje_descuento = float(porcentaje_str) if porcentaje_str else 0.0
    monto_descuento = monto * (porcentaje_descuento / 100) if tiene_descuento else 0
    
    es_recurrente = 1 if request.form.get('es_recurrente') else 0
    frecuencia = request.form.get('frecuencia') if es_recurrente else None
    
    conn = get_db()
    conn.execute('''
        INSERT INTO Egresos (
            descripcion, monto, fecha_vencimiento, categoria, etiqueta,
            tiene_descuento, fecha_limite_descuento, porcentaje_descuento, monto_descuento,
            es_recurrente, frecuencia
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (descripcion, monto, fecha_vencimiento, categoria, etiqueta,
          tiene_descuento, fecha_limite_descuento, porcentaje_descuento, monto_descuento,
          es_recurrente, frecuencia))
    conn.commit()
    conn.close()
    
    flash(f'✅ Gasto "{descripcion}" añadido correctamente', 'success')
    return redirect(url_for('gestion_gastos'))

@app.route('/gasto/pagar/<int:gasto_id>', methods=['POST'])
def pagar_gasto(gasto_id):
    usuario = request.form.get('usuario', 'Usuario Anónimo')
    conn = get_db()
    gasto = conn.execute('SELECT * FROM Egresos WHERE id = ?', (gasto_id,)).fetchone()
    
    if not gasto:
        flash('❌ Gasto no encontrado', 'error')
        return redirect(url_for('gestion_gastos'))
    
    fecha_venc = datetime.strptime(gasto['fecha_vencimiento'], '%Y-%m-%d')
    mes, anio = fecha_venc.month, fecha_venc.year
    
    conn.execute("UPDATE Egresos SET estado = 'Pagado', fecha_pago = CURRENT_TIMESTAMP, usuario_que_pago = ? WHERE id = ?", 
                (usuario, gasto_id))
    conn.commit()
    conn.close()
    
    actualizar_presupuestos_mes(mes, anio)
    
    if gasto['es_recurrente']:
        from dateutil.relativedelta import relativedelta
        freq_map = {'Mensual': 1, 'Trimestral': 3, 'Semestral': 6, 'Anual': 12}
        meses = freq_map.get(gasto['frecuencia'], 1)
        proxima_fecha = fecha_venc + relativedelta(months=meses)
        
        fecha_limite_desc = None
        if gasto['tiene_descuento'] and gasto['fecha_limite_descuento']:
            fecha_desc_original = datetime.strptime(gasto['fecha_limite_descuento'], '%Y-%m-%d')
            dias_diferencia = (fecha_venc - fecha_desc_original).days
            fecha_limite_desc = proxima_fecha - relativedelta(days=dias_diferencia)
        
        conn = get_db()
        conn.execute('''
            INSERT INTO Egresos (descripcion, monto, fecha_vencimiento, categoria, etiqueta,
                                tiene_descuento, fecha_limite_descuento, porcentaje_descuento, monto_descuento,
                                es_recurrente, frecuencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (gasto['descripcion'], gasto['monto'], proxima_fecha.strftime('%Y-%m-%d'),
              gasto['categoria'], gasto['etiqueta'], gasto['tiene_descuento'],
              fecha_limite_desc.strftime('%Y-%m-%d') if fecha_limite_desc else None,
              gasto['porcentaje_descuento'], gasto['monto_descuento'], 1, gasto['frecuencia']))
        conn.commit()
        conn.close()
        flash(f'✅ Gasto pagado. Próximo vencimiento: {proxima_fecha.strftime("%Y-%m-%d")}', 'success')
    else:
        flash('✅ Gasto pagado. Presupuestos actualizados.', 'success')
    
    return redirect(url_for('gestion_gastos'))

@app.route('/gasto/eliminar/<int:gasto_id>', methods=['POST'])
def eliminar_gasto(gasto_id):
    conn = get_db()
    conn.execute("DELETE FROM Egresos WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()
    flash('🗑️ Gasto eliminado', 'warning')
    return redirect(url_for('gestion_gastos'))

@app.route('/gasto/editar/<int:gasto_id>', methods=['GET'])
def editar_gasto_form(gasto_id):
    conn = get_db()
    gasto = conn.execute('SELECT * FROM Egresos WHERE id = ?', (gasto_id,)).fetchone()
    categorias = conn.execute('SELECT nombre FROM Categorias WHERE activa = 1 ORDER BY orden').fetchall()
    conn.close()
    
    if not gasto:
        flash('❌ Gasto no encontrado', 'error')
        return redirect(url_for('gestion_gastos'))
    
    return render_template('editar_gasto.html', gasto=gasto, categorias=categorias)

@app.route('/gasto/editar/<int:gasto_id>', methods=['POST'])
def editar_gasto(gasto_id):
    descripcion = request.form['descripcion']
    monto = float(request.form['monto'])
    fecha_vencimiento = request.form['fecha_vencimiento']
    categoria = request.form['categoria']
    etiqueta = request.form['etiqueta']
    
    tiene_descuento = 1 if request.form.get('tiene_descuento') else 0
    fecha_limite_descuento = request.form.get('fecha_limite_descuento') or None
    porcentaje_str = request.form.get('porcentaje_descuento', '0').strip()
    porcentaje_descuento = float(porcentaje_str) if porcentaje_str else 0.0
    monto_descuento = monto * (porcentaje_descuento / 100) if tiene_descuento else 0
    
    es_recurrente = 1 if request.form.get('es_recurrente') else 0
    frecuencia = request.form.get('frecuencia') if es_recurrente else None
    
    conn = get_db()
    conn.execute('''
        UPDATE Egresos SET descripcion = ?, monto = ?, fecha_vencimiento = ?, 
        categoria = ?, etiqueta = ?, tiene_descuento = ?, fecha_limite_descuento = ?,
        porcentaje_descuento = ?, monto_descuento = ?, es_recurrente = ?, frecuencia = ?
        WHERE id = ?
    ''', (descripcion, monto, fecha_vencimiento, categoria, etiqueta,
          tiene_descuento, fecha_limite_descuento, porcentaje_descuento, monto_descuento,
          es_recurrente, frecuencia, gasto_id))
    conn.commit()
    conn.close()
    
    flash('✅ Gasto actualizado correctamente', 'success')
    return redirect(url_for('gestion_gastos'))

# ===============================================
# PRESUPUESTOS - MES ACTUAL
# ===============================================

@app.route('/presupuestos')
def presupuestos():
    conn = get_db()
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    
    # Pestaña activa
    tab = request.args.get('tab', 'mes_actual')
    
    # Actualizar presupuestos antes de mostrar
    actualizar_presupuestos_mes(mes_actual, anio_actual)
    detectar_alertas_tendencias()
    
    # Presupuestos del mes actual
    presupuestos_mes = conn.execute('''
        SELECT * FROM Presupuestos 
        WHERE mes = ? AND anio = ?
        ORDER BY categoria
    ''', (mes_actual, anio_actual)).fetchall()
    
    # Gastos reales del mes
    gastos_reales = conn.execute('''
        SELECT categoria, etiqueta, SUM(monto) as total
        FROM Egresos
        WHERE strftime('%m', fecha_vencimiento) = ? 
        AND strftime('%Y', fecha_vencimiento) = ?
        AND estado = 'Pagado'
        GROUP BY categoria, etiqueta
    ''', (f"{mes_actual:02d}", str(anio_actual))).fetchall()
    
    # Templates activos
    templates = conn.execute('''
        SELECT * FROM PresupuestosTemplates
        WHERE activo = 1
        ORDER BY categoria
    ''').fetchall()
    
    # Categorías ACTIVAS para formularios
    categorias = conn.execute('SELECT * FROM Categorias WHERE activa = 1 ORDER BY orden, nombre').fetchall()

    # TODAS las categorías para gestión
    todas_categorias = conn.execute('SELECT * FROM Categorias ORDER BY orden, nombre').fetchall()
    
    # Alertas de tendencias
    alertas_tendencias = conn.execute('''
        SELECT * FROM AlertasTendencias
        WHERE activa = 1
        ORDER BY severidad DESC, fecha_deteccion DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('presupuestos.html',
                            presupuestos=presupuestos_mes,
                            gastos_reales=gastos_reales,
                            templates=templates,
                            categorias=categorias,
                            todas_categorias=todas_categorias,
                            alertas_tendencias=alertas_tendencias,
                            mes_actual=mes_actual,
                            anio_actual=anio_actual,
                            tab=tab)

@app.route('/presupuesto/crear', methods=['POST'])
def crear_presupuesto():
    mes = int(request.form['mes'])
    anio = int(request.form['anio'])
    categoria = request.form['categoria']
    etiqueta = request.form['etiqueta']
    monto_presupuestado = float(request.form['monto'])
    
    conn = get_db()
    try:
        # Calcular monto ya gastado
        resultado = conn.execute('''
            SELECT COALESCE(SUM(monto), 0) as total
            FROM Egresos
            WHERE categoria = ? AND etiqueta = ? AND estado = 'Pagado'
            AND strftime('%m', fecha_vencimiento) = ? AND strftime('%Y', fecha_vencimiento) = ?
        ''', (categoria, etiqueta, f"{mes:02d}", str(anio))).fetchone()
        
        monto_gastado = resultado['total']
        
        conn.execute('''
            INSERT INTO Presupuestos (mes, anio, categoria, etiqueta, monto_presupuestado, monto_gastado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mes, anio, categoria, etiqueta, monto_presupuestado, monto_gastado))
        conn.commit()
        flash(f'✅ Presupuesto creado. Gastado: ${monto_gastado:,.0f} de ${monto_presupuestado:,.0f}', 'success')
    except sqlite3.IntegrityError:
        flash('⚠️ Ya existe un presupuesto para esa categoría en ese mes', 'warning')
    finally:
        conn.close()
    
    return redirect(url_for('presupuestos'))

@app.route('/presupuesto/editar/<int:presupuesto_id>', methods=['GET'])
def editar_presupuesto_form(presupuesto_id):
    conn = get_db()
    presupuesto = conn.execute('SELECT * FROM Presupuestos WHERE id = ?', (presupuesto_id,)).fetchone()
    categorias = conn.execute('SELECT nombre FROM Categorias WHERE activa = 1 ORDER BY orden').fetchall()
    conn.close()
    
    if not presupuesto:
        flash('❌ Presupuesto no encontrado', 'error')
        return redirect(url_for('presupuestos'))
    
    # Solo permitir editar mes actual
    if presupuesto['mes'] != datetime.now().month or presupuesto['anio'] != datetime.now().year:
        flash('⚠️ Solo puedes editar presupuestos del mes actual', 'warning')
        return redirect(url_for('presupuestos'))
    
    return render_template('editar_presupuesto.html', presupuesto=presupuesto, categorias=categorias)

@app.route('/presupuesto/editar/<int:presupuesto_id>', methods=['POST'])
def editar_presupuesto(presupuesto_id):
    monto_presupuestado = float(request.form['monto'])
    
    conn = get_db()
    presupuesto = conn.execute('SELECT * FROM Presupuestos WHERE id = ?', (presupuesto_id,)).fetchone()
    
    if presupuesto['mes'] != datetime.now().month or presupuesto['anio'] != datetime.now().year:
        flash('⚠️ Solo puedes editar presupuestos del mes actual', 'warning')
        return redirect(url_for('presupuestos'))
    
    conn.execute('UPDATE Presupuestos SET monto_presupuestado = ? WHERE id = ?', 
                (monto_presupuestado, presupuesto_id))
    conn.commit()
    conn.close()
    
    flash('✅ Presupuesto actualizado correctamente', 'success')
    return redirect(url_for('presupuestos'))

@app.route('/presupuesto/eliminar/<int:presupuesto_id>', methods=['POST'])
def eliminar_presupuesto(presupuesto_id):
    pin = request.form.get('pin', '')
    
    conn = get_db()
    presupuesto = conn.execute('SELECT * FROM Presupuestos WHERE id = ?', (presupuesto_id,)).fetchone()
    
    if not presupuesto:
        flash('❌ Presupuesto no encontrado', 'error')
        return redirect(url_for('presupuestos'))
    
    # Si tiene gastos, requiere PIN
    if presupuesto['monto_gastado'] > 0:
        if pin != '0000':
            flash('❌ PIN incorrecto. No se eliminó el presupuesto.', 'error')
            return redirect(url_for('presupuestos'))
    
    conn.execute('DELETE FROM Presupuestos WHERE id = ?', (presupuesto_id,))
    conn.commit()
    conn.close()
    
    flash('🗑️ Presupuesto eliminado correctamente', 'success')
    return redirect(url_for('presupuestos'))

# ===============================================
# TEMPLATES DE PRESUPUESTOS
# ===============================================

@app.route('/template/crear', methods=['POST'])
def crear_template():
    categoria = request.form['categoria']
    etiqueta = request.form['etiqueta']
    monto_base = float(request.form['monto_base'])
    
    # Montos especiales (opcionales)
    monto_febrero_str = request.form.get('monto_febrero', '').strip()
    monto_junio_str = request.form.get('monto_junio', '').strip()
    monto_diciembre_str = request.form.get('monto_diciembre', '').strip()
    
    monto_febrero = float(monto_febrero_str) if monto_febrero_str else None
    monto_junio = float(monto_junio_str) if monto_junio_str else None
    monto_diciembre = float(monto_diciembre_str) if monto_diciembre_str else None
    
    observaciones = request.form.get('observaciones', '')
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO PresupuestosTemplates 
            (categoria, etiqueta, monto_base, monto_febrero, monto_junio, monto_diciembre, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (categoria, etiqueta, monto_base, monto_febrero, monto_junio, monto_diciembre, observaciones))
        conn.commit()
        flash('✅ Template creado correctamente', 'success')
    except sqlite3.IntegrityError:
        flash('⚠️ Ya existe un template para esa categoría y etiqueta', 'warning')
    finally:
        conn.close()
    
    return redirect(url_for('presupuestos', tab='templates'))

@app.route('/template/editar/<int:template_id>', methods=['GET'])
def editar_template_form(template_id):
    conn = get_db()
    template = conn.execute('SELECT * FROM PresupuestosTemplates WHERE id = ?', (template_id,)).fetchone()
    categorias = conn.execute('SELECT nombre FROM Categorias WHERE activa = 1 ORDER BY orden').fetchall()
    conn.close()
    
    if not template:
        flash('❌ Template no encontrado', 'error')
        return redirect(url_for('presupuestos', tab='templates'))
    
    return render_template('editar_template.html', template=template, categorias=categorias)

@app.route('/template/editar/<int:template_id>', methods=['POST'])
def editar_template(template_id):
    monto_base = float(request.form['monto_base'])
    
    monto_febrero_str = request.form.get('monto_febrero', '').strip()
    monto_junio_str = request.form.get('monto_junio', '').strip()
    monto_diciembre_str = request.form.get('monto_diciembre', '').strip()
    
    monto_febrero = float(monto_febrero_str) if monto_febrero_str else None
    monto_junio = float(monto_junio_str) if monto_junio_str else None
    monto_diciembre = float(monto_diciembre_str) if monto_diciembre_str else None
    
    observaciones = request.form.get('observaciones', '')
    
    conn = get_db()
    conn.execute('''
        UPDATE PresupuestosTemplates 
        SET monto_base = ?, monto_febrero = ?, monto_junio = ?, monto_diciembre = ?,
            observaciones = ?, fecha_modificacion = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (monto_base, monto_febrero, monto_junio, monto_diciembre, observaciones, template_id))
    conn.commit()
    conn.close()
    
    flash('✅ Template actualizado. Los cambios se aplicarán desde el próximo mes.', 'success')
    return redirect(url_for('presupuestos', tab='templates'))

@app.route('/template/pausar/<int:template_id>', methods=['POST'])
def pausar_template(template_id):
    conn = get_db()
    template = conn.execute('SELECT activo FROM PresupuestosTemplates WHERE id = ?', (template_id,)).fetchone()
    
    nuevo_estado = 0 if template['activo'] else 1
    conn.execute('UPDATE PresupuestosTemplates SET activo = ? WHERE id = ?', (nuevo_estado, template_id))
    conn.commit()
    conn.close()
    
    mensaje = '⏸️ Template pausado' if nuevo_estado == 0 else '▶️ Template reactivado'
    flash(mensaje, 'success')
    return redirect(url_for('presupuestos', tab='templates'))

@app.route('/template/eliminar/<int:template_id>', methods=['POST'])
def eliminar_template(template_id):
    conn = get_db()
    conn.execute('DELETE FROM PresupuestosTemplates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    
    flash('🗑️ Template eliminado correctamente', 'warning')
    return redirect(url_for('presupuestos', tab='templates'))

# ===============================================
# CATEGORÍAS
# ===============================================

@app.route('/categorias')
def gestionar_categorias():
    conn = get_db()
    categorias = conn.execute('SELECT * FROM Categorias ORDER BY orden, nombre').fetchall()
    conn.close()
    return render_template('categorias.html', categorias=categorias)

@app.route('/categoria/crear', methods=['POST'])
def crear_categoria():
    nombre = request.form['nombre']
    descripcion = request.form.get('descripcion', '')
    color = request.form.get('color', '#667eea')
    
    conn = get_db()
    try:
        # Obtener el siguiente número de orden
        max_orden = conn.execute('SELECT MAX(orden) as max_orden FROM Categorias').fetchone()
        nuevo_orden = (max_orden['max_orden'] or 0) + 1
        
        conn.execute('''
            INSERT INTO Categorias (nombre, descripcion, color, orden)
            VALUES (?, ?, ?, ?)
        ''', (nombre, descripcion, color, nuevo_orden))
        conn.commit()
        flash(f'✅ Categoría "{nombre}" creada correctamente', 'success')
    except sqlite3.IntegrityError:
        flash('⚠️ Ya existe una categoría con ese nombre', 'warning')
    finally:
        conn.close()
    
    return redirect(url_for('gestionar_categorias'))

@app.route('/categoria/editar/<int:categoria_id>', methods=['POST'])
def editar_categoria(categoria_id):
    nombre = request.form['nombre']
    descripcion = request.form.get('descripcion', '')
    color = request.form.get('color', '#667eea')
    
    conn = get_db()
    conn.execute('''
        UPDATE Categorias 
        SET nombre = ?, descripcion = ?, color = ?
        WHERE id = ?
    ''', (nombre, descripcion, color, categoria_id))
    conn.commit()
    conn.close()
    
    flash('✅ Categoría actualizada correctamente', 'success')
    return redirect(url_for('gestionar_categorias'))

@app.route('/categoria/desactivar/<int:categoria_id>', methods=['POST'])
def desactivar_categoria(categoria_id):
    conn = get_db()
    categoria = conn.execute('SELECT activa FROM Categorias WHERE id = ?', (categoria_id,)).fetchone()
    
    nuevo_estado = 0 if categoria['activa'] else 1
    conn.execute('UPDATE Categorias SET activa = ? WHERE id = ?', (nuevo_estado, categoria_id))
    conn.commit()
    conn.close()
    
    mensaje = '⏸️ Categoría desactivada' if nuevo_estado == 0 else '▶️ Categoría reactivada'
    flash(mensaje, 'success')
    return redirect(url_for('presupuestos', tab='categorias'))

# ===============================================
# TAREAS
# ===============================================

@app.route('/tareas')
def tareas():
    conn = get_db()
    filtro_estado = request.args.get('estado', 'Pendiente')
    
    if filtro_estado == 'TODAS':
        tareas_list = conn.execute('SELECT * FROM Tareas ORDER BY fecha_vencimiento ASC').fetchall()
    else:
        tareas_list = conn.execute(
            'SELECT * FROM Tareas WHERE estado = ? ORDER BY fecha_vencimiento ASC',
            (filtro_estado,)
        ).fetchall()
    
    conn.close()
    return render_template('tareas.html', tareas=tareas_list, filtro_estado=filtro_estado)

@app.route('/tarea/crear', methods=['POST'])
def crear_tarea():
    descripcion = request.form['descripcion']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form.get('prioridad', 'Media')
    categoria = request.form.get('categoria', 'Interno')
    cliente_relacionado = request.form.get('cliente_relacionado', '')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO Tareas (descripcion, fecha_vencimiento, prioridad, categoria, cliente_relacionado)
        VALUES (?, ?, ?, ?, ?)
    ''', (descripcion, fecha_vencimiento, prioridad, categoria, cliente_relacionado))
    conn.commit()
    conn.close()
    
    flash('✅ Tarea creada correctamente', 'success')
    return redirect(url_for('tareas'))

@app.route('/tarea/completar/<int:tarea_id>', methods=['POST'])
def completar_tarea(tarea_id):
    conn = get_db()
    conn.execute("UPDATE Tareas SET estado = 'Completada', fecha_completado = CURRENT_TIMESTAMP WHERE id = ?", 
                (tarea_id,))
    conn.commit()
    conn.close()
    
    flash('✅ Tarea completada', 'success')
    return redirect(url_for('tareas'))

# ===============================================
# API Y UTILIDADES
# ===============================================

@app.route('/api/alertas/resumen')
def api_alertas_resumen():
    conn = get_db()
    today = date.today()
    
    vencidos = conn.execute('''
        SELECT COUNT(*) as total FROM Egresos 
        WHERE estado = 'Pendiente' AND date(fecha_vencimiento) < date('now')
    ''').fetchone()['total']
    
    hoy = conn.execute('''
        SELECT COUNT(*) as total FROM Egresos 
        WHERE estado = 'Pendiente' AND date(fecha_vencimiento) = date('now')
    ''').fetchone()['total']
    
    proximos_3 = conn.execute('''
        SELECT COUNT(*) as total FROM Egresos 
        WHERE estado = 'Pendiente' 
        AND date(fecha_vencimiento) BETWEEN date('now', '+1 day') AND date('now', '+3 days')
    ''').fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'vencidos': vencidos,
        'hoy': hoy,
        'proximos_3_dias': proximos_3,
        'total_critico': vencidos + hoy + proximos_3
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)