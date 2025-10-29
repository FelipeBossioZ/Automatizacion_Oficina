
import os
from email.message import EmailMessage
from email.headerregistry import Address

def crear_correo_cxc(cliente, cuenta_cobro, ruta_pdf):
    """
    Crea un archivo .eml para una cuenta de cobro, listo para ser abierto en Outlook.
    """
    try:
        msg = EmailMessage()

        # --- Configurar Asunto ---
        asunto = f"Declaración y Cuenta de cobro asesoría tributaria AG 2024 - {cliente['nombre_completo']}"
        if cliente['grupo_familiar']:
            asunto = f"Declaración y Cuenta de cobro asesoría tributaria AG 2024 - Familia {cliente['grupo_familiar']}"
        msg['Subject'] = asunto

        # --- Configurar Remitente y Destinatario ---
        msg['From'] = Address("Tu Nombre", "tu_correo@oficina.com")
        msg['To'] = Address(cliente['nombre_completo'], cliente['correo_electronico'])

        # --- Construir Cuerpo del Correo ---
        cuerpo = f"""
Cordial saludo {cliente['nombre_completo'].split()[0]},

Adjunto declaración de renta presentada y cuenta de cobro número {cuenta_cobro['numero_cxc']} correspondiente a la asesoría prestada este año.

Se puede consignar o Transferir en:

Banco Ahorros
Cuenta No.: “”
También a través de la llave:

A nombre de: “”
C. c. No.: “”

Tan pronto se efectúe el pago por favor nos notifica para asentar la cancelación de la cuenta de cobro.

Cualquier inquietud con gusto la atenderemos.

Cordialmente,
TU NOMBRE
TU CARGO
TU EMPRESA
TU TELEFONO
"""
        msg.set_content(cuerpo)

        # --- Adjuntar el PDF ---
        with open(ruta_pdf, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(ruta_pdf))

        # --- Guardar el archivo .eml ---
        nombre_archivo = f"Correo_{cliente['nombre_completo']}.eml"
        ruta_salida = f"SISTEMA_CONTABLE/DATOS/Salidas/Correos_Borradores/{nombre_archivo}"

        with open(ruta_salida, 'wb') as f:
            f.write(msg.as_bytes())

        print(f"Correo .eml generado para {cliente['nombre_completo']} en {ruta_salida}")
        return ruta_salida

    except Exception as e:
        print(f"Error al generar correo para {cliente['nombre_completo']}: {e}")
        return None

if __name__ == '__main__':
    # Datos de prueba
    cliente_prueba = {
        'nombre_completo': 'Cliente Individual de Prueba',
        'correo_electronico': 'individual@test.com',
        'grupo_familiar': None
    }
    cuenta_cobro_prueba = {'numero_cxc': '25-141'}
    # Asumimos que el PDF de prueba existe
    ruta_pdf_prueba = 'SISTEMA_CONTABLE/DATOS/Salidas/CuentasCobro_PDFs/CXC_RL-001_Cliente de Prueba ReportLab.pdf'

    if os.path.exists(ruta_pdf_prueba):
        crear_correo_cxc(cliente_prueba, cuenta_cobro_prueba, ruta_pdf_prueba)
    else:
        print(f"Archivo PDF de prueba no encontrado en {ruta_pdf_prueba}. No se puede generar el correo de prueba.")
