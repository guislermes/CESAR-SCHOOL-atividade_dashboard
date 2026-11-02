# stage_0031_overlay — briefing

## Objetivo

Compositar imagem/GIF de alerta sobre cada bbox de ônibus detectado.
Pasta de assets vazia → passa a imagem original (sem overlay).

## Estilo

- Classe `BusOverlay` (sem funções soltas amontoadas).
- Knobs em `stage_0010_globals/node_003_globals.py`.
- Enum `OverlayAnchor`: `top` | `right` | `left` | `bottom`.

## Contrato

`BusOverlay.compose(base, boxes) -> PIL.Image | bytes (GIF)`

- `boxes`: `list[{x1,y1,x2,y2,conf}]` do `BusDetector`.
- Zero boxes ou pasta `OVERLAY_ASSETS_DIR` vazia → still original.
- Vários buses → um overlay por bbox, timeline sincronizada se GIF.
