import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import shutil
import re
import json
import io
import inspect
import unicodedata
import gdown
import holidays
from datetime import datetime, time

# ===========================================================
# CONFIGURACIÓN DE PÁGINA Y TEMA CORPORATIVO (BDI CONSULTORA)
# ===========================================================
st.set_page_config(
    page_title="Dashboard de Mensajería | BDI Consultora",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Compatibilidad de versiones: Streamlit reemplazó `use_container_width` por `width`.
# Se detecta en runtime para que la app no se rompa cuando el Cloud actualice la librería.
try:
    _SOPORTA_WIDTH = 'width' in inspect.signature(st.dataframe).parameters
except (ValueError, TypeError):
    _SOPORTA_WIDTH = False
ANCHO = {'width': 'stretch'} if _SOPORTA_WIDTH else {'use_container_width': True}

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
        margin-right: 6px;
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
# CONSTANTES Y PALETAS DE COLORES
# ---------------------------------------------------------
USER_COLORS = {
    'Ruso': '#157347', 'Harry': '#2FA66B', 'BDI': '#3AAFB9',
    'Gian': '#0B3D27', 'Toto': '#5BC49A', 'Mariano': '#A9C9A4'
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
MESES_ORDEN = [MESES_ES_MAP[m] for m in range(1, 13)]
NOMBRE_MES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
              7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

# Escala del mapa de calor en verdes BDI (de papel a verde institucional).
BDI_HEATSCALE = [
    [0.00, '#FFFFFF'], [0.12, '#EDF7F1'], [0.28, '#CFE9DA'], [0.45, '#9FD3B6'],
    [0.62, '#5FBB8C'], [0.78, '#2FA66B'], [0.90, '#157347'], [1.00, '#0B3D27']
]

# Etiquetas comerciales que no son broker ni segmento patrimonial.
# ORDEN = PRIORIDAD: la primera que matchea gana, así "Membresia PLUS" no cae en "Membresia".
SERVICIOS = ['Membresia PLUS', 'Membresia', 'Premium', 'Agro', 'Consultoria', '+1 Cuenta']
SERVICIO_COLORS = {'Membresia PLUS': '#0B3D27', 'Membresia': '#157347', 'Premium': '#C9A227',
                   'Agro': '#8FBF74', 'Consultoria': '#3AAFB9', '+1 Cuenta': '#2FA66B'}

# Estado comercial del contacto (clave para leer la conexión Comercial).
ESTADOS = ['Potencial Cliente', 'EX CLIENTE', 'no es cliente', 'No califica']

# Colores de reserva para asesores que aparezcan más adelante y no estén en USER_COLORS.
PALETA_ASESORES = ['#1F8A5C', '#3E92CC', '#C9A227', '#8FBF74', '#D6336C', '#0B3D66', '#5BC49A', '#A9C9A4']

# ===========================================================
# DESENLACE DEL LEAD (solo línea comercial)
# ===========================================================
# La distinción que define si el número comercial sirve o no:
#
#   GANA EL COMERCIAL (lead nuevo convertido):
#     «Membresia - Comercial»   → vendió una membresía
#     «Consultoria - Comercial» → vendió una consultoría
#     «Derivado a asesor»       → lo pasó a la mesa de asesores
#
#   NO ES LEAD (cliente que ya tenía el servicio y escribe por una consulta):
#     «Membresia», «Membresia BDI», «Membresia PLUS», «Consultoria»
#     Por eso existen las etiquetas "- Comercial": para no contar como ganado
#     a alguien que ya era cliente.
#
#   NO APLICA:
#     «No califica» → interés real que no llega a los mínimos requeridos.
#
# Todo lo demás (sin etiqueta o con cualquier otra) cae en "Sin definir".
# La comparación es por igualdad exacta sobre la etiqueta normalizada, así
# «Consultoria - Comercial» nunca se confunde con «Consultoria» a secas.
TAG_MEMBRESIA_COMERCIAL = 'membresiacomercial'
TAG_CONSULTORIA_COMERCIAL = 'consultoriacomercial'
TAGS_DERIVADO = ('derivado', 'derivadoaasesor', 'derivadoasesor', 'derivadoaasesores')
TAGS_CLIENTE_EXISTENTE = ('membresia', 'membresiabdi', 'membresiaplus', 'consultoria')
TAG_NO_CALIFICA = 'nocalifica'
TAGS_EN_PROCESO = ('enproceso', 'engestion', 'seguimiento', 'enseguimiento')

DES_MEMBRESIA = 'Membresía - Comercial'
DES_CONSULTORIA = 'Consultoría - Comercial'
DES_DERIVADO = 'Derivado a asesor'
DES_NO_CALIFICA = 'No califica'
DES_EN_PROCESO = 'En proceso'
DES_SIN_DEFINIR = 'Sin definir'
DES_CLIENTE = 'Consulta de cliente existente'

# Las tres que cuentan como lead ganado, en el orden en que se muestran en el embudo.
DESENLACES_GANADOS = [DES_MEMBRESIA, DES_CONSULTORIA, DES_DERIVADO]
DESENLACES = DESENLACES_GANADOS + [DES_NO_CALIFICA, DES_EN_PROCESO, DES_SIN_DEFINIR]
DESENLACE_COLORS = {
    DES_MEMBRESIA: '#0F5132', DES_CONSULTORIA: '#C9A227', DES_DERIVADO: '#3AAFB9',
    DES_NO_CALIFICA: '#D6336C', DES_EN_PROCESO: '#8FBF74', DES_SIN_DEFINIR: '#C9D2CE',
    DES_CLIENTE: '#B9C2BD'
}
COLOR_ETAPA_1 = '#157347'
COLOR_ETAPA_2 = '#5FBB8C'
COLOR_ETAPA_3 = '#2FA66B'

def normalizar_tag(texto):
    """'Membresía - Comercial' → 'membresiacomercial'. Inmune a acentos, guiones y espacios."""
    limpio = unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]', '', limpio.lower())
ESTADO_COLORS = {'Potencial Cliente': '#C9A227', 'EX CLIENTE': '#AEB6B2', 'no es cliente': '#D6336C'}

# Conexiones (líneas de WhatsApp). Los colores se asignan por volumen en runtime,
# así una línea nueva se pinta sola sin tocar el código.
CONEXION_PALETA = ['#0F5132', '#C9A227', '#3AAFB9', '#8FBF74', '#D6336C', '#0B3D66', '#5BC49A']

NOMBRE_A_NUM = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'setiembre': 9, 'octubre': 10,
    'noviembre': 11, 'diciembre': 12
}

DRIVE_FOLDER_ID = "1CYKA6e2R_enmSVHpTrUdCFyGiZ_pKZH2"

# Lista de respaldo. Solo se usa si NO hay credenciales de Service Account.
ARCHIVOS_DRIVE_DIRECTOS = {
    '1 Enero.xlsx': '1zFNQvWpxMwlU_E-18WsTjsVa-E-14MkH',
    '2 Febrero.xlsx': '1unvZXggYzOB-xe-N1CeoYHTMz0QssfSj',
    '3 Marzo.xlsx': '1IUnaC_s51MHd2609yfcpUaxMhPcScxkp',
    '4 Abril.xlsx': '17Mmdng_JeNPXgHcOYlLK_2Edj8d3BQBt',
    '5 Mayo.xlsx': '1fkDQJejM25KzwiApnmRat_-IqdgKrdE0',
    '6 Junio.xlsx': '1ZBNevn_X5nBDQDBjHc7HrM1EaYQp2yn1',
    '7 Julio.xlsx': '1M_Ydu3-UGkcV8epF5UzjTLkXr03Jh6Gn',
    '8 Agosto (20/08).xlsx': '1VfXGVcWD9bfJrEYAALylDpyNqU1RizxM'
}

EXCLUIR_CONTACTOS = ['Soporte IOL', 'Caroline Pascuzzi - Soporte IOL', 'Caroline Pascuzzi - Soporte Inviu']

# ===========================================================
# JORNADA LABORAL BDI — 9:30 a 17:30, lunes a viernes, sin feriados AR.
# Todo tiempo de respuesta y de resolución se mide SOLO dentro de esta ventana.
# Para cambiar el horario, se tocan únicamente estas cuatro constantes.
# ===========================================================
HORARIO_INICIO = time(9, 30)
HORARIO_FIN = time(17, 30)
MINUTOS_JORNADA = ((HORARIO_FIN.hour * 60 + HORARIO_FIN.minute) -
                   (HORARIO_INICIO.hour * 60 + HORARIO_INICIO.minute))
HORAS_JORNADA = MINUTOS_JORNADA / 60.0
HORA_GRAF_INI = HORARIO_INICIO.hour          # 9  → primera franja del heatmap
HORA_GRAF_FIN = HORARIO_FIN.hour             # 17 → última franja del heatmap
HORARIO_TXT = f"{HORARIO_INICIO.strftime('%H:%M')} a {HORARIO_FIN.strftime('%H:%M')}"
ORIGEN_BUSDAY = np.datetime64('2020-01-01', 'D')

DATA_DIR = "./data_drive"
MANIFEST_PATH = os.path.join(DATA_DIR, "_manifest.json")
COLS_MINIMAS = ['createdAt', 'contactNumber']

# ID real de cada conversación en el export de Whaticket.
# OJO: 'chatId' NO sirve — es el hilo del contacto y se repite en todas sus conversaciones
# (en el export de enero: 1.934 conversationId únicos contra apenas 722 chatId).
COL_ID = 'conversationId'
COLS_DEDUP_FALLBACK = ['chatId', 'contactNumber', 'createdAt', 'firstSentMessageAt', 'user']

# -----------------------------------------------------------
# FUNCIONES AUXILIARES DE PRESENTACIÓN
# -----------------------------------------------------------
def apply_bdi_theme(fig, legend_below=False):
    """Tema visual BDI.

    OJO con el orden: esta función se llama DESPUÉS de armar cada gráfico, así que
    no debe tocar `textposition` — antes lo forzaba a 'auto' y pisaba el 'outside'
    de cada trace, lo que metía las etiquetas adentro de la barra y las achicaba
    hasta volverlas ilegibles. `uniformtext` con mode='show' impide ese encogido.
    """
    fig.update_layout(
        font=dict(family='Inter, Segoe UI, sans-serif', color='#1A252C', size=15),
        title=dict(font=dict(color='#0F5132', size=20), x=0.01, xanchor='left'),
        xaxis=dict(title_font=dict(color='#3F4F49', size=15), tickfont=dict(color='#4A5D57', size=14),
                   gridcolor='#EAF0ED'),
        yaxis=dict(title_font=dict(color='#3F4F49', size=15), tickfont=dict(color='#4A5D57', size=14),
                   gridcolor='#EAF0ED'),
        legend=dict(
            title_font=dict(color='#0F5132', size=14), font=dict(color='#3F4F49', size=14),
            orientation='h' if legend_below else 'v', yanchor='top', y=-0.18 if legend_below else 1,
            xanchor='center' if legend_below else 'left', x=0.5 if legend_below else 1.02,
            bgcolor='rgba(0,0,0,0)'
        ),
        uniformtext=dict(minsize=13, mode='show'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=70, b=55, l=60, r=50), bargap=0.28,
        hoverlabel=dict(bgcolor='#0F5132', font_color='white', font_size=14)
    )
    fig.update_traces(textfont=dict(size=15), selector=dict(type="bar"))
    fig.update_traces(textfont=dict(size=15), selector=dict(type="pie"))
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

# -----------------------------------------------------------
# FUNCIONES AUXILIARES DE DATOS
# -----------------------------------------------------------
def time_str_to_minutes(val):
    """'27:35:52' -> 1655.87 minutos. El CRM no rellena con ceros y las horas pueden pasar de 24."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return float(val)
    partes = str(val).strip().split(':')
    try:
        if len(partes) == 3:
            h, m, s = (int(p) for p in partes)
            return h * 60 + m + s / 60.0
        if len(partes) == 2:
            m, s = (int(p) for p in partes)
            return m + s / 60.0
    except (ValueError, TypeError):
        return np.nan
    return np.nan

def etiqueta_periodo(ts):
    """'2026-01 · Enero'. Incluye el año para que enero 2027 no se mezcle con enero 2026."""
    if pd.isna(ts):
        return 'Sin Período'
    return f"{ts.year}-{ts.month:02d} · {NOMBRE_MES[ts.month]}"

def extract_etiquetas(tag_str, catalogo):
    """Primera coincidencia gana, respetando el orden del catálogo.

    Evita que 'Membresia PLUS' se cuente además como 'Membresia'.
    """
    if pd.isna(tag_str):
        return []
    encontradas = []
    for bruta in str(tag_str).split(','):
        t = bruta.strip().lower()
        if not t:
            continue
        for etiqueta in catalogo:
            if etiqueta.lower() in t:
                if etiqueta not in encontradas:
                    encontradas.append(etiqueta)
                break
    return encontradas

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
    fn = str(filename).lower()
    for name, num in NOMBRE_A_NUM.items():
        if name in fn:
            return MESES_ES_MAP[num]
    match = re.search(r'(\b\d{1,2}\b)', fn)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 12:
            return MESES_ES_MAP[num]
    return 'Mes No Especificado'

def col_segura(df, nombre):
    """Devuelve la columna si existe; si no, una serie de NaN del mismo largo."""
    if nombre in df.columns:
        return df[nombre]
    return pd.Series(np.nan, index=df.index)

def nombre_seguro(nombre):
    return re.sub(r'[\\/:*?"<>|]', '_', str(nombre))

def es_xlsx_valido(path):
    """Un .xlsx real es un ZIP: empieza con 'PK'. Descarta HTML de error de Drive."""
    try:
        if os.path.getsize(path) < 5000:
            return False
        with open(path, 'rb') as f:
            return f.read(2) == b'PK'
    except OSError:
        return False


# -----------------------------------------------------------
# TIEMPOS EN HORARIO LABORAL
# -----------------------------------------------------------
def feriados_np(anios):
    try:
        fer = holidays.AR(years=sorted({int(a) for a in anios if a and a > 2000}))
        return np.array(sorted(fer.keys()), dtype='datetime64[D]')
    except Exception:
        return np.array([], dtype='datetime64[D]')

def _minutos_acumulados(ts, feriados):
    """Minutos de jornada transcurridos desde ORIGEN_BUSDAY hasta cada timestamp.

    Un chat que entra a las 20:00 cuenta como si hubiese llegado al cierre: el reloj
    laboral arranca recién a las 9:30 del siguiente día hábil.
    """
    fechas = ts.dt.normalize().values.astype('datetime64[D]')
    dias_previos = np.busday_count(ORIGEN_BUSDAY, fechas, holidays=feriados).astype(float)
    habil = np.is_busday(fechas, holidays=feriados)
    minuto_del_dia = (ts.dt.hour * 60 + ts.dt.minute + ts.dt.second / 60.0).values
    desde_apertura = minuto_del_dia - (HORARIO_INICIO.hour * 60 + HORARIO_INICIO.minute)
    dentro = np.clip(desde_apertura, 0, MINUTOS_JORNADA)
    dentro = np.where(habil, dentro, 0.0)
    return dias_previos * MINUTOS_JORNADA + dentro

def minutos_laborales(inicio, fin, feriados):
    """Minutos de jornada entre dos timestamps. NaN si falta alguno."""
    out = pd.Series(np.nan, index=inicio.index, dtype='float64')
    mask = inicio.notna() & fin.notna()
    if not mask.any():
        return out
    a = _minutos_acumulados(inicio[mask], feriados)
    b = _minutos_acumulados(fin[mask], feriados)
    out.loc[mask] = np.clip(b - a, 0, None)
    return out

def en_horario_laboral(ts, feriados):
    """True si el timestamp cae dentro de la jornada de un día hábil."""
    res = pd.Series(False, index=ts.index)
    mask = ts.notna()
    if not mask.any():
        return res
    t = ts[mask]
    fechas = t.dt.normalize().values.astype('datetime64[D]')
    habil = np.is_busday(fechas, holidays=feriados)
    minuto = (t.dt.hour * 60 + t.dt.minute).values
    apertura = HORARIO_INICIO.hour * 60 + HORARIO_INICIO.minute
    cierre = HORARIO_FIN.hour * 60 + HORARIO_FIN.minute
    res.loc[mask] = habil & (minuto >= apertura) & (minuto < cierre)
    return res

# -----------------------------------------------------------
# CAPA 1 · CONEXIÓN Y LISTADO DE ARCHIVOS EN DRIVE
# -----------------------------------------------------------
@st.cache_resource(show_spinner=False)
def servicio_drive():
    """Cliente autenticado de Drive, o None si no hay credenciales.

    Se usa TANTO para listar como para descargar. Descargar con las mismas
    credenciales evita tener que compartir cada planilla como pública:
    alcanza con que la carpeta esté compartida con la Service Account.
    """
    try:
        tiene_sa = "gcp_service_account" in st.secrets
    except Exception:
        return None
    if not tiene_sa:
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=creds, cache_discovery=False)
    except Exception:
        return None

@st.cache_data(ttl=120, show_spinner=False)
def listar_archivos_drive():
    """Devuelve (archivos, log, listado_en_vivo).

    `listado_en_vivo` indica si la lista vino de la API. Si es False estamos con la
    lista fija de respaldo y NO se debe borrar nada local: la carpeta podría tener
    planillas que el respaldo desconoce.
    """
    log, archivos = [], {}
    service = servicio_drive()

    if service is None:
        log.append(("warn", "No hay credenciales `gcp_service_account` cargadas: "
                            "no se detectan archivos nuevos de forma automática."))
    else:
        try:
            page_token = None
            hojas_google = []
            while True:
                res = service.files().list(
                    q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
                    fields="nextPageToken, files(id, name, modifiedTime, mimeType)",
                    pageSize=200,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                for item in res.get('files', []):
                    mime = item.get('mimeType', '')
                    es_xlsx = item['name'].lower().endswith('.xlsx')
                    # Drive puede convertir un .xlsx subido en Hoja de cálculo de Google.
                    # Esas NO terminan en .xlsx y quedaban invisibles: hay que exportarlas.
                    es_sheet = mime == 'application/vnd.google-apps.spreadsheet'
                    if not (es_xlsx or es_sheet):
                        continue
                    nombre = item['name'] if es_xlsx else f"{item['name']}.xlsx"
                    if nombre in archivos:   # colisión entre una Sheet y un .xlsx del mismo nombre
                        nombre = f"{item['name']} ({item['id'][:6]}).xlsx"
                    archivos[nombre] = {'id': item['id'], 'modified': item.get('modifiedTime'),
                                        'mime': mime, 'sheet': es_sheet}
                    if es_sheet:
                        hojas_google.append(item['name'])
                page_token = res.get('nextPageToken')
                if not page_token:
                    break

            log.append(("ok", f"Drive API conectada · {len(archivos)} planillas detectadas en la carpeta."))
            if hojas_google:
                log.append(("ok", f"{len(hojas_google)} archivo(s) son Hojas de cálculo de Google "
                                  f"({', '.join(hojas_google)}): se exportan a .xlsx al vuelo."))
            if archivos:
                return archivos, log, True
            log.append(("error", "La carpeta respondió vacía. Verificá que esté compartida "
                                 "con el mail de la Service Account."))
        except Exception as e:
            log.append(("error", f"Falló el listado de Drive → {type(e).__name__}: {e}"))

    archivos = {n: {'id': i, 'modified': None, 'mime': '', 'sheet': False}
                for n, i in ARCHIVOS_DRIVE_DIRECTOS.items()}
    log.append(("warn", f"Usando la lista fija de {len(archivos)} IDs. Las planillas nuevas de Drive "
                        "no aparecen hasta configurar la Service Account."))
    return archivos, log, False

# -----------------------------------------------------------
# CAPA 2 · DESCARGA Y SINCRONIZACIÓN LOCAL
# -----------------------------------------------------------
def _bajar_con_api(service, meta, destino):
    """Descarga autenticada. No requiere que el archivo sea público."""
    from googleapiclient.http import MediaIoBaseDownload
    if meta.get('sheet'):
        pedido = service.files().export_media(
            fileId=meta['id'],
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        pedido = service.files().get_media(fileId=meta['id'], supportsAllDrives=True)
    with io.FileIO(destino, 'wb') as fh:
        bajador = MediaIoBaseDownload(fh, pedido, chunksize=5 * 1024 * 1024)
        terminado = False
        while not terminado:
            _, terminado = bajador.next_chunk()

def sincronizar_archivos(archivos, forzar=False, listado_en_vivo=False):
    """Descarga a un archivo temporal y solo reemplaza la copia buena si el .xlsx es válido.

    Regla de oro: nunca dejar al usuario sin datos. Si una descarga falla y existe una
    copia local previa, esa copia se conserva y se avisa.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    log = []
    service = servicio_drive()

    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    esperados = set()

    for nombre, meta in archivos.items():
        safe = nombre_seguro(nombre)
        esperados.add(safe)
        path = os.path.join(DATA_DIR, safe)
        tmp = path + ".descarga"
        remoto = meta.get('modified')
        local = manifest.get(safe, {})
        hay_copia = es_xlsx_valido(path)

        al_dia = (
            hay_copia
            and local.get('id') == meta['id']
            and (remoto is None or local.get('modified') == remoto)
        )
        if al_dia and not forzar:
            continue

        error = None
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
            if service is not None:
                _bajar_con_api(service, meta, tmp)
            else:
                # Sin credenciales solo queda gdown, que exige el archivo público.
                if gdown.download(id=meta['id'], output=tmp, quiet=True) is None:
                    error = ("La descarga anónima falló. Sin Service Account, el archivo "
                             "tiene que estar compartido como «Cualquiera con el enlace».")
            if error is None and not es_xlsx_valido(tmp):
                error = "Lo descargado no es un .xlsx válido."
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        if error is None:
            os.replace(tmp, path)          # reemplazo atómico: recién acá se pisa la copia buena
            manifest[safe] = {'id': meta['id'], 'modified': remoto,
                              'descargado': datetime.now().strftime('%d/%m/%Y %H:%M')}
            log.append(("ok", f"«{nombre}» descargado / actualizado."))
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
            if hay_copia:
                log.append(("warn", f"«{nombre}»: no se pudo actualizar ({error}). "
                                    "Se mantiene la copia local anterior."))
            else:
                log.append(("error", f"«{nombre}»: {error}"))

    # Limpieza SOLO con listado en vivo: con la lista fija borraríamos planillas legítimas.
    if listado_en_vivo:
        for f in glob.glob(os.path.join(DATA_DIR, "*.xlsx")):
            base = os.path.basename(f)
            if base not in esperados:
                try:
                    os.remove(f)
                    manifest.pop(base, None)
                    log.append(("warn", f"«{base}» ya no está en Drive: se eliminó la copia local."))
                except OSError:
                    pass

    try:
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False)
    except Exception:
        pass

    return log, manifest

