
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm

def generar_pdf_cxc(cliente, valor, numero_cxc):
    """Genera un archivo PDF para una cuenta de cobro usando ReportLab."""
    try:
        nombre_archivo = f"CXC_{numero_cxc}_{cliente['nombre_completo']}.pdf"
        ruta_salida = f"SISTEMA_CONTABLE/DATOS/Salidas/CuentasCobro_PDFs/{nombre_archivo}"

        c = canvas.Canvas(ruta_salida, pagesize=letter)
        width, height = letter  # Ancho y alto de la página

        # --- DIBUJAR EL FORMATO ---
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2.0, height - 1.5*cm, f"CUENTA DE COBRO N°: {numero_cxc}")

        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height - 2.5*cm, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")

        # Sección "Debe A"
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, height - 4*cm, "DEBE A:")
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, height - 4.5*cm, "TU NOMBRE O EMPRESA")
        c.drawString(2*cm, height - 5*cm, "C.C. o NIT: TU NIT")

        # Línea divisoria
        c.line(2*cm, height - 5.5*cm, width - 2*cm, height - 5.5*cm)

        # Sección "Cliente"
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, height - 6.2*cm, "Apellidos y Nombre y/o Razón Social:")
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, height - 6.7*cm, str(cliente.get('nombre_completo', '')))

        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, height - 7.4*cm, "C.C. o NIT:")
        c.setFont("Helvetica", 11)
        c.drawString(5*cm, height - 7.4*cm, str(cliente.get('nit_cc', '')))

        # Tabla de Conceptos
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, height - 9*cm, "POR CONCEPTO DE")
        c.drawRightString(width - 2*cm, height - 9*cm, "VALOR")
        c.line(2*cm, height - 9.2*cm, width - 2*cm, height - 9.2*cm)

        c.setFont("Helvetica", 11)
        c.drawString(2*cm, height - 9.8*cm, "Asesoría tributaria año gravable 2024")
        c.drawRightString(width - 2*cm, height - 9.8*cm, f"${valor:,.2f}")
        c.line(2*cm, height - 10*cm, width - 2*cm, height - 10*cm)

        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 2*cm, height - 11*cm, f"TOTAL A PAGAR: ${valor:,.2f}")

        # Datos de pago y Firma
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, 5*cm, "DATOS PARA EL PAGO:")
        c.drawString(2*cm, 4.5*cm, "Banco Ahorros, Cuenta No.: '' | A nombre de: '', C.c. No.: ''")

        c.drawString(2*cm, 2.5*cm, "Atentamente,")
        c.drawString(2*cm, 1*cm, "_________________________")
        c.drawString(2*cm, 0.5*cm, "TU NOMBRE")

        c.save() # Guarda el archivo PDF

        print(f"PDF generado (con ReportLab) para {cliente['nombre_completo']} en {ruta_salida}")
        return ruta_salida

    except Exception as e:
        print(f"Error al generar PDF con ReportLab para {cliente['nombre_completo']}: {e}")
        return None

if __name__ == '__main__':
    # Datos de prueba para verificar la generación de un PDF
    cliente_prueba = {'nombre_completo': 'Cliente de Prueba ReportLab', 'nit_cc': '987654321'}
    generar_pdf_cxc(cliente_prueba, 750000, 'RL-001')
