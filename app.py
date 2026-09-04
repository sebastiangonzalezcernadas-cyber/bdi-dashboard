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
    if pd.isna(val): return np.nan
    if isinstance(val, (int, float)): return float(val)
    try:
        parts = str(val).split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 60 + m + (s / 60.0)
        if len(parts) == 2:
            m, s = map(int, parts)
            return m + (s / 60.0)
    except Exception:
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

def procesar(df):
    """Normaliza y deriva columnas. Se aplica UNA sola vez sobre Drive + subidas manuales."""
    if df.empty:
        return df

    if 'contactName' in df.columns:
        df = df[~df['contactName'].isin(EXCLUIR_CONTACTOS)]

    # Deduplicación por chat: si un mes se solapa con otro archivo, no se cuenta dos veces.
    if 'chatId' in df.columns:
        df = df.drop_duplicates(subset=['chatId'], keep='last')
    else:
        df = df.drop_duplicates(subset=[c for c in ['contactNumber', 'createdAt'] if c in df.columns])

    df = df.reset_index(drop=True)

    df['createdAt_dt'] = pd.to_datetime(col_segura(df, 'createdAt'), errors='coerce')
    df['firstSentMessageAt_dt'] = pd.to_datetime(col_segura(df, 'firstSentMessageAt'), errors='coerce')

    df['fecha_corta'] = df['createdAt_dt'].dt.date
    df['mes_nombre'] = df['createdAt_dt'].dt.month.map(MESES_ES_MAP)
    df['mes_nombre'] = df['mes_nombre'].fillna(df['mes_archivo'])

    df['dia_semana'] = df['createdAt_dt'].dt.day_name().map(DAY_MAP)
    df['hora'] = df['createdAt_dt'].dt.hour
    df['hora_30m'] = df['createdAt_dt'].dt.floor('30min').dt.strftime('%H:%M')

    df['FRT_min'] = (df['firstSentMessageAt_dt'] - df['createdAt_dt']).dt.total_seconds() / 60.0
    df['resp_time_wh_min'] = col_segura(df, 'workingHoursResponseTime').apply(time_str_to_minutes)
    df['res_time_wh_min'] = col_segura(df, 'workingHoursResolutionTime').apply(time_str_to_minutes)

    df['brokers'] = col_segura(df, 'tags').apply(extract_brokers)
    df['tier'] = col_segura(df, 'tags').apply(extract_tier)

    if 'chatId' not in df.columns:
        df['chatId'] = np.arange(len(df))
    if 'user' not in df.columns:
        df['user'] = 'Sin Asignar'
    df['user'] = df['user'].fillna('Sin Asignar')

    df['isNewContact'] = col_segura(df, 'isNewContact').fillna(False).astype(bool)
    df['resolvedByInactivity'] = col_segura(df, 'resolvedByInactivity').fillna(False).astype(bool)

    return df

# ---------------------------------------------------------
# PANEL DE CONTROL LATERAL
# ---------------------------------------------------------
st.sidebar.markdown("### ⚙️ Panel de Control")

def marcar_sincronizacion():
    st.session_state["_forzar_sync"] = True
    st.cache_data.clear()

st.sidebar.button("🔄 Sincronizar datos de Google Drive",
                  on_click=marcar_sincronizacion, use_container_width=True)

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

df_raw = procesar(pd.concat(frames, ignore_index=True)) if frames else pd.DataFrame()

# ---------------------------------------------------------
# DIAGNÓSTICO (clave para saber si el mes nuevo entró o no)
# ---------------------------------------------------------
todos_los_logs = log_listado + log_descarga + log_lectura + log_upload
hay_errores = any(nivel == "error" for nivel, _ in todos_los_logs)

with st.sidebar.expander("🩺 Diagnóstico de carga", expanded=hay_errores):
    for nivel, msg in todos_los_logs:
        if nivel == "ok":
            st.success(msg, icon="✅")
        elif nivel == "warn":
            st.warning(msg, icon="⚠️")
        else:
            st.error(msg, icon="🚫")

if df_raw.empty:
    st.error("No se encontraron datos para procesar. Abrí **🩺 Diagnóstico de carga** en la barra lateral "
             "para ver exactamente qué archivo falló, o cargá las planillas manualmente.")
    st.stop()

resumen_archivos = df_raw.groupby('archivo_origen').agg(
    Filas=('archivo_origen', 'size'),
    Desde=('createdAt_dt', 'min'),
    Hasta=('createdAt_dt', 'max')
).reset_index()
resumen_archivos['Desde'] = resumen_archivos['Desde'].dt.strftime('%d/%m/%Y')
resumen_archivos['Hasta'] = resumen_archivos['Hasta'].dt.strftime('%d/%m/%Y')
resumen_archivos.columns = ['Planilla', 'Filas', 'Desde', 'Hasta']