def firma_local():
    """Huella de los archivos locales. Cambia cuando cambia cualquier planilla → invalida el caché."""
    out = []
    for f in sorted(glob.glob(os.path.join(DATA_DIR, "*.xlsx"))):
        out.append((os.path.basename(f), os.path.getsize(f), int(os.path.getmtime(f))))
    return tuple(out)

# -----------------------------------------------------------
# CAPA 3 · LECTURA Y PROCESAMIENTO
# -----------------------------------------------------------
@st.cache_data(show_spinner="Leyendo planillas…")
def leer_planillas(firma):
    dfs, log = [], []
    for nombre, _, _ in firma:
        path = os.path.join(DATA_DIR, nombre)
        try:
            d = pd.read_excel(path)
        except Exception as e:
            log.append(("error", f"«{nombre}» no se pudo abrir → {type(e).__name__}: {e}"))
            continue
        if d.empty:
            log.append(("warn", f"«{nombre}» está vacío."))
            continue
        faltantes = [c for c in COLS_MINIMAS if c not in d.columns]
        if faltantes:
            log.append(("error", f"«{nombre}» no tiene las columnas {faltantes}. Se omite (¿cambió el export del CRM?)."))
            continue
        d['archivo_origen'] = nombre
        d['mes_archivo'] = extract_month_from_filename(nombre)
        dfs.append(d)
        log.append(("ok", f"«{nombre}»: {len(d):,} filas leídas."))
    if not dfs:
        return pd.DataFrame(), log
    return pd.concat(dfs, ignore_index=True), log

def dias_habiles_efectivos(serie_fechas):
    """Días hábiles reales de los meses presentes, respetando meses parciales.

    Evita el error de tomar min→max cuando se filtran meses no contiguos
    (ej. enero + agosto no son 8 meses de días hábiles).
    """
    fechas = serie_fechas.dropna()
    if fechas.empty:
        return 1
    anios = sorted({int(a) for a in fechas.dt.year.unique() if a > 2000})
    feriados = holidays.AR(years=anios) if anios else holidays.AR()
    dias = set()
    for _, grupo in fechas.groupby(fechas.dt.to_period('M')):
        for d in pd.date_range(grupo.min().date(), grupo.max().date()):
            if d.weekday() < 5 and d.date() not in feriados:
                dias.add(d.date())
    return max(len(dias), 1)


# -----------------------------------------------------------
# ANÁLISIS DE CAPTACIÓN (líneas comerciales / top of funnel)
# -----------------------------------------------------------
TRAMOS_FRT = [
    ('Menos de 5 min', 0, 5, '#0F5132'),
    ('5 a 15 min', 5, 15, '#2FA66B'),
    ('15 a 60 min', 15, 60, '#8FBF74'),
    ('Más de 60 min', 60, np.inf, '#C9A227'),
    ('Sin respuesta', None, None, '#D6336C'),
]
TRAMO_COLORS = {t[0]: t[3] for t in TRAMOS_FRT}
ORDEN_TRAMOS = [t[0] for t in TRAMOS_FRT]

def clasificar_tramo(frt):
    if pd.isna(frt):
        return 'Sin respuesta'
    for nombre, desde, hasta, _ in TRAMOS_FRT[:-1]:
        if desde <= frt < hasta:
            return nombre
    return 'Más de 60 min'

def analizar_captacion(df_linea, df_historia, linea):
    """Convierte las conversaciones de una línea de captación en una tabla de LEADS.

    Un lead = un contacto único. Se clasifica contra el historial completo de las
    OTRAS líneas para separar tres cosas que no son lo mismo:
      - Lead nuevo sin derivar todavía
      - Lead derivado (después aparece hablando con un asesor)
      - Cliente que ya existía y escribió al número equivocado (no es captación)
    """
    if df_linea.empty:
        return pd.DataFrame()

    otras = df_historia[df_historia['conexion'] != linea]
    primera_otra = otras.groupby('contactNumber')['createdAt_dt'].min()

    filas = []
    for contacto, g in df_linea.groupby('contactNumber'):
        g = g.sort_values('createdAt_dt')
        primer_chat = g['createdAt_dt'].min()
        frt = g['FRT_min'].min()          # el mejor intento de respuesta al lead
        ref = primera_otra.get(contacto, pd.NaT)

        if pd.notna(ref) and ref < primer_chat:
            estado = 'Ya era cliente'
            horas = np.nan
        elif pd.notna(ref) and ref > primer_chat:
            estado = 'Derivado a asesores'
            horas = (ref - primer_chat).total_seconds() / 3600
        else:
            estado = 'Sin derivar'
            horas = np.nan

        # Desenlace comercial. Se juntan las etiquetas de TODAS las conversaciones del
        # lead: la etiqueta de cierre se carga al final de la charla, no en el primer chat.
        crudas = [t.strip() for x in g['tags'].dropna().astype(str) for t in x.split(',') if t.strip()]
        normalizadas = {normalizar_tag(t) for t in crudas}

        if TAG_MEMBRESIA_COMERCIAL in normalizadas:
            desenlace = DES_MEMBRESIA
        elif TAG_CONSULTORIA_COMERCIAL in normalizadas:
            desenlace = DES_CONSULTORIA
        elif normalizadas & set(TAGS_CLIENTE_EXISTENTE):
            # Ya tenía membresía o consultoría: escribe por una consulta, no es un lead.
            desenlace = DES_CLIENTE
        elif TAG_NO_CALIFICA in normalizadas:
            desenlace = DES_NO_CALIFICA
        elif (normalizadas & set(TAGS_DERIVADO)) or estado == 'Derivado a asesores':
            # Vale la etiqueta manual o la evidencia: el contacto aparece después
            # conversando en la línea de asesores.
            desenlace = DES_DERIVADO
        elif normalizadas & set(TAGS_EN_PROCESO):
            # Conversación abierta: todavía no se decidió. No es lo mismo que no etiquetar.
            desenlace = DES_EN_PROCESO
        else:
            desenlace = DES_SIN_DEFINIR

        filas.append({
            'contactNumber': contacto,
            'contactName': g['contactName'].iloc[0],
            'Asesor': g['user'].mode()[0] if not g['user'].mode().empty else g['user'].iloc[0],
            'Primer Chat': primer_chat,
            'Conversaciones': g[COL_ID].nunique(),
            'FRT_min': frt,
            'Tramo': clasificar_tramo(frt),
            'Respondido': pd.notna(frt),
            'Estado': estado,
            'Desenlace': desenlace,
            'Etiquetas': ', '.join(sorted(set(crudas))),
            'Horas a Derivación': horas,
            'hora_ingreso': primer_chat.hour if pd.notna(primer_chat) else np.nan,
            'fecha': primer_chat.date() if pd.notna(primer_chat) else None,
            'fuera_horario': not bool(g['en_horario'].iloc[0]),
            'FRT_real': g['FRT_real_min'].min(),
        })
    return pd.DataFrame(filas)


def metricas_usuario_linea(df_linea, etiqueta_linea=None):
    """Métricas de cada asesor DENTRO de una sola línea.

    Nunca se mezclan conexiones: un mismo asesor rinde distinto en la línea de cartera
    que en la comercial, y promediarlas esconde las dos cosas.
    """
    if df_linea.empty:
        return pd.DataFrame()
    total = df_linea[COL_ID].nunique()
    dias = dias_habiles_efectivos(df_linea['createdAt_dt'])
    m = df_linea.groupby('user').agg(
        Chats=(COL_ID, 'nunique'),
        Contactos=('contactNumber', 'nunique'),
        FRT_Mediano=('FRT_min', 'median'),
        FRT_p90=('FRT_min', lambda s: s.quantile(0.9)),
        Resolucion_Mediana=('res_time_wh_min', 'median'),
        Nuevos=('isNewContact', 'sum'),
    ).reset_index()
    m['% de la Línea'] = m['Chats'] / total * 100 if total else np.nan
    m['Chats/Día'] = m['Chats'] / dias if dias else np.nan
    m['Chats/Contacto'] = m['Chats'] / m['Contactos']
    if etiqueta_linea is not None:
        m.insert(1, 'Conexión', etiqueta_linea)
    return m.sort_values('Chats', ascending=False)

def metricas_usuario_por_conexion(df):
    """Una fila por asesor y conexión."""
    partes = [metricas_usuario_linea(g, conexion) for conexion, g in df.groupby('conexion')]
    partes = [p for p in partes if not p.empty]
    if not partes:
        return pd.DataFrame()
    return pd.concat(partes, ignore_index=True).sort_values(['Conexión', 'Chats'], ascending=[True, False])

def detectar_linea_captacion(df):
    """La línea con mayor proporción de contactos nuevos es, por definición, la de captación."""
    if df.empty or df['conexion'].nunique() == 0:
        return None
    ranking = df.groupby('conexion')['isNewContact'].mean().sort_values(ascending=False)
    return ranking.index[0]

def detectar_linea_principal(df):
    """La línea de cartera: la de mayor volumen de conversaciones."""
    if df.empty or df['conexion'].nunique() == 0:
        return None
    return df.groupby('conexion')[COL_ID].nunique().sort_values(ascending=False).index[0]

def resumen_por_conexion(df):
    """Métricas normalizadas por línea. Cada conexión se mide sobre SUS días activos,
    porque una línea nueva arranca a mitad de mes y el volumen crudo no es comparable."""
    filas = []
    for conexion, g in df.groupby('conexion'):
        conv = g[COL_ID].nunique()
        contactos = g['contactNumber'].nunique()
        dias = dias_habiles_efectivos(g['createdAt_dt'])
        filas.append({
            'Conexión': conexion,
            'Conversaciones': conv,
            'Contactos': contactos,
            'Chats/Contacto': conv / contactos if contactos else np.nan,
            'Días Hábiles': dias,
            'Chats/Día': conv / dias if dias else np.nan,
            '% Nuevos': g['isNewContact'].mean() * 100,
            'FRT Mediano': g['FRT_min'].median(),
            'Resolución Mediana': g['res_time_wh_min'].median(),
            '% Inicia Cliente': g['startedByContact'].mean() * 100,
            'Desde': g['createdAt_dt'].min(),
            'Hasta': g['createdAt_dt'].max(),
        })
    res = pd.DataFrame(filas).sort_values('Conversaciones', ascending=False).reset_index(drop=True)
    return res

