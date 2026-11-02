"""
node_003 — smoke BusDetector em snapshots CTTU

Baixa 3–5 cameras, detecta bus, grava contact sheet + frames anotados
em SMOKE_EXPORT (node_003_globals).
"""

from __future__ import annotations

import io
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GLOBALS_DIR = Path(__file__).resolve().parents[1] / "stage_0010_globals"
if str(GLOBALS_DIR) not in sys.path:
    sys.path.insert(0, str(GLOBALS_DIR))

import node_003_globals as node_003

from node_002_bus_detector import BusDetector

SMOKE_N = 5


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


class BusSmoke:
    """Smoke: detect em N cameras + contact sheet em SMOKE_EXPORT."""

    CELL_W = 480
    CELL_H = 360

    def __init__(
        self,
        detector: BusDetector | None = None,
        client: CttuSnapshotClient | None = None,
        export_dir: Path | None = None,
    ) -> None:
        self.detector = detector or BusDetector()
        self.client = client or CttuSnapshotClient()
        self.export_dir = Path(export_dir) if export_dir else node_003.SMOKE_EXPORT

    @classmethod
    def resolve_keys(cls, n: int = SMOKE_N) -> tuple[str, ...]:
        """Primeiras N keys cuspidas por DF_CAMERAS (CAMERAS_JSON). Sem hardcode."""
        catalog = [str(k) for k in node_003.DF_CAMERAS.index.tolist()]
        if not catalog:
            raise RuntimeError(
                f"DF_CAMERAS vazio — confira {node_003.CAMERAS_JSON}"
            )
        return tuple(catalog[:n])

    def _annotate(self, image: Image.Image, boxes: list[dict], title: str) -> Image.Image:
        frame = image.copy()
        draw = ImageDraw.Draw(frame)
        font = ImageFont.load_default()
        for box in boxes:
            xy = (box["x1"], box["y1"], box["x2"], box["y2"])
            draw.rectangle(xy, outline=(0, 255, 0), width=3)
            label = f"bus {box['conf']:.2f}"
            draw.text((box["x1"], max(0, box["y1"] - 12)), label, fill=(0, 255, 0), font=font)
        draw.text((8, 8), f"{title} | n={len(boxes)}", fill=(255, 255, 0), font=font)
        return frame

    def _fit_cell(self, image: Image.Image) -> Image.Image:
        cell = Image.new("RGB", (self.CELL_W, self.CELL_H), (24, 24, 24))
        fitted = image.copy()
        fitted.thumbnail((self.CELL_W, self.CELL_H))
        x = (self.CELL_W - fitted.width) // 2
        y = (self.CELL_H - fitted.height) // 2
        cell.paste(fitted, (x, y))
        return cell

    def run(
        self,
        keys: tuple[str, ...] | list[str] | None = None,
        conf: float | None = None,
    ) -> Path:
        keys = tuple(keys) if keys else self.resolve_keys()
        self.export_dir.mkdir(parents=True, exist_ok=True)
        cells: list[Image.Image] = []
        summary: list[str] = [f"catalog={node_003.CAMERAS_JSON.name}", f"keys={keys}"]

        for key in keys:
            url = str(node_003.DF_CAMERAS.loc[key, "url"])
            try:
                image = self.client.fetch(url)
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
                summary.append(f"{key}: FETCH_FAIL {exc}")
                fail = Image.new("RGB", (self.CELL_W, self.CELL_H), (48, 16, 16))
                ImageDraw.Draw(fail).text((16, 16), f"{key}\nFETCH_FAIL", fill=(255, 180, 180))
                cells.append(fail)
                continue

            boxes = self.detector.detect(image, conf=conf)
            annotated = self._annotate(image, boxes, key)
            out_frame = self.export_dir / f"smoke_{key}.jpg"
            annotated.save(out_frame, quality=90)
            cells.append(self._fit_cell(annotated))
            summary.append(f"{key}: buses={len(boxes)}")

        if not cells:
            raise RuntimeError("smoke sem nenhuma celula (keys/fetch falharam)")

        cols = min(3, len(cells))
        rows = (len(cells) + cols - 1) // cols
        sheet = Image.new(
            "RGB",
            (cols * self.CELL_W, rows * self.CELL_H),
            (16, 16, 16),
        )
        for i, cell in enumerate(cells):
            r, c = divmod(i, cols)
            sheet.paste(cell, (c * self.CELL_W, r * self.CELL_H))

        sheet_path = self.export_dir / "contact_sheet_bus_smoke.jpg"
        sheet.save(sheet_path, quality=92)
        summary_path = self.export_dir / "smoke_summary.txt"
        summary_path.write_text("\n".join(summary) + "\n", encoding="utf-8")
        print("SMOKE_EXPORT", self.export_dir)
        print("contact_sheet", sheet_path)
        for line in summary:
            print(line)
        return sheet_path


if __name__ == "__main__":
    BusSmoke().run()