st.sidebar.success(f"📁 **{len(resumen_archivos)} planillas activas**")
with st.sidebar.expander("📄 Cobertura por planilla"):
    st.dataframe(resumen_archivos, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# FILTROS DINÁMICOS
# ---------------------------------------------------------
st.sidebar.markdown("### 🔎 Filtros de Búsqueda")
meses_disponibles = [m for m in MESES_ORDEN if m in set(df_raw['mes_nombre'].dropna())]
meses_disponibles += sorted(set(df_raw['mes_nombre'].dropna()) - set(MESES_ORDEN))
meses_sel = st.sidebar.multiselect("Mes:", meses_disponibles, default=meses_disponibles)

asesores_disponibles = sorted(df_raw['user'].dropna().unique())
asesores_sel = st.sidebar.multiselect("Asesor:", asesores_disponibles, default=asesores_disponibles)

df = df_raw.copy()
if meses_sel: df = df[df['mes_nombre'].isin(meses_sel)]
if asesores_sel: df = df[df['user'].isin(asesores_sel)]

if df.empty:
    st.warning("Los filtros actuales no devuelven ningún chat. Ampliá la selección de meses o asesores.")
    st.stop()

# ---------------------------------------------------------
# HEADER PRINCIPAL Y KPIs
# ---------------------------------------------------------
ultimo_dato = df_raw['createdAt_dt'].max()
ultimo_dato_txt = ultimo_dato.strftime('%d/%m/%Y %H:%M') if pd.notna(ultimo_dato) else "s/d"

st.markdown(f"""
<div class="bdi-header">
    <h1>📈 Dashboard de Gestión de Mensajería</h1>
    <p>BDI Consultora — Consolidado analítico de conversaciones, rendimiento operativo por asesor y distribución patrimonial.</p>
    <span class="bdi-badge">Último chat en la base: {ultimo_dato_txt}</span>
    <span class="bdi-badge">Tablero generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
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
        df_mes['orden'] = df_mes['mes_nombre'].apply(
            lambda m: meses_disponibles.index(m) if m in meses_disponibles else 99)
        df_mes = df_mes.sort_values('orden')
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
    st.plotly_chart(fig_tier_broker, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: CLIENTES
# ---------------------------------------------------------
with tab3:
    section_header("RANKING", "Top 10 Clientes con Mayor Interacción")
    df_clients_all = df.groupby(['contactName', 'contactNumber']).agg(
        Total_Chats=('chatId', 'count'),
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
    st.plotly_chart(fig_top10, use_container_width=True)

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
        use_container_width=True, hide_index=True, height=420
    )

# ---------------------------------------------------------
# TAB 4: ACTIVIDAD POR USUARIO Y EFICIENCIA OPERATIVA
# ---------------------------------------------------------
with tab4:
    section_header("EFICIENCIA", "Desempeño Operativo por Asesor")

    total_general_chats = len(df)

    if not df['createdAt_dt'].dropna().empty:
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
    st.caption("Excluye fines de semana · Horario comercial (8 a 18 hs) · El color indica volumen absoluto; el porcentaje, el peso relativo del día.")

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
            colorscale=[[0.0, '#F4F9F6'], [0.5, '#8FBF74'], [1.0, '#0F5132']],
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

    df_tier_frt_kpi = df[df['tier'] != 'Sin Etiqueta Monto'].groupby('tier')['FRT_min'].median().dropna()
    segmento_mas_lento = df_tier_frt_kpi.idxmax() if not df_tier_frt_kpi.empty else "—"

    kf1, kf2, kf3, kf4 = st.columns(4)
    kf1.metric("Ratio Global de Fricción", f"{ratio_global:.2f} chats/cliente" if pd.notna(ratio_global) else "s/d", help="Promedio de chats por cliente único.")
    kf2.metric("Resolución Promedio", f"{res_time_prom:.0f} min" if pd.notna(res_time_prom) else "s/d", help="Tiempo promedio de resolución en horario laboral.")
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
        fig_fric_b.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Broker", showlegend=False)
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
        fig_fric_t.update_layout(xaxis_title="Promedio de Chats por Cliente", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_fric_t, use_container_width=True)

    divider()

    section_header(
        "COMPLEJIDAD OPERATIVA", "Análisis de Tiempos de Atención (SLA)",
        subtitle="Cruza tiempos de resolución y de primera respuesta con plataformas y patrimonio."
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
            color='tier', color_discrete_map=TIER_COLORS, category_orders={'tier': TIERS},
            title="SLA de Facto: FRT Mediano por Patrimonio"
        )
        fig_comp_t.update_traces(texttemplate='%{text:.1f} min', textposition='outside', cliponaxis=False)
        fig_comp_t = add_reference_line(fig_comp_t, df_comp_tier['FRT_min'].mean(), orientation='v')
        fig_comp_t = apply_bdi_theme(fig_comp_t)
        fig_comp_t.update_layout(xaxis_title="Minutos (Mediana)", yaxis_title="Segmento Patrimonial", showlegend=False)
        st.plotly_chart(fig_comp_t, use_container_width=True)

    st.caption("🟡 La línea punteada dorada marca el promedio del grupo.")
