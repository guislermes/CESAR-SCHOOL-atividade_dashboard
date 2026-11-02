"""
node_003 — knobs visuais + shell HTML/CSS v029.

LAYOUT LOCK (home + multicam) — ver .cursor/rules/layout-lock.mdc
Refs: __visuals__/ref_app.jpg + __visuals__/hmtl_ref/
Catálogo + STYLE_*: stage_0010_globals.
"""

from __future__ import annotations

import base64
import html
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components

_ROOT = Path(__file__).resolve().parents[1]
_GLOBALS = _ROOT / "stage_0010_globals"
if str(_GLOBALS) not in sys.path:
    sys.path.insert(0, str(_GLOBALS))

import node_003_globals as g

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
VISUALS_DIR = Path(__file__).resolve().parent / "__visuals__"
HTML_CSS_DIR = VISUALS_DIR / "html_css" / "v029"
HTML_CSS_STYLES = HTML_CSS_DIR / "styles.css"
MAP_COMPONENT_DIR = HTML_CSS_DIR / "map_component"

_map_pick = components.declare_component(
    "cesar_map_pick",
    path=str(MAP_COMPONENT_DIR),
)
CAMERAS_BY_ZONE_JSON = VISUALS_DIR / "cameras_recife_por_zona.json"
CAMERA_OFFLINE = VISUALS_DIR / "camera_error_v001.jpg"
REF_APP = VISUALS_DIR / "ref_app.jpg"
REF_MAP_HTML = VISUALS_DIR / "hmtl_ref" / "Recife por zonas.html"
CAM_ICON_SVG = VISUALS_DIR / "hmtl_ref" / "icone_camera_video.svg"

# ---------------------------------------------------------------------------
# COPY / BRAND  ← stage_0010 STYLE_*
# ---------------------------------------------------------------------------
TITLE = g.STYLE_TITLE
SUBTITLE = g.STYLE_SUBTITLE
MAP_HINT = g.STYLE_MAP_HINT
HOME_ABOUT_TITLE = g.STYLE_HOME_ABOUT_TITLE
HOME_ABOUT_BODY = g.STYLE_HOME_ABOUT_BODY
HOME_ABOUT_WIDTH_PX = int(g.STYLE_HOME_ABOUT_WIDTH_PX)
FEED_BACK_LABEL = g.STYLE_BACK_LABEL
ZONE_PAGE_TITLE = g.STYLE_ZONE_PAGE_TITLE
PAGER_PREV_LABEL = g.STYLE_PAGER_PREV
PAGER_NEXT_LABEL = g.STYLE_PAGER_NEXT
VISION_SPINNER = g.STYLE_VISION_SPINNER
MULTICAM_LOADING = g.STYLE_MULTICAM_LOADING
HOME_DATE_LABEL = g.STYLE_HOME_DATE_LABEL
HOME_TIME_LABEL = g.STYLE_HOME_TIME_LABEL
HOME_DATE_FMT = g.STYLE_HOME_DATE_FMT
HOME_TIME_FMT = g.STYLE_HOME_TIME_FMT
# ---------------------------------------------------------------------------
# LAYOUT / UX KNOBS  ← stage_0010 STYLE_*
# ---------------------------------------------------------------------------
PANEL_PAGE_SIZE = int(g.STYLE_PANEL_PAGE_SIZE)
GRID_COLS = int(g.STYLE_GRID_COLS)
GRID_GAP = str(g.STYLE_GRID_GAP)
SHELL_HEIGHT_PX = 630
MAP_HEIGHT_PX = 630  # home mapa altura (clique/geo LOCK)
CAM_ICON_PX = int(g.STYLE_ICON_PX)
THUMB_WIDTH_PX = 160  # legado
GRID_TILE_VH = float(g.STYLE_GRID_TILE_VH)
FEED_WIDTH_VW = 60
FEED_MAX_HEIGHT_VH = 65
MAP_VIEWBOX = "0 0 600 700"
MAP_SMOOTH_AMP = 9
ZONE_CLICK_SELECTS_ONE = True
MAP_HEIGHT_ZONE_PX = 340  # legado

