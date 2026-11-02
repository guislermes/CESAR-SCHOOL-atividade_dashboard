"""Decision palette: verde default; abaixo de 0.75 baixa a saturação."""

from __future__ import annotations

import colorsys

# Verde default (conf >= CONF_GREEN_FULL). Abaixo: mesmo hue, menos saturação.
decision_pallete = [
    "#48F233",
]

CONF_GREEN_FULL = 0.75


class DecisionPalette:
    """conf >= 0.75 → verde cheio; conf menor → desatura o mesmo verde."""

    GREEN_HEX = decision_pallete[0]
    CONF_FULL = CONF_GREEN_FULL

    @classmethod
    def hex_to_rgb(cls, hex_color: str) -> tuple[int, int, int]:
        h = hex_color.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @classmethod
    def rgb_to_hex(cls, rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @classmethod
    def saturation_factor(cls, conf: float) -> float:
        c = max(0.0, min(1.0, float(conf)))
        if c >= cls.CONF_FULL:
            return 1.0
        return c / cls.CONF_FULL

    @classmethod
    def rgb_for_conf(cls, conf: float) -> tuple[int, int, int]:
        r, g, b = cls.hex_to_rgb(cls.GREEN_HEX)
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        s *= cls.saturation_factor(conf)
        rn, gn, bn = colorsys.hsv_to_rgb(h, s, v)
        return (int(round(rn * 255)), int(round(gn * 255)), int(round(bn * 255)))

    @classmethod
    def hex_for_conf(cls, conf: float) -> str:
        return cls.rgb_to_hex(cls.rgb_for_conf(conf))
