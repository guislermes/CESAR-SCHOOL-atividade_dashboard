# stage_0021_vision — briefing

## Objetivo

Detectar **ônibus** em snapshots reais CTTU (Recife) com modelo vision **pré-treinado**,
integrar no Streamlit (`stage_0070`) e, se houver bbox, compositar um GIF animado
(`stage_0031_overlay`) em cima de cada bbox. Sem treino. Sem Blender neste caminho.

## Estilo de código

- **Classes**, não funções soltas amontoadas no módulo — isso deixa o fluxo bizarramente confuso.
- Um responsável claro por arquivo: `BusDetector` (0021), `BusOverlay` (0031), widget/app (0070).
- Parâmetros essenciais (paths, conf default, timeout, nome da classe COCO, asset GIF) vivem como
  **variáveis** em `stage_0010_globals/node_003_globals.py` — sem class de knobs; stages em classes.
- `stage_0021` **não** importa `streamlit`. Cache do modelo (`@st.cache_resource`) só no **0070**.

## Domínio

- Câmera fixa de trânsito (CTTU / Serttel).
- Input visual: JPEG sujo de snapshot IP (não render sintético).
- Target com UI: COCO class `bus`.
- Distractors (car, truck, person, …): detectáveis pelo modelo, **sem** overlay / sem destaque.

## Fluxo (quem → contrato → quem)

1. `stage_0010` JSON `cameras_recife_27_10_2026.json` → key → `id_camera`
2. `node_003_globals` → `DF_CAMERAS.url` + knobs (`YOLO_WEIGHTS`, `BUS_CLASS_NAME`, …)
3. `stage_0070` selectbox → fetch JPEG → `PIL.Image`
4. `stage_0021` `BusDetector.detect(image)` → `list[{x1,y1,x2,y2,conf}]`
5. `stage_0031_overlay` `BusOverlay.compose(...)` (se bboxes e toggle on) → GIF bytes
6. `st.image` mostra GIF ou still; `st.caption` = count de buses

## Knobs em `node_003_globals` (variáveis)

| Param | Papel |
|-------|--------|
| `YOLO_WEIGHTS` | `stage_0021_vision/yolo11n.pt` (COCO; não `best.pt` Dolphin) |
| `BUS_CLASS_NAME` | `"bus"` (filtro por nome; COCO id 5 só referência) |
| `BUS_CONF_DEFAULT` | threshold default do detect |
| `SNAPSHOT_TIMEOUT_S` | timeout do fetch JPEG |
| `SNAPSHOT_USER_AGENT` | UA de browser no request |
| `OVERLAY_ASSETS_DIR` | pasta de artes `stage_0031_overlay/assets/` (vazia = sem overlay) |
| `OVERLAY_ANCHOR` | enum `OverlayAnchor`: top / right / left / bottom |
| `SMOKE_EXPORT` | pasta contact sheet `stage_0021_vision/EXPORT/v001/` |

## stage_0021_vision (este stage)

- Classe `BusDetector`: carrega `YOLO_WEIGHTS`; `detect(image, conf=None)` usa
  `BUS_CONF_DEFAULT` se `conf` omitido; retorna só `BUS_CLASS_NAME`.
- Return: `list[dict]` keys `x1, y1, x2, y2, conf` (pixels da imagem de entrada).
- Sem training. Smoke: 3–5 câmeras → contact sheet com bbox em `SMOKE_EXPORT`.

## stage_0031_overlay

- Classe `BusOverlay` em `stage_0031_overlay`: assets em `OVERLAY_ASSETS_DIR`, âncora `OVERLAY_ANCHOR`.
- Pasta vazia → still original (validador `resolve_asset`).
- Âncora ao redor do bbox: `top` / `right` / `left` / `bottom`.
- Zero detections → still original; vários buses → um overlay por bbox.

## stage_0070 (integração)

- Sidebar: conf slider, camera selectbox, toggle overlay.
- Uma câmera por vez (não iterar o JSON inteiro na UI).
- Timeout/falha de fetch: aviso na câmera atual; não derruba o app.
## Aceite

- [ ] Smoke 0021: pelo menos 1 frame Recife com bbox `bus` plausível
- [ ] `st.image` mostra still anotado ou GIF quando toggle + bus
- [ ] Sem bus / toggle off: snapshot limpo (default: limpo se overlay off e sem draw debug)
- [ ] Knobs só via variáveis do globals; stages em classes
