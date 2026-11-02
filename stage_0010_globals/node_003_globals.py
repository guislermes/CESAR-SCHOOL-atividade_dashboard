
from enum import Enum
from pathlib import Path
import pandas as pd
import node_002_scrape


# =============================================================================
# CTTU — catálogo de câmeras
# =============================================================================

def camera_snapshot_url(codigo: int | str) -> str:
    """URL JPEG snapshot CTTU para um Codigo de câmera."""
    return (
        f"{node_002_scrape.URL.rstrip('/')}"
        f"/Index?handler=Snapshot&Codigo={int(codigo)}"
    )


CAMERAS_JSON = (
    Path(__file__).parent / "EXPORT" / "v001" / "cameras_recife_27_10_2026.json"
)
# DataFrame: index=key textual, colunas id_camera + url snapshot
DF_CAMERAS = pd.read_json(CAMERAS_JSON, orient="index")
DF_CAMERAS.columns = ["id_camera"]
DF_CAMERAS.index.name = "key"
DF_CAMERAS["url"] = DF_CAMERAS["id_camera"].map(camera_snapshot_url)


# =============================================================================
# VISION — detector ônibus (stage_0021 / 0031 / 0070)
# =============================================================================

_ROOT = Path(__file__).resolve().parent.parent

YOLO_WEIGHTS = _ROOT / "stage_0021_vision" / "yolo11n.pt"

BUS_CLASS_NAME = "bus"  # classe principal no predict filtrado
# COCO: "train" também conta como alvo p/ overlay / filtro
BUS_CLASS_NAMES = ("bus", "train")

BUS_CONF_DEFAULT = 0.15  # conf mínima do bbox (0–1)
# True → predict todas classes COCO (debug); GIF overlay só em BUS_CLASS_NAMES
VISION_DEBUG_ALL_CLASSES = True

SMOKE_EXPORT = _ROOT / "stage_0021_vision" / "EXPORT" / "v001"
BENCH_EXPORT = _ROOT / "stage_0070_streamlit" / "EXPORT" / "v001"


# =============================================================================
# SNAPSHOT HTTP — httpx Async
# layout: _fetch_snapshots_run | widget: fetch_async | bench: node_005
# Bench (9 cams): GAP=0.15 + WORKERS=6 → ~1.8s wall / 0×429
# =============================================================================

SNAPSHOT_TIMEOUT_S = 30  # timeout total httpx por request
SNAPSHOT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
# Pacer entre starts de fetch (Serttel sem doc de rate limit)
SNAPSHOT_FETCH_GAP_S = 0.15
# Retries após HTTP 429 (honra header Retry-After se existir)
SNAPSHOT_429_RETRIES = 2


class OverlayAnchor(str, Enum):
    """Lado do bbox onde a arte (GIF/PNG) é ancorada."""

    TOP = "top"
    RIGHT = "right"
    LEFT = "left"
    BOTTOM = "bottom"


OVERLAY_ASSETS_DIR = _ROOT / "stage_0031_overlay" / "assets"
OVERLAY_ANCHOR = OverlayAnchor.TOP
OVERLAY_SIZE_FRAC = 0.45  # tamanho da arte ≈ fração do lado do bbox
OVERLAY_MARGIN_PX = 4  # folga em px entre arte e borda do bbox
OVERLAY_IMAGE_EXTS = (".gif", ".png", ".webp")

# -----------------------------------------------------------------------------
# SHARED — cores + fontes + botões
# -----------------------------------------------------------------------------

STYLE_BG = "#eef3f2"  # fundo página (.stApp, shell multicam)
STYLE_INK = "#0f2a36"  # h1 "Trânsito Recife" (HOME)
STYLE_MUTE = STYLE_INK  # secundário (= INK nesta build)
STYLE_MULTICAM_TEXT = STYLE_INK  # texto MULTICAM (= Trânsito Recife)
STYLE_ACCENT = "#2c7a9b"  # pin brand / highlights
STYLE_LINE = "#cfdcdd"  # borda glass / tiles
STYLE_IDLE = "#e9f0eb"  # placeholder loading tile
STYLE_SHADOW = "0 8px 24px rgba(15, 42, 54, 0.1)"
STYLE_PANEL = "rgba(255, 255, 255, 0.92)"  # glass brand / chip / containers

