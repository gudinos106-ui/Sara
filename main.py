import streamlit as st
import pdfplumber
import pandas as pd
import plotly.express as px
import os
import base64
import utils
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
# Importamos las herramientas
from utils import enviar_telegram, limpiar_monto, categorizar

# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv(dotenv_path=".env.py")
st.set_page_config(page_title="BCR MoneyTracker Gold", page_icon="💰", layout="wide")

# Validación de datos con Pydantic
class MovimientoBCR(BaseModel):
    concepto: str
    monto: float = Field(gt=0, description="El monto debe ser mayor a cero")

# --- 2. DISEÑO DE INTERFAZ (¡RECUPERANDO EL FONDO!) ---
# Esta es la función que hace la magia visual
def set_background(png_file):
    try:
        with open(png_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        # Aquí recuperamos tus estilos originales y los mejoramos un poco
        st.markdown(f'''
        <style>
        /* Fondo de pantalla completo */
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}

        /* Títulos estilizados (Fondo oscuro, texto dorado, borde lateral) */
        h1, h2, h3 {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            color: #FFFFFF !important; /* Color Dorado */
            padding: 10px 20px !important;
            border-radius: 12px !important;
            border-left: 6px solid #FFD700 !important; /* Detalle dorado para el toque 'Gold' */
            text-shadow: 2px 2px 4px rgba(0,0,0,1) !important; /* Sombra negra para que la letra 'salte' */
            width: fit-content !important;
            margin-bottom: 20px !important;
        }}
        
        /* Contenedores blancos y nítidos para datos */
        .stMetric, .stDataFrame, [data-testid="stTable"], .stTable, .stExpander, .stTabs {{
            background-color: rgba(255, 255, 255, 1.0) !important;
            padding: 15px;
            border-radius: 15px;
            color: black !important;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            border: 1px solid #FFD700;
        }}

        /* Ajuste de color para los labels de métricas */
        [data-testid="stMetricLabel"] {{
            color: #2E4053 !important;
        }}

        /* Tablas y otros contenedores en blanco para lectura clara */
        .stDataFrame, [data-testid="stTable"], .stTable, .stExpander, .stTabs {{
        background-color: rgba(255, 255, 255, 1.0) !important;
        padding: 15px;
        border-radius: 15px;
        color: black !important;

        }}      

        </style>
        ''', unsafe_allow_html=True)
    except:
        # Si no encuentra la imagen, no hace nada pero no rompe el programa
        pass

# Buscamos la imagen de fondo (asegúrate de que el nombre sea correcto)
if os.path.exists("fondo_tarjeta.png"):
    set_background("fondo_tarjeta.png")
else:
    st.warning("⚠️ No se encontró la imagen 'fondo_tarjeta.png'. El fondo será predeterminado.")

# --- 3. SIDEBAR (PERFIL Y CONFIGURACIÓN) ---
with st.sidebar:
    st.markdown("### 👩‍💻 Perfil de Usuario")
    nombre_usuario = st.text_input("¿Quién analiza hoy?", value="Sara")
    presupuesto_limite = st.number_input("Presupuesto Mensual (₡)", min_value=0.0, value=200000.0, step=1000.0)
    archivo = st.file_uploader("Sube tu PDF del BCR", type=['pdf'], key="sidebar_pdf")
    dia_corte = st.number_input("Día de Pago Mensual", min_value=1, max_value=31, value=15)
    st.markdown("---")
    st.info("💡 Consejo: Revisa la pestaña 'Gráficos' para ver en qué gastas más.")

# --- 4. TÍTULO PRINCIPAL ---
# El título 
st.title(f"🛡️ MoneyTracker: Estado de Cuenta Inteligente")

# --- 5. LÓGICA DE RECORDATORIO (Días de pago) ---
hoy = datetime.now()
try:
    fecha_pago_mes = datetime(hoy.year, hoy.month, int(dia_corte))
    dias_faltantes = (fecha_pago_mes - hoy).days + 1
    if hoy.day == int(dia_corte):
        st.error(f"🔔 **URGENTE:** Hoy es tu día de pago, {nombre_usuario}.")
    elif 0 < dias_faltantes <= 3:
        st.info(f"📅 **RECORDATORIO:** Tu fecha de pago es en {dias_faltantes} días.")
except:
    pass

# --- 6. LÓGICA PRINCIPAL (PDF) ---
if archivo:
    with st.spinner("Anatizando tus finanzas..."):
        datos_totales = []
        with pdfplumber.open(archivo) as pdf:
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if tabla: datos_totales.extend(tabla)

        if datos_totales:
            # Creamos el DataFrame
            df = pd.DataFrame(datos_totales[1:], columns=datos_totales[0])
            # Limpiamos nombres de columnas
            df.columns = [str(col).strip().upper() for col in df.columns if col]

            # Renombramos columnas comunes del BCR a nuestro estándar
            columnas_dict = {'DESCRIPCION': 'CONCEPTO', 'IMPORTE': 'MONTO', 'VALOR': 'MONTO', 'MOVIMIENTO': 'CONCEPTO'}
            df = df.rename(columns=columnas_dict)

            if 'MONTO' in df.columns:
                # Limpiamos y convertimos los montos usando la función en utils.py
                df['MONTO'] = df['MONTO'].apply(limpiar_monto)

                # --- VALIDACIÓN CON PYDANTIC ---
                movimientos_validados = []
                for index, fila in df.iterrows():
                    try:
                        # Pydantic asegura que 'monto' sea > 0
                        datos_validados = MovimientoBCR(
                            concepto=str(fila['CONCEPTO']),
                            monto=fila['MONTO']
                        )
                        movimientos_validados.append(datos_validados)
                    except ValidationError:
                        # Si la línea está corrupta o el monto es 0, la ignoramos
                        continue
                         # Si tenemos datos válidos, continuamos
                if movimientos_validados:
                    # Convertimos la lista de modelos Pydantic de vuelta a DataFrame
                    df_final = pd.DataFrame([m.model_dump() for m in movimientos_validados])
                    # Categorizamos usando la función en utils.py
                    df_final['CATEGORÍA'] = df_final['concepto'].apply(categorizar)

                    total_gastado = df_final['monto'].sum()
                    saldo_final = presupuesto_limite - total_gastado

                    # --- DASHBOARD (MÉTRICAS RESALTADAS) ---
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Usamos delta para mostrar el gasto acumulado
                        st.metric("💰 Gasto Total", f"₡ {total_gastado:,.2f}", delta=f"Total: ₡ {total_gastado:,.2f}", delta_color="inverse")

                    with col2:
                        st.metric("🏦 Presupuesto Meta", f"₡ {presupuesto_limite:,.2f}")

                    with col3:
                        # Color dinámico para el saldo restante
                        color_delta = "normal" if saldo_final >= 0 else "inverse"
                        st.metric("✅ Saldo Restante", f"₡ {saldo_final:,.2f}", delta=f"{saldo_final:,.2f}", delta_color=color_delta)

                    st.divider()

                    # --- SECCIÓN DE ALERTAS Y DATOS ---

                    # 1. Alerta de Duplicados (Lógica Inteligente)
                    df_dups = df_final[df_final.duplicated(subset=['concepto', 'monto'], keep=False)]
                    if not df_dups.empty:
                        st.error(f"⚠️ ¡Atención! Se detectaron {len(df_dups)} posibles cobros duplicados.")
                        with st.expander("Ver detalle de duplicados"):
                            st.dataframe(df_dups, use_container_width="stretch")

                        # Alerta automática a Telegram si hay duplicados
                        if 'alerta_duplicados_enviada' not in st.session_state:
                            mensaje_bot = (
                                f"🚨 *Alerta BCR ({nombre_usuario})*\n\n"
                                f"Se detectaron posibles duplicados:\n"
                                f"{df_dups[['concepto', 'monto']].to_string(index=False)}"
                            )
                            if utils.enviar_telegram(mensaje_bot):
                                st.toast("Alerta de duplicados enviada a Telegram 📲")
                                st.session_state['alerta_duplicados_enviada'] = True

                    # 2. Pestañas para organizar la visualización
                    tab1, tab2 = st.tabs(["📊 Análisis de Distribución", "📋 Lista de Movimientos"])

                    with tab1:
                        st.subheader("¿A dónde se va tu dinero?")
                        # Agrupamos por categoría para el gráfico
                        df_grafico = df_final.groupby('CATEGORÍA')['monto'].sum().reset_index()
                        # Creamos gráfico de pastel (Donut chart) con Plotly
                        fig = px.pie(df_grafico, values='monto', names='CATEGORÍA',
                                    hole=0.5, # Hace el hueco central (donut)
                                    title="Distribución de Gastos por Categoría",
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                        st.plotly_chart(fig, width="stretch")

                    with tab2:
                        st.subheader("Detalle Completo de Transacciones")
                        st.dataframe(df_final, width="stretch")

                    # --- 7. EXPORTAR DATOS ---
                    st.divider()
                    st.subheader("📥 Exportar Resultados")
                    # Generamos el CSV en memoria
                    csv_data = df_final.to_csv(index=False).encode('utf-8-sig')

                    col_down1, col_down2 = st.columns([1,3])
                    with col_down1:
                        st.download_button(
                            label="Descargar Reporte en CSV",
                            data=csv_data,
                            file_name=f'Reporte_Gastos_{nombre_usuario}_{hoy.strftime("%Y%m%d")}.csv',
                            mime='text/csv',
                        )
                    with col_down2:
                        st.info("El archivo CSV se puede abrir en Excel para análisis históricos.")

                else:
                    st.error("No se pudieron extraer movimientos válidos del PDF. Revisa el formato.")
            else:
                st.error("No se encontró la columna 'MONTO' o 'IMPORTE' en el PDF.")
        else:
            st.error("No se pudieron extraer tablas del archivo PDF subido.")
else:
    # Mensaje de bienvenida si no hay archivo
    st.info(f"👋 ¡Hola {nombre_usuario}! Sube tu estado de cuenta del BCR en la barra lateral para empezar el análisis inteligente.")

# --- 8. BOTÓN DE PRUEBA DE CONEXIÓN (Siempre visible) ---
st.divider()
with st.expander("🛠️ Herramientas de Conexión"):
    if utils.enviar_telegram(f"¡Hola {nombre_usuario}! 💰 Tu MoneyTracker ya está conectado y listo para analizar tus estados de cuenta. 📊"):
            resultado = utils.enviar_telegram(f"Abriste tu App")
            if resultado:
                st.success("¡Enviado!")
            else:
                # ESTO NOS DIRÁ EL ERROR REAL EN LA PANTALLA
                st.error(f"Error detectado: Revisa la consola negra para ver el detalle.")
                print("--- DETALLE DEL ERROR PARA SARA ---")
