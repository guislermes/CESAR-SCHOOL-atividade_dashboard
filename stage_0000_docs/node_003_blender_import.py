"""
node_003 task: IMPORT

API: bpy.ops.import_scene.gltf/fbx, wm.obj_import, wm.alembic_import, wm.usd_import
Mapa: node_000_pipeline_mindmap.md | index: node_003_blender.py

Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

MINDMAP = """
import
├── escolher formato (GLB preferido Meshy)
├── bpy.ops.import_scene.*
├── diff objects before/after
├── rename byd_<modelo>_v001
└── collection COL_BYD
"""

PASSO_A_PASSO = (
    "1. Fechar/duplicar cena limpa ou collection vazia COL_BYD",
    "2. Anotar set(bpy.data.objects.keys()) ANTES do import",
    "3. Importar GLB (preferido) ou FBX do Meshy",
    "4. Diff: objetos novos = importados",
    "5. Active = root mesh; rename byd_<modelo>_v001",
    "6. Mover para COL_BYD; aplicar scale se unidade errada",
    "7. Gate visual: lateral + 3/4 frente + 3/4 tras",
)

IMPORT_NOTES = """
GLTF/GLB — materials embutidos; rename na hora.
FBX — checar apply_transform / bake scale; armature aparte se so precisa casca.
Escala — Blender Z-up metros; transform_apply scale se minúsculo/gigante.
Append/Link — bpy.ops.wm.append / link para .blend interno.
"""

API_CHEAT = {
    "gltf": "bpy.ops.import_scene.gltf(filepath, filter_glob='*.glb;*.gltf')",
    "fbx": "bpy.ops.import_scene.fbx(filepath, ...)",
    "obj": "bpy.ops.wm.obj_import(filepath)",
    "alembic": "bpy.ops.wm.alembic_import(filepath, as_background_job=False)",
    "usd": "bpy.ops.wm.usd_import(filepath)",
    "append_blend": "bpy.ops.wm.append(filepath=blend_and_datablock_path)",
    "link_blend": "bpy.ops.wm.link(filepath=...)",
    "collections": "bpy.data.collections.new(name); bpy.context.scene.collection.children.link(col)",
    "move_to_col": "col.objects.link(obj); old.objects.unlink(obj)",
}


def example_import_glb(filepath: str, object_name: str) -> str:
    """
    Passos 2-5: import GLB + rename.

    1. filepath = export Meshy .glb
    2. Colar no Blender Text / MCP / --python
    3. Conferir nome no Outliner
    """
    return f'''
import bpy
from pathlib import Path

fp = r"{filepath}"
before = set(bpy.data.objects.keys())
bpy.ops.import_scene.gltf(filepath=fp)
new = [n for n in bpy.data.objects.keys() if n not in before]
for name in new:
    obj = bpy.data.objects[name]
    obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects[new[0]]
bpy.context.view_layer.objects.active.name = "{object_name}"
print("imported", new, "->", "{object_name}")
'''


def example_import_fbx(filepath: str) -> str:
    """Passo 3 alternativo: FBX."""
    return f'''
import bpy
bpy.ops.import_scene.fbx(
    filepath=r"{filepath}",
    automatic_bone_orientation=True,
    use_image_search=True,
)
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