# ---------------------------------------------------------------------------
# STYLE tokens (CSS / chips)
# ---------------------------------------------------------------------------
STYLE_BG = g.STYLE_BG
STYLE_INK = g.STYLE_INK
STYLE_MUTE = g.STYLE_MUTE
STYLE_MULTICAM_TEXT = g.STYLE_MULTICAM_TEXT
STYLE_ACCENT = g.STYLE_ACCENT
STYLE_LINE = g.STYLE_LINE
STYLE_PANEL = g.STYLE_PANEL
STYLE_IDLE = g.STYLE_IDLE
STYLE_SHADOW = g.STYLE_SHADOW
STYLE_FONT_DISPLAY = g.STYLE_FONT_DISPLAY
STYLE_FONT_UI = g.STYLE_FONT_UI
STYLE_FONT_SIZE_TITLE_REM = float(g.STYLE_FONT_SIZE_TITLE_REM)
STYLE_FONT_SIZE_SUB_REM = float(g.STYLE_FONT_SIZE_SUB_REM)
STYLE_FONT_SIZE_CHIP_REM = float(g.STYLE_FONT_SIZE_CHIP_REM)
STYLE_FONT_WEIGHT_TITLE = int(g.STYLE_FONT_WEIGHT_TITLE)
STYLE_FONT_WEIGHT_UI = int(g.STYLE_FONT_WEIGHT_UI)
STYLE_RADIUS_PX = int(g.STYLE_RADIUS_PX)
STYLE_GLASS_BLUR_PX = int(g.STYLE_GLASS_BLUR_PX)
STYLE_LIST_ITEM_GAP_REM = float(g.STYLE_LIST_ITEM_GAP_REM)
STYLE_CHIP_BG = g.STYLE_CHIP_BG
STYLE_CHIP_FG = g.STYLE_CHIP_FG
STYLE_BUTTON_BG = g.STYLE_BUTTON_BG
STYLE_BUTTON_FG = g.STYLE_BUTTON_FG
STYLE_BUTTON_BORDER = g.STYLE_BUTTON_BORDER
STYLE_MAP_SEA_STOPS = tuple(g.STYLE_MAP_SEA_STOPS)

# ---------------------------------------------------------------------------
# CORES DE ZONA ← STYLE_ZONE_COLORS
# ---------------------------------------------------------------------------
ZONE_COLORS = dict(g.STYLE_ZONE_COLORS)

ZONA_JSON_TO_LABEL = {
    "centro": "Centro",
    "norte": "Norte",
    "noroeste": "Noroeste",
    "oeste": "Oeste",
    "sudoeste": "Sudoeste",
    "sul": "Sul",
    "indeterminado": "Indeterminado",
}

ZONA_RPA = {
    "centro": "RPA 1",
    "norte": "RPA 2",
    "noroeste": "RPA 3",
    "oeste": "RPA 4",
    "sudoeste": "RPA 5",
    "sul": "RPA 6",
    "indeterminado": "Sem localização segura",
}

# Ordem de desenho (sombra → frente): sul por cima no litoral
ZONA_MAP_ORDER = ("norte", "noroeste", "centro", "oeste", "sudoeste", "sul")

ZONA_ORDER = (
    "norte",
    "centro",
    "noroeste",
    "oeste",
    "sudoeste",
    "sul",
    "indeterminado",
)

