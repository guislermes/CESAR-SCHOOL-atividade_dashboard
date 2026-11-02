"""
node_003 task: PARTICLE

API: modifiers PARTICLE_SYSTEM, ParticleSettings (EMITTER / HAIR)
Mapa: node_000_pipeline_mindmap.md | index: node_003_blender.py

OPCIONAL. Nao gera label YOLO. Nao substitui crypto.
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

MINDMAP = """
particle
├── mesh alvo selecionado
├── modifier PARTICLE_SYSTEM
├── settings EMITTER | HAIR
├── render HALO | OBJECT | COLLECTION
└── bake cache se animado
"""

PASSO_A_PASSO = (
    "1. Confirmar: label YOLO ja sai da mesh (modelling). Particle = FX so",
    "2. Selecionar mesh emissora",
    "3. modifiers.new(..., type='PARTICLE_SYSTEM')",
    "4. settings.type = EMITTER ou HAIR",
    "5. count / lifetime / emit_from (FACE tipico)",
    "6. render_type; se OBJECT, setar instance_object",
    "7. Viewport check; bake cache se frame_start != frame_end",
    "8. Render beauty; labels continuam da mesh, nao das particulas",
)

PARTICLE_NOTES = """
EMITTER = pontos/objetos no tempo. HAIR = fios.
psys = obj.particle_systems[-1]; ps = psys.settings
Depsgraph se ler geometria avaliada.
"""

API_CHEAT = {
    "add_psys": "mod=obj.modifiers.new(name='PS', type='PARTICLE_SYSTEM'); psys=obj.particle_systems[-1]",
    "settings": "ps = psys.settings",
    "emitter": "ps.type='EMITTER'; ps.count=1000; ps.frame_start=1; ps.frame_end=1; ps.lifetime=50",
    "hair": "ps.type='HAIR'; ps.hair_length=0.2",
    "emit_from": "ps.emit_from='FACE'",
    "render_object": "ps.render_type='OBJECT'; ps.instance_object=other_obj",
    "remove": "obj.modifiers.remove(mod)",
}


def example_emitter_on_car(obj_name: str, count: int = 500) -> str:
    """Passos 2-6: emitter simples no carro."""
    return f'''
import bpy

obj = bpy.data.objects["{obj_name}"]
mod = obj.modifiers.new(name="PS_Emitter", type="PARTICLE_SYSTEM")
psys = obj.particle_systems[-1]
ps = psys.settings
ps.name = "PS_{obj_name}"
ps.type = "EMITTER"
ps.count = {count}
ps.frame_start = 1
ps.frame_end = 1
ps.lifetime = 25
ps.emit_from = "FACE"
ps.normal_factor = 0.05
ps.render_type = "HALO"
ps.particle_size = 0.02
print("particle", ps.name, "on", obj.name)
'''


def example_hair(obj_name: str) -> str:
    """Passo 4 alternativo: HAIR."""
    return f'''
import bpy
obj = bpy.data.objects["{obj_name}"]
obj.modifiers.new(name="PS_Hair", type="PARTICLE_SYSTEM")
ps = obj.particle_systems[-1].settings
ps.type = "HAIR"
ps.hair_length = 0.15
ps.count = 2000
ps.child_type = "INTERPOLATED"
'''


def example_instance_collection(emitter_name: str, instance_obj_name: str) -> str:
    """Passo 6: render como objeto."""
    return f'''
import bpy
emitter = bpy.data.objects["{emitter_name}"]
inst = bpy.data.objects["{instance_obj_name}"]
ps = emitter.particle_systems[-1].settings
ps.render_type = "OBJECT"
ps.instance_object = inst
ps.particle_size = 1.0
ps.use_scale_instance = True
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
