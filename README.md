# CESAR Recife (`CESAR-atividade_dashboard`)

Protótipo Streamlit (disciplina **Visualização de Dados**): mapa por zona + multicam CTTU + YOLO em snapshots.

---

## Arquitetura

```text
CESAR-atividade_dashboard/
├── main.py                          # entry: streamlit run main.py
├── pyproject.toml
├── README.md
├── .cursor/rules/
│   ├── layout-lock.mdc              # HOME + MULTICAM + status LOCK
│   ├── so-mexa-no-pedido.mdc
│   └── sempre-versione-antes.mdc
├── stage_0000_docs/                 # estudo (não roda no app)
├── stage_0010_globals/              # catálogo + knobs
│   ├── node_002_scrape.py           # scrape HTML Serttel → JSON
│   ├── node_003_globals.py          # DF_CAMERAS + SNAPSHOT_* + YOLO_* + STYLE_*
│   └── EXPORT/v001/cameras_*.json
├── stage_0021_vision/               # detecção
│   ├── node_002_bus_detector.py     # BusDetector (YOLO)
│   ├── yolo11n.pt
│   └── EXPORT/v001/
├── stage_0031_overlay/              # arte no bbox
│   ├── node_002_bus_overlay.py      # BusOverlay
│   └── assets/                      # GIF/PNG; vazio = sem overlay
└── stage_0070_streamlit/            # UI
    ├── node_007.app.py              # bootstrap (também via main.py)
    ├── node_003_visuals.py          # mapa HTML/CSS, chrome, zones
    ├── node_004_layout.py           # orquestra HOME + MULTICAM
    ├── node_002_widget_cameras.py   # httpx snapshot + vision
    ├── node_005_bench_httpx.py      # afina GAP × WORKERS (anti-429)
    └── __visuals__/html_css/v029/
```

**Papel de cada stage**

```text
stage_0000_docs      →  estudo / briefing (fora do runtime)
stage_0010_globals   →  dados + knobs (fonte única de verdade)
stage_0021_vision    →  JPEG → bboxes
stage_0031_overlay   →  bboxes → frame anotado (GIF/PNG)
stage_0070_streamlit →  UI + orquestração
```

---

## Processo ponta a ponta

```text
CTTU (Serttel)
│
├─1─ scrape HTML ──► EXPORT/v001/cameras_*.json
│                      │
│                      ▼
│                 node_003_globals
│                 DF_CAMERAS[key → id → url Snapshot]
│
├─2─ UI HOME (mapa por zona)
│         clique zona ──► ?zona=<nome>&page=0
│
└─3─ UI MULTICAM (grade 3×3)
          │
          ├─ fetch JPEG async (httpx + GAP + WORKERS)
          ├─ paint cru
          ├─ YOLO (BusDetector) + overlay (BusOverlay)
          └─ paint anotado
```

**Contratos**

```text
BusDetector.detect(PIL)
  └──► list[{x1, y1, x2, y2, conf, cls, name}]

BusOverlay.compose(base, boxes)
  └──► PIL | bytes GIF
```

---

## Navegação do app

```text
main.py
  └── render_app()                    # node_004_layout
        │
        ├─ sem ?zona ──► HOME
        │     rail: brand + Sobre
        │     mapa: SVG zonas (html_css/v029)
        │     clique zona ──► query_params
        │
        └─ ?zona=… ──► MULTICAM
              rail: Voltar + título + status
              frame: banner status + grade 3×3 + pager
              page N ──► 9 câmeras da zona
```

Query:

```text
?zona=norte          → página 0
?zona=norte&page=1   → próxima página (9 cams)
(sem params)         → HOME
```

---

## Pipeline MULTICAM (ordem fixa)

```text
_render_cam_grid
│
├─1─ placeholders na grade
├─2─ fetch async ──► dict[key → PIL cru]
│       status: FETCH_LOADING ↔ FETCH_CONTACTING
│       fim:     FETCH_CONNECTED
├─3─ paint cru (todas as tiles da página)
├─4─ YOLO + overlay por tile
│       status: DETECT_LOADING → DETECT_DONE
└─5─ paint anotado (banner some no fim)
```

Quem faz o quê:

```text
node_004_layout
  ├── orquestra fases + status (rail e quadro branco)
  └── chama widget

node_002_widget_cameras
  ├── CttuSnapshotClient (httpx)
  └── _vision_on_image → detect + overlay

node_003_visuals
  └── mapa, CSS, labels, zones_filtered
```