def procesar(df, dedup=True):
    """Normaliza y deriva columnas. Se aplica UNA sola vez sobre Drive + subidas manuales."""
    log = []
    if df.empty:
        return df, log

    filas_iniciales = len(df)

    if 'contactName' in df.columns:
        df = df[~df['contactName'].isin(EXCLUIR_CONTACTOS)]
    excluidos = filas_iniciales - len(df)
    if excluidos:
        log.append(("ok", f"{excluidos:,} filas excluidas por contactos de soporte."))

    # Deduplicación por el ID real de la conversación.
    if dedup:
        antes = len(df)
        if COL_ID in df.columns:
            df = df.drop_duplicates(subset=[COL_ID], keep='last')
            criterio = f"`{COL_ID}`"
        else:
            claves = [c for c in COLS_DEDUP_FALLBACK if c in df.columns]
            df = df.drop_duplicates(subset=claves, keep='last') if claves else df
            criterio = f"huella compuesta {claves}"
            log.append(("warn", f"El export no trae `{COL_ID}`: se deduplica con {criterio}."))
        removidas = antes - len(df)
        if removidas:
            pct = removidas / antes * 100
            log.append(("warn" if pct > 5 else "ok",
                        f"{removidas:,} conversaciones repetidas eliminadas ({pct:.1f}%) por {criterio}."))
    else:
        log.append(("warn", "Deduplicación desactivada: los días solapados entre planillas se cuentan dos veces."))

    df = df.reset_index(drop=True)

    # --- Fechas
    df['createdAt_dt'] = pd.to_datetime(col_segura(df, 'createdAt'), errors='coerce')
    df['firstSentMessageAt_dt'] = pd.to_datetime(col_segura(df, 'firstSentMessageAt'), errors='coerce')
    df['resolvedAt_dt'] = pd.to_datetime(col_segura(df, 'resolvedAt'), errors='coerce')

    sin_fecha = df['createdAt_dt'].isna().sum()
    if sin_fecha:
        log.append(("warn", f"{sin_fecha:,} filas sin `createdAt` válido: quedan fuera del análisis temporal."))

    df['fecha_corta'] = df['createdAt_dt'].dt.date
    df['periodo'] = df['createdAt_dt'].apply(etiqueta_periodo)
    df['mes_nombre'] = df['createdAt_dt'].dt.month.map(MESES_ES_MAP)

    df['dia_semana'] = df['createdAt_dt'].dt.day_name().map(DAY_MAP)
    df['hora'] = df['createdAt_dt'].dt.hour
    df['hora_30m'] = df['createdAt_dt'].dt.floor('30min').dt.strftime('%H:%M')

    # --- Tiempos
    # El reloj de calendario queda como referencia (lo que espera el cliente en la vida real),
    # pero TODAS las métricas del tablero usan la versión en jornada laboral.
    df['FRT_real_min'] = (df['firstSentMessageAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df.loc[df['FRT_real_min'] < 0, 'FRT_real_min'] = np.nan
    df['res_real_min'] = (df['resolvedAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df.loc[df['res_real_min'] < 0, 'res_real_min'] = np.nan

    fer = feriados_np(df['createdAt_dt'].dt.year.dropna().unique())
    df['FRT_min'] = minutos_laborales(df['createdAt_dt'], df['firstSentMessageAt_dt'], fer)
    df['res_time_wh_min'] = minutos_laborales(df['createdAt_dt'], df['resolvedAt_dt'], fer)
    df['en_horario'] = en_horario_laboral(df['createdAt_dt'], fer)

    # Si el CRM no trae resolvedAt, se cae a su propio cálculo de horario laboral.
    faltan_res = df['res_time_wh_min'].isna()
    if faltan_res.any():
        df.loc[faltan_res, 'res_time_wh_min'] = (
            col_segura(df, 'workingHoursResolutionTime')[faltan_res].apply(time_str_to_minutes))

    df['res_time_min'] = df['res_real_min']
    df['resp_time_min'] = col_segura(df, 'responseTime').apply(time_str_to_minutes)

    # --- Etiquetas
    df['brokers'] = col_segura(df, 'tags').apply(extract_brokers)
    df['tier'] = col_segura(df, 'tags').apply(extract_tier)
    df['servicios'] = col_segura(df, 'tags').apply(lambda t: extract_etiquetas(t, SERVICIOS))
    df['estados'] = col_segura(df, 'tags').apply(lambda t: extract_etiquetas(t, ESTADOS))

    # --- Conexiones (líneas de WhatsApp)
    # Se agrupan por `connectionId`, NO por el nombre: el CRM permite renombrar la línea
    # y el mismo número figuró como "Conexión principal" y después como "Asesores BDI".
    # Sin esto, una misma línea aparecería partida en dos series a lo largo del año.
    if 'connectionId' in df.columns and df['connectionId'].notna().any():
        con_id = df.dropna(subset=['connectionId']).sort_values('createdAt_dt')
        nombres_actuales = con_id.groupby('connectionId')['connection'].last()
        df['conexion'] = df['connectionId'].map(nombres_actuales)
        df['conexion'] = df['conexion'].fillna(col_segura(df, 'connection')).fillna('Sin Conexión')

        historicos = con_id.groupby('connectionId')['connection'].nunique()
        for cid, cant in historicos[historicos > 1].items():
            previos = sorted(set(con_id[con_id['connectionId'] == cid]['connection'].dropna()))
            actual = nombres_actuales[cid]
            otros = [p for p in previos if p != actual]
            log.append(("ok", f"La línea «{actual}» figuró antes como {', '.join(otros)}: "
                              "se unifica por `connectionId` para no partir la serie histórica."))
    else:
        df['conexion'] = col_segura(df, 'connection').fillna('Sin Conexión')

    df['departamento'] = col_segura(df, 'department').fillna('Sin Departamento')

    # --- Identificadores y flags
    if COL_ID not in df.columns:
        df[COL_ID] = np.arange(len(df)).astype(str)
    # Conversaciones sin asesor asignado: quedaron en el chatbot o se cerraron solas.
    # No representan el trabajo de nadie, así que no entran en ninguna métrica.
    if 'user' not in df.columns:
        log.append(("error", "El export no trae la columna `user`: no se puede atribuir ninguna conversación."))
        df['user'] = pd.NA
    df['user'] = df['user'].astype('object').where(df['user'].notna(), pd.NA)
    vacios = df['user'].isna() | (df['user'].astype(str).str.strip() == '')
    if vacios.any():
        sin_resp = int(df.loc[vacios, 'firstSentMessageAt_dt'].isna().sum())
        log.append(("warn", f"{int(vacios.sum()):,} conversaciones sin asesor asignado quedaron fuera del "
                            f"análisis ({sin_resp} de ellas nunca recibieron respuesta). "
                            "Son chats que no salieron del chatbot o se cerraron sin tomarse."))
        df = df[~vacios].reset_index(drop=True)
    if 'contactName' not in df.columns:
        df['contactName'] = 'Sin Nombre'
    df['contactName'] = df['contactName'].fillna('Sin Nombre')

    df['isNewContact'] = col_segura(df, 'isNewContact').fillna(False).astype(bool)
    df['resolvedByInactivity'] = col_segura(df, 'resolvedByInactivity').fillna(False).astype(bool)
    df['startedByContact'] = col_segura(df, 'startedByContact').fillna(False).astype(bool)

    log.append(("ok", f"Base final: {len(df):,} conversaciones de {filas_iniciales:,} filas leídas."))
    return df, log


# -----------------------------------------------------------
# GRÁFICO COMPARTIDO: COMPOSICIÓN PATRIMONIAL POR ASESOR
# -----------------------------------------------------------
def fig_patrimonio_por_asesor(d, para_pdf=False):
    """Una torta por asesor con su mix de segmentos patrimoniales.

    Se arma como subplots en una sola figura (en vez de N gráficos sueltos) para
    que comparta leyenda y se pueda exportar al PDF de una sola pieza. Las
    etiquetas muestran cantidad y porcentaje sin depender del hover.
    """
    from plotly.subplots import make_subplots

    dd = d[d['tier'] != 'Sin Etiqueta Monto']
    if dd.empty:
        return None
    orden = dd.groupby('user')[COL_ID].nunique().sort_values(ascending=False).index.tolist()
    if not orden:
        return None

    cols = min(3, len(orden))
    filas = int(np.ceil(len(orden) / cols))
    fig = make_subplots(
        rows=filas, cols=cols,
        specs=[[{'type': 'domain'} for _ in range(cols)] for _ in range(filas)],
        subplot_titles=[f"{a} · {dd[dd['user'] == a][COL_ID].nunique():,} chats" for a in orden],
        vertical_spacing=0.14, horizontal_spacing=0.04
    )
    for i, asesor in enumerate(orden):
        g = dd[dd['user'] == asesor].groupby('tier')[COL_ID].nunique().reindex(TIERS).fillna(0)
        fig.add_trace(go.Pie(
            labels=list(g.index), values=list(g.values), hole=0.38,
            marker=dict(colors=[TIER_COLORS[t] for t in g.index],
                        line=dict(color='#FFFFFF', width=2)),
            texttemplate='%{value}<br>%{percent}', textposition='inside',
            textfont=dict(size=16 if para_pdf else 12, color='#FFFFFF'),
            insidetextorientation='horizontal',
            sort=False, showlegend=(i == 0),
            hovertemplate="<b>%{label}</b><br>%{value} chats (%{percent})<extra></extra>"
        ), row=i // cols + 1, col=i % cols + 1)

    for ann in fig.layout.annotations:
        ann.font = dict(color='#0F5132', size=15 if para_pdf else 14,
                        family='Inter, Segoe UI, sans-serif')
    fig.update_layout(
        title=dict(text="Mix Patrimonial de la Cartera de Cada Asesor",
                   font=dict(color='#0F5132', size=20), x=0.01, xanchor='left'),
        legend=dict(orientation='h', yanchor='top', y=-0.06, xanchor='center', x=0.5,
                    font=dict(size=13), title=dict(text="Segmento (USD)")),
        height=max(330 * filas, 380),
        paper_bgcolor='#FFFFFF' if para_pdf else 'rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, Segoe UI, sans-serif', color='#1A252C', size=14),
        margin=dict(t=90, b=90, l=30, r=30),
        uniformtext=dict(minsize=11, mode='hide')
    )
    return fig

def grafico(fig, titulo, seccion, alto=None):
    """Dibuja el gráfico en pantalla. El PDF arma los suyos aparte, desde datos
    filtrados por conexión, para que un reporte de asesores no arrastre comercial."""
    st.plotly_chart(fig, **ANCHO)



# ===========================================================
# REPORTE PDF
# ===========================================================
# Las figuras del PDF se arman acá, aparte de las de pantalla y SIEMPRE sobre un
# dataframe ya filtrado por conexión: así un reporte "Solo Asesores" no arrastra
# ni un chat del comercial. Además se dibujan con márgenes y tipografías pensados
# para papel — en pantalla sobra lugar, en A4 apaisado no.
# ===========================================================

def _tema_pdf(fig, alto, leyenda=False, izq=70, inf=70):
    """Normaliza una figura para impresión: fondo blanco, tipografía grande y
    suficiente aire abajo para que la leyenda no se monte sobre el título del eje."""
    fig.update_layout(
        font=dict(family='Inter, Segoe UI, sans-serif', color='#1A252C', size=15),
        title=dict(font=dict(color='#0F5132', size=19), x=0.01, xanchor='left'),
        paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
        height=alto, margin=dict(t=64, b=inf, l=izq, r=60),
        uniformtext=dict(minsize=11, mode='hide'),
        showlegend=leyenda
    )
    if leyenda:
        # La leyenda va MUY por debajo del eje y el margen inferior se agranda en
        # consecuencia: con y=-0.22 el título del eje X quedaba escrito encima.
        fig.update_layout(margin=dict(t=64, b=max(inf, 135), l=izq, r=60),
                          legend=dict(orientation='h', yanchor='top', y=-0.34,
                                      xanchor='center', x=0.5, font=dict(size=13),
                                      bgcolor='rgba(0,0,0,0)'))
    fig.update_xaxes(gridcolor='#EAF0ED', title_font=dict(color='#3F4F49', size=14),
                     tickfont=dict(color='#4A5D57', size=13), title_standoff=14)
    fig.update_yaxes(gridcolor='#EAF0ED', title_font=dict(color='#3F4F49', size=14),
                     tickfont=dict(color='#4A5D57', size=13))
    return fig

def _acortar(serie, largo=26):
    return serie.astype(str).map(lambda t: t if len(t) <= largo else t[:largo - 1] + '…')

def _item(titulo, desc, fig, ancho='full', ratio=0.34, solo=False):
    """`solo=True` reserva una página entera para ese gráfico."""
    return {'tipo': 'fig', 'titulo': titulo, 'desc': desc, 'obj': fig,
            'ancho': ancho, 'ratio': ratio, 'solo': solo}

def figuras_asesores(d, linea, periodos_orden):
    """Todo el bloque de asesores, calculado sobre `d` (ya filtrado a esa línea)."""
    items = []
    if d.empty:
        return items

    conv = d[COL_ID].nunique()
    cont = d['contactNumber'].nunique()
    dias = dias_habiles_efectivos(d['createdAt_dt'])
    items.append({'tipo': 'kpis', 'titulo': f"Capacidad instalada · {linea}",
                  'desc': f"Medido sobre {dias} días hábiles reales del período, con jornada de "
                          f"{HORARIO_TXT} hs. Todos los tiempos descuentan noches, fines de semana y feriados.",
                  'obj': [("Conversaciones", f"{conv:,}"), ("Clientes atendidos", f"{cont:,}"),
                          ("Chats por cliente", f"{conv/cont:.2f}" if cont else "s/d"),
                          ("Chats por día hábil", f"{conv/dias:.1f}" if dias else "s/d"),
                          ("Chats por hora", f"{conv/dias/HORAS_JORNADA:.1f}" if dias else "s/d"),
                          ("FRT mediano", f"{d['FRT_min'].median():.0f} min" if d['FRT_min'].notna().any() else "s/d"),
                          ("FRT p90", f"{d['FRT_min'].quantile(0.9):.0f} min" if d['FRT_min'].notna().any() else "s/d"),
                          ("Resolución mediana", f"{d['res_time_wh_min'].median():.0f} min" if d['res_time_wh_min'].notna().any() else "s/d")]})

    # 1 · Volumen mes a mes
    dm = d.groupby('periodo')[COL_ID].nunique().reset_index(name='Chats').sort_values('periodo')
    f = px.bar(dm, x='periodo', y='Chats', text='Chats', color_discrete_sequence=['#157347'],
               category_orders={'periodo': periodos_orden}, title="Volumen Mensual de Conversaciones")
    f.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=14))
    _tema_pdf(f, 400, inf=90)
    f.update_layout(xaxis_title="", yaxis_title="Conversaciones", xaxis=dict(tickangle=-25))
    items.append(_item("Volumen de trabajo mes a mes",
                       "Conversaciones únicas iniciadas en cada mes. Es la medida de carga: cuánto "
                       "volumen tuvo que absorber el equipo. Compararlo contra la dotación del mes "
                       "muestra si el crecimiento se está acompañando con gente.", f, ratio=0.235))

    # 2 · Carga horaria
    dh = d[(d['hora'] >= HORA_GRAF_INI) & (d['hora'] <= HORA_GRAF_FIN)]
    if not dh.empty:
        dh = dh.groupby('hora_30m')[COL_ID].nunique().reset_index(name='Chats')
        f = px.area(dh, x='hora_30m', y='Chats', markers=True, color_discrete_sequence=['#157347'],
                    title=f"Carga por Franja Horaria ({HORARIO_TXT} hs)")
        f.update_traces(marker=dict(size=7, color='#0F5132'), line=dict(color='#0F5132', width=2),
                        fillcolor='rgba(21,115,71,0.18)')
        _tema_pdf(f, 400, inf=95)
        f.update_layout(xaxis_title="Franja de 30 minutos", yaxis_title="Conversaciones",
                        xaxis=dict(tickangle=-45))
        items.append(_item("A qué hora del día llega la demanda",
                           "Conversaciones acumuladas del período por franja de media hora. Marca dónde "
                           "poner gente: el pico define la dotación mínima y los valles, el margen para "
                           "tareas que no son atención.", f, ratio=0.235))

    # 3 · Mapa de calor
    dhm = d[(d['hora'] >= HORA_GRAF_INI) & (d['hora'] <= HORA_GRAF_FIN) &
            (~d['dia_semana'].isin(['Sábado', 'Domingo']))]
    if not dhm.empty:
        hc = dhm.groupby(['dia_semana', 'hora'])[COL_ID].nunique().reset_index(name='Chats')
        horas = list(range(HORA_GRAF_INI, HORA_GRAF_FIN + 1))
        pv = hc.pivot(index='dia_semana', columns='hora', values='Chats').reindex(
            index=DAY_ORDER_LABORAL, columns=horas).fillna(0)
        z = pv.values
        zmax = z.max() if z.max() > 0 else 1
        xs = [f"{h:02d}h" for h in horas]
        f = go.Figure(go.Heatmap(z=z, x=xs, y=list(pv.index), colorscale=BDI_HEATSCALE,
                                 xgap=4, ygap=4, zmin=0, zmax=zmax,
                                 colorbar=dict(title=dict(text="Chats", font=dict(size=13)),
                                               thickness=14, len=0.8, outlinewidth=0)))
        anns = []
        for i, dia in enumerate(pv.index):
            for j, h in enumerate(horas):
                v = z[i][j]
                if v:
                    anns.append(dict(x=xs[j], y=dia, text=f"<b>{int(v)}</b>", showarrow=False,
                                     font=dict(color='#FFFFFF' if v / zmax > 0.6 else '#14382A', size=13)))
        f.update_layout(annotations=anns,
                        title=dict(text="Concentración de Conversaciones por Día y Hora",
                                   font=dict(color='#0F5132', size=19), x=0.01))
        _tema_pdf(f, 420, izq=110, inf=40)
        f.update_xaxes(side='top', showgrid=False, ticks='', title=None,
                       tickfont=dict(color='#0F5132', size=14))
        f.update_yaxes(showgrid=False, autorange='reversed', ticks='', title=None,
                       tickfont=dict(color='#0F5132', size=15))
        f.update_layout(plot_bgcolor='#FBFDFC')
        pico = hc.loc[hc['Chats'].idxmax()]
        items.append(_item("Distribución de la demanda por día y hora",
                           f"Cruce de día de semana y hora. El pico del período fue {pico['dia_semana']} "
                           f"a las {int(pico['hora']):02d}:00, con {int(pico['Chats'])} conversaciones. "
                           "Las celdas más intensas marcan las franjas de mayor concentración, que son "
                           "las que conviene tener cubiertas.",
                           f, ratio=0.235))

    # 4 · Composición mensual por asesor
    comp = d.groupby(['periodo', 'user'])[COL_ID].nunique().reset_index(name='Chats')
    if not comp.empty:
        comp['Pct'] = comp['Chats'] / comp.groupby('periodo')['Chats'].transform('sum') * 100
        orden_u = comp.groupby('user')['Chats'].sum().sort_values(ascending=False).index.tolist()
        px_ord = [p for p in periodos_orden if p in set(comp['periodo'])]
        f = go.Figure()
        for asesor in orden_u:
            g = comp[comp['user'] == asesor].set_index('periodo').reindex(px_ord)
            ch, pc = g['Chats'].fillna(0), g['Pct'].fillna(0)
            txt = [f"{asesor}<br>{int(c)} · {p:.0f}%" if p >= 7 else "" for c, p in zip(ch, pc)]
            f.add_bar(x=px_ord, y=ch, name=asesor, text=txt,
                      marker=dict(color=USER_COLORS.get(asesor), line=dict(color='#FFFFFF', width=1.5)),
                      textposition='inside', insidetextanchor='middle',
                      textfont=dict(color='#FFFFFF', size=13))
        f.update_layout(barmode='stack', bargap=0.18,
                        title=dict(text="Reparto de la Carga entre Asesores, Mes a Mes",
                                   font=dict(color='#0F5132', size=19), x=0.01))
        _tema_pdf(f, 620, leyenda=True, inf=140)
        f.update_layout(xaxis_title="", yaxis_title="Conversaciones",
                        xaxis=dict(tickangle=-25, tickfont=dict(size=14)),
                        legend=dict(font=dict(size=15)))
        items.append(_item("Reparto del volumen dentro del equipo, mes a mes",
                           "Cada barra es un mes completo, dividido por asesor, con cantidad y peso "
                           "relativo. Las porciones que pesan menos del 7% van sin número para que el "
                           "texto no se amontone. Sirve para ver cómo se distribuye la carga y cómo "
                           "evoluciona esa distribución a lo largo del año.", f, ratio=0.50, solo=True))

    # 5 · Rendimiento por asesor (tabla)
    mu = metricas_usuario_linea(d)
    if not mu.empty:
        tabla = mu[['user', 'Chats', '% de la Línea', 'Chats/Día', 'Contactos', 'Chats/Contacto',
                    'FRT_Mediano', 'FRT_p90', 'Resolucion_Mediana']].rename(columns={
            'user': 'Asesor', '% de la Línea': '% del total', 'Chats/Contacto': 'Chats/cliente',
            'FRT_Mediano': 'FRT med. (min)', 'FRT_p90': 'FRT p90 (min)',
            'Resolucion_Mediana': 'Resolución med. (min)'})
        items.append({'tipo': 'tabla', 'titulo': "Detalle por asesor", 'solo': True,
                      'desc': "Volumen, ritmo diario y tiempos de cada asesor dentro de esta línea. La "
                              "mediana describe la respuesta habitual; el p90, el tiempo que espera el "
                              "10% de conversaciones más demoradas. Una mediana baja junto a un p90 alto "
                              "indica casos puntuales que quedan sin seguimiento, no una demora general.",
                      'obj': tabla})

        comp_p = mu.melt(id_vars='user', value_vars=['FRT_Mediano', 'FRT_p90'],
                         var_name='Métrica', value_name='Minutos')
        comp_p['Métrica'] = comp_p['Métrica'].map({'FRT_Mediano': 'Mediana', 'FRT_p90': 'p90 (la cola)'})
        f = px.bar(comp_p, x='Minutos', y='user', color='Métrica', orientation='h', barmode='group',
                   color_discrete_map={'Mediana': '#157347', 'p90 (la cola)': '#C9A227'},
                   title="Velocidad de Respuesta en Minutos de Jornada: Mediana vs. p90")
        f.update_traces(texttemplate='%{x:.0f}', textposition='outside', cliponaxis=False,
                        textfont=dict(size=13))
        _tema_pdf(f, 400, leyenda=True, izq=120, inf=120)
        f.update_layout(xaxis_title="", yaxis_title="", legend=dict(title=dict(text="")))
        f.update_yaxes(tickfont=dict(size=15))
        items.append(_item("Tiempo de respuesta habitual y cola, por asesor",
                           "Dos barras por asesor: la mediana de la primera respuesta y el p90. La "
                           "distancia entre ambas muestra cuán uniforme es la atención. Medido en "
                           "minutos de jornada, de modo que un mensaje recibido a las 20:00 empieza a "
                           "contar recién al día hábil siguiente.", f, ratio=0.235))

    # 6 · Semáforo
    tr = d['FRT_min'].apply(clasificar_tramo).value_counts().reindex(ORDEN_TRAMOS).fillna(0).reset_index()
    tr.columns = ['Tramo', 'Chats']
    total_tr = tr['Chats'].sum()
    tr['Texto'] = tr.apply(lambda r: f"{int(r['Chats'])} ({r['Chats']/total_tr*100:.0f}%)" if total_tr else "", axis=1)
    f = px.bar(tr[::-1], x='Chats', y='Tramo', orientation='h', text='Texto', color='Tramo',
               color_discrete_map=TRAMO_COLORS, category_orders={'Tramo': ORDEN_TRAMOS[::-1]},
               title="Tiempo hasta la Primera Respuesta")
    f.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=14))
    _tema_pdf(f, 380, izq=170)
    f.update_layout(xaxis_title="Conversaciones", yaxis_title="")
    items.append(_item("Distribución del tiempo de primera respuesta",
                       "La mediana resume, pero no muestra los extremos. Acá está la distribución "
                       "completa en cinco tramos. El de más de 60 minutos es el relevante: son "
                       "conversaciones en las que el cliente ya percibió una demora.", f, ratio=0.235))

    # 7 · Patrimonio por asesor
    fp = fig_patrimonio_por_asesor(d, para_pdf=True)
    if fp is not None:
        fp.update_layout(margin=dict(t=80, b=80, l=40, r=40))
        items.append(_item("Composición patrimonial de cada cartera",
                           "Una torta por asesor con la cantidad de conversaciones y el peso de cada "
                           "segmento dentro de su cartera. Atender patrimonios altos y atender volumen "
                           "de tickets chicos son cargas de naturaleza distinta, y esto permite "
                           "distinguirlas.", fp, ratio=fp.layout.height / 1350.0, solo=True))

    # 8 · Brokers y segmentos (tortas, media página cada una)
    dexp = d.explode('brokers')
    dexp = dexp[dexp['brokers'].notna()]
    if not dexp.empty:
        bu = dexp.drop_duplicates(subset=['contactNumber', 'brokers'])['brokers'].value_counts().reset_index()
        bu.columns = ['Broker', 'Personas']
        f = px.pie(bu, values='Personas', names='Broker', hole=0.45, color='Broker',
                   color_discrete_map=BROKER_COLORS, title="Personas Únicas por Broker")
        f.update_traces(texttemplate='<b>%{value}</b><br>%{percent}', textposition='inside',
                        textfont=dict(size=19, color='#FFFFFF'),
                        marker=dict(line=dict(color='#FFFFFF', width=2)))
        _tema_pdf(f, 560, leyenda=True, izq=20, inf=130)
        f.update_layout(legend=dict(font=dict(size=16)), margin=dict(t=64, b=130, l=20, r=20))
        items.append(_item("Con qué brokers opera la cartera",
                           "Personas distintas atendidas por broker, no cantidad de conversaciones: "
                           "evita que un cliente muy conversador distorsione el peso de su plataforma.",
                           f, ancho='medio', ratio=0.86))

    dt = d[d['tier'] != 'Sin Etiqueta Monto']
    if not dt.empty:
        tu = dt.drop_duplicates(subset=['contactNumber', 'tier'])['tier'].value_counts().reindex(TIERS).dropna().reset_index()
        tu.columns = ['Segmento', 'Personas']
        f = px.pie(tu, values='Personas', names='Segmento', hole=0.45, color='Segmento',
                   color_discrete_map=TIER_COLORS, category_orders={'Segmento': TIERS},
                   title="Personas Únicas por Segmento Patrimonial")
        f.update_traces(texttemplate='<b>%{value}</b><br>%{percent}', textposition='inside',
                        textfont=dict(size=19, color='#FFFFFF'),
                        marker=dict(line=dict(color='#FFFFFF', width=2)))
        _tema_pdf(f, 560, leyenda=True, izq=20, inf=150)
        f.update_layout(legend=dict(font=dict(size=15)), margin=dict(t=64, b=150, l=20, r=20))
        items.append(_item("Cómo se reparte el patrimonio de la base",
                           "Clientes distintos por tramo de monto declarado. Es el mapa de a quién se "
                           "está atendiendo, independiente de cuánto escriba cada uno.",
                           f, ancho='medio', ratio=0.86))

    # 9 · Fricción y SLA
    if not dexp.empty:
        fr = dexp.groupby('brokers').agg(Chats=(COL_ID, 'nunique'),
                                         Usuarios=('contactNumber', 'nunique')).reset_index()
        fr['Ratio'] = fr['Chats'] / fr['Usuarios']
        f = px.bar(fr.sort_values('Ratio'), x='Ratio', y='brokers', orientation='h', text='Ratio',
                   color='brokers', color_discrete_map=BROKER_COLORS,
                   title="Conversaciones por Cliente, según Broker")
        f.update_traces(texttemplate='%{text:.2f}', textposition='outside', cliponaxis=False,
                        textfont=dict(size=17))
        _tema_pdf(f, 360, izq=120)
        f.update_xaxes(tickfont=dict(size=15)); f.update_yaxes(tickfont=dict(size=16))
        f.update_layout(xaxis_title="Chats por cliente único", yaxis_title="")
        items.append(_item("Consultas por cliente según plataforma",
                           "Conversaciones divididas por clientes únicos de cada broker. Un valor alto "
                           "indica que el mismo cliente vuelve a escribir más veces, lo que suele "
                           "responder a fricción operativa de esa plataforma y se trabaja con "
                           "instructivos o soporte.", f, ancho='medio', ratio=0.52))

    if not dt.empty:
        sla = dt.groupby('tier')['FRT_min'].median().reindex(TIERS).dropna().reset_index()
        f = px.bar(sla, x='FRT_min', y='tier', orientation='h', text='FRT_min', color='tier',
                   color_discrete_map=TIER_COLORS, category_orders={'tier': TIERS},
                   title="Tiempo de Respuesta según Patrimonio")
        f.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False,
                        textfont=dict(size=17))
        _tema_pdf(f, 360, izq=165)
        f.update_xaxes(tickfont=dict(size=15)); f.update_yaxes(tickfont=dict(size=16))
        f.update_layout(xaxis_title="Minutos de jornada (mediana)", yaxis_title="")
        items.append(_item("Tiempo de respuesta según segmento patrimonial",
                           "Mediana de primera respuesta por tramo de monto. Es el SLA que surge de la "
                           "práctica, no del manual. Permite verificar si el orden de atención coincide "
                           "con el que la consultora se propuso.", f, ancho='medio', ratio=0.52))

    # 10 · Top clientes
    top = d.groupby('contactName').agg(
        Chats=(COL_ID, 'nunique'),
        Asesor=('user', lambda x: x.mode()[0] if not x.mode().empty else '')).reset_index()
    top = top.sort_values('Chats', ascending=False).head(12).sort_values('Chats')
    if not top.empty:
        top['Nombre'] = _acortar(top['contactName'], 34)
        f = px.bar(top, x='Chats', y='Nombre', orientation='h', text='Chats', color='Asesor',
                   color_discrete_map=USER_COLORS, title="Clientes con Mayor Volumen de Consultas")
        f.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=15))
        _tema_pdf(f, 620, leyenda=True, izq=300, inf=120)
        f.update_layout(xaxis_title="Conversaciones", yaxis_title="", bargap=0.35,
                        legend_title="Asesor habitual")
        items.append(_item("Clientes con mayor volumen de consultas",
                           "Los doce contactos con más conversaciones en el período, con el color del "
                           "asesor que los atiende habitualmente. Sirve para dimensionar cuánto tiempo "
                           "concentran unas pocas cuentas y evaluar si conviene otro canal para ellas.",
                           f, ratio=0.36, solo=True))

    return items

