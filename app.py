import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import shutil
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

    /* Fondo general */
    .stApp { background-color: #F4F7F6 !important; }

    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1A252C;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Ocultar elementos por defecto de Streamlit para look "presentación" */
    #MainMenu, footer { visibility: hidden; }

    /* --------------------- HEADER --------------------- */
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

    /* --------------------- SIDEBAR --------------------- */
    section[data-testid="stSidebar"] {
        background-color: #0F5132 !important;
        border-right: 1px solid #0B3D27;
    }
    section[data-testid="stSidebar"] * {
        color: #F1F7F3 !important;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
    }

    /* --------------------- TABS --------------------- */
    div[data-testid="stTabs"] { margin-top: 6px; }
    div[data-testid="stTabs"] button p, div[data-testid="stTabs"] button span {
        color: #4A5D57 !important;
        font-weight: 600 !important;
        font-size: 1.0rem !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p, div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #0F5132 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 3px solid #157347 !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #E1E7E4;
        flex-wrap: wrap;
    }

    /* --------------------- TÍTULOS DE SECCIÓN --------------------- */
    h1, h2, h3, h4, h5, h6, h1 span, h2 span, h3 span {
        color: #0F5132 !important;
        background-color: transparent !important;
        font-weight: 700 !important;
    }
    h3 { font-size: 1.25rem !important; margin-top: 0.4rem !important; }

    .section-divider {
        border: none;
        border-top: 1px solid #DDE5E1;
        margin: 28px 0 22px 0;
    }
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
    .section-sub {
        color: #5B6E67 !important;
        font-size: 0.88rem !important;
        margin: -4px 0 10px 0 !important;
    }

    /* --------------------- KPI CARDS --------------------- */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5EBE8;
        border-left: 4px solid #157347;
        border-radius: 12px;
        padding: 14px 18px 10px 18px;
        box-shadow: 0 2px 8px rgba(15, 81, 50, 0.06);
        transition: box-shadow 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 6px 16px rgba(15, 81, 50, 0.12);
    }
    [data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] div {
        color: #5B6E67 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        background-color: transparent !important;
    }
    [data-testid="stMetricValue"] div {
        color: #0F5132 !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        background-color: transparent !important;
    }

    /* --------------------- CHART CARDS --------------------- */
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E5EBE8;
        border-radius: 14px;
        padding: 12px 8px 4px 8px;
        box-shadow: 0 2px 10px rgba(15, 81, 50, 0.05);
        margin-bottom: 18px;
    }

    /* --------------------- DATAFRAMES --------------------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E5EBE8;
        border-radius: 12px;
        overflow: hidden;
    }

    /* --------------------- ALERTAS / INSIGHTS (marca propia) --------------------- */
    div[data-testid="stAlert"] {
        background-color: #E7F4EC !important;
        border: 1px solid #BFE0CC !important;
        border-left: 4px solid #157347 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] p {
        color: #0F5132 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    /* --------------------- BOTONES --------------------- */
    .stButton>button {
        background-color: #157347 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0F5132 !important;
        color: white !important;
    }

    /* --------------------- INPUT TEXTO --------------------- */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #D3DED8 !important;
    }

    /* --------------------- CAPTIONS --------------------- */
    .stCaption, [data-testid="stCaptionContainer"] p {
        color: #5B6E67 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PALETAS DE COLORES ESPECÍFICAS
# ---------------------------------------------------------
USER_COLORS = {
    'Ruso': '#157347',
    'Harry': '#2FA66B',
    'BDI': '#3AAFB9',
    'Gian': '#0B3D27',
    'Toto': '#5BC49A',
    'Mariano': '#A9C9A4',
    'Sin Asignar': '#C9D2CE'
}
BROKER_COLORS = {
    'Balanz': '#0B3D66',
    'BMB': '#3E92CC',
    'IOL': '#D6336C',
    'Inviu': '#2FA66B',
    'Sin Broker': '#AEB6B2'
}
TIER_COLORS = {
    '0 a 50K USD': '#0F5132',
    '50 a 100K USD': '#2FA66B',
    '100k a 250k USD': '#3AAFB9',
    '250k a 500k USD': '#8FBF74',
    'Mas de 500k USD': '#C9A227',
    'Sin Etiqueta Monto': '#B9C2BD'
}
GREEN_PALETTE = ['#0F5132', '#157347', '#2FA66B', '#3AAFB9', '#8FBF74', '#C9A227']

BROKERS = ['Balanz', 'BMB', 'IOL', 'Inviu']
TIERS = ['0 a 50K USD', '50 a 100K USD', '100k a 250k USD', '250k a 500k USD', 'Mas de 500k USD']
DAY_MAP = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
DAY_ORDER_LABORAL = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
DRIVE_FOLDER_ID = "1CYKA6e2R_enmSVHpTrUdCFyGiZ_pKZH2"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1CYKA6e2R_enmSVHpTrUdCFyGiZ_pKZH2?usp=sharing"
EXCLUIR_CONTACTOS = ['Soporte IOL', 'Caroline Pascuzzi - Soporte IOL', 'Caroline Pascuzzi - Soporte Inviu']

# -----------------------------------------------------------
# TEMA APLICADO A TODOS LOS GRÁFICOS
# -----------------------------------------------------------
def apply_bdi_theme(fig, legend_below=False):
    """Aplica estilo corporativo consistente y evita solapamientos de texto."""
    fig.update_layout(
        font=dict(family='Inter, Segoe UI, sans-serif', color='#1A252C', size=13),
        title=dict(font=dict(color='#0F5132', size=17, family='Inter, Segoe UI, sans-serif'), x=0.01, xanchor='left'),
        xaxis=dict(title_font=dict(color='#3F4F49', size=13), tickfont=dict(color='#4A5D57'),
                    gridcolor='#EAF0ED', zerolinecolor='#EAF0ED'),
        yaxis=dict(title_font=dict(color='#3F4F49', size=13), tickfont=dict(color='#4A5D57'),
                    gridcolor='#EAF0ED', zerolinecolor='#EAF0ED'),
        legend=dict(
            title_font=dict(color='#0F5132', size=12),
            font=dict(color='#3F4F49', size=12),
            orientation='h' if legend_below else 'v',
            yanchor='top', y=-0.18 if legend_below else 1,
            xanchor='center' if legend_below else 'left',
            x=0.5 if legend_below else 1.02,
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=50, l=50, r=40),
        bargap=0.25,
        bargroupgap=0.08,
        uniformtext_minsize=11,
        uniformtext_mode='hide',
        hoverlabel=dict(bgcolor='#0F5132', font_color='white', font_size=12)
    )
    fig.update_traces(
        textposition='auto',
        insidetextanchor='middle',
        textfont=dict(size=12, family='Inter, Segoe UI, sans-serif'),
        insidetextfont=dict(color='white', size=12),
        outsidetextfont=dict(color='#1A252C', size=12),
        marker_line_width=0,
        selector=dict(type="bar")
    )
    fig.update_traces(
        insidetextfont=dict(color='white', size=13),
        outsidetextfont=dict(color='#1A252C', size=13),
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        selector=dict(type="pie")
    )
    fig.update_traces(
        line=dict(width=3),
        selector=dict(type="scatter")
    )
    return fig


def section_header(tag, title, subtitle=None):
    sub_html = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
        <div class="section-tag">{tag}</div>
        <h3 style="margin-top:0;">{title}</h3>
        {sub_html}
    """, unsafe_allow_html=True)


def add_reference_line(fig, value, orientation='v', label='Promedio'):
    """Agrega una línea de referencia (promedio) a un gráfico de barras para dar contexto ejecutivo."""
    if pd.isna(value):
        return fig
    if orientation == 'v':
        fig.add_vline(
            x=value, line_width=2, line_dash="dot", line_color="#C9A227",
            annotation_text=f"{label}: {value:.1f}", annotation_position="top right",
            annotation_font=dict(color="#8A6D00", size=11)
        )
    else:
        fig.add_hline(
            y=value, line_width=2, line_dash="dot", line_color="#C9A227",
            annotation_text=f"{label}: {value:.1f}", annotation_position="top left",
            annotation_font=dict(color="#8A6D00", size=11)
        )
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


@st.cache_data(ttl=1800)
def cargar_datos_drive():
    """
    Descarga siempre una copia fresca de todos los .xlsx de la carpeta de Drive.
    Se borra el directorio local antes de descargar para evitar quedarse con
    archivos viejos (por ejemplo, si se borró un Excel en Drive y se subió
    uno nuevo con otro ID interno pero el mismo nombre).
    """
    output_dir = "./data_drive"

    # Limpieza total del directorio local antes de sincronizar
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    # Descarga de la carpeta completa de Drive (siempre trae el contenido actual)
    try:
        gdown.download_folder(id=DRIVE_FOLDER_ID, output=output_dir, quiet=True, remaining_ok=True)
    except Exception:
        pass

    all_files = glob.glob(os.path.join(output_dir, "**", "*.xlsx"), recursive=True)
    if not all_files:
        return pd.DataFrame()

    dfs = []
    for file in sorted(all_files):
        try:
            df_temp = pd.read_excel(file)
            dfs.append(df_temp)
        except Exception:
            continue

    if not dfs: return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)

    df = df[~df['contactName'].isin(EXCLUIR_CONTACTOS)]

    df['createdAt_dt'] = pd.to_datetime(df['createdAt'])
    df['firstSentMessageAt_dt'] = pd.to_datetime(df['firstSentMessageAt'])

    df['fecha_corta'] = df['createdAt_dt'].dt.date
    df['mes_nombre'] = df['createdAt_dt'].dt.strftime('%m - %B')
    df['dia_semana'] = df['createdAt_dt'].dt.day_name().map(DAY_MAP)
    df['hora'] = df['createdAt_dt'].dt.hour

    df['hora_30m'] = df['createdAt_dt'].dt.floor('30min').dt.strftime('%H:%M')

    df['FRT_min'] = (df['firstSentMessageAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df['resp_time_wh_min'] = df['workingHoursResponseTime'].apply(time_str_to_minutes)
    df['res_time_wh_min'] = df['workingHoursResolutionTime'].apply(time_str_to_minutes)

    df['brokers'] = df['tags'].apply(extract_brokers)
    df['tier'] = df['tags'].apply(extract_tier)

    df['isNewContact'] = df['isNewContact'].astype(bool)
    df['resolvedByInactivity'] = df['resolvedByInactivity'].astype(bool)

    return df


def sincronizar_datos():
    """Limpia el caché y fuerza una nueva descarga desde Drive en el próximo rerun."""
    st.cache_data.clear()


st.sidebar.markdown("### ⚙️ Panel de Control")
st.sidebar.button("🔄 Sincronizar datos de Google Drive", on_click=sincronizar_datos, use_container_width=True)
st.sidebar.caption("Usá este botón cada vez que agregues, borres o reemplaces archivos en la carpeta de Drive. Recargar la página (F5) no alcanza para traer los datos nuevos.")

# Opción extra: Cargar archivo manualmente directamente en el navegador
uploaded_files = st.sidebar.file_uploader("📂 O subir planilla .xlsx manualmente:", type=["xlsx"], accept_multiple_files=True)

df_raw = cargar_datos_drive()

if uploaded_files:
    dfs_up = []
    for up_file in uploaded_files:
        try:
            dfs_up.append(pd.read_excel(up_file))
        except Exception:
            pass
    if dfs_up:
        df_uploaded = pd.concat(dfs_up, ignore_index=True)
        if not df_raw.empty:
            df_raw = pd.concat([df_raw, df_uploaded], ignore_index=True).drop_duplicates()
        else:
            df_raw = df_uploaded

if df_raw.empty:
    st.error("No se encontraron datos para procesar. Verifique el acceso a Google Drive o suba los archivos .xlsx mediante la opción del panel lateral.")
    st.stop()

# ---------------------------------------------------------
# HEADER PRINCIPAL
# ---------------------------------------------------------
st.markdown(f"""
<div class="bdi-header">
    <h1>📈 Dashboard de Gestión de Mensajería</h1>
    <p>BDI Consultora — Consolidado analítico de conversaciones, rendimiento operativo por asesor y distribución patrimonial.</p>
    <span class="bdi-badge">Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🔎 Filtros de Búsqueda")
meses_sel = st.sidebar.multiselect("Mes:", sorted(df_raw['mes_nombre'].dropna().unique()), default=sorted(df_raw['mes_nombre'].dropna().unique()))
asesores_sel = st.sidebar.multiselect("Asesor:", sorted(df_raw['user'].dropna().unique()), default=sorted(df_raw['user'].dropna().unique()))

st.sidebar.markdown("---")
st.sidebar.caption("💡 Los filtros aplican a todas las solapas del dashboard en simultáneo.")

# ---------------------------------------------------------
# FILTRO GLOBAL PARA TODO EL SISTEMA
# ---------------------------------------------------------
df = df_raw.copy()
if meses_sel: df = df[df['mes_nombre'].isin(meses_sel)]
if asesores_sel: df = df[df['user'].isin(asesores_sel)]

# ---------------------------------------------------------
# KPIs PRINCIPALES
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Chats", f"{len(df):,}", help="Chats generados en el período y por los asesores seleccionados.")
kpi2.metric("Contactos Únicos", f"{df['contactNumber'].nunique():,}", help="Cantidad de personas o números distintos que escribieron.")
kpi3.metric("Nuevos Contactos", f"{df['isNewContact'].sum():,}", help="Cantidad de clientes/prospectos escribiendo por primera vez.")
kpi4.metric("FRT Mediano", f"{df['FRT_min'].median():.1f} min", help="Tiempo de Primera Respuesta. Los minutos que demora el asesor en enviar el primer mensaje desde que el cliente inicia la consulta.")
kpi5.metric("Cierre Inactividad", f"{df['resolvedByInactivity'].sum():,}", help="Chats cerrados automáticamente por el sistema debido a la inactividad del cliente.")

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
        fig_mes = px.bar(
            df_mes, x='mes_nombre', y='Chats', text='Chats',
            color_discrete_sequence=['#157347'], title="Evolución Mensual de Chats"
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
        fig_broker.update_layout(margin=dict(t=60, b=80, l=40, r=40))
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
        fig_tier.update_layout(margin=dict(t=60, b=80, l=40, r=40))
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
        fig_broker_filt.update_layout(margin=dict(t=60, b=80, l=40, r=40))
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
        fig_tier_filt.update_layout(margin=dict(t=60, b=80, l=40, r=40))
        st.plotly_chart(fig_tier_filt, use_container_width=True)

    divider()

    section_header("ALCANCE REAL", "Análisis Basado en Usuarios Únicos")
    col_b5, col_b6 = st.columns(2)
    with col_b5:
        unique_brokers = df_exp[df_exp['brokers'] != 'Sin Broker'].drop_duplicates(subset=['contactNumber', 'brokers'])
        broker_users = unique_brokers['brokers'].value_counts().reset_index()
        broker_users.columns = ['Broker', 'Usuarios_Unicos']
        fig_broker_usr = px.pie(
            broker_users, values='Usuarios_Unicos', names='Broker', hole=0.45,
            color='Broker', color_discrete_map=BROKER_COLORS,
            title="Personas Únicas Atendidas por Broker"
        )
        fig_broker_usr.update_traces(textinfo='percent', textposition='inside')
        fig_broker_usr = apply_bdi_theme(fig_broker_usr, legend_below=True)
        fig_broker_usr.update_layout(margin=dict(t=60, b=80, l=40, r=40))
        st.plotly_chart(fig_broker_usr, use_container_width=True)

    with col_b6:
        unique_tiers = df[df['tier'] != 'Sin Etiqueta Monto'].drop_duplicates(subset=['contactNumber', 'tier'])
        tier_users = unique_tiers['tier'].value_counts().reset_index()
        tier_users.columns = ['Segmento', 'Usuarios_Unicos']
        fig_tier_usr = px.pie(
            tier_users, values='Usuarios_Unicos', names='Segmento', hole=0.45,
            color='Segmento', color_discrete_map=TIER_COLORS,
            title="Personas Únicas Atendidas por Patrimonio",
            category_orders={'Segmento': TIERS}
        )
        fig_tier_usr.update_traces(textinfo='percent', textposition='inside')
        fig_tier_usr = apply_bdi_theme(fig_tier_usr, legend_below=True)
        fig_tier_usr.update_layout(margin=dict(t=60, b=80, l=40, r=40))
        st.plotly_chart(fig_tier_usr, use_container_width=True)

    divider()

    section_header("COMPOSICIÓN CRUZADA", "Brokers vs. Segmentos Patrimoniales")
    df_tier_broker = df_exp[df_exp['tier'] != 'Sin Etiqueta Monto'].groupby(['brokers', 'tier']).size().reset_index(name='Chats')
    totals = df_tier_broker.groupby('brokers')['Chats'].transform('sum')
    df_tier_broker['Porcentaje'] = (df_tier_broker['Chats'] / totals * 100).round(1)
    df_tier_broker['Texto'] = df_tier_broker['Chats'].astype(str) + " (" + df_tier_broker['Porcentaje'].astype(str) + "%)"

    fig_tier_broker = px.bar(
        df_tier_broker,
        x='Chats',
        y='brokers',
        color='tier',
        barmode='group',
        orientation='h',
        text='Texto',
        category_orders={'tier': TIERS},
        color_discrete_map=TIER_COLORS,
        title="Volumen de Consultas Patrimoniales por Broker"
    )
    fig_tier_broker.update_traces(textposition='outside', cliponaxis=False)
    fig_tier_broker = apply_bdi_theme(fig_tier_broker, legend_below=True)
    fig_tier_broker.update_layout(
        xaxis_title="Cantidad de Chats",
        yaxis_title="Broker",
        legend_title="Segmento (USD)",
        height=780,
        margin=dict(t=60, b=90, l=60, r=60)
    )
    st.plotly_chart(fig_tier_broker, use_container_width=True)

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

    df_top10 = df_clients_all.sort_values('Total_Chats', ascending=False).head(10)
    df_top10 = df_top10.sort_values('Total_Chats', ascending=True)

    fig_top10 = px.bar(
        df_top10, x='Total_Chats', y='contactName', orientation='h', text='Total_Chats',
        color='Asesor_Habitual', color_discrete_map=USER_COLORS,
        title="Top 10 Clientes (Color = Asesor Principal)",
        labels={'contactName': 'Cliente', 'Total_Chats': 'Cantidad de Chats', 'Asesor_Habitual': 'Asesor Principal'}
    )
    fig_top10.update_traces(textposition='outside', cliponaxis=False)
    fig_top10 = apply_bdi_theme(fig_top10, legend_below=True)
    fig_top10.update_layout(height=650, margin=dict(t=60, b=90, l=140, r=60))
    st.plotly_chart(fig_top10, use_container_width=True)

    divider()

    section_header("BASE DE CLIENTES", "Listado Completo e Interactivo")

    # Lógica de Pareto (Concentración de Demanda)
    df_pareto = df_clients_all.sort_values('Total_Chats', ascending=False)
    total_chats_pareto = df_pareto['Total_Chats'].sum()
    if total_chats_pareto > 0:
        df_pareto['CumSum'] = df_pareto['Total_Chats'].cumsum()
        df_pareto['CumPct'] = df_pareto['CumSum'] / total_chats_pareto
        pareto_80_idx = df_pareto[df_pareto['CumPct'] <= 0.8].shape[0]
        if pareto_80_idx == 0: pareto_80_idx = 1
        pareto_client_pct = (pareto_80_idx / len(df_pareto)) * 100
        st.info(f"💡 **Concentración de la Demanda (Ley de Pareto):** El **{pareto_client_pct:.1f}%** de los clientes registrados ({pareto_80_idx} de {len(df_pareto)}) genera el 80% del volumen total de chats operativos.")

    search_query = st.text_input("🔍 Buscador de clientes (nombre o número telefónico):", "")
    df_filtered_clients = df_clients_all.copy().sort_values('Total_Chats', ascending=False)

    if search_query:
        mask = (
            df_filtered_clients['contactName'].astype(str).str.contains(search_query, case=False, na=False) |
            df_filtered_clients['contactNumber'].astype(str).str.contains(search_query, case=False, na=False)
        )
        df_filtered_clients = df_filtered_clients[mask]

    st.caption(f"Mostrando **{len(df_filtered_clients):,}** clientes registrados.")
    df_display_clients = df_filtered_clients.rename(columns={
        'contactName': 'Nombre del Cliente', 'contactNumber': 'Número de Teléfono',
        'Total_Chats': 'Total Chats', 'Asesor_Habitual': 'Asesor Principal', 'Segmento_Monto': 'Segmento Patrimonial'
    })
    st.dataframe(df_display_clients, use_container_width=True, hide_index=True, height=420)

# ---------------------------------------------------------
# TAB 4: ACTIVIDAD POR USUARIO Y EFICIENCIA OPERATIVA
# ---------------------------------------------------------
with tab4:
    section_header("EFICIENCIA", "Desempeño Operativo por Asesor")

    total_general_chats = len(df)

    if not df.empty:
        df_meses = df_raw.copy()
        if meses_sel: df_meses = df_meses[df_meses['mes_nombre'].isin(meses_sel)]

        min_date = df_meses['createdAt_dt'].min().date()
        max_date = df_meses['createdAt_dt'].max().date()
        years = df_meses['createdAt_dt'].dt.year.unique().tolist()
        ar_holidays = holidays.AR(years=years)

        all_dates = pd.date_range(start=min_date, end=max_date)
        dias_laborales = [d for d in all_dates if d.weekday() < 5 and d.date() not in ar_holidays]
        base_dias = len(dias_laborales) if len(dias_laborales) > 0 else 1
    else:
        base_dias = 1

    st.caption(f"📅 **Base de cálculo temporal:** {base_dias} días hábiles (excluye fines de semana y feriados nacionales) · Jornada de 8 hs (09:30–17:30).")

    df_user_eff = df.groupby('user').agg(
        Total_Chats=('chatId', 'count'),
        FRT_Mediano_Min=('FRT_min', 'median'),
        Contactos_Nuevos=('isNewContact', 'sum')
    ).reset_index()

    df_user_eff['Participación (%)'] = (df_user_eff['Total_Chats'] / total_general_chats * 100)
    df_user_eff['Contactos Nuevos (%)'] = (df_user_eff['Contactos_Nuevos'] / df_user_eff['Total_Chats'] * 100)

    df_user_eff['Chats / Día'] = df_user_eff['Total_Chats'] / base_dias
    df_user_eff['Chats / Hora (8hs)'] = df_user_eff['Chats / Día'] / 8.0

    df_user_eff = df_user_eff.sort_values('Total_Chats', ascending=False)

    df_table_eff = df_user_eff[['user', 'Total_Chats', 'Participación (%)', 'FRT_Mediano_Min',
                                'Chats / Día', 'Chats / Hora (8hs)',
                                'Contactos_Nuevos', 'Contactos Nuevos (%)']].copy()

    df_table_eff.columns = ['Asesor', 'Total Chats', 'Participación (%)', 'FRT Mediano (Min)',
                            'Chats / Día', 'Chats / Hora (8hs)', 'Nuevos Contactos (#)', 'Nuevos Contactos (%)']

    st.markdown("##### Resumen de Métricas de Agilidad, Volumen y Calidad")
    st.dataframe(
        df_table_eff.style.format({
            'Participación (%)': '{:.1f}%', 'FRT Mediano (Min)': '{:.1f}',
            'Chats / Día': '{:.1f}', 'Chats / Hora (8hs)': '{:.1f}',
            'Nuevos Contactos (%)': '{:.1f}%'
        }),
        column_config={
            "FRT Mediano (Min)": st.column_config.NumberColumn(help="First Response Time: minutos que tarda el asesor en responder el primer mensaje."),
            "Chats / Día": st.column_config.NumberColumn(help="Total de chats dividido la cantidad de días hábiles (Lun a Vie) descontando feriados."),
            "Chats / Hora (8hs)": st.column_config.NumberColumn(help="Promedio diario dividido las 8 horas de la jornada laboral teórica."),
            "Nuevos Contactos (#)": st.column_config.NumberColumn(help="Cantidad absoluta de clientes que escribieron a la línea por primera vez."),
            "Nuevos Contactos (%)": st.column_config.NumberColumn(help="Porcentaje de clientes que escribieron a la línea por primera vez respecto al total atendido.")
        },
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
        fig_pie.update_layout(margin=dict(t=60, b=80, l=40, r=40))
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
        fig_frt.update_layout(showlegend=False, xaxis_title="Minutos", yaxis_title="", margin=dict(t=60, b=40, l=100, r=60))
        st.plotly_chart(fig_frt, use_container_width=True)

    divider()

    section_header("PATRIMONIO", "Distribución de Cartera por Asesor")
    df_user_tier = df[df['tier'] != 'Sin Etiqueta Monto']
    asesores_activos = df_user_tier['user'].dropna().unique()

    if len(asesores_activos) > 0:
        cols_pie = st.columns(3)
        for idx, asesor in enumerate(asesores_activos):
            df_as = df_user_tier[df_user_tier['user'] == asesor].groupby('tier').size().reset_index(name='Chats')

            fig_p = px.pie(
                df_as, names='tier', values='Chats',
                title=f"Asesor: {asesor}",
                color='tier', color_discrete_map=TIER_COLORS, hole=0.35
            )
            fig_p.update_traces(textinfo='percent', textposition='inside')
            fig_p = apply_bdi_theme(fig_p)
            fig_p.update_layout(
                showlegend=False,
                margin=dict(t=45, b=15, l=30, r=30),
                title_font=dict(color='#0F5132', size=15)
            )
            cols_pie[idx % 3].plotly_chart(fig_p, use_container_width=True)
        st.caption("💡 Pasá el cursor sobre cada porción para ver el detalle exacto por segmento y asesor.")
    else:
        st.info("No hay datos de patrimonio etiquetados para mostrar bajo los filtros actuales.")

    divider()

    section_header("SATURACIÓN", "Picos de Actividad por Día y Hora")
    st.caption("Excluye sábados y domingos · Horario comercial (8 a 18 hs) · El color indica volumen absoluto; el porcentaje, el peso relativo dentro de ese día.")

    df_heatmap = df[(df['hora'] >= 8) & (df['hora'] <= 18) & (~df['dia_semana'].isin(['Sábado', 'Domingo']))]

    if not df_heatmap.empty:
        heatmap_counts = df_heatmap.groupby(['dia_semana', 'hora']).size().reset_index(name='Chats')
        totals_per_day = heatmap_counts.groupby('dia_semana')['Chats'].transform('sum')
        heatmap_counts['Porcentaje'] = (heatmap_counts['Chats'] / totals_per_day * 100).round(1)

        heatmap_data = heatmap_counts.pivot(index='dia_semana', columns='hora', values='Chats').reindex(DAY_ORDER_LABORAL).fillna(0)
        heatmap_pct = heatmap_counts.pivot(index='dia_semana', columns='hora', values='Porcentaje').reindex(DAY_ORDER_LABORAL).fillna(0)

        z = heatmap_data.values
        zmax = z.max() if z.max() > 0 else 1

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=z,
            x=[f"{h:02d}:00" for h in heatmap_data.columns],
            y=heatmap_data.index,
            colorscale=[[0, '#F4F9F6'], [0.5, '#8FBF74'], [1, '#0F5132']],
            colorbar=dict(title="Chats", thickness=14, len=0.8),
            hovertemplate="<b>%{y}, %{x}</b><br>Chats: %{z}<extra></extra>",
            zmin=0, zmax=zmax
        ))

        annotations = []
        for i, day in enumerate(heatmap_data.index):
            for j, hour in enumerate(heatmap_data.columns):
                val = z[i][j]
                pct = heatmap_pct.values[i][j]
                intensity = val / zmax if zmax > 0 else 0
                text_color = '#FFFFFF' if intensity > 0.55 else '#1A252C'
                annotations.append(dict(
                    x=f"{hour:02d}:00", y=day,
                    text=f"<b>{int(val)}</b><br>{pct:.0f}%",
                    showarrow=False,
                    font=dict(color=text_color, size=10.5),
                    align="center"
                ))
        fig_heatmap.update_layout(annotations=annotations)
        fig_heatmap.update_xaxes(title="Hora del día", side="bottom")
        fig_heatmap.update_yaxes(title="Día de la semana")
        fig_heatmap = apply_bdi_theme(fig_heatmap)
        fig_heatmap.update_layout(
            title=dict(text="Distribución de Carga de Trabajo (Horario Comercial)", font=dict(color='#0F5132', size=17), x=0.01),
            height=420,
            margin=dict(t=60, b=50, l=110, r=40)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No hay chats registrados en horario comercial para la selección actual.")

# ---------------------------------------------------------
# TAB 5: FRICCIÓN Y COMPLEJIDAD
# ---------------------------------------------------------
with tab5:
    # Explode reutilizable para esta solapa (respeta filtros globales)
    df_exp_5 = df.explode('brokers')
    df_exp_5['brokers'] = df_exp_5['brokers'].fillna('Sin Broker')

    # -------------------------------------------------
    # RESUMEN EJECUTIVO
    # -------------------------------------------------
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
    kf1.metric("Ratio Global de Fricción", f"{ratio_global:.2f} chats/cliente", help="Cantidad promedio de chats que genera cada cliente único. Un número alto sugiere procesos que requieren idas y vueltas.")
    kf2.metric("Resolución Promedio", f"{res_time_prom:.0f} min" if pd.notna(res_time_prom) else "s/d", help="Tiempo promedio de resolución en horario laboral, para todos los chats del período filtrado.")
    kf3.metric("Broker Más Dependiente", broker_mas_dependiente, help="Broker cuyos clientes generan, en promedio, más chats por persona.")
    kf4.metric("Segmento Más Lento (FRT)", segmento_mas_lento, help="Segmento patrimonial con la mediana de Tiempo de Primera Respuesta más alta.")

    divider()

    # -------------------------------------------------
    # FRICCIÓN / ÍNDICE DE INDEPENDENCIA
    # -------------------------------------------------
    section_header(
        "FRICCIÓN", "Índice de Independencia del Cliente",
        subtitle="Cuántas veces nos vuelve a escribir un mismo cliente único. Un ratio menor indica mayor autonomía y menor necesidad de asistencia."
    )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        df_fric_broker = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers').agg(
            Chats=('chatId', 'count'),
            Usuarios=('contactNumber', 'nunique')
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
        fig_fric_b.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Broker", showlegend=False)
        st.plotly_chart(fig_fric_b, use_container_width=True)

    with col_f2:
        df_fric_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier').agg(
            Chats=('chatId', 'count'),
            Usuarios=('contactNumber', 'nunique')
        ).reset_index()
        df_fric_tier['Ratio'] = df_fric_tier['Chats'] / df_fric_tier['Usuarios']

        fig_fric_t = px.bar(
            df_fric_tier, x='Ratio', y='tier', orientation='h', text='Ratio',
            color='tier', color_discrete_map=TIER_COLORS,
            category_orders={'tier': TIERS},
            title="Ratio de Chats por Usuario (por Patrimonio)"
        )
        fig_fric_t.update_traces(texttemplate='%{text:.2f} chats/usr', textposition='outside', cliponaxis=False)
        fig_fric_t = add_reference_line(fig_fric_t, df_fric_tier['Ratio'].mean(), orientation='v')
        fig_fric_t = apply_bdi_theme(fig_fric_t)
        fig_fric_t.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_fric_t, use_container_width=True)

    divider()

    # -------------------------------------------------
    # COMPLEJIDAD OPERATIVA (SLA)
    # -------------------------------------------------
    section_header(
        "COMPLEJIDAD OPERATIVA", "Análisis de Tiempos de Atención (SLA)",
        subtitle="Cruza tiempos de resolución y de primera respuesta con plataformas y patrimonio para detectar burocracia o atención priorizada."
    )

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        df_comp_broker = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers')['res_time_wh_min'].mean().reset_index()

        fig_comp_b = px.bar(
            df_comp_broker.sort_values('res_time_wh_min', ascending=True),
            x='res_time_wh_min', y='brokers', orientation='h', text='res_time_wh_min',
            color='brokers', color_discrete_map=BROKER_COLORS,
            title="Tiempo Promedio de Resolución por Broker"
        )
        fig_comp_b.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_comp_b = add_reference_line(fig_comp_b, df_comp_broker['res_time_wh_min'].mean(), orientation='v')
        fig_comp_b = apply_bdi_theme(fig_comp_b)
        fig_comp_b.update_layout(xaxis_title="Minutos Promedio en Horario Laboral", yaxis_title="Broker", showlegend=False)
        st.plotly_chart(fig_comp_b, use_container_width=True)

    with col_c2:
        df_comp_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median().reset_index()

        fig_comp_t = px.bar(
            df_comp_tier, x='FRT_min', y='tier', orientation='h', text='FRT_min',
            color='tier', color_discrete_map=TIER_COLORS,
            category_orders={'tier': TIERS},
            title="SLA de Facto: FRT Mediano por Patrimonio"
        )
        fig_comp_t.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_comp_t = add_reference_line(fig_comp_t, df_comp_tier['FRT_min'].mean(), orientation='v')
        fig_comp_t = apply_bdi_theme(fig_comp_t)
        fig_comp_t.update_layout(xaxis_title="Minutos (Mediana)", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_comp_t, use_container_width=True)

    st.caption("🟡 La línea punteada dorada marca el promedio del grupo — útil para identificar rápidamente quién está por encima o por debajo del estándar.")
