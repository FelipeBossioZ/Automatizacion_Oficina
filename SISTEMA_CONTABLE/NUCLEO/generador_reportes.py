
import pandas as pd
from datetime import datetime

def generar_reporte(datos_extraidos, plantilla_path):
    """
    Toma los datos extraídos y los inserta en una nueva copia de la plantilla de relación.
    """
    print("Iniciando la generación del reporte...")

    try:
        # Cargar la plantilla de relación
        df_plantilla = pd.read_excel(plantilla_path, header=None)

        # Crear una copia para no modificar el original
        df_reporte = df_plantilla.copy()

        # Lógica para encontrar secciones y rellenar datos
        for seccion_nombre, items in datos_extraidos.items():
            fila_insercion = -1
            # Buscar la fila que contiene el nombre de la sección
            for i, row in df_reporte.iterrows():
                # Buscamos de forma flexible, ignorando espacios y mayúsculas
                if any(seccion_nombre.lower() in str(cell).lower() for cell in row):
                    # Una vez encontrada la sección, buscamos la primera fila completamente vacía debajo de ella
                    for j in range(i + 1, len(df_reporte)):
                        if df_reporte.iloc[j].isnull().all():
                            fila_insercion = j
                            break
                    break # Salimos del bucle principal una vez encontrada la sección

            if fila_insercion != -1:
                # Insertar los datos en la fila encontrada
                nuevas_filas = []
                for item in items:
                    # La descripción va en la columna 0, el valor en la 1 (por ejemplo)
                    # Esto podría necesitar ajuste si la plantilla cambia
                    nuevas_filas.append({0: item['descripcion'], 1: item['valor']})

                df_nuevas_filas = pd.DataFrame(nuevas_filas)

                # Desplazar las filas existentes y insertar las nuevas
                df_superior = df_reporte.iloc[:fila_insercion]
                df_inferior = df_reporte.iloc[fila_insercion:]

                df_reporte = pd.concat([df_superior, df_nuevas_filas, df_inferior], ignore_index=True)


        # Guardar el nuevo reporte
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        nombre_archivo = f"Relacion_Generada_{timestamp}.xlsx"
        ruta_salida = f"SISTEMA_CONTABLE/DATOS/Salidas/Reportes/{nombre_archivo}"

        df_reporte.to_excel(ruta_salida, index=False, header=False)

        print(f"Reporte generado exitosamente en: {ruta_salida}")
        return ruta_salida

    except Exception as e:
        print(f"Error al generar el reporte: {e}")
        return None

if __name__ == '__main__':
    # Esto es solo para pruebas, la data vendrá del motor principal
    datos_de_prueba = {
        "EFECTIVO, BANCOS, CUENTAS DE AHORROS": [
            {'descripcion': 'Banco Falso 123', 'valor': 20000},
            {'descripcion': 'Banquito', 'valor': 3500000}
        ]
    }
    plantilla = "SISTEMA_CONTABLE/DATOS/plantilla_relacion.xlsx"
    generar_reporte(datos_de_prueba, plantilla)