# Geometria esquemática (viewBox 600×700) — ref hmtl_ref
# p = vértices "x,y …"; l = âncora do rótulo [x, y]
RPA_ZONES = {
    "norte": {
        "p": "300,40 430,70 450,170 380,215 300,200 270,130",
        "l": (370, 130),
    },
    "noroeste": {
        "p": "270,130 130,110 110,220 170,300 270,290 340,290 300,200",
        "l": (205, 205),
    },
    "centro": {
        "p": "300,200 380,215 450,170 505,235 490,310 400,320 340,290",
        "l": (432, 262),
    },
    "oeste": {
        "p": "170,300 270,290 340,290 400,320 380,370 300,420 190,430 80,390 100,330",
        "l": (235, 360),
    },
    "sudoeste": {
        "p": "190,430 300,420 380,370 385,460 410,570 340,640 220,600 150,510",
        "l": (295, 520),
    },
    "sul": {
        "p": "400,320 490,310 520,400 545,520 565,640 470,665 410,570 385,460 380,370",
        "l": (470, 500),
    },
}

SEA_RING = "300,-10 270,40 400,70 420,170 475,235 460,310 490,400 515,520 535,640 440,665 600,720 610,-10"

# Compat: aliases antigos usados em código legado
ZONE_PALETTE = list(g.STYLE_ZONE_COLOR_LIST)
ZONA_JSON_TO_PALETTE_INDEX = {k: i for i, k in enumerate(ZONE_COLORS)}
MAP_LAND = g.STYLE_MAP_LAND
RPA_POLYGONS = {k: v["p"] for k, v in RPA_ZONES.items()}
ZONA_PIN_XY = {k: v["l"] for k, v in RPA_ZONES.items()}


def _parse_pts(s: str) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for part in s.split():
        x_s, y_s = part.split(",")
        out.append((float(x_s), float(y_s)))
    return out


def _rnd(a: tuple[float, float], b: tuple[float, float]) -> float:
    s = math.sin(a[0] * 12.9898 + a[1] * 78.233 + b[0] * 37.719 + b[1] * 4.581) * 43758.5453
    return s - math.floor(s) - 0.5


def _edge(
    a: tuple[float, float],
    b: tuple[float, float],
    amp: float,
) -> list[tuple[float, float]]:
    forward = a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])
    p, q = (a, b) if forward else (b, a)
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy) or 1.0
    m = min(amp, length * 0.14)
    samples = [
        (0.25, _rnd(p, q)),
        (0.5, _rnd(q, p) * 1.2),
        (0.75, _rnd((p[1], p[0]), (q[1], q[0]))),
    ]
    pts = [
        (
            p[0] + dx * t - dy / length * o * m * 2,
            p[1] + dy * t + dx / length * o * m * 2,
        )
        for t, o in samples
    ]
    return pts if forward else list(reversed(pts))


def smooth_path(verts: list[tuple[float, float]], amp: float = MAP_SMOOTH_AMP) -> str:
    """Path SVG fechado com bordas suaves (algoritmo da ref hmtl_ref)."""
    if len(verts) < 3:
        return ""
    widened: list[tuple[float, float]] = []
    n0 = len(verts)
    for i, a in enumerate(verts):
        widened.append(a)
        if amp:
            widened.extend(_edge(a, verts[(i + 1) % n0], amp))
    n = len(widened)
    f = lambda x: f"{x:.1f}"
    d = f"M{f(widened[0][0])},{f(widened[0][1])}"
    for i in range(n):
        p0 = widened[(i - 1 + n) % n]
        p1 = widened[i]
        p2 = widened[(i + 1) % n]
        p3 = widened[(i + 2) % n]
        d += (
            f"C{f(p1[0] + (p2[0] - p0[0]) / 6)},{f(p1[1] + (p2[1] - p0[1]) / 6)} "
            f"{f(p2[0] - (p3[0] - p1[0]) / 6)},{f(p2[1] - (p3[1] - p1[1]) / 6)} "
            f"{f(p2[0])},{f(p2[1])}"
        )
    return d + "Z"


