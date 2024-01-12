import fpdf
from datetime import datetime


fecha_actual = datetime.today()


def formatear_fecha(fecha):
    return fecha.strftime('%d/%m/%Y')


# Obtener el nombre del cliente
cliente = Cliente.objects.get(id=cliente_id)
nombre_cliente = cliente.nombre
documento_identidad = cliente.documento_identidad

# Generar un número de factura único
numero_factura = next_sequence(Factura.objects.order_by('-id').values_list('id', flat=True))

# Obtener la lista de servicios prestados
servicios_prestados = FacturaDetalle.objects.filter(factura_id=factura.id)

# Escribir la información de la factura

factura = fpdf.FPDF()
factura.add_page()

# Título de la factura
factura.cell(200, 10, 'Factura', 0, 1, 'C')

# Número de factura
factura.cell(200, 10, 'Número de factura: {}'.format(numero_factura), 0, 1, 'C')

# Fecha
factura.cell(200, 10, 'Fecha: {}'.format(formatear_fecha(fecha_actual)), 0, 1, 'C')

# Cliente
factura.cell(200, 10, 'Cliente: {}'.format(nombre_cliente), 0, 1, 'C')

# Documento de identidad
factura.cell(200, 10, 'Documento de identidad: {}'.format(documento_identidad), 0, 1, 'C')

# Servicios prestados
for servicio in servicios_prestados:
  factura.cell(200, 10, '{}: {}'.format(servicio.servicio.nombre, servicio.cantidad * servicio.precio), 0, 1, 'C')

# Importe total
factura.cell(200, 10, 'Importe total: {}'.format(importe_total), 0, 1, 'C')

# Guardar la factura en formato PDF
factura.output('factura.pdf')
