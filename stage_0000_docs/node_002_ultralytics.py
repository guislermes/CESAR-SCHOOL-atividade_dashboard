"""
node_002 — Ultralytics (YOLO)

Markdown: node_002_ultralytics.md
Mapa show: node_000_pipeline_mindmap.md

Contrato: detection (classe + bbox). 1x .pt, 3 classes BYD.
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

ULTRALYTICS_VERSION = "8.4.191"
TASK = "detect"
DEFAULT_WEIGHTS = "yolo11n.pt"
MODES = ("train", "val", "predict", "export", "track", "benchmark")

MINDMAP = """
ultralytics_detect
├── setup (venv, pip, version)
├── dataset (images, labels, data.yaml)
├── train (yolo11n, epochs, best.pt)
├── val (map50 por classe)
├── predict (webcam, boxes)
└── app (Streamlit, filter class)
"""

PASSO_A_PASSO = (
    "1. .venv ativo; import ultralytics == 8.4.191",
    "2. Criar images/train|val e labels/train|val (stem igual)",
    "3. Escrever data.yaml com path + names 0..2",
    "4. Validar 1 label manual: class_id cx cy w h em 0-1",
    "5. train -> anotar runs/.../weights/best.pt",
    "6. val -> map50 por classe; reforcar classe fraca",
    "7. predict source=0 stream=True; ler xyxy/conf/cls",
    "8. App: 1x best.pt; CSS + classes=[id] por modelo",
)

CONCEPTS = {
    "model": "Wrapper YOLO (.pt / .yaml)",
    "task": "detect | segment | classify | pose | obb",
    "mode": "train | val | predict | export | track | benchmark",
    "data.yaml": "paths + names de classe",
    "imgsz": "lado resize (ex. 640)",
    "batch": "imagens por step",
    "epochs": "passes no train",
    "device": "cpu | 0 | 0,1 | mps",
    "project/name": "pasta runs",
    "weights": "checkpoint .pt",
}

DATASET_LAYOUT = """
datasets/byd/
  images/train|val|test/
  labels/train|val|test/
  data.yaml
"""

DATA_YAML_EXAMPLE = """
path: datasets/byd
train: images/train
val: images/val
test: images/test
names:
  0: byd_model_a
  1: byd_model_b
  2: byd_model_c
"""

LABEL_LINE = "class_id cx cy w h   # todos normalizados 0-1"

API_CHEAT = {
    "load": 'YOLO("yolo11n.pt") | YOLO("best.pt") | YOLO("yolo11n.yaml")',
    "train": "model.train(data=..., epochs=..., imgsz=640, batch=..., device=...)",
    "val": "model.val(data=...)",
    "predict": "model.predict(source=0|path|url, stream=True, conf=0.35, classes=[0])",
    "track": 'model.track(source=0, persist=True, tracker="bytetrack.yaml")',
    "export": 'model.export(format="onnx"|"engine"|"torchscript")',
    "boxes": "r.boxes.xyxy | .xywh | .xyxyn | .xywhn | .conf | .cls | .id",
    "plot": "r.plot()  # BGR anotado",
    "callback": 'model.add_callback("on_train_epoch_end", fn)',
    "settings": "yolo settings | %APPDATA%\\\\Ultralytics\\\\settings.json",
}

COMMON_ERRORS = {
    "Dataset not found": "path/train no yaml vs cwd",
    "mAP 0": "label fora 0-1, class_id >= nc, stem imagem!=label",
    "CUDA OOM": "baixar batch/imgsz ou usar yolo11n",
    "webcam fail": "source index errado / camera ocupada",
    "classes invertidas": "ordem names != ids nos .txt",
}


def xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h):
    """
    Passo: converter bbox pixel (x1,y1,x2,y2) -> linha YOLO.

    1. Conferir img_w/img_h da frame renderizada.
    2. Chamar esta func.
    3. Gravar: f\"{class_id} {cx} {cy} {w} {h}\\n\" no .txt stem da imagem.
    """
    cx = ((x1 + x2) / 2) / img_w
    cy = ((y1 + y2) / 2) / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    return cx, cy, w, h


def example_install() -> str:
    """Passo 1 do PASSO_A_PASSO: instalar e checar versao."""
    return r"""
.\.venv\Scripts\python.exe -m pip install ultralytics
.\.venv\Scripts\python.exe -c "import ultralytics; print(ultralytics.__version__)"
"""


def example_cli_train() -> str:
    """Passos 5-7 via CLI."""
    return """
yolo detect train data=datasets/byd/data.yaml model=yolo11n.pt epochs=100 imgsz=640 batch=16 device=0
yolo detect val model=runs/detect/train/weights/best.pt data=datasets/byd/data.yaml
yolo detect predict model=best.pt source=0
yolo export model=best.pt format=onnx
"""


def example_train(data_yaml: str = "datasets/byd/data.yaml", epochs: int = 100) -> str:
    """
    Passo 5: treino Python.

    1. data.yaml existe e paths resolvem a partir do cwd.
    2. Rodar este snippet no .venv.
    3. Guardar caminho de weights/best.pt.
    """
    return f'''
from ultralytics import YOLO

model = YOLO("{DEFAULT_WEIGHTS}")
results = model.train(
    data="{data_yaml}",
    epochs={epochs},
    imgsz=640,
    batch=16,
    device=0,
    project="runs/byd",
    name="detect_v001",
    patience=50,
    pretrained=True,
)
'''


def example_val(weights: str = "best.pt", data_yaml: str = "datasets/byd/data.yaml") -> str:
    """Passo 6: validacao e metricas por classe."""
    return f'''
from ultralytics import YOLO
model = YOLO("{weights}")
metrics = model.val(data="{data_yaml}")
print(metrics.box.map, metrics.box.map50, metrics.box.maps)
'''


def example_predict_webcam(weights: str = "best.pt", conf: float = 0.35, class_ids=None) -> str:
    """
    Passos 7-8: webcam + filtro de classe (Streamlit).

    1. Abrir camera (source=0).
    2. stream=True no loop.
    3. class_ids=[n] quando sidebar escolhe um BYD.
    """
    return f'''
from ultralytics import YOLO

model = YOLO("{weights}")
results = model.predict(
    source=0,
    conf={conf},
    iou=0.5,
    imgsz=640,
    stream=True,
    classes={class_ids!r},
    verbose=False,
)
for r in results:
    if r.boxes is None:
        continue
    xyxy = r.boxes.xyxy.cpu().numpy()
    confs = r.boxes.conf.cpu().numpy()
    cls = r.boxes.cls.cpu().numpy()
    names = r.names
'''


def example_export(weights: str = "best.pt", fmt: str = "onnx") -> str:
    """Opcional pos-passo 6: export deploy."""
    return f'''
from ultralytics import YOLO
model = YOLO("{weights}")
model.export(format="{fmt}", dynamic=False, simplify=True)
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