class AppVisuals:
    @classmethod
    def load_zones(cls) -> dict[str, dict[str, int]]:
        raw = json.loads(CAMERAS_BY_ZONE_JSON.read_text(encoding="utf-8"))
        return {
            str(z): {str(k): int(v) for k, v in cams.items()}
            for z, cams in raw.items()
        }

    @classmethod
    def zones_filtered(
        cls,
        catalog_keys: set[str] | list[str],
    ) -> dict[str, dict[str, int]]:
        allowed = set(catalog_keys)
        out: dict[str, dict[str, int]] = {}
        for zona, cams in cls.load_zones().items():
            kept = {k: i for k, i in cams.items() if k in allowed}
            if kept:
                out[zona] = kept
        return out

    @classmethod
    def zone_color(cls, zona_key: str) -> str:
        return ZONE_COLORS.get(zona_key, ZONE_COLORS["indeterminado"])

    @classmethod
    def zone_label(cls, zona_key: str) -> str:
        return ZONA_JSON_TO_LABEL.get(zona_key, zona_key)

    @classmethod
    def zone_rpa(cls, zona_key: str) -> str:
        return ZONA_RPA.get(zona_key, "")

    @classmethod
    def zone_page_title(cls, zona_key: str) -> str:
        return ZONE_PAGE_TITLE.format(zona=cls.zone_label(zona_key))

    @classmethod
    def offline_path(cls) -> Path:
        return CAMERA_OFFLINE

    @classmethod
    def offline_uri(cls) -> str:
        return CAMERA_OFFLINE.resolve().as_uri()

    @classmethod
    def cam_icon_data_uri(cls) -> str:
        raw = CAM_ICON_SVG.read_text(encoding="utf-8")
        raw = re.sub(r"<metadata>.*?</metadata>", "", raw, flags=re.DOTALL)
        b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{b64}"

    @classmethod
    def cam_loading_icon_html(cls, *, size_px: int | None = None) -> str:
        """SVG placeholder no tile até o frame vision chegar."""
        px = int(size_px or CAM_ICON_PX)
        return (
            f'<div class="cesar-cam-loading" style="--icon:{px}px">'
            f'<img src="{cls.cam_icon_data_uri()}" width="{px}" height="{px}" '
            f'alt="" aria-hidden="true"/>'
            f"</div>"
        )

    @classmethod
    def load_stylesheet(cls) -> str:
        return HTML_CSS_STYLES.read_text(encoding="utf-8")

    @classmethod
    def nav_base_url(cls) -> str:
        try:
            raw = str(st.context.url or "")
        except Exception:
            raw = ""
        if not raw:
            return "http://localhost:8501/"
        return raw.split("?")[0].split("#")[0] or "http://localhost:8501/"

    @classmethod
    def nav_href(cls, **params: str) -> str:
        base = cls.nav_base_url().rstrip("?")
        clean = {k: str(v) for k, v in params.items() if v is not None and str(v) != ""}
        if not clean:
            return base
        # Evita //? se base termina com /
        if base.endswith("/"):
            return f"{base}?{urlencode(clean)}"
        return f"{base}?{urlencode(clean)}"

    @classmethod
    def map_svg_inner(
        cls,
        active_zona: str | None,
        zone_counts: dict[str, int] | None = None,
        *,
        base_url: str | None = None,
    ) -> str:
        counts = zone_counts or {}
        base = base_url or cls.nav_base_url()
        # fundo = degradê azul do .map-card (CSS); sem inland verde / sem label oceano
        parts: list[str] = [
            f'<svg viewBox="{MAP_VIEWBOX}" xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'role="img" aria-label="Mapa esquemático das regiões de Recife" '
            f'preserveAspectRatio="xMidYMid meet">',
            "<defs>",
            '<linearGradient id="hl" x1="0" y1="0" x2="1" y2="1">',
            '<stop offset="0" stop-color="#fff" stop-opacity="0.4"/>',
            '<stop offset="0.5" stop-color="#fff" stop-opacity="0"/>',
            '<stop offset="1" stop-color="#000" stop-opacity="0.3"/>',
            "</linearGradient>",
            '<filter id="b8" x="-30%" y="-30%" width="160%" height="170%">'
            '<feGaussianBlur stdDeviation="8"/></filter>',
            "</defs>",
            '<rect width="600" height="700" fill="none"/>',
        ]
        parts.append('<g filter="url(#b8)" opacity="0.38">')
        for key in ZONA_MAP_ORDER:
            d = smooth_path(_parse_pts(RPA_ZONES[key]["p"]))
            parts.append(f'<path d="{d}" fill="#000" transform="translate(10,22)"/>')
        parts.append("</g>")

        parts.append('<g id="zones">')
        for key in ZONA_MAP_ORDER:
            z = RPA_ZONES[key]
            d = smooth_path(_parse_pts(z["p"]))
            color = cls.zone_color(key)
            active = " is-active" if active_zona == key else ""
            label = html.escape(cls.zone_label(key))
            n_cam = int(counts.get(key, 0))
            safe = html.escape(key)
            # data-zona no <g>: component JS manda setComponentValue (sem top-nav)
            parts.append(
                f'<g class="zg zone-hit{active}" data-zona="{safe}" '
                f'tabindex="0" role="button" style="--zc:{color}" '
                f'aria-label="{label}, {n_cam} câmeras">'
                f'<path class="side" d="{d}"/>'
                f'<path class="top" d="{d}"/>'
                f'<path class="hl" d="{d}"/>'
                f"</g>"
            )
        parts.append("</g>")

        parts.append('<g class="labels" pointer-events="none">')
        for key in ZONA_MAP_ORDER:
            lx, ly = RPA_ZONES[key]["l"]
            label = html.escape(cls.zone_label(key))
            n_cam = int(counts.get(key, 0))
            on = " is-active" if active_zona == key else ""
            parts.append(
                f'<text class="zone-label{on}" x="{lx}" y="{ly}">{label}</text>'
                f'<text class="zone-count{on}" x="{lx}" y="{ly + 18}">'
                f"{n_cam} câmeras</text>"
            )
        parts.append("</g></svg>")
        return "".join(parts)

    @classmethod
    def build_map_html(
        cls,
        zona: str | None,
        *,
        zone_counts: dict[str, int] | None = None,
    ) -> str:
        """Mapa + painel Sobre (STYLE_HOME_ABOUT_*). Clique zona LOCK."""
        css = cls.load_stylesheet()
        theme = cls.map_theme_css()
        now = datetime.now()
        date_s = html.escape(now.date().strftime(HOME_DATE_FMT))
        time_s = html.escape(now.strftime(HOME_TIME_FMT))
        date_lbl = html.escape(HOME_DATE_LABEL)
        time_lbl = html.escape(HOME_TIME_LABEL)
        about_title = html.escape(g.STYLE_HOME_ABOUT_TITLE)
        about_body = html.escape(g.STYLE_HOME_ABOUT_BODY)
        hint = ""
        if not zona:
            hint = f'<div class="map-hint">{html.escape(MAP_HINT)}</div>'
        return f"""<style>{css}
{theme}
a.zone-link {{ text-decoration: none; color: inherit; }}
</style>
<div class="viewport">
  <div class="stage">
    <aside class="side-rail">
      <div class="brand">
        <div class="pin"></div>
        <div class="brand-body">
          <h1>{html.escape(TITLE)}</h1>
          <p class="sub">{html.escape(SUBTITLE)}</p>
          <div class="brand-stats">
            <div class="brand-stat">
              <p class="lbl">{date_lbl}</p>
              <p class="val">{date_s}</p>
            </div>
            <div class="brand-stat">
              <p class="lbl">{time_lbl}</p>
              <p class="val">{time_s}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="about-panel" aria-label="{about_title}">
        <h2>{about_title}</h2>
        <p class="about-body">{about_body}</p>
      </div>
    </aside>
    <div class="map-card">
      {cls.map_svg_inner(zona, zone_counts)}
      {hint}
    </div>
  </div>
</div>"""

    @classmethod
    def render_map(
        cls,
        zona: str | None,
        *,
        zone_counts: dict[str, int] | None = None,
        height: int | None = None,
    ) -> dict | None:
        """
        Renderiza mapa via declare_component.
        Retorno: {"action":"zone","zona":...,"t":...} no clique, ou None.
        """
        h = int(height or MAP_HEIGHT_PX)
        shell = cls.build_map_html(zona, zone_counts=zone_counts)
        return _map_pick(
            html=shell,
            height=h,
            default=None,
            key="cesar_map_pick",
        )

    @classmethod
    def brand_scale(cls) -> float:
        """Lê STYLE_HOME_BRAND_SCALE ao vivo (não congela no import)."""
        return float(g.STYLE_HOME_BRAND_SCALE)

    @classmethod
    def map_theme_css(cls) -> str:
        """Override :root do mapa a partir de STYLE_* (geometria LOCK)."""
        zc = ZONE_COLORS
        s1, s2, s3 = STYLE_MAP_SEA_STOPS
        brand_scale = cls.brand_scale()
        return f"""
:root {{
  --bg: {STYLE_BG};
  --panel: {STYLE_PANEL};
  --ink: {STYLE_INK};
  --mute: {STYLE_MUTE};
  --line: {STYLE_LINE};
  --inland: {MAP_LAND};
  --s1: {s1};
  --s2: {s2};
  --s3: {s3};
  --idle: {STYLE_IDLE};
  --accent: {STYLE_ACCENT};
  --glass-blur: {STYLE_GLASS_BLUR_PX}px;
  --radius: {STYLE_RADIUS_PX}px;
  --shadow: {STYLE_SHADOW};
  --font-display: {STYLE_FONT_DISPLAY};
  --font-ui: {STYLE_FONT_UI};
  --font-weight-title: {STYLE_FONT_WEIGHT_TITLE};
  --font-weight-ui: {STYLE_FONT_WEIGHT_UI};
  --brand-scale: {brand_scale};
  --about-width: {int(g.STYLE_HOME_ABOUT_WIDTH_PX)}px;
  --rail-width: {int(g.STYLE_HOME_ABOUT_WIDTH_PX)}px;
  --c-centro: {zc.get("centro", STYLE_ACCENT)};
  --c-norte: {zc.get("norte", STYLE_ACCENT)};
  --c-noroeste: {zc.get("noroeste", STYLE_ACCENT)};
  --c-oeste: {zc.get("oeste", STYLE_ACCENT)};
  --c-sudoeste: {zc.get("sudoeste", STYLE_ACCENT)};
  --c-sul: {zc.get("sul", STYLE_ACCENT)};
  --c-indeterminado: {zc.get("indeterminado", STYLE_MUTE)};
}}
.brand {{
  --brand-scale: {brand_scale};
}}
"""

    @classmethod
    def streamlit_chrome_css(cls) -> str:
        tile_vh = float(GRID_TILE_VH)
        return f"""
<style>
html, body, .stApp {{
  min-height: 100vh;
  background: {STYLE_BG} !important;
}}
[data-testid="stSidebar"] {{ display: none; }}
header[data-testid="stHeader"] {{
  background: transparent;
  height: 0 !important;
}}
.stAppDeployButton, [data-testid="stToolbar"] {{
  z-index: 999;
}}
.block-container {{
  padding: 10px !important;
  max-width: 100% !important;
  background: {STYLE_BG} !important;
}}
section.main, [data-testid="stMain"] {{
  background: {STYLE_BG} !important;
}}
iframe {{
  border: none !important;
}}
/* MULTICAM: theme Streamlit pinta branco — forçar STYLE_MULTICAM_TEXT */
.stApp .cesar-loading-banner,
.stApp .cesar-loading-banner .cesar-loading-sub,
.stApp .meta-line,
.stApp .sub-line,
.stApp .cesar-grid .cam-chip,
.stApp .cesar-grid .cam-chip span,
.stApp .cesar-pager-meta,
.stApp [data-testid="stMarkdownContainer"] .cesar-loading-banner,
.stApp [data-testid="stMarkdownContainer"] .cesar-loading-sub,
.stApp [data-testid="stMarkdownContainer"] .meta-line,
.stApp [data-testid="stMarkdownContainer"] .sub-line,
.stApp [data-testid="stMarkdownContainer"] .cam-chip,
.stApp [data-testid="stMarkdownContainer"] .cam-chip span,
.stApp [data-testid="stMarkdownContainer"] .cesar-pager-meta,
.stApp div[data-testid="stButton"] > button,
.stApp div[data-testid="stButton"] > button p,
.stApp div[data-testid="stButton"] > button span,
.stApp [data-testid="stSpinner"],
.stApp [data-testid="stSpinner"] *,
.stApp .stSpinner,
.stApp .stSpinner * {{
  color: {STYLE_MULTICAM_TEXT} !important;
}}
/* rail | frame — containers nativos com borda */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: {STYLE_PANEL};
  border: 1px solid {STYLE_LINE} !important;
  border-radius: {STYLE_RADIUS_PX}px !important;
  box-shadow: {STYLE_SHADOW};
}}
.meta-line {{
  margin: 0.35rem 0 0;
  font-family: {STYLE_FONT_DISPLAY};
  font-size: {STYLE_FONT_SIZE_TITLE_REM}rem;
  font-weight: {STYLE_FONT_WEIGHT_TITLE};
  color: {STYLE_MULTICAM_TEXT} !important;
  line-height: 1.25;
}}
.sub-line {{
  margin: 0.2rem 0 0;
  font-family: {STYLE_FONT_UI};
  font-size: {STYLE_FONT_SIZE_SUB_REM}rem;
  color: {STYLE_MULTICAM_TEXT} !important;
}}
.cesar-loading-banner {{
  margin: 0 0 0.5rem;
  padding: 0.65rem 0.85rem;
  background: {STYLE_PANEL};
  border: 1px solid {STYLE_LINE};
  border-radius: {STYLE_RADIUS_PX}px;
  box-shadow: {STYLE_SHADOW};
  font-family: {STYLE_FONT_DISPLAY};
  font-weight: {STYLE_FONT_WEIGHT_TITLE};
  font-size: {STYLE_FONT_SIZE_TITLE_REM}rem;
  color: {STYLE_MULTICAM_TEXT} !important;
  text-align: center;
}}
.cesar-loading-banner .cesar-loading-sub {{
  margin: 0.25rem 0 0;
  font-family: {STYLE_FONT_UI};
  font-weight: {STYLE_FONT_WEIGHT_UI};
  font-size: {STYLE_FONT_SIZE_SUB_REM}rem;
  color: {STYLE_MULTICAM_TEXT} !important;
}}
.cesar-back-wrap {{
  width: 100%;
  max-width: none;
  margin: 0 0 0.35rem;
}}
.cesar-back-wrap div[data-testid="stButton"] > button {{
  width: 100% !important;
}}
div[data-testid="stButton"] > button {{
  background-color: {STYLE_BUTTON_BG} !important;
  background-image: none !important;
  border: 1px solid {STYLE_BUTTON_BORDER} !important;
  box-shadow: {STYLE_SHADOW} !important;
  font-family: {STYLE_FONT_UI} !important;
  font-weight: {STYLE_FONT_WEIGHT_TITLE} !important;
  color: {STYLE_BUTTON_FG} !important;
}}
div[data-testid="stButton"] > button:hover {{
  background-color: {STYLE_BUTTON_BG} !important;
  border-color: {STYLE_MULTICAM_TEXT} !important;
  color: {STYLE_BUTTON_FG} !important;
  opacity: 0.92;
}}
.cesar-grid {{
  padding: 0.15rem 0.2rem 0.25rem;
  background: transparent;
}}
.cesar-grid-cell {{
  position: relative;
  text-align: left;
  padding: 0;
  background: {STYLE_PANEL};
  border: 1px solid {STYLE_LINE};
  border-radius: {STYLE_RADIUS_PX}px;
  margin-bottom: {STYLE_LIST_ITEM_GAP_REM}rem;
  overflow: hidden;
  box-shadow: {STYLE_SHADOW};
}}
.cesar-cam-loading {{
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: {tile_vh}vh;
  max-height: {tile_vh}vh;
  background: {STYLE_IDLE};
}}
.cesar-cam-loading img {{
  width: var(--icon, {CAM_ICON_PX}px);
  height: var(--icon, {CAM_ICON_PX}px);
  object-fit: contain;
  opacity: 0.85;
}}
.cesar-grid-cell [data-testid="stImage"] {{
  display: block;
  width: 100%;
}}
.cesar-grid-cell [data-testid="stImage"] img {{
  margin: 0 !important;
  border-radius: 0;
  object-fit: cover !important;
  width: 100% !important;
  height: {tile_vh}vh !important;
  max-height: {tile_vh}vh !important;
}}
.cesar-grid .cam-chip {{
  margin: -2.15rem 0.45rem 0.35rem;
  position: relative;
  z-index: 2;
  display: inline-block;
  max-width: calc(100% - 0.9rem);
  padding: 0.28rem 0.5rem;
  border-radius: 8px;
  background: {STYLE_CHIP_BG};
  border: 1px solid {STYLE_LINE};
  font-size: {STYLE_FONT_SIZE_CHIP_REM}rem;
  font-weight: {STYLE_FONT_WEIGHT_TITLE};
  line-height: 1.2;
  font-family: {STYLE_FONT_DISPLAY};
  color: {STYLE_CHIP_FG} !important;
}}
/* pager = slot do hint (baixo do frame) */
.cesar-pager {{
  margin: 0.35rem 0 0.25rem;
  padding: 0.45rem 0.55rem;
  background: {STYLE_PANEL};
  border: 1px solid {STYLE_LINE};
  border-radius: 999px;
  box-shadow: {STYLE_SHADOW};
}}
.cesar-pager-meta {{
  text-align: center;
  margin: 0.35rem 0 0;
  font-size: {STYLE_FONT_SIZE_SUB_REM}rem;
  font-family: {STYLE_FONT_UI};
  color: {STYLE_MULTICAM_TEXT} !important;
}}
</style>
"""

    @classmethod
    def feed_chrome_css(cls) -> str:
        w = FEED_WIDTH_VW
        mh = FEED_MAX_HEIGHT_VH
        return f"""
<style>
html, body, .stApp {{
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}}
[data-testid="stSidebar"] {{ display: none; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{
  padding: 0.45rem 0.75rem 0.5rem !important;
  max-width: 100% !important;
  overflow: hidden !important;
}}
section.main, [data-testid="stMain"] {{
  overflow: hidden !important;
}}
.cesar-feed-back {{
  margin: 0 0 0.45rem 0;
  width: fit-content;
  max-width: 220px;
}}
.feed-title {{
  color: {STYLE_INK};
  margin: 0.2rem auto 0.4rem;
  width: {w}vw;
  max-width: {w}vw;
  font-size: {STYLE_FONT_SIZE_TITLE_REM}rem;
  font-family: {STYLE_FONT_DISPLAY};
}}
div[data-testid="stImage"] img {{
  width: auto !important;
  max-width: {w}vw !important;
  max-height: {mh}vh !important;
  height: auto !important;
  object-fit: contain !important;
  display: block;
  margin: 0 auto;
}}
div[data-testid="stImage"] {{
  width: {w}vw !important;
  max-width: {w}vw !important;
  margin: 0 auto !important;
}}
</style>
"""
