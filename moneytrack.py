import streamlit as st
import pdfplumber
import pandas as pd
from fpdf import FPDF, XPos, YPos
import plotly.express as px
import os
import base64
import utils
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
# Importamos las herramientas
from utils import enviar_telegram, limpiar_monto, categorizar


st.set_page_config(
    page_title="MoneyTrack Gold",
    layout="wide", 
    initial_sidebar_state="expanded"
)

def generar_pdf_reporte(nombre, total, saldo, resumen_gastos, df_final):
    pdf = FPDF()
    pdf.add_page()
    def limpiar(t): return str(t).encode('latin-1', 'ignore').decode('latin-1')

    # --- ENCABEZADO AZUL (EL "GOLD") ---
    pdf.set_fill_color(44, 62, 80)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 22)
    pdf.cell(190, 15, text=limpiar("MONEYTRACK GOLD"), align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(190, 10, text=limpiar(f"Informe para: {nombre} | Fecha: {datetime.now().strftime('%d/%m/%Y')}"), align='C', new_x="LMARGIN", new_y="NEXT")
    
    # --- CONTENIDO ---
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(95, 10, text=f"Total Gastado: CRC {total:,.2f}", border='B')
    pdf.cell(95, 10, text=f"Saldo: CRC {saldo:,.2f}", border='1', align='R', new_x="LMARGIN", new_y="NEXT")
    
    # Resumen Categorías 
    pdf.ln(5)
    pdf.set_fill_color(255, 215, 0) # Dorado
    pdf.cell(190, 10, text=limpiar("RESUMEN POR CATEGORÍA"), border='B', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", '', 9)
    for cat, monto in resumen_gastos.items():
        pdf.cell(140, 7, text=limpiar(cat), border=1)
        pdf.cell(50, 7, text=f"C {monto:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT")
        
    # --- NOTA FINAL ---
  # --- SECCIÓN DE ANÁLISIS INTELIGENTE ---
    pdf.ln(10)
    pdf.set_fill_color(44, 62, 80) # Azul oscuro
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(190, 10, text=limpiar("DIAGNÓSTICO DE SALUD FINANCIERA"), border=0, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", '', 10)
    pdf.ln(2)

    # 1. Cálculo de porcentaje de uso
    porcentaje_uso = (total / presupuesto_limite) * 100 if presupuesto_limite > 0 else 0
    
    # 2. Lógica de consejos automáticos
    if porcentaje_uso <= 80:
        diagnostico = f"¡Excelente gestión! Has consumido solo el {porcentaje_uso:.1f}% de tu presupuesto. Tienes un margen de ahorro saludable."
    elif 80 < porcentaje_uso <= 100:
        diagnostico = f"Cuidado: Has consumido el {porcentaje_uso:.1f}% de tu presupuesto. Estás cerca del límite establecido."
    else:
        diagnostico = f"Alerta: Has excedido tu presupuesto en un {porcentaje_uso-100:.1f}%. Se recomienda revisar los gastos en 'Banco' y 'Avances'."

    pdf.multi_cell(190, 7, text=limpiar(diagnostico), border='L')
    pdf.ln(5)

    # 3. Identificación del "Fugitivo de Dinero" (Top Gasto)
    if resumen_para_pdf:
        # Buscamos la categoría más alta pero ignoramos "Pago de Tarjeta" porque no es un gasto real
        gastos_reales = {k: v for k, v in resumen_para_pdf.items() if "Pago" not in k}
        if gastos_reales:
            top_cat = max(gastos_reales, key=gastos_reales.get)
            monto_top = gastos_reales[top_cat]
            consejo_top = f"Tu mayor salida de dinero fue en {top_cat} (₡ {monto_top:,.2f})."
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(190, 8, text=limpiar(f"📍 Punto de Atención: {consejo_top}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- PIE DE PÁGINA PROFESIONAL ---BORRA
    pdf.set_y(-30)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, text=limpiar("Este informe es un análisis automatizado generado por MoneyTrack Gold para uso personal.Programadora Sara Gudino"), align='C')
    
    return bytes(pdf.output())

# --- SISTEMA DE SEGURIDAD ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔐 Acceso a MoneyTrack Gold")
        # Tu nombre de usuario y una clave secreta (puedes cambiarlas)
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar"):
            if usuario == "Sara" and clave == "2026": # ¡Tu clave personal!
                st.session_state.autenticado = True
                st.success("¡Bienvenida, Sara! Accediendo al sistema...")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True

# 
if login():
    # AQUÍ VA TODO EL RESTO DE TU CÓDIGO (st.title, st.sidebar, etc.)
    st.sidebar.write(f"Conectada como: Sara Gudiño")
    st.title("MoneyTrack Gold")

def generar_pdf_reclamo(df_dups):
    pdf = FPDF()
    pdf.add_page()
    def limpiar(t): return str(t).encode('latin-1', 'ignore').decode('latin-1')

    # --- DISEÑO SOBRIO (GRIS/OFICIAL) ---
    pdf.set_fill_color(60, 60, 60)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(190, 15, text=limpiar("REPORTE DE DISCREPANCIAS TRANSACCIONALES"), align='C', new_x="LMARGIN", new_y="NEXT")

    # --- CAMPOS PARA LLENAR A MANO (Lo que ideaste) ---
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(190, 8, text=limpiar("DATOS DEL TITULAR (Completar para gestión bancaria):"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(190, 8, text=limpiar("Nombre: __________________________________________________"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(95, 8, text=limpiar("Cédula/ID: _________________"), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(95, 8, text=limpiar("Teléfono: _________________"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(95, 8, text=limpiar("N° Tarjeta (Últimos 4): ________"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(95, 8, text=limpiar("Fecha de Gestión: __/__/2026"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # --- TABLA DE DUPLICADOS ---
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(190, 8, text=limpiar("DETALLE DE CARGOS A REVISAR"), border='B', fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", '', 8)
    pdf.cell(30, 7, text="Fecha", border=1)
    pdf.cell(110, 7, text="Comercio / Concepto", border=1)
    pdf.cell(50, 7, text="Monto (CRC)", border=1, new_x="LMARGIN", new_y="NEXT")

    for _, fila in df_dups.iterrows():
        pdf.cell(30, 7, text=str(fila.get('fecha', 'N/A')), border=1)
        pdf.cell(110, 7, text=limpiar(fila['concepto'])[:50], border=1)
        pdf.cell(50, 7, text=f"{fila['monto']:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT")

    # --- NOTA FINAL ---
    pdf.ln(10)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.multi_cell(190, 5, text=limpiar("OBSERVACIÓN: Se sugiere verificar estos cargos por posible duplicidad. Documento generado como auxiliar para el cliente."))
    
    return bytes(pdf.output())
    
# --- 1. CONFIGURACIÓN INICIAL ---
load_dotenv(dotenv_path=".env.py")
st.set_page_config(page_title="BCR MoneyTracker Gold", page_icon="💰", layout="wide")

# Validación de datos con Pydantic
class MovimientoBCR(BaseModel):
    concepto: str
    monto: float = Field(gt=0, description="El monto debe ser mayor a cero")

# --- 2. DISEÑO DE INTERFAZ ---
def set_background(png_file):
    try:
        with open(png_file, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        h1, h2, h3 {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            color: #FFFFFF !important;
            padding: 10px 20px !important;
            border-radius: 12px !important;
            border-left: 6px solid #FFD700 !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,1) !important;
            width: fit-content !important;
            margin-bottom: 20px !important;
        }}
        .stMetric, .stDataFrame, [data-testid="stTable"], .stTable, .stExpander, .stTabs {{
            background-color: rgba(255, 255, 255, 1.0) !important;
            padding: 15px;
            border-radius: 15px;
            color: black !important;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            border: 1px solid #FFD700;
        }}
        
        [data-testid="stMetricLabel"] {{ color: #2E4053 !important; }}

        
        /* ... AQUÍ EL TRUCO PARA LAS 3 COLUMNAS EN CELULAR - ... */
        [data-testid="column"] {{
            width: 33% !important;
            flex: 1 1 33% !important;
            min-width: 33% !important;
        }}

        [data-testid="stMetricValue"] {{
            font-size: 1.4rem !important;
        }}
        
        </style>
        
        ''', unsafe_allow_html=True)
    except:
        pass

if os.path.exists("fondo_tarjeta.png"):
    set_background("fondo_tarjeta.png")
else:
    st.warning("⚠️ No se encontró la imagen 'fondo_tarjeta.png'.")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 👩‍💻 Perfil de Usuario")
    nombre_usuario = st.text_input("¿Quién analiza hoy?", value="Sara")
    presupuesto_limite = st.number_input("Presupuesto Mensual (₡)", min_value=0.0, value=200000.0, step=1000.0)
    archivo = st.file_uploader("Sube tu PDF del BCR", type=['pdf'], key="sidebar_pdf")
    dia_corte = st.number_input("Día de Pago Mensual", min_value=1, max_value=31, value=15)
    st.markdown("---")
    st.info("💡 Consejo: Revisa la pestaña 'Gráficos' para ver en qué gastas más.")

# --- 4. TÍTULO PRINCIPAL ---
st.title(f"🛡️ MoneyTracker: Estado de Cuenta Inteligente")

# --- 5. LÓGICA DE RECORDATORIO ---
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
    with st.spinner("Analizando tus finanzas..."):
        datos_totales = []
        with pdfplumber.open(archivo) as pdf:
            for pagina in pdf.pages:
                tabla = pagina.extract_table()
                if tabla: datos_totales.extend(tabla)

        if datos_totales:
            df = pd.DataFrame(datos_totales[1:], columns=datos_totales[0])
            df.columns = [str(col).strip().upper() for col in df.columns if col]
            columnas_dict = {'DESCRIPCION': 'CONCEPTO', 'IMPORTE': 'MONTO', 'VALOR': 'MONTO', 'MOVIMIENTO': 'CONCEPTO'}
            df = df.rename(columns=columnas_dict)

            if 'MONTO' in df.columns:
                df['MONTO'] = df['MONTO'].apply(limpiar_monto)
                movimientos_validados = []
                
                for index, fila in df.iterrows():
                    try:
                        datos_validados = MovimientoBCR(
                            concepto=str(fila['CONCEPTO']),
                            monto=fila['MONTO']
                        )
                        movimientos_validados.append(datos_validados)
                    except ValidationError:
                        continue

                if movimientos_validados:
                    df_final = pd.DataFrame([m.model_dump() for m in movimientos_validados])
                    df_final['CATEGORÍA'] = df_final['concepto'].apply(categorizar)

                    total_gastado = df_final['monto'].sum()
                    saldo_final = presupuesto_limite - total_gastado

                    # DASHBOARD
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Gasto Total", f"₡ {total_gastado:,.2f}", delta=f"Total: ₡ {total_gastado:,.2f}", delta_color="inverse")
                    with col2:
                        st.metric("🏦 Presupuesto Meta", f"₡ {presupuesto_limite:,.2f}")
                    with col3:
                        color_delta = "normal" if saldo_final >= 0 else "inverse"
                        st.metric("✅ Saldo Restante", f"₡ {saldo_final:,.2f}", delta=f"{saldo_final:,.2f}", delta_color=color_delta)

                    st.divider()

                    # ALERTAS DUPLICADOS
                    df_dups = df_final[df_final.duplicated(subset=['monto', 'concepto'], keep=False)]
                    if not df_dups.empty:
                        st.error(f"⚠️ ¡Atención! Se detectaron {len(df_dups)} posibles cobros duplicados.")
                        st.dataframe(df_dups, width='stretch')

                        if 'alerta_duplicados_enviada' not in st.session_state:
                            mensaje_bot = f"🚨 *Alerta BCR ({nombre_usuario})*\n\nDuplicados detectados."
                            if utils.enviar_telegram(mensaje_bot):
                                st.toast("Alerta enviada 📲")
                                st.session_state['alerta_duplicados_enviada'] = True

                    # VISUALIZACIÓN GRAFICA
                    tab1, tab2 = st.tabs(["📊 Análisis de Distribución", "📋 Lista de Movimientos"])
                    with tab1:
                        st.subheader("¿A dónde se va tu dinero?")
                        df_grafico = df_final.groupby('CATEGORÍA')['monto'].sum().reset_index()
                        fig = px.pie(df_grafico, values='monto', names='CATEGORÍA', hole=0.5, title="Gastos por Categoría")
                        st.plotly_chart(fig, width='stretch')

                    with tab2:
                        st.subheader("Detalle Completo de Transacciones")
                        st.dataframe(df_final, width='stretch')

                    # 7--- EXPORTAR DATOS ---
                    if not df_final.empty: 
                        st.divider()
                        st.subheader("📥 Exportar Resultados")
                    
                        resumen_para_pdf = df_final.groupby('CATEGORÍA')['monto'].sum().to_dict()
                    
                    # 2. El botón actualizado con los 5 datos que faltan
                        col_down1, col_down2 = st.columns(2)
                        with col_down1:
                            if st.button("📄 Generar Informe Premium PDF"):
                                try:
                                    pdf_gold_bytes = generar_pdf_reporte(
                                        nombre_usuario,
                                        total_gastado,
                                        saldo_final,
                                        resumen_para_pdf,
                                        df_final,
                                    )
                                    st.download_button(
                                        label="Descargar Informe Gold",
                                        data=pdf_gold_bytes,
                                        file_name=f"Informe_BCR_{nombre_usuario}.pdf",
                                        mime="application/pdf"
                                    )
                                    # 2. Generamos el Reporte de Reclamo (Solo si hay duplicados)
                                    if not df_dups.empty:
                                        pdf_reclamo_bytes = generar_pdf_reclamo(df_dups)
                                        st.download_button(
                                            label="⚠️ Descargar Boleta de Reclamo",
                                            data=pdf_reclamo_bytes,
                                            file_name=f"Reclamo_BCR_{nombre_usuario}.pdf",
                                            mime="application/pdf"
                                        )
                                        st.warning("Se detectaron posibles duplicados. Descargue la boleta de reclamo.")
                                    else:
                                        st.success("¡Informe Gold listo! No se detectaron duplicados.")
                                     
                                except Exception as e:
                                    st.error(f"Error PDF: {e}")
                    
                        with col_down2:
                            csv_data = df_final.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                label="📊 Descargar CSV para Excel",
                                data=csv_data,
                                file_name=f"Reporte_{nombre_usuario}.csv",
                                mime="text/csv"
                             )
                    else:
                        st.warning("⚠️ Esperando datos... Por favor, sube un PDF para generar el informe.")
            

# --- 8. BOTÓN DE PRUEBA ---
st.divider()
with st.expander("🛠️ Herramientas"):
    if st.button("Probar Conexión"):
        if utils.enviar_telegram(f"App abierta por {nombre_usuario}"):
            st.success("Conexión OK")
