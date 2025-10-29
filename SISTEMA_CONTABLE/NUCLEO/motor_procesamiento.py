
import json
import pandas as pd
from datetime import datetime

def cargar_configuracion():
    """Carga el archivo de configuración con el mapeo de columnas."""
    # Como encontramos problemas creando archivos, incrustamos la configuración.
    # Si en el futuro se soluciona, podemos cambiar esto para leer el JSON.
    config_data = {
      "patrimonio": [
        {
          "nombre_en_relacion": "EFECTIVO, BANCOS, CUENTAS DE AHORROS",
          "hoja_excel": "Movimientos",
          "secciones": [
            "BANCOS, Cuentas corrientes",
            "BANCOS, Cuentas de ahorro"
          ],
          "columna_descripcion": "CONCEPTO y/o RAZÓN SOCIAL o APELLIDOS Y NOMBRES",
          "columna_valor": "SALDO FINAL"
        },
        {
          "nombre_en_relacion": "CUENTAS POR COBRAR",
          "hoja_excel": "Movimientos",
          "secciones": [
            "CUENTAS POR COBRAR"
          ],
          "columna_descripcion": "CONCEPTO y/o RAZÓN SOCIAL o APELLIDOS Y NOMBRES",
          "columna_valor": "SALDO FINAL"
        },
        {
          "nombre_en_relacion": "INVERSIONES MOBILIARIAS, BONOS, CDT's Y DEMÁS INVERSIONES",
          "hoja_excel": "Movimientos",
          "secciones": [
            "FONDOS",
            "OTRAS INVERSIONES"
          ],
          "columna_descripcion": "CONCEPTO y/o RAZÓN SOCIAL o APELLIDOS Y NOMBRES",
          "columna_valor": "SALDO FINAL"
        },
        {
          "nombre_en_relacion": "ACCIONES Y APORTES EN SOCIEDADES",
          "hoja_excel": "Acciones y Aportes",
          "secciones": [
            "Para: Dividendos y participaciones 2016 y anteriores"
          ],
          "columna_descripcion": "RAZÓN SOCIAL DE LA SOCIEDAD",
          "columna_valor": "COSTO FISCAL Final"
        },
        {
          "nombre_en_relacion": "BIENES RAÍCES Y TERRENOS",
          "hoja_excel": "Propiedad, Planta y Equipo",
          "secciones": [
            "CONSTRUCCIONES Y EDIFICACIONES"
          ],
          "columna_descripcion": "DIRECCIÓN",
          "columna_valor": "VALOR Final"
        }
      ],
      "pasivos": [
        {
          "nombre_en_relacion": "FINANCIEROS",
          "hoja_excel": "Movimientos",
          "secciones": [
            "OBLIGACIONES FINANCIERAS"
          ],
          "columna_descripcion": "CONCEPTO y/o RAZÓN SOCIAL o APELLIDOS Y NOMBRES",
          "columna_valor": "SALDO FINAL"
        },
        {
          "nombre_en_relacion": "OTRAS CUENTAS POR PAGAR",
          "hoja_excel": "Movimientos",
          "secciones": [
            "CUENTAS POR PAGAR"
          ],
          "columna_descripcion": "CONCEPTO y/o RAZÓN SOCIAL o APELLIDOS Y NOMBRES",
          "columna_valor": "SALDO FINAL"
        }
      ],
      "ingresos": [
        {
          "nombre_en_relacion": "PENSIONES, SALARIOS Y DEMÁS PAGOS LABORALES",
          "hoja_excel": "Ingresos Laborales y Pensiones",
          "secciones": [
            "RENTAS POR SALARIOS",
            "PENSIONES DE: JUBILACIÓN, INVALIDEZ, VEJEZ, DE SOBREVIVIENTE Y SOBRE RIESGOS LABORALES"
          ],
          "columna_descripcion": "RAZÓN SOCIAL O APELLIDOS Y NOMBRES",
          "columna_valor": "TOTAL INGRESO"
        },
        {
          "nombre_en_relacion": "OTROS INGRESOS Y RETENCIONES",
          "hoja_excel": "Ingresos Capital y No Laborales",
          "secciones": [
            "ARRENDAMIENTOS"
          ],
          "columna_descripcion": "RAZÓN SOCIAL O APELLIDOS Y NOMBRES",
          "columna_valor": "TOTAL INGRESO"
        }
      ]
    }
    return config_data

def extraer_datos(ruta_excel, config):
    """
    Extrae datos del archivo Excel pesado basándose en la configuración.
    """
    datos_extraidos = {}
    print("Iniciando extracción de datos...")

    all_configs = [item for sublist in config.values() for item in sublist]

    hojas_a_leer = {item['hoja_excel'] for item in all_configs}

    for hoja_nombre in hojas_a_leer:
        try:
            print(f"  Procesando hoja: '{hoja_nombre}'...")
            df = pd.read_excel(ruta_excel, sheet_name=hoja_nombre, header=None)

            configs_para_hoja = [c for c in all_configs if c['hoja_excel'] == hoja_nombre]

            for item_config in configs_para_hoja:
                nombre_relacion = item_config['nombre_en_relacion']
                if nombre_relacion not in datos_extraidos:
                    datos_extraidos[nombre_relacion] = []

                # 1. Encontrar la fila de encabezado y los índices de las columnas
                header_row_idx, desc_col_idx, val_col_idx = -1, -1, -1
                for i, row in df.iterrows():
                    row_values = [str(cell).strip() for cell in row.values]
                    if item_config['columna_descripcion'] in row_values:
                        header_row_idx = i
                        desc_col_idx = row_values.index(item_config['columna_descripcion'])
                        try:
                            val_col_idx = row_values.index(item_config['columna_valor'])
                        except ValueError:
                            continue
                        break

                if header_row_idx == -1:
                    continue

                # 2. Encontrar cada sección y extraer sus datos
                for section_name in item_config['secciones']:
                    section_start_row = -1
                    # Encontrar la fila donde comienza la sección
                    for i in range(len(df)):
                        if section_name in df.iloc[i].to_string():
                            section_start_row = i
                            break

                    if section_start_row == -1:
                        continue

                    # 3. Iterar debajo de la sección para encontrar datos
                    for i in range(section_start_row + 1, len(df)):
                        row_data = df.iloc[i]

                        # Criterio de parada: si llegamos a una fila que parece un total o una nueva sección
                        # Asumimos que la descripción está en una columna a la izquierda de la sección encontrada

                        possible_desc_cell = str(row_data[desc_col_idx]).strip()

                        if "TOTAL" in possible_desc_cell.upper() or possible_desc_cell == "nan" and row_data.isnull().all():
                           break # Fin de la subsección

                        descripcion = possible_desc_cell
                        valor = row_data[val_col_idx]

                        if descripcion and descripcion != 'nan' and pd.to_numeric(valor, errors='coerce') != 0:
                            valor_numerico = pd.to_numeric(valor, errors='coerce')
                            if not pd.isna(valor_numerico):
                                datos_extraidos[nombre_relacion].append({
                                    'descripcion': descripcion,
                                    'valor': valor_numerico
                                })

        except Exception as e:
            print(f"Error al procesar la hoja '{hoja_nombre}': {e}")

    print("Extracción de datos finalizada.")
    return datos_extraidos

def main():
    """Función principal del motor de procesamiento."""

    print("Iniciando el motor de procesamiento...")
    config = cargar_configuracion()

    ruta_declaracion = "SISTEMA_CONTABLE/DATOS/declaracion_completa.xlsx"

    datos = extraer_datos(ruta_declaracion, config)

    print("Procesamiento completado.")

if __name__ == "__main__":
    main()
