"""
node_003 task: GEOMETRY NODES

API: GeometryNodeTree, NodesModifier, interface sockets, node types
Mapa: node_000_pipeline_mindmap.md | index: node_003_blender.py

OPCIONAL. Scatter/join = 'atrapalhar' sem Particle.
Nao gera label YOLO (label continua da mesh carro).
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

MINDMAP = """
geometry_nodes
├── node_groups.new GeometryNodeTree
├── interface INPUT/OUTPUT Geometry
├── Group Input -> nodes -> Group Output
├── modifier NODES no Object
└── Realize Instances se precisar mesh real
"""

PASSO_A_PASSO = (
    "1. Confirmar necessidade: scatter/FX procedural? senao skip",
    "2. bpy.data.node_groups.new(name, 'GeometryNodeTree')",
    "3. interface.clear(); new_socket Geometry INPUT + OUTPUT",
    "4. nodes: GroupInput, GroupOutput (+ Distribute/Instance/Join)",
    "5. links.new ate Geometry chegar no Group Output",
    "6. obj.modifiers.new(..., 'NODES'); mod.node_group = tree",
    "7. Viewport: geometria aparece? Spreadsheet/Viewer se falhar",
    "8. Realize Instances se export/bake mesh",
    "9. Labels YOLO: sempre da mesh do carro, nao das instances",
)

GEOMETRY_NODES_NOTES = """
Blender 4+/5: tree.interface.new_socket (nao tree.inputs legado).
Join Geometry aceita multiplas conexoes no input Geometry.
Object Info transform_space = RELATIVE pra mundo coerente.
"""

API_CHEAT = {
    "new_tree": "ng=bpy.data.node_groups.new('GN_Name', 'GeometryNodeTree')",
    "socket_in": "ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')",
    "socket_out": "ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')",
    "modifier": "mod=obj.modifiers.new('GN', 'NODES'); mod.node_group=ng",
    "group_io": "ni=ng.nodes.new('NodeGroupInput'); no=ng.nodes.new('NodeGroupOutput')",
    "link": "ng.links.new(a.outputs[0], b.inputs[0])",
    "apply_mod": "bpy.ops.object.modifier_apply(modifier='GN')",
}

NODE_TYPE_INDEX = [
    "NodeGroupInput",
    "NodeGroupOutput",
    "GeometryNodeDistributePointsOnFaces",
    "GeometryNodeInstanceOnPoints",
    "GeometryNodeRealizeInstances",
    "GeometryNodeJoinGeometry",
    "GeometryNodeTransformGeometry",
    "GeometryNodeObjectInfo",
    "GeometryNodeMeshToPoints",
    "GeometryNodeDeleteGeometry",
    "GeometryNodeViewer",
    "FunctionNodeRandomValue",
    "GeometryNodeInputPosition",
]


def example_empty_gn_modifier(obj_name: str, group_name: str = "GN_PassThrough") -> str:
    """Passos 2-6: GN passthrough (smoke test)."""
    return f'''
import bpy

obj = bpy.data.objects["{obj_name}"]
ng = bpy.data.node_groups.new("{group_name}", "GeometryNodeTree")

ng.interface.clear()
ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

n_in = ng.nodes.new("NodeGroupInput")
n_out = ng.nodes.new("NodeGroupOutput")
n_in.location = (-200, 0)
n_out.location = (200, 0)
ng.links.new(n_in.outputs["Geometry"], n_out.inputs["Geometry"])

mod = obj.modifiers.new(name="{group_name}", type="NODES")
mod.node_group = ng
print("GN on", obj.name, ng.name)
'''


def example_scatter_on_faces(obj_name: str, instance_name: str, density: float = 5.0) -> str:
    """
    Passos 4-8: scatter de props (atrapalhar).

    1. target = chao/mesh; instance = prop
    2. Distribute Points on Faces -> Instance on Points
    3. Realize + Join com geometria base
    4. Carro continua objeto separado pra bbox
    """
    return f'''
import bpy

target = bpy.data.objects["{obj_name}"]
inst = bpy.data.objects["{instance_name}"]

ng = bpy.data.node_groups.new("GN_Scatter", "GeometryNodeTree")
ng.interface.clear()
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

nodes = ng.nodes
links = ng.links
n_in = nodes.new("NodeGroupInput")
n_out = nodes.new("NodeGroupOutput")
dist = nodes.new("GeometryNodeDistributePointsOnFaces")
dist.inputs["Density"].default_value = {density}
objinfo = nodes.new("GeometryNodeObjectInfo")
objinfo.inputs["Object"].default_value = inst
objinfo.transform_space = "RELATIVE"
iop = nodes.new("GeometryNodeInstanceOnPoints")
real = nodes.new("GeometryNodeRealizeInstances")
join = nodes.new("GeometryNodeJoinGeometry")

links.new(n_in.outputs["Geometry"], dist.inputs["Mesh"])
links.new(dist.outputs["Points"], iop.inputs["Points"])
links.new(objinfo.outputs["Geometry"], iop.inputs["Instance"])
links.new(iop.outputs["Instances"], real.inputs["Geometry"])
links.new(n_in.outputs["Geometry"], join.inputs["Geometry"])
links.new(real.outputs["Geometry"], join.inputs["Geometry"])
links.new(join.outputs["Geometry"], n_out.inputs["Geometry"])

mod = target.modifiers.new("GN_Scatter", "NODES")
mod.node_group = ng
'''


def example_object_info_join(base_name: str, other_name: str) -> str:
    """Passo 4 alternativo: Join via Object Info."""
    return f'''
import bpy
base = bpy.data.objects["{base_name}"]
ng = bpy.data.node_groups.new("GN_JoinObj", "GeometryNodeTree")
ng.interface.clear()
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
n_in = ng.nodes.new("NodeGroupInput")
n_out = ng.nodes.new("NodeGroupOutput")
info = ng.nodes.new("GeometryNodeObjectInfo")
info.inputs["Object"].default_value = bpy.data.objects["{other_name}"]
info.transform_space = "RELATIVE"
join = ng.nodes.new("GeometryNodeJoinGeometry")
ng.links.new(n_in.outputs["Geometry"], join.inputs["Geometry"])
ng.links.new(info.outputs["Geometry"], join.inputs["Geometry"])
ng.links.new(join.outputs["Geometry"], n_out.inputs["Geometry"])
mod = base.modifiers.new("GN_JoinObj", "NODES")
mod.node_group = ng
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
