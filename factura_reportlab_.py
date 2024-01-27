from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_invoice(invoice_data):
    c = canvas.Canvas("factura.pdf", pagesize=letter)
    c.setFont("Helvetica", 10)
    width, height = letter

    # Añadir el logo
    c.drawImage("/path/to/logo.png", 40, height - 50, width=100, preserveAspectRatio=True, mask='auto')

    # Añadir la información del cliente y la factura
    c.drawString(100, height - 100, f"Cliente: {invoice_data['cliente_nombre']}")
    c.drawString(100, height - 120, f"Fecha: {invoice_data['fecha']}")

    # Añadir detalles de los servicios/productos
    y_position = height - 140
    for item in invoice_data['items']:
        c.drawString(80, y_position, f"Servicio: {item['descripcion']} - Precio: {item['precio']}")
        y_position -= 20

    # Añadir el total
    c.drawString(80, y_position, f"Total: {invoice_data['total']}")

    c.save()

invoice_data = {
    'cliente_nombre': 'Nombre del Cliente',
    'fecha': '2024-01-01',
    'items': [
        {'descripcion': 'Servicio 1', 'precio': '100.00'},
        {'descripcion': 'Servicio 2', 'precio': '200.00'}
    ],
    'total': '300.00'
}

generate_invoice(invoice_data)
