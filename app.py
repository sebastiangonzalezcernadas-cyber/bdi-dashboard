import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import shutil
import re
import gdown
import holidays
from datetime import datetime

# ===========================================================
# CONFIGURACIÓN DE PÁGINA Y TEMA CORPORATIVO (BDI CONSULTORA)
# ===========================================================
st.set_page_config(
    page_title="Dashboard de Mensajería | BDI Consultora",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------
# ESTILOS GLOBALES
# -----------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
    .stApp { background-color: #F4F7F6 !important; }
    .stApp p, .stApp span, .stApp label, .stApp div { color: #1A252C; font-family: 'Inter', 'Segoe UI', sans-serif; }
    #MainMenu, footer { visibility: hidden; }

    .bdi-header {
        background: linear-gradient(135deg, #0F5132 0%, #157347 55%, #1F8A5C 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(15, 81, 50, 0.18);
    }
    .bdi-header h1 {
        color: #FFFFFF !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        margin: 0 0 4px 0 !important;
        letter-spacing: -0.3px;
    }
    .bdi-header p {
        color: #DFF3E7 !important;
        font-size: 1rem !important;
        margin: 0 !important;
        font-weight: 400;
    }
    .bdi-header .bdi-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        margin-top: 10px;
        border: 1px solid rgba(255,255,255,0.25);
    }

    section[data-testid="stSidebar"] {
        background-color: #0F5132 !important;
        border-right: 1px solid #0B3D27;
    }
    section[data-testid="stSidebar"] * { color: #F1F7F3 !important; }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-weight: 700 !important; }
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stTabs"] { margin-top: 6px; }
    div[data-testid="stTabs"] button p, div[data-testid="stTabs"] button span {
        color: #4A5D57 !important;
        font-weight: 600 !important;
        font-size: 1.0rem !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p, div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #0F5132 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom: 3px solid #157347 !important; }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #E1E7E4; flex-wrap: wrap; }

    h1, h2, h3, h4, h5, h6, h1 span, h2 span, h3 span { color: #0F5132 !important; background-color: transparent !important; font-weight: 700 !important; }
    h3 { font-size: 1.25rem !important; margin-top: 0.4rem !important; }

    .section-divider { border: none; border-top: 1px solid #DDE5E1; margin: 28px 0 22px 0; }
    .section-tag {
        display: inline-block;
        background-color: #E7F4EC;
        color: #0F5132 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .section-sub { color: #5B6E67 !important; font-size: 0.88rem !important; margin: -4px 0 10px 0 !important; }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5EBE8;
        border-left: 4px solid #157347;
        border-radius: 12px;
        padding: 14px 18px 10px 18px;
        box-shadow: 0 2px 8px rgba(15, 81, 50, 0.06);
    }
    [data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] div {
        color: #5B6E67 !important; font-size: 0.85rem !important; font-weight: 600 !important; text-transform: uppercase;
    }
    [data-testid="stMetricValue"] div { color: #0F5132 !important; font-weight: 800 !important; font-size: 1.9rem !important; }

    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E5EBE8;
        border-radius: 14px;
        padding: 12px 8px 4px 8px;
        box-shadow: 0 2px 10px rgba(15, 81, 50, 0.05);
        margin-bottom: 18px;
    }
    div[data-testid="stDataFrame"] { border: 1px solid #E5EBE8; border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSTANTES Y MAPEOS
# ---------------------------------------------------------
USER_COLORS = {
    'Ruso': '#157347', 'Harry': '#2FA66B', 'BDI': '#3AAFB9',
    'Gian': '#0B3D27', 'Toto': '#5BC49A', 'Mariano': '#A9C9A4', 'Sin Asignar': '#C9D2CE'
}
BROKER_COLORS = {
    'Balanz': '#0B3D66', 'BMB': '#3E92CC', 'IOL': '#D6336C', 'Inviu': '#2FA66B', 'Sin Broker': '#AEB6B2'
}
TIER_COLORS = {
    '0 a 50K USD': '#0F5132', '50 a 100K USD': '#2FA66B', '100k a 250k USD': '#3AAFB9',
    '250k a 500k USD': '#8FBF74', 'Mas de 500k USD': '#C9A227', 'Sin Etiqueta Monto': '#B9C2BD'
}

BROKERS = ['Balanz', 'BMB', 'IOL', 'Inviu']
TIERS = ['0 a 50K USD', '50 a 100K USD', '100k a 250k USD', '250k a 500k USD', 'Mas de 500k USD']
DAY_MAP = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
DAY_ORDER_LABORAL = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

MESES_ES_MAP = {
    1: '01 - Enero', 2: '02 - Febrero', 3: '03 - Marzo', 4: '04 - Abril',
    5: '05 - Mayo', 6: '06 - Junio', 7: '07 - Julio', 8: '08 - Agosto',
    9: '09 - Septiembre', 10: '10 - Octubre', 11: '11 - Noviembre', 12: '12 - Diciembre'
}

NOMBRE_A_NUM = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'setiembre': 9, 'octubre': 10,
    'noviembre': 11, 'diciembre': 12
}

DRIVE_FOLDER_ID = "1CYKA6e2R_enmSVHpTrUdCFyGiZ_pKZH2"
EXCLUIR_CONTACTOS = ['Soporte IOL', 'Caroline Pascuzzi - Soporte IOL', 'Caroline Pascuzzi - Soporte Inviu']

# -----------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------
def apply_bdi_theme(fig, legend_below=False):
    fig.update_layout(
        font=dict(family='Inter, Segoe UI, sans-serif', color='#1A252C', size=13),
        title=dict(font=dict(color='#0F5132', size=17), x=0.01, xanchor='left'),
        xaxis=dict(title_font=dict(color='#3F4F49', size=13), tickfont=dict(color='#4A5D57'), gridcolor='#EAF0ED'),
        yaxis=dict(title_font=dict(color='#3F4F49', size=13), tickfont=dict(color='#4A5D57'), gridcolor='#EAF0ED'),
        legend=dict(
            title_font=dict(color='#0F5132', size=12), font=dict(color='#3F4F49', size=12),
            orientation='h' if legend_below else 'v', yanchor='top', y=-0.18 if legend_below else 1,
            xanchor='center' if legend_below else 'left', x=0.5 if legend_below else 1.02,
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=50, l=50, r=40), bargap=0.25,
        hoverlabel=dict(bgcolor='#0F5132', font_color='white', font_size=12)
    )
    fig.update_traces(textposition='auto', textfont=dict(size=12), selector=dict(type="bar"))
    fig.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)), selector=dict(type="pie"))
    return fig

def section_header(tag, title, subtitle=None):
    sub_html = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(f'<div class="section-tag">{tag}</div><h3 style="margin-top:0;">{title}</h3>{sub_html}', unsafe_allow_html=True)

def add_reference_line(fig, value, orientation='v', label='Promedio'):
    if pd.isna(value): return fig
    if orientation == 'v':
        fig.add_vline(x=value, line_width=2, line_dash="dot", line_color="#C9A227",
                      annotation_text=f"{label}: {value:.1f}", annotation_position="top right",
                      annotation_font=dict(color="#8A6D00", size=11))
    else:
        fig.add_hline(y=value, line_width=2, line_dash="dot", line_color="#C9A227",
                      annotation_text=f"{label}: {value:.1f}", annotation_position="top left",
                      annotation_font=dict(color="#8A6D00", size=11))
    return fig

def divider():
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

def time_str_to_minutes(val):
    if pd.isna(val) or not isinstance(val, str): return np.nan
    try:
        parts = val.split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 60 + m + (s / 60.0)
    except:
        return np.nan
    return np.nan

def extract_brokers(tag_str):
    if pd.isna(tag_str): return []
    tags = [t.strip() for t in str(tag_str).split(',')]
    return [b for b in BROKERS if any(b.lower() == t.lower() or b.lower() in t.lower() for t in tags)]

def extract_tier(tag_str):
    if pd.isna(tag_str): return 'Sin Etiqueta Monto'
    tags = [t.strip() for t in str(tag_str).split(',')]
    for tier in TIERS:
        if any(tier.lower() in t.lower() for t in tags): return tier
    return 'Sin Etiqueta Monto'

def extract_month_from_filename(filename):
    fn = os.path.basename(filename).lower()
    for name, num in NOMBRE_A_NUM.items():
        if name in fn:
            return MESES_ES_MAP[num]
    match = re.search(r'^\s*(\d{1,2})[\s_-]', fn)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 12:
            return MESES_ES_MAP[num]
    return 'Mes No Especificado'

# -----------------------------------------------------------
# CARGA Y DESCARGA DINÁMICA DE DATOS
# -----------------------------------------------------------
@st.cache_data(ttl=300)
def cargar_datos_drive():
    output_dir = "./data_drive"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        folder_url = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"
        gdown.download_folder(url=folder_url, output=output_dir, quiet=True, use_cookies=False, remaining_ok=True)
    except Exception:
        pass

    all_files = glob.glob(os.path.join(output_dir, "**", "*.xlsx"), recursive=True)
    if not all_files:
        return pd.DataFrame()

    dfs = []
    for file in sorted(all_files):
        try:
            df_temp = pd.read_excel(file)
            df_temp['archivo_origen'] = os.path.basename(file)
            df_temp['mes_archivo'] = extract_month_from_filename(file)
            dfs.append(df_temp)
        except Exception:
            continue

    if not dfs: return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)

    df = df[~df['contactName'].isin(EXCLUIR_CONTACTOS)]

    df['createdAt_dt'] = pd.to_datetime(df['createdAt'], errors='coerce')
    df['firstSentMessageAt_dt'] = pd.to_datetime(df['firstSentMessageAt'], errors='coerce')

    df['fecha_corta'] = df['createdAt_dt'].dt.date
    
    # Asignación del mes cronológico
    df['mes_nombre'] = df['createdAt_dt'].dt.month.map(MESES_ES_MAP)
    df['mes_nombre'] = df['mes_nombre'].fillna(df['mes_archivo'])

    df['dia_semana'] = df['createdAt_dt'].dt.day_name().map(DAY_MAP)
    df['hora'] = df['createdAt_dt'].dt.hour
    df['hora_30m'] = df['createdAt_dt'].dt.floor('30min').dt.strftime('%H:%M')

    df['FRT_min'] = (df['firstSentMessageAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df['resp_time_wh_min'] = df['workingHoursResponseTime'].apply(time_str_to_minutes)
    df['res_time_wh_min'] = df['workingHoursResolutionTime'].apply(time_str_to_minutes)

    df['brokers'] = df['tags'].apply(extract_brokers)
    df['tier'] = df['tags'].apply(extract_tier)

    df['isNewContact'] = df['isNewContact'].fillna(False).astype(bool)
    df['resolvedByInactivity'] = df['resolvedByInactivity'].fillna(False).astype(bool)

    return df

# ---------------------------------------------------------
# PANEL DE CONTROL LATERAL
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Panel de Control")

if st.sidebar.button("🔄 Sincronizar datos de Google Drive", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

uploaded_files = st.sidebar.file_uploader("📂 O cargar planilla .xlsx:", type=["xlsx"], accept_multiple_files=True)

df_raw = cargar_datos_drive()

if uploaded_files:
    dfs_up = []
    for up_file in uploaded_files:
        try:
            df_temp = pd.read_excel(up_file)
            df_temp['archivo_origen'] = up_file.name
            df_temp['mes_archivo'] = extract_month_from_filename(up_file.name)
            dfs_up.append(df_temp)
        except Exception:
            pass
    if dfs_up:
        df_uploaded = pd.concat(dfs_up, ignore_index=True)
        df_uploaded['createdAt_dt'] = pd.to_datetime(df_uploaded['createdAt'], errors='coerce')
        df_uploaded['firstSentMessageAt_dt'] = pd.to_datetime(df_uploaded['firstSentMessageAt'], errors='coerce')
        df_uploaded['mes_nombre'] = df_uploaded['createdAt_dt'].dt.month.map(MESES_ES_MAP).fillna(df_uploaded['mes_archivo'])
        df_uploaded['dia_semana'] = df_uploaded['createdAt_dt'].dt.day_name().map(DAY_MAP)
        df_uploaded['hora'] = df_uploaded['createdAt_dt'].dt.hour
        df_uploaded['hora_30m'] = df_uploaded['createdAt_dt'].dt.floor('30min').dt.strftime('%H:%M')
        df_uploaded['FRT_min'] = (df_uploaded['firstSentMessageAt_dt'] - df_uploaded['createdAt_dt']).dt.total_seconds() / 60.0
        df_uploaded['resp_time_wh_min'] = df_uploaded['workingHoursResponseTime'].apply(time_str_to_minutes)
        df_uploaded['res_time_wh_min'] = df_uploaded['workingHoursResolutionTime'].apply(time_str_to_minutes)
        df_uploaded['brokers'] = df_uploaded['tags'].apply(extract_brokers)
        df_uploaded['tier'] = df_uploaded['tags'].apply(extract_tier)
        df_uploaded['isNewContact'] = df_uploaded['isNewContact'].fillna(False).astype(bool)
        df_uploaded['resolvedByInactivity'] = df_uploaded['resolvedByInactivity'].fillna(False).astype(bool)

        if not df_raw.empty:
            df_raw = pd.concat([df_raw, df_uploaded], ignore_index=True).drop_duplicates()
        else:
            df_raw = df_uploaded

if df_raw.empty:
    st.error("No se encontraron datos para procesar. Verifique el acceso a Google Drive o cargue los archivos manualmente en el panel lateral.")
    st.stop()

# Feedback de archivos detectados
archivos_cargados = df_raw['archivo_origen'].dropna().unique()
st.sidebar.success(f"📁 **{len(archivos_cargados)} planillas procesadas**")
with st.sidebar.expander("📄 Ver archivos detectados"):
    for a in sorted(archivos_cargados):
        st.write(f"- {a}")

# ---------------------------------------------------------
# FILTROS DINÁMICOS
# ---------------------------------------------------------
st.sidebar.markdown("### 🔎 Filtros de Búsqueda")
meses_disponibles = sorted(df_raw['mes_nombre'].dropna().unique())
meses_sel = st.sidebar.multiselect("Mes:", meses_disponibles, default=meses_disponibles)

asesores_disponibles = sorted(df_raw['user'].dropna().unique())
asesores_sel = st.sidebar.multiselect("Asesor:", asesores_disponibles, default=asesores_disponibles)

df = df_raw.copy()
if meses_sel: df = df[df['mes_nombre'].isin(meses_sel)]
if asesores_sel: df = df[df['user'].isin(asesores_sel)]

# ---------------------------------------------------------
# HEADER PRINCIPAL Y KPIs
# ---------------------------------------------------------
st.markdown(f"""
<div class="bdi-header">
    <h1>📈 Dashboard de Gestión de Mensajería</h1>
    <p>BDI Consultora — Consolidado analítico de conversaciones, rendimiento operativo y distribución patrimonial.</p>
    <span class="bdi-badge">Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Chats", f"{len(df):,}")
kpi2.metric("Contactos Únicos", f"{df['contactNumber'].nunique():,}")
kpi3.metric("Nuevos Contactos", f"{df['isNewContact'].sum():,}")
kpi4.metric("FRT Mediano", f"{df['FRT_min'].median():.1f} min" if not df['FRT_min'].dropna().empty else "s/d")
kpi5.metric("Cierre Inactividad", f"{df['resolvedByInactivity'].sum():,}")

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅  Evolución y Temporalidad",
    "💼  Brokers y Patrimonio",
    "👥  Clientes",
    "🧑‍💼  Actividad por Usuario",
    "🧩  Fricción y Complejidad"
])

# ---------------------------------------------------------
# TAB 1: EVOLUCIÓN Y TEMPORALIDAD
# ---------------------------------------------------------
with tab1:
    section_header("VOLUMEN", "Evolución de Chats en el Tiempo")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        df_mes = df.groupby('mes_nombre').size().reset_index(name='Chats')
        df_mes = df_mes.sort_values('mes_nombre')
        fig_mes = px.bar(
            df_mes, x='mes_nombre', y='Chats', text='Chats',
            color_discrete_sequence=['#157347'], title="Evolución Mensual de Chats",
            category_orders={'mes_nombre': meses_disponibles}
        )
        fig_mes.update_traces(textposition='outside')
        fig_mes = apply_bdi_theme(fig_mes)
        fig_mes.update_layout(xaxis_title="Mes", yaxis_title="Cantidad de Chats")
        st.plotly_chart(fig_mes, use_container_width=True)

    with col_t2:
        df_dias = df['dia_semana'].value_counts().reindex(DAY_ORDER_LABORAL).fillna(0).reset_index()
        df_dias.columns = ['Día', 'Chats']
        fig_dias = px.bar(
            df_dias, x='Día', y='Chats', text='Chats',
            color_discrete_sequence=['#2FA66B'], title="Distribución de Chats (Lunes a Viernes)"
        )
        fig_dias.update_traces(textposition='outside')
        fig_dias = apply_bdi_theme(fig_dias)
        fig_dias.update_layout(xaxis_title="Día", yaxis_title="Cantidad de Chats")
        st.plotly_chart(fig_dias, use_container_width=True)

    section_header("CARGA HORARIA", "Distribución de Consultas por Hora")
    df_hora = df.groupby('hora').size().reset_index(name='Chats')
    fig_hora = px.area(
        df_hora, x='hora', y='Chats', markers=True,
        color_discrete_sequence=['#3AAFB9'], title="Carga Horaria General (Franja de 0 a 23 hs)"
    )
    fig_hora.update_traces(marker=dict(size=8, color='#0F5132'), fillcolor='rgba(58,175,185,0.15)', line=dict(color='#0F5132'))
    fig_hora = apply_bdi_theme(fig_hora)
    fig_hora.update_layout(xaxis_title="Hora del día", yaxis_title="Cantidad de Chats", xaxis=dict(dtick=1))
    st.plotly_chart(fig_hora, use_container_width=True)

    df_hora_30 = df[(df['hora'] >= 8) & (df['hora'] <= 18)].groupby('hora_30m').size().reset_index(name='Chats')
    fig_hora_30 = px.area(
        df_hora_30, x='hora_30m', y='Chats', markers=True,
        color_discrete_sequence=['#157347'], title="Carga Horaria Comercial (08:00 a 18:00 hs · Intervalos de 30 min)"
    )
    fig_hora_30.update_traces(marker=dict(size=8, color='#0F5132'), fillcolor='rgba(21,115,71,0.15)', line=dict(color='#0F5132'))
    fig_hora_30 = apply_bdi_theme(fig_hora_30)
    fig_hora_30.update_layout(xaxis_title="Franja horaria", yaxis_title="Cantidad de Chats", xaxis=dict(tickangle=-45))
    st.plotly_chart(fig_hora_30, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: BROKERS Y PATRIMONIO
# ---------------------------------------------------------
with tab2:
    df_exp = df.explode('brokers')
    df_exp['brokers'] = df_exp['brokers'].fillna('Sin Broker')

    section_header("VOLUMEN TOTAL", "Análisis Global (Basado en Cantidad de Chats)")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        broker_counts = df_exp['brokers'].value_counts().reset_index()
        broker_counts.columns = ['Broker', 'Chats']
        fig_broker = px.pie(
            broker_counts, values='Chats', names='Broker', hole=0.45,
            color='Broker', color_discrete_map=BROKER_COLORS,
            title="Participación Global por Broker"
        )
        fig_broker.update_traces(textinfo='percent', textposition='inside')
        fig_broker = apply_bdi_theme(fig_broker, legend_below=True)
        st.plotly_chart(fig_broker, use_container_width=True)

    with col_b2:
        tier_counts = df['tier'].value_counts().reset_index()
        tier_counts.columns = ['Segmento', 'Chats']
        fig_tier = px.pie(
            tier_counts, values='Chats', names='Segmento', hole=0.45,
            color='Segmento', color_discrete_map=TIER_COLORS,
            title="Distribución Global por Segmento Patrimonial",
            category_orders={'Segmento': TIERS + ['Sin Etiqueta Monto']}
        )
        fig_tier.update_traces(textinfo='percent', textposition='inside')
        fig_tier = apply_bdi_theme(fig_tier, legend_below=True)
        st.plotly_chart(fig_tier, use_container_width=True)

    divider()

    section_header("CARTERA EFECTIVA", "Análisis Excluyendo Registros sin Datos")
    col_b3, col_b4 = st.columns(2)
    with col_b3:
        broker_counts_filt = df_exp[df_exp['brokers'] != 'Sin Broker']['brokers'].value_counts().reset_index()
        broker_counts_filt.columns = ['Broker', 'Chats']
        fig_broker_filt = px.pie(
            broker_counts_filt, values='Chats', names='Broker', hole=0.45,
            color='Broker', color_discrete_map=BROKER_COLORS,
            title="Participación de Brokers Activos"
        )
        fig_broker_filt.update_traces(textinfo='percent', textposition='inside')
        fig_broker_filt = apply_bdi_theme(fig_broker_filt, legend_below=True)
        st.plotly_chart(fig_broker_filt, use_container_width=True)

    with col_b4:
        tier_counts_filt = df[df['tier'] != 'Sin Etiqueta Monto']['tier'].value_counts().reset_index()
        tier_counts_filt.columns = ['Segmento', 'Chats']
        fig_tier_filt = px.pie(
            tier_counts_filt, values='Chats', names='Segmento', hole=0.45,
            color='Segmento', color_discrete_map=TIER_COLORS,
            title="Segmentación Patrimonial Activa",
            category_orders={'Segmento': TIERS}
        )
        fig_tier_filt.update_traces(textinfo='percent', textposition='inside')
        fig_tier_filt = apply_bdi_theme(fig_tier_filt, legend_below=True)
        st.plotly_chart(fig_tier_filt, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: CLIENTES
# ---------------------------------------------------------
with tab3:
    section_header("RANKING", "Top 10 Clientes con Mayor Interacción")
    df_clients_all = df.groupby(['contactName', 'contactNumber']).agg(
        Total_Chats=('chatId', 'count'),
        Asesor_Habitual=('user', lambda x: x.mode()[0] if not x.empty else ''),
        Segmento_Monto=('tier', lambda x: x.mode()[0] if not x.empty else '')
    ).reset_index()

    df_top10 = df_clients_all.sort_values('Total_Chats', ascending=False).head(10).sort_values('Total_Chats', ascending=True)

    fig_top10 = px.bar(
        df_top10, x='Total_Chats', y='contactName', orientation='h', text='Total_Chats',
        color='Asesor_Habitual', color_discrete_map=USER_COLORS,
        title="Top 10 Clientes (Color = Asesor Principal)"
    )
    fig_top10.update_traces(textposition='outside', cliponaxis=False)
    fig_top10 = apply_bdi_theme(fig_top10, legend_below=True)
    fig_top10.update_layout(height=600, margin=dict(t=60, b=90, l=140, r=60))
    st.plotly_chart(fig_top10, use_container_width=True)

    divider()

    section_header("BASE DE CLIENTES", "Listado Completo e Interactivo")
    search_query = st.text_input("🔍 Buscador de clientes (nombre o número telefónico):", "")
    df_filtered_clients = df_clients_all.copy().sort_values('Total_Chats', ascending=False)

    if search_query:
        mask = (
            df_filtered_clients['contactName'].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered_clients['contactNumber'].astype(str).str.contains(search_query, case=False, na=False)
        )
        df_filtered_clients = df_filtered_clients[mask]

    st.caption(f"Mostrando **{len(df_filtered_clients):,}** clientes registrados.")
    st.dataframe(
        df_filtered_clients.rename(columns={
            'contactName': 'Nombre del Cliente', 'contactNumber': 'Número de Teléfono',
            'Total_Chats': 'Total Chats', 'Asesor_Habitual': 'Asesor Principal', 'Segmento_Monto': 'Segmento Patrimonial'
        }),
        use_container_width=True, hide_index=True, height=420
    )

# ---------------------------------------------------------
# TAB 4: ACTIVIDAD POR USUARIO Y EFICIENCIA OPERATIVA
# ---------------------------------------------------------
with tab4:
    section_header("EFICIENCIA", "Desempeño Operativo por Asesor")

    total_general_chats = len(df)

    if not df.empty and not df['createdAt_dt'].dropna().empty:
        min_date = df['createdAt_dt'].min().date()
        max_date = df['createdAt_dt'].max().date()
        years = df['createdAt_dt'].dt.year.dropna().unique().tolist()
        years = [int(y) for y in years if y > 2000]
        ar_holidays = holidays.AR(years=years) if years else holidays.AR()

        all_dates = pd.date_range(start=min_date, end=max_date)
        dias_laborales = [d for d in all_dates if d.weekday() < 5 and d.date() not in ar_holidays]
        base_dias = len(dias_laborales) if len(dias_laborales) > 0 else 1
    else:
        base_dias = 1

    st.caption(f"📅 **Base de cálculo temporal:** {base_dias} días hábiles (excluye fines de semana y feriados de Argentina) · Jornada de 8 hs.")

    df_user_eff = df.groupby('user').agg(
        Total_Chats=('chatId', 'count'),
        FRT_Mediano_Min=('FRT_min', 'median'),
        Contactos_Nuevos=('isNewContact', 'sum')
    ).reset_index()

    df_user_eff['Participación (%)'] = (df_user_eff['Total_Chats'] / total_general_chats * 100) if total_general_chats > 0 else 0
    df_user_eff['Contactos Nuevos (%)'] = (df_user_eff['Contactos_Nuevos'] / df_user_eff['Total_Chats'] * 100)
    df_user_eff['Chats / Día'] = df_user_eff['Total_Chats'] / base_dias
    df_user_eff['Chats / Hora (8hs)'] = df_user_eff['Chats / Día'] / 8.0

    df_user_eff = df_user_eff.sort_values('Total_Chats', ascending=False)

    df_table_eff = df_user_eff[['user', 'Total_Chats', 'Participación (%)', 'FRT_Mediano_Min',
                                'Chats / Día', 'Chats / Hora (8hs)',
                                'Contactos_Nuevos', 'Contactos Nuevos (%)']].copy()

    df_table_eff.columns = ['Asesor', 'Total Chats', 'Participación (%)', 'FRT Mediano (Min)',
                            'Chats / Día', 'Chats / Hora (8hs)', 'Nuevos Contactos (#)', 'Nuevos Contactos (%)']

    st.dataframe(
        df_table_eff.style.format({
            'Participación (%)': '{:.1f}%', 'FRT Mediano (Min)': '{:.1f}',
            'Chats / Día': '{:.1f}', 'Chats / Hora (8hs)': '{:.1f}',
            'Nuevos Contactos (%)': '{:.1f}%'
        }),
        use_container_width=True, hide_index=True
    )

    divider()

    section_header("PARTICIPACIÓN", "Distribución de la Carga Operativa")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        fig_pie = px.pie(
            df_user_eff, names='user', values='Total_Chats',
            title="Tasa de Participación Operativa (% de Chats Totales)",
            color='user', color_discrete_map=USER_COLORS, hole=0.4
        )
        fig_pie.update_traces(textinfo='percent', textposition='inside')
        fig_pie = apply_bdi_theme(fig_pie, legend_below=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_u2:
        fig_frt = px.bar(
            df_user_eff.sort_values('FRT_Mediano_Min'), x='FRT_Mediano_Min', y='user',
            orientation='h', text='FRT_Mediano_Min',
            color='user', color_discrete_map=USER_COLORS,
            title="Tiempo de Primera Respuesta Mediano por Asesor (min)"
        )
        fig_frt.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_frt = apply_bdi_theme(fig_frt)
        fig_frt.update_layout(showlegend=False, xaxis_title="Minutos", yaxis_title="")
        st.plotly_chart(fig_frt, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: FRICCIÓN Y COMPLEJIDAD
# ---------------------------------------------------------
with tab5:
    df_exp_5 = df.explode('brokers')
    df_exp_5['brokers'] = df_exp_5['brokers'].fillna('Sin Broker')

    section_header("RESUMEN EJECUTIVO", "Fricción y Complejidad de un Vistazo")
    contactos_unicos = df['contactNumber'].nunique()
    ratio_global = (len(df) / contactos_unicos) if contactos_unicos > 0 else np.nan
    res_time_prom = df['res_time_wh_min'].mean()

    df_brk_ratio_kpi = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers').agg(
        Chats=('chatId', 'count'), Usuarios=('contactNumber', 'nunique')
    )
    df_brk_ratio_kpi['Ratio'] = df_brk_ratio_kpi['Chats'] / df_brk_ratio_kpi['Usuarios']
    broker_mas_dependiente = df_brk_ratio_kpi['Ratio'].idxmax() if not df_brk_ratio_kpi.empty else "—"

    df_tier_frt_kpi = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median()
    segmento_mas_lento = df_tier_frt_kpi.idxmax() if not df_tier_frt_kpi.empty else "—"

    kf1, kf2, kf3, kf4 = st.columns(4)
    kf1.metric("Ratio Global de Fricción", f"{ratio_global:.2f} chats/cliente" if pd.notna(ratio_global) else "s/d")
    kf2.metric("Resolución Promedio", f"{res_time_prom:.0f} min" if pd.notna(res_time_prom) else "s/d")
    kf3.metric("Broker Más Dependiente", broker_mas_dependiente)
    kf4.metric("Segmento Más Lento (FRT)", segmento_mas_lento)

    divider()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        df_fric_broker = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers').agg(
            Chats=('chatId', 'count'), Usuarios=('contactNumber', 'nunique')
        ).reset_index()
        df_fric_broker['Ratio'] = df_fric_broker['Chats'] / df_fric_broker['Usuarios']

        fig_fric_b = px.bar(
            df_fric_broker.sort_values('Ratio', ascending=True), x='Ratio', y='brokers', orientation='h', text='Ratio',
            color='brokers', color_discrete_map=BROKER_COLORS,
            title="Ratio de Chats por Usuario (por Broker)"
        )
        fig_fric_b.update_traces(texttemplate='%{text:.2f} chats/usr', textposition='outside', cliponaxis=False)
        fig_fric_b = add_reference_line(fig_fric_b, df_fric_broker['Ratio'].mean(), orientation='v')
        fig_fric_b = apply_bdi_theme(fig_fric_b)
        st.plotly_chart(fig_fric_b, use_container_width=True)

    with col_f2:
        df_fric_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier').agg(
            Chats=('chatId', 'count'), Usuarios=('contactNumber', 'nunique')
        ).reset_index()
        df_fric_tier['Ratio'] = df_fric_tier['Chats'] / df_fric_tier['Usuarios']

        fig_fric_t = px.bar(
            df_fric_tier, x='Ratio', y='tier', orientation='h', text='Ratio',
            color='tier', color_discrete_map=TIER_COLORS, category_orders={'tier': TIERS},
            title="Ratio de Chats por Usuario (por Patrimonio)"
        )
        fig_fric_t.update_traces(texttemplate='%{text:.2f} chats/usr', textposition='outside', cliponaxis=False)
        fig_fric_t = add_reference_line(fig_fric_t, df_fric_tier['Ratio'].mean(), orientation='v')
        fig_fric_t = apply_bdi_theme(fig_fric_t)
        st.plotly_chart(fig_fric_t, use_container_width=True)
