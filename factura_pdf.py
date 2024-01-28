from reportlab.lib import colors
from reportlab.lib.colors import black  # Importa el color negro desde reportlab.lib.colors
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import streamlit as st
from database import (get_facturas, insertar_detalle_factura, insertar_factura, obtener_cliente_por_nombre, obtener_nombre_cliente_por_id,
                      obtener_nombre_servicio_por_id, create_server_connection, obtener_total_factura, servicio_asignados_cliente, factura_ya_existe)
 

# Configuración de la página de Streamlit
st.set_page_config(page_title="Factura de Venta", layout="wide")

# Función para generar el PDF usando ReportLab

def generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection):
    # Dibujar un marco alrededor del PDF
    c = canvas.Canvas("factura.pdf", pagesize=letter)
    width, height = letter
    c.drawImage("assets/logo.png", 40, height - 50, width=100, preserveAspectRatio=True, mask='auto')
    c.rect(20, 20, width - 40, height - 40)


    # Define los colores de la plantilla
    color_header = colors.HexColor("#FFEEEE")  # o el color que corresponda

    # Establece la fuente y el tamaño para el título de la factura
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2.0, height - 50, "FACTURA")
    # Información del cliente
    c.setFont("Helvetica-Bold", 12)

    cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
    c.drawString(100, height - 100, f"CLIENTE: {cliente_info}")
    # c.drawString(100, height - 115, f"{cliente_info}")

    # Crea una línea para separar la sección del encabezado
    c.setStrokeColor(colors.black)
    c.line(50, height - 130, width - 50, height - 130)

    # Encabezados de las columnas con fondo de color
    c.setFillColor(color_header)
    c.rect(50, height - 155, width - 100, 20, fill=1)
    c.setFillColor(colors.black)
    c.drawString(60, height - 150, "DESCRIPCIÓN DE LOS SERVICIOS")
    c.drawString(350, height - 150, "CANTIDAD")
    c.drawString(500, height - 150, "PRECIO")
    # Establece la fuente para el cuerpo de la factura
    c.setFont("Helvetica", 10)
    y_position = height - 180


    # Itera sobre los servicios y los imprime en la factura
    for servicio in servicios_asignados:
        nombre_servicio = obtener_nombre_servicio_por_id(servicio[1], connection)
        c.drawString(60, y_position, nombre_servicio)
        c.drawString(350, y_position, str(servicio[2]))
        c.drawString(500, y_position, f"${servicio[3]:,.2f}")
        y_position -= 20


    # Imprime el subtotal
    c.drawString(350, y_position, "Subtotal:")
    c.drawString(500, y_position, f"${total:,.2f}")
    # Calcula el descuento y el total final
    descuento = Decimal(descuento) if not isinstance(descuento, Decimal) else descuento
    descuento_aplicado = total * (descuento / Decimal('100'))
    total_final = total - descuento_aplicado

    # Imprime el descuento y el total final
    c.drawString(350, y_position - 20, f"Descuento ({descuento}%):")
    c.drawString(500, y_position - 20, f"-${descuento_aplicado:,.2f}")
    c.drawString(350, y_position - 40, "Total Final:")
    c.drawString(500, y_position - 40, f"${total_final:,.2f}")

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
        factura_id = insertar_factura(cliente_id, total, descuento, connection)  # Add this line to get the factura_id

        if factura_id:
            for servicio in servicios_asignados:
                insertar_detalle_factura(factura_id, servicio[1], servicio[2], servicio[3], connection)

            # Generar y mostrar el PDF de la factura
            pdf_file = generar_factura_pdf(cliente_id, servicios_asignados, factura_id, total, descuento, connection)  # Pass factura_id to the function
            mostrar_factura_pdf(pdf_file, servicios_asignados, connection)
            st.success("Factura generada y guardada con éxito.")
        else:
            st.error("Error al insertar factura en la base de datos.")
    else:
        st.error("Datos de previsualización no están disponibles.")
            


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
        
        if st.button("Ver Facturas"):
         facturas = get_facturas(connection)
         if facturas:
            st.subheader("Lista de Facturas")
            for factura in facturas:
                cliente_id = factura[1]
                with st.container():
                 st.subheader("Lista de Facturas")
                for factura in facturas:
                    cliente_id = factura[1]
                    cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
                    st.write(f"ID: {factura[2]} - Cliente: {cliente_info} - Total: {obtener_total_factura(factura[3], connection)}")
                    cliente_id = factura[1]
                    servicios_asignados = servicio_asignados_cliente(cliente_id, connection)
                    total = obtener_total_factura(factura[3], connection)
                    descuento = Decimal(0.0)
                    pdf_file = generar_factura_pdf(cliente_id, servicios_asignados, str(factura[4]), total, descuento, connection)
                    mostrar_factura_pdf(pdf_file, servicios_asignados, connection)
        else:
            st.write("No hay facturas disponibles.")

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