def figuras_comercial(d, linea, df_historia):
    """Bloque comercial, calculado sobre `d` (ya filtrado a la línea comercial)."""
    items = []
    leads = analizar_captacion(d, df_historia, linea)
    if leads.empty:
        return items

    total = len(leads)
    es_cli = ((leads['Desenlace'] == DES_CLIENTE) | (leads['Estado'] == 'Ya era cliente'))
    n_cli = int(es_cli.sum())
    nv = leads[~es_cli]
    n_leads = len(nv)
    n_mem = int((nv['Desenlace'] == DES_MEMBRESIA).sum())
    n_con = int((nv['Desenlace'] == DES_CONSULTORIA).sum())
    n_der = int((nv['Desenlace'] == DES_DERIVADO).sum())
    n_nc = int((nv['Desenlace'] == DES_NO_CALIFICA).sum())
    n_ep = int((nv['Desenlace'] == DES_EN_PROCESO).sum())
    n_sd = int((nv['Desenlace'] == DES_SIN_DEFINIR).sum())
    ganados = n_mem + n_con + n_der
    conv = ganados / n_leads * 100 if n_leads else np.nan

    items.append({'tipo': 'kpis', 'titulo': f"Resultado comercial · {linea}",
                  'desc': "La unidad es el contacto único, no la conversación: en captación la persona "
                          "escribe una vez y no vuelve. La tasa de conversión se calcula sobre leads "
                          "reales, descontando a quienes ya eran clientes.",
                  'obj': [("Escribieron", f"{total:,}"), ("Ya eran clientes", f"{n_cli:,}"),
                          ("Leads reales", f"{n_leads:,}"), ("Leads ganados", f"{ganados:,}"),
                          ("Tasa de conversión", f"{conv:.1f}%" if pd.notna(conv) else "s/d"),
                          ("Membresías", f"{n_mem:,}"), ("Consultorías", f"{n_con:,}"),
                          ("Derivados", f"{n_der:,}"), ("No aplica", f"{n_nc:,}"),
                          ("En proceso", f"{n_ep:,}"), ("Sin definir", f"{n_sd:,}"),
                          ("FRT p90", f"{nv['FRT_min'].quantile(0.9):.0f} min" if nv['FRT_min'].notna().any() else "s/d")]})

    # Embudo
    ys = ['3 · Leads ganados', '2 · Leads reales', '1 · Escribieron al comercial']
    anchos = [ganados, n_leads, total]
    amax = max(total, 1)
    pc = lambda v, b: f"{v/b*100:.0f}%" if b else "s/d"
    f = go.Figure()
    f.add_bar(y=ys, x=[(amax - a) / 2 for a in anchos], orientation='h',
              marker=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip')
    f.add_bar(y=ys, x=[0, n_leads, total], orientation='h',
              marker=dict(color=['rgba(0,0,0,0)', COLOR_ETAPA_2, COLOR_ETAPA_1],
                          line=dict(color='#FFFFFF', width=2)),
              text=['', f"{n_leads} leads reales · {pc(n_leads, total)}", f"{total} contactos únicos"],
              textposition='inside', insidetextanchor='middle',
              textfont=dict(color='#FFFFFF', size=16), showlegend=False)
    for et, val in [(DES_MEMBRESIA, n_mem), (DES_CONSULTORIA, n_con), (DES_DERIVADO, n_der)]:
        corto = et.split(' - ')[0].split(' a ')[0]
        f.add_bar(y=ys, x=[val, 0, 0], orientation='h', name=et,
                  marker=dict(color=DESENLACE_COLORS[et], line=dict(color='#FFFFFF', width=2)),
                  text=[f"{corto}<br>{val} · {pc(val, n_leads)}" if val else '', '', ''],
                  textposition='inside', insidetextanchor='middle',
                  textfont=dict(color='#FFFFFF', size=14))
    f.update_layout(barmode='stack', bargap=0.3,
                    title=dict(text=f"Embudo Comercial · {linea}",
                               font=dict(color='#0F5132', size=19), x=0.01))
    _tema_pdf(f, 400, leyenda=True, izq=230, inf=120)
    f.update_layout(xaxis=dict(visible=False, range=[0, amax * 1.02]),
                    yaxis=dict(showgrid=False, tickfont=dict(color='#0F5132', size=15),
                               categoryorder='array', categoryarray=ys))
    for fila, cant, txt, col in [('2 · Leads reales', n_cli, 'ya eran clientes', '#8A6D00'),
                                 ('3 · Leads ganados', n_leads - ganados, 'sin cerrar', '#7A867F')]:
        if cant:
            f.add_annotation(xref='paper', x=1.015, y=fila, xanchor='left', yanchor='middle',
                             text=f"<b>−{cant}</b><br><span style='font-size:12px'>{txt}</span>",
                             showarrow=False, align='left', font=dict(color=col, size=14))
    f.update_layout(margin=dict(t=64, b=120, l=230, r=170))
    items.append(_item("Del primer mensaje a la venta",
                       "Tres escalones: todo lo que entró, lo que era lead de verdad y lo que se ganó. "
                       "El último se abre en las tres formas de ganarlo — membresía, consultoría o "
                       "derivación a un asesor. A la derecha, lo que se cae en cada paso.", f, ratio=0.235))

    # Conciliación
    cats = [(DES_MEMBRESIA, n_mem), (DES_CONSULTORIA, n_con), (DES_DERIVADO, n_der),
            (DES_NO_CALIFICA, n_nc), (DES_EN_PROCESO, n_ep), (DES_SIN_DEFINIR, n_sd)]
    f = go.Figure()
    for et, val in cats:
        if not val:
            continue
        p = val / n_leads * 100 if n_leads else 0
        f.add_bar(y=['Leads reales'], x=[val], orientation='h', name=et,
                  marker=dict(color=DESENLACE_COLORS[et], line=dict(color='#FFFFFF', width=2)),
                  text=[f"{val}<br>{p:.0f}%"], textposition='inside', insidetextanchor='middle',
                  textfont=dict(color='#FFFFFF' if et != DES_SIN_DEFINIR else '#14382A', size=14))
    f.update_layout(barmode='stack', bargap=0.65,
                    title=dict(text=f"Desglose Completo de los {n_leads} Leads Reales",
                               font=dict(color='#0F5132', size=19), x=0.01))
    _tema_pdf(f, 300, leyenda=True, izq=40, inf=110)
    f.update_layout(xaxis=dict(visible=False), yaxis=dict(showticklabels=False, showgrid=False))
    items.append(_item("En qué terminó cada lead",
                       "El hueco entre leads y ganados no es una sola cosa. «No aplica» es un descarte "
                       "decidido, «En proceso» una charla abierta y «Sin definir» un desenlace que nadie "
                       "registró. Solo el tercero es un problema de gestión. Cuando llegue a cero, la "
                       "conversión del embudo deja de ser un piso y pasa a ser el número real.",
                       f, ratio=0.235))

    # Semáforo de leads
    tr = nv['Tramo'].value_counts().reindex(ORDEN_TRAMOS).fillna(0).reset_index()
    tr.columns = ['Tramo', 'Leads']
    f = px.bar(tr[::-1], x='Leads', y='Tramo', orientation='h', color='Tramo',
               text=[f"{int(v)} ({v/n_leads*100:.0f}%)" if n_leads else "" for v in tr['Leads'][::-1]],
               color_discrete_map=TRAMO_COLORS, category_orders={'Tramo': ORDEN_TRAMOS[::-1]},
               title="Tiempo hasta Contestarle a un Lead")
    f.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=14))
    _tema_pdf(f, 380, izq=170)
    f.update_layout(xaxis_title="Leads", yaxis_title="")
    items.append(_item("Tiempo de respuesta a prospectos",
                       "En captación la velocidad pesa más que en cartera: el prospecto todavía no "
                       "tiene relación con nosotros y está comparando. Cada tramo que se corre hacia "
                       "abajo es conversión que se pierde sin dejar rastro.", f, ratio=0.235))

    # Flujo diario
    pd_ = nv.groupby(['fecha', 'Desenlace']).size().reset_index(name='Leads')
    if not pd_.empty:
        f = px.bar(pd_, x='fecha', y='Leads', color='Desenlace', color_discrete_map=DESENLACE_COLORS,
                   category_orders={'Desenlace': DESENLACES}, title="Leads que Entran, Día por Día")
        _tema_pdf(f, 400, leyenda=True, inf=110)
        f.update_layout(barmode='stack', xaxis_title="", yaxis_title="Leads",
                        legend=dict(font=dict(size=15)))
        f.update_xaxes(tickfont=dict(size=15)); f.update_yaxes(tickfont=dict(size=15))
        items.append(_item("Entrada de leads día por día",
                           "Leads nuevos por día, coloreados por cómo terminaron. Sirve para ver si la "
                           "captación es pareja o depende de picos puntuales, y si los días de más "
                           "volumen son también los de peor cierre.", f, ancho='medio', ratio=0.52))

    # Hora de entrada vs demora
    ph = nv.groupby('hora_ingreso').agg(Leads=('contactNumber', 'count'),
                                        FRT=('FRT_min', 'median')).reset_index()
    if not ph.empty:
        f = go.Figure()
        f.add_bar(x=ph['hora_ingreso'], y=ph['Leads'], name='Leads que entran', marker_color='#8FBF74')
        f.add_scatter(x=ph['hora_ingreso'], y=ph['FRT'], name='Demora mediana (min)', yaxis='y2',
                      mode='lines+markers', line=dict(color='#C9A227', width=3), marker=dict(size=8))
        f.update_layout(title=dict(text="Entrada de Leads y Demora, por Hora del Día",
                                   font=dict(color='#0F5132', size=19), x=0.01))
        _tema_pdf(f, 400, leyenda=True, inf=110, izq=70)
        f.update_layout(legend=dict(font=dict(size=15)))
        f.update_layout(xaxis=dict(title="", dtick=1, tickfont=dict(size=14)),
                        yaxis=dict(title="Leads"),
                        yaxis2=dict(title="Minutos", overlaying='y', side='right', showgrid=False,
                                    title_font=dict(color='#8A6D00'), tickfont=dict(color='#8A6D00')))
        items.append(_item("Entrada y demora según hora del día",
                           "Barras: cuántos leads entran en cada hora. Línea dorada: cuánto tardan en "
                           "recibir respuesta. Donde la barra es alta y la línea también, hay demanda "
                           "llegando a una hora en la que nadie está mirando.", f, ancho='medio', ratio=0.52))

    # Tabla por asesor
    pa = nv.groupby('Asesor').agg(
        Leads=('contactNumber', 'nunique'),
        FRT_Mediano=('FRT_min', 'median'),
        FRT_p90=('FRT_min', lambda s: s.quantile(0.9)),
        Membresias=('Desenlace', lambda s: int((s == DES_MEMBRESIA).sum())),
        Consultorias=('Desenlace', lambda s: int((s == DES_CONSULTORIA).sum())),
        Derivados=('Desenlace', lambda s: int((s == DES_DERIVADO).sum())),
        No_Califica=('Desenlace', lambda s: int((s == DES_NO_CALIFICA).sum())),
        En_Proceso=('Desenlace', lambda s: int((s == DES_EN_PROCESO).sum())),
        Sin_Definir=('Desenlace', lambda s: int((s == DES_SIN_DEFINIR).sum())),
    ).reset_index()
    pa['Ganados'] = pa['Membresias'] + pa['Consultorias'] + pa['Derivados']
    pa['% Conv.'] = np.where(pa['Leads'] > 0, pa['Ganados'] / pa['Leads'] * 100, np.nan)
    pa = pa.sort_values('Leads', ascending=False)
    items.append({'tipo': 'tabla', 'titulo': "Detalle por asesor en la línea comercial",
                  'desc': "Leads tomados por cada asesor, tiempos de respuesta y desenlace. Una "
                          "columna «Sin definir» alta no indica menos ventas, sino registro incompleto: "
                          "mientras esa columna tenga peso, la conversión de esa fila es un piso y no "
                          "un resultado comparable.",
                  'obj': pa[['Asesor', 'Leads', 'FRT_Mediano', 'FRT_p90', 'Membresias', 'Consultorias',
                             'Derivados', 'Ganados', '% Conv.', 'No_Califica', 'En_Proceso',
                             'Sin_Definir']].rename(columns={
                      'FRT_Mediano': 'FRT med.', 'FRT_p90': 'FRT p90', 'Membresias': 'Memb.',
                      'Consultorias': 'Consult.', 'No_Califica': 'No aplica',
                      'En_Proceso': 'En proceso', 'Sin_Definir': 'Sin definir'})})
    return items


def _fig_a_png(fig, ancho_px, alto_px):
    """kaleido 0.2.1 trae su propio chromium: no depende de que haya navegador."""
    return fig.to_image(format='png', width=int(ancho_px), height=int(alto_px), scale=2)

def construir_pdf(bloques, titulo, subtitulo, meta):
    """A4 apaisado. El layout se calcula a mano: cada gráfico declara si ocupa toda
    la página o media, y los de media se emparejan de a dos. Así no quedan hojas
    con un solo gráfico y medio metro de blanco debajo."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                    Table, TableStyle, PageBreak, KeepTogether, CondPageBreak)

    buf = io.BytesIO()
    W, H = landscape(A4)
    MG = 13 * mm
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=MG, rightMargin=MG,
                            topMargin=17 * mm, bottomMargin=13 * mm,
                            title=titulo, author="BDI Consultora")
    util = W - 2 * MG
    medio = (util - 8 * mm) / 2

    S = getSampleStyleSheet()
    H1 = ParagraphStyle('H1', parent=S['Title'], fontName='Helvetica-Bold', fontSize=23,
                        textColor=colors.HexColor('#0F5132'), alignment=TA_LEFT,
                        spaceAfter=3, leading=27)
    SUB = ParagraphStyle('SUB', parent=S['Normal'], fontSize=9.5, leading=13,
                         textColor=colors.HexColor('#5B6E67'), spaceAfter=14)
    H2 = ParagraphStyle('H2', parent=S['Heading2'], fontName='Helvetica-Bold', fontSize=15,
                        textColor=colors.white, spaceBefore=0, spaceAfter=0, leading=19)
    TIT = ParagraphStyle('TIT', parent=S['Heading3'], fontName='Helvetica-Bold', fontSize=12,
                         textColor=colors.HexColor('#0F5132'), spaceBefore=0, spaceAfter=2, leading=15)
    DESC = ParagraphStyle('DESC', parent=S['Normal'], fontSize=8.3, leading=11.2,
                          textColor=colors.HexColor('#5B6E67'), spaceAfter=5, alignment=TA_JUSTIFY)

    def banda(texto):
        t = Table([[Paragraph(texto, H2)]], colWidths=[util], rowHeights=[9 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0F5132')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        return t

    def encabezado(c, d_):
        c.saveState()
        c.setFillColor(colors.HexColor('#0F5132'))
        c.rect(0, H - 9 * mm, W, 9 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white); c.setFont('Helvetica-Bold', 8.5)
        c.drawString(MG, H - 6.2 * mm, "BDI CONSULTORA · Dashboard de Mensajería")
        c.drawRightString(W - MG, H - 6.2 * mm, titulo)
        c.setStrokeColor(colors.HexColor('#DDE5E1')); c.setLineWidth(0.5)
        c.line(MG, 10 * mm, W - MG, 10 * mm)
        c.setFillColor(colors.HexColor('#8A9A93')); c.setFont('Helvetica', 7)
        c.drawString(MG, 6.5 * mm, meta)
        c.drawRightString(W - MG, 6.5 * mm, f"Página {d_.page}")
        c.restoreState()

    def img(item, ancho_pt):
        # El lienzo se calcula PROPORCIONAL al ancho final en la hoja. Antes todo se
        # renderizaba a 1450 px: un gráfico de media página se achicaba a la mitad y
        # su tipografía terminaba imprimiéndose a 3,8 pt, ilegible.
        alto_pt = ancho_pt * item['ratio']
        lienzo = ancho_pt * 1.9
        png = _fig_a_png(item['obj'], lienzo, lienzo * item['ratio'])
        return Image(io.BytesIO(png), width=ancho_pt, height=alto_pt)

    def partes(item, ancho_pt):
        """Título + explicación + gráfico. Como lista plana, porque un KeepTogether
        adentro de una celda de tabla reporta altura infinita y rompe el layout."""
        return [Paragraph(item['titulo'], TIT), Paragraph(item['desc'], DESC),
                img(item, ancho_pt)]

    def celda(item, ancho_pt):
        """Para gráficos a ancho completo: se mantiene unido título, texto y figura."""
        return KeepTogether(partes(item, ancho_pt) + [Spacer(1, 7)])

    def tabla_kpi(pares, ancho_pt, cols=None):
        # Con muchos indicadores conviene 6 columnas: entran en dos filas y dejan
        # lugar para que el primer gráfico comparta la página.
        cols = cols or (6 if len(pares) > 8 else 4)
        datos, fila = [], []
        for et, val in pares:
            fila.append(Paragraph(
                f"<font size=6.2 color='#5B6E67'>{et.upper()}</font><br/>"
                f"<font size=13 color='#0F5132'><b>{val}</b></font>", DESC))
            if len(fila) == cols:
                datos.append(fila); fila = []
        if fila:
            fila += [''] * (cols - len(fila)); datos.append(fila)
        t = Table(datos, colWidths=[ancho_pt / cols] * cols)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDE5E1')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FBFDFC')),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 9), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        return t

    def tabla_datos(dfv, ancho_pt):
        dfv = dfv.copy()
        for c in dfv.columns:
            if pd.api.types.is_float_dtype(dfv[c]):
                dfv[c] = dfv[c].map(lambda v: '—' if pd.isna(v) else f"{v:,.1f}")
        cab = ParagraphStyle('cab', parent=S['Normal'], fontSize=7.4, leading=9,
                             textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
        datos = [[Paragraph(str(c), cab) for c in dfv.columns]] + dfv.astype(str).values.tolist()
        n = len(dfv.columns)
        anchos = [ancho_pt * 0.16] + [(ancho_pt * 0.84) / (n - 1)] * (n - 1) if n > 1 else [ancho_pt]
        t = Table(datos, repeatRows=1, colWidths=anchos)
        estilo = [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F5132')),
                  ('FONTSIZE', (0, 1), (-1, -1), 8),
                  ('ALIGN', (1, 0), (-1, -1), 'CENTER'), ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                  ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                  ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#DDE5E1')),
                  ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]
        for i in range(1, len(datos)):
            if i % 2 == 0:
                estilo.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F4F9F6')))
        t.setStyle(TableStyle(estilo))
        return t

    # ---- Paginado.
    # Antes del elemento se inserta un CondPageBreak con su alto estimado: reportlab
    # salta de hoja solo si realmente no entra. Llevar la cuenta a mano generaba
    # páginas en blanco cuando la estimación y el alto real no coincidían.
    FRAME = H - doc.topMargin - doc.bottomMargin
    ALTO_TITULO, ALTO_DESC, ALTO_BANDA = 17, 40, 36

    hist = [Paragraph(titulo, H1), Paragraph(subtitulo, SUB)]

    def alto_de(item, ancho_pt):
        if item['tipo'] == 'kpis':
            cols_kpi = 6 if len(item['obj']) > 8 else 4
            return ALTO_TITULO + ALTO_DESC + int(np.ceil(len(item['obj']) / cols_kpi)) * 35 + 12
        if item['tipo'] == 'tabla':
            return ALTO_TITULO + ALTO_DESC + (len(item['obj']) + 1) * 23 + 14
        return ALTO_TITULO + ALTO_DESC + ancho_pt * item['ratio'] + 12

    for bi, (nombre, items) in enumerate(bloques):
        if not items:
            continue
        if bi > 0:
            hist.append(PageBreak())
        hist += [banda(nombre), Spacer(1, 10)]

        i = 0
        while i < len(items):
            it = items[i]
            empareja = (it.get('ancho') == 'medio' and i + 1 < len(items)
                        and items[i + 1].get('ancho') == 'medio')
            ancho_pt = medio if empareja else util
            h = alto_de(it, ancho_pt)
            if empareja:
                h = max(h, alto_de(items[i + 1], medio))
            # Un elemento marcado `solo` pide casi toda la hoja, así queda destacado.
            hist.append(CondPageBreak(min(FRAME - 6, h + 30 if it.get('solo') else h)))

            if it['tipo'] == 'kpis':
                hist += [Paragraph(it['titulo'], TIT), Paragraph(it['desc'], DESC),
                         tabla_kpi(it['obj'], util), Spacer(1, 12)]
            elif it['tipo'] == 'tabla':
                hist += [Paragraph(it['titulo'], TIT), Paragraph(it['desc'], DESC),
                         tabla_datos(it['obj'], util), Spacer(1, 12)]
            elif empareja:
                par = Table([[partes(it, medio), partes(items[i + 1], medio)]],
                            colWidths=[medio, medio])
                par.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                         ('RIGHTPADDING', (0, 0), (0, 0), 8 * mm),
                                         ('RIGHTPADDING', (1, 0), (1, 0), 0),
                                         ('TOPPADDING', (0, 0), (-1, -1), 0),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
                hist += [par, Spacer(1, 10)]
            else:
                hist += partes(it, util) + [Spacer(1, 10)]

            i += 2 if empareja else 1

    while hist and isinstance(hist[-1], PageBreak):
        hist.pop()
    doc.build(hist, onFirstPage=encabezado, onLaterPages=encabezado)
    buf.seek(0)
    return buf.getvalue()

# ---------------------------------------------------------
# PANEL DE CONTROL LATERAL
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Panel de Control")

def marcar_sincronizacion():
    st.session_state["_forzar_sync"] = True
    st.cache_data.clear()

st.sidebar.button("🔄 Sincronizar datos de Google Drive",
                  on_click=marcar_sincronizacion, **ANCHO)

# Forzar NO borra la carpeta local: solo ignora el manifiesto y revalida contra Drive.
# Borrar primero y descargar después dejaba la app sin datos si la descarga fallaba.
forzar = st.session_state.pop("_forzar_sync", False)

archivos_drive, log_listado, listado_en_vivo = listar_archivos_drive()
log_descarga, manifest = sincronizar_archivos(archivos_drive, forzar=forzar,
                                              listado_en_vivo=listado_en_vivo)
df_drive_raw, log_lectura = leer_planillas(firma_local())

uploaded_files = st.sidebar.file_uploader("📂 O cargar planilla .xlsx manualmente:",
                                          type=["xlsx"], accept_multiple_files=True)

frames = [df_drive_raw] if not df_drive_raw.empty else []
log_upload = []
if uploaded_files:
    for up in uploaded_files:
        try:
            d = pd.read_excel(up)
            d['archivo_origen'] = f"[manual] {up.name}"
            d['mes_archivo'] = extract_month_from_filename(up.name)
            frames.append(d)
            log_upload.append(("ok", f"«{up.name}» (manual): {len(d):,} filas."))
        except Exception as e:
            log_upload.append(("error", f"«{up.name}» → {type(e).__name__}: {e}"))

dedup_on = st.sidebar.checkbox(
    "Eliminar filas duplicadas", value=True,
    help="Descarta filas idénticas cuando dos planillas comparten días. Si sospechás que se están "
         "borrando chats legítimos, destildalo y compará el Total Chats."
)

if frames:
    df_raw, log_proceso = procesar(pd.concat(frames, ignore_index=True), dedup=dedup_on)
else:
    df_raw, log_proceso = pd.DataFrame(), []

# ---------------------------------------------------------
# DIAGNÓSTICO (clave para saber si el mes nuevo entró o no)
# ---------------------------------------------------------
todos_los_logs = log_listado + log_descarga + log_lectura + log_upload + log_proceso
hay_errores = any(nivel == "error" for nivel, _ in todos_los_logs)

if df_raw.empty:
    st.error("**No hay datos para procesar.** Abajo está el detalle de qué falló.")
    st.markdown("#### 🩺 Qué pasó")
    for nivel, msg in todos_los_logs:
        if nivel == "error":
            st.error(msg, icon="🚫")
        elif nivel == "warn":
            st.warning(msg, icon="⚠️")
    st.markdown("""
