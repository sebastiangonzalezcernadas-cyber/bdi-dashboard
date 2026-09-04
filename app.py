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
import inspect
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
MESES_ORDEN = [MESES_ES_MAP[m] for m in range(1, 13)]
NOMBRE_MES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
              7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

# Escala del mapa de calor en verdes BDI (de papel a verde institucional).
BDI_HEATSCALE = [
    [0.00, '#FFFFFF'], [0.12, '#EDF7F1'], [0.28, '#CFE9DA'], [0.45, '#9FD3B6'],
    [0.62, '#5FBB8C'], [0.78, '#2FA66B'], [0.90, '#157347'], [1.00, '#0B3D27']
]

# Etiquetas comerciales que no son broker ni segmento patrimonial.
SERVICIOS = ['Membresia', 'Agro', 'Consultoria', 'Potencial Cliente', '+1 Cuenta']
SERVICIO_COLORS = {'Membresia': '#0F5132', 'Agro': '#8FBF74', 'Consultoria': '#3AAFB9',
                   'Potencial Cliente': '#C9A227', '+1 Cuenta': '#2FA66B'}

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

def extract_servicios(tag_str):
    if pd.isna(tag_str):
        return []
    tags = [t.strip().lower() for t in str(tag_str).split(',')]
    return [s for s in SERVICIOS if any(s.lower() == t or s.lower() in t for t in tags)]

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
# CAPA 1 · LISTADO DE ARCHIVOS EN DRIVE
# -----------------------------------------------------------
@st.cache_data(ttl=120, show_spinner=False)
def listar_archivos_drive():
    """Devuelve {nombre: {'id':..., 'modified':...}} y un log de diagnóstico."""
    log, archivos = [], {}

    try:
        tiene_sa = "gcp_service_account" in st.secrets
    except Exception:
        tiene_sa = False  # No hay secrets.toml configurado

    if tiene_sa:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=creds)

            page_token = None
            while True:
                res = service.files().list(
                    q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
                    fields="nextPageToken, files(id, name, modifiedTime)",
                    pageSize=200,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                for item in res.get('files', []):
                    if item['name'].lower().endswith('.xlsx'):
                        archivos[item['name']] = {'id': item['id'], 'modified': item.get('modifiedTime')}
                page_token = res.get('nextPageToken')
                if not page_token:
                    break

            log.append(("ok", f"Drive API conectada · {len(archivos)} planillas .xlsx en la carpeta."))
            if not archivos:
                log.append(("error", "La carpeta respondió vacía. Verificá que la carpeta esté compartida con el mail de la Service Account."))
        except Exception as e:
            log.append(("error", f"Falló el listado de Drive → {type(e).__name__}: {e}"))
    else:
        log.append(("warn", "No hay credenciales `gcp_service_account` cargadas: no se detectan archivos nuevos de forma automática."))

    if not archivos:
        archivos = {n: {'id': i, 'modified': None} for n, i in ARCHIVOS_DRIVE_DIRECTOS.items()}
        log.append(("warn",
                    f"Usando la lista fija de {len(archivos)} IDs. Cualquier planilla nueva que subas a Drive "
                    "NO va a aparecer hasta agregarla a ARCHIVOS_DRIVE_DIRECTOS o configurar la Service Account."))
    return archivos, log

# -----------------------------------------------------------
# CAPA 2 · DESCARGA Y SINCRONIZACIÓN LOCAL
# -----------------------------------------------------------
def sincronizar_archivos(archivos, forzar=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    log = []

    manifest = {}
    if os.path.exists(MANIFEST_PATH) and not forzar:
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
        remoto = meta.get('modified')
        local = manifest.get(safe, {})

        al_dia = (
            es_xlsx_valido(path)
            and local.get('id') == meta['id']
            and (remoto is None or local.get('modified') == remoto)
        )
        if al_dia and not forzar:
            continue

        try:
            if os.path.exists(path):
                os.remove(path)
            resultado = gdown.download(id=meta['id'], output=path, quiet=True)
            if resultado is None or not es_xlsx_valido(path):
                if os.path.exists(path):
                    os.remove(path)
                manifest.pop(safe, None)
                log.append(("error",
                            f"«{nombre}»: la descarga falló o no devolvió un .xlsx válido. "
                            "Revisá que el archivo esté compartido como “Cualquier persona con el enlace”."))
                continue
            manifest[safe] = {
                'id': meta['id'],
                'modified': remoto,
                'descargado': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            log.append(("ok", f"«{nombre}» descargado / actualizado."))
        except Exception as e:
            log.append(("error", f"«{nombre}» → {type(e).__name__}: {e}"))

    # Limpieza: borra planillas locales que ya no están en Drive (evita meses duplicados)
    for f in glob.glob(os.path.join(DATA_DIR, "*.xlsx")):
        base = os.path.basename(f)
        if base not in esperados:
            try:
                os.remove(f)
                manifest.pop(base, None)
                log.append(("warn", f"«{base}» ya no está en la carpeta de Drive: se eliminó la copia local."))
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
    df['FRT_min'] = (df['firstSentMessageAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df.loc[df['FRT_min'] < 0, 'FRT_min'] = np.nan
    df['resp_time_min'] = col_segura(df, 'responseTime').apply(time_str_to_minutes)
    df['resp_time_wh_min'] = col_segura(df, 'workingHoursResponseTime').apply(time_str_to_minutes)
    df['res_time_min'] = col_segura(df, 'resolutionTime').apply(time_str_to_minutes)
    df['res_time_wh_min'] = col_segura(df, 'workingHoursResolutionTime').apply(time_str_to_minutes)

    # --- Etiquetas
    df['brokers'] = col_segura(df, 'tags').apply(extract_brokers)
    df['tier'] = col_segura(df, 'tags').apply(extract_tier)
    df['servicios'] = col_segura(df, 'tags').apply(extract_servicios)

    # --- Identificadores y flags
    if COL_ID not in df.columns:
        df[COL_ID] = np.arange(len(df)).astype(str)
    if 'user' not in df.columns:
        df['user'] = 'Sin Asignar'
    df['user'] = df['user'].fillna('Sin Asignar')
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

forzar = st.session_state.pop("_forzar_sync", False)
if forzar and os.path.exists(DATA_DIR):
    shutil.rmtree(DATA_DIR, ignore_errors=True)

archivos_drive, log_listado = listar_archivos_drive()
log_descarga, manifest = sincronizar_archivos(archivos_drive, forzar=forzar)
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
    st.error("No se encontraron datos para procesar. Abrí **🩺 Diagnóstico de carga** en la barra lateral "
             "para ver exactamente qué archivo falló, o cargá las planillas manualmente.")
    st.stop()

resumen_archivos = df_raw.groupby('archivo_origen').agg(
    Conversaciones=(COL_ID, 'nunique'),
    Contactos=('contactNumber', 'nunique'),
    Desde=('createdAt_dt', 'min'),
    Hasta=('createdAt_dt', 'max'),
    Periodos=('periodo', lambda s: ', '.join(sorted(s.dropna().unique())))
).reset_index()
resumen_archivos['Desde'] = resumen_archivos['Desde'].dt.strftime('%d/%m/%Y')
resumen_archivos['Hasta'] = resumen_archivos['Hasta'].dt.strftime('%d/%m/%Y')
resumen_archivos.columns = ['Planilla', 'Conversaciones', 'Contactos', 'Desde', 'Hasta', 'Períodos']

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

asesores_disponibles = sorted(df_raw['user'].dropna().unique())
asesores_sel = st.sidebar.multiselect("Asesor:", asesores_disponibles, default=asesores_disponibles)

brokers_disponibles = sorted({b for lista in df_raw['brokers'] for b in lista})
brokers_sel = st.sidebar.multiselect("Broker:", brokers_disponibles, default=brokers_disponibles,
                                     help="Un chat con varias etiquetas de broker aparece si coincide con alguna.")

df = df_raw.copy()
if periodos_sel: df = df[df['periodo'].isin(periodos_sel)]
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
kpi4.metric("FRT Mediano", f"{df['FRT_min'].median():.1f} min" if df['FRT_min'].notna().any() else "s/d")
kpi5.metric("Cierre Inactividad", f"{int(df['resolvedByInactivity'].sum()):,}")

kpi6, kpi7, kpi8, kpi9, kpi10 = st.columns(5)
kpi6.metric("Chats por Contacto", f"{ratio_chats_contacto:.2f}" if pd.notna(ratio_chats_contacto) else "s/d",
            help="Conversaciones totales dividido contactos únicos.")
kpi7.metric("Resolución Mediana", f"{df['res_time_wh_min'].median():.0f} min" if df['res_time_wh_min'].notna().any() else "s/d",
            help="Mediana del tiempo de resolución en horario laboral. Se usa mediana porque unos pocos chats de varios días distorsionan el promedio.")
kpi8.metric("Iniciados por Cliente", f"{df['startedByContact'].mean()*100:.0f}%" if len(df) else "s/d",
            help="Porcentaje de conversaciones que abrió el cliente y no el asesor.")
kpi9.metric("Sin Responder", f"{int(df['FRT_min'].isna().sum()):,}",
            help="Conversaciones sin `firstSentMessageAt`: nunca se envió un primer mensaje desde BDI.")
kpi10.metric("Días Hábiles", f"{dias_habiles_efectivos(df['createdAt_dt']):,}",
             help="Días hábiles reales de los períodos seleccionados, sin fines de semana ni feriados AR.")

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
        df_mes = df.groupby('periodo')[COL_ID].nunique().reset_index(name='Chats')
        df_mes = df_mes.sort_values('periodo')
        fig_mes = px.bar(
            df_mes, x='periodo', y='Chats', text='Chats',
            color_discrete_sequence=['#157347'], title="Evolución Mensual de Chats",
            category_orders={'periodo': periodos_disponibles}
        )
        fig_mes.update_traces(textposition='outside')
        fig_mes = apply_bdi_theme(fig_mes)
        fig_mes.update_layout(xaxis_title="Período", yaxis_title="Cantidad de Chats", xaxis=dict(tickangle=-30))
        st.plotly_chart(fig_mes, **ANCHO)

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
        st.plotly_chart(fig_dias, **ANCHO)

    if df['fecha_corta'].notna().any():
        df_diario = df.groupby('fecha_corta')[COL_ID].nunique().reset_index(name='Chats')
        fig_diario = px.line(
            df_diario, x='fecha_corta', y='Chats',
            color_discrete_sequence=['#0F5132'], title="Serie Diaria de Conversaciones"
        )
        fig_diario.update_traces(line=dict(width=2))
        fig_diario = add_reference_line(fig_diario, df_diario['Chats'].mean(), orientation='h', label='Promedio diario')
        fig_diario = apply_bdi_theme(fig_diario)
        fig_diario.update_layout(xaxis_title="Fecha", yaxis_title="Conversaciones", height=330)
        st.plotly_chart(fig_diario, **ANCHO)

    section_header("CARGA HORARIA", "Distribución de Consultas por Hora")
    df_hora = df.groupby('hora').size().reset_index(name='Chats')
    fig_hora = px.area(
        df_hora, x='hora', y='Chats', markers=True,
        color_discrete_sequence=['#3AAFB9'], title="Carga Horaria General (Franja de 0 a 23 hs)"
    )
    fig_hora.update_traces(marker=dict(size=8, color='#0F5132'), fillcolor='rgba(58,175,185,0.15)', line=dict(color='#0F5132'))
    fig_hora = apply_bdi_theme(fig_hora)
    fig_hora.update_layout(xaxis_title="Hora del día", yaxis_title="Cantidad de Chats", xaxis=dict(dtick=1))
    st.plotly_chart(fig_hora, **ANCHO)

    df_hora_30 = df[(df['hora'] >= 8) & (df['hora'] <= 18)].groupby('hora_30m').size().reset_index(name='Chats')
    fig_hora_30 = px.area(
        df_hora_30, x='hora_30m', y='Chats', markers=True,
        color_discrete_sequence=['#157347'], title="Carga Horaria Comercial (08:00 a 18:00 hs · Intervalos de 30 min)"
    )
    fig_hora_30.update_traces(marker=dict(size=8, color='#0F5132'), fillcolor='rgba(21,115,71,0.15)', line=dict(color='#0F5132'))
    fig_hora_30 = apply_bdi_theme(fig_hora_30)
    fig_hora_30.update_layout(xaxis_title="Franja horaria", yaxis_title="Cantidad de Chats", xaxis=dict(tickangle=-45))
    st.plotly_chart(fig_hora_30, **ANCHO)

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

    st.caption(f"📅 **Base de cálculo temporal:** {base_dias} días hábiles reales de los períodos seleccionados "
               "(excluye fines de semana y feriados de Argentina, y respeta meses incompletos) · Jornada de 8 hs.")

    df_user_eff = df.groupby('user').agg(
        Total_Chats=(COL_ID, 'nunique'),
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

    st.markdown("##### Resumen de Métricas de Agilidad, Volumen y Calidad")
    st.dataframe(
        df_table_eff.style.format({
            'Participación (%)': '{:.1f}%', 'FRT Mediano (Min)': '{:.1f}',
            'Chats / Día': '{:.1f}', 'Chats / Hora (8hs)': '{:.1f}',
            'Nuevos Contactos (%)': '{:.1f}%'
        }),
        column_config={
            "FRT Mediano (Min)": st.column_config.NumberColumn(help="First Response Time: minutos que tarda el asesor en responder el primer mensaje."),
            "Chats / Día": st.column_config.NumberColumn(help="Total de chats dividido la cantidad de días hábiles descontando feriados."),
            "Chats / Hora (8hs)": st.column_config.NumberColumn(help="Promedio diario dividido las 8 horas de jornada laboral."),
            "Nuevos Contactos (#)": st.column_config.NumberColumn(help="Cantidad absoluta de nuevos clientes."),
            "Nuevos Contactos (%)": st.column_config.NumberColumn(help="Porcentaje de clientes que escribieron por primera vez.")
        },
        hide_index=True, **ANCHO
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
        st.plotly_chart(fig_pie, **ANCHO)

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
    st.caption("Excluye fines de semana · Horario comercial (8 a 18 hs) · La intensidad del verde indica el volumen absoluto; el porcentaje, el peso de esa franja dentro del día.")

    df_heatmap = df[(df['hora'] >= 8) & (df['hora'] <= 18) & (~df['dia_semana'].isin(['Sábado', 'Domingo']))]

    if not df_heatmap.empty:
        heatmap_counts = df_heatmap.groupby(['dia_semana', 'hora'])[COL_ID].nunique().reset_index(name='Chats')
        totals_per_day = heatmap_counts.groupby('dia_semana')['Chats'].transform('sum')
        heatmap_counts['Porcentaje'] = (heatmap_counts['Chats'] / totals_per_day * 100).round(1)

        horas = list(range(8, 19))
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
        st.info("No hay chats registrados en horario comercial para la selección actual.")

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
