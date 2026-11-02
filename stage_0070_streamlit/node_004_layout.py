"""
node_004 — home mapa LOCK | multicam vision | voltar

LAYOUT LOCK (home + multicam) — ver .cursor/rules/layout-lock.mdc
Home: rail brand+Sobre | mapa. Clique/geo LOCK.
Multicam: rail Voltar+título | frame grade + pager.
"""

from __future__ import annotations

import asyncio
import html
import sys
import threading
from pathlib import Path

import httpx
import streamlit as st
from PIL import Image

_ROOT = Path(__file__).resolve().parents[1]
_GLOBALS = _ROOT / "stage_0010_globals"
if str(_GLOBALS) not in sys.path:
    sys.path.insert(0, str(_GLOBALS))

import node_003_globals as node_003

from node_002_widget_cameras import CameraBusWidget
from node_003_visuals import (
    FEED_BACK_LABEL,
    GRID_COLS,
    GRID_GAP,
    MAP_HEIGHT_PX,
    PAGER_NEXT_LABEL,
    PAGER_PREV_LABEL,
    PANEL_PAGE_SIZE,
    STYLE_CHIP_FG,
    STYLE_MULTICAM_TEXT,
    AppVisuals,
)


class RecifeMonitorApp:
    def __init__(self, widget: CameraBusWidget | None = None) -> None:
        self.widget = widget or CameraBusWidget()
        self.zones = AppVisuals.zones_filtered(node_003.DF_CAMERAS.index.tolist())

    def _all_cameras_for_zona(self, zona: str) -> list[tuple[str, int]]:
        cams = self.zones.get(zona, {})
        return [(key, int(cam_id)) for key, cam_id in cams.items()]

    def _zone_counts(self) -> dict[str, int]:
        return {z: len(cams) for z, cams in self.zones.items()}

    def _go_main_menu(self) -> None:
        st.query_params.from_dict({})
        st.rerun()

    def _set_page(self, zona: str, page: int) -> None:
        st.query_params.from_dict({"zona": zona, "page": str(max(0, page))})
        st.rerun()

    def _apply_map_event(self, event: object) -> bool:
        if not isinstance(event, dict):
            return False
        t = event.get("t")
        if t is not None and t == st.session_state.get("_cesar_map_t"):
            return False
        if t is not None:
            st.session_state["_cesar_map_t"] = t
        if event.get("action") == "zone":
            zona = event.get("zona")
            if isinstance(zona, str) and zona in self.zones:
                st.query_params.from_dict({"zona": zona, "page": "0"})
                return True
        return False

    def _back_button(self, *, key: str) -> None:
        st.markdown('<div class="cesar-back-wrap">', unsafe_allow_html=True)
        if st.button(
            FEED_BACK_LABEL,
            key=key,
            type="primary",
            width="content",
        ):
            self._go_main_menu()
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_pager(
        self,
        *,
        zona: str,
        page: int,
        n_pages: int,
        total: int,
        page_size: int,
    ) -> None:
        """Slot inferior do frame (lugar do hint da home): Anterior / N / Próxima."""
        multi = total > page_size
        st.markdown('<div class="cesar-pager">', unsafe_allow_html=True)
        prev_c, mid_c, next_c = st.columns([1, 1, 1])
        with prev_c:
            if st.button(
                PAGER_PREV_LABEL,
                key=f"cesar_prev_{zona}_{page}",
                disabled=(not multi) or page <= 0,
                width="stretch",
            ):
                self._set_page(zona, page - 1)
        with mid_c:
            st.markdown(
                f'<p class="cesar-pager-meta" style="color:{STYLE_MULTICAM_TEXT}">'
                f"{page + 1} / {n_pages}</p>",
                unsafe_allow_html=True,
            )
        with next_c:
            if st.button(
                PAGER_NEXT_LABEL,
                key=f"cesar_next_{zona}_{page}",
                disabled=(not multi) or page >= n_pages - 1,
                width="stretch",
            ):
                self._set_page(zona, page + 1)
        st.markdown("</div>", unsafe_allow_html=True)

    def _detect_rail_msg(self, slot: object, text: str) -> None:
        slot.markdown(
            f'<p class="sub-line" style="color:{STYLE_MULTICAM_TEXT}">'
            f"{html.escape(text)}</p>",
            unsafe_allow_html=True,
        )

    def _fetch_banner_msg(self, slot: object, text: str, *, n_load: int) -> None:
        """Quadro branco acima da grade — mesmo status do rail."""
        slot.markdown(
            f'<div class="cesar-loading-banner" style="color:{STYLE_MULTICAM_TEXT}">'
            f"{html.escape(text)}"
            f'<p class="cesar-loading-sub" style="color:{STYLE_MULTICAM_TEXT}">'
            f"{n_load} câmeras nesta tela</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    def _set_fetch_status(
        self,
        *,
        rail_slot: object,
        banner_slot: object,
        text: str,
        n_load: int,
    ) -> None:
        self._detect_rail_msg(rail_slot, text)
        self._fetch_banner_msg(banner_slot, text, n_load=n_load)

    def _fetch_snapshots_run(self, keys: list[str]) -> dict[str, Image.Image]:
        """Fase 1: só JPEG async (httpx). Widget intocado."""
        client = self.widget.client
        workers = max(1, min(int(node_003.STYLE_MULTICAM_WORKERS), len(keys) or 1))
        gap_s = float(node_003.SNAPSHOT_FETCH_GAP_S)
        offline = Image.open(AppVisuals.offline_path()).convert("RGB")

        async def _run() -> dict[str, Image.Image]:
            sem = asyncio.Semaphore(workers)
            pacer = asyncio.Lock()
            next_fetch_at = 0.0
            out: dict[str, Image.Image] = {}

            async def _pace() -> None:
                nonlocal next_fetch_at
                async with pacer:
                    now = asyncio.get_running_loop().time()
                    wait = next_fetch_at - now
                    if wait > 0:
                        await asyncio.sleep(wait)
                    next_fetch_at = asyncio.get_running_loop().time() + gap_s

            async def _one(http: httpx.AsyncClient, key: str) -> None:
                async with sem:
                    try:
                        if key not in node_003.DF_CAMERAS.index:
                            out[key] = offline.copy()
                            return
                        url = str(node_003.DF_CAMERAS.loc[key, "url"])
                        await _pace()
                        out[key] = await client.fetch_async(http, url)
                    except Exception:  # noqa: BLE001 — tile offline, grade segue
                        out[key] = offline.copy()

            timeout = httpx.Timeout(client.timeout_s)
            headers = {"User-Agent": client.user_agent}
            async with httpx.AsyncClient(
                timeout=timeout,
                headers=headers,
                follow_redirects=True,
            ) as http:
                await asyncio.gather(*[_one(http, k) for k in keys])
            return out

        return asyncio.run(_run()) if keys else {}

    def _render_cam_grid(
        self,
        zona: str,
        page: int,
        *,
        detect_slot: object,
    ) -> None:
        cameras = self._all_cameras_for_zona(zona)
        total = len(cameras)
        page_size = PANEL_PAGE_SIZE
        cols_n = GRID_COLS
        n_pages = max(1, (total + page_size - 1) // page_size) if total else 1
        page = max(0, min(page, n_pages - 1))
        slice_cams = cameras[page * page_size : (page + 1) * page_size]
        n_load = len(slice_cams)

        # banner (quadro branco): espelha STATUS_* do fetch / detect
        loading_slot = st.empty()
        self._fetch_banner_msg(
            loading_slot, node_003.STYLE_FETCH_LOADING, n_load=n_load
        )

        # 1) monta grade com placeholder (ícone) em todos os tiles
        slots: list[tuple[str, int, str, object, object]] = []
        st.markdown('<div class="cesar-grid">', unsafe_allow_html=True)
        for row_i in range(0, page_size, cols_n):
            row = slice_cams[row_i : row_i + cols_n]
            if not row:
                break
            cols = st.columns(cols_n, gap=GRID_GAP)
            for j, col in enumerate(cols):
                with col:
                    if j >= len(row):
                        continue
                    key, cam_id = row[j]
                    label = key.replace("_", " ").title()
                    if len(label) > 36:
                        label = label[:33] + "…"
                    st.markdown('<div class="cesar-grid-cell">', unsafe_allow_html=True)
                    frame = st.empty()
                    frame.markdown(
                        AppVisuals.cam_loading_icon_html(),
                        unsafe_allow_html=True,
                    )
                    foot = st.empty()
                    slots.append((key, cam_id, label, frame, foot))
                    st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        keys = [s[0] for s in slots]

        # 2) snapshots async — rail + banner alternam até acabar
        interval_s = float(node_003.STYLE_FETCH_STATUS_INTERVAL_S)
        fetch_box: dict[str, dict[str, Image.Image]] = {}

        def _fetch_worker() -> None:
            fetch_box["raw"] = self._fetch_snapshots_run(keys)

        worker = threading.Thread(target=_fetch_worker, daemon=True)
        worker.start()
        flip = False
        self._set_fetch_status(
            rail_slot=detect_slot,
            banner_slot=loading_slot,
            text=node_003.STYLE_FETCH_LOADING,
            n_load=n_load,
        )
        while worker.is_alive():
            worker.join(timeout=interval_s)
            if not worker.is_alive():
                break
            flip = not flip
            self._set_fetch_status(
                rail_slot=detect_slot,
                banner_slot=loading_slot,
                text=(
                    node_003.STYLE_FETCH_CONTACTING
                    if flip
                    else node_003.STYLE_FETCH_LOADING
                ),
                n_load=n_load,
            )
        worker.join()
        self._set_fetch_status(
            rail_slot=detect_slot,
            banner_slot=loading_slot,
            text=node_003.STYLE_FETCH_CONNECTED,
            n_load=n_load,
        )
        raw = fetch_box.get("raw") or {}
        for key, _cam_id, label, frame, foot in slots:
            frame.image(raw[key], width="stretch")
            foot.markdown(
                f'<p class="cam-chip" style="color:{STYLE_CHIP_FG}">'
                f"{html.escape(label)}</p>",
                unsafe_allow_html=True,
            )

        # 3) YOLO depois — status rail + banner
        self._set_fetch_status(
            rail_slot=detect_slot,
            banner_slot=loading_slot,
            text=node_003.STYLE_DETECT_LOADING,
            n_load=n_load,
        )
        for key, _cam_id, label, frame, foot in slots:
            image, _caption, _meta = self.widget._vision_on_image(key, raw[key])
            frame.image(image, width="stretch")
        self._set_fetch_status(
            rail_slot=detect_slot,
            banner_slot=loading_slot,
            text=node_003.STYLE_DETECT_DONE,
            n_load=n_load,
        )
        loading_slot.empty()

        # 4) pager no rodapé do frame (slot do hint da home)
        self._render_pager(
            zona=zona,
            page=page,
            n_pages=n_pages,
            total=total,
            page_size=page_size,
        )

    def _view_zone(self, zona: str, page: int) -> None:
        total = self._zone_counts().get(zona, 0)
        page_size = PANEL_PAGE_SIZE
        n_pages = max(1, (total + page_size - 1) // page_size) if total else 1
        page = max(0, min(page, n_pages - 1))

        # diagramação = home: rail | frame (widgets nativos — sem div HTML wrapping)
        rail, main = st.columns([1, 3.4], gap="small")
        with rail:
            with st.container(border=True):
                self._back_button(key="cesar_btn_back_zone")
                st.markdown(
                    f'<p class="meta-line" style="color:{STYLE_MULTICAM_TEXT}">'
                    f"{AppVisuals.zone_page_title(zona)}</p>"
                    f'<p class="sub-line" style="color:{STYLE_MULTICAM_TEXT}">'
                    f"{total} câmeras · {page_size}/tela"
                    f" · página {page + 1}/{n_pages}</p>",
                    unsafe_allow_html=True,
                )
                detect_slot = st.empty()
        with main:
            with st.container(border=True):
                self._render_cam_grid(zona, page, detect_slot=detect_slot)

    def _view_home(self) -> None:
        counts = self._zone_counts()
        event = AppVisuals.render_map(
            None,
            zone_counts=counts,
            height=MAP_HEIGHT_PX,
        )
        if event and self._apply_map_event(event):
            st.rerun()

    def render(self) -> None:
        if not self.zones:
            st.error(
                "Nenhuma câmera do JSON de zonas coincide com "
                f"{node_003.CAMERAS_JSON.name}."
            )
            return

        zona_qp = st.query_params.get("zona")
        zona = zona_qp if zona_qp in self.zones else None
        try:
            page = int(st.query_params.get("page", "0"))
        except ValueError:
            page = 0

        st.markdown(AppVisuals.streamlit_chrome_css(), unsafe_allow_html=True)

        if zona:
            self._view_zone(zona, page)
            return

        self._view_home()


def render_app() -> None:
    RecifeMonitorApp().render()