STYLE_FONT_DISPLAY = "Helvetica, Arial, sans-serif"
STYLE_FONT_UI = "Helvetica, Arial, sans-serif"
STYLE_FONT_WEIGHT_TITLE = 700
STYLE_FONT_WEIGHT_UI = 400

# st.button Voltar + pager — visual = card brand
STYLE_BACK_LABEL = "← Voltar ao menu principal"
STYLE_BUTTON_BG = STYLE_PANEL
STYLE_BUTTON_FG = STYLE_MULTICAM_TEXT
STYLE_BUTTON_BORDER = STYLE_LINE

# -----------------------------------------------------------------------------
# PAGE HOME — HTML iframe (AppVisuals.build_map_html) — LAYOUT LOCK
# -----------------------------------------------------------------------------

STYLE_TITLE = "CESAR-SCHOOL"
STYLE_SUBTITLE = "Engenharia e Análise de Dados - Guilherme Sarinho"
# escala do card brand (box + h1 + sub + Data/Hora + pin)
STYLE_HOME_BRAND_SCALE = 1.12

STYLE_MAP_HINT = "Clique numa região do mapa para ver as câmeras"

# rail esquerdo: brand em cima + Sobre embaixo | mapa à direita
STYLE_HOME_ABOUT_TITLE = "Análise e Olhar"

# About — 5W2H (knobs). BODY monta na ordem. Ajuste topico a topico.
# Fontes: 120 cams (out/2026), 6 zonas, YOLO11n + overlay GIF.
STYLE_HOME_ABOUT_WHAT = (
    "Dashboard para mostrar skills em Streamlit tendo como objeto o trânsito do Recife, "
    "desenvolvido na disciplina Visualização de Dados. O protótipo reúne mapa interativo "
    "por zona, grade multicâmera e a implementação de um modelo pré-treinado para "
    "detecção de componentes do ambiente, dando especial atenção à detecção de ônibus."
)
STYLE_HOME_ABOUT_FOR_WHOM = (
    "Material open source com fins acadêmicos, voltado a quem vive o trânsito do Recife, "
    "a capital mais congestionada do Brasil em 2025 (TomTom Traffic Index: 64,7%)."
)
STYLE_HOME_ABOUT_WHY = (
    "O problema é mensurável e urgente. Em 2024, a CTTU registrou 159 mortes no trânsito "
    "do Recife, o pior número desde 2017 (alta de cerca de 10%); pedestres e motociclistas "
    "somaram 86% das vítimas (Relatório Preliminar / BIGRS). No congestionamento, a TomTom "
    "estima cerca de 130 horas perdidas no horário de pico em 2025. O projeto organiza o "
    "monitoramento por zona e coloca a visão computacional no centro: ela pode ser "
    "customizada para mapear equipamentos públicos, apoiar a segurança viária e medir "
    "gargalos de infraestrutura."
)
STYLE_HOME_ABOUT_WHERE = (
    "Recife, nas zonas Centro, Norte, Noroeste, Oeste, Sudoeste e Sul, conectadas ao "
    "catálogo público de câmeras da Autarquia de Trânsito e Transporte Urbano (CTTU)."
)
STYLE_HOME_ABOUT_WHEN = (
    "Projeto realizado entre 26/10/2026 e 02/11/2026."
)
STYLE_HOME_ABOUT_HOW_MUCH = (
    "120 câmeras, 6 zonas e grade 3×3 por página. Escala de protótipo, sem custo de API própria."
)
STYLE_HOME_ABOUT_HOW = (
    "O Streamlit conectado faz requisição à CTTU; o layout interativo mostra a "
    "organização das câmeras por zona. A partir do carregamento das câmeras, o YOLO "
    "é aplicado aos snapshots. GIFs dummy inseridos sobre os ônibus demonstram que é "
    "possível inserir labels customizados sobre o material gerado e que, se aprimorado, "
    "pode gerar valor tanto no mercado quanto na sociedade."
)