#### Cómo recuperarlo

1. **Ahora mismo:** cargá los `.xlsx` con **📂 "O cargar planilla .xlsx manualmente"**
   en la barra lateral. Eso no depende de Drive y el tablero funciona igual.
2. **Si los errores dicen que la descarga falló:** la app necesita credenciales para bajar
   archivos privados. Revisá que `gcp_service_account` esté en los *Secrets* y que la carpeta
   de Drive esté compartida con ese mail.
3. **Si dice que no hay credenciales:** sin Service Account cada planilla tiene que estar
   compartida como *«Cualquiera con el enlace»* para que la descarga anónima funcione.
""")
    st.stop()

resumen_archivos = df_raw.groupby('archivo_origen').agg(
    Conversaciones=(COL_ID, 'nunique'),
    Contactos=('contactNumber', 'nunique'),
    Desde=('createdAt_dt', 'min'),
    Hasta=('createdAt_dt', 'max'),
    Periodos=('periodo', lambda s: ', '.join(sorted(s.dropna().unique()))),
    Conexiones=('conexion', lambda s: ', '.join(sorted(s.dropna().unique())))
).reset_index()
resumen_archivos['Desde'] = resumen_archivos['Desde'].dt.strftime('%d/%m/%Y')
resumen_archivos['Hasta'] = resumen_archivos['Hasta'].dt.strftime('%d/%m/%Y')
resumen_archivos.columns = ['Planilla', 'Conversaciones', 'Contactos', 'Desde', 'Hasta', 'Períodos', 'Conexiones']

# Aviso si el nombre del archivo declara un mes distinto al de su contenido.
for _, fila in resumen_archivos.iterrows():
    mes_nombre_archivo = extract_month_from_filename(fila['Planilla'])
    meses_reales = {p.split('· ')[-1] for p in fila['Períodos'].split(', ') if '· ' in p}
    if mes_nombre_archivo != 'Mes No Especificado' and meses_reales:
        declarado = mes_nombre_archivo.split(' - ')[-1]
        if declarado not in meses_reales:
            todos_los_logs.append(("warn",
                f"«{fila['Planilla']}» sugiere {declarado} por su nombre pero contiene {', '.join(sorted(meses_reales))}. "
                "Se usan siempre las fechas reales de `createdAt`, no el nombre del archivo."))

with st.sidebar.expander("🩺 Diagnóstico de carga", expanded=hay_errores):
    for nivel, msg in todos_los_logs:
        if nivel == "ok":
            st.success(msg, icon="✅")
        elif nivel == "warn":
            st.warning(msg, icon="⚠️")
        else:
            st.error(msg, icon="🚫")

st.sidebar.success(f"📁 **{len(resumen_archivos)} planillas activas**")
with st.sidebar.expander("📄 Cobertura por planilla"):
    st.dataframe(resumen_archivos, hide_index=True, **ANCHO)

# Asesores que aparezcan más adelante y no estén en la paleta fija reciben color propio,
# para que un alta nueva no quede con el color por defecto de Plotly.
for _i, _u in enumerate(sorted(df_raw['user'].dropna().unique())):
    if _u not in USER_COLORS:
        USER_COLORS[_u] = PALETA_ASESORES[_i % len(PALETA_ASESORES)]

# ---------------------------------------------------------
# FILTROS DINÁMICOS
# ---------------------------------------------------------
st.sidebar.markdown("### 🔎 Filtros de Búsqueda")

# Los períodos llevan año ("2026-01 · Enero"), así que ordenan solos y soportan varios años.
periodos_disponibles = sorted(p for p in df_raw['periodo'].dropna().unique() if p != 'Sin Período')
if 'Sin Período' in set(df_raw['periodo'].dropna()):
    periodos_disponibles.append('Sin Período')
periodos_sel = st.sidebar.multiselect("Período:", periodos_disponibles, default=periodos_disponibles)

# Conexiones ordenadas por volumen: el color se asigna solo, sin tocar el código
# cuando se sume una línea nueva.
conexiones_disponibles = list(
    df_raw.groupby('conexion')[COL_ID].nunique().sort_values(ascending=False).index
)
CONEXION_COLORS = {c: CONEXION_PALETA[i % len(CONEXION_PALETA)]
                   for i, c in enumerate(conexiones_disponibles)}

conexiones_sel = st.sidebar.multiselect(
    "Conexión (línea de WhatsApp):", conexiones_disponibles, default=conexiones_disponibles,
    help="Cada línea es un número distinto. Los asesores atienden en las dos, "
         "así que el filtro sirve para aislar el rendimiento de cada una."
)

asesores_disponibles = sorted(df_raw['user'].dropna().unique())
asesores_sel = st.sidebar.multiselect("Asesor:", asesores_disponibles, default=asesores_disponibles)

brokers_disponibles = sorted({b for lista in df_raw['brokers'] for b in lista})
brokers_sel = st.sidebar.multiselect("Broker:", brokers_disponibles, default=brokers_disponibles,
                                     help="Un chat con varias etiquetas de broker aparece si coincide con alguna.")

df = df_raw.copy()
if periodos_sel: df = df[df['periodo'].isin(periodos_sel)]
if conexiones_sel: df = df[df['conexion'].isin(conexiones_sel)]
if asesores_sel: df = df[df['user'].isin(asesores_sel)]
if brokers_sel and len(brokers_sel) < len(brokers_disponibles):
    df = df[df['brokers'].apply(lambda lista: any(b in brokers_sel for b in lista))]

if df.empty:
    st.warning("Los filtros actuales no devuelven ninguna conversación. Ampliá la selección.")
    st.stop()

# ---------------------------------------------------------
# HEADER PRINCIPAL Y KPIs
# ---------------------------------------------------------
ultimo_dato = df_raw['createdAt_dt'].max()
ultimo_dato_txt = ultimo_dato.strftime('%d/%m/%Y %H:%M') if pd.notna(ultimo_dato) else "s/d"
periodos_txt = f"{len(periodos_sel)} período(s)" if periodos_sel else "todos los períodos"

st.markdown(f"""
<div class="bdi-header">
    <h1>📈 Dashboard de Gestión de Mensajería</h1>
    <p>BDI Consultora — Consolidado analítico de conversaciones, rendimiento operativo por asesor y distribución patrimonial.</p>
    <span class="bdi-badge">Último chat en la base: {ultimo_dato_txt}</span>
    <span class="bdi-badge">Analizando: {periodos_txt}</span>
    <span class="bdi-badge">Conexiones: {' + '.join(conexiones_sel) if conexiones_sel else 'todas'}</span>
    <span class="bdi-badge">Tablero generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

total_conv = df[COL_ID].nunique()
contactos_unicos = df['contactNumber'].nunique()
ratio_chats_contacto = total_conv / contactos_unicos if contactos_unicos else np.nan

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Chats", f"{total_conv:,}")
kpi2.metric("Contactos Únicos", f"{contactos_unicos:,}")
kpi3.metric("Nuevos Contactos", f"{int(df['isNewContact'].sum()):,}")
kpi4.metric("FRT Mediano", f"{df['FRT_min'].median():.1f} min" if df['FRT_min'].notna().any() else "s/d",
            help=f"Minutos de jornada laboral ({HORARIO_TXT} hs) hasta la primera respuesta. "
                 "Un chat que entra a las 20:00 empieza a contar a las 9:30 del día hábil siguiente.")
kpi5.metric("Cierre Inactividad", f"{int(df['resolvedByInactivity'].sum()):,}")

kpi6, kpi7, kpi8, kpi9, kpi10 = st.columns(5)
kpi6.metric("Chats por Contacto", f"{ratio_chats_contacto:.2f}" if pd.notna(ratio_chats_contacto) else "s/d",
            help="Conversaciones totales dividido contactos únicos.")
kpi7.metric("Resolución Mediana", f"{df['res_time_wh_min'].median():.0f} min" if df['res_time_wh_min'].notna().any() else "s/d",
            help=f"Minutos de jornada ({HORARIO_TXT} hs) hasta el cierre. Se usa mediana porque unos pocos chats de varios días distorsionan el promedio.")
kpi8.metric("Iniciados por Cliente", f"{df['startedByContact'].mean()*100:.0f}%" if len(df) else "s/d",
            help="Porcentaje de conversaciones que abrió el cliente y no el asesor.")
kpi9.metric("Resolución p90", f"{df['res_time_wh_min'].quantile(0.9):.0f} min" if df['res_time_wh_min'].notna().any() else "s/d",
            help="El 10% de conversaciones que más tardan en cerrarse demora al menos esto, en minutos de jornada.")

kpi10.metric("Conexiones Activas", f"{df['conexion'].nunique()}",
             help="Líneas de WhatsApp con al menos una conversación en la selección. El detalle está en la pestaña Conexiones.")

st.write("")

tab_pan, tab_ase, tab_car, tab_com, tab_pdf = st.tabs([
    "📊  Panorama",
    "🧑‍💼  Asesores · Capacidad y Eficiencia",
    "💼  Cartera y Clientes",
    "🎯  Comercial · Embudo de Ventas",
    "📄  Reporte PDF"
])

