"""
node_002 — pipeline câmera: fetch → BusDetector → BusOverlay

UI de zona/lista/mapa: node_004_layout.py
Knobs detect: stage_0010_globals; knobs UI: node_003_visuals
"""

from __future__ import annotations

import asyncio
import io
import sys
import threading
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import httpx
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

_ROOT = Path(__file__).resolve().parents[1]
for _sub in ("stage_0010_globals", "stage_0021_vision", "stage_0031_overlay"):
    _path = _ROOT / _sub
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import node_003_globals as node_003
from node_002_bus_detector import BusDetector
from node_002_bus_overlay import BusOverlay
from node_003_globals import OverlayAnchor
from __visuals__._references import DecisionPalette

import node_003_visuals as visuals


class CttuSnapshotClient:
    """Fetch JPEG de snapshot CTTU → PIL."""

    def __init__(
        self,
        timeout_s: float | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.timeout_s = (
            node_003.SNAPSHOT_TIMEOUT_S if timeout_s is None else float(timeout_s)
        )
        self.user_agent = user_agent or node_003.SNAPSHOT_USER_AGENT

    def fetch(self, url: str) -> Image.Image:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            data = resp.read()
        if data[:2] != b"\xff\xd8":
            raise ValueError(f"resposta nao e JPEG: {url}")
        return Image.open(io.BytesIO(data)).convert("RGB")

    async def fetch_async(
        self,
        client: httpx.AsyncClient,
        url: str,
    ) -> Image.Image:
        retries = int(node_003.SNAPSHOT_429_RETRIES)
        gap = float(node_003.SNAPSHOT_FETCH_GAP_S)
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            resp = await client.get(url)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else gap * (attempt + 2)
                await asyncio.sleep(max(wait_s, gap))
                last_exc = httpx.HTTPStatusError(
                    "Too Many Requests",
                    request=resp.request,
                    response=resp,
                )
                continue
            resp.raise_for_status()
            data = resp.content
            if data[:2] != b"\xff\xd8":
                raise ValueError(f"resposta nao e JPEG: {url}")
            return Image.open(io.BytesIO(data)).convert("RGB")
        assert last_exc is not None
        raise last_exc


class CameraBusWidget:
    """Detect + overlay; sem UI de zona (isso vive no layout)."""

    def __init__(
        self,
        client: CttuSnapshotClient | None = None,
    ) -> None:
        self.client = client or CttuSnapshotClient()
        self._detect_lock = threading.Lock()

    @staticmethod
    @st.cache_resource
    def load_detector(class_name: str, debug_all: bool) -> BusDetector:
        return BusDetector(class_name=class_name, debug_all_classes=debug_all)

    @staticmethod
    def display_name(name: str, bus_names: tuple[str, ...]) -> str:
        return "bus" if name in bus_names else name

    @classmethod
    def annotate_debug(
        cls,
        image: Image.Image,
        boxes: list[dict],
        bus_names: tuple[str, ...] | None = None,
    ) -> Image.Image:
        bus_names = bus_names or tuple(node_003.BUS_CLASS_NAMES)
        frame = image.copy()
        draw = ImageDraw.Draw(frame)
        font = ImageFont.load_default()
        for box in boxes:
            color = DecisionPalette.rgb_for_conf(float(box["conf"]))
            xy = (box["x1"], box["y1"], box["x2"], box["y2"])
            draw.rectangle(xy, outline=color, width=2)
            shown = cls.display_name(str(box.get("name", "?")), bus_names)
            label = f"{shown} {box['conf']:.2f}"
            draw.text(
                (box["x1"], max(0, box["y1"] - 12)),
                label,
                fill=color,
                font=font,
            )
        return frame

    def _offline(
        self,
        key: str,
        meta: str,
    ) -> tuple[Image.Image, str, str]:
        offline = Image.open(visuals.AppVisuals.offline_path()).convert("RGB")
        return offline, key, meta

    def _vision_on_image(
        self,
        key: str,
        image: Image.Image,
    ) -> tuple[Image.Image | bytes, str, str]:
        debug_all = bool(node_003.VISION_DEBUG_ALL_CLASSES)
        class_name = str(node_003.BUS_CLASS_NAME)
        bus_names = tuple(node_003.BUS_CLASS_NAMES)
        detector = self.load_detector(class_name, debug_all)
        with self._detect_lock:
            boxes = detector.detect(image)

        mode = "all_coco" if debug_all else "+".join(bus_names)
        meta = (
            f"n={len(boxes)} | class={mode} | "
            f"conf>={float(node_003.BUS_CONF_DEFAULT):.2f}"
        )
        if boxes:
            counts = Counter(b.get("name", "?") for b in boxes)
            meta += " | " + ", ".join(f"{n}={c}" for n, c in counts.most_common(6))

        annotated = self.annotate_debug(image, boxes, bus_names) if boxes else image
        bus_boxes = [b for b in boxes if b.get("name") in bus_names]
        caption = key

        if bus_boxes and BusOverlay.list_gifs():
            overlay = BusOverlay(anchor=OverlayAnchor(node_003.OVERLAY_ANCHOR))
            picked = overlay.resolve_asset()
            result = overlay.compose(annotated, bus_boxes, asset_path=picked)
            if picked is not None:
                caption = f"{key} | gif={picked.name}"
            return result, caption, meta

        return annotated, caption, meta

    def process_camera(
        self,
        key: str,
    ) -> tuple[Image.Image | bytes, str, str]:
        """
        Retorna (imagem|gif_bytes, caption, meta_caption).
        Em falha de fetch: placeholder CAMERA_OFFLINE.
        """
        if key not in node_003.DF_CAMERAS.index:
            return self._offline(key, "key ausente no DF_CAMERAS")

        url = str(node_003.DF_CAMERAS.loc[key, "url"])
        try:
            image = self.client.fetch(url)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            return self._offline(key, f"offline: {exc}")

        return self._vision_on_image(key, image)

    async def process_cameras_async(
        self,
        keys: list[str],
        *,
        max_workers: int | None = None,
        on_done: Callable[
            [str, tuple[Image.Image | bytes, str, str]], None
        ]
        | None = None,
    ) -> dict[str, tuple[Image.Image | bytes, str, str]]:
        """
        Fetch JPEG async (httpx) + vision.
        as_completed: chama on_done a cada câmera pronta (pintar tile já).
        YOLO detect serializado por lock (modelo compartilhado).
        """
        if not keys:
            return {}

        workers = int(
            max_workers
            if max_workers is not None
            else node_003.STYLE_MULTICAM_WORKERS
        )
        workers = max(1, min(workers, len(keys)))
        sem = asyncio.Semaphore(workers)
        gap_s = float(node_003.SNAPSHOT_FETCH_GAP_S)
        pacer = asyncio.Lock()
        next_fetch_at = 0.0
        timeout = httpx.Timeout(self.client.timeout_s)
        headers = {"User-Agent": self.client.user_agent}

        async def _pace_fetch() -> None:
            """Espaça starts de Snapshot — Serttel sem quota doc, evita 429."""
            nonlocal next_fetch_at
            async with pacer:
                now = asyncio.get_running_loop().time()
                wait = next_fetch_at - now
                if wait > 0:
                    await asyncio.sleep(wait)
                next_fetch_at = asyncio.get_running_loop().time() + gap_s

        async def _one(
            client: httpx.AsyncClient,
            key: str,
        ) -> tuple[str, tuple[Image.Image | bytes, str, str]]:
            async with sem:
                try:
                    if key not in node_003.DF_CAMERAS.index:
                        return key, self._offline(key, "key ausente no DF_CAMERAS")
                    url = str(node_003.DF_CAMERAS.loc[key, "url"])
                    await _pace_fetch()
                    image = await self.client.fetch_async(client, url)
                    # YOLO sync/CPU — não bloqueia o loop das outras fetches
                    payload = await asyncio.to_thread(
                        self._vision_on_image, key, image
                    )
                    return key, payload
                except Exception as exc:  # noqa: BLE001 — tile não pode derrubar a grade
                    return key, self._offline(key, f"erro: {exc}")

        out: dict[str, tuple[Image.Image | bytes, str, str]] = {}
        async with httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:
            tasks = [asyncio.create_task(_one(client, k)) for k in keys]
            for fut in asyncio.as_completed(tasks):
                key, payload = await fut
                out[key] = payload
                if on_done is not None:
                    on_done(key, payload)
        return out

    def process_cameras_async_run(
        self,
        keys: list[str],
        *,
        max_workers: int | None = None,
        on_done: Callable[
            [str, tuple[Image.Image | bytes, str, str]], None
        ]
        | None = None,
    ) -> dict[str, tuple[Image.Image | bytes, str, str]]:
        """Entry sync p/ Streamlit: asyncio.run + on_done progressivo."""
        return asyncio.run(
            self.process_cameras_async(
                keys, max_workers=max_workers, on_done=on_done
            )
        )
