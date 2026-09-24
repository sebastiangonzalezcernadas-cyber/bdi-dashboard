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
ESTADOS = ['Potencial Cliente', 'EX CLIENTE', 'no es cliente']
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
        Sin_Responder=('FRT_min', lambda s: int(s.isna().sum())),
        Resolucion_Mediana=('res_time_wh_min', 'median'),
        Nuevos=('isNewContact', 'sum'),
    ).reset_index()
    m['% de la Línea'] = m['Chats'] / total * 100 if total else np.nan
    m['Chats/Día'] = m['Chats'] / dias if dias else np.nan
    m['% Sin Responder'] = m['Sin_Responder'] / m['Chats'] * 100
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
            '% Sin Responder': g['FRT_min'].isna().mean() * 100,
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
kpi9.metric("Sin Responder", f"{int(df['FRT_min'].isna().sum()):,}",
            help="Conversaciones sin `firstSentMessageAt`: nunca se envió un primer mensaje desde BDI.")

kpi10.metric("Conexiones Activas", f"{df['conexion'].nunique()}",
             help="Líneas de WhatsApp con al menos una conversación en la selección. El detalle está en la pestaña Conexiones.")

st.write("")

tab1, tab_con, tab_cap, tab_pri, tab2, tab3, tab4, tab5 = st.tabs([
    "📅  Evolución y Temporalidad",
    "📞  Conexiones",
    "🎯  Captación Comercial",
    "🏦  Línea Principal",
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
                              xaxis=dict(tickangle=-30), legend_title="Conexión")
        st.plotly_chart(fig_mes, **ANCHO)

    with col_t2:
        if df['conexion'].nunique() > 1:
            df_dias = (df[df['dia_semana'].isin(DAY_ORDER_LABORAL)]
                       .groupby(['dia_semana', 'conexion'])[COL_ID].nunique().reset_index(name='Chats'))
            fig_dias = px.bar(
                df_dias, x='dia_semana', y='Chats', text='Chats', color='conexion',
                color_discrete_map=CONEXION_COLORS,
                category_orders={'dia_semana': DAY_ORDER_LABORAL},
                title="Distribución de Chats por Día (total apilado por conexión)"
            )
            fig_dias.update_traces(textposition='inside', textfont=dict(color='#FFFFFF'))
            fig_dias = apply_bdi_theme(fig_dias, legend_below=True)
            fig_dias.update_layout(barmode='stack')
        else:
            df_dias = df['dia_semana'].value_counts().reindex(DAY_ORDER_LABORAL).fillna(0).reset_index()
            df_dias.columns = ['Día', 'Chats']
            fig_dias = px.bar(
                df_dias, x='Día', y='Chats', text='Chats',
                color_discrete_sequence=['#2FA66B'], title="Distribución de Chats (Lunes a Viernes)"
            )
            fig_dias.update_traces(textposition='outside')
            fig_dias = apply_bdi_theme(fig_dias)
        fig_dias.update_layout(xaxis_title="Día", yaxis_title="Cantidad de Chats", legend_title="Conexión")
        st.plotly_chart(fig_dias, **ANCHO)

    if df['fecha_corta'].notna().any():
        varias_conexiones = df['conexion'].nunique() > 1
        if varias_conexiones:
            df_diario = df.groupby(['fecha_corta', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
            fig_diario = px.area(
                df_diario, x='fecha_corta', y='Chats', color='conexion',
                color_discrete_map=CONEXION_COLORS,
                title="Serie Diaria de Conversaciones (apilada por conexión)"
            )
            fig_diario.update_traces(line=dict(width=1.5))
            fig_diario = apply_bdi_theme(fig_diario, legend_below=True)
            fig_diario.update_layout(legend_title="Conexión")
        else:
            df_diario = df.groupby('fecha_corta')[COL_ID].nunique().reset_index(name='Chats')
            fig_diario = px.line(
                df_diario, x='fecha_corta', y='Chats',
                color_discrete_sequence=['#0F5132'], title="Serie Diaria de Conversaciones"
            )
            fig_diario.update_traces(line=dict(width=2))
            fig_diario = add_reference_line(fig_diario, df_diario['Chats'].mean(), orientation='h', label='Promedio diario')
            fig_diario = apply_bdi_theme(fig_diario)
        fig_diario.update_layout(xaxis_title="Fecha", yaxis_title="Conversaciones", height=340)
        st.plotly_chart(fig_diario, **ANCHO)

    section_header("REPARTO", "Peso de Cada Conexión en el Total")
    col_d1, col_d2 = st.columns([2, 3])
    with col_d1:
        rep = df.groupby('conexion')[COL_ID].nunique().reset_index(name='Chats')
        fig_rep = px.pie(
            rep, values='Chats', names='conexion', hole=0.5,
            color='conexion', color_discrete_map=CONEXION_COLORS,
            title="Chats Totales por Conexión"
        )
        fig_rep.update_traces(textinfo='percent+value', textposition='inside')
        fig_rep = apply_bdi_theme(fig_rep, legend_below=True)
        fig_rep.update_layout(margin=dict(t=60, b=80, l=30, r=30), height=380)
        st.plotly_chart(fig_rep, **ANCHO)
    with col_d2:
        rep_u = df.groupby(['conexion', 'user'])[COL_ID].nunique().reset_index(name='Chats')
        fig_repu = px.bar(
            rep_u, x='conexion', y='Chats', color='user', text='Chats',
            color_discrete_map=USER_COLORS, title="Composición de Cada Conexión por Asesor"
        )
        fig_repu.update_traces(textposition='inside', textfont=dict(color='#FFFFFF'))
        fig_repu = apply_bdi_theme(fig_repu, legend_below=True)
        fig_repu.update_layout(barmode='stack', xaxis_title="", yaxis_title="Conversaciones",
                               legend_title="Asesor", height=380)
        st.plotly_chart(fig_repu, **ANCHO)

    section_header("CARGA HORARIA", "Distribución de Consultas por Hora")
    if df['conexion'].nunique() > 1:
        df_hora = df.groupby(['hora', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
        fig_hora = px.area(
            df_hora, x='hora', y='Chats', color='conexion', markers=True,
            color_discrete_map=CONEXION_COLORS,
            title="Carga Horaria General (total apilado por conexión, 0 a 23 hs)"
        )
        fig_hora.update_traces(marker=dict(size=6))
        fig_hora = apply_bdi_theme(fig_hora, legend_below=True)
    else:
        df_hora = df.groupby('hora')[COL_ID].nunique().reset_index(name='Chats')
        fig_hora = px.area(
            df_hora, x='hora', y='Chats', markers=True,
            color_discrete_sequence=['#3AAFB9'], title="Carga Horaria General (Franja de 0 a 23 hs)"
        )
        fig_hora.update_traces(marker=dict(size=8, color='#0F5132'),
                               fillcolor='rgba(58,175,185,0.15)', line=dict(color='#0F5132'))
        fig_hora = apply_bdi_theme(fig_hora)
    fig_hora.update_layout(xaxis_title="Hora del día", yaxis_title="Cantidad de Chats",
                           xaxis=dict(dtick=1), legend_title="Conexión")
    st.plotly_chart(fig_hora, **ANCHO)

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
    st.plotly_chart(fig_hora_30, **ANCHO)


# ---------------------------------------------------------
# TAB CONEXIONES: COMPARATIVA ENTRE LÍNEAS DE WHATSAPP
# ---------------------------------------------------------
with tab_con:
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
        c[5].metric("% Sin Responder", f"{fila['% Sin Responder']:.1f}%")
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
            if pd.notna(otra['% Sin Responder']) and otra['% Sin Responder'] > max(principal['% Sin Responder'] * 1.5, 10):
                lecturas.append(
                    f"⚠️ **{otra['Conexión']}** deja **{otra['% Sin Responder']:.0f}% de conversaciones sin "
                    f"primera respuesta** (vs {principal['% Sin Responder']:.0f}%).")
        if lecturas:
            st.info("🔎 **Lectura automática**\n\n" + "\n\n".join(f"- {l}" for l in lecturas))

    divider()

    section_header("TABLA COMPARATIVA", "Todas las Métricas Lado a Lado")
    tabla = res_con.drop(columns=['Desde', 'Hasta']).copy()
    st.dataframe(
        tabla.style.format({
            'Chats/Contacto': '{:.2f}', 'Chats/Día': '{:.1f}', '% Nuevos': '{:.1f}%',
            'FRT Mediano': '{:.1f}', '% Sin Responder': '{:.1f}%',
            'Resolución Mediana': '{:.0f}', '% Inicia Cliente': '{:.0f}%'
        }),
        column_config={
            "Chats/Día": st.column_config.NumberColumn(help="Conversaciones divididas los días hábiles en que ESA línea estuvo activa."),
            "% Nuevos": st.column_config.NumberColumn(help="Porcentaje de conversaciones con un contacto que escribe por primera vez."),
            "FRT Mediano": st.column_config.NumberColumn(help="Minutos hasta el primer mensaje enviado desde BDI."),
            "% Sin Responder": st.column_config.NumberColumn(help="Conversaciones que nunca recibieron un primer mensaje nuestro."),
            "% Inicia Cliente": st.column_config.NumberColumn(help="Conversaciones abiertas por el cliente y no por el asesor.")
        },
        hide_index=True, **ANCHO
    )

    divider()

    section_header("EVOLUCIÓN", "Volumen Diario por Conexión",
                   subtitle="Sirve para ver desde qué día quedó operativa cada línea.")
    df_dia_con = df.groupby(['fecha_corta', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
    fig_dc = px.line(
        df_dia_con, x='fecha_corta', y='Chats', color='conexion',
        color_discrete_map=CONEXION_COLORS, markers=True,
        title="Conversaciones por Día y Conexión"
    )
    fig_dc.update_traces(line=dict(width=2), marker=dict(size=5))
    fig_dc = apply_bdi_theme(fig_dc, legend_below=True)
    fig_dc.update_layout(xaxis_title="Fecha", yaxis_title="Conversaciones", legend_title="Conexión", height=380)
    st.plotly_chart(fig_dc, **ANCHO)

    col_cc1, col_cc2 = st.columns(2)
    with col_cc1:
        fig_nuevos = px.bar(
            res_con, x='Conexión', y='% Nuevos', text='% Nuevos',
            color='Conexión', color_discrete_map=CONEXION_COLORS,
            title="Captación: % de Contactos Nuevos"
        )
        fig_nuevos.update_traces(texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
        fig_nuevos = apply_bdi_theme(fig_nuevos)
        fig_nuevos.update_layout(showlegend=False, xaxis_title="", yaxis_title="% de conversaciones")
        st.plotly_chart(fig_nuevos, **ANCHO)
    with col_cc2:
        fig_frtc = px.bar(
            res_con, x='Conexión', y='FRT Mediano', text='FRT Mediano',
            color='Conexión', color_discrete_map=CONEXION_COLORS,
            title="Agilidad: FRT Mediano por Conexión (min)"
        )
        fig_frtc.update_traces(texttemplate='%{text:.0f} min', textposition='outside', cliponaxis=False)
        fig_frtc = apply_bdi_theme(fig_frtc)
        fig_frtc.update_layout(showlegend=False, xaxis_title="", yaxis_title="Minutos (mediana)")
        st.plotly_chart(fig_frtc, **ANCHO)

    divider()

    section_header("QUIÉN ATIENDE QUÉ", "Reparto de Asesores entre Líneas",
                   subtitle="Los asesores responden en las dos conexiones: acá se ve cuánto pesa cada una en su carga.")
    df_uc = df.groupby(['user', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
    orden_users = df_uc.groupby('user')['Chats'].sum().sort_values(ascending=True).index.tolist()

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        fig_uc = px.bar(
            df_uc, x='Chats', y='user', color='conexion', orientation='h', text='Chats',
            color_discrete_map=CONEXION_COLORS, category_orders={'user': orden_users},
            title="Conversaciones por Asesor y Conexión"
        )
        fig_uc.update_traces(textposition='inside', textfont=dict(color='#FFFFFF'))
        fig_uc = apply_bdi_theme(fig_uc, legend_below=True)
        fig_uc.update_layout(barmode='stack', xaxis_title="Conversaciones", yaxis_title="",
                             legend_title="Conexión", height=420)
        st.plotly_chart(fig_uc, **ANCHO)

    with col_q2:
        df_frt_uc = df.groupby(['user', 'conexion'])['FRT_min'].median().reset_index()
        fig_frt_uc = px.bar(
            df_frt_uc, x='FRT_min', y='user', color='conexion', orientation='h', text='FRT_min',
            barmode='group', color_discrete_map=CONEXION_COLORS, category_orders={'user': orden_users},
            title="FRT Mediano por Asesor y Conexión (min)"
        )
        fig_frt_uc.update_traces(texttemplate='%{text:.0f}', textposition='outside', cliponaxis=False)
        fig_frt_uc = apply_bdi_theme(fig_frt_uc, legend_below=True)
        fig_frt_uc.update_layout(xaxis_title="Minutos (mediana)", yaxis_title="",
                                 legend_title="Conexión", height=420)
        st.plotly_chart(fig_frt_uc, **ANCHO)

    st.caption("💡 Un asesor con FRT alto en una sola de las líneas suele indicar que esa conexión "
               "no está en su rutina de revisión, no que responda lento en general.")

    section_header("HORARIOS", "Cuándo Escribe Cada Línea",
                   subtitle="Normalizado dentro de cada conexión para que una línea chica no quede aplastada.")
    df_hc = df[(df['hora'] >= HORA_GRAF_INI - 1) & (df['hora'] <= HORA_GRAF_FIN + 2)].groupby(['conexion', 'hora'])[COL_ID].nunique().reset_index(name='Chats')
    if not df_hc.empty:
        tot_h = df_hc.groupby('conexion')['Chats'].transform('sum')
        df_hc['Pct'] = df_hc['Chats'] / tot_h * 100
        fig_hc = px.line(
            df_hc, x='hora', y='Pct', color='conexion', markers=True,
            color_discrete_map=CONEXION_COLORS,
            title="Distribución Horaria Relativa por Conexión (%)"
        )
        fig_hc.update_traces(line=dict(width=2.5), marker=dict(size=7))
        fig_hc = apply_bdi_theme(fig_hc, legend_below=True)
        fig_hc.update_layout(xaxis_title="Hora del día", yaxis_title="% de las conversaciones de la línea",
                             legend_title="Conexión", xaxis=dict(dtick=1), height=380)
        st.plotly_chart(fig_hc, **ANCHO)
    else:
        st.info("No hay conversaciones en la franja horaria analizada.")


# ---------------------------------------------------------
# TAB CAPTACIÓN: EMBUDO DE LA LÍNEA COMERCIAL
# ---------------------------------------------------------
with tab_cap:
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
            total_leads = len(leads)
            nuevos = leads[leads['Estado'] != 'Ya era cliente']
            n_nuevos = len(nuevos)
            respondidos = int(nuevos['Respondido'].sum())
            rapidos = int((nuevos['FRT_min'] < 15).sum())
            derivados = int((nuevos['Estado'] == 'Derivado a asesores').sum())

            section_header("EMBUDO", f"Recorrido del Lead en {linea_cap}",
                           subtitle="La unidad es el contacto único, no la conversación: en una línea de "
                                    "captación la persona escribe una vez y no vuelve.")

            etapas = pd.DataFrame({
                'Etapa': ['Leads que escribieron', 'Recibieron respuesta',
                          'Respondidos en menos de 15 min', 'Derivados a un asesor'],
                'Leads': [n_nuevos, respondidos, rapidos, derivados]
            })
            etapas['% del total'] = (etapas['Leads'] / n_nuevos * 100) if n_nuevos else 0

            fig_emb = px.bar(
                etapas[::-1], x='Leads', y='Etapa', orientation='h', text='Leads',
                color_discrete_sequence=['#157347'], title="Embudo de Captación (leads únicos)"
            )
            fig_emb.update_traces(textposition='outside', cliponaxis=False)
            fig_emb = apply_bdi_theme(fig_emb)
            fig_emb.update_layout(xaxis_title="Leads", yaxis_title="", height=330,
                                  margin=dict(t=60, b=40, l=230, r=60))
            st.plotly_chart(fig_emb, **ANCHO)

            k = st.columns(5)
            k[0].metric("Leads Reales", f"{n_nuevos:,}",
                        help="Contactos únicos nuevos. Excluye a los que ya eran clientes de la línea de asesores.")
            k[1].metric("Tasa de Respuesta", f"{respondidos/n_nuevos*100:.0f}%" if n_nuevos else "s/d",
                        help="Porcentaje de leads que recibió al menos una respuesta.")
            k[2].metric("Leads Perdidos", f"{n_nuevos - respondidos:,}",
                        delta=f"-{(n_nuevos-respondidos)/n_nuevos*100:.0f}%" if n_nuevos else None,
                        delta_color="inverse",
                        help="Escribieron y nunca recibieron una respuesta. Cada uno es una oportunidad que se fue sin ruido.")
            k[3].metric("FRT p90", f"{nuevos['FRT_min'].quantile(0.9):.0f} min" if nuevos['FRT_min'].notna().any() else "s/d",
                        help="El 10% peor de los leads espera al menos esto. Es la cola que hunde la conversión, no la mediana.")
            k[4].metric("Tasa de Derivación", f"{derivados/n_nuevos*100:.0f}%" if n_nuevos else "s/d",
                        help="Leads que después aparecen conversando en la línea de asesores.")

            conv_sin_resp = int(df_cap['FRT_min'].isna().sum())
            if conv_sin_resp > (n_nuevos - respondidos):
                st.caption(f"⚠️ Ojo con la diferencia de unidades: **{n_nuevos - respondidos} lead(s) nunca "
                           f"recibieron ninguna respuesta**, pero hubo **{conv_sin_resp} conversaciones sin "
                           "responder**. La diferencia son personas ya contestadas alguna vez que volvieron "
                           "a escribir y quedaron sin respuesta en ese segundo intento.")

            ya_clientes = total_leads - n_nuevos
            if ya_clientes:
                st.caption(f"ℹ️ Además entraron **{ya_clientes} contactos que ya eran clientes** de la línea de "
                           "asesores y escribieron a este número. No se cuentan como captación, pero sirven "
                           "para detectar si el número comercial se está difundiendo donde no corresponde.")

            divider()

            section_header("VELOCIDAD", "Cuánto Tarda en Contestarse un Lead",
                           subtitle=f"Minutos de jornada laboral ({HORARIO_TXT} hs). En captación lo que "
                                    "define el resultado es la cola, no el promedio.")
            col_v1, col_v2 = st.columns([3, 2])
            with col_v1:
                tramos = (nuevos['Tramo'].value_counts()
                          .reindex(ORDEN_TRAMOS).fillna(0).reset_index())
                tramos.columns = ['Tramo', 'Leads']
                tramos['Pct'] = tramos['Leads'] / n_nuevos * 100
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
                                     height=340, margin=dict(t=60, b=40, l=150, r=70))
                st.plotly_chart(fig_tr, **ANCHO)
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

            section_header("QUIÉN ATIENDE", "Rendimiento por Asesor en la Línea Comercial",
                           subtitle="Volumen, cobertura y cola de espera. El p90 muestra al que contesta rápido "
                                    "casi siempre pero deja algunos leads dormidos.")
            por_asesor = nuevos.groupby('Asesor').agg(
                Leads=('contactNumber', 'nunique'),
                Respondidos=('Respondido', 'sum'),
                FRT_Mediano=('FRT_min', 'median'),
                FRT_p90=('FRT_min', lambda s: s.quantile(0.9)),
                Derivados=('Estado', lambda s: (s == 'Derivado a asesores').sum())
            ).reset_index()
            por_asesor['Sin Responder'] = por_asesor['Leads'] - por_asesor['Respondidos']
            por_asesor['% Respuesta'] = por_asesor['Respondidos'] / por_asesor['Leads'] * 100
            por_asesor['% Derivación'] = por_asesor['Derivados'] / por_asesor['Leads'] * 100
            por_asesor['% de la Línea'] = por_asesor['Leads'] / n_nuevos * 100
            por_asesor = por_asesor.sort_values('Leads', ascending=False)

            st.dataframe(
                por_asesor[['Asesor', 'Leads', '% de la Línea', '% Respuesta', 'Sin Responder',
                            'FRT_Mediano', 'FRT_p90', 'Derivados', '% Derivación']].style.format({
                    '% de la Línea': '{:.0f}%', '% Respuesta': '{:.0f}%',
                    'FRT_Mediano': '{:.0f}', 'FRT_p90': '{:.0f}', '% Derivación': '{:.0f}%'
                }),
                column_config={
                    "FRT_Mediano": st.column_config.NumberColumn("FRT Mediano (min)"),
                    "FRT_p90": st.column_config.NumberColumn("FRT p90 (min)",
                        help="El 10% de leads peor atendidos esperó al menos esto."),
                    "Sin Responder": st.column_config.NumberColumn(help="Leads que nunca recibieron respuesta de este asesor."),
                },
                hide_index=True, **ANCHO
            )

            if len(por_asesor) and por_asesor.iloc[0]['% de la Línea'] > 70:
                top = por_asesor.iloc[0]
                st.warning(f"**{top['Asesor']}** concentra el **{top['% de la Línea']:.0f}%** de los leads de esta línea. "
                           "Si está en una reunión o de licencia, la captación se frena entera.", icon="⚠️")

            col_a1, col_a2 = st.columns(2)
            with col_a1:
                fig_pa = px.bar(
                    por_asesor.sort_values('Leads'), x='Leads', y='Asesor', orientation='h', text='Leads',
                    color='Asesor', color_discrete_map=USER_COLORS, title="Leads Atendidos por Asesor"
                )
                fig_pa.update_traces(textposition='outside', cliponaxis=False)
                fig_pa = apply_bdi_theme(fig_pa)
                fig_pa.update_layout(showlegend=False, xaxis_title="Leads únicos", yaxis_title="", height=320)
                st.plotly_chart(fig_pa, **ANCHO)
            with col_a2:
                comp = por_asesor.melt(id_vars='Asesor', value_vars=['FRT_Mediano', 'FRT_p90'],
                                       var_name='Métrica', value_name='Minutos')
                comp['Métrica'] = comp['Métrica'].map({'FRT_Mediano': 'Mediana', 'FRT_p90': 'p90 (la cola)'})
                fig_pp = px.bar(
                    comp, x='Minutos', y='Asesor', color='Métrica', orientation='h', barmode='group',
                    color_discrete_map={'Mediana': '#157347', 'p90 (la cola)': '#C9A227'},
                    title="Tiempo de Respuesta: Mediana vs. Cola"
                )
                fig_pp.update_traces(texttemplate='%{x:.0f}', textposition='outside', cliponaxis=False)
                fig_pp = apply_bdi_theme(fig_pp, legend_below=True)
                fig_pp.update_layout(xaxis_title="Minutos", yaxis_title="", legend_title="", height=320)
                st.plotly_chart(fig_pp, **ANCHO)

            divider()

            section_header("FLUJO", "Entrada de Leads y Ventanas sin Cobertura")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                por_dia = leads.groupby(['fecha', 'Estado']).size().reset_index(name='Leads')
                fig_fd = px.bar(
                    por_dia, x='fecha', y='Leads', color='Estado',
                    color_discrete_map={'Sin derivar': '#8FBF74', 'Derivado a asesores': '#0F5132',
                                        'Ya era cliente': '#C9D2CE'},
                    title="Leads por Día y Desenlace"
                )
                fig_fd = apply_bdi_theme(fig_fd, legend_below=True)
                fig_fd.update_layout(barmode='stack', xaxis_title="Fecha", yaxis_title="Leads",
                                     legend_title="", height=340)
                st.plotly_chart(fig_fd, **ANCHO)
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
                st.plotly_chart(fig_fh, **ANCHO)
            st.caption("💡 Las horas donde la barra es alta y la línea dorada también lo es son las ventanas "
                       "a cubrir primero: ahí entra volumen y se responde tarde.")

            divider()

            section_header("DERIVACIÓN", "Leads que Llegaron a un Asesor")
            derivados_df = nuevos[nuevos['Estado'] == 'Derivado a asesores']
            if not derivados_df.empty:
                cd1, cd2 = st.columns([2, 3])
                with cd1:
                    st.metric("Horas medianas hasta la derivación",
                              f"{derivados_df['Horas a Derivación'].median():.0f} hs")
                    st.caption("Desde que el lead escribe al número comercial hasta su primera conversación "
                               "con un asesor.")
                with cd2:
                    tabla_der = derivados_df[['contactName', 'Asesor', 'Primer Chat', 'Horas a Derivación']].copy()
                    tabla_der['Primer Chat'] = tabla_der['Primer Chat'].dt.strftime('%d/%m %H:%M')
                    tabla_der.columns = ['Lead', 'Atendido por', 'Primer Contacto', 'Horas a Derivación']
                    st.dataframe(tabla_der.style.format({'Horas a Derivación': '{:.1f}'}),
                                 hide_index=True, **ANCHO)
            else:
                st.info("Todavía ningún lead de esta línea aparece conversando en la línea de asesores. "
                        "Con pocos días de operación es esperable: la derivación en septiembre tardó entre 24 y 44 horas.")

            st.markdown("""
---
##### Lo que este tablero todavía no puede medir

La derivación se detecta sola porque el contacto reaparece en la otra línea. **La venta de
membresía no deja rastro en el CRM**, así que no hay forma de calcularla. Con una etiqueta por
lead — `Derivado`, `Membresia`, `No califica`, `Sin interés` — estas mismas métricas pasan a
mostrar conversión real por asesor y por origen, sin tocar el código.
""")


# ---------------------------------------------------------
# TAB LÍNEA PRINCIPAL: CARTERA / ATENCIÓN DE CLIENTES
# ---------------------------------------------------------
with tab_pri:
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
            p2[1].metric("Sin Responder", f"{int(df_pri['FRT_min'].isna().sum()):,}")
            p2[2].metric("% Sin Responder", f"{df_pri['FRT_min'].isna().mean()*100:.1f}%")
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
                    'FRT_Mediano', 'FRT_p90', 'Sin_Responder', '% Sin Responder',
                    'Resolucion_Mediana', 'Nuevos']].rename(columns={
                        'user': 'Asesor', 'FRT_Mediano': 'FRT Mediano (min)', 'FRT_p90': 'FRT p90 (min)',
                        'Sin_Responder': 'Sin Responder', 'Resolucion_Mediana': 'Resolución Mediana (min)',
                        'Nuevos': 'Contactos Nuevos'
                    }).style.format({
                        '% de la Línea': '{:.1f}%', 'Chats/Día': '{:.1f}', 'Chats/Contacto': '{:.2f}',
                        'FRT Mediano (min)': '{:.1f}', 'FRT p90 (min)': '{:.0f}',
                        '% Sin Responder': '{:.1f}%', 'Resolución Mediana (min)': '{:.0f}'
                    }),
                column_config={
                    "FRT p90 (min)": st.column_config.NumberColumn(help="La cola: el 10% peor atendido de este asesor."),
                    "Chats/Contacto": st.column_config.NumberColumn(help="Cuántas veces vuelve a escribir el mismo cliente a este asesor."),
                },
                hide_index=True, **ANCHO
            )

            col_pr1, col_pr2 = st.columns(2)
            with col_pr1:
                fig_pu = px.bar(
                    mu.sort_values('Chats'), x='Chats', y='user', orientation='h', text='Chats',
                    color='user', color_discrete_map=USER_COLORS,
                    title=f"Volumen por Asesor · {linea_pri}"
                )
                fig_pu.update_traces(textposition='outside', cliponaxis=False)
                fig_pu = apply_bdi_theme(fig_pu)
                fig_pu.update_layout(showlegend=False, xaxis_title="Conversaciones", yaxis_title="", height=360)
                st.plotly_chart(fig_pu, **ANCHO)
            with col_pr2:
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
                fig_pf.update_layout(xaxis_title="Minutos", yaxis_title="", legend_title="", height=360)
                st.plotly_chart(fig_pf, **ANCHO)

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
                                  height=340, margin=dict(t=60, b=40, l=150, r=80))
            st.plotly_chart(fig_trp, **ANCHO)

            divider()

            section_header("SATURACIÓN", f"Carga por Día y Hora · {linea_pri}")
            df_hp = df_pri[(df_pri['hora'] >= HORA_GRAF_INI) & (df_pri['hora'] <= HORA_GRAF_FIN) &
                           (~df_pri['dia_semana'].isin(['Sábado', 'Domingo']))]
            if not df_hp.empty:
                hc = df_hp.groupby(['dia_semana', 'hora'])[COL_ID].nunique().reset_index(name='Chats')
                horas_p = list(range(HORA_GRAF_INI, HORA_GRAF_FIN + 1))
                hdp = hc.pivot(index='dia_semana', columns='hora', values='Chats').reindex(
                    index=DAY_ORDER_LABORAL, columns=horas_p).fillna(0)
                zp = hdp.values
                zmaxp = zp.max() if zp.max() > 0 else 1
                xs_p = [f"{h:02d}h" for h in horas_p]
                fig_hp = go.Figure(data=go.Heatmap(
                    z=zp, x=xs_p, y=list(hdp.index), colorscale=BDI_HEATSCALE, xgap=4, ygap=4,
                    colorbar=dict(title=dict(text="Chats", font=dict(color='#0F5132', size=12)),
                                  thickness=12, len=0.75, outlinewidth=0,
                                  tickfont=dict(color='#4A5D57', size=11)),
                    hovertemplate="<b>%{y} · %{x}</b><br>Conversaciones: %{z}<extra></extra>",
                    zmin=0, zmax=zmaxp
                ))
                anns = []
                for i, day in enumerate(hdp.index):
                    for j, h in enumerate(horas_p):
                        v = zp[i][j]
                        if v == 0:
                            continue
                        anns.append(dict(x=xs_p[j], y=day, text=f"<b>{int(v)}</b>", showarrow=False,
                                         font=dict(color='#FFFFFF' if v/zmaxp > 0.60 else '#14382A', size=12)))
                fig_hp.update_layout(annotations=anns)
                fig_hp = apply_bdi_theme(fig_hp)
                fig_hp.update_xaxes(title="Hora del día", side="top", showgrid=False,
                                    tickfont=dict(color='#0F5132', size=12), ticks="")
                fig_hp.update_yaxes(title="", showgrid=False, autorange="reversed",
                                    tickfont=dict(color='#0F5132', size=13), ticks="")
                fig_hp.update_layout(title=dict(text=f"Distribución de Carga · {linea_pri}",
                                                font=dict(color='#0F5132', size=17), x=0.01),
                                     height=430, plot_bgcolor='#FBFDFC',
                                     margin=dict(t=90, b=30, l=110, r=40))
                st.plotly_chart(fig_hp, **ANCHO)
            else:
                st.info("No hay conversaciones en jornada laboral para esta línea.")

            divider()

            section_header("CLIENTES", f"Quiénes Más Escriben a {linea_pri}")
            top_p = df_pri.groupby(['contactName', 'contactNumber']).agg(
                Chats=(COL_ID, 'nunique'),
                Asesor=('user', lambda x: x.mode()[0] if not x.mode().empty else '')
            ).reset_index().sort_values('Chats', ascending=False).head(12)
            fig_tp = px.bar(
                top_p.sort_values('Chats'), x='Chats', y='contactName', orientation='h', text='Chats',
                color='Asesor', color_discrete_map=USER_COLORS,
                title=f"Top 12 Clientes · {linea_pri}"
            )
            fig_tp.update_traces(textposition='outside', cliponaxis=False)
            fig_tp = apply_bdi_theme(fig_tp, legend_below=True)
            fig_tp.update_layout(height=520, xaxis_title="Conversaciones", yaxis_title="",
                                 margin=dict(t=60, b=90, l=180, r=60))
            st.plotly_chart(fig_tp, **ANCHO)

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
        st.plotly_chart(fig_broker, **ANCHO)

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
        st.plotly_chart(fig_tier, **ANCHO)

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
        st.plotly_chart(fig_broker_filt, **ANCHO)

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
        st.plotly_chart(fig_tier_filt, **ANCHO)

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
        st.plotly_chart(fig_broker_usr, **ANCHO)

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
        st.plotly_chart(fig_tier_usr, **ANCHO)

    divider()

    section_header("SERVICIOS", "Etiquetas Comerciales",
                   subtitle="Membresía, Agro, Consultoría y demás etiquetas del CRM que no son broker ni segmento.")
    df_serv = df.explode('servicios').dropna(subset=['servicios'])
    if not df_serv.empty:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            serv_counts = df_serv.groupby('servicios')[COL_ID].nunique().reset_index(name='Chats')
            fig_serv = px.bar(
                serv_counts.sort_values('Chats'), x='Chats', y='servicios', orientation='h', text='Chats',
                color='servicios', color_discrete_map=SERVICIO_COLORS,
                title="Conversaciones por Servicio"
            )
            fig_serv.update_traces(textposition='outside', cliponaxis=False)
            fig_serv = apply_bdi_theme(fig_serv)
            fig_serv.update_layout(showlegend=False, xaxis_title="Conversaciones", yaxis_title="")
            st.plotly_chart(fig_serv, **ANCHO)
        with col_s2:
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
            st.plotly_chart(fig_serv_u, **ANCHO)
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
        height=780, margin=dict(t=60, b=90, l=60, r=60)
    )
    st.plotly_chart(fig_tier_broker, **ANCHO)

# ---------------------------------------------------------
# TAB 3: CLIENTES
# ---------------------------------------------------------
with tab3:
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
    fig_top10.update_layout(height=600, margin=dict(t=60, b=90, l=140, r=60))
    st.plotly_chart(fig_top10, **ANCHO)

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
with tab4:
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
                   'FRT_Mediano', 'FRT_p90', 'Sin_Responder', '% Sin Responder',
                   'Resolucion_Mediana', 'Nuevos']].rename(columns={
                       'user': 'Asesor', 'FRT_Mediano': 'FRT Mediano (min)', 'FRT_p90': 'FRT p90 (min)',
                       'Sin_Responder': 'Sin Responder', 'Resolucion_Mediana': 'Resolución Mediana (min)',
                       'Nuevos': 'Contactos Nuevos'
                   }).style.format({
                       '% de la Línea': '{:.1f}%', 'Chats/Día': '{:.1f}',
                       'FRT Mediano (min)': '{:.1f}', 'FRT p90 (min)': '{:.0f}',
                       '% Sin Responder': '{:.1f}%', 'Resolución Mediana (min)': '{:.0f}'
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

    section_header("PARTICIPACIÓN", "Distribución de la Carga Operativa por Conexión")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        df_uc4 = df.groupby(['user', 'conexion'])[COL_ID].nunique().reset_index(name='Chats')
        orden_u4 = df_uc4.groupby('user')['Chats'].sum().sort_values(ascending=True).index.tolist()
        fig_pie = px.bar(
            df_uc4, x='Chats', y='user', color='conexion', orientation='h', text='Chats',
            color_discrete_map=CONEXION_COLORS, category_orders={'user': orden_u4},
            title="Conversaciones por Asesor, Divididas por Conexión"
        )
        fig_pie.update_traces(textposition='inside', textfont=dict(color='#FFFFFF'))
        fig_pie = apply_bdi_theme(fig_pie, legend_below=True)
        fig_pie.update_layout(barmode='stack', xaxis_title="Conversaciones", yaxis_title="",
                              legend_title="Conexión", height=400)
        st.plotly_chart(fig_pie, **ANCHO)

    with col_u2:
        df_frt4 = df.groupby(['user', 'conexion'])['FRT_min'].median().reset_index()
        fig_frt = px.bar(
            df_frt4, x='FRT_min', y='user', color='conexion', orientation='h', text='FRT_min',
            barmode='group', color_discrete_map=CONEXION_COLORS, category_orders={'user': orden_u4},
            title="FRT Mediano por Asesor y Conexión (min)"
        )
        fig_frt.update_traces(texttemplate='%{text:.0f}', textposition='outside', cliponaxis=False)
        fig_frt = apply_bdi_theme(fig_frt, legend_below=True)
        fig_frt.update_layout(xaxis_title="Minutos", yaxis_title="", legend_title="Conexión", height=400)
        st.plotly_chart(fig_frt, **ANCHO)

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
            cols_pie[idx % 3].plotly_chart(fig_p, **ANCHO)
        st.caption("💡 Pasá el cursor sobre cada porción para ver el detalle exacto por segmento y asesor.")
    else:
        st.info("No hay datos de patrimonio etiquetados para mostrar bajo los filtros actuales.")

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
        st.plotly_chart(fig_heatmap, **ANCHO)

        pico = heatmap_counts.loc[heatmap_counts['Chats'].idxmax()]
        st.caption(f"🔥 **Pico de demanda:** {pico['dia_semana']} a las {int(pico['hora']):02d}:00 hs "
                   f"con {int(pico['Chats'])} conversaciones ({pico['Porcentaje']:.0f}% del día).")
    else:
        st.info("No hay chats registrados en jornada laboral para la selección actual.")

# ---------------------------------------------------------
# TAB 5: FRICCIÓN Y COMPLEJIDAD
# ---------------------------------------------------------
with tab5:
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

    col_f1, col_f2 = st.columns(2)
    with col_f1:
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
        fig_fric_b.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Broker", showlegend=False)
        st.plotly_chart(fig_fric_b, **ANCHO)

    with col_f2:
        df_fric_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier').agg(
            Chats=(COL_ID, 'nunique'), Usuarios=('contactNumber', 'nunique')
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
        fig_fric_t.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_fric_t, **ANCHO)

    divider()

    section_header(
        "COMPLEJIDAD OPERATIVA", "Análisis de Tiempos de Atención (SLA)",
        subtitle="Cruza tiempos de resolución y de primera respuesta con plataformas y patrimonio."
    )

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        df_comp_broker = df_exp_5[df_exp_5['brokers'] != 'Sin Broker'].groupby('brokers')['res_time_wh_min'].median().reset_index()

        fig_comp_b = px.bar(
            df_comp_broker.sort_values('res_time_wh_min', ascending=True),
            x='res_time_wh_min', y='brokers', orientation='h', text='res_time_wh_min',
            color='brokers', color_discrete_map=BROKER_COLORS,
            title="Tiempo Mediano de Resolución por Broker"
        )
        fig_comp_b.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_comp_b = add_reference_line(fig_comp_b, df_comp_broker['res_time_wh_min'].mean(), orientation='v')
        fig_comp_b = apply_bdi_theme(fig_comp_b)
        fig_comp_b.update_layout(xaxis_title="Minutos (Mediana) en Horario Laboral", yaxis_title="Broker", showlegend=False)
        st.plotly_chart(fig_comp_b, **ANCHO)

    with col_c2:
        df_comp_tier = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median().reset_index()

        fig_comp_t = px.bar(
            df_comp_tier, x='FRT_min', y='tier', orientation='h', text='FRT_min',
            color='tier', color_discrete_map=TIER_COLORS, category_orders={'tier': TIERS},
            title="SLA de Facto: FRT Mediano por Patrimonio"
        )
        fig_comp_t.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_comp_t = add_reference_line(fig_comp_t, df_comp_tier['FRT_min'].mean(), orientation='v')
        fig_comp_t = apply_bdi_theme(fig_comp_t)
        fig_comp_t.update_layout(xaxis_title="Minutos (Mediana)", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_comp_t, **ANCHO)

    st.caption("🟡 La línea punteada dorada marca el promedio del grupo. Los tiempos usan **mediana**: "
               "unas pocas conversaciones que quedan abiertas varios días vuelven engañoso el promedio simple.")