---

## Knobs (`node_003_globals.py`)

```text
node_003_globals.py
├── Catálogo
│   ├── CAMERAS_JSON
│   ├── DF_CAMERAS
│   └── camera_snapshot_url()
├── Vision                    ← 0021 / 0070
│   ├── YOLO_WEIGHTS
│   ├── BUS_CLASS_*
│   ├── BUS_CONF_DEFAULT
│   └── VISION_DEBUG_ALL_CLASSES
├── Snapshot HTTP             ← layout / widget / bench
│   ├── SNAPSHOT_TIMEOUT_S
│   ├── SNAPSHOT_USER_AGENT
│   ├── SNAPSHOT_FETCH_GAP_S      # default 0.15
│   └── SNAPSHOT_429_RETRIES
├── Overlay                   ← 0031
│   ├── OVERLAY_ASSETS_DIR
│   ├── OVERLAY_ANCHOR
│   └── OVERLAY_SIZE_FRAC
├── UI HOME                   ← visuals
│   ├── STYLE_TITLE / STYLE_HOME_ABOUT_*
│   ├── STYLE_MAP_SEA_STOPS
│   └── STYLE_ZONE_COLORS
└── UI MULTICAM               ← layout + visuals
    ├── STYLE_GRID_* / STYLE_PANEL_PAGE_SIZE
    ├── STYLE_MULTICAM_WORKERS    # default 6
    ├── STYLE_FETCH_*
    └── STYLE_DETECT_*
```

Anti-429: afinar no bench, depois copiar GAP/WORKERS nos knobs.

```bash
python stage_0070_streamlit/node_005_bench_httpx.py
# saída: stage_0070_streamlit/EXPORT/v001/bench_httpx_*
```

---

## Subir o app

Python **≥ 3.13**. Preferir o venv do projeto.

```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/macOS

pip install -e .
streamlit run main.py
```

Deps: `streamlit`, `httpx`, `ultralytics`, `pillow`, `pandas`, `beautifulsoup4`, …

Smoke vision (opcional):

```bash
python stage_0021_vision/node_003_smoke.py
```

---

## Escopo

```text
FAZ
├── scrape / catálogo CTTU
├── snapshot JPEG sob demanda
├── YOLO COCO (bus / train) + overlay opcional
└── UI mapa → multicam paginada + status

NÃO FAZ (runtime atual)
├── treino YOLO / Blender sintético   (só docs em stage_0000)
├── auth / proxy CTTU
└── streaming contínuo de vídeo
```

---

## LAYOUT LOCK

Regra: `.cursor/rules/layout-lock.mdc`. Diagramação e fases de status **congeladas** até unlock.

```text
PODE sem unlock
├── texto STYLE_FETCH_* / STYLE_DETECT_* / About
├── cores, interval, conf
└── bugfix 429 / timeout (sem mudar diagramação)

PRECISA unlock
├── mover rail / pager / quadro branco / colunas
├── fundir fetch+YOLO sem status intermediário
├── slice do SVG / brand flutuando no mapa
└── refator do shell HTML/CSS
```

HTML/CSS versionado: `__visuals__/html_css/v029/` — não sobrescrever; versionar se mudar visual.

---

## Troubleshooting

| Sintoma | Onde olhar |
|---------|------------|
| Muitas cams offline / 429 | `SNAPSHOT_FETCH_GAP_S`, `STYLE_MULTICAM_WORKERS`, `SNAPSHOT_429_RETRIES` + bench |
| Status “travado” | fetch ainda aberto; `CONNECTED` só no fim do gather |
| Grade sem bbox | `BUS_CONF_DEFAULT`, `VISION_DEBUG_ALL_CLASSES`, `YOLO_WEIGHTS` |
| Sem GIF no bus | `OVERLAY_ASSETS_DIR` vazia ou extensão fora de `OVERLAY_IMAGE_EXTS` |
| Mapa / multicam quebrado | LOCK + CSS `v029` |

---

## Docs irmãs

```text
stage_0000_docs/
├── node_000_pipeline_mindmap.md   # mapa histórico (Blender/treino)
└── node_001_briefing.md           # briefing

node_003_globals.py (docstring)    # knob → consumidor
```
