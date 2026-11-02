"""
node_002 — BusDetector (YOLO COCO → classe alvo ou debug all)

Briefing: node_001_briefing.md
Knobs: stage_0010_globals.node_003_globals
Contrato: BusDetector.detect(PIL) -> list[{x1,y1,x2,y2,conf,cls,name}]
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

GLOBALS_DIR = Path(__file__).resolve().parents[1] / "stage_0010_globals"
if str(GLOBALS_DIR) not in sys.path:
    sys.path.insert(0, str(GLOBALS_DIR))

import node_003_globals as node_003


class BusDetector:
    """Detector COCO pré-treinado; filtro por classe ou all-classes (debug)."""

    def __init__(
        self,
        weights: Path | str | None = None,
        class_name: str | None = None,
        debug_all_classes: bool | None = None,
    ) -> None:
        self.weights = self.resolve_weights(weights)
        self.class_name = class_name or node_003.BUS_CLASS_NAME
        self.class_names = tuple(node_003.BUS_CLASS_NAMES)
        self.debug_all_classes = (
            bool(node_003.VISION_DEBUG_ALL_CLASSES)
            if debug_all_classes is None
            else bool(debug_all_classes)
        )
        self._model = YOLO(str(self.weights))
        self._id_to_name = {
            idx: name for name, idx in self.names_to_id_map(self._model).items()
        }
        self._class_ids = [
            self.resolve_class_id(self._model, name) for name in self.class_names
        ]
        self._class_id = self.resolve_class_id(self._model, self.class_name)

    @classmethod
    def resolve_weights(cls, weights: Path | str | None = None) -> Path:
        path = Path(weights) if weights else Path(node_003.YOLO_WEIGHTS)
        if not path.is_file():
            raise FileNotFoundError(f"pesos YOLO nao encontrados: {path}")
        return path

    @classmethod
    def names_to_id_map(cls, model: YOLO) -> dict[str, int]:
        names = model.names
        if isinstance(names, dict):
            return {str(name): int(idx) for idx, name in names.items()}
        return {str(name): idx for idx, name in enumerate(names)}

    @classmethod
    def resolve_class_id(cls, model: YOLO, class_name: str) -> int:
        name_to_id = cls.names_to_id_map(model)
        if class_name not in name_to_id:
            raise KeyError(
                f"classe {class_name!r} ausente no modelo; "
                f"disponiveis={sorted(name_to_id)}"
            )
        return name_to_id[class_name]

    def detect(
        self,
        image: Image.Image,
        conf: float | None = None,
    ) -> list[dict]:
        """Bboxes em pixels. Debug: all COCO; senão BUS_CLASS_NAMES (bus+train)."""
        threshold = node_003.BUS_CONF_DEFAULT if conf is None else float(conf)
        rgb = image.convert("RGB")
        predict_kw: dict = {
            "source": rgb,
            "conf": threshold,
            "verbose": False,
        }
        if not self.debug_all_classes:
            predict_kw["classes"] = list(self._class_ids)
        results = self._model.predict(**predict_kw)
        boxes: list[dict] = []
        if not results:
            return boxes
        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return boxes
        xyxy = result.boxes.xyxy.cpu().tolist()
        confs = result.boxes.conf.cpu().tolist()
        cls_ids = result.boxes.cls.cpu().tolist()
        for (x1, y1, x2, y2), score, cls_id in zip(xyxy, confs, cls_ids):
            cid = int(cls_id)
            boxes.append(
                {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                    "conf": float(score),
                    "cls": cid,
                    "name": self._id_to_name.get(cid, str(cid)),
                }
            )
        return boxes
