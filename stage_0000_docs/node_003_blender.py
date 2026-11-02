"""
node_003 — Blender Python API (bpy) index

Blender: 5.2 — C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe
API: https://docs.blender.org/api/current/
Mapa show: node_000_pipeline_mindmap.md

Tasks irmas:
  node_003_blender_import.py
  node_003_blender_modelling.py
  node_003_blender_particle.py
  node_003_blender_texture.py
  node_003_blender_geometry_nodes.py

Headless: blender --background --python path\\to\\script.py
MCP: uvx mcp-for-blender + addon (mcp.json Cursor).
Contrato: bbox detect. Crypto fora.

Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

TASKS = (
    "import",
    "modelling",
    "particle",
    "texture",
    "geometry_nodes",
)

MODULES = {
    "import": "node_003_blender_import.py",
    "modelling": "node_003_blender_modelling.py",
    "particle": "node_003_blender_particle.py",
    "texture": "node_003_blender_texture.py",
    "geometry_nodes": "node_003_blender_geometry_nodes.py",
}

MINDMAP = """
blender_byd
├── import (GLB/FBX Meshy -> Object)
├── modelling (scale, origin, bbox->YOLO)
├── texture (Principled, UV) [opcional domain]
├── particle (emitter/hair FX) [opcional]
├── geometry_nodes (scatter/join) [opcional]
└── render (PNG + label stem)
"""

PASSO_A_PASSO = (
    "1. Abrir Blender 5.2 (ou --background)",
    "2. IMPORT: GLB/FBX Meshy; rename byd_<modelo>_v001",
    "3. MODELLING: metros Z-up; origin; testar bbox camera",
    "4. TEXTURE: paint/maps se precisar (senao skip)",
    "5. PARTICLE / GN: so FX visual; nao gera label",
    "6. Camera + luz + variacao de angulo/frame",
    "7. Render PNG sequence; stem = label .txt",
    "8. Export labels YOLO via modelling.bbox helper",
    "9. Entregar images+labels para node_002 train",
)

CRITICO = ("import", "modelling", "render_labels")
OPCIONAL = ("texture", "particle", "geometry_nodes")


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
    print("modules:", MODULES)
