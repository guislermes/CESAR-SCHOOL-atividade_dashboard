"""
node_object_detection — Ultralytics YOLO + OpenCV

Markdown: node_object_detection.md
Cheat curto: node_002_ultralytics.py
Mapa show: node_000_pipeline_mindmap.md

Contrato: detection (classe + bbox). OpenCV = I/O BGR + desenho.
Regra: sem PASSO_A_PASSO documentado = nao e script.
"""

ULTRALYTICS_PACKAGE = "ultralytics"  # pip install ultralytics
# ultralytics_platform = dependencia interna; NAO e de onde se importa YOLO

IMPORT_OK = "from ultralytics import YOLO"
IMPORT_BAD = (
    "from ultralytics_platform import YOLO",  # errado
    "import YOLO",
    "from ultralytics import yolo",
)

DEFAULT_WEIGHTS = "yolo11n.pt"
TASK = "detect"
CLASS_NAMES_DOLPHIN = {0: "dolphin", 1: "trouble"}

MINDMAP = """
object_detection
├── install (pip ultralytics → puxa opencv + torch)
├── import (from ultralytics import YOLO)
├── dataset (images + labels + data.yaml)
├── train / val (best.pt)
├── predict (boxes.xyxy conf cls)
└── opencv (imread BGR, rectangle, putText, st.image RGB)
"""

PASSO_A_PASSO = (
    "1. .venv do kernel; pip install ultralytics",
    "2. from ultralytics import YOLO  (nunca ultralytics_platform)",
    "3. YOLO_MODEL = 'yolo11n.pt' ou path best.pt (string sua)",
    "4. model = YOLO(YOLO_MODEL)",
    "5. train(data=data.yaml, ...) → EXPORT/.../weights/best.pt",
    "6. predict → r.boxes.xyxy / conf / cls",
    "7. cv2.rectangle + putText OU r.plot()",
    "8. Streamlit: st.image(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))",
)

API_CHEAT = {
    "install": r".\.venv\Scripts\python.exe -m pip install ultralytics",
    "import": "from ultralytics import YOLO",
    "load": 'YOLO("yolo11n.pt") | YOLO("best.pt")',
    "train": "model.train(data=..., epochs=..., imgsz=480, batch=8, device=0|\"cpu\")",
    "val": "model.val(data=...)",
    "predict": "model.predict(source=path|bgr|0, conf=0.35, classes=[0])",
    "boxes": "r.boxes.xyxy | .conf | .cls | .xywhn",
    "plot_yolo": "r.plot()  # BGR anotado",
    "cv2_read": "cv2.imread(path)  # BGR",
    "cv2_draw": "cv2.rectangle(img, (x1,y1), (x2,y2), (B,G,R), 2)",
    "cv2_text": "cv2.putText(img, text, org, font, 0.5, color, 1)",
    "to_rgb": "cv2.cvtColor(img, cv2.COLOR_BGR2RGB)",
}

COMMON_ERRORS = {
    "No module named 'ultralytics'": "kernel != venv; pip install no python do notebook",
    "No module named 'ultralytics_platform' / ImportError YOLO": "use from ultralytics import YOLO",
    "NameError YOLO_MODEL": "definir string na celula HYPERS antes do train",
    "CUDA OOM": 'device="cpu" ou batch/imgsz menor',
    "boxes vazios": "conf alto demais / classe errada / domain gap",
}


def example_import_and_train() -> str:
    return '''
from ultralytics import YOLO

YOLO_MODEL = "yolo11n.pt"
model = YOLO(YOLO_MODEL)
model.train(
    data=r"C:\\Python\\CESAR-atividade_dashboard\\stage_0030_training\\EXPORT\\V001\\data.yaml",
    epochs=50,
    imgsz=480,
    batch=8,
    device=0,
    project=r"C:\\Python\\CESAR-atividade_dashboard\\stage_0030_training\\EXPORT\\V001",
    name="train",
    exist_ok=False,
)
'''


def example_predict_opencv() -> str:
    return '''
import cv2
from ultralytics import YOLO

model = YOLO("best.pt")
img = cv2.imread("frame.png")  # BGR
r = model.predict(img, conf=0.35, classes=[0], verbose=False)[0]

for box in r.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    cid = int(box.cls[0])
    conf = float(box.conf[0])
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 229, 0), 2)
    cv2.putText(
        img, f"{r.names[cid]} {conf:.2f}", (x1, max(15, y1 - 5)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 229, 0), 1, cv2.LINE_AA,
    )
# st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
'''


if __name__ == "__main__":
    print(MINDMAP)
    for step in PASSO_A_PASSO:
        print(step)
    print("IMPORT_OK:", IMPORT_OK)
    print("IMPORT_BAD:", IMPORT_BAD)
