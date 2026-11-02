# stage_0070_streamlit — briefing

## Objetivo

UI alinhada a `__visuals__/ref_app.jpg` + `__visuals__/hmtl_ref/Recife por zonas.html`:

- mapa Recife esquemático (RPAs suaves, mar Atlântico)
- **grid harmônico** mapa | painel glass (câmeras)
- click câmera → **feed ~70% viewport** (vision + GIF)

Catálogo: `stage_0010_globals` / `cameras_recife_*.json`.

## Entrada

```text
streamlit run main.py
```

## Nodes

| Node | Papel |
|------|--------|
| `node_002_widget_cameras` | fetch + detect + overlay (httpx async) |
| `node_003_visuals` | **knobs** + mapa component + CSS |
| `node_004_layout` | home + multicam (LAYOUT LOCK) |
| `node_005_bench_httpx` | bench tempo/429 Snapshot → `EXPORT/v001/` |

## Knobs (`node_003_visuals`)

- `PANEL_PAGE_SIZE` (9), `GRID_COLS` (3), `MAP_HEIGHT_PX`, `THUMB_WIDTH_PX`, `FEED_WIDTH_VW`
- `CAM_OPEN_LABEL`, `CAM_OPEN_ICON`, `CAM_OPEN_HELP_PREFIX`
- `ZONE_COLORS`, `RPA_ZONES`, `MAP_SMOOTH_AMP`, `MAP_VIEWBOX`
- `TITLE`, `SUBTITLE`, `MAP_PILL`, `MAP_HINT`, `FEED_BACK_LABEL`

## Nav

1. Home LOCK: clique zona no mapa → `?zona=`
2. Zona: grid 3×3 **thumb + Ver câmera** (`st.button`); `>9` → pager
3. Feed: snapshot + detect; Voltar → menu

## Query

- `?zona=norte` — painel na zona
- `?zona=norte&page=1` — página do painel (4 cams)
- `?view=feed&cam=KEY` — fullscreen detect
