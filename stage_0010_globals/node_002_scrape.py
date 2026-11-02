"""
node_002 — scrape CTTU Recife

Fonte: https://transito-recife.serttel.com.br/
Contrato: CameraCatalog. Concreto: RecifeCttuScrape.
Export: EXPORT/v00N/cameras_recife_dd_mm_yyyy.json (dict key -> IdCamera).
"""

from __future__ import annotations

import json
import re
import unicodedata
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

URL = "https://transito-recife.serttel.com.br/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
CAMERAS_RE = re.compile(r"let cameras = (\[.*?\]);", re.S)


class CameraCatalog(ABC):
    """Contrato: dict {KEY_NORMALIZADA: id_camera_int}."""

    @classmethod
    def normalize_key(cls, endereco: str) -> str:
        text = unicodedata.normalize("NFKD", endereco)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.upper()
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in text)
        return "_".join(part for part in cleaned.split("_") if part)

    @abstractmethod
    def fetch(self) -> dict[str, int]:
        """Busca e devolve CODE_CTTU."""

    def export(self, when: datetime | None = None) -> Path:
        when = when or datetime.now()
        out_dir = next_export_dir()
        out_path = out_dir / f"cameras_recife_{when.strftime('%d_%m_%Y')}.json"
        data = self.fetch()
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return out_path


class RecifeCttuScrape(CameraCatalog):
    def __init__(self, url: str = URL) -> None:
        self.url = url

    def _fetch_html(self) -> str:
        req = urllib.request.Request(self.url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")

    def _parse_cameras(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        scripts = "\n".join(tag.get_text() for tag in soup.find_all("script"))
        match = CAMERAS_RE.search(scripts)
        if not match:
            raise ValueError("JSON cameras nao encontrado no HTML")
        return json.loads(match.group(1))

    def fetch(self) -> dict[str, int]:
        cameras = self._parse_cameras(self._fetch_html())
        code_cttu: dict[str, int] = {}
        for cam in cameras:
            key = self.normalize_key(cam["Endereco"])
            code_cttu[key] = int(cam["IdCamera"])
        return code_cttu


def next_export_dir(
    export_root: Path | None = None,
) -> Path:
    root = export_root or (Path(__file__).resolve().parent / "EXPORT")
    root.mkdir(parents=True, exist_ok=True)
    version_re = re.compile(r"^v(\d+)$")
    versions: list[int] = []
    for path in root.iterdir():
        if not path.is_dir():
            continue
        match = version_re.match(path.name)
        if match:
            versions.append(int(match.group(1)))
    next_n = (max(versions) + 1) if versions else 1
    out_dir = root / f"v{next_n:03d}"
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir


if __name__ == "__main__":
    scrape = RecifeCttuScrape()
    path = scrape.export()
    code = json.loads(path.read_text(encoding="utf-8"))
    print(f"cameras: {len(code)}")
    print(f"AV_17_DE_AGOSTO -> {code.get('AV_17_DE_AGOSTO')}")
    print(f"PRACA_DA_CONVENCAO_BEBERIBE -> {code.get('PRACA_DA_CONVENCAO_BEBERIBE')}")
    print(f"salvo: {path}")
