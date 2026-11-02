"""
node_003 task: TEXTURE / MATERIAL

API: materials, Principled BSDF, ShaderNodeTexImage, UV
Mapa: node_000_pipeline_mindmap.md | index: node_003_blender.py

OPCIONAL pro domain gap. Bbox nao depende de texture.
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

MINDMAP = """
texture
├── material.use_nodes = True
├── Principled BSDF
├── Image Texture (sRGB vs Non-Color)
├── UV unwrap / smart_project
└── assign slot no Object
"""

PASSO_A_PASSO = (
    "1. Decidir: texture ajuda dominio real? senao skip task",
    "2. materials.new; use_nodes=True",
    "3. Pegar/criar Principled BSDF + Material Output",
    "4. Base Color / Metallic / Roughness (car paint)",
    "5. Se mapa: ShaderNodeTexImage + load; colorspace certo",
    "6. links.new tex -> bsdf input",
    "7. UV: EDIT + smart_project se mesh Meshy sem UV util",
    "8. Assign material no obj.data.materials[0]",
    "9. Render smoke test 1 frame antes do batch",
)

TEXTURE_NOTES = """
Color = sRGB. Rough/Metal/Normal = Non-Color.
Bake Cycles so se precisar maps; fora do caminho critico YOLO.
"""

API_CHEAT = {
    "new_mat": "mat=bpy.data.materials.new(name); mat.use_nodes=True; nt=mat.node_tree",
    "principled": "nt.nodes.get('Principled BSDF')",
    "img_tex": "n=nt.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(path)",
    "link": "nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])",
    "assign": "obj.data.materials.clear(); obj.data.materials.append(mat)",
    "load_image": "bpy.data.images.load(filepath, check_existing=True)",
    "pack": "image.pack()",
}


def example_principled_car_paint(mat_name: str, hex_rgb=(0.02, 0.1, 0.35), metallic: float = 0.8, roughness: float = 0.25) -> str:
    """Passos 2-4: car paint basico."""
    r, g, b = hex_rgb
    return f'''
import bpy

mat = bpy.data.materials.new(name="{mat_name}")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = ({r}, {g}, {b}, 1.0)
bsdf.inputs["Metallic"].default_value = {metallic}
bsdf.inputs["Roughness"].default_value = {roughness}
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
out.location = (300, 0)
bsdf.location = (0, 0)
'''


def example_image_texture(mat_name: str, image_path: str) -> str:
    """Passos 5-6: mapa de cor."""
    return f'''
import bpy

mat = bpy.data.materials.get("{mat_name}") or bpy.data.materials.new("{mat_name}")
mat.use_nodes = True
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(r"{image_path}", check_existing=True)
tex.image.colorspace_settings.name = "sRGB"
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
'''


def example_assign_material(obj_name: str, mat_name: str) -> str:
    """Passo 8: assign."""
    return f'''
import bpy
obj = bpy.data.objects["{obj_name}"]
mat = bpy.data.materials["{mat_name}"]
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
'''


def example_smart_uv(obj_name: str) -> str:
    """Passo 7: UV se faltar."""
    return f'''
import bpy
obj = bpy.data.objects["{obj_name}"]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
