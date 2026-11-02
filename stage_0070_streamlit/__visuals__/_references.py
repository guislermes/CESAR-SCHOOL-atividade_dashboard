"""Reexport: fonte da palette é stage_0031_overlay/__visuals__."""

from __future__ import annotations

import sys
from pathlib import Path

_OVERLAY = Path(__file__).resolve().parents[2] / "stage_0031_overlay"
if str(_OVERLAY) not in sys.path:
    sys.path.insert(0, str(_OVERLAY))

from __visuals__._references import DecisionPalette, decision_pallete

__all__ = ["DecisionPalette", "decision_pallete"]