# ---------------------------------------------------------
# PANORAMA: volumen, horarios y comparativa de conexiones
# ---------------------------------------------------------
with tab_pan:

    section_header("VOLUMEN", "Evolución de Chats en el Tiempo")
    if df['conexion'].nunique() > 1:
        df_mes = df.groupby(['periodo', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
        fig_mes = px.bar(
            df_mes.sort_values('periodo'), x='periodo', y='Chats', text='Chats', color='conexion',
            color_discrete_map=CONEXION_COLORS, title="Evolución Mensual de Chats por Conexión",
            category_orders={'periodo': periodos_disponibles}
        )
    else:
        df_mes = df.groupby('periodo')[COL_ID].nunique().reset_index(name='Chats')
        df_mes = df_mes.sort_values('periodo')
        fig_mes = px.bar(
            df_mes, x='periodo', y='Chats', text='Chats',
            color_discrete_sequence=['#157347'], title="Evolución Mensual de Chats",
            category_orders={'periodo': periodos_disponibles}
        )
    fig_mes.update_traces(textposition='outside')
    fig_mes = apply_bdi_theme(fig_mes, legend_below=df['conexion'].nunique() > 1)
    fig_mes.update_layout(xaxis_title="Período", yaxis_title="Cantidad de Chats",
                          xaxis=dict(tickangle=-30), legend_title="Conexión", height=440,
                          margin=dict(t=70, b=95, l=70, r=50))
    grafico(fig_mes, 'Evolución mensual de chats', 'asesores')

    section_header("CARGA HORARIA", "Distribución de Consultas dentro de la Jornada")
    df_h30_base = df[(df['hora'] >= HORA_GRAF_INI) & (df['hora'] <= HORA_GRAF_FIN)]
    if df['conexion'].nunique() > 1:
        df_hora_30 = df_h30_base.groupby(['hora_30m', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
        fig_hora_30 = px.area(
            df_hora_30, x='hora_30m', y='Chats', color='conexion', markers=True,
            color_discrete_map=CONEXION_COLORS,
            title=f"Carga Horaria en Jornada Laboral ({HORARIO_TXT} hs · apilado por conexión)"
        )
        fig_hora_30.update_traces(marker=dict(size=5))
        fig_hora_30 = apply_bdi_theme(fig_hora_30, legend_below=True)
    else:
        df_hora_30 = df_h30_base.groupby('hora_30m')[COL_ID].nunique().reset_index(name='Chats')
        fig_hora_30 = px.area(
            df_hora_30, x='hora_30m', y='Chats', markers=True,
            color_discrete_sequence=['#157347'], title=f"Carga Horaria en Jornada Laboral ({HORARIO_TXT} hs · intervalos de 30 min)"
        )
        fig_hora_30.update_traces(marker=dict(size=8, color='#0F5132'),
                                  fillcolor='rgba(21,115,71,0.15)', line=dict(color='#0F5132'))
        fig_hora_30 = apply_bdi_theme(fig_hora_30)
    fig_hora_30.update_layout(xaxis_title="Franja horaria", yaxis_title="Cantidad de Chats", xaxis=dict(tickangle=-45))
    grafico(fig_hora_30, 'Carga horaria dentro de la jornada', 'asesores')


    divider()

    section_header("SATURACIÓN", "Picos de Actividad por Día y Hora")
    st.caption(f"Excluye fines de semana · Jornada laboral ({HORARIO_TXT} hs) · La intensidad del verde indica "
               "el volumen absoluto; el porcentaje, el peso de esa franja dentro del día.")

    df_heatmap = df[(df['hora'] >= HORA_GRAF_INI) & (df['hora'] <= HORA_GRAF_FIN) &
                    (~df['dia_semana'].isin(['Sábado', 'Domingo']))]

    if not df_heatmap.empty:
        heatmap_counts = df_heatmap.groupby(['dia_semana', 'hora'])[COL_ID].nunique().reset_index(name='Chats')
        totals_per_day = heatmap_counts.groupby('dia_semana')['Chats'].transform('sum')
        heatmap_counts['Porcentaje'] = (heatmap_counts['Chats'] / totals_per_day * 100).round(1)

        horas = list(range(HORA_GRAF_INI, HORA_GRAF_FIN + 1))
        heatmap_data = (heatmap_counts.pivot(index='dia_semana', columns='hora', values='Chats')
                        .reindex(index=DAY_ORDER_LABORAL, columns=horas).fillna(0))
        heatmap_pct = (heatmap_counts.pivot(index='dia_semana', columns='hora', values='Porcentaje')
                       .reindex(index=DAY_ORDER_LABORAL, columns=horas).fillna(0))

        z = heatmap_data.values
        zmax = z.max() if z.max() > 0 else 1
        etiquetas_x = [f"{h:02d}h" for h in horas]

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=z,
            x=etiquetas_x,
            y=list(heatmap_data.index),
            customdata=heatmap_pct.values,
            colorscale=BDI_HEATSCALE,
            xgap=4, ygap=4,
            colorbar=dict(
                title=dict(text="Chats", font=dict(color='#0F5132', size=12)),
                thickness=12, len=0.75, outlinewidth=0, tickfont=dict(color='#4A5D57', size=11),
                ticks="outside", ticklen=4, tickcolor='#DDE5E1'
            ),
            hovertemplate="<b>%{y} · %{x}</b><br>Conversaciones: %{z}<br>Peso del día: %{customdata:.1f}%<extra></extra>",
            zmin=0, zmax=zmax
        ))

        annotations = []
        for i, day in enumerate(heatmap_data.index):
            for j, hour in enumerate(horas):
                val = z[i][j]
                if val == 0:
                    continue
                pct = heatmap_pct.values[i][j]
                intensity = val / zmax
                text_color = '#FFFFFF' if intensity > 0.60 else '#14382A'
                annotations.append(dict(
                    x=etiquetas_x[j], y=day,
                    text=f"<b>{int(val)}</b><br><span style='font-size:9px;opacity:0.85'>{pct:.0f}%</span>",
                    showarrow=False,
                    font=dict(color=text_color, size=12, family='Inter, Segoe UI, sans-serif'),
                    align="center"
                ))

        fig_heatmap.update_layout(annotations=annotations)
        fig_heatmap = apply_bdi_theme(fig_heatmap)
        fig_heatmap.update_xaxes(title="Hora del día", side="top", showgrid=False,
                                 tickfont=dict(color='#0F5132', size=12), ticks="")
        fig_heatmap.update_yaxes(title="", showgrid=False, autorange="reversed",
                                 tickfont=dict(color='#0F5132', size=13), ticks="")
        fig_heatmap.update_layout(
            title=dict(text="Distribución de Carga de Trabajo (Horario Comercial)",
                       font=dict(color='#0F5132', size=17), x=0.01),
            height=430,
            plot_bgcolor='#FBFDFC',
            margin=dict(t=90, b=30, l=110, r=40)
        )
        grafico(fig_heatmap, 'Mapa de calor: día y hora', 'asesores')

        pico = heatmap_counts.loc[heatmap_counts['Chats'].idxmax()]
        st.caption(f"🔥 **Pico de demanda:** {pico['dia_semana']} a las {int(pico['hora']):02d}:00 hs "
                   f"con {int(pico['Chats'])} conversaciones ({pico['Porcentaje']:.0f}% del día).")
    else:
        st.info("No hay chats registrados en jornada laboral para la selección actual.")

# ---------------------------------------------------------
# TAB CONEXIONES: COMPARATIVA ENTRE LÍNEAS DE WHATSAPP
# ---------------------------------------------------------


    res_con = resumen_por_conexion(df)

    if len(res_con) < 2:
        unica = res_con.iloc[0]['Conexión'] if not res_con.empty else "—"
        st.info(f"La selección actual solo incluye la conexión **{unica}**. "
                "Ampliá el filtro de conexiones o de períodos para comparar líneas entre sí.")

    section_header("PANORAMA", "Rendimiento por Línea de WhatsApp",
                   subtitle="Cada línea se mide sobre sus propios días activos: una conexión que arrancó "
                            "a mitad de mes no es comparable en volumen bruto.")

    for _, fila in res_con.iterrows():
        color = CONEXION_COLORS.get(fila['Conexión'], '#157347')
        st.markdown(
            f"<div style='border-left:5px solid {color};background:#FFFFFF;border:1px solid #E5EBE8;"
            f"border-radius:12px;padding:10px 16px;margin-bottom:10px;'>"
            f"<b style='color:{color};font-size:1.05rem'>{fila['Conexión']}</b>"
            f"<span style='color:#5B6E67;font-size:0.85rem'> · activa del "
            f"{fila['Desde'].strftime('%d/%m/%Y')} al {fila['Hasta'].strftime('%d/%m/%Y')} "
            f"({int(fila['Días Hábiles'])} días hábiles)</span></div>",
            unsafe_allow_html=True
        )
        c = st.columns(6)
        c[0].metric("Conversaciones", f"{int(fila['Conversaciones']):,}")
        c[1].metric("Chats / Día", f"{fila['Chats/Día']:.1f}")
        c[2].metric("Contactos", f"{int(fila['Contactos']):,}")
        c[3].metric("% Nuevos", f"{fila['% Nuevos']:.1f}%")
        c[4].metric("FRT Mediano", f"{fila['FRT Mediano']:.0f} min" if pd.notna(fila['FRT Mediano']) else "s/d")
        c[5].metric("Resolución Mediana", f"{fila['Resolución Mediana']:.0f} min"
                    if pd.notna(fila['Resolución Mediana']) else "s/d")
        st.write("")

    # Lectura automática: compara la línea principal contra el resto.
    if len(res_con) >= 2:
        principal = res_con.iloc[0]
        lecturas = []
        for _, otra in res_con.iloc[1:].iterrows():
            if pd.notna(otra['% Nuevos']) and pd.notna(principal['% Nuevos']) and principal['% Nuevos'] > 0:
                veces = otra['% Nuevos'] / principal['% Nuevos']
                if veces >= 1.5:
                    lecturas.append(
                        f"**{otra['Conexión']}** trae **{otra['% Nuevos']:.0f}% de contactos nuevos** contra "
                        f"{principal['% Nuevos']:.0f}% de {principal['Conexión']} ({veces:.0f}× más): "
                        "funciona como puerta de entrada, no como atención de cartera.")
            if pd.notna(otra['FRT Mediano']) and pd.notna(principal['FRT Mediano']):
                if otra['FRT Mediano'] > principal['FRT Mediano'] * 1.3:
                    lecturas.append(
                        f"⚠️ **{otra['Conexión']}** responde en **{otra['FRT Mediano']:.0f} min** contra "
                        f"{principal['FRT Mediano']:.0f} min de {principal['Conexión']}. "
                        "Si es la línea que capta prospectos, ese retraso pega donde más cuesta.")
        if lecturas:
            st.info("🔎 **Lectura automática**\n\n" + "\n\n".join(f"- {l}" for l in lecturas))

    divider()

    section_header("TABLA COMPARATIVA", "Todas las Métricas Lado a Lado")
    tabla = res_con.drop(columns=['Desde', 'Hasta']).copy()
    st.dataframe(
        tabla.style.format({
            'Chats/Contacto': '{:.2f}', 'Chats/Día': '{:.1f}', '% Nuevos': '{:.1f}%',
            'FRT Mediano': '{:.1f}',
            'Resolución Mediana': '{:.0f}', '% Inicia Cliente': '{:.0f}%'
        }),
        column_config={
            "Chats/Día": st.column_config.NumberColumn(help="Conversaciones divididas los días hábiles en que ESA línea estuvo activa."),
            "% Nuevos": st.column_config.NumberColumn(help="Porcentaje de conversaciones con un contacto que escribe por primera vez."),
            "FRT Mediano": st.column_config.NumberColumn(help="Minutos hasta el primer mensaje enviado desde BDI."),
            "% Inicia Cliente": st.column_config.NumberColumn(help="Conversaciones abiertas por el cliente y no por el asesor.")
        },
        hide_index=True, **ANCHO
    )

    divider()

# ---------------------------------------------------------
# TAB CAPTACIÓN: EMBUDO DE LA LÍNEA COMERCIAL
# ---------------------------------------------------------

# ---------------------------------------------------------
# ASESORES: capacidad instalada y eficiencia por persona
# ---------------------------------------------------------
with tab_ase:

    lineas_p = list(df['conexion'].dropna().unique())
    if not lineas_p:
        st.info("No hay conexiones en la selección actual.")
    else:
        sugerida_p = detectar_linea_principal(df)
        idx_p = lineas_p.index(sugerida_p) if sugerida_p in lineas_p else 0
        linea_pri = st.selectbox(
            "Línea a analizar:", lineas_p, index=idx_p, key="sel_linea_principal",
            help="Por defecto la de mayor volumen. Todas las métricas de esta solapa son "
                 "exclusivas de esta línea: no se mezcla con ninguna otra conexión."
        )

        df_pri = df[df['conexion'] == linea_pri]

        if df_pri.empty:
            st.info(f"No hay conversaciones de **{linea_pri}** en la selección actual.")
        else:
            conv_p = df_pri[COL_ID].nunique()
            cont_p = df_pri['contactNumber'].nunique()
            dias_p = dias_habiles_efectivos(df_pri['createdAt_dt'])

            section_header("PANORAMA", f"Atención de Cartera · {linea_pri}",
                           subtitle=f"{dias_p} días hábiles · jornada {HORARIO_TXT} hs. Todo lo de esta solapa "
                                    "corresponde únicamente a esta conexión.")

            p = st.columns(6)
            p[0].metric("Conversaciones", f"{conv_p:,}")
            p[1].metric("Clientes Atendidos", f"{cont_p:,}")
            p[2].metric("Chats / Cliente", f"{conv_p/cont_p:.2f}" if cont_p else "s/d")
            p[3].metric("Chats / Día", f"{conv_p/dias_p:.1f}" if dias_p else "s/d")
            p[4].metric("FRT Mediano", f"{df_pri['FRT_min'].median():.0f} min" if df_pri['FRT_min'].notna().any() else "s/d")
            p[5].metric("FRT p90", f"{df_pri['FRT_min'].quantile(0.9):.0f} min" if df_pri['FRT_min'].notna().any() else "s/d",
                        help="El 10% de conversaciones peor atendidas esperó al menos esto.")

            p2 = st.columns(6)
            p2[0].metric("Resolución Mediana", f"{df_pri['res_time_wh_min'].median():.0f} min" if df_pri['res_time_wh_min'].notna().any() else "s/d")
            p2[1].metric("Resolución p90", f"{df_pri['res_time_wh_min'].quantile(0.9):.0f} min"
                         if df_pri['res_time_wh_min'].notna().any() else "s/d",
                         help="El 10% de conversaciones que más tarda en cerrarse.")
            p2[2].metric("Chats / Hora", f"{conv_p/dias_p/HORAS_JORNADA:.1f}" if dias_p else "s/d",
                         help=f"Promedio diario repartido en las {HORAS_JORNADA:.0f} horas de jornada.")
            p2[3].metric("Contactos Nuevos", f"{int(df_pri['isNewContact'].sum()):,}")
            p2[4].metric("% Nuevos", f"{df_pri['isNewContact'].mean()*100:.1f}%")
            p2[5].metric("Inicia el Cliente", f"{df_pri['startedByContact'].mean()*100:.0f}%")

            divider()

            section_header("ASESORES", f"Rendimiento Individual dentro de {linea_pri}",
                           subtitle="Estas cifras son solo de esta línea. El mismo asesor tiene números "
                                    "distintos en las otras conexiones.")
            mu = metricas_usuario_linea(df_pri)
            st.dataframe(
                mu[['user', 'Chats', '% de la Línea', 'Chats/Día', 'Contactos', 'Chats/Contacto',
                    'FRT_Mediano', 'FRT_p90', 'Resolucion_Mediana', 'Nuevos']].rename(columns={
                        'user': 'Asesor', 'FRT_Mediano': 'FRT Mediano (min)', 'FRT_p90': 'FRT p90 (min)',
                        'Resolucion_Mediana': 'Resolución Mediana (min)',
                        'Nuevos': 'Contactos Nuevos'
                    }).style.format({
                        '% de la Línea': '{:.1f}%', 'Chats/Día': '{:.1f}', 'Chats/Contacto': '{:.2f}',
                        'FRT Mediano (min)': '{:.1f}', 'FRT p90 (min)': '{:.0f}',
                        'Resolución Mediana (min)': '{:.0f}'
                    }),
                column_config={
                    "FRT p90 (min)": st.column_config.NumberColumn(help="La cola: el 10% peor atendido de este asesor."),
                    "Chats/Contacto": st.column_config.NumberColumn(help="Cuántas veces vuelve a escribir el mismo cliente a este asesor."),
                },
                hide_index=True, **ANCHO
            )

            fig_pu = px.bar(
                mu.sort_values('Chats'), x='Chats', y='user', orientation='h', text='Chats',
                color='user', color_discrete_map=USER_COLORS,
                title=f"Volumen por Asesor · {linea_pri}"
            )
            fig_pu.update_traces(textposition='outside', cliponaxis=False)
            fig_pu = apply_bdi_theme(fig_pu)
            fig_pu.update_layout(showlegend=False, xaxis_title="Conversaciones", yaxis_title="", height=400,
                                 margin=dict(t=70, b=55, l=110, r=90))
            grafico(fig_pu, 'Volumen por asesor', 'asesores')
            comp_p = mu.melt(id_vars='user', value_vars=['FRT_Mediano', 'FRT_p90'],
                             var_name='Métrica', value_name='Minutos')
            comp_p['Métrica'] = comp_p['Métrica'].map({'FRT_Mediano': 'Mediana', 'FRT_p90': 'p90 (la cola)'})
            fig_pf = px.bar(
                comp_p, x='Minutos', y='user', color='Métrica', orientation='h', barmode='group',
                color_discrete_map={'Mediana': '#157347', 'p90 (la cola)': '#C9A227'},
                title=f"Respuesta: Mediana vs. Cola · {linea_pri}"
            )
            fig_pf.update_traces(texttemplate='%{x:.0f}', textposition='outside', cliponaxis=False)
            fig_pf = apply_bdi_theme(fig_pf, legend_below=True)
            fig_pf.update_layout(xaxis_title="Minutos", yaxis_title="", legend_title="", height=420,
                                 margin=dict(t=70, b=90, l=110, r=90))
            grafico(fig_pf, 'Tiempo de respuesta: mediana vs cola', 'asesores')

            divider()

            divider()

            section_header("PATRIMONIO", f"Cartera de Cada Asesor · {linea_pri}",
                           subtitle="Cantidad de chats y porcentaje por segmento, dentro de la cartera de "
                                    "cada uno. Sirve para ver quién concentra patrimonio alto y quién "
                                    "atiende volumen de tickets chicos.")
            fig_pat = fig_patrimonio_por_asesor(df_pri)
            if fig_pat is not None:
                grafico(fig_pat, 'Mix patrimonial por asesor', 'asesores')
            else:
                st.info("No hay segmentos patrimoniales etiquetados en esta línea con los filtros actuales.")

            divider()

            section_header("VELOCIDAD", "Semáforo de Primera Respuesta",
                           subtitle=f"Minutos de jornada laboral ({HORARIO_TXT} hs), por conversación: en una "
                                    "línea de cartera el mismo cliente escribe muchas veces y cada consulta "
                                    "merece respuesta.")
            tr_p = df_pri['FRT_min'].apply(clasificar_tramo).value_counts().reindex(ORDEN_TRAMOS).fillna(0).reset_index()
            tr_p.columns = ['Tramo', 'Chats']
            tr_p['Pct'] = tr_p['Chats'] / conv_p * 100
            tr_p['Texto'] = tr_p.apply(lambda r: f"{int(r['Chats'])} ({r['Pct']:.0f}%)", axis=1)
            fig_trp = px.bar(
                tr_p[::-1], x='Chats', y='Tramo', orientation='h', text='Texto',
                color='Tramo', color_discrete_map=TRAMO_COLORS,
                category_orders={'Tramo': ORDEN_TRAMOS[::-1]},
                title=f"Tiempo hasta la Primera Respuesta · {linea_pri}"
            )
            fig_trp.update_traces(textposition='outside', cliponaxis=False)
            fig_trp = apply_bdi_theme(fig_trp)
            fig_trp.update_layout(showlegend=False, xaxis_title="Conversaciones", yaxis_title="",
                                  height=400, margin=dict(t=70, b=55, l=185, r=120))
            grafico(fig_trp, 'Semáforo de primera respuesta', 'asesores')

            divider()

# ---------------------------------------------------------
# TAB 2: BROKERS Y PATRIMONIO
# ---------------------------------------------------------


    section_header("EFICIENCIA", "Desempeño Operativo por Asesor")

    total_general_chats = df[COL_ID].nunique()
    base_dias = dias_habiles_efectivos(df['createdAt_dt'])

    st.caption(f"📅 **Base de cálculo:** {base_dias} días hábiles reales de los períodos seleccionados "
               f"(sin fines de semana ni feriados AR, respetando meses incompletos) · Jornada {HORARIO_TXT} hs "
               f"({HORAS_JORNADA:.0f} hs). Todos los tiempos de respuesta y resolución se miden solo dentro de esa ventana.")

    df_user_eff = df.groupby('user').agg(
        Total_Chats=(COL_ID, 'nunique'),
        FRT_Mediano_Min=('FRT_min', 'median'),
        Contactos_Nuevos=('isNewContact', 'sum')
    ).reset_index()

    df_user_eff['Participación (%)'] = (df_user_eff['Total_Chats'] / total_general_chats * 100) if total_general_chats > 0 else 0
    df_user_eff['Contactos Nuevos (%)'] = (df_user_eff['Contactos_Nuevos'] / df_user_eff['Total_Chats'] * 100)
    df_user_eff['Chats / Día'] = df_user_eff['Total_Chats'] / base_dias
    df_user_eff['Chats / Hora (8hs)'] = df_user_eff['Chats / Día'] / HORAS_JORNADA

    df_user_eff = df_user_eff.sort_values('Total_Chats', ascending=False)

    df_table_eff = df_user_eff[['user', 'Total_Chats', 'Participación (%)', 'FRT_Mediano_Min',
                                'Chats / Día', 'Chats / Hora (8hs)',
                                'Contactos_Nuevos', 'Contactos Nuevos (%)']].copy()

    df_table_eff.columns = ['Asesor', 'Total Chats', 'Participación (%)', 'FRT Mediano (Min)',
                            'Chats / Día', 'Chats / Hora (8hs)', 'Nuevos Contactos (#)', 'Nuevos Contactos (%)']

    st.markdown("##### Resumen por Asesor y Conexión")
    st.caption("⚠️ Cada fila es un asesor **dentro de una línea**. Un mismo asesor rinde distinto "
               "en cartera que en captación, y un promedio único de las dos esconde las dos cosas.")

    df_mu = metricas_usuario_por_conexion(df)
    if not df_mu.empty:
        st.dataframe(
            df_mu[['user', 'Conexión', 'Chats', '% de la Línea', 'Chats/Día', 'Contactos',
                   'FRT_Mediano', 'FRT_p90', 'Resolucion_Mediana', 'Nuevos']].rename(columns={
                       'user': 'Asesor', 'FRT_Mediano': 'FRT Mediano (min)', 'FRT_p90': 'FRT p90 (min)',
                       'Resolucion_Mediana': 'Resolución Mediana (min)',
                       'Nuevos': 'Contactos Nuevos'
                   }).style.format({
                       '% de la Línea': '{:.1f}%', 'Chats/Día': '{:.1f}',
                       'FRT Mediano (min)': '{:.1f}', 'FRT p90 (min)': '{:.0f}',
                       'Resolución Mediana (min)': '{:.0f}'
                   }),
            column_config={
                "% de la Línea": st.column_config.NumberColumn(help="Peso del asesor DENTRO de esa conexión, no sobre el total general."),
                "Chats/Día": st.column_config.NumberColumn(help="Sobre los días hábiles en que esa línea estuvo activa."),
                "FRT p90 (min)": st.column_config.NumberColumn(help="La cola: el 10% de conversaciones peor atendidas."),
            },
            hide_index=True, **ANCHO
        )

    with st.expander("📊 Ver totales consolidados por asesor (todas las conexiones juntas)"):
        st.caption("Útil para carga de trabajo global. Para evaluar desempeño, usá la tabla de arriba: "
                   "los tiempos de una línea de captación y una de cartera no son comparables entre sí.")
        st.dataframe(
            df_table_eff.style.format({
                'Participación (%)': '{:.1f}%', 'FRT Mediano (Min)': '{:.1f}',
                'Chats / Día': '{:.1f}', 'Chats / Hora (8hs)': '{:.1f}',
                'Nuevos Contactos (%)': '{:.1f}%'
            }),
            hide_index=True, **ANCHO
        )

    divider()

    section_header("COMPOSICIÓN MENSUAL", "Reparto de Chats por Asesor, Mes a Mes",
                   subtitle="Cada barra es un mes completo. La altura es el volumen; los colores, quién lo atendió.")

    opciones_conx = ['Todas las conexiones'] + list(conexiones_disponibles)
    conx_comp = st.radio("Conexión a mostrar:", opciones_conx, horizontal=True, key="radio_comp_mensual",
                         help="Los asesores atienden en las dos líneas. Separarlas muestra repartos "
                              "muy distintos: la comercial la concentran pocas personas.")

    df_comp = df if conx_comp == 'Todas las conexiones' else df[df['conexion'] == conx_comp]

    if df_comp.empty:
        st.info(f"No hay conversaciones de **{conx_comp}** con los filtros actuales.")
    else:
        cobertura = st.slider(
            "Etiquetar a los asesores que cubren este % del mes:", 50, 100, 90, step=5,
            key="slider_cobertura_mes",
            help="Se etiquetan los asesores de mayor volumen hasta llegar a ese porcentaje del mes. "
                 "Los que quedan abajo siguen en la barra y en el hover, pero sin número encima, "
                 "para que no se amontonen las porciones chicas."
        )

        comp = df_comp.groupby(['periodo', 'user'])[COL_ID].nunique().reset_index(name='Chats')
        total_mes = comp.groupby('periodo')['Chats'].transform('sum')
        comp['Pct'] = comp['Chats'] / total_mes * 100

        # Dentro de cada mes se ordena por volumen y se acumula: solo llevan etiqueta los
        # primeros asesores hasta cubrir el porcentaje elegido. Además se exige un piso de
        # altura, porque una porción de 2 % no tiene lugar físico para tres líneas de texto.
        comp = comp.sort_values(['periodo', 'Chats'], ascending=[True, False])
        comp['Acumulado'] = comp.groupby('periodo')['Pct'].cumsum()
        comp['Rango'] = comp.groupby('periodo').cumcount()
        PISO_ALTURA = 4.0
        comp['Etiquetar'] = (((comp['Acumulado'] - comp['Pct'] < cobertura) | (comp['Rango'] == 0))
                             & (comp['Pct'] >= PISO_ALTURA))

        periodos_x = [p for p in periodos_disponibles if p in set(comp['periodo'])]
        # De mayor a menor volumen total: el asesor más grande queda en la base del apilado,
        # así la referencia visual no salta de un mes a otro.
        orden_asesores = (comp.groupby('user')['Chats'].sum()
                          .sort_values(ascending=False).index.tolist())

        # Se arma con go.Bar en vez de px.bar: px le pone un offsetgroup distinto a cada
        # trace y, según la versión de plotly, eso hace que las barras se dibujen una al
        # lado de la otra en vez de apiladas. Con go.Bar el apilado es determinístico.
        fig_comp = go.Figure()
        for asesor in orden_asesores:
            g = comp[comp['user'] == asesor].set_index('periodo').reindex(periodos_x)
            chats = g['Chats'].fillna(0)
            pct = g['Pct'].fillna(0)
            textos = [
                f"{asesor}<br>{int(c)} · {p:.0f}%" if bool(e) else ""
                for c, p, e in zip(chats, pct, g['Etiquetar'].fillna(False))
            ]
            fig_comp.add_bar(
                x=periodos_x, y=chats, name=asesor, text=textos,
                marker=dict(color=USER_COLORS.get(asesor), line=dict(color='#FFFFFF', width=1.5)),
                textposition='inside', insidetextanchor='middle',
                textfont=dict(color='#FFFFFF', size=14, family='Inter, Segoe UI, sans-serif'),
                textangle=0, cliponaxis=False,
                customdata=np.stack([pct.values], axis=-1),
                hovertemplate=f"<b>{asesor}</b><br>%{{x}}<br>Chats: %{{y}}"
                              "<br>Peso del mes: %{customdata[0]:.1f}%<extra></extra>"
            )

        fig_comp = apply_bdi_theme(fig_comp, legend_below=True)
        fig_comp.update_layout(
            title=dict(text=f"Chats por Asesor y Mes · {conx_comp}",
                       font=dict(color='#0F5132', size=20), x=0.01, xanchor='left'),
            barmode='stack',
            bargap=0.15,                      # barras anchas: poco aire entre meses
            xaxis_title="Período", yaxis_title="Conversaciones", legend_title="Asesor",
            height=720, xaxis=dict(tickangle=-25, tickfont=dict(size=14)),
            uniformtext=dict(minsize=12, mode='hide'),  # si no entra, se oculta: nunca se solapa
            margin=dict(t=80, b=130, l=90, r=60)
        )
        grafico(fig_comp, 'Composición mensual por asesor', 'asesores')

        etiquetar = comp['Etiquetar']
        sin_etiqueta = int((~etiquetar).sum())
        if sin_etiqueta:
            st.caption(f"Quedaron {sin_etiqueta} porciones sin texto: o caen en la cola del "
                       f"{100 - cobertura}% de su mes, o pesan menos del {PISO_ALTURA:.0f}% y no hay "
                       "lugar físico para escribir adentro. Siguen contando en la barra y el detalle "
                       "aparece al pasar el cursor.")

    divider()

# ---------------------------------------------------------
# TAB 5: FRICCIÓN Y COMPLEJIDAD
# ---------------------------------------------------------

# ---------------------------------------------------------
# CARTERA Y CLIENTES: brokers, patrimonio, servicios y fricción
# ---------------------------------------------------------
with tab_car:

    df_exp = df.explode('brokers')
    df_exp['brokers'] = df_exp['brokers'].fillna('Sin Broker')

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
        fig_broker_usr.update_traces(textinfo='percent', textposition='inside', textfont=dict(size=16))
        fig_broker_usr = apply_bdi_theme(fig_broker_usr, legend_below=True)
        fig_broker_usr.update_layout(margin=dict(t=60, b=80, l=40, r=40))
        grafico(fig_broker_usr, 'Personas únicas por broker', 'asesores')

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
        fig_tier_usr.update_traces(textinfo='percent', textposition='inside', textfont=dict(size=16))
        fig_tier_usr = apply_bdi_theme(fig_tier_usr, legend_below=True)
        fig_tier_usr.update_layout(margin=dict(t=60, b=80, l=40, r=40))
        grafico(fig_tier_usr, 'Personas únicas por segmento patrimonial', 'asesores')

    divider()

    section_header("SERVICIOS", "Etiquetas Comerciales",
                   subtitle="Membresía, Agro, Consultoría y demás etiquetas del CRM que no son broker ni segmento.")
    df_serv = df.explode('servicios').dropna(subset=['servicios'])
    if not df_serv.empty:
        serv_users = df_serv.drop_duplicates(subset=['contactNumber', 'servicios'])
        serv_u = serv_users.groupby('servicios')['contactNumber'].nunique().reset_index(name='Contactos')
        fig_serv_u = px.bar(
            serv_u.sort_values('Contactos'), x='Contactos', y='servicios', orientation='h', text='Contactos',
            color='servicios', color_discrete_map=SERVICIO_COLORS,
            title="Contactos Únicos por Servicio"
        )
        fig_serv_u.update_traces(textposition='outside', cliponaxis=False)
        fig_serv_u = apply_bdi_theme(fig_serv_u)
        fig_serv_u.update_layout(showlegend=False, xaxis_title="Contactos únicos", yaxis_title="")
        grafico(fig_serv_u, 'Contactos únicos por servicio', 'asesores')
    else:
        st.info("No hay etiquetas de servicio en la selección actual.")

    divider()

    section_header("COMPOSICIÓN CRUZADA", "Brokers vs. Segmentos Patrimoniales")
    df_tier_broker = df_exp[df_exp['tier'] != 'Sin Etiqueta Monto'].groupby(['brokers', 'tier']).size().reset_index(name='Chats')
    totals = df_tier_broker.groupby('brokers')['Chats'].transform('sum')
    df_tier_broker['Porcentaje'] = (df_tier_broker['Chats'] / totals * 100).round(1)
    df_tier_broker['Texto'] = df_tier_broker['Chats'].astype(str) + " (" + df_tier_broker['Porcentaje'].astype(str) + "%)"

    fig_tier_broker = px.bar(
        df_tier_broker, x='Chats', y='brokers', color='tier',
        barmode='group', orientation='h', text='Texto',
        category_orders={'tier': TIERS}, color_discrete_map=TIER_COLORS,
        title="Volumen de Consultas Patrimoniales por Broker"
    )
    fig_tier_broker.update_traces(textposition='outside', cliponaxis=False)
    fig_tier_broker = apply_bdi_theme(fig_tier_broker, legend_below=True)
    fig_tier_broker.update_layout(
        xaxis_title="Cantidad de Chats", yaxis_title="Broker", legend_title="Segmento (USD)",
        height=820, margin=dict(t=70, b=95, l=110, r=110)
    )
    grafico(fig_tier_broker, 'Brokers vs segmentos patrimoniales', 'asesores')

# ---------------------------------------------------------
# TAB 3: CLIENTES
# ---------------------------------------------------------


    section_header("RANKING", "Top 10 Clientes con Mayor Interacción")
    df_clients_all = df.groupby(['contactName', 'contactNumber']).agg(
        Total_Chats=(COL_ID, 'nunique'),
        Asesor_Habitual=('user', lambda x: x.mode()[0] if not x.mode().empty else ''),
        Segmento_Monto=('tier', lambda x: x.mode()[0] if not x.mode().empty else '')
    ).reset_index()

    df_top10 = df_clients_all.sort_values('Total_Chats', ascending=False).head(10).sort_values('Total_Chats', ascending=True)

    fig_top10 = px.bar(
        df_top10, x='Total_Chats', y='contactName', orientation='h', text='Total_Chats',
        color='Asesor_Habitual', color_discrete_map=USER_COLORS,
        title="Top 10 Clientes (Color = Asesor Principal)"
    )
    fig_top10.update_traces(textposition='outside', cliponaxis=False)
    fig_top10 = apply_bdi_theme(fig_top10, legend_below=True)
    fig_top10.update_layout(height=640, xaxis_title="Conversaciones", yaxis_title="",
                            margin=dict(t=70, b=95, l=230, r=90))
    grafico(fig_top10, 'Top 10 clientes', 'asesores')

    divider()

    section_header("BASE DE CLIENTES", "Listado Completo e Interactivo")

    df_pareto = df_clients_all.sort_values('Total_Chats', ascending=False)
    total_chats_pareto = df_pareto['Total_Chats'].sum()
    if total_chats_pareto > 0:
        df_pareto['CumSum'] = df_pareto['Total_Chats'].cumsum()
        df_pareto['CumPct'] = df_pareto['CumSum'] / total_chats_pareto
        pareto_80_idx = df_pareto[df_pareto['CumPct'] <= 0.8].shape[0]
        if pareto_80_idx == 0: pareto_80_idx = 1
        pareto_client_pct = (pareto_80_idx / len(df_pareto)) * 100
        st.info(f"💡 **Concentración de la Demanda (Ley de Pareto):** El **{pareto_client_pct:.1f}%** de los clientes ({pareto_80_idx} de {len(df_pareto)}) genera el 80% del volumen total de chats.")

    search_query = st.text_input("🔍 Buscador de clientes (nombre o número telefónico):", "")
    df_filtered_clients = df_clients_all.copy().sort_values('Total_Chats', ascending=False)

    if search_query:
        mask = (
            df_filtered_clients['contactName'].astype(str).str.contains(search_query, case=False, na=False, regex=False) |
            df_filtered_clients['contactNumber'].astype(str).str.contains(search_query, case=False, na=False, regex=False)
        )
        df_filtered_clients = df_filtered_clients[mask]

    st.caption(f"Mostrando **{len(df_filtered_clients):,}** clientes registrados.")
    st.dataframe(
        df_filtered_clients.rename(columns={
            'contactName': 'Nombre del Cliente', 'contactNumber': 'Número de Teléfono',
            'Total_Chats': 'Total Chats', 'Asesor_Habitual': 'Asesor Principal', 'Segmento_Monto': 'Segmento Patrimonial'
        }),
        hide_index=True, **ANCHO, height=420
    )

# ---------------------------------------------------------
# TAB 4: ACTIVIDAD POR USUARIO Y EFICIENCIA OPERATIVA
# ---------------------------------------------------------


    df_exp_5 = df.explode('brokers')
    df_exp_5['brokers'] = df_exp_5['brokers'].fillna('Sin Broker')

    section_header("RESUMEN EJECUTIVO", "Fricción y Complejidad de un Vistazo")
    contactos_unicos_5 = df['contactNumber'].nunique()
    ratio_global = (df[COL_ID].nunique() / contactos_unicos_5) if contactos_unicos_5 > 0 else np.nan
    res_time_med = df['res_time_wh_min'].median()

    df_brk_ratio_kpi = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers').agg(
        Chats=(COL_ID, 'nunique'), Usuarios=('contactNumber', 'nunique')
    )
    df_brk_ratio_kpi['Ratio'] = df_brk_ratio_kpi['Chats'] / df_brk_ratio_kpi['Usuarios']
    broker_mas_dependiente = df_brk_ratio_kpi['Ratio'].idxmax() if not df_brk_ratio_kpi.empty else "—"

    df_tier_frt_kpi = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median().dropna()
    segmento_mas_lento = df_tier_frt_kpi.idxmax() if not df_tier_frt_kpi.empty else "—"

    kf1, kf2, kf3, kf4 = st.columns(4)
    kf1.metric("Ratio Global de Fricción", f"{ratio_global:.2f} chats/cliente" if pd.notna(ratio_global) else "s/d", help="Promedio de chats por cliente único.")
    kf2.metric("Resolución Mediana", f"{res_time_med:.0f} min" if pd.notna(res_time_med) else "s/d", help="Mediana del tiempo de resolución en horario laboral. La mediana evita que unos pocos chats de varios días distorsionen el número.")
    kf3.metric("Broker Más Dependiente", broker_mas_dependiente, help="Broker con mayor promedio de consultas por cliente.")
    kf4.metric("Segmento Más Lento (FRT)", segmento_mas_lento, help="Segmento patrimonial con la mediana de respuesta inicial más lenta.")

    divider()

    section_header(
        "FRICCIÓN", "Índice de Independencia del Cliente",
        subtitle="Cuántas veces nos vuelve a escribir un mismo cliente único. Un ratio menor indica mayor autonomía."
    )

    df_fric_broker = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers').agg(
        Chats=(COL_ID, 'nunique'), Usuarios=('contactNumber', 'nunique')
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
    fig_fric_b.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Broker",
                             showlegend=False, height=420, margin=dict(t=70, b=55, l=110, r=120))
    grafico(fig_fric_b, 'Chats por cliente, por broker', 'asesores')

    divider()

    section_header(
        "COMPLEJIDAD OPERATIVA", "Análisis de Tiempos de Atención (SLA)",
        subtitle="Cruza tiempos de resolución y de primera respuesta con plataformas y patrimonio."
    )

    df_comp_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median().reset_index()

    fig_comp_t = px.bar(
        df_comp_tier, x='FRT_min', y='tier', orientation='h', text='FRT_min',
        color='tier', color_discrete_map=TIER_COLORS, category_orders={'tier': TIERS},
        title="SLA de Facto: FRT Mediano por Patrimonio"
    )
    fig_comp_t.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
    fig_comp_t = add_reference_line(fig_comp_t, df_comp_tier['FRT_min'].mean(), orientation='v')
    fig_comp_t = apply_bdi_theme(fig_comp_t)
    fig_comp_t.update_layout(xaxis_title="Minutos (Mediana)", yaxis_title="Segmento Patrimonial",
                             showlegend=False, height=460, margin=dict(t=70, b=55, l=170, r=120))
    grafico(fig_comp_t, 'SLA de facto por segmento patrimonial', 'asesores')

    st.caption("🟡 La línea punteada dorada marca el promedio del grupo. Los tiempos usan **mediana**: "
               "unas pocas conversaciones que quedan abiertas varios días vuelven engañoso el promedio simple.")