STYLE_HOME_ABOUT_BODY = (
    f"O quê: {STYLE_HOME_ABOUT_WHAT}\n\n"
    f"Para quem: {STYLE_HOME_ABOUT_FOR_WHOM}\n\n"
    f"Por quê: {STYLE_HOME_ABOUT_WHY}\n\n"
    f"Onde: {STYLE_HOME_ABOUT_WHERE}\n\n"
    f"Quando: {STYLE_HOME_ABOUT_WHEN}\n\n"
    f"Quanto: {STYLE_HOME_ABOUT_HOW_MUCH}\n\n"
    f"Como: {STYLE_HOME_ABOUT_HOW}"
)
STYLE_HOME_ABOUT_WIDTH_PX = 252  # --rail-width / --about-width no CSS

STYLE_GLASS_BLUR_PX = 12
STYLE_RADIUS_PX = 14

# fundo do map-card = degradê azul (sem inland verde / sem label oceano)
STYLE_MAP_SEA_STOPS = ("#8AD3D4", "#2F8AAE", "#0C3A66")
# token legado de terra (ainda exposto em --inland no theme; mapa usa SEA)
STYLE_MAP_LAND = "#BFD0C6"

STYLE_ZONE_COLORS = {
    "centro": "#C2503A",
    "norte": "#2C7A9B",
    "noroeste": "#5B8C3E",
    "oeste": "#8A5DB0",
    "sudoeste": "#D79A1E",
    "sul": "#1F9E8A",
    "indeterminado": "#7C8B93",
}
STYLE_ZONE_COLOR_LIST = list(STYLE_ZONE_COLORS.values())

STYLE_HOME_DATE_LABEL = "Data"
STYLE_HOME_TIME_LABEL = "Hora"
STYLE_HOME_DATE_FMT = "%d/%m/%Y"
STYLE_HOME_TIME_FMT = "%H:%M:%S"

# -----------------------------------------------------------------------------
# PAGE MULTICAM — node_004_layout — LAYOUT LOCK
# rail: Voltar + título + status
# frame: quadro branco status + grade 3×3 + pager
# pipeline: fetch JPEG async → paint cru → YOLO → paint anotado
# -----------------------------------------------------------------------------

STYLE_ZONE_PAGE_TITLE = "Monitoramento do {zona} da cidade"
STYLE_FONT_SIZE_TITLE_REM = 1.05
STYLE_FONT_SIZE_SUB_REM = 0.78

STYLE_PAGER_PREV = "← Anterior"
STYLE_PAGER_NEXT = "Próxima →"

STYLE_VISION_SPINNER = "Carregando câmeras…"
STYLE_MULTICAM_LOADING = "Carregando câmeras…"  # alias legado (= FETCH_LOADING)

# status rail + quadro branco — fase snapshot CTTU (httpx async)
STYLE_FETCH_LOADING = "Carregando câmeras…"
STYLE_FETCH_CONTACTING = "Contactando servidores…"
STYLE_FETCH_CONNECTED = "Conectada"
# enquanto fetch roda: alterna LOADING ↔ CONTACTING a cada N segundos
STYLE_FETCH_STATUS_INTERVAL_S = 2.0

# status rail + quadro branco — fase YOLO (após snapshots na grade)
STYLE_DETECT_LOADING = "Carregando detecção…"
STYLE_DETECT_DONE = "Detecção carregada"

STYLE_GRID_COLS = 3
STYLE_PANEL_PAGE_SIZE = 9  # tiles / página (= n do bench default)
STYLE_GRID_TILE_VH = 26
STYLE_GRID_GAP = "small"
# concurrency httpx (bench node_005: 6 beats 9 em wall+0×429)
STYLE_MULTICAM_WORKERS = 6
STYLE_LIST_ITEM_GAP_REM = 0.4  # margem entre tiles

STYLE_FONT_SIZE_CHIP_REM = 0.72
STYLE_CHIP_BG = STYLE_PANEL
STYLE_CHIP_FG = STYLE_MULTICAM_TEXT  # só nome da rua no tile

# SVG placeholder até st.image pintar
STYLE_ICON_PX = 72
