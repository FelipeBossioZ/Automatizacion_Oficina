
import sqlite3
import pandas as pd
from datetime import datetime
from .database import inicializar_bd
from .lector_cobros import leer_y_poblar_clientes
from .generador_cxc import generar_pdf_cxc
from .generador_correos import crear_correo_cxc

def obtener_siguiente_numero_cxc():
    """Obtiene el último número de CXC y calcula el siguiente."""
    # En una implementación futura, esto leería el último número de la BD.
    # Por ahora, usaremos un número inicial basado en la fecha.
    return datetime.now().strftime("25-%H%M%S")

def ejecutar_flujo_cxc():
    """
    Orquesta el flujo completo del módulo de Cuentas por Cobro.
    """
    print("=============================================")
    print("INICIANDO MÓDULO DE CUENTAS POR COBRO (CXC)")
    print("=============================================")

    # 1. Inicializar y Poblar la Base de Datos
    inicializar_bd()
    leer_y_poblar_clientes('SISTEMA_CONTABLE/DATOS/SISTEMA_DE_COBROS.xlsx')

    # 2. Lógica principal: Obtener montos y generar archivos
    df_cobros = pd.read_excel('SISTEMA_CONTABLE/DATOS/SISTEMA_DE_COBROS.xlsx', header=None)
    conn = sqlite3.connect('SISTEMA_CONTABLE/DATOS/contabilidad.db')
    cursor = conn.cursor()

    # Obtenemos todos los clientes de la BD
    cursor.execute("SELECT id, nombre_completo, nit_cc, correo_electronico, grupo_familiar, es_titular FROM Clientes")
    todos_los_clientes = cursor.fetchall()

    clientes_a_procesar = [c for c in todos_los_clientes if c[5] or c[4] is None] # Titulares o individuales

    for cliente_db in clientes_a_procesar:
        cliente_info = {
            'id': cliente_db[0],
            'nombre_completo': cliente_db[1],
            'nit_cc': cliente_db[2],
            'correo_electronico': cliente_db[3],
            'grupo_familiar': cliente_db[4]
        }

        valor_a_cobrar = 0
        nombres_en_grupo = []

        if cliente_info['grupo_familiar']:
            # Sumar valores de todo el grupo
            miembros_grupo = [c for c in todos_los_clientes if c[4] == cliente_info['grupo_familiar']]
            for miembro in miembros_grupo:
                # Buscar el valor en el dataframe original
                nombre_miembro = miembro[1]
                nombres_en_grupo.append(nombre_miembro)
                valor_fila = df_cobros[df_cobros[1] == nombre_miembro][7].values
                if len(valor_fila) > 0:
                    valor_numerico = pd.to_numeric(valor_fila[0], errors='coerce')
                    if pd.notna(valor_numerico):
                        valor_a_cobrar += valor_numerico
        else:
            # Valor individual
            valor_fila = df_cobros[df_cobros[1] == cliente_info['nombre_completo']][7].values
            if len(valor_fila) > 0:
                valor_numerico = pd.to_numeric(valor_fila[0], errors='coerce')
                if pd.notna(valor_numerico):
                    valor_a_cobrar = valor_numerico

        if valor_a_cobrar <= 0:
            print(f"  -> ADVERTENCIA: {cliente_info['nombre_completo']} tiene un valor de cero en el Excel. Usando valor de prueba (500,000 COP) para la demostración.")
            valor_a_cobrar = 500000

        print(f"  -> Procesando a {cliente_info['nombre_completo']} con un valor de ${valor_a_cobrar:,.2f}")

        # Generar PDF
        numero_cxc = obtener_siguiente_numero_cxc()
        ruta_pdf = generar_pdf_cxc(cliente_info, valor_a_cobrar, numero_cxc)

        if ruta_pdf:
            # Generar Correo
            cuenta_cobro_info = {'numero_cxc': numero_cxc}
            crear_correo_cxc(cliente_info, cuenta_cobro_info, ruta_pdf)

    conn.close()

    print("\n=============================================")
    print("MÓDULO CXC FINALIZADO")
    print("=============================================")

if __name__ == '__main__':
    ejecutar_flujo_cxc()
