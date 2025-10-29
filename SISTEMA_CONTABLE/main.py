
from NUCLEO.motor_procesamiento import cargar_configuracion, extraer_datos
from NUCLEO.generador_reportes import generar_reporte

def ejecutar_flujo_completo():
    """
    Orquesta el flujo completo: carga configuración, extrae datos y genera el reporte.
    """
    print("=============================================")
    print("INICIANDO SISTEMA DE AUTOMATIZACIÓN CONTABLE")
    print("=============================================")

    # 1. Cargar Configuración
    config = cargar_configuracion()

    # 2. Extraer Datos del Excel
    ruta_declaracion = "SISTEMA_CONTABLE/DATOS/declaracion_completa.xlsx"
    datos_extraidos = extraer_datos(ruta_declaracion, config)

    # Imprimir un resumen de los datos extraídos para verificación
    print("\n--- Resumen de Datos Extraídos ---")
    for seccion, items in datos_extraidos.items():
        print(f"  Sección: {seccion}")
        for item in items:
            print(f"    - {item['descripcion']}: {item['valor']}")
    print("----------------------------------\n")

    # 3. Generar el Reporte Final
    if datos_extraidos:
        ruta_plantilla = "SISTEMA_CONTABLE/DATOS/plantilla_relacion.xlsx"
        generar_reporte(datos_extraidos, ruta_plantilla)
    else:
        print("No se extrajeron datos, no se generará el reporte.")

    print("=============================================")
    print("PROCESO FINALIZADO")
    print("=============================================")


if __name__ == "__main__":
    ejecutar_flujo_completo()
