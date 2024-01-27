from decimal import Decimal
from MySQLdb import Connection
import streamlit as st
from fpdf import FPDF
from database import insertar_detalle_factura, insertar_factura, obtener_cliente_por_nombre, obtener_nombre_cliente_por_id, obtener_nombre_servicio_por_id, create_server_connection, servicio_asignados_cliente
import datetime

# Configuración de la página de Streamlit
st.set_page_config(page_title="Factura de Venta", layout="wide")

# Función para generar el PDF
def generar_factura_pdf(cliente_id, servicios_asignados, fecha_factura, total, descuento, connection):
    factura = FPDF()
    factura.add_page()
    factura.set_font("Arial", size=12)
    factura.cell(200, 10, txt="Factura", ln=True, align='C')

    # Añade la información del cliente y los servicios
    factura.cell(100, 10, txt=f"De: Servicios Lucmo", ln=True)
    factura.cell(100, 10, txt=f"Para: {obtener_nombre_cliente_por_id(cliente_id, connection)}", ln=True)
    factura.cell(100, 10, txt=f"Fecha: {fecha_factura}", ln=True)

    for servicio in servicios_asignados:
        id_servicio = servicio[0]  # Primer elemento de la tupla
        cantidad = servicio[1]     # Segundo elemento
        precio = servicio[2]  
        factura.cell(100, 10, txt=f"Servicio: {id_servicio} - Cantidad: {cantidad} - Precio: {precio}", ln=True)

    # Añade descuento y total
    if descuento:
        descuento_aplicado = total * (descuento / 100)
        total_final = total - descuento_aplicado
        factura.cell(100, 10, txt=f"Descuento: {descuento_aplicado}", ln=True)
        factura.cell(100, 10, txt=f"Total Final: {total_final}", ln=True)
    else:
        factura.cell(100, 10, txt=f"Total: {total}", ln=True)

    pdf_file = "factura.pdf"
    factura.output(pdf_file)
    return pdf_file

# Función para mostrar la previsualización de la factura
def mostrar_previsualizacion(connection):
    datos = st.session_state.get('previsualizacion_datos', {})
    if datos:
        st.subheader("Previsualización de la Factura")
        st.write(f"Cliente: {datos['nombre_cliente']}")
        for servicio in datos['servicios_asignados']:
            nombre_servicio = obtener_nombre_servicio_por_id(servicio[0], connection)# servicio[0] es id_servicio
            cantidad_servicio = servicio[1]  # servicio[1] es cantidad
            precio_servicio = servicio[2]  # servicio[2] es precio
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
           id_servicio = servicio[0]
           cantidad = servicio[1]
           precio = servicio[2]
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
                insertar_detalle_factura(factura_id, servicio[0], servicio[1], servicio[2], connection)

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
