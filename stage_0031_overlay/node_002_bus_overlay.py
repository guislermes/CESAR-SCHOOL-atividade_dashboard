"""
node_002 — BusOverlay (arte sobre bbox de bus)

Briefing: node_001_briefing.md
Knobs: stage_0010_globals.node_003_globals
Contrato: BusOverlay.compose(PIL, boxes) -> PIL still | bytes GIF
"""

from __future__ import annotations

import io
import random
import sys
from pathlib import Path

from PIL import Image

GLOBALS_DIR = Path(__file__).resolve().parents[1] / "stage_0010_globals"
if str(GLOBALS_DIR) not in sys.path:
    sys.path.insert(0, str(GLOBALS_DIR))

import node_003_globals as node_003
from node_003_globals import OverlayAnchor


class BusOverlay:
    """Composita asset da pasta OVERLAY_ASSETS_DIR sobre cada bbox."""

    def __init__(
        self,
        assets_dir: Path | str | None = None,
        anchor: OverlayAnchor | str | None = None,
        size_frac: float | None = None,
        margin_px: int | None = None,
    ) -> None:
        self.assets_dir = (
            Path(assets_dir) if assets_dir else Path(node_003.OVERLAY_ASSETS_DIR)
        )
        self.anchor = self.resolve_anchor(anchor)
        self.size_frac = (
            node_003.OVERLAY_SIZE_FRAC if size_frac is None else float(size_frac)
        )
        self.margin_px = (
            node_003.OVERLAY_MARGIN_PX if margin_px is None else int(margin_px)
        )

    @classmethod
    def resolve_anchor(cls, anchor: OverlayAnchor | str | None) -> OverlayAnchor:
        if anchor is None:
            return OverlayAnchor(node_003.OVERLAY_ANCHOR)
        if isinstance(anchor, OverlayAnchor):
            return anchor
        return OverlayAnchor(str(anchor).strip().lower())

    @classmethod
    def list_assets(cls, assets_dir: Path | None = None) -> list[Path]:
        root = Path(assets_dir) if assets_dir else Path(node_003.OVERLAY_ASSETS_DIR)
        if not root.is_dir():
            return []
        exts = tuple(e.lower() for e in node_003.OVERLAY_IMAGE_EXTS)
        return [
            p
            for p in sorted(root.iterdir())
            if p.is_file() and p.suffix.lower() in exts
        ]

    @classmethod
    def list_gifs(cls, assets_dir: Path | None = None) -> list[Path]:
        return [p for p in cls.list_assets(assets_dir) if p.suffix.lower() == ".gif"]

    @classmethod
    def resolve_asset(cls, assets_dir: Path | None = None) -> Path | None:
        """GIF aleatório da pasta; vazia → None (compose sem arte)."""
        files = cls.list_gifs(assets_dir)
        if not files:
            return None
        return random.choice(files)

    def compose(
        self,
        base: Image.Image,
        boxes: list[dict],
        asset_path: Path | str | None = None,
    ) -> Image.Image | bytes:
        """
        Sem boxes ou sem GIF → still original.
        GIF animado → bytes; um GIF random por chamada (salvo override).
        """
        rgb = base.convert("RGBA")
        if not boxes:
            return base.convert("RGB")

        path = Path(asset_path) if asset_path else self.resolve_asset(self.assets_dir)
        if path is None:
            return base.convert("RGB")

        frames, durations = self._load_overlay_frames(path)
        if not frames:
            return base.convert("RGB")

        composed: list[Image.Image] = []
        for frame in frames:
            canvas = rgb.copy()
            for box in boxes:
                placed = self._place_frame(frame, box)
                if placed is None:
                    continue
                overlay, xy = placed
                canvas.alpha_composite(overlay, dest=xy)
            composed.append(canvas.convert("RGB"))

        if len(composed) == 1 and path.suffix.lower() != ".gif":
            return composed[0]

        return self._encode_gif(composed, durations)

    def _load_overlay_frames(self, path: Path) -> tuple[list[Image.Image], list[int]]:
        img = Image.open(path)
        frames: list[Image.Image] = []
        durations: list[int] = []
        try:
            index = 0
            while True:
                img.seek(index)
                frame = img.convert("RGBA")
                frames.append(frame)
                durations.append(int(img.info.get("duration", 100)))
                index += 1
        except EOFError:
            pass
        if not frames:
            frames = [img.convert("RGBA")]
            durations = [100]
        return frames, durations

    def _target_size(self, box: dict, frame: Image.Image) -> tuple[int, int]:
        bw = max(1.0, float(box["x2"]) - float(box["x1"]))
        side = max(1, int(round(bw * self.size_frac)))
        aspect = frame.height / max(1, frame.width)
        return side, max(1, int(round(side * aspect)))

    def _anchor_xy(
        self,
        box: dict,
        ow: int,
        oh: int,
    ) -> tuple[int, int]:
        x1, y1, x2, y2 = (
            float(box["x1"]),
            float(box["y1"]),
            float(box["x2"]),
            float(box["y2"]),
        )
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        m = self.margin_px

        if self.anchor is OverlayAnchor.TOP:
            return int(round(cx - ow / 2.0)), int(round(y1 - oh - m))
        if self.anchor is OverlayAnchor.BOTTOM:
            return int(round(cx - ow / 2.0)), int(round(y2 + m))
        if self.anchor is OverlayAnchor.LEFT:
            return int(round(x1 - ow - m)), int(round(cy - oh / 2.0))
        if self.anchor is OverlayAnchor.RIGHT:
            return int(round(x2 + m)), int(round(cy - oh / 2.0))
        raise ValueError(f"anchor invalido: {self.anchor}")

    def _place_frame(
        self,
        frame: Image.Image,
        box: dict,
    ) -> tuple[Image.Image, tuple[int, int]] | None:
        tw, th = self._target_size(box, frame)
        if tw < 1 or th < 1:
            return None
        resized = frame.resize((tw, th), Image.Resampling.LANCZOS)
        return resized, self._anchor_xy(box, tw, th)

    @staticmethod
    def _encode_gif(frames: list[Image.Image], durations: list[int]) -> bytes:
        buf = io.BytesIO()
        first, rest = frames[0], frames[1:]
        first.save(
            buf,
            format="GIF",
            save_all=True,
            append_images=rest,
            duration=durations[: len(frames)],
            loop=0,
            disposal=2,
        )
        return buf.getvalue()
