import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from decimal import Decimal
 
import streamlit as st
from database import (get_facturas, insertar_detalle_factura, insertar_factura, obtener_cliente_por_nombre, obtener_nombre_cliente_por_id,
                      obtener_nombre_servicio_por_id, create_server_connection, obtener_total_factura, servicio_asignados_cliente, factura_ya_existe)
 

# Configuración de la página de Streamlit
st.set_page_config(page_title="Factura de Venta", layout="wide")

# Función para generar el PDF usando ReportLab
def generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection):
    file_name = "factura.pdf"
    document = SimpleDocTemplate(file_name, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Añade un logo y establece un marco alrededor del PDF
    story.append(Spacer(1, 2*cm))
    im = Image('assets/logo.png', 2*inch, 1*inch)
    story.append(im)
    
    # Título de la factura
    style = styles['Title']
    story.append(Paragraph("FACTURA", style))
    story.append(Spacer(1, 0.5*cm))

    # Información del cliente
    style = styles['Normal']
    cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
    story.append(Paragraph(f"Cliente: {cliente_info}", style))
    story.append(Spacer(1, 0.5*cm))

    # Encabezados de las columnas
    style = styles['Heading2']
    encabezados = [('Descripción de los Servicios', 'Cantidad', 'Precio')]
    servicios_data = [encabezados[0]]
    
    # Itera sobre los servicios y los añade a la lista
    for servicio in servicios_asignados:
        nombre_servicio = obtener_nombre_servicio_por_id(servicio[1], connection)
        servicios_data.append((nombre_servicio, servicio[2], f"${servicio[3]:,.2f}"))
    
    # Añade la tabla de servicios al documento
    t = Table(servicios_data, colWidths=[3*inch, inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFEEEE")), # Fondo del encabezado
        ('TEXTCOLOR', (0,0), (-1,0), colors.black), # Color del texto del encabezado
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), # Alineación del texto en todas las celdas
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Fuente del encabezado
        ('BOTTOMPADDING', (0,0), (-1,0), 12), # Relleno inferior del encabezado
        ('BACKGROUND', (0,1), (-1,-1), colors.beige), # Fondo del resto de la tabla
        ('GRID', (0,0), (-1,-1), 1, colors.black), # Líneas de la tabla
        # Añade más estilos según sea necesario
    ]))
    story.append(t)
    
    # Añade el subtotal, descuento y total final
    descuento = Decimal(descuento) if not isinstance(descuento, Decimal) else descuento
    descuento_aplicado = total * (descuento / Decimal('100'))
    total_final = total - descuento_aplicado
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Subtotal: ${total:,.2f}", style))
    story.append(Paragraph(f"Descuento ({descuento}%): -${descuento_aplicado:,.2f}", style))
    story.append(Paragraph(f"Total Final: ${total_final:,.2f}", style))
    
    # Construye el PDF
    document.build(story)
    return file_name


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
            connection = create_server_connection("localhost", "root", "123", "lucmonet")
            for servicio in servicios_asignados:
                insertar_detalle_factura(factura_id, servicio[1], servicio[2], servicio[3], total, cliente_id, descuento, connection)

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
                factura_id = factura[0]  # Asumiendo que el ID de la factura está en factura[0]
                cliente_id = factura[1]
                fecha_factura = factura[4]  # Asumiendo que factura[4] es la fecha de la factura
                cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
                servicios_asignados = servicio_asignados_cliente(cliente_id, connection)
                total = obtener_total_factura(factura_id, connection)
                descuento = Decimal('0.0')  # Si tienes el descuento en la factura, úsalo aquí

                # Generamos el nombre del archivo PDF para cada factura
                nombre_archivo_pdf = f"factura-{factura_id}.pdf"

                with st.container():
                    st.write(f"ID: {factura_id} - Cliente: {cliente_info} - Total: {total}")
                    
                    # Comprobamos si el archivo de la factura ya existe para no generar uno nuevo cada vez
                    ruta_archivo_pdf = f"/invoices{cliente_id}"  # Debes actualizar esta ruta según tu configuración
                    
                    # Generamos el PDF solo si no existe, para evitar la regeneración en cada click
                    if not os.path.exists(ruta_archivo_pdf):
                        ruta_archivo_pdf = generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection)

                    # Botón para descargar la factura específica
                    with open(ruta_archivo_pdf, "rb") as pdf_file:
                        st.download_button(
                            label="Descargar Factura",
                            data=pdf_file,
                            file_name=nombre_archivo_pdf,
                            mime="application/pdf"
                    )
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
