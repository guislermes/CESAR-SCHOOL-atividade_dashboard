"""
node_003 task: MODELLING

API: Object/Mesh/bmesh, transform, bound_box, world_to_camera_view
Mapa: node_000_pipeline_mindmap.md | index: node_003_blender.py

Critico pro dataset: bbox projetado -> label YOLO.
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

MINDMAP = """
modelling
├── Object vs Mesh
├── transform / matrix_world
├── origin + apply scale
├── bmesh edit (se precisar)
└── bound_box -> camera -> YOLO txt
"""

PASSO_A_PASSO = (
    "1. Object mesh ativo; type == MESH",
    "2. Ajustar location/rotation/scale; unidade = metros",
    "3. origin_set ORIGIN_GEOMETRY se pivot errado",
    "4. transform_apply scale se animacao/particle quebrar",
    "5. Scene.camera definida; resolution = imgsz alvo (ex 640)",
    "6. Rodar example_bbox_to_yolo_camera",
    "7. Clamp xyxy na frame; gravar labels/<stem>.txt",
    "8. Repetir por frame/angulo da sequencia de render",
)

MODELLING_NOTES = """
Object = transform/parent/modifiers. Mesh = vertices/edges/faces.
obj.matrix_world = local->world. bound_box = 8 cantos local.
EDIT mode: bmesh.from_edit_mesh. OBJECT: bmesh.from_mesh / to_mesh.
"""

API_CHEAT = {
    "new_mesh_obj": "mesh=bpy.data.meshes.new(n); obj=bpy.data.objects.new(n, mesh); bpy.context.collection.objects.link(obj)",
    "select_active": "obj.select_set(True); bpy.context.view_layer.objects.active = obj",
    "duplicate": "bpy.ops.object.duplicate(linked=False)",
    "join": "bpy.ops.object.join()",
    "delete": "bpy.data.objects.remove(obj, do_unlink=True)",
    "bmesh_create": "bm=bmesh.new(); bm.from_mesh(mesh); ...; bm.to_mesh(mesh); bm.free()",
    "bmesh_edit": "bm=bmesh.from_edit_mesh(mesh); ...; bmesh.update_edit_mesh(mesh)",
    "shade_smooth": "bpy.ops.object.shade_smooth()",
    "bound_box": "obj.bound_box  # 8 cantos local",
}


def example_world_bbox(obj_name: str) -> str:
    """Passos 1-2: AABB world do carro."""
    return f'''
import bpy
from mathutils import Vector

obj = bpy.data.objects["{obj_name}"]
corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
xs = [c.x for c in corners]; ys = [c.y for c in corners]; zs = [c.z for c in corners]
print(min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
'''


def example_bbox_to_yolo_camera(obj_name: str, cam_name: str = "Camera") -> str:
    """
    Passos 5-7: projetar bound_box na camera -> cx cy w h.

    1. Camera = scene.camera
    2. world_to_camera_view em cada canto
    3. min/max -> xyxy pixel (Y flip)
    4. normalizar; gravar com class_id
    """
    return f'''
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

scene = bpy.context.scene
cam = bpy.data.objects["{cam_name}"]
obj = bpy.data.objects["{obj_name}"]
scene.camera = cam

res_x = scene.render.resolution_x
res_y = scene.render.resolution_y
scale = scene.render.resolution_percentage / 100.0
w = int(res_x * scale)
h = int(res_y * scale)

corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
co_ndc = [world_to_camera_view(scene, cam, c) for c in corners]
xs = [v.x for v in co_ndc]
ys = [v.y for v in co_ndc]
x1 = max(0.0, min(xs)) * w
x2 = min(1.0, max(xs)) * w
y1 = max(0.0, (1.0 - max(ys))) * h
y2 = min(1.0, (1.0 - min(ys))) * h
cx = ((x1 + x2) / 2) / w
cy = ((y1 + y2) / 2) / h
bw = (x2 - x1) / w
bh = (y2 - y1) / h
print("yolo", cx, cy, bw, bh)
'''


def example_bmesh_extrude() -> str:
    """Opcional: editar topologia (nao necessario pro bbox)."""
    return '''
import bpy, bmesh
obj = bpy.context.object
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
faces = [f for f in bm.faces if f.select]
ret = bmesh.ops.extrude_face_region(bm, geom=faces)
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
