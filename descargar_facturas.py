from datetime import date, datetime
import os
import streamlit as st
from database import *
from factura_pdf import mostrar_factura_pdf

 
#----------------------------------------------------------------------------------
def interfaz_descargar_facturas(get_facturas_por_fecha, obtener_detalle_cliente_por_id, obtener_cliente_por_nombre, obtener_total_factura, connection):
    cliente_input = st.text_input("Ingrese Nombre o ID del cliente para la búsqueda")
    
    if cliente_input == "":
        st.warning("Por favor, ingrese un nombre o ID de cliente para buscar facturas.")
        return
    
    inicio = st.date_input("Fecha de inicio", min_value=datetime(2020, 1, 1))
    fin = st.date_input("Fecha de fin", min_value=datetime(2020, 1, 1))
    
    if inicio > fin:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
        return
    
    if st.button("Buscar Facturas"):
        try:
            facturas = get_facturas_por_fecha(connection, inicio, fin, cliente_input)
            if facturas:
                mostrar_facturas(facturas, connection)
                # Suponiendo que `mostrar_facturas` proporciona la ruta del PDF
                pdf_path = "I:\Desarrollo\proyecto\facutracion_internet\aplicativo_facturación\facturas/facturas.pdf"  # Cambia esto por la ruta real del PDF
                with open(pdf_path, "rb") as f:
                    st.download_button(label="Descargar Factura", data=f, file_name="factura.pdf", mime="application/pdf")
            else:
                st.info("No se encontraron facturas en el rango de fechas seleccionado.")
        except Exception as e:
            st.error(f"Error al buscar facturas: {e}")
        finally:
            if connection.is_connected():
                connection.close()

# .............................................................................
                
                
def mostrar_facturas(facturas, connection):
    st.subheader("Facturas encontradas:")
    for factura in facturas:
        factura_id, cliente_id, fecha_factura, total, descuento = factura
        nombre_archivo_pdf = f"factura-{cliente_id}-{factura_id}.pdf"
        ruta_archivo_pdf = os.path.join('./facturas', nombre_archivo_pdf)

        st.write(f"Factura ID: {factura_id}")
        st.write(f"Cliente ID: {cliente_id}")
        st.write(f"Fecha de Factura: {fecha_factura}")
        st.write(f"Total: {total}")
        st.write(f"Descuento: {descuento}")

        if os.path.exists(ruta_archivo_pdf):
            with open(ruta_archivo_pdf, "rb") as f:
                data = f.read()
            st.download_button(label=f"Descargar Factura {factura_id}", data=data, file_name=nombre_archivo_pdf, mime="application/pdf")
        else:
            st.warning(f"No se encontró la factura {factura_id}.")
            st.write("Por favor, genere el archivo PDF y vuelva a intentarlo.")

if __name__ == "__main__":
    st.set_page_config(page_title="Descargar Facturas", layout="wide")
    connection = create_server_connection("localhost", "root", "123", "lucmonet")

    if not os.path.exists('I:\Desarrollo\proyecto\facutracion_internet\aplicativo_facturación/facturas'):
        os.makedirs('./facturas')

    interfaz_descargar_facturas(connection)