# ---------------------------------------------------------
# COMERCIAL: embudo de ventas
# ---------------------------------------------------------
with tab_com:

    lineas = list(df['conexion'].dropna().unique())
    if not lineas:
        st.info("No hay conexiones en la selección actual.")
    else:
        sugerida = detectar_linea_captacion(df)
        idx = lineas.index(sugerida) if sugerida in lineas else 0
        linea_cap = st.selectbox(
            "Línea de captación a analizar:", lineas, index=idx,
            help="Por defecto se propone la línea con mayor proporción de contactos nuevos. "
                 "Si mañana sumás otra línea comercial, aparece acá sola."
        )

        df_cap = df[df['conexion'] == linea_cap]
        leads = analizar_captacion(df_cap, df_raw, linea_cap)

        if leads.empty:
            st.info(f"No hay conversaciones de **{linea_cap}** en la selección actual.")
        else:
            # ---- Base del embudo: TODOS los contactos únicos que escribieron al comercial.
            # Un solo filtro antes de medir conversión: quién es lead y quién no.
            # «No califica», «En proceso» y los sin etiquetar NO son escalones del embudo:
            # son las tres formas distintas de no haber cerrado todavía, y se abren abajo
            # en la barra de conciliación. Meterlas como escalón mezcla un descarte
            # definitivo con una conversación que sigue abierta.
            total_leads = len(leads)
            es_cliente = ((leads['Desenlace'] == DES_CLIENTE) | (leads['Estado'] == 'Ya era cliente'))

            n_cliente = int(es_cliente.sum())
            nuevos = leads[~es_cliente]
            n_leads = len(nuevos)

            n_membresia = int((nuevos['Desenlace'] == DES_MEMBRESIA).sum())
            n_consultoria = int((nuevos['Desenlace'] == DES_CONSULTORIA).sum())
            n_derivado = int((nuevos['Desenlace'] == DES_DERIVADO).sum())
            no_califica = int((nuevos['Desenlace'] == DES_NO_CALIFICA).sum())
            en_proceso = int((nuevos['Desenlace'] == DES_EN_PROCESO).sum())
            sin_definir = int((nuevos['Desenlace'] == DES_SIN_DEFINIR).sum())
            n_ganados = n_membresia + n_consultoria + n_derivado
            conversion = n_ganados / n_leads * 100 if n_leads else np.nan
            horas_der = nuevos.loc[nuevos['Desenlace'] == DES_DERIVADO, 'Horas a Derivación'].median()

            section_header("EMBUDO", f"Del Primer Mensaje a la Venta · {linea_cap}",
                           subtitle="La unidad es el contacto único, no la conversación. Un solo filtro: "
                                    "quién es lead y quién ya era cliente. El último escalón se abre en "
                                    "las tres formas de ganarlo.")

            # ---- Embudo centrado de tres niveles.
            # Cada fila es una barra apilada con un espaciador transparente a la izquierda,
            # de ancho (máximo − total de la fila) / 2. Eso la centra y produce la silueta
            # de embudo sin salir de go.Bar, que permite segmentar el último nivel.
            etiquetas_y = ['3 · Leads ganados', '2 · Leads reales', '1 · Escribieron al comercial']
            anchos = [n_ganados, n_leads, total_leads]
            ancho_max = max(total_leads, 1)

            def _pct(v, base):
                return f"{v / base * 100:.0f}%" if base else "s/d"

            espaciador = [(ancho_max - a) / 2 for a in anchos]
            fig_emb = go.Figure()
            fig_emb.add_bar(y=etiquetas_y, x=espaciador, orientation='h',
                            marker=dict(color='rgba(0,0,0,0)'), showlegend=False,
                            hoverinfo='skip', name='')
            fig_emb.add_bar(
                y=etiquetas_y, x=[0, n_leads, total_leads], orientation='h',
                marker=dict(color=['rgba(0,0,0,0)', COLOR_ETAPA_2, COLOR_ETAPA_1],
                            line=dict(color='#FFFFFF', width=2)),
                text=['',
                      f"{n_leads} leads reales · {_pct(n_leads, total_leads)} de los que escribieron",
                      f"{total_leads} contactos únicos"],
                textposition='inside', insidetextanchor='middle',
                textfont=dict(color='#FFFFFF', size=17, family='Inter, Segoe UI, sans-serif'),
                showlegend=False, name='Etapa',
                hovertemplate="%{y}<br>%{x} contactos<extra></extra>"
            )
            for etiqueta, valor in [(DES_MEMBRESIA, n_membresia),
                                    (DES_CONSULTORIA, n_consultoria),
                                    (DES_DERIVADO, n_derivado)]:
                corto = etiqueta.split(' - ')[0].split(' a ')[0]
                fig_emb.add_bar(
                    y=etiquetas_y, x=[valor, 0, 0], orientation='h', name=etiqueta,
                    marker=dict(color=DESENLACE_COLORS[etiqueta], line=dict(color='#FFFFFF', width=2)),
                    text=[f"{corto}<br>{valor} · {_pct(valor, n_leads)}" if valor else '', '', ''],
                    textposition='inside', insidetextanchor='middle',
                    textfont=dict(color='#FFFFFF', size=15, family='Inter, Segoe UI, sans-serif'),
                    hovertemplate=f"<b>{etiqueta}</b><br>%{{x}} leads<extra></extra>"
                )

            fig_emb = apply_bdi_theme(fig_emb, legend_below=True)
            fig_emb.update_layout(
                title=dict(text=f"Embudo Comercial · {linea_cap}",
                           font=dict(color='#0F5132', size=20), x=0.01, xanchor='left'),
                barmode='stack', bargap=0.30,
                xaxis=dict(visible=False, range=[0, ancho_max * 1.02]),
                yaxis=dict(tickfont=dict(color='#0F5132', size=16), showgrid=False,
                           categoryorder='array', categoryarray=etiquetas_y),
                legend_title="Cómo se ganó",
                uniformtext=dict(minsize=12, mode='hide'),
                height=440, margin=dict(t=80, b=110, l=250, r=200)
            )
            pendientes = n_leads - n_ganados
            # Las anotaciones van FUERA del área del gráfico (xref paper), con margen
            # derecho reservado: antes se escribían en coordenadas de dato y el texto
            # quedaba cortado contra el borde.
            for fila, cantidad, texto, color in [
                ('2 · Leads reales', n_cliente, 'ya eran clientes', '#8A6D00'),
                ('3 · Leads ganados', pendientes, 'sin cerrar todavía', '#7A867F')]:
                if cantidad:
                    fig_emb.add_annotation(
                        xref='paper', x=1.015, y=fila, xanchor='left', yanchor='middle',
                        text=f"<b>−{cantidad}</b><br><span style='font-size:12px'>{texto}</span>",
                        showarrow=False, align='left', font=dict(color=color, size=15))
            grafico(fig_emb, 'Embudo comercial', 'comercial')

            k = st.columns(5)
            k[0].metric("Escribieron", f"{total_leads:,}",
                        help="Contactos únicos que escribieron al número comercial.")
            k[1].metric("Leads Reales", f"{n_leads:,}",
                        delta=f"−{n_cliente} ya eran clientes", delta_color="off",
                        help="Lo que queda tras descontar a quienes ya tenían membresía o consultoría, "
                             "o ya conversaban con la mesa de asesores.")
            k[2].metric("Leads Ganados", f"{n_ganados:,}",
                        help="Membresía + consultoría + derivados a un asesor.")
            k[3].metric("Tasa de Conversión", f"{conversion:.1f}%" if pd.notna(conversion) else "s/d",
                        help="Ganados sobre leads reales. Es un piso mientras queden leads sin definir.")
            k[4].metric("Sin Cerrar", f"{pendientes:,}",
                        delta=f"{pendientes/n_leads*100:.0f}% de los leads" if n_leads else None,
                        delta_color="off",
                        help="El hueco entre leads reales y ganados. Abajo se abre en sus tres causas.")

            k2 = st.columns(5)
            k2[0].metric("Membresías", f"{n_membresia:,}", help="Etiqueta «Membresia - Comercial».")
            k2[1].metric("Consultorías", f"{n_consultoria:,}", help="Etiqueta «Consultoria - Comercial».")
            k2[2].metric("Derivados", f"{n_derivado:,}",
                         delta=f"{horas_der:.0f} hs hasta derivar" if pd.notna(horas_der) else None,
                         delta_color="off",
                         help="Etiqueta de derivación, o el contacto aparece después conversando con un asesor.")
            k2[3].metric("No Califica", f"{no_califica:,}",
                         delta=f"{no_califica/n_leads*100:.1f}% de los leads" if n_leads else None,
                         delta_color="off",
                         help="Decidido que no: mostraron interés pero no llegan a los mínimos.")
            k2[4].metric("FRT p90", f"{nuevos['FRT_min'].quantile(0.9):.0f} min" if nuevos['FRT_min'].notna().any() else "s/d",
                         help="El 10% peor atendido de los leads espera al menos esto, en minutos de jornada laboral.")

            # ---- Conciliación: los leads reales desglosados al 100%.
            # Es la auditoría del embudo. Si todo está etiquetado, "Sin definir" debe
            # quedar en cero y las otras cinco tienen que sumar exactamente los leads reales.
            section_header("CONCILIACIÓN", f"Los {n_leads} Leads Reales, Categoría por Categoría",
                           subtitle="El hueco entre leads y ganados no es una sola cosa: «No aplica» es un "
                                    "descarte decidido, «En proceso» es una charla abierta y «Sin definir» "
                                    "es un desenlace que nadie registró. Solo el tercero es un problema.")

            categorias = [(DES_MEMBRESIA, n_membresia), (DES_CONSULTORIA, n_consultoria),
                          (DES_DERIVADO, n_derivado), (DES_NO_CALIFICA, no_califica),
                          (DES_EN_PROCESO, en_proceso), (DES_SIN_DEFINIR, sin_definir)]
            fig_con = go.Figure()
            for etiqueta, valor in categorias:
                if not valor:
                    continue
                pct = valor / n_leads * 100 if n_leads else 0
                fig_con.add_bar(
                    y=['Leads reales'], x=[valor], orientation='h', name=etiqueta,
                    marker=dict(color=DESENLACE_COLORS[etiqueta], line=dict(color='#FFFFFF', width=2)),
                    text=[f"{valor}<br>{pct:.0f}%"], textposition='inside', insidetextanchor='middle',
                    textfont=dict(color='#FFFFFF' if etiqueta != DES_SIN_DEFINIR else '#14382A', size=15),
                    hovertemplate=f"<b>{etiqueta}</b><br>%{{x}} leads ({pct:.1f}%)<extra></extra>"
                )
            fig_con = apply_bdi_theme(fig_con, legend_below=True)
            fig_con.update_layout(
                title=dict(text="Desglose Completo de los Leads Reales",
                           font=dict(color='#0F5132', size=20), x=0.01, xanchor='left'),
                barmode='stack', bargap=0.6,
                xaxis=dict(visible=False, range=[0, max(n_leads, 1) * 1.01]),
                yaxis=dict(showticklabels=False, showgrid=False),
                legend_title="Desenlace", uniformtext=dict(minsize=12, mode='hide'),
                height=300, margin=dict(t=80, b=120, l=40, r=40)
            )
            grafico(fig_con, 'Conciliación de leads reales', 'comercial')

            if sin_definir == 0 and n_leads:
                st.success(f"Los {n_leads} leads del período están todos etiquetados: "
                           f"{n_ganados} ganados, {no_califica} no aplican y {en_proceso} en proceso. "
                           "La conversión que muestra el embudo es el número real, no un piso.", icon="✅")

            # Los clientes existentes ya aparecen como escalón del embudo; acá solo se
            # desglosa por qué quedaron fuera y si alguno igual terminó comprando.
            con_tag = int((leads['Desenlace'] == DES_CLIENTE).sum())
            solo_historial = n_cliente - con_tag
            if n_cliente:
                detalle_cli = []
                if con_tag:
                    detalle_cli.append(f"{con_tag} con etiqueta de membresía o consultoría vigente")
                if solo_historial:
                    detalle_cli.append(f"{solo_historial} que ya conversaban con la mesa de asesores")
                st.caption(f"ℹ️ Los **{n_cliente} contactos que ya eran clientes** se descuentan en el "
                           f"escalón 2: {' y '.join(detalle_cli)}. No son captación, pero miden cuánta "
                           "carga de consulta absorbe el número comercial "
                           f"({n_cliente/total_leads*100:.0f}% de todo lo que entra).")

            ganados_clientes = int(leads.loc[es_cliente, 'Desenlace'].isin(DESENLACES_GANADOS).sum())
            if ganados_clientes:
                st.caption(f"💰 De esos clientes existentes, **{ganados_clientes} terminaron comprando** "
                           "por este número. Es upsell, no captación de leads nuevos, así que no entra "
                           "en la tasa de conversión — pero la venta se hizo acá.")

            if n_ganados == 0 and n_leads:
                st.info("Todavía no hay ningún lead con las etiquetas **«Membresia - Comercial»** o "
                        "**«Consultoria - Comercial»**. El tablero ya las reconoce: en cuanto se carguen "
                        "en Whaticket, el embudo se llena solo, sin tocar el código.", icon="🏷️")

            divider()

            section_header("VELOCIDAD", "Cuánto Tarda en Contestarse un Lead",
                           subtitle=f"Minutos de jornada laboral ({HORARIO_TXT} hs). En captación lo que "
                                    "define el resultado es la cola, no el promedio.")
            col_v1, col_v2 = st.columns([3, 2])
            with col_v1:
                tramos = (nuevos['Tramo'].value_counts()
                          .reindex(ORDEN_TRAMOS).fillna(0).reset_index())
                tramos.columns = ['Tramo', 'Leads']
                tramos['Pct'] = tramos['Leads'] / n_leads * 100
                tramos['Texto'] = tramos.apply(lambda r: f"{int(r['Leads'])} ({r['Pct']:.0f}%)", axis=1)
                fig_tr = px.bar(
                    tramos[::-1], x='Leads', y='Tramo', orientation='h', text='Texto',
                    color='Tramo', color_discrete_map=TRAMO_COLORS,
                    category_orders={'Tramo': ORDEN_TRAMOS[::-1]},
                    title="Semáforo de Primera Respuesta"
                )
                fig_tr.update_traces(textposition='outside', cliponaxis=False)
                fig_tr = apply_bdi_theme(fig_tr)
                fig_tr.update_layout(showlegend=False, xaxis_title="Leads", yaxis_title="",
                                     height=400, margin=dict(t=70, b=55, l=185, r=110))
                grafico(fig_tr, 'Semáforo de primera respuesta a leads', 'comercial')
            with col_v2:
                dentro = nuevos[~nuevos['fuera_horario']]['FRT_min'].median()
                fuera = nuevos[nuevos['fuera_horario']]['FRT_min'].median()
                n_fuera = int(nuevos['fuera_horario'].sum())
                st.markdown("##### Dentro vs. fuera de horario")
                real_med = nuevos['FRT_real'].median()
                st.metric("Espera real del lead (reloj de pared)",
                          f"{real_med/60:.1f} hs" if pd.notna(real_med) else "s/d",
                          help="Tiempo calendario que el lead percibe, sin descontar noches ni fines de "
                               "semana. Las demás métricas usan minutos de jornada laboral.")
                st.metric("Leads fuera de horario", f"{n_fuera:,}",
                          help=f"Entraron fuera de la jornada de {HORARIO_TXT} hs, o un fin de semana o feriado.")
                st.metric("FRT mediano dentro de horario", f"{dentro:.0f} min" if pd.notna(dentro) else "s/d")
                st.metric("FRT mediano fuera de horario", f"{fuera:.0f} min" if pd.notna(fuera) else "s/d")
                if pd.notna(dentro) and pd.notna(fuera) and fuera > dentro * 3:
                    st.warning(f"Aun midiendo solo minutos de jornada, un lead que entra fuera de horario "
                               f"espera **{fuera/dentro:.0f} veces más**. "
                               "Un autorespondedor que fije expectativa y pida datos cuesta poco y tapa ese agujero.",
                               icon="⚠️")

            divider()

            divider()

            section_header("POR ASESOR", "Volumen, Velocidad y Cierre en una Sola Tabla",
                           subtitle="Antes esto estaba partido en dos tablas con columnas repetidas. "
                                    "Acá se ve de corrido: cuántos leads tomó cada uno, cuán rápido "
                                    "contestó y en qué terminaron.")

            por_asesor = nuevos.groupby('Asesor').agg(
                Leads=('contactNumber', 'nunique'),
                FRT_Mediano=('FRT_min', 'median'),
                FRT_p90=('FRT_min', lambda s: s.quantile(0.9)),
                Membresias=('Desenlace', lambda s: int((s == DES_MEMBRESIA).sum())),
                Consultorias=('Desenlace', lambda s: int((s == DES_CONSULTORIA).sum())),
                Derivados=('Desenlace', lambda s: int((s == DES_DERIVADO).sum())),
                No_Califica=('Desenlace', lambda s: int((s == DES_NO_CALIFICA).sum())),
                En_Proceso=('Desenlace', lambda s: int((s == DES_EN_PROCESO).sum())),
                Sin_Definir=('Desenlace', lambda s: int((s == DES_SIN_DEFINIR).sum())),
            ).reset_index()
            por_asesor['Ganados'] = (por_asesor['Membresias'] + por_asesor['Consultorias']
                                     + por_asesor['Derivados'])
            por_asesor['% Conversión'] = np.where(por_asesor['Leads'] > 0,
                                                  por_asesor['Ganados'] / por_asesor['Leads'] * 100, np.nan)
            por_asesor['% Sin Definir'] = por_asesor['Sin_Definir'] / por_asesor['Leads'] * 100
            por_asesor = por_asesor.sort_values('Leads', ascending=False)

            st.dataframe(
                por_asesor[['Asesor', 'Leads', 'FRT_Mediano', 'FRT_p90',
                            'Membresias', 'Consultorias', 'Derivados', 'Ganados', '% Conversión',
                            'No_Califica', 'En_Proceso', 'Sin_Definir', '% Sin Definir']].rename(columns={
                    'FRT_Mediano': 'FRT Mediano', 'FRT_p90': 'FRT p90', 'No_Califica': 'No Califica',
                    'Membresias': 'Membresías', 'Consultorias': 'Consultorías',
                    'En_Proceso': 'En Proceso', 'Sin_Definir': 'Sin Definir'}).style.format({
                        'FRT Mediano': '{:.0f}', 'FRT p90': '{:.0f}',
                        '% Conversión': '{:.1f}%', '% Sin Definir': '{:.0f}%'}),
                column_config={
                    "FRT Mediano": st.column_config.NumberColumn(help="Minutos de jornada hasta la primera respuesta."),
                    "FRT p90": st.column_config.NumberColumn(help="El 10% de leads peor atendidos esperó al menos esto."),
                    "Ganados": st.column_config.NumberColumn(help="Membresías + consultorías + derivados."),
                    "% Conversión": st.column_config.NumberColumn(help="Ganados sobre los leads reales de ese asesor."),
                    "En Proceso": st.column_config.NumberColumn(help="Charla abierta: todavía no se decidió."),
                    "Sin Definir": st.column_config.NumberColumn(help="Sin ninguna etiqueta de desenlace."),
                },
                hide_index=True, **ANCHO
            )

            if len(por_asesor):
                top = por_asesor.iloc[0]
                peso = top['Leads'] / n_leads * 100 if n_leads else 0
                if peso > 70:
                    st.warning(f"**{top['Asesor']}** concentra el **{peso:.0f}%** de los leads de esta línea. "
                               "Si está en una reunión o de licencia, la captación se frena entera.", icon="⚠️")

            section_header("FLUJO", "Entrada de Leads y Ventanas sin Cobertura")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                por_dia = nuevos.groupby(['fecha', 'Desenlace']).size().reset_index(name='Leads')
                fig_fd = px.bar(
                    por_dia, x='fecha', y='Leads', color='Desenlace',
                    color_discrete_map=DESENLACE_COLORS,
                    category_orders={'Desenlace': DESENLACES},
                    title="Leads por Día y Desenlace"
                )
                fig_fd = apply_bdi_theme(fig_fd, legend_below=True)
                fig_fd.update_layout(barmode='stack', xaxis_title="Fecha", yaxis_title="Leads",
                                     legend_title="", height=340)
                grafico(fig_fd, 'Leads por día y desenlace', 'comercial')
            with col_f2:
                por_hora = nuevos.groupby('hora_ingreso').agg(
                    Leads=('contactNumber', 'count'), FRT=('FRT_min', 'median')).reset_index()
                fig_fh = go.Figure()
                fig_fh.add_bar(x=por_hora['hora_ingreso'], y=por_hora['Leads'], name='Leads que entran',
                               marker_color='#8FBF74')
                fig_fh.add_scatter(x=por_hora['hora_ingreso'], y=por_hora['FRT'], name='FRT mediano (min)',
                                   yaxis='y2', mode='lines+markers',
                                   line=dict(color='#C9A227', width=3), marker=dict(size=8))
                fig_fh = apply_bdi_theme(fig_fh, legend_below=True)
                fig_fh.update_layout(
                    title=dict(text="Hora de Entrada vs. Demora en Responder", font=dict(color='#0F5132', size=17), x=0.01),
                    xaxis=dict(title="Hora del día", dtick=1),
                    yaxis=dict(title="Leads"),
                    yaxis2=dict(title="Minutos", overlaying='y', side='right', showgrid=False,
                                title_font=dict(color='#8A6D00'), tickfont=dict(color='#8A6D00')),
                    height=340
                )
                grafico(fig_fh, 'Hora de entrada vs demora', 'comercial')
            st.caption("💡 Las horas donde la barra es alta y la línea dorada también lo es son las ventanas "
                       "a cubrir primero: ahí entra volumen y se responde tarde.")

            divider()

            section_header("DETALLE", "Lead por Lead")
            opciones_det = DESENLACES + [DES_CLIENTE]
            filtro_des = st.multiselect("Filtrar por desenlace:", opciones_det, default=DESENLACES,
                                        key="filtro_desenlace",
                                        help=f"«{DES_CLIENTE}» está fuera del embudo; se puede sumar acá "
                                             "para revisar qué consultas llegan al número comercial.")
            det = leads[leads['Desenlace'].isin(filtro_des)].copy()
            det = det.sort_values('Primer Chat', ascending=False)
            det['Primer Chat'] = det['Primer Chat'].dt.strftime('%d/%m %H:%M')
            st.caption(f"{len(det):,} leads en la selección.")
            st.dataframe(
                det[['contactName', 'Asesor', 'Primer Chat', 'Desenlace', 'FRT_min',
                     'Conversaciones', 'Etiquetas']].rename(columns={
                        'contactName': 'Lead', 'FRT_min': 'FRT (min laborales)',
                        'Conversaciones': 'Chats'}).style.format({'FRT (min laborales)': '{:.0f}'}),
                hide_index=True, **ANCHO
            )


