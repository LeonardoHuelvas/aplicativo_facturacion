import streamlit as st
from dotenv import load_dotenv
import auth
from panels import mostrar_interfaz_carga_servicios, show_panels
from database import create_server_connection, get_clientes
from styles import load_styles

st.markdown(load_styles(), unsafe_allow_html=True)

# Función para manejar el inicio de sesión
def handle_login():
    with st.form(key='login_form'):
        login_username = st.text_input("Nombre de Usuario", key="login_username")
        login_password = st.text_input("Contraseña", type="password", key="login_password")
        submit_button = st.form_submit_button(label="Iniciar Sesión")
        
        if submit_button:
            if auth.verify_login(login_username, login_password):
                st.session_state['logged_in'] = True
                st.success("Inicio de sesión exitoso")
                return True
            else:
                st.error("Error en el inicio de sesión")
                return False
    return False

# Función principal
def main():
    st.title("Sistema de Facturación")

    # Inicializar estado de la sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'selected_cliente_id' not in st.session_state:
        st.session_state['selected_cliente_id'] = None  # Inicialización

    if not st.session_state['logged_in']:
        st.subheader("Iniciar Sesión")
        if handle_login():
            st.experimental_rerun() 
            st.rerun()
    else:
        selected_panel = show_panels(st)
        if selected_panel == "Opciones de Facturación":
            st.header("Opciones de Facturación")
            with create_server_connection("localhost", "root", "123", "lucmonet") as connection:
                clientes = get_clientes(connection)
                if clientes:
                    cliente_id = st.selectbox("Seleccionar Cliente", clientes, key="select_cliente")
                    st.session_state['selected_cliente_id'] = cliente_id
                    st.subheader("Cargar Servicios")
                    if st.session_state.get('selected_cliente_id'):  # Verificar antes de usar
                        mostrar_interfaz_carga_servicios(st.session_state['selected_cliente_id'], connection)
                else:
                    st.warning("No hay clientes disponibles en este momento.")
        elif selected_panel == "Gestionar Asignación de Servicios":
            # Implementa la función para gestionar asignación de servicios aquí
            pass            
        if st.button("Cerrar Sesión"):
            auth.logout()   
            st.experimental_rerun()   
            st.success("Sesión cerrada correctamente")  # Muestra un mensaje de confirmación


# Inicio de la aplicación
if __name__ == "__main__":
    main()
    load_dotenv()
