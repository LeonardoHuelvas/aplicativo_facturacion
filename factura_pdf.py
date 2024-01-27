import colorsys
from reportlab.lib.colors import black  # Importa el color negro desde reportlab.lib.colors
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import streamlit as st
from database import (insertar_detalle_factura, insertar_factura, obtener_cliente_por_nombre, obtener_nombre_cliente_por_id,
                      obtener_nombre_servicio_por_id, create_server_connection, servicio_asignados_cliente)
 

# Configuración de la página de Streamlit
st.set_page_config(page_title="Factura de Venta", layout="wide")

# Función para generar el PDF usando ReportLab
def generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection):
    # Convertir fecha_factura a datetime si no lo es
    if isinstance(fecha_factura, str):
         
        try:
            fecha_factura = datetime.strptime(fecha_factura, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Fecha_factura debe ser una cadena en el formato 'AAAA-MM-DD'")
    elif not isinstance(fecha_factura, datetime):
        raise TypeError("fecha_factura debe ser una instancia de cadena o datetime")


    c = canvas.Canvas("factura.pdf", pagesize=letter)
    width, height = letter

    # Establece la fuente y el tamaño para el título de la factura
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2.0, height - 50, "FACTURA")

    # Establece la fuente y el tamaño para los detalles del cliente
    c.setFont("Helvetica", 12)
    cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
    c.drawString(100, height - 100, f"Cliente: {cliente_info}")
    c.drawString(100, height - 120, f"Fecha: {fecha_factura.strftime('%d/%m/%Y')}")

    # Encabezados de las columnas
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 150, "Descripción de los Servicios")
    c.drawString(350, height - 150, "Cantidad")
    c.drawString(450, height - 150, "Precio")

    # Crea líneas para separar la sección del encabezado y los encabezados de las columnas
    c.setStrokeColor(black)
    c.line(50, height - 130, width - 50, height - 130)
    c.line(50, height - 160, width - 50, height - 160)

    # Establece la fuente para el cuerpo de la factura
    c.setFont("Helvetica", 10)
    y_position = height - 180

    # Itera sobre los servicios y los imprime en la factura
    for servicio in servicios_asignados:
        nombre_servicio = obtener_nombre_servicio_por_id(servicio[1], connection)
        c.drawString(100, y_position, nombre_servicio)
        c.drawString(350, y_position, str(servicio[2]))
        c.drawString(450, y_position, f"${servicio[3]:,.2f}")
        y_position -= 20

    # Imprime el total antes del descuento
    c.drawString(350, y_position, "Subtotal:")
    c.drawString(450, y_position, f"${total:,.2f}")
    descuento = Decimal(descuento) if not isinstance(descuento, Decimal) else descuento
    total = Decimal(total) if not isinstance(total, Decimal) else total

    # Calcula el descuento y el total final
    descuento_aplicado = total * (descuento / Decimal('100'))
    total_final = total - descuento_aplicado

    # Imprime el descuento y el total final
    c.drawString(350, y_position - 20, f"Descuento ({descuento}%):")
    c.drawString(450, y_position - 20, f"-${descuento_aplicado:,.2f}")
    c.drawString(350, y_position - 40, "Total Final:")
    c.drawString(450, y_position - 40, f"${total_final:,.2f}")

    # Guarda el PDF
    c.save()
    return "factura.pdf"

# Función para mostrar la previsualización de la factura
def mostrar_previsualizacion(connection):
    datos = st.session_state.get('previsualizacion_datos', {})
    if datos:
        st.subheader("Previsualización de la Factura")
        st.write(f"Cliente: {datos['nombre_cliente']}")
        for servicio in datos['servicios_asignados']:
            nombre_servicio = obtener_nombre_servicio_por_id(servicio[1], connection)# servicio[0] es id_servicio
            cantidad_servicio = servicio[2]  # servicio[1] es cantidad
            precio_servicio = servicio[3]  # servicio[2] es precio
            st.write(f"Servicio: {nombre_servicio} - Cantidad: {cantidad_servicio} - Precio: {precio_servicio}")


        st.write(f"Total antes de descuento: {datos['total']}")
        st.write(f"Descuento: {datos['descuento']}%")
        descuento_decimal = Decimal(str(datos['descuento']))
        total_con_descuento = datos['total'] * (1 - (descuento_decimal / 100))
        st.write(f"Total después de descuento: {total_con_descuento}")


# Función para mostrar el botón de descarga del PDF
def mostrar_factura_pdf(pdf_file, servicios_asignados, connection):
    with open(pdf_file, "rb") as f:
        st.download_button(label="Descargar Factura", data=f, file_name="factura.pdf", mime="application/pdf")
        st.write("Servicios:")
        for servicio in servicios_asignados:
           id_servicio = servicio[1]
           cantidad = servicio[2]
           precio = servicio[3]
           nombre_servicio = obtener_nombre_servicio_por_id(id_servicio, connection)
           st.write(f"Nombre: {nombre_servicio} - Cantidad: {cantidad} - Precio: {precio}")
          
            
def generar_factura_final():
    datos = st.session_state.get('previsualizacion_datos', {})
    if datos:
        connection = create_server_connection("localhost", "root", "123", "lucmonet")
        cliente_id = datos['cliente_id']
        servicios_asignados = datos['servicios_asignados']
        total = datos['total']
        descuento = datos['descuento']
        fecha_factura = datos['fecha_factura']

        # Llamar a insertar_factura con los argumentos correctos
        factura_id = insertar_factura(cliente_id, total, descuento, connection)
        if factura_id:
            for servicio in servicios_asignados:
                # servicio[0] es el ID del servicio, servicio[1] es cantidad, servicio[2] es precio
                insertar_detalle_factura(factura_id, servicio[1], servicio[2], servicio[3], connection)

            # Generar y mostrar el PDF de la factura
            pdf_file = generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection)
            mostrar_factura_pdf(pdf_file, servicios_asignados, connection)
            st.success("Factura generada y guardada con éxito.")
        else:
            st.error("Error al insertar factura en la base de datos.")



# Función principal para manejar la interfaz de usuario de Streamlit
def run():
    connection = create_server_connection("localhost", "root", "123", "lucmonet")
    
    # Interfaz de usuario de Streamlit para recopilar datos de la factura
    with st.form("invoice_form"):
        st.title("Generador de Facturas")

        from_who = st.text_input("De", "Servicios Lucmo")
        to_who = st.text_input("Cobrar a", "Nombre del cliente")
        date_invoice = st.date_input("Fecha")

        st.subheader("Añadir Servicio")
        servicio = st.text_input("Servicio", "Descripción del servicio")
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
        precio = st.number_input("Precio", min_value=0.0, format='%f')

        st.subheader("Descuentos")
        descuento = Decimal(str(descuento))
        descuento = st.number_input("Descuento %", min_value=0.0, value=0.0, format='%f')

        submit_button = st.form_submit_button("Generar Factura")

        if submit_button:
            cliente = obtener_cliente_por_nombre(to_who, connection)

            if cliente:
                items = [{"Servicio": servicio, "Cantidad": cantidad, "Precio": precio}]
                total = sum(item["Cantidad"] * item["Precio"] for item in items)
                pdf_file = generar_factura_pdf(cliente['id'], items, str(date_invoice), total, descuento, connection)
                mostrar_factura_pdf(pdf_file, servicio_asignados_cliente)
            else:
                st.error("El cliente no existe. Por favor, verifica el nombre.")

# Llamada a la función principal
if __name__ == "__main__":
    run()