# ---------------------------------------------------------
# TAB LÍNEA PRINCIPAL: CARTERA / ATENCIÓN DE CLIENTES
# ---------------------------------------------------------


# ---------------------------------------------------------
# REPORTE PDF
# ---------------------------------------------------------
with tab_pdf:
    section_header("EXPORTAR", "Reporte en PDF",
                   subtitle="Cada bloque se calcula sobre su propia línea: un reporte de asesores no "
                            "incluye ni un chat del comercial. Respeta el filtro de período del panel "
                            "lateral; la conexión la define la opción que elijas acá.")

    linea_ase = detectar_linea_principal(df_raw)
    linea_com = detectar_linea_captacion(df_raw)

    OPCIONES_PDF = {
        f"Solo Asesores ({linea_ase})": ['asesores'],
        f"Solo Comercial ({linea_com})": ['comercial'],
        "Completo (las dos líneas)": ['asesores', 'comercial'],
    }
    eleccion = st.radio("¿Qué querés exportar?", list(OPCIONES_PDF), key="radio_pdf")
    claves = OPCIONES_PDF[eleccion]

    df_pdf = df_raw.copy()
    if periodos_sel:
        df_pdf = df_pdf[df_pdf['periodo'].isin(periodos_sel)]
    base_ase = df_pdf[df_pdf['conexion'] == linea_ase]
    base_com = df_pdf[df_pdf['conexion'] == linea_com]

    resumen = []
    if 'asesores' in claves:
        resumen.append(f"**{linea_ase}**: {base_ase[COL_ID].nunique():,} conversaciones")
    if 'comercial' in claves:
        resumen.append(f"**{linea_com}**: {base_com['contactNumber'].nunique():,} contactos")
    st.caption("Va a incluir " + " y ".join(resumen) +
               f", del período {', '.join(periodos_sel) if periodos_sel else 'completo'}.")

    if st.button("🖨️  Generar PDF", type="primary", key="btn_pdf"):
        with st.spinner("Renderizando los gráficos y armando el documento…"):
            try:
                bloques = []
                if 'asesores' in claves:
                    bloques.append((f"Asesores · Capacidad y Eficiencia · {linea_ase}",
                                    figuras_asesores(base_ase, linea_ase, periodos_disponibles)))
                if 'comercial' in claves:
                    bloques.append((f"Comercial · Embudo de Ventas · {linea_com}",
                                    figuras_comercial(base_com, linea_com, df_raw)))

                etiqueta_corta = ("asesores" if claves == ['asesores']
                                  else "comercial" if claves == ['comercial'] else "completo")
                pdf = construir_pdf(
                    bloques,
                    titulo=f"Reporte de Mensajería · {eleccion.split(' (')[0]}",
                    subtitulo=f"Período analizado: {', '.join(periodos_sel) if periodos_sel else 'todo el histórico'}. "
                              f"Jornada laboral de {HORARIO_TXT} hs: todos los tiempos de respuesta y "
                              "resolución están medidos en minutos de jornada, descontando noches, fines "
                              "de semana y feriados de Argentina. La unidad de conteo es la conversación "
                              "única, y en el bloque comercial, el contacto único.",
                    meta=f"BDI Consultora · generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                st.session_state['pdf_bytes'] = pdf
                st.session_state['pdf_nombre'] = (
                    f"BDI_mensajeria_{etiqueta_corta}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
            except Exception as e:
                st.session_state.pop('pdf_bytes', None)
                st.error(f"No se pudo generar el PDF → {type(e).__name__}: {e}")
                st.caption("Si el error menciona `kaleido`, falta esa dependencia en requirements.txt "
                           "(`kaleido==0.2.1`), que es la que convierte los gráficos en imágenes.")

    if st.session_state.get('pdf_bytes'):
        st.success(f"Listo · {len(st.session_state['pdf_bytes'])/1024/1024:.1f} MB", icon="✅")
        st.download_button("⬇️  Descargar PDF", data=st.session_state['pdf_bytes'],
                           file_name=st.session_state.get('pdf_nombre', 'reporte.pdf'),
                           mime="application/pdf", type="primary", key="dl_pdf")
        st.caption("Queda disponible hasta que cambies los filtros y lo vuelvas a generar.")

    st.markdown("""
---
**Cómo está armado**

Cada gráfico lleva un título que dice qué pregunta responde y un párrafo corto que explica qué mide
y cómo leerlo, para que el reporte se entienda sin tener a alguien al lado explicándolo.

- **Solo Asesores** — capacidad instalada, volumen mensual, carga horaria, mapa de calor día/hora,
  reparto entre asesores, velocidad de respuesta, mix patrimonial de cada cartera, brokers,
  fricción por plataforma y clientes que más demandan.
- **Solo Comercial** — embudo de tres escalones, desglose de desenlaces, velocidad de respuesta a
  prospectos, ritmo diario de entrada, ventanas horarias sin cobertura y rendimiento por asesor.
- **Completo** — las dos, cada una arrancando en página nueva con su banda de título.
""")